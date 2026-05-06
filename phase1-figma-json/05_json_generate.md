# S5 · 生成节点树 JSON

> 开始前先读取 `00_core_rules.md` + `ref/templates.md`，基于 S3 骨架 + S4 组件表执行

---

## JSON 顶层结构

```json
{
  "screens": [
    { "name": "界面_xxx", "w": 1080, "h": 2400, "layers": [] }
  ],
  "flow": []
}
```

## 屏幕根层必备元素

### 界面_ 屏幕
如果有全屏背景（地图/场景/房间/天空等），`layers[0]` 必须是：
```json
{ "type": "RECTANGLE", "name": "背景_xxx",
  "x": 0, "y": 0, "w": 1080, "h": 2400,
  "constraints": { "horizontal": "SCALE", "vertical": "SCALE" } }
```
❌ 禁止把全屏背景放进"中间弹性区"容器内。

### 浮层_ 屏幕
`layers[0]` 必须是全屏半透明黑色遮罩：
```json
{ "type": "RECTANGLE", "name": "遮罩_浮层背景",
  "x": 0, "y": 0, "w": 1080, "h": 2400,
  "constraints": { "horizontal": "SCALE", "vertical": "SCALE" } }
```
插件自动识别 `遮罩_` 前缀，加深灰 + opacity=0.7。遮罩之上放卡片/按钮/顶栏。

---
## 节点规则

### 位置服从铁律
- 父级 `NONE`：子节点保留 `x, y` 绝对坐标
- 父级 `HORIZONTAL/VERTICAL`：通过 padding / itemSpacing / 对齐控制位置

### FRAME
- 必须设 `layoutMode`（NONE / HORIZONTAL / VERTICAL）
- 必须设 `primaryAxisAlignItems`（MIN / MAX / CENTER / SPACE_BETWEEN）
- **手搓节点** fill 一律省略；`component_ref` 节点不受此约束，组件库内部 fill 由 Figma 自身维护

### RECTANGLE
- 纯图片/背景/装饰占位，有明确 w/h
- **手搓节点** fill 一律省略；`component_ref` 内部的 RECTANGLE 不受此约束

### TEXT
- 不设 w（除非有固定宽度约束）
- 居中文本必须加 `textAlignHorizontal: CENTER` + `textAlignVertical: CENTER`

### component_ref
- 独立 key，不写 layoutSizingHorizontal/Vertical
- 尺寸用 S4 计算结果

---

## 按钮与底板（v20）

### 手搓按钮铁律

所有手搓按钮必须用 `按钮_xxx` FRAME 作外壳，`底板_xxx` RECT 作内层装饰底板：

```
按钮_xxx (FRAME NONE, 固定w/h)            ← "按钮_" 前缀 = 触控层 REDNodeButton
├── 底板_xxx (RECTANGLE, x=0, y=0, SCALE/SCALE)   ← 按钮内层装饰(父是按钮 → 最浅灰)
├── (可选) 图标_xxx / 图片_xxx
├── (可选) 文本_xxx
├── (可选) 内容区_xxx (FRAME AL CENTER/CENTER)    ← 多子元素需要自动居中时使用
└── (可选) 角标_xxx / 徽章_xxx / 底标_xxx         ← 装饰附件,一起响应点击反馈
```

**三条核心规则：**
1. 按钮外壳命名必须**严格以 `按钮_` 开头**，FRAME 类型
2. 按钮内层底板命名用 `底板_xxx` RECT，**不加"形状"后缀，不用 FRAME 包装**
3. 所有内容（文字、图标、装饰）作为按钮 FRAME 的 children

❌ 禁止：
```json
{ "type": "TEXT", "name": "文本_开始", "x": 150, "y": 45, "content": "開始" }
↑ 按钮内容用绝对坐标估算，飞出按钮
```

### 按钮在 NONE 父容器内（简单场景）

```
组_xxx (FRAME NONE)                                 ← 容器,非按钮
├── 按钮_xxx (FRAME NONE)                           ← 按钮触控层
│   ├── 底板_xxx (RECTANGLE, corner_radius)          ← 按钮内层(最浅灰)
│   └── 文本_xxx / 图标_xxx / ...                    ← 直接作为按钮 children
```

### 按钮在 NONE 父容器内（带内容区）

