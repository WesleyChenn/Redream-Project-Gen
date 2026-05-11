# Figma → Redream 自动化出图 + 建节点树

从 Figma 视觉设计稿自动导出图片、创建 .red 场景、构建节点树、映射布局坐标。

> 与 `figma-to-redream.md`（从工程结构说明文档转换）不同，本工作流面向**视觉设计稿**，自动识别图层→导出图片→建立对应节点树。

---

## 工具

| 工具 | 用途 |
|------|------|
| MCP `get_metadata` | 获取 Figma 节点树结构（名称、ID、层级、位置、尺寸） |
| MCP `get_design_context` | 获取详细设计上下文（含截图） |
| Figma REST API `/v1/files/:key/nodes` | 获取完整节点属性（颜色、字体、约束、填充等） |
| Figma REST API `/v1/images/:key` | 批量导出图片 |
| Python `tools/figma_auto_export.py` | 节点分析、坐标转换、图片下载、TexturePacker 打图、CLI 命令生成 |
| TexturePacker CLI | 散图打包为 plist + webp 图集 |
| Redream CLI | 创建场景、添加节点、设置属性 |

---

## 完整流程（8 步）

### Step 1: 获取 Figma 数据

**输入：** Figma URL（如 `https://figma.com/design/QGnttK1FTJfNi6CpwBEGTa/xxx?node-id=11-2`）

**操作：**
1. 从 URL 提取 `fileKey` 和 `nodeId`（`-` → `:`）
2. 调用 MCP `get_metadata` 获取节点树概览
3. 调用 MCP `get_design_context` 获取截图（可选，用于验证）
4. 需要详细属性时，用 Figma REST API：

```bash
# 获取节点详细数据（需要 FIGMA_TOKEN）
curl -H "X-Figma-Token: $FIGMA_TOKEN" \
  "https://api.figma.com/v1/files/{fileKey}/nodes?ids={nodeId}"
```

**输出：** 节点树 JSON 数据

### Step 2: 分析节点，制定计划

**操作：** 将 Figma 节点数据保存为 JSON，调用分析工具：

```bash
python3 tools/figma_auto_export.py analyze \
  --input figma_nodes.json \
  --project-prefix FP \
  --module-name 开启通知
```

**节点分类规则（按命名前缀）：**

| Figma 前缀 | Redream 类型 | 导出图片 | 说明 |
|------------|-------------|---------|------|
| `按钮_` | REDNodeButton | ✗（子元素导出） | |
| `底板_` | CCScale9Sprite | ✓ | |
| `底板Frame_` | CCSprite | ✓ | Frame 整图导出，子节点清空 |
| `文字_` | CCRedLabel | ✗ | |
| `图片_` / `插图_` / `图标_` | CCSprite | ✓ | |
| `面板_` | CCNode | ✗ | |
| `遮罩_` | CCLayerColor | ✗ | 名称含"遮罩"即匹配 |
| `弹窗_` | CCNode | ✗ | |
| `按钮基底_` | CCSprite | ✓ | |
| `底板组_` | CCNode | ✗ | |
| `进度条_` | CCProgressTimer | ✓ | |
| `背景图_` / `特效_` / `效果图_` | CCSprite | ✓ | |

**Frame 整图导出**：`底板Frame_` 前缀的节点作为 FRAME 整体导出一张图片，其子节点不单独建立节点树。图片命名时自动去除 "Frame" 字样。

**输出：** 分析报告（JSON），包含节点树结构、类型统计、导出清单。

**确认：** 向用户展示分析报告，确认后继续。

### Step 3: 下载图片到工程目录

**操作：** 调用 `download-images` 自动下载图片到工程 `image/{图集名}/` 目录：

```bash
python3 tools/figma_auto_export.py download-images \
  --input figma_nodes.json \
  --file-key QGnttK1FTJfNi6CpwBEGTa \
  --project-dir /path/to/project \
  --project-prefix FP \
  --module-name 开启通知 \
  --scale 1
```

**图集文件夹命名：** `{项目前缀}_{模块名}`（如 `FP_开启通知`），可通过 `--atlas-name` 手动指定。

**图片命名规范：** `[项目前缀]_[模块名]_[类型前缀]_[语义描述].png`

**目录结构：**
```
image/FP_开启通知/
├── FP_开启通知_底板_弹窗底板.png
├── FP_开启通知_按钮基底_绿色.png
└── ...
```

### Step 3.5: TexturePacker 打图

**操作：** 自动生成 tps 文件并调用 TexturePacker：

