# .red 节点树构建规范

从 Figma 工程结构说明文档还原 .red 场景的节点树结构、类型选择、层级组织的完整规范。
基于 BrilliantSortAppDemo + redream_demo + FindDifferenceGame 三个真实项目提取。

## 节点类型速查

| 类型 | 用途 | 关键属性 |
|------|------|----------|
| `CCNode` | 通用容器/分组/定位点 | position, contentSize, visible |
| `CCLayer` | 全屏场景根节点（界面/弹窗） | contentSize=[100,100,2,2] (百分比) |
| `CCLayerColor` | 纯色矩形（弹窗半透明遮罩） | color=[0,0,0], opacity=180~204 |
| `CCSprite` | 静态图片（图标/装饰/背景） | displayFrame=[plist, frame.png] |
| `CCScale9Sprite` | 可拉伸图片（按钮底板/面板/进度条背景） | spriteFrame, preferedSize, insets |
| `CCRedLabel` | 双层位图标签（前景+描边） | frontBMFntFile, backBMFntFile, string |
| `CCLabelPlus` | 多层位图标签（渐变+纯色+描边） | labelConfig[], string, localizationV2 |
| `CCLabelBMFont` | 单层位图标签（渐变字体） | fntFile, string |
| `REDNodeButton` | 可点击按钮 | ccControl, preferedSize, scaleRatio, swallowTouches |
| `REDFile` | 子场景嵌入 | redFile=相对路径, animation=-2 |
| `RedSafeAreaLayer` | 安全区域容器（刘海适配） | ignoreAnchorPointForPosition=true |
| `CCProgressTimer` | 进度条填充 | midpoint, barChangeRate, type=1, percentage |
| `RParticleSystem` | 粒子特效 | 内联配置 |
| `SkeletonAnimation` | Spine 3.x 骨骼动画 | dataFile, atlasFile, skin |
| `SkeletonAnimation4` | Spine 4.x 骨骼动画 | dataFile, atlasFile, frame |
| `CCLabelBMFont` | 单层位图标签（渐变字体伴侣） | fntFile, string |
| `CCBlockTouchLayer` | 触摸屏蔽层 | (无特殊属性) |
| `REDPolygonClippingNode2` | 多边形遮罩裁切 | polygonVerts, Inverted |
| `UISlider` | 滑动条 | bar, ball (FrameSet) |

### 类型选择规则

- **显示文本** → `CCRedLabel`（数值/金币数/倒计时）或 `CCLabelPlus`（UI 文本/按钮文字）
- **显示图片** → `CCSprite`（固定尺寸）或 `CCScale9Sprite`（可拉伸）
- **可点击** → `REDNodeButton`（不要用 CCNode 当按钮）
- **嵌入子场景** → `REDFile`（包裹在同名 CCNode 里）
- **定位/分组** → `CCNode`
- **全屏根节点** → `CCLayer`（界面/弹窗），`CCNode`（子 CCB/组件）

## 场景骨架模式

### 模式 A：组件场景（CCNode 根）

用于：可复用小组件（金币栏、按钮、进度条）

```
CCNode (root)
└── 总组 (CCNode)
    └── <内容节点>
```

### 模式 B：全屏页面（CCLayer 根）

用于：主页、游戏界面

```
CCLayer (root, contentSize=[100,100,2,2])
└── 总组 (CCNode, position=[50,50,0,2,2])
    ├── 背景组 (CCNode)
    │   └── 背景 (CCSprite / CCScale9Sprite)
    ├── <内容区域>
    └── 浮层定位层 (CCNode)
```

### 模式 C：弹窗/对话框（CCLayer 根）

用于：设置弹窗、道具解锁弹窗、确认框

```
CCLayer (root)
└── 总组 (CCNode)
    ├── 背景组 (CCNode)
    │   ├── 全屏防穿透按钮 (REDNodeButton, preferedSize=[100,100,2,2], swallowTouches=true)
    │   ├── 全屏点击按钮 (REDNodeButton, preferedSize=[100,100,2,2])
    │   └── 遮罩 (CCLayerColor, color=[0,0,0], opacity=180)
    └── 安全区域节点 (RedSafeAreaLayer)
        └── 弹窗总组 (CCNode)
            ├── 弹窗底板组 (CCNode)
            │   └── 底板 (CCScale9Sprite)
            ├── 标题栏组 (CCNode)
            │   ├── 标题底板 (CCSprite)
            │   ├── 标题文本 (CCLabelPlus / CCRedLabel)
            │   └── 关闭按钮 (REDNodeButton)
            │       └── 关闭按钮 (CCSprite)
            ├── 信息组 (CCNode) — 内容区
            └── 按钮组 (CCNode) — 操作按钮
```

