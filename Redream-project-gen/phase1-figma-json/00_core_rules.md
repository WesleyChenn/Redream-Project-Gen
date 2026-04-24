# S0 · 核心铁律（贯穿全流程，每步必读）

---

## 命名枚举锁（Enum Whitelist）

所有 JSON 节点 `name` 前缀必须且只能来自以下白名单，违反即为幻觉错误：

`界面_` `浮层_` `组_` `底板_` `内容区_` `内容_` `容器_` `导航_` `列表项_` `网格行_` `网格项_` `弹窗_` `按钮_` `图片_` `图标_` `背景_` `遮罩_` `文本_` `文字_` `弹性缝隙` `角标_` `徽章_` `进度_` `Tab_` `Toggle_` `请求_` `消息项_` `活动_` `底标_`

### 底板_ 命名子规范（影响插件灰色层次，必须遵守）

插件通过**节点类型 + 命名后缀**共同识别底板的三种角色：

| 节点类型 | 命名形式 | 用途 | 插件颜色 |
|---|---|---|---|
| `FRAME` | `底板_xxx` | **手搓按钮外壳**（透明包装层，内含底板形状 + 内容区）| 透明，不上色 |
| `RECTANGLE` | `底板_xxx形状` | **按钮内层底板**（外层 FRAME `底板_xxx` 的子节点）| 按父 FRAME 后缀分级灰（见下表）|
| `RECTANGLE` | `底板_xxx`（不含"形状"）| **外层容器底板**（弹窗 / 卡片 / 背景区域直接用）| 中深灰 |

**区分关键点：**
- **FRAME 底板_xxx**（按钮外壳）和 **RECTANGLE 底板_xxx**（外层容器底板）共享相同的命名，**靠节点类型区分**
- RECTANGLE 一旦含"形状"后缀就是按钮内层（作为 FRAME `底板_xxx` 的唯一子节点）
- RECTANGLE 不含"形状"后缀就是外层容器底板（独立使用，不需要外层包装 FRAME）

**强制规则：**
- FRAME `底板_xxx` 下的子 RECTANGLE 必须命名为 `底板_xxx形状`，不得省略"形状"后缀 — 否则会被插件误判为外层容器而上深色
- 独立使用的容器底板必须是 RECTANGLE 类型，且名字不得含"形状"

```
按钮结构示例：
底板_开始按钮 (FRAME 外壳)            ← FRAME，透明（包装层）
├── 底板_开始按钮形状 (RECTANGLE)     ← RECTANGLE + 含"形状" = 按钮内层（最浅灰）
└── 内容区_开始按钮 (FRAME AL)
    └── 文本_开始 (TEXT)

卡片结构示例：
容器_卡片 (FRAME NONE)
├── 底板_卡片 (RECTANGLE)              ← RECTANGLE + 不含"形状" = 外层容器底板（中深灰）
└── 其他内容...

弹窗结构示例：
弹窗_设定 (FRAME NONE)
├── 底板_弹窗设定 (RECTANGLE)          ← RECTANGLE + 不含"形状" + 后缀含"弹窗" = 可选最深灰
└── 内容...
```

### 底板_ FRAME 语义后缀规范（按钮层级分色）

插件通过 FRAME `底板_xxx` 中 `xxx` 的语义来区分**按钮内层底板**（RECTANGLE `底板_xxx形状`）的灰度，**不同层级自动获得不同灰度**，确保弹窗/卡片/按钮可辨识。

| FRAME `底板_` 后缀包含 | 场景 | 内层形状插件灰度 | 示例命名 |
|---|---|---|---|
| `弹窗` / `浮层` | 弹窗外壳底板 | 最深 | `底板_弹窗设定` |
| `Toggle` / `卡片` | Toggle / 卡片底板 | 中灰 | `底板_Toggle音量` |
| `开关` | 开关控件底板 | 较浅 | `底板_开关音量` |
| 其余（按钮名/功能名） | 普通按钮底板 | 最浅 | `底板_首頁` |

**强制规则：FRAME `底板_` 后缀必须使用能反映所包裹内容类型的语义词，不得用无意义编号或泛称。**

