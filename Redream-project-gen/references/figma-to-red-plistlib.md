---
source: 用户本地 figma-to-red skill（plistlib 工具链）
status: 当前可用方案（CLI 到位前的主力工具）
target: 未来迁移到 CLI（phase3-implement-redream.md + cli-modify.md）
---

# Figma JSON → .red 生成规范（plistlib 版本）

> **⚠️ 这是 CLI 到位前的兜底方案。**
>
> - 按团队约定，**以后 .red / .rebolt 的生成一律走 CLI**（见 `phases/phase3-implement-redream.md` + `references/cli-modify.md`）
> - 目前部分成员（Mengmeng）尚未拿到 CLI 二进制，仍用 Python plistlib 直接生成 .red
> - 本文档记录当前 plistlib 流程下 .red 文件的结构规范，保证在拿到 CLI 前产出的文件仍然有效、引擎能打开
> - CLI 到位后，本文档降级为历史参考

## 使用前提

- 主工具：`~/Desktop/red_tool/app.py`（Flask + Web UI）
- 启动：`cd ~/Desktop/red_tool && python3 app.py`
- 浏览器打开：`http://localhost:5000`
- 参考文件：`~/Desktop/red_output/界面_主菜单/Resources/界面_主菜单.red`
- 输出目录：`~/Desktop/red_output/<屏幕名>/Resources/<屏幕名>.red`

---

## .red 文件结构（顶层 12 个 key）

```python
{
  'centeredOrigin':    True,
  'currentResolution': 2,
  'currentSequenceId': 0,
  'fileType':          'Redream',
  'fileVersion':       1,
  'guides':            [],
  'nodeGraph':         cclayer,
  'rebolt':            {'isRebolted': False, 'redInfos': {}},
  'referenceImgNode':  ref['referenceImgNode'],
  'resolutions':       [...],
  'sequences':         [...],
  'stageBorder':       0,
}
```

---

## 节点层级结构

```
CCLayer (customClass=CoreLayer, expand=True)
  pos=[0,0 u=0,0]  size=[100,100 u=2,2]
└── scene_root CCNode（屏幕名）
      pos=[50,50 u=2,2]  size=[100,100 u=2,2]  anchor=(0.5,0.5)
    ├── [浮层] 放穿透层 REDNodeButton (100%×100% u=2,2)
    ├── [浮层] 遮罩_背景 CCLayerColor (100%×100% u=2,2)
    ├── 普通内容节点
    ├── 组_顶部合并（多个 TOP 节点自动合并）
    └── 组_底部合并（多个 BOTTOM 节点自动合并）
```

---

## 坐标系统（核心规则）

### 第一步：算绝对边距

```python
左边距 = x
右边距 = sw - (x + w)
上边距 = y
下边距 = sh - (y + h)
```

### 第二步：全宽判断

`horizontal == 'SCALE'` 或 `(horizontal == 'LEFT' 且右边距 < 10)` → 全宽节点

### 第三步：场景分类

**全宽节点（宽=100% u=2，高=固定 px u=0）：**

| vertical | pos x | pos y | anchor |
|---|---|---|---|
| TOP | 50% u=2 | 100% u=2 | (0.5, 1.0) |
| BOTTOM | 50% u=2 | 0% u=2 | (0.5, 0.0) |
| SCALE/CENTER | 50% u=2 | 50% u=2 | (0.5, 0.5) |

**固定宽节点（宽=固定 px u=0，高=固定 px u=0）：**

- 水平：看绝对坐标对称性（差 < 10px → 居中，左 < 右 → 靠左，左 > 右 → 靠右）
- 垂直：CENTER→50% u=2，TOP→100% u=2，BOTTOM→0% u=2

### 第四步：多个同向贴边节点自动合并

```
组_顶部合并 / 组_底部合并
  宽=100% u=2，高=总高固定 px u=0，贴顶/底

内部各节点：
  pos x=50% u=2，pos y=绝对 px u=0
  宽=100% u=2，高=固定 px u=0
```

### 子节点坐标

```python
cx = fx + w / 2.0
cy = parent_h - fy - h / 2.0    # Cocos y 轴翻转
anchor = (0.5, 0.5)

# 父节点全宽：x=百分比 u=2，y=绝对 px u=0
# 父节点固定尺寸：x=绝对 px u=0，y=绝对 px u=0
```