## 按钮构建规范

### B1：图标按钮（关闭、设置等）

```
<名称>按钮 (REDNodeButton)
  | preferedSize = 点击区域大小
  | scaleRatio = 0.95
  | swallowTouches = true
  └── <名称> (CCSprite)
      | displayFrame = [plist, frame.png]
      | position = [50,50,0,2,2]  ← 居中
```

### B2：文字按钮（确认、购买等）

```
<名称>按钮 (REDNodeButton)
  | preferedSize = 点击区域大小
  | scaleRatio = 0.95
  ├── 按钮底板 (CCScale9Sprite)
  │   | spriteFrame = [plist, 按钮底板.png]
  │   | preferedSize = 底板尺寸
  │   | position = [50,50,0,2,2]
  └── 按钮文本 (CCLabelPlus / CCRedLabel)
      | string = "确认"
      | localizationV2 = {...}
```

### B3：状态按钮（已解锁/未解锁）

```
<名称> (CCNode) ← 容器
  ├── 已解锁状态组 (CCNode, visible=false)
  │   ├── 道具图标 (CCSprite)
  │   └── 数量组 (CCNode)
  │       ├── 数量底板 (CCSprite)
  │       └── 道具数量 (CCRedLabel)
  ├── 未解锁状态组 (CCNode, visible=false)
  │   └── 锁图标 (CCSprite)
  └── <名称>按钮 (REDNodeButton)
```

### B4：全屏屏蔽按钮（弹窗必备）

```
全屏防穿透按钮 (REDNodeButton)
  | preferedSize = [100,100,2,2]  ← 百分比全屏
  | swallowTouches = true         ← 阻止触摸穿透
全屏点击按钮 (REDNodeButton)
  | preferedSize = [100,100,2,2]
  ← 用于检测"点击外部关闭"
```

## 标签构建规范

### CCRedLabel（数值显示首选）

用于：金币数、道具数量、倒计时等需要 rebolt 动态更新的数值。

```
金币数 (CCRedLabel)
  | frontBMFntFile = "拉丁语/通用_字体_拉丁语_纯白字体.fnt"
  | frontColor = [255, 255, 255]
  | backBMFntFile = "拉丁语/通用_字体_拉丁语_描边字体.fnt"
  | backColor = [25, 84, 2]
  | string = "0"
  | horizontalAlignment = 1  ← 居中
  | dimensions = [200, 60, 0, 0]
  | scale = [0.5, 0.5, true]
```

### CCLabelPlus（UI 文本首选）

用于：按钮文字、标题、说明文本。支持渐变+纯色+描边三层。

```
标题 (CCLabelPlus)
  | labelConfig = [
  |   {"fntFile":"通用_字体_渐变字体.fnt", "fontColor":"[255,255,255]", "style":"渐变样式"},
  |   {"fntFile":"通用_字体_纯白字体.fnt", "fontColor":"[217,255,167]", "style":"纯白样式"},
  |   {"fntFile":"通用_字体_描边字体.fnt", "fontColor":"[25,84,2]",     "style":"描边样式"}
  | ]
  | string = "标题文本"
  | localizationV2 = {"isLocalization":true, "lanFile":"xxx.lan", "lanKey":"key1_标题文本"}
```

## 子场景嵌入规范

### 标准嵌入

```
<子场景名> (CCNode)                ← 定位容器
  | contentSize = 子场景边界大小
  └── <子场景名> (REDFile)         ← 同名
      | redFile = <模块>/<文件名>.red
      | animation = -2            ← 不自动播放，由 rebolt 控制
      | position = [50,50,0,2,2]  ← 居中于父容器
```

### 重复嵌入（网格布局）

同一个 .red 文件多次引用，每个包裹 CCNode 设不同 position：

```
第一关 (CCNode, position=A) → 第一关 (REDFile) → 关卡.red
第二关 (CCNode, position=B) → 第二关 (REDFile) → 关卡.red
第三关 (CCNode, position=C) → 第三关 (REDFile) → 关卡.red
```