```
✅ 底板_弹窗设定     ← 后缀含"弹窗"，插件上最深灰，弹窗底板与内容区对比明显
✅ 底板_Toggle音量   ← 后缀含"Toggle"，插件上中灰，卡片与按钮有区分
✅ 底板_首頁         ← 普通按钮，插件上最浅灰

❌ 底板_1            ← 无语义后缀，插件无法判断层级，按默认最浅处理
❌ 底板_底板         ← 后缀无意义，影响层次识别
```

---

## fill 规则

- **FRAME**：永远不填充颜色，插件强制透明，fill 字段一律省略
- **RECTANGLE（手搓）**：fill 字段一律省略，由插件按命名前缀自动分配灰色（见上方底板_子规范）
- **`component_ref` 节点**：不受此规则约束，组件库内部 fill 由 Figma 自身维护

---

## 组件库加载铁律

**每次 S1 开始前，用户必须提供组件库 JSON 文件。**

- Claude 在 S3 组件匹配阶段必须逐一比对截图元素与组件库条目名称和结构
- 能匹配则**强制使用 `component_ref`**，不得退化为手搓
- 组件库未提供时，必须在 S1 开始前向用户索取，不得跳过直接手搓

---

## constraints 规则

| 场景 | constraints |
|---|---|
| `screen.layers` 直接子节点 | ✅ 必须写 |
| `NONE` 父容器的子节点 | ✅ 必须写 |
| `HORIZONTAL` / `VERTICAL` 父容器的子节点 | ❌ 不写 |

---

## 手搓按钮内容居中铁律

所有手搓按钮（非 component_ref）内部必须使用以下结构，**禁止用估算绝对坐标放置内容**：

```
底板_xxx FRAME (NONE, 固定w/h)                         ← FRAME 类型 = 按钮外壳（透明）
├── 底板_xxx形状 RECTANGLE (x=0, y=0, SCALE/SCALE)     ← RECTANGLE + 含"形状" = 按钮内层（分级灰）
└── 内容区_xxx FRAME (x=0, y=0, w=按钮w, h=按钮h,
      layoutMode: HORIZONTAL 或 VERTICAL,
      primaryAxisSizingMode: FIXED,
      counterAxisSizingMode: FIXED,
      primaryAxisAlignItems: CENTER,
      counterAxisAlignItems: CENTER,
      constraints: SCALE/SCALE)
    └── 所有内容子元素（图标、文字等，不写 x/y）
```

- 按钮内容不限于文字，图标+文字组合同样适用此规则
- 内容区_ FRAME 的 w/h 必须与按钮底板完全一致
- 子元素不写 x/y，由 AUTO LAYOUT CENTER 自动居中
- FRAME `底板_xxx` 与 RECTANGLE `底板_xxx形状` 同名不同类型，插件按 type 分别处理

**正确示例：**
```json
{
  "type": "FRAME", "name": "底板_开始按钮",
  "w": 446, "h": 150, "layoutMode": "NONE", "corner_radius": 75,
  "children": [
    { "type": "RECTANGLE", "name": "底板_开始按钮形状",
      "x": 0, "y": 0, "w": 446, "h": 150, "corner_radius": 75,
      "constraints": { "horizontal": "SCALE", "vertical": "SCALE" } },
    { "type": "FRAME", "name": "内容区_开始按钮",
      "x": 0, "y": 0, "w": 446, "h": 150,
      "layoutMode": "HORIZONTAL",
      "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
      "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "CENTER",
      "constraints": { "horizontal": "SCALE", "vertical": "SCALE" },
      "children": [
        { "type": "TEXT", "name": "文本_开始", "content": "開始遊戲",
          "font_size": 60, "font_weight": "Bold", "textAlignHorizontal": "CENTER" }
      ]
    }
  ]
}
```

**❌ 禁止：**
```json
{ "type": "RECTANGLE", "name": "底板_开始按钮" }
↑ 底板_ 下的子矩形缺少"形状"后缀，插件会上错误深灰色

{ "type": "TEXT", "name": "文本_开始", "x": 150, "y": 45, "content": "開始遊戲" }
↑ 内容绝对坐标估算，内容会飞出按钮
```

