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

## 底板分离（手搓节点）

### 手搓按钮内容居中铁律

所有手搓按钮内部**必须**使用 `内容区_` FRAME 承载内容，**禁止用估算绝对坐标放置内容**：

```
底板_xxx (FRAME NONE)                             ← FRAME 类型 = 按钮外壳（透明）
├── 底板_xxx形状 (RECTANGLE, x=0, y=0, SCALE/SCALE) ← RECTANGLE + 含"形状" = 按钮内层（分级灰）
└── 内容区_xxx (FRAME AL, x=0, y=0, w=按钮w, h=按钮h,
      layoutMode: HORIZONTAL 或 VERTICAL,
      primaryAxisSizingMode: FIXED, counterAxisSizingMode: FIXED,
      primaryAxisAlignItems: CENTER, counterAxisAlignItems: CENTER,
      constraints: SCALE/SCALE)
    └── 所有子元素（图标、文字等）← 不写 x/y
```

❌ 禁止：
```json
{ "type": "TEXT", "name": "文本_开始", "x": 150, "y": 45, "content": "開始" }
```

### 按钮在 NONE 父容器内
```
组_xxx (FRAME NONE, 无fill)
├── 底板_xxx (FRAME NONE, 无fill)                   ← 按钮外壳 FRAME
│   ├── 底板_xxx形状 (RECTANGLE, corner_radius)     ← 按钮内层（含"形状"）
│   └── 内容区_xxx (FRAME AL, 无fill)
│       └── children...
```

### 外层容器底板（卡片 / 弹窗 / 大区域）
```
容器_xxx (FRAME NONE)
├── 底板_xxx (RECTANGLE, corner_radius)              ← RECTANGLE + 不含"形状" = 外层容器底板（中深灰）
└── 其他内容 (文本 / 图片 / 按钮 / ...)
```
与按钮外壳 FRAME 共用命名 `底板_xxx`，靠节点类型区分。

### AL 父容器内
```
底板_背景形状 (RECTANGLE, layoutPositioning: ABSOLUTE, x:0 y:0)
```
注意：`layoutPositioning: ABSOLUTE` 仅在 AL 容器内使用，NONE 容器内不写。

---

## component_ref 叠加结构

当 component_ref 上有视觉叠加元素（角标、倒计时、徽章等），必须用专属 NONE 小组包裹。

**专属小组尺寸原则：对外 w/h = 主体 w/h，附加元素溢出不撑大小组，主体用 x/y 偏移让位。**

**附加元素约束铁律：一律 LEFT/TOP，坐标全正数。禁止 RIGHT/CENTER/负数坐标（会导致元素飞出）。**

**附加元素位置确认（防止居中/左对齐误判）：**
```
居中期望 x = (主体w - 附加w) / 2
实际量测 x_actual（相对主体左边缘）
|x_actual - x| < 10px → 居中，x 用计算值
偏差 > 10px → 左/右对齐，x 用量测值
（无论哪种，constraints 都写 LEFT/TOP）
```

**四种常见场景：**

| 场景 | 专属小组 w/h | 主体 x/y | 附加元素 x/y | constraints |
|---|---|---|---|---|
| 右上角角标溢出顶部 | 主体w × 主体h | 0, 角标h/2 | 主体w-角标w/2, 0 | LEFT/TOP |
| 角标正上方居中 | 主体w × 主体h | 0, 溢出量 | (主体w-角标w)/2, 0 | LEFT/TOP |
| 底标下方居中溢出 | 主体w × 主体h | 0, 0 | (主体w-附加w)/2, 主体h+间距 | LEFT/TOP |
| 右上角内侧不溢出 | 主体w × 主体h | 0, 0 | 主体w-角标w-偏移, 偏移 | LEFT/TOP |

```
专属小组结构示意（右上角角标，主体h=231，角标h=34）：

组_活动_花朵 (NONE, w=170, h=231)  ← 对外h=主体h，不含角标溢出
├── 活动_花朵 (component_ref, x=0, y=17)  ← y=角标h/2=17，往下让位
└── 角标_数字1 (FRAME NONE, x=136, y=0, constraints: LEFT/TOP)  ← y=0，溢出顶部
    ├── 底板_角标 (RECTANGLE)
    └── 文本_角标 (TEXT)

专属小组结构示意（底标下方，主体h=99）：

组_Tab_Weekly (NONE, w=219, h=99)  ← 对外h=主体h，不含底标
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
1. 父容器：`overflow: "VERTICAL"` + `clipsContent: true` + `primaryAxisSizingMode: "FIXED"`
2. 子容器：`primaryAxisSizingMode: "AUTO"` + **w 必须显式指定**
3. 子 h > 父 h

---

⛔ 输出完成后立即停止，等待回复「继续S6」