### REDFile 路径规则

- 相对于 `ccb/` 目录
- 包含子目录：`通用模块/宝石排序_通用模块_金币栏.red`
- `animation` 始终为 `-2`

## 命名约定

### 节点命名

| 后缀/前缀 | 含义 | 示例 |
|-----------|------|------|
| `总组` | 最外层内容容器 | 总组 |
| `背景组` | 背景层 | 背景组 |
| `信息组` | 内容区域 | 信息组 |
| `按钮组` | 按钮区域 | 按钮组 |
| `底板` | 背景面板 | 弹窗底板, 按钮底板 |
| `定位点` | 程序用锚点 | 金币栏定位点, 飞行定位层 |
| `程序-` | C++ 代码用定位节点（不可见） | 程序-游戏区域上边沿 |
| `<名称>按钮` | 可点击按钮 | 关闭按钮, 金币栏按钮 |

### reboltName 分配规则

**需要 reboltName 的节点**：
- REDFile 子场景（被父 rebolt 控制的）
- 状态容器（visible 切换）
- 定位点（C++ 需要获取引用的）
- 按钮（BTButtonClickFuncAction 需要引用的）
- 标签（BTLabelTitleAction 需要引用的）

**不需要 reboltName 的节点**：
- 纯装饰（背景图、分隔线）
- 结构容器（总组、背景组、信息组）
- 不被逻辑引用的 Sprite

## 进度条构建

```
进度条组 (CCNode)
├── 进度条底板 (CCScale9Sprite)
│   | spriteFrame = [plist, 进度条底板.png]
│   | preferedSize = 底板尺寸
├── 进度条 (CCNode)
│   └── 进度条填充 (CCProgressTimer)
│       | midpoint = [0, 1]
│       | barChangeRate = [1, 0]
│       | type = 1
│       | displayFrame = [plist, 进度条填充.png]
│       | percentage = 0
└── 进度文本 (CCRedLabel)
    | string = "0%"
```

## position 格式参考

`[x, y, referenceCorner, xUnit, yUnit]`

| 值 | xUnit/yUnit=0 | xUnit/yUnit=2 |
|----|---------------|---------------|
| 含义 | 绝对像素 | 百分比（0~100） |

常用 position：
- `[50,50,0,2,2]` — 父容器正中
- `[0,0,0,0,0]` — 左下角原点
- `[50,100,0,2,2]` — 顶部居中
- `[50,0,0,2,2]` — 底部居中

## 跨项目共性模式

以下模式在三个项目中均被验证：

### 左右镜像技巧

几乎所有对称面板/按钮底板/标题栏使用左右镜像节点对，节省纹理空间：

```
底板_左 (CCScale9Sprite, anchorPoint=[1,0.5])
底板_右 (CCScale9Sprite, anchorPoint=[1,0.5], scale=[-1,1,false])
```

两个节点使用相同 `spriteFrame`，右侧用 `scaleX=-1` 水平翻转。

### 双标签叠加

重要文本使用两个 CCRedLabel 叠加实现描边效果：

```
文本 (CCNode)
├── 文本_描边 (CCRedLabel)  ← 底层：描边字体 + 深色
│   | frontBMFntFile = "描边字体.fnt"
│   | frontColor = [53, 59, 147]
└── 文本_前景 (CCRedLabel)  ← 上层：纯白字体 + 亮色
    | frontBMFntFile = "纯白字体.fnt"
    | frontColor = [255, 253, 252]
```

### memberVarAssignmentName 不使用

三个项目均不使用 `memberVarAssignmentName`/`memberVarAssignmentType`，全部通过 `rebolt.redInfos` 的 alias 管理节点身份。

### ccControl 标准值

所有按钮的 `ccControl` 值为 `[, 0, 32]`（无 C++ selector，target=0，controlEvents=32=TouchUpInside）。按钮交互逻辑由 rebolt `BTButtonClickFuncAction` 驱动。

### animation = -2

所有 REDFile 嵌入均使用 `animation = -2`（不自动播放），由 rebolt 或 C++ 控制动画。

### 不使用 CCLabelTTF

三个项目中 **均未使用 CCLabelTTF**。标签统一用 `CCRedLabel`（数值显示）和 `CCLabelPlus`（UI 文本，仅 BrilliantSortApp）或 `CCLabelBMFont`（渐变字体伴侣）。
