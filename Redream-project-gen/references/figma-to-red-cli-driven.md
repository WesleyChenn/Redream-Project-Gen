---
source: 用户 RED Tool v15（CLI 驱动版）
status: ✅ 当前方案（Python 转换层 + Redream CLI 规范化）
aligned_with: SKILL.md 铁律 2（CLI 优先）、Redream CLI 1.3.4
date: 2026-04-24
---

# Figma JSON → .red 生成规范（CLI 驱动版）

> **本文档记录 RED Tool（`~/Desktop/red_tool/red_tool 14/`）的 Figma → Redream 工程生成流程。**
>
> - 架构：Python 转换层 + Redream CLI 规范化
> - 核心原则：Python 只生成**中间 .red**，合法性由 Redream CLI `build-scene --config` 保证
> - 不再维护 plist schema，CLI 升级自动兼容
> - 这是 `ai_dev_skill` 铁律 2（"CLI 优先，不直接改源文件"）的一种具体实现

## 架构总览

```
Figma 画布
  ↓ 插件「导出 JSON」（必须含 x/y）
含 x/y 的导出 JSON
  ↓ 粘进 RED Tool (http://localhost:5000)
Python：坐标计算 + 场景分类 + 生成中间 .red
  ↓ 写入临时文件
Redream CLI 1.3.4:
  ├─ modify new-project（首次）+ --add-resource-path Resources
  ├─ modify build-scene --config 中间.red → 规范化 .red + 自动生成 .rebolt
  └─ inspect check → 校验合法性
  ↓
~/Desktop/red_output/
├── red_project.redproj
├── Resources/
│   ├── 界面_XXX.red
│   ├── 界面_XXX.rebolt
│   └── ...
└── ccb/
```

### 组件分工

- **HTML**：可视化界面，Python 脚本的 GUI（不是独立工具）
- **Python** (`app.py`)：核心转换层，实现约束规则和场景分类
- **Redream CLI** (v1.3.4)：`/Applications/Redream.app/Contents/MacOS/Redream` —— 生成合法 .red 和校验

### 工具路径

- 项目位置：`~/Desktop/red_tool/red_tool 14/`
- 启动：`cd ~/Desktop/red_tool/red_tool\ 14 && python3 app.py`
- 访问：`http://localhost:5000`（必须 http，不能用 file://）

---

## 两种 JSON 区别（关键）

### 生成 JSON（Import: JSON → Figma）
- **不含 x/y 坐标**
- 用于从 JSON 在 Figma 画布画出界面
- AL 容器内子节点靠 Figma 自动排列

### 导出 JSON（Export: Figma → JSON）
- **含真实 x/y 坐标**（Figma 自动计算好的）
- 用于把 Figma 画布的实际状态导出
- **RED Tool 只认这种**

**喂错 JSON 的症状**：所有子节点挤在左上角（因为 Python 对没 x/y 的节点按 0 处理）。

**正确流程**：
1. 用生成 JSON 在 Figma 画出界面
2. 在 Figma 里点插件「导出 JSON」
3. 把导出的 JSON 粘进 RED Tool

---

## 约束 → Redream 对应规则

### 顶层节点分类（`classify_top_layers` + `build_top_layer`）

**步骤 1：算绝对边距**
```
left   = x
right  = sw - (x + w)
top    = y
bottom = sh - (y + h)
```

**步骤 2：判断全宽**
```python
is_fullwidth = horizontal == 'SCALE' or (horizontal == 'LEFT' and right < 10)
```

**步骤 3：分场景生成**

#### 全宽节点

宽 = 100% u=2, 高 = 固定 px u=0

| vertical | pos | anchor |
|---|---|---|
| TOP | `[50%, 100% u=2,2]` | (0.5, 1.0) |
| BOTTOM | `[50%, 0% u=2,2]` | (0.5, 0.0) |
| CENTER | `[50%, 50% u=2,2]` | (0.5, 0.5) |

#### 固定宽节点（宽高都 u=0）

**水平对称性判断：**
| 条件 | 结果 |
|---|---|
| `abs(left-right) < 10` | 居中：`x=50% u=2 ax=0.5` |
| `left < right` | 靠左：`x=left/sw*100% u=2 ax=0.0` |
| `left > right` | 靠右：`x=right/sw*100% u=2 ax=1.0` |

**垂直对齐：**
| constraints.vertical | y | uy | ay |
|---|---|---|---|
| CENTER | 50% | 2 | 0.5 |
| TOP | 100% | 2 | 1.0 |
| BOTTOM | 0% | 2 | 0.0 |

### 多节点合并（`merge_edge_nodes`）

多个同向（全 TOP 或全 BOTTOM）节点自动合并：
- 包装名：`组_顶部合并` / `组_底部合并`
- 宽 100% u=2，高 = 所有节点高度之和
- 内部子节点也全宽：`x=50% u=2, y=绝对 px u=0`