```
按钮_xxx (FRAME NONE)
├── 底板_xxx (RECTANGLE)
└── 内容区_xxx (FRAME AL CENTER/CENTER)              ← 自动居中内部文字+图标
    └── 文本_xxx / 图标_xxx ...
```

### 外层容器底板（卡片 / 弹窗 / 大区域）

```
容器_xxx (FRAME NONE)                                ← 容器,不是按钮
├── 底板_xxx (RECTANGLE, corner_radius)              ← 外层容器底板(父非按钮 → 中深灰)
└── 其他内容(文本 / 图片 / 按钮 / ...)
```

⚠️ **装按钮的容器禁止命名为 `底板_` 开头**，必须用 `组_` / `容器_` / `弹窗_` 等。

### 按钮分组（装饰一起响应按钮变换）

装饰附件（角标 / 徽章 / 底标 / Popular 标签 / 倒计时胶囊）**必须作为按钮 FRAME 的 children**，兄弟关系错误。

```
正确:                              错误:
按钮_xxx (FRAME)                   组_xxx (FRAME NONE)
├── 底板_xxx                       ├── 按钮_xxx              ← 按钮
├── 图标_xxx                       └── 角标_xxx              ← 兄弟,点击不跟随 ❌
└── 角标_xxx (与按钮一起响应点击反馈 ✅)
```

### component_ref + 装饰（做法 B：父按钮 FRAME 包装）

```
按钮_活动紫罐 (FRAME)                ← 按钮触控层
├── 活动_紫罐 (component_ref)        ← 组件库主体
└── 角标_感叹号                     ← 装饰,一起响应点击反馈
```

### AL 父容器内的 ABSOLUTE 底板

```
底板_xxx (RECTANGLE, layoutPositioning: ABSOLUTE, x:0 y:0)
```
注意：`layoutPositioning: ABSOLUTE` 仅在 AL 容器内使用，NONE 容器内不写。

---

## component_ref 替换手搓的陷阱（铁律）

用户临时要求把某个 `component_ref` 改为手搓时（比如组件库里某组件被删），必须**把组件内部结构完整展开**，不能只是把 ref 替换成一个 FRAME 就完事。

**常见坑：展开后 `底板_` 仍是 FRAME 而不是 RECT**

错误示例（`矩形按钮_纯文本` ref 替换为手搓）:
```json
❌ 错误结构: 外层按钮 children 里有个 "底板_xxx FRAME"
{
  "type": "FRAME", "name": "按钮_Area13",
  "children": [
    { "type": "FRAME", "name": "底板_Area13",        ← ❌ 底板_ 居然是 FRAME
      "children": [
        { "type": "RECTANGLE", "name": "底板_Area13形" },
        { "type": "TEXT", ... }
      ]
    },
    { "type": "FRAME", "name": "角标_数字1_Area13" }
  ]
}
```

这违反 v20 按钮规则（"按钮内层底板 = 底板_xxx RECT,父是 `按钮_` FRAME"）。插件按名字 `底板_xxx` 会尝试上灰色,但遇到 FRAME 类型就会跳过,导致按钮内层无颜色。

**正确做法**:把被替换组件的内部 FRAME/RECT/TEXT 层级**直接展开为按钮的直接 children**,不要保留组件原本的包装 FRAME 层：
```json
✅ 正确结构: 底板、文本直接作为按钮 children
{
  "type": "FRAME", "name": "按钮_Area13",
  "children": [
    { "type": "RECTANGLE", "name": "底板_Area13", ... },  ← ✅ RECT
    { "type": "TEXT", "name": "文本_Area13", ... },
    { "type": "FRAME", "name": "角标_数字1_Area13", ... }
  ]
}
```

**执行步骤**：
1. 找到要被手搓替换的 ref 节点
2. 把组件库里该组件的**实际结构**读出来
3. 把组件内部的 FRAME 外壳扔掉（组件本身就是一个 FRAME 层）,**只保留内部 RECT/TEXT/装饰**
4. 把这些内部元素**直接作为外层按钮 FRAME 的 children**
5. 把 ref 节点的 `overrides` 内容回填到对应 TEXT 的 `content`
6. 保留 ref 节点的 `x / y / w / h / constraints` 到**整组元素的对齐基准**上（不是单个元素）

**自检**：替换后扫一遍所有"按钮_xxx" FRAME 的 children,凡是名为"底板_xxx"的都必须是 RECTANGLE type,不能是 FRAME。

---

## component_ref 叠加结构