```bash
python3 tools/figma_auto_export.py pack-images \
  --project-dir /path/to/project \
  --atlas-name FP_开启通知
```

**自动完成：**
1. 在 `tps/` 下生成 `FP_开启通知.tps`（复制已有 tps 为模板或使用内置模板）
2. 调用 TexturePacker CLI 打图
3. 输出 `_img_plist/FP_开启通知.plist` + `_img_plist/FP_开启通知.webp`

**三者命名一致性：**
```
tps/FP_开启通知.tps          ← tps 配置
image/FP_开启通知/            ← 散图源文件
_img_plist/FP_开启通知.plist  ← TexturePacker 输出
_img_plist/FP_开启通知.webp   ← TexturePacker 输出
```

### Step 4: 创建 .red 文件

```bash
# 1. 创建场景
Redream modify new-scene --scene ccb/FP_弹窗_开启通知.red -p project.redproj

# 2. 修复根节点类型和分辨率
python3 tools/figma_auto_export.py fix-scene \
  --red-file ccb/FP_弹窗_开启通知.red \
  --scene-name 弹窗_开启通知
```

**根节点类型判断：**
- 文件名包含 `弹窗` / `浮层` / `全屏反馈` / `界面` → CCLayer（4 条分辨率）
- 其他 → CCNode（1 条 0x0 分辨率）

### Step 5: 构建节点树

**方式 A：逐条命令**

```bash
# 生成所有 CLI 命令（spriteFrame 自动引用 plist名.plist,帧名.png）
python3 tools/figma_auto_export.py generate \
  --input figma_nodes.json \
  --scene ccb/FP_弹窗_开启通知.red \
  --project project.redproj \
  --project-prefix FP \
  --module-name 开启通知 \
  --format commands
```

**方式 B：批量配置**

```bash
# 生成 batch JSON 配置
python3 tools/figma_auto_export.py generate \
  --input figma_nodes.json \
  --scene ccb/FP_弹窗_开启通知.red \
  --project project.redproj \
  --project-prefix FP \
  --module-name 开启通知 \
  --format batch > batch_config.json

# 执行批量操作
Redream modify batch --config batch_config.json -p project.redproj
```

**方式 C：生成完整 Shell 脚本**

```bash
python3 tools/figma_auto_export.py generate \
  --input figma_nodes.json \
  --scene ccb/FP_弹窗_开启通知.red \
  --project project.redproj \
  --project-prefix FP \
  --module-name 开启通知 \
  --format shell > build_scene.sh

chmod +x build_scene.sh && ./build_scene.sh
```

### Step 6: 设置属性 + 布局映射

属性在 Step 5 的命令中已包含，主要包括：

| 属性 | 来源 | CLI 格式 |
|------|------|---------|
| `position` | Figma x/y + 坐标转换 | `x%,y%,0,2,2`（百分比相对父级） |
| `contentSize` | Figma width/height | `w,h,wUnit,hUnit` |
| `displayFrame` / `spriteFrame` | 图集引用 | `plist名.plist,帧名.png` |
| `color` | Figma fill 颜色 | `r,g,b` |
| `opacity` | Figma opacity × 255 | `0-255` |
| `visible` | Figma visible | `true/false` |
| `string` | Figma 文本内容 | 文本字符串 |

**spriteFrame 引用格式：** `FP_开启通知.plist,FP_开启通知_底板_弹窗底板.png`

### Step 6.5: plistlib 后处理（锚点与忽略锚点修正）

CLI 无法对所有节点类型设置 `anchorPoint` 和 `ignoreAnchorPointForPosition`，需通过 plistlib 直接修改 .red 文件：

```bash
python3 tools/figma_auto_export.py postprocess \
  --red-file ccb/FP_弹窗_开启通知.red
```

或在 Python 中直接调用：
```python
from figma_auto_export import postprocess_red_file
postprocess_red_file("ccb/FP_弹窗_开启通知.red")
```

**自动应用规则：**
1. 所有节点 `ignoreAnchorPointForPosition = false`
2. CCLayer 根节点 `anchorPoint = [0, 0]`
3. 所有其他节点 `anchorPoint = [0.5, 0.5]`

> 生成的 shell 脚本（`--format shell`）已自动包含此步骤。

### Step 7: 验证

```bash
# 检查节点树
Redream inspect scene ccb/FP_弹窗_开启通知.red --properties -p project.redproj

# 验证工程完整性
Redream inspect check -p project.redproj
```

---

## 锚点与忽略锚点规则