---

## 节点类型映射

| 条件 | baseClass | 备注 |
|---|---|---|
| 根场景 | CCLayer | customClass=CoreLayer |
| scene_root | CCNode | 50%,50% / 100%×100% |
| 普通 FRAME/GROUP | CCNode | |
| 内含触控层的任意容器 | CCNode | 内容自动并入触控层 |
| `底板_XXX` FRAME（v19）| REDNodeButton | 触控层新命名 |
| `切图_底板_XXX`（旧）| REDNodeButton | 兼容 |
| `图片_`/`图标_`/`背景_`/`插图_`/`特效_` | CCSprite | |
| `底板_XXX` RECTANGLE（非形状）| CCSprite | 外层容器底板 |
| `底板_XXX形状` RECTANGLE | 跳过 | |
| `文本_`/`文字_` / TEXT | CCRedLabel | |
| `内容区_XXX` | 跳过 | 提升子节点 |
| `弹性缝隙` | 跳过 | |
| `遮罩_背景` | CCLayerColor | opacity=178，黑色，100%×100% |
| `放穿透层` | REDNodeButton | 仅浮层，100%×100% |

---

## 触控层识别（is_btn_layer）

```python
def is_btn_layer(name, node_type=''):
    if name.startswith('切图_底板_'):       # 老命名（任意 type）
        return True
    if (name.startswith('底板_')
            and not name.endswith('形状')
            and node_type.upper() == 'FRAME'):  # 新命名 v19
        return True
    return False
```

**按钮容器识别：不看名字前缀，看有无触控层子节点**

- 有 `is_btn_layer` 子节点 → 是按钮容器 → 其他内容并入触控层

---

## REDNodeButton 属性（严格 7 个）

```
position / contentSize(固定 px) / anchorPoint(0.5,0.5)
opacity(255) / color([255,255,255])
ccControl(['',1,32]) / preferedSize(同 contentSize)
```

**ccControl 含义：**
- `''` = Selector 空
- `1` = 启用
- `32` = Up inside

---

## 按钮内容结构

```
CCNode 容器（任意名称，内有触控层）
└── 底板_XXX (REDNodeButton)
    ├── 图标_XXX (CCSprite)     ← 子节点，缩放时跟随 ✅
    └── 文本_XXX (CCRedLabel)   ← 子节点，缩放时跟随 ✅
```

---

## 浮层屏幕

```
scene_root (浮层_XXX)
├── 放穿透层 REDNodeButton  pos=[50%,50% u=2,2]  size=[100%×100% u=2,2]
├── 遮罩_背景 CCLayerColor  pos=[50%,50% u=2,2]  size=[100%×100% u=2,2]  opacity=178
└── 弹窗_XXX CCNode         pos=[50%,50% u=2,2]  size=[固定 px u=0,0]
```

---

## 分辨率配置

```python
[设计分辨率 1080×2400 / 正常 1080×2080 / 偏宽 1560×2080 / 偏高 1080×2800]
```

---

## 参考文件（本地）

| 文件 | 用途 |
|---|---|
| `界面_主菜单.red` | referenceImgNode 来源 |
| `每日任务活动_活动弹窗.red` | REDNodeButton / 放穿透层参考 |
| `JI_主游戏模块_主界面.red` | 全宽贴顶/底参考 |
| `~/Desktop/red_tool/app.py` | 主力生成工具（v10b） |

---

## CLI 迁移对照提示（未来）

当 CLI 到位后，以下映射关系需要整理到正式 CLI 对照表：

| plistlib 操作 | CLI 等价命令 |
|---|---|
| 手动构建 CCNode dict | `modify add-node --type CCNode --name <n>` |
| 手动构建 REDNodeButton dict | `modify add-node --type REDNodeButton --name <n>` |
| 手动设置 position dict（含 unit） | `modify set-property --property position --value "x,y,xUnit,yUnit,corner"` |
| 手动 copy referenceImgNode | CLI 自动处理 |
| 手动生成 uniqueNodeId | CLI 自动处理 |
| `rebolt: {redInfos: {}}` | `modify new-scene --enable-rebolt` 自动处理 |

具体 CLI 命令以 `references/cli-modify.md` 为准。