当 component_ref 上有视觉叠加元素（角标、倒计时、徽章等），**统一使用 `按钮_xxx` FRAME 包装（做法 B）**。

**禁止**用 `组_xxx` NONE 容器包裹按钮 + 装饰（装饰不会响应点击反馈）。无论主体是"按钮类组件"（椭圆按钮/方形按钮/圆形按钮/矩形按钮）还是"Tab 状态切换类组件"，一律用 `按钮_xxx` FRAME 包装。

**包装层尺寸原则：对外 w/h = 主体 w/h，附加元素溢出不撑大包装层，主体用 x/y 偏移让位。**

**附加元素约束铁律：一律 LEFT/TOP，坐标全正数。禁止 RIGHT/CENTER/负数坐标（会导致元素飞出）。**

**附加元素位置确认（防止居中/左对齐误判）：**
```
居中期望 x = (主体w - 附加w) / 2
实际量测 x_actual（相对主体左边缘）
|x_actual - x| < 10px → 居中,x 用计算值
偏差 > 10px → 左/右对齐,x 用量测值
（无论哪种,constraints 都写 LEFT/TOP）
```

**四种常见场景：**

| 场景 | 包装层 w/h | 主体 x/y | 附加元素 x/y | constraints |
|---|---|---|---|---|
| 右上角角标溢出顶部 | 主体w × 主体h | 0, 角标h/2 | 主体w-角标w/2, 0 | LEFT/TOP |
| 角标正上方居中 | 主体w × 主体h | 0, 溢出量 | (主体w-角标w)/2, 0 | LEFT/TOP |
| 底标下方居中溢出 | 主体w × 主体h | 0, 0 | (主体w-附加w)/2, 主体h+间距 | LEFT/TOP |
| 右上角内侧不溢出 | 主体w × 主体h | 0, 0 | 主体w-角标w-偏移, 偏移 | LEFT/TOP |

```
包装层结构示意（右上角角标，主体h=231，角标h=34）：

按钮_活动花朵 (FRAME NONE, w=170, h=231)  ← 对外h=主体h,不含角标溢出
├── 活动_花朵 (component_ref, x=0, y=17)   ← y=角标h/2=17,往下让位
└── 角标_数字1 (FRAME NONE, x=136, y=0, constraints: LEFT/TOP)  ← y=0,溢出顶部
    ├── 底板_角标 (RECTANGLE)
    └── 文本_角标 (TEXT)

包装层结构示意（Tab + 底标,主体h=99）：

按钮_Tab_Weekly (FRAME NONE, w=219, h=99)  ← 对外h=主体h,不含底标
├── Tab_Weekly (component_ref, x=0, y=0, constraints: LEFT/TOP)
└── 底标_4d22h (component_ref, x=17, y=103, constraints: LEFT/TOP)  ← y=主体h+间距
```

---

## Auto Layout 规则

| 属性 | 合法值 |
|---|---|
| primaryAxisAlignItems | MIN / MAX / CENTER / SPACE_BETWEEN |
| counterAxisAlignItems | MIN / MAX / CENTER / BASELINE |
| primaryAxisSizingMode | FIXED / AUTO |
| counterAxisSizingMode | FIXED / AUTO |
| layoutSizingHorizontal | FIXED / HUG / FILL |

**禁止：** SPACE_AROUND、STRETCH、primaryAxisSizingMode: FILL/HUG

**关键规则：**
1. VERTICAL 容器内背景底板 → ABSOLUTE
2. VERTICAL 容器内子 FRAME → `layoutSizingHorizontal: FILL`
3. 弹性缝隙：`{ "type": "FRAME", "name": "弹性缝隙", "layoutMode": "NONE", "layoutSizingHorizontal": "FILL", "w": 0, "h": 0 }`
4. 唯一大空档用弹性缝隙，多均等空档用 SPACE_BETWEEN

---

## 导航栏建模（双态组件）

每个屏幕的导航栏：
- **当前页 Tab** → `导航栏_页面切换_选中` + overrides `{"内容_标签": "文字"}`
- **其他 Tab** → `导航栏_页面切换_未选中` + 有角标时 `{"数字_角标": "数字"}`
- 按钮统一命名 `导航_项N`

状态切换（屏内Tab）：
- 选中 → `导航栏_状态切换_选中` + `{"文本_Selected": "文字"}`
- 未选中 → `导航栏_状态切换_未选中` + `{"文本_Selected": "文字"}`
- 状态切换 Tab 若有附加元素（倒计时等），用 NONE 容器包裹，参见「component_ref 叠加结构」