### 子节点构建（`build_child`）

根据父节点类型：
- **父是全宽容器**：`x=百分比 u=2, y=绝对 px u=0`
- **父是固定尺寸**：`x/y 都绝对 px u=0`
- anchor 统一 (0.5, 0.5)

### 特殊节点

| 节点 | 规则 |
|---|---|
| scene_root | `pos=[50%,50% u=2,2] size=[100%×100% u=2,2]` |
| 遮罩_背景 | `CCLayerColor`, 100%×100% u=2, opacity=178, RGB=(0,0,0) |
| 放穿透层 | `REDNodeButton`, 100%×100% u=2，contentSize 和 preferedSize **都**要 u=2 |
| CCLayer 根 | `size=[100,100 u=2,2]`, customClass=CoreLayer |

### 关键限制

- **unit=3 只能用于 contentSize 高度**（减去模式），NEVER 用于 position
- position 只能 u=0（绝对像素）或 u=2（百分比）

---

## 按钮命名规则（v20，与 phase1 对齐）

### 识别优先级（Python 端，和 Redream 引擎保持一致）

```python
def is_btn_layer(name, node_type=''):
    if name.startswith('切图_底板_'):                           # v18 老命名
        return True
    if name.startswith('按钮_') and node_type.upper() == 'FRAME':  # v20 新命名
        return True
    if (name.startswith('底板_') and not name.endswith('形状')
            and node_type.upper() == 'FRAME'):                    # v19 过渡命名
        return True
    return False
```

### 三版命名对照

| 版本 | 触控层（REDNodeButton） | 按钮内层底板 |
|---|---|---|
| **v20（新）** | `按钮_XXX` FRAME | `底板_XXX` RECTANGLE（不加"形状"后缀）|
| v19（兼容）| `底板_XXX` FRAME（非"形状"后缀）| - |
| v18（兼容）| `切图_底板_XXX`（任意类型）| - |

### 节点类型对应

| 节点名 + 类型 | 父节点 | 输出 |
|---|---|---|
| `按钮_XXX` FRAME | 任意 | REDNodeButton |
| `底板_XXX` RECTANGLE | 非按钮 | CCSprite（外层容器底板）|
| `底板_XXX` RECTANGLE | 是按钮 | CCSprite（按钮内层装饰）|
| `底板_XXX形状` RECT | 任意 | 跳过（v19 兼容）|

### 按钮容器识别

- **不看名字前缀**，看是否有 `baseClass='REDNodeButton'` 子节点
- 有 → 是按钮容器，其他兄弟节点（图标/文字/角标）并入触控层 children
- 目的：点击缩放时装饰一起响应

### auto_btn（自动补触控层）

名字是 `按钮_` / `组_按钮_` 但没有触控层子节点：
- 自动插入一个 REDNodeButton
- 把现有 children 全部移到 REDNodeButton 的 children 里

### REDNodeButton 的 7 个属性

```python
position        # [x, y, 0, ux, uy]
contentSize     # [w, h, uw, uh, False, False]
anchorPoint     # [0.5, 0.5]
opacity         # 255
color           # [255, 255, 255]
ccControl       # ['', 1, 32]   ← '' Selector空, 1 启用, 32 Up inside
preferedSize    # [w, h, uw, uh, False, False]  ← 单位必须和 contentSize 一致
```

---

## 放穿透层规则

### 三条核心规则

1. **所有屏幕都要加**（`界面_` 和 `浮层_` 都加）
2. **位置**：scene_root 的 children[0]（在 CCLayer > scene_root 下面）
3. **尺寸**：100%×100%
   - `contentSize:  [100, 100, 2, 2]`
   - `preferedSize: [100, 100, 2, 2]` ← **两个单位必须都是 2**

### 常见坑

- `preferedSize` 写成 `[100, 100, 0, 0]`（100 像素）会导致渲染成小方块
- 只在 scene_root children[0] 位置，不能放 scene_root 外面

### 浮层_ 屏幕的完整结构

```
CCLayer
└── 浮层_XXX (scene_root CCNode)
    ├── 放穿透层 (REDNodeButton 100%×100%)
    ├── 遮罩_背景 (CCLayerColor 100%×100% opacity=178 黑)
    └── 弹窗_XXX / 其他内容
```

### 界面_ 屏幕的完整结构

```
CCLayer
└── 界面_XXX (scene_root CCNode)
    ├── 放穿透层 (REDNodeButton 100%×100%)
    └── 其他内容（背景 / 顶部 HUD / 底部导航等）
```

---

## 跳过规则