---

## JSON 格式铁律

| 正确 | 错误 |
|---|---|
| `"RECTANGLE"` | ~~RECT~~ |
| `"content"` (TEXT内容) | ~~text~~ |
| `"textAlignHorizontal"` | ~~text_align~~ |
| `"flow"` | ~~flows~~ |
| `{ "name", "w", "h", "layers" }` (屏幕) | ~~{ type, children }~~ |
| 屏幕顶层 `layers`，内部 `children` | |
| 每条 flow 含 `"trigger": "ON_CLICK"` | |
| 手搓节点 fill **一律省略** | ~~hex~~ ~~transparent~~ |

---

## component_ref 规则

- 独立 key（不是 type 的值）
- 不写 layoutSizingHorizontal/Vertical
- **必须等比缩放**：输出 w/h = 截图量测 × scale（不使用组件库原始尺寸）
- 缩放比计算：`scale = 目标h / 原始h`，非正方形组件以高度为基准等比推算宽度
- 组件库内部结构由 Figma 维护，Claude 不检查也不重写库内节点

---

## 两类节点

| 类型 | 底板分离 | 内部结构 |
|---|---|---|
| **component_ref** | 不适用 | 不管，由库自身维护 |
| **手搓节点** | 强制：`底板_xxx FRAME` + `底板_xxx形状 RECTANGLE` + `内容区_ FRAME` | 内容区必须 AUTO LAYOUT CENTER，禁止估算坐标 |

---

## 零幻觉

图里没有的元素，绝对不能写进 JSON。不脑补、不推断。

---

## 全局尺寸

- 输出固定 **1080×2400**
- `scale_x = 1080 / W`，`scale_y = 2400 / H`
- 所有坐标/尺寸 = 截图量测 × scale，取整，不估算
- 录屏帧 H 必须排除视频播放器 UI

---

## 屏幕类型判断

- **界面_**：全屏替换，原画面完全消失 → `dissolve 300ms`
- **浮层_**：原画面变暗仍可见，新内容浮上 → `OVERLAY` + `CLOSE`
- 活动页面（Easter Pass / Team Tournament 等）是 **界面_**，不是浮层

---

## 浮层遮罩铁律

所有 `浮层_` 屏幕的 `layers[0]` 必须是**全屏半透明黑色遮罩**：

```json
{
  "type": "RECTANGLE",
  "name": "遮罩_浮层背景",
  "x": 0, "y": 0, "w": 1080, "h": 2400,
  "constraints": { "horizontal": "SCALE", "vertical": "SCALE" }
}
```

- 插件识别 `遮罩_` 前缀后自动赋予深灰底色 + opacity=0.7（半透明）
- 遮罩位于 `layers[0]`（图层最底），其上的所有卡片/按钮/顶栏正常显示
- 遮罩 h=2400 覆盖整屏，卡片可以不占满屏幕（下方遮罩区透出底层界面的底部导航等）
- 遮罩 fill 字段一律省略（由插件按命名自动处理）

---

## 界面背景铁律

`界面_` 屏幕如果有全屏背景图（地图场景 / 房间 / 天空等），**必须作为屏幕 `layers[0]` 的全屏 `背景_xxx` RECTANGLE**：

```json
{
  "type": "RECTANGLE",
  "name": "背景_地图场景",
  "x": 0, "y": 0, "w": 1080, "h": 2400,
  "constraints": { "horizontal": "SCALE", "vertical": "SCALE" }
}
```

- 背景位于 `layers[0]`，尺寸 1080×2400 贴满整屏
- 其上的 HUD / 进度条 / 中间内容 / 底部导航浮在背景之上，透明区域自然透出背景
- **❌ 禁止**把全屏背景塞进"中间弹性区容器"（如 `组_地图内容`）内部，这会导致：
  - 背景只占中间区高度，顶部 / 底部无背景可透
  - 容器内元素绝对定位会与背景混淆
- 背景 fill 字段一律省略（由插件按 `背景_` 前缀上最浅灰）

---

⛔ 本文件为全局参考，不单独执行。每个步骤开始时必须先读取本文件。