---

## 语义路由 Flow

1. 读取选中态 `导航_项N` 的 overrides `内容_标签` 值
2. 语义映射到 screens 中的屏幕名
3. **N 个已识别屏幕 → N×(N-1) 条 slide 300ms 连线**（全量连线，不遗漏）
4. 只写视频中实际出现的目标屏幕，未出现的屏幕不写
5. 状态切换**不生成 flow**
6. 全屏跳转 → dissolve 300ms
7. 浮层打开 → dissolve 300ms (OVERLAY)，关闭 → to 空字符串 (CLOSE)

---

## children 顺序

**从底到顶排序。** 底板/背景在前，内容/按钮在后。NONE 父容器内的关闭/信息按钮必须放 children 最后，否则被遮挡。

---

## 滚动容器

三条件缺一不可：
1. 父容器：`overflow: "VERTICAL"` + `clip_content: true` + `primaryAxisSizingMode: "FIXED"`
2. 子容器：`primaryAxisSizingMode: "AUTO"` + **w 必须显式指定** + `layoutSizingVertical: "HUG"`（内容自撑）
3. 子 h > 父 h

⚠️ **字段名是 `clip_content`（下划线），不是 `clipsContent`（驼峰）** — 详见下方"字段命名铁律"章节。

⚠️ **生成后必须在 Figma 里手动滚一下验证**：
- 正确表现：顶部固定区不动,只有滚动区内容移动
- 若顶部固定区跟着滚动 → 99% 是 `clip_content` 字段名写错(写成 `clipsContent`),插件读不到

---

## 字段命名铁律（生成 JSON 前必读）

插件 `code.js` 里有些字段读下划线，有些读驼峰，**必须对照插件实现严格写，不要想当然按 Figma API 写**。

**读下划线的字段：**

| 字段 | 错误写法 | 用途 |
|---|---|---|
| `clip_content` | ~~`clipsContent`~~ | 裁切子节点（滚动容器必需）|
| `corner_radius` | ~~`cornerRadius`~~ | 圆角半径 |
| `font_size` | ~~`fontSize`~~ | TEXT 字号 |
| `font_weight` | ~~`fontWeight`~~ | TEXT 粗细 |
| `component_ref` | ~~`componentRef`~~ | 组件库引用 key |

**读驼峰的字段（按 Figma API）：**

| 字段 | 用途 |
|---|---|
| `layoutMode` | NONE / HORIZONTAL / VERTICAL |
| `primaryAxisSizingMode` / `counterAxisSizingMode` | FIXED / AUTO |
| `primaryAxisAlignItems` / `counterAxisAlignItems` | MIN / CENTER / MAX / SPACE_BETWEEN |
| `layoutSizingHorizontal` / `layoutSizingVertical` | FIXED / HUG / FILL |
| `textAlignHorizontal` / `textAlignVertical` | LEFT / CENTER / RIGHT / TOP / BOTTOM |
| `paddingLeft` / `paddingRight` / `paddingTop` / `paddingBottom` | 内边距 |
| `itemSpacing` | AL 子元素间距 |
| `overflow` | VERTICAL / HORIZONTAL / NONE |
| `layoutPositioning` | ABSOLUTE（AL 容器内）|
| `constraints` | `{ horizontal: SCALE/LEFT/RIGHT/CENTER, vertical: SCALE/TOP/BOTTOM/CENTER }` |

**判断字段命名的唯一正确方法：** 在 `code.js` 里 grep `layer.xxx` 查看插件实际读取哪个键名。例如：

```js
// code.js L381:
fr.clipsContent = !!layer.clip_content;  ← 插件读 clip_content

// code.js L380:
if (layer.corner_radius) fr.cornerRadius = layer.corner_radius;  ← 读 corner_radius
```

Figma 节点属性本身在 Figma API 里叫 `clipsContent`/`cornerRadius`（驼峰），但**插件 JSON 输入端读的是下划线**。这是 `.red` 文件格式规范决定的,不是 Figma API。

**命名错误的后果**: 字段被插件忽略,**完全不生效**。表现上看 JSON "格式正确",实际缺少关键属性。本轮 `clipsContent` 错写导致 Easter Pass 整屏跟着滚动就是这个原因。

---

⛔ 输出完成后立即停止，等待回复「继续S6」