**全局规则（通过 plistlib 后处理强制执行）：**
1. **所有节点**：`ignoreAnchorPointForPosition = false`（不勾选"忽略锚点"）
2. **CCLayer 根节点**：`anchorPoint = [0, 0]`
3. **所有其他节点**：`anchorPoint = [0.5, 0.5]`

> CLI `set-property anchorPoint` 对 CCNode 等类型可能不生效，需通过 `postprocess_red_file()` 用 plistlib 直接修改 .red 文件。

---

## 弹窗骨架节点属性

弹窗标准骨架使用以下属性值。

**Position 格式：** `[x, y, posType, xRef, yRef]` — posType 始终为 0；xRef/yRef: 0=绝对坐标, 2=百分比（相对父级）

**ContentSize 格式：** `[w, h, wUnit, hUnit]` — wUnit/hUnit: 0=绝对点值, 2=百分比（相对父级）

| 节点 | position | contentSize | 其他属性 |
|------|----------|-------------|---------|
| CCLayer（根节点） | 默认 | `100,100,2,2` | anchorPoint=`0,0`, ignoreAnchorPointForPosition=`false` |
| 总组 | `50,50,0,2,2` | `100,100,2,2` | anchorPoint=`0.5,0.5`, visible=`false`, ignoreAnchorPointForPosition=`false` |
| 全屏防穿透按钮 | `50,50,0,2,2` | `100,100,2,2` | anchorPoint=`0.5,0.5`, opacity=`0`, swallowTouches=`true`, zoomOnTouchDown=`false` |
| 黑色遮罩 | `0,0,0,0,0` | `100,100,2,2` | ignoreAnchorPointForPosition=`false`, color=`0,0,0` |
| 安全区域 | `0,0,0,0,0` | - | ignoreAnchorPointForPosition=`false` |
| 弹窗总组 | `50,50,0,2,2` | 动态 | anchorPoint=`0.5,0.5` |

---

## 坐标转换公式

统一使用百分比定位格式 `[x%, y%, 0, 2, 2]`（相对父级百分比），不使用 corner 概念。

**Position 格式：** `[x, y, posType, xRef, yRef]`
- posType: 始终为 0
- xRef/yRef: 0=绝对坐标（像素值），2=百分比（相对父级）
- 标准百分比居中示例: `[50, 50, 0, 2, 2]`（x=50%父宽，y=50%父高）

**转换公式（Figma 左上角原点 → Redream 左下角原点）：**

Figma API `absoluteBoundingBox` 返回的是页面绝对坐标，需先转为相对父级坐标：
```
relative_x = abs_x - parent_abs_x
relative_y = abs_y - parent_abs_y
```

然后转换为 Redream 百分比坐标（anchorPoint = 0.5, 0.5）：
```
x% = (relative_x + node_width × 0.5) / parent_width × 100
y% = (1 - (relative_y + node_height × 0.5) / parent_height) × 100
```

**输出格式：** `x%,y%,0,2,2`

**注意：**
- Figma Y 轴向下，Redream Y 轴向上（左下角原点），所以 y% 需要翻转
- Figma API 返回的是绝对坐标，必须先减去父级绝对坐标得到相对坐标
- 子节点遍历顺序：Figma API children 顺序 = 从后到前（first child = 最底层），与 Redream 一致，**不需要 reverse**

---

## Python 工具参考

**路径：** `tools/figma_auto_export.py`

**子命令：**

| 命令 | 功能 | 关键参数 |
|------|------|---------|
| `analyze` | 分析节点树，生成报告 | `--input`, `--project-prefix`, `--module-name` |
| `generate` | 生成 Redream CLI 命令 | `--input`, `--scene`, `--project`, `--format`, `--atlas-name` |
| `export-images` | 生成图片导出计划 | `--input`, `--file-key`, `--scale` |
| `download-images` | 下载图片到工程目录 | `--input`, `--file-key`, `--project-dir`, `--figma-token` |
| `pack-images` | 生成 tps + TexturePacker 打图 | `--project-dir`, `--atlas-name` |
| `fix-scene` | 修复 new-scene 创建的场景 | `--red-file`, `--scene-name` |

**输入格式：** Figma REST API 的节点 JSON（`/v1/files/:key/nodes` 返回值）

---

## 当前不包含

- **时间线动画**：进入/退出动画需手动配置
- **Rebolt 逻辑**：行为树需根据业务逻辑单独配置
- **字体文件**：文本节点的字体引用需工程中已有对应 .fnt 文件