| 节点名 | 处理 |
|---|---|
| `弹性缝隙` | 跳过，不生成 |
| `内容区_XXX` | 跳过容器本身，子节点累加 offset 提升到父级 |
| `底板_XXX形状` RECTANGLE | 跳过（v19 兼容）|
| `底板_遮罩` | 跳过（用 make_mask 生成）|
| `遮罩_背景` | 顶层跳过，由 generate_red 单独用 make_mask 处理 |

---

## Redream CLI 关键命令

> 完整命令列表见 `references/cli-modify.md` 和 `references/cli-inspect.md`。
> 本节只列 RED Tool 用到的子集。

### 参数顺序铁律

```
Redream [options] action
```

action **必须放最后**。

错误示例：`Redream -p xxx inspect check --json`（--json 在 action 后 → `Unknown option`）

正确：`Redream --json -p xxx inspect check`

### 常用命令

**创建项目（两步）：**
```bash
# 1. 创建空项目
Redream modify new-project --project xxx.redproj --resolution 1080x2400

# 2. 把 Resources 加入资源路径（默认只加 ccb）
Redream modify --project xxx.redproj --add-resource-path Resources project
```

**构建场景（克隆规范化）：**
```bash
# --config 传源 .red 文件，CLI 克隆并规范化为新 schema
Redream modify build-scene \
  --project xxx.redproj \
  --scene Resources/目标.red \
  --config 中间文件.red
```

**校验项目：**
```bash
Redream inspect check --project xxx.redproj
# 输出 "ok." 表示全部通过
```

### 数据格式

- **Position**：`"x,y,z,unitX,unitY"`（帮助写 anchorX/Y/Z 是误导）
- **Size**：`"w,h,unitW,unitH,lockedW,lockedH"`
- **单位**：0=绝对像素，2=父容器百分比
- **`--json`**：帮助写了但 v1.3.4 不支持，去掉就能用

---

## 启动与排查

### 启动流程

```bash
cd ~/Desktop/red_tool/red_tool\ 14
python3 app.py
```

终端应显示：`* Running on http://127.0.0.1:5000`

### 端口被占用（最常见问题）

**症状**：`Address already in use` / `Port 5000 is in use`

**原因 1：AirPlay Receiver**（macOS Monterey+ 默认开启，占用 5000 端口）
- 系统设置 → 通用 → 隔空投送与接力 → 关掉"隔空投送接收器"

**原因 2：之前的 Python 进程残留**
```bash
lsof -i :5000          # 查看占用
kill -9 <PID>          # 杀掉（PID 从上面看到）
# 或
killall python3        # 全部杀
```

### 常见错误对照表

| 症状 | 原因 | 解决 |
|---|---|---|
| `Failed to fetch` | Flask 没启动 | 启动服务，用 `http://localhost:5000` |
| `Internal Server Error` | Flask 代码异常 | 看终端 Traceback |
| 按钮全挤在左上角 | 喂的是生成 JSON（没 x/y） | 用 Figma 插件「导出 JSON」 |
| 放穿透层渲染成小方块 | preferedSize 单位错误 | 确认是 `[100,100,2,2]` |
| 项目打开只有 ccb | Resources 没加入资源路径 | v15+ 自动加；或 `--add-resource-path Resources` |
| 双击 HTML 直接打开 | 应该用 localhost:5000 | 终端跑 `python3 app.py`，浏览器用 http |

### 重启服务

改代码后**必须重启**才生效：
1. 终端按 `Ctrl + C` 停止
2. 按 ↑ 调回 `python3 app.py` 回车
3. 浏览器刷新（Cmd+R）

---

## RED Tool 版本历史

| 版本 | 改动 |
|---|---|
| v13 | CLI 驱动版（去掉参考文件、改 build-scene）|
| v13b | 端口改 5001（兼容 AirPlay 占用）|
| v14 | 所有屏幕都加放穿透层（不只是浮层）|
| v14b | 修复 preferedSize 单位错误（小方块问题）|
| v15 | 新建项目自动加 Resources 资源路径 |

---

## 已知限制

1. **Python 只处理约束布局**，不模拟 Auto Layout 排列——必须用含 x/y 的导出 JSON
2. **同名覆盖**：生成的 .red 同名直接覆盖
3. **端口固定 5000**：如需改，修改 `app.py` 末尾的 `port=5000`
4. **只生成单项目**：所有屏幕放一个 `red_project.redproj` 里

---

## 未实现（按需后续补）

- 滚动容器（overflow / clip_content）
- component_ref 的实际组件展开
- Figma prototype flow 生成交互连线
- 多分辨率自适应（resolutions 字段生成）

---

## 关联

- `phase1-figma-json/` — 输入端：Figma JSON 规范（v20 按钮规则）
- `references/cli-modify.md` — CLI 完整写命令列表
- `references/cli-inspect.md` — CLI 完整读命令列表
- `phases/phase3-implement-redream.md` — 引擎组的 CLI 落地方法论
- `lessons/` — 实战坑和教训
