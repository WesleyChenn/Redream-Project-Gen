# S0 · 核心铁律（贯穿全流程，每步必读）

---

## 命名枚举锁（Enum Whitelist）

所有 JSON 节点 `name` 前缀必须且只能来自以下白名单，违反即为幻觉错误：

`界面_` `浮层_` `组_` `底板_` `内容区_` `内容_` `容器_` `导航_` `列表项_` `网格行_` `网格项_` `弹窗_` `按钮_` `图片_` `图标_` `背景_` `遮罩_` `文本_` `文字_` `弹性缝隙` `角标_` `徽章_` `进度_` `进度条_` `Tab_` `Toggle_` `请求_` `消息项_` `活动_` `底标_`

> 注: `进度条_` 是 v20.4 进度条建模铁律(双层 RECT 中的"填充层")的强制要求,
> 必须在白名单内。早期 skill 误漏,此版本补上。

### 按钮识别铁律（v20，与 Redream 引擎对齐）

**引擎只识别 `按钮_xxx` FRAME 为触控层（REDNodeButton），其他任何命名都不会被识别为按钮。**

| 视觉角色 | 节点类型 | 命名 | 引擎识别 | 插件上色 |
|---|---|---|---|---|
| **真正的按钮（可点击触控层）** | `FRAME` | `按钮_xxx` | REDNodeButton ✅ | 透明 |
| **按钮内层底板**（按钮内的视觉装饰底） | `RECTANGLE` | `底板_xxx`（父是 `按钮_xxx` FRAME）| CCSprite | 最浅灰（按按钮后缀可分级）|
| **外层容器底板**（卡片 / 弹窗 / 面板底，不可点击）| `RECTANGLE` | `底板_xxx`（父非按钮）| CCSprite | 中深灰 |
| **装按钮的容器**（纯分组，不是按钮）| `FRAME` | `组_xxx` / `容器_xxx` / `弹窗_xxx` | CCNode | 透明 |
| **组件库按钮**（圆形按钮/方形按钮/椭圆按钮 等）| `INSTANCE` 节点 | `component_ref`（非 `按钮_` 开头）| 组件库 | 组件自维护 |

**区分机制：**
- 按钮识别：**只有 name 严格以 `按钮_` 开头的 FRAME** 会被识别为按钮触控层
- 两种 `底板_xxx` RECT（按钮内层 vs 外层容器）靠**父节点类型**区分灰度
- 组件库按钮（`圆形按钮_xxx` 等）**不以 `按钮_` 开头**，不经过按钮识别路径

**强制规则：**
- 手搓按钮外壳一律用 `按钮_xxx` FRAME
- 按钮内层装饰底板用 `底板_xxx` RECT（不加"形状"后缀，不用 FRAME 包装）
- 装按钮的容器一律用 `组_xxx` / `容器_xxx` 等非按钮前缀，**禁止用 `底板_` 开头**
- 卡片 / 弹窗的视觉底板一律用 `底板_xxx` RECT，**不要用 FRAME**

**嵌套按钮冲突警告（组件库维护铁律）：**

一个 `按钮_xxx` FRAME 内部**禁止再嵌套另一个 `按钮_` 前缀的 FRAME**（通过 component_ref 间接嵌套也不行）。若出现嵌套,引擎行为不可预测：可能只识别外层 / 只识别内层 / 两层都触发导致冲突。

**常见引发场景**：
- 组件库里某组件被误命名为 `按钮_xxx`（例如 `椭圆按钮_活动` 内部若有一个节点叫 `按钮_开始`）
- 外层按钮包装一个 component_ref,而该 ref 内部 FRAME 里又有 `按钮_` 前缀的子节点

**防御措施**：
1. 组件库内部**子节点命名一律不用 `按钮_` 开头**,用 `活动按钮_xxx` / `按钮组_xxx` / `按钮_底板` 等替代
2. 组件 key 本身可以叫 `圆形按钮_关闭` / `矩形按钮_纯文本` 等（作为 key 名被引用,不进入 is_btn_layer 识别路径）
3. 生成 JSON 后做一次嵌套检查：任何 `按钮_xxx` FRAME 的 children 递归里不应再出现 `按钮_` 开头的 FRAME

**当前组件库状态**（本项目）：
- ✅ `椭圆按钮_活动` 内部用 `活动按钮_xxx`,安全
- ✅ `圆形按钮_xxx` 内部用 `按钮_xxx_底板` 等,不是纯 `按钮_xxx`,安全
- ⚠️ 若未来组件库改动将某内部节点命名为纯 `按钮_xxx` 开头,会触发嵌套冲突

### 按钮分组铁律（装饰必须与按钮一起响应点击）

**所有视觉上与按钮绑定的装饰附件，必须作为按钮 FRAME 的 children**，这样引擎点击时整组一起响应反馈。

附件包括：**角标、徽章、底标（倒计时 / 进度）、贴纸、Popular 标签、数字提示** 等。

**正确结构：**
```
按钮_活动紫罐 (FRAME)         ← 触控层 REDNodeButton
├── 底板_紫罐 (RECTANGLE)      ← 按钮内层装饰底板
├── 图标_紫罐
├── 文本_时间 "2d 4h"
└── 角标_感叹号                ← 装饰附件,作为子节点一起响应点击反馈 ✅
```

**错误结构（兄弟关系，装饰不跟随按钮变换）：**
```
组_活动_紫罐 (FRAME NONE)
├── 按钮_活动紫罐 (FRAME)      ← 按钮
└── 角标_感叹号                ← 兄弟,点击时不跟随按钮变换 ❌
```

**特殊情况：component_ref + 装饰（做法 B）**

当按钮主体是组件库 `component_ref`（如 `椭圆按钮_活动`）且需要添加装饰角标时，用**父按钮 FRAME 包装法**：

```
按钮_活动紫罐 (FRAME)          ← 外层按钮触控层 REDNodeButton
├── 活动_紫罐 (component_ref)  ← 主体视觉,组件库引用
└── 角标_感叹号                ← 装饰,作为子节点一起响应点击反馈 ✅
```

外层按钮 FRAME 不需要独立的 `底板_xxx` RECT，视觉依赖 component_ref 提供。

### 按钮触控范围铁律（v20，引擎侧行为）

**引擎约定**：按钮的触控范围 = 该 `按钮_xxx` FRAME 自身的 `w × h` 矩形范围。装饰（角标/徽章/底标）视觉上可以"溢出"按钮 FRAME 边界，但**溢出部分不在触控范围内**，那块区域点击无反馈。

**设计取舍**：
- 列表/网格里的按钮必须视觉对齐 → 所有同类按钮的 FRAME 尺寸应该**统一**
- 但装饰的大小/位置因按钮而异（有角标/有底标/无装饰等）
- 如果为"让装饰溢出区域也能点"而扩大每个按钮的 FRAME，会导致 FRAME 尺寸不齐、对齐错乱

**规则（对齐优先）**：

1. **按钮 FRAME 尺寸 = 主体尺寸**（不扩大去包装饰溢出部分）
2. **装饰仍然必须作为按钮 children**（按钮分组铁律：和按钮一起视觉反馈/缩放/移动）
3. **装饰允许视觉上溢出 FRAME 边界**（用负坐标或 y+h 超出按钮 h 都可以）
4. **接受的代价**：溢出在 FRAME 边界外的装饰区域**点击不触发按钮反馈**（但用户目标是点按钮主体，这个代价可接受）

**正确示例**：

```
右上角角标溢出顶部,按钮 FRAME h 不扩大

按钮_活动紫罐 FRAME (w=205, h=238)   ← 和其他活动按钮 h 相同,对齐
├── 主体 (x=0, y=0, h=238)            ← 主体占满按钮 FRAME
└── 角标 (x=143, y=-15, h=34)         ← 负坐标,视觉溢出顶部

点击主体(0..238)→ 触发按钮 ✅
点击角标凸出部分(y<0)→ 无反馈 ❌(可接受)
整个按钮和装饰一起缩放/移动/视觉反馈 ✅(装饰在 children 内)
```

**为什么不"扩大按钮 h 包住溢出"**：

```
❌ 错误做法: 为了让角标也能点,扩大按钮 h
按钮_活动紫罐 FRAME (w=205, h=253)   ← 比 h=238 大了 15
按钮_活动盾牌 FRAME (w=205, h=244)   ← 角标小一点,按钮也小一点
按钮_活动花朵 FRAME (w=205, h=263)   ← 有底标,按钮更大
→ 所有按钮 FRAME 尺寸全不一样,AL 对齐错乱,视觉参差不齐 ❌
```

**按钮分组铁律的真正含义**（避免误解）：
- ✅ 装饰作为 children → 装饰和按钮一起响应视觉反馈（缩放/位移/透明度等）
- ❌ **不等于**：装饰溢出区域也要能触发点击

`children` 关系决定**视觉层次和一体动画**,**不决定触控范围**。触控范围只由 FRAME 自身的 w×h 决定。

### 按钮判断清单（生成 JSON 前自问）

对每个视觉元素走一遍清单，判断是否是按钮：

```
□ 有独立视觉边界（底板 / 描边 / 色块对比）?
    └ 无 → 不是按钮,是装饰 / 显示
    └ 有 ↓

□ 是规则形状（矩形 / 圆 / 胶囊 / 圆角方）?
    └ 否（自由形状 / 场景图 / 大插图）→ 是装饰图,不是按钮
    └ 是 ↓

□ 和相邻元素紧贴?（间距 < 元素自身宽度）
    └ 紧贴 → 与相邻元素合并为**一个**按钮
    └ 独立 ↓

□ 在导航栏里?
    └ 是 → 每项独立按钮（反例规则）
    └ 否 ↓

□ 有可操作语义?（Claim / Start / Action / Level xxx / 数字+号 / OPEN 等）
    └ 有 → 按钮
    └ 纯显示（单纯数字 / 图标 / 标题文字）→ 不是按钮
```

**合并 vs 独立判断示例**（按紧贴/语义规则推演出的典型场景）:

| 场景 | 处理 | 示例 |
|---|---|---|
| HUD 资源栏（金币图标+数字+加号紧贴）| **整栏合并为 1 个按钮** | `按钮_金币栏`（含 图标_金币 + 文本_860 + 角标_加）|
| HUD 心栏（心+数字+加号+倒计时）| **整栏合并为 1 个按钮** | `按钮_心栏`（含 心图标 + 4 + 加 + 22:00）|
| 大进度条（胶囊+文字+倍数角标+倒计时）| **整条合并为 1 个按钮** | `按钮_活动进度`（含 小火车 + 873/1000 + x2 + 22:43）|
| 地图活动按钮（椭圆+角标+底标）| **一个大按钮** | `按钮_活动紫罐`（含主体 + 角标 + 倒计时）|
| 导航栏 5 个 Tab | **每个独立按钮**（反例）| `导航_项1` / `导航_项2` / ... |
| Stage 1-5 Tab | **每个独立按钮**（反例）| `按钮_Tab_Stage1` / `按钮_Tab_Stage2` / ... |

**规则总结**：
- 紧贴的元素组合 = 合并为 1 个按钮（HUD 资源栏、进度条、活动按钮）
- 平行排列的同类切换项 = 每个独立（导航栏、Tab 栏、页签）

**识别方法**：如果这一组里的元素**语义上是一体的**（"我要充金币就点金币栏整条"），合并；如果**每项有独立语义**（"我要切到 Weekly Tab"），独立。

**生成过程中遇到不确定的按钮边界，向用户提问确认，不猜测。**

### 按钮内层底板语义后缀（插件上色可选分级）

当 `按钮_xxx` FRAME 内的 `底板_xxx` RECT 需要按按钮类型区分深浅时，按钮 FRAME 的后缀决定内层灰度：

| `按钮_` 后缀包含 | 场景 | 内层底板灰度 | 示例命名 |
|---|---|---|---|
| `弹窗` / `浮层` | 弹窗级按钮 | 最深 | `按钮_弹窗关闭` |
| `Toggle` / `卡片` | Toggle / 卡片按钮 | 中灰 | `按钮_Toggle音量` |
| `开关` | 开关控件 | 较浅 | `按钮_开关音量` |
| 其余（动作名 / 功能名）| 普通按钮 | 最浅 | `按钮_开始` / `按钮_Claim` |

```
✅ 按钮_开始         ← 普通按钮,内层最浅灰
✅ 按钮_弹窗关闭     ← 弹窗级按钮,内层最深灰
❌ 按钮_1            ← 无语义后缀
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
按钮_xxx FRAME (NONE, 固定w/h)                         ← v20: "按钮_" 前缀 = 触控层 REDNodeButton
├── 底板_xxx RECTANGLE (x=0, y=0, SCALE/SCALE)         ← 按钮内层装饰底板（RECT,父是按钮 → 最浅灰）
├── (可选) 图标_xxx / 图片_xxx
├── (可选) 文本_xxx
└── (可选) 角标_xxx / 徽章_xxx / 底标_xxx              ← 装饰附件,一起响应点击反馈
```

**三条核心规则：**
1. **按钮外壳**：`按钮_xxx` FRAME（不是 `底板_xxx`，不是 RECT）
2. **按钮内层底板**：`底板_xxx` RECT（不加"形状"后缀，父是 `按钮_` 时插件自动上最浅灰）
3. **按钮内容**：全部作为按钮 FRAME 的 children，点击时一起响应反馈

**关于 `内容区_` FRAME（可选使用）：**
- 当按钮内有多个子元素需要自动居中排列时，可以在按钮 FRAME 内加一个 `内容区_xxx` FRAME（HORIZONTAL/VERTICAL AL，CENTER/CENTER）来组织内容
- 简单按钮（单一文字或单一图标）不需要 `内容区_`，子元素直接作为按钮 FRAME 的 children，用绝对坐标或 AL 任选

**正确示例（带内容区，自动居中）：**
```json
{
  "type": "FRAME", "name": "按钮_开始",
  "w": 446, "h": 150, "layoutMode": "NONE", "corner_radius": 75,
  "children": [
    { "type": "RECTANGLE", "name": "底板_开始",
      "x": 0, "y": 0, "w": 446, "h": 150, "corner_radius": 75,
      "constraints": { "horizontal": "SCALE", "vertical": "SCALE" } },
    { "type": "FRAME", "name": "内容区_开始",
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

**正确示例（带装饰角标,一起响应点击反馈）：**
```json
{
  "type": "FRAME", "name": "按钮_活动紫罐",
  "w": 163, "h": 213, "layoutMode": "NONE",
  "children": [
    { "type": "RECTANGLE", "name": "底板_活动紫罐",
      "x": 0, "y": 0, "w": 163, "h": 213, "corner_radius": 80,
      "constraints": { "horizontal": "SCALE", "vertical": "SCALE" } },
    { "type": "RECTANGLE", "name": "图片_紫罐",
      "x": 20, "y": 20, "w": 123, "h": 170,
      "constraints": { "horizontal": "LEFT", "vertical": "TOP" } },
    { "type": "FRAME", "name": "角标_感叹号",
      "x": 115, "y": 0, "w": 56, "h": 58, "layoutMode": "NONE",
      "constraints": { "horizontal": "LEFT", "vertical": "TOP" },
      "children": [
        { "type": "RECTANGLE", "name": "底板_角标感叹号",
          "x": 0, "y": 0, "w": 56, "h": 58, "corner_radius": 29,
          "constraints": { "horizontal": "SCALE", "vertical": "SCALE" } }
      ]
    }
  ]
}
```

**❌ 常见错误：**
```json
// 错误 1：按钮用 底板_ FRAME（v19 老命名，v20 应改为 按钮_）
{ "type": "FRAME", "name": "底板_开始按钮" }
// 应为：
{ "type": "FRAME", "name": "按钮_开始" }

// 错误 2：内层底板还在用"形状"后缀（v19 老命名，v20 去掉后缀）
{ "type": "RECTANGLE", "name": "底板_开始按钮形状" }
// 应为：
{ "type": "RECTANGLE", "name": "底板_开始" }

// 错误 3：装饰角标和按钮平级（不会跟随按钮变换）
{ "name": "组_活动_紫罐", "children": [
  { "name": "按钮_活动紫罐", ... },
  { "name": "角标_感叹号", ... }   // ❌ 兄弟关系
]}
// 应为：
{ "name": "按钮_活动紫罐", "children": [
  { "name": "底板_活动紫罐" },
  { "name": "角标_感叹号" }         // ✅ 作为按钮 children
]}

// 错误 4：TEXT 用绝对坐标估算放在按钮内
{ "type": "TEXT", "name": "文本_开始", "x": 150, "y": 45 }
// 应放在内容区_ 内,由 AUTO LAYOUT CENTER 自动居中
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
- **component_ref + 装饰**：用 `按钮_xxx` FRAME 包装（做法 B），装饰作为按钮 children

---

## 两类节点

| 类型 | 按钮结构 | 内部内容 |
|---|---|---|
| **component_ref** | 若需添加装饰，用 `按钮_xxx` FRAME 包装 | 组件库自维护，装饰作为按钮 children |
| **手搓节点** | 强制：`按钮_xxx FRAME` + `底板_xxx RECT`（+ 可选 `内容区_ FRAME`）| 所有内容作为按钮 children,装饰一起响应按钮变换 |

---

## 进度条建模铁律（v20.4，与 Redream 引擎对齐）

进度条是引擎侧 `CCProgressTimer` 节点,**不允许用 FRAME 包装的伪结构**。组件库的 `进度条_短` / `进度条_宽` 是 FRAME 包装,**与引擎不兼容,一律改为手搓**。完整规则见下方各小节。

### 进度条建模铁律（v20.4 三层结构 + 内缩 + 中心对齐）

#### 一、识别规范

**视觉特征**: 胶囊条 + 进度数字(如 873/1000),已达色(绿/金) + 未达色(蓝/灰)双层叠加。

**与按钮内层底板的区分**:
- 进度条 = **底板 + 进度条 配对出现**(双层 RECT)
- 按钮内层底板 = **单独**(只有底板,无配对填充层)
- 通过**外层 `组_进度_` 包装层**区分,内部底板和按钮内层底板可以同名(在不同父 FRAME 内,引擎按路径识别)

#### 二、命名规范

**核心规则:"进度"二字只出现在外层包装 FRAME,内部底板/进度条 XXX 保持简洁**。

```
组_进度_<XXX>[_<方向后缀>]      ← 外层包装,带"进度"二字提示这是进度条单元
└── 底板_<XXX>[_<方向后缀>]     ← 内部底板,XXX 不重复带"进度"
└── 进度条_<XXX>[_<方向后缀>]   ← 内部填充,XXX 不重复带"进度"
```

**为什么这么设计**:
- "进度"是给读图人看的语义提示(让人一眼看出这是进度条),放在外层包装上即可
- 引擎识别靠 `底板_` / `进度条_` 前缀,不需要内部 XXX 含"进度"
- 内部命名简洁,降低嵌套时的视觉噪音

**三层 XXX 必须完全一致**(包括方向后缀,但"进度"二字只在外层):
- ✅ `组_进度_经验` + `底板_经验` + `进度条_经验`
- ✅ `组_进度_活动` + `底板_活动` + `进度条_活动`
- ✅ `组_进度_EasterPass19_tb` + `底板_EasterPass19_tb` + `进度条_EasterPass19_tb`
- ❌ `组_进度_经验进度` + `底板_经验进度` + `进度条_经验进度`(内部冗余加"进度")
- ❌ `组_进度_经验` + `底板_经验进度`(三层 XXX 不一致)

**XXX 同屏唯一规则**:
- 同一父 FRAME 内,XXX 唯一
- 不同父 FRAME 内,XXX 可以同名(引擎按路径识别,不会混淆)
  - 例: 同屏有 `按钮_活动` 和 `组_进度_活动`,内部都有 `底板_活动` —— OK,因为父 FRAME 不同

**方向后缀**(99% 场景默认横向左→右,不加):
| 后缀 | 方向 |
|---|---|
| (无) | `horizontal_lr` 水平左→右(默认) |
| `_rl` | `horizontal_rl` 水平右→左 |
| `_bt` | `vertical_bt` 垂直下→上 |
| `_tb` | `vertical_tb` 垂直上→下 |

⚠️ 环形进度条暂不支持(barType=1 Radial 引擎未实现)。

#### 三、图层规范

**三层嵌套结构**:

```
组_xxx (FRAME, 不可点击) 或 按钮_xxx (FRAME, 可点击) ← 外层容器
├── 组_进度_XXX (FRAME)              ← 包装层(含"进度"二字)
│   ├── 底板_XXX (RECTANGLE)         ← Z 序低,XXX 不带"进度"
│   └── 进度条_XXX (RECTANGLE)       ← Z 序高,XXX 不带"进度"
├── (可选) 文本_xxx (TEXT)            ← 文本是外层容器的兄弟,不进 组_进度_
└── (可选) 图标_xxx 或 component_ref  ← 图标也是兄弟
```

**Z 序铁律**: children 数组里 `进度条_XXX` 的 index 必须 > `底板_XXX` 的 index(进度条覆盖在底板之上)。

**包装 FRAME 尺寸 = 底板尺寸**: `组_进度_XXX` 的 w/h 等于 `底板_XXX` 的 w/h(包装层视觉上和底板一样大,只是分组用)。

**🔴 尺寸规范(底板大,进度条小,内缩中心对齐)**:

`进度条_XXX` RECT 必须**小于** `底板_XXX` RECT,内缩中心对齐:
- 进度条 RECT 表达"100% 满时填充内容的视觉区域"(不含底板边框)
- 底板边框/描边由底板 RECT 显示
- 引擎按 percentage 切割时,在进度条 RECT 范围内切割,不会盖到底板边框

**内缩量规则**(按底板尺寸分级):

| 底板尺寸范围 | 横向内缩(每边) | 纵向内缩(每边) |
|---|---|---|
| 大 (w≥200, h≥80) | 10px | 10px |
| 中 (100≤w<200, 50≤h<80) | 8px | 5px |
| 小 (w<100, h<50) | 5px | 3-5px |

**中心对齐铁律**:
```
进度条 中心 = 底板 中心
即:
  进度条 x + 进度条 w / 2 = 底板 x + 底板 w / 2
  进度条 y + 进度条 h / 2 = 底板 y + 底板 h / 2
```

最简实现(进度条尺寸 = 底板 - 2×内缩):
```json
{ "type": "RECTANGLE", "name": "底板_活动",
  "x": 0, "y": 0, "w": 1040, "h": 95 },
{ "type": "RECTANGLE", "name": "进度条_活动",
  "x": 10, "y": 10, "w": 1020, "h": 75 }   ← 横纵各内缩 10px,中心自动对齐
```

中心点验证: 底板中心 (520, 47.5) = 进度条中心 (520, 47.5) ✅

❌ 禁止: 进度条 = 底板 同尺寸同位置(看不到底板边框,失去视觉区分)
❌ 禁止: 进度条偏离底板中心(左对齐/右对齐/顶对齐)

#### 四、容器规范

| 容器类型 | 何时用 | 命名 |
|---|---|---|
| 不可点击 | 纯展示进度(关卡进度、HP 条等) | `组_xxx` FRAME |
| 可点击 | 整条点击触发交互(如点进度条进入活动详情) | `按钮_xxx` FRAME |

可点击进度条遵循 v20 按钮分组铁律: 所有 children(包装 FRAME / 文本 / 图标)作为 `按钮_xxx` FRAME 的子节点,一起响应点击变换。

**文本 / 图标位置**: 作为**外层容器**的兄弟元素,**不放进 `组_进度_xxx` 包装内**。

```json
✅ 正确(文本/图标在外层,与包装 FRAME 同级):
{ "type": "FRAME", "name": "按钮_活动进度",
  "children": [
    { "type": "FRAME", "name": "组_进度_活动进度",
      "children": [
        { "type": "RECTANGLE", "name": "底板_活动", ... },
        { "type": "RECTANGLE", "name": "进度条_活动", ... }
      ]
    },
    { "type": "TEXT", "name": "文本_活动进度", ... },        ← 兄弟
    { "component_ref": "角标_x2", "name": "角标_x2", ... }    ← 兄弟
  ]
}

❌ 错误(把文本/图标放进包装 FRAME 内):
{ "type": "FRAME", "name": "组_进度_活动进度",
  "children": [
    { "type": "RECTANGLE", "name": "底板_活动", ... },
    { "type": "RECTANGLE", "name": "进度条_活动", ... },
    { "type": "TEXT", "name": "文本_活动进度", ... }    ← 不应放这
  ]
}
```

#### 五、引擎侧 cocos2d-x 翻译表（仅供引擎实现参考）

| Figma direction | barType | midpoint | barChangeRate |
|---|---|---|---|
| `horizontal_lr` | 0 | [0, 0.5] | [1, 0] |
| `horizontal_rl` | 0 | [1, 0.5] | [1, 0] |
| `vertical_bt` | 0 | [0.5, 0] | [0, 1] |
| `vertical_tb` | 0 | [0.5, 1] | [0, 1] |

#### 六、完整示例

**手搓不可点击进度条(组_xxx 包装,横向)**:
```json
{ "type": "FRAME", "name": "组_进度_经验",
  "w": 600, "h": 60, "layoutMode": "NONE",
  "children": [
    { "type": "RECTANGLE", "name": "图标_左_钥匙",
      "x": 0, "y": 5, "w": 50, "h": 50 },
    { "type": "FRAME", "name": "组_进度_经验进度",
      "x": 50, "y": 10, "w": 500, "h": 40, "layoutMode": "NONE",
      "children": [
        { "type": "RECTANGLE", "name": "底板_经验",
          "x": 0, "y": 0, "w": 500, "h": 40, "corner_radius": 20 },
        { "type": "RECTANGLE", "name": "进度条_经验",
          "x": 10, "y": 5, "w": 480, "h": 30, "corner_radius": 15 }
      ]
    },
    { "type": "TEXT", "name": "文本_经验进度", "content": "5/600", ... }
  ]
}
```

**手搓可点击进度条(按钮_xxx 包装,横向)**:
```json
{ "type": "FRAME", "name": "按钮_活动进度",
  "w": 1040, "h": 140, "layoutMode": "NONE", "corner_radius": 47,
  "children": [
    { "type": "FRAME", "name": "组_进度_活动进度",
      "x": 0, "y": 20, "w": 1040, "h": 95, "layoutMode": "NONE",
      "children": [
        { "type": "RECTANGLE", "name": "底板_活动",
          "x": 0, "y": 0, "w": 1040, "h": 95, "corner_radius": 47 },
        { "type": "RECTANGLE", "name": "进度条_活动",
          "x": 10, "y": 10, "w": 1020, "h": 75, "corner_radius": 37 }
      ]
    },
    { "type": "TEXT", "name": "文本_活动进度数", "content": "873/1000", ... }
  ]
}
```

**列表型纵向进度条(每行一段,vertical_tb)**:
```json
{ "type": "FRAME", "name": "网格行_EasterPass_第19级",
  "children": [
    { "type": "FRAME", "name": "组_进度_EasterPass进度19_tb",
      "x": 510, "y": 0, "w": 60, "h": 364, "layoutMode": "NONE",
      "children": [
        { "type": "RECTANGLE", "name": "底板_EasterPass19_tb",
          "x": 0, "y": 0, "w": 60, "h": 364, "corner_radius": 30 },
        { "type": "RECTANGLE", "name": "进度条_EasterPass19_tb",
          "x": 5, "y": 10, "w": 50, "h": 344, "corner_radius": 25 }
      ]
    },
    { "type": "FRAME", "name": "按钮_奖励_L_19", ... },
    { "type": "FRAME", "name": "按钮_奖励_R_19", ... },
    { "type": "FRAME", "name": "图标_等级徽章_19", ... }
  ]
}
```

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

## 嵌套 CCB 铁律（大 CCB / 子 CCB，v20.7+）

复合视觉单元（如列表行、卡片、按钮组）必须按 **嵌套 CCB 模型**建模，**禁止把所有子元素摊平到外层 FRAME**。

### 模型

```
列表项 (大 CCB / 外层 Component)
├─ 排名圆 (子 CCB INSTANCE)
├─ 图片_头像 (单纯 RECT 占位,数据绑定)
├─ 角标_王冠 (子 CCB INSTANCE,可隐藏)
└─ 文本/分数 (TEXT/RECT 直接子节点)
```

- **大 CCB**：是被列表/网格复用的外层容器（如 `列表项_排名`）
- **子 CCB**：是大 CCB 内部可独立复用的子单元（如 `角标_王冠`、`排名圆`），自己也可能多 Variant
- **图片占位**：单纯 `图片_xxx` / `图标_xxx` RECT，运行时数据绑定，**不做 Variant**

### 子 CCB 显隐铁律（必读）

子 CCB INSTANCE 在不同行/卡的"出现/不出现"，**用 wrapper 节点的 `visible: true/false` 表达，不用增删 children**。

❌ **错误**：rank 5 行的 children 数组里加 `角标_王冠`，rank 6 行不加
- 后果：6 行 structural_fingerprint 不一致，extract_components 抽不出统一的 `列表项` Component

✅ **正确**：6 行 children 数组都包含 `角标_王冠`，需要隐藏的行写 `"visible": false`
- 6 行 structural_fingerprint 一致 → 抽成同 1 个 `列表项` Component
- visual_signature 因 `visible` 字段差异 → 自动分成 2 个 Variant
- extract_components 在替换 INSTANCE 时**会保留 wrapper 的 visible 字段**（v20.7+ 修复）→ 引擎按 INSTANCE.visible 决定是否渲染

### 例子

```json
{
  "type": "FRAME", "name": "列表项_排名6",
  "w": 1000, "h": 130,
  "children": [
    { "type": "RECTANGLE", "name": "底板_行", ... },
    { "type": "FRAME", "name": "排名圆", ... },          ← 子 CCB,所有行都有
    { "type": "RECTANGLE", "name": "图片_头像", ... },
    { "type": "FRAME", "name": "角标_王冠",              ← 子 CCB
      "visible": false,                                  ← rank 6 隐藏
      "children": [
        { "type": "RECTANGLE", "name": "底板_角标王冠", ... },
        { "type": "RECTANGLE", "name": "图标_王冠", ... }
      ]
    },
    { "type": "TEXT", "name": "文本_玩家名", "content": "mmmmm", ... }
  ]
}
```

### 阶段二抽取后的输出形态

```
components:
  列表项_排名 (Variant 常态):  ... INSTANCE 角标_王冠 visible=false  ...
  列表项_排名 (Variant 变体2): ... INSTANCE 角标_王冠 visible=true   ...
  角标_王冠 (单 Component): 自身 layers 里描述完整内容(底板 + 图标)
```

引擎渲染：
- 行 INSTANCE 选中 Variant `常态` → 内嵌 INSTANCE `角标_王冠` 的 `visible=false` → 不渲染王冠 ✅
- 行 INSTANCE 选中 Variant `变体2` → 内嵌 INSTANCE `角标_王冠` 的 `visible=true` → 渲染王冠 ✅

---

## Variant 内部建模铁律（v20.7+，与 extract_components 行为对齐）

抽取出来的 Component 经常带多个 Variant。Variant 内部数据如何组织有 3 条硬规则，写错了引擎要么渲染丢数据，要么时间线污染。

### 1. Variant.layers 只放该 Variant 实际可见的图层

**Figma 编辑期允许 visible 切换** —— 设计师方便开关元素。
**进 Variant.layers 时必须过滤 visible=false 节点** —— extract_components 的 `_filter_invisible` 自动做这件事，进引擎的时间线只剩可见层。

```json
flat_scene 输入(Figma 编辑期):
  列表项_排名6 children:
    - 底板_行
    - 排名圆 INSTANCE
    - 图片_头像
    - 角标_王冠 (visible: false)    ← 设计师标记隐藏
    - 文本_玩家名

final_scene 输出(进引擎):
  列表项_排名 Variant 常态 layers:
    - 底板_行
    - 排名圆 INSTANCE
    - 图片_头像
                                    ← 角标_王冠 已被 _filter_invisible 删除
    - 文本_玩家名
```

**❌ 错误**：把 visible=false 节点也写进 Variant.layers，靠引擎运行时切换可见性。
**✅ 正确**：visible=false 在 Variant 内**直接物理删除**，运行时不再存在。

### 2. wrapper 级的 visible / opacity 必须保留到 INSTANCE 节点

子 CCB 的 wrapper（即 INSTANCE 节点）在某个 Variant 里可能整体隐藏（例如 rank 1 没有物品架，rank 6 没有王冠）。这种"整个组件隐藏"的状态**必须保留在父 Variant 的 INSTANCE 节点上**，而不是擦掉。

```json
列表项_排名 Variant 常态 layers:
  ...
  {
    "type": "INSTANCE",
    "name": "角标_王冠",
    "component_name": "角标_王冠",
    "variant": "常态",
    "visible": false        ← wrapper 级别的 visible 必须传给 INSTANCE
  }
```

`extract_components._make_instance_node` 已自动复制 wrapper 的 `visible` / `opacity` 到 INSTANCE。手写 JSON 时也要遵守这条。

### 3. 实例间数据差异 → 每个 INSTANCE 节点上的 overrides

**6 行排行榜不能渲染同一个名字。** 每个 INSTANCE 节点必须自带 `overrides`，覆盖 Variant 模板里的对应字段。

```json
列表项_排名 Variant 常态 layers (模板):
  - 排名圆 INSTANCE (overrides: { 圆形容器_图标_文本: "8" })
  - 文本_玩家名: content="kibuntenkan"
  - 文本_分数: content="50"

屏幕里的 INSTANCE 引用:
  {
    "type": "INSTANCE",
    "name": "列表项_排名9",
    "component_name": "列表项_排名",
    "variant": "常态",
    "overrides": {                  ← 实例独立 override
      "排名圆": { "圆形容器_图标_文本": "9" },
      "文本_玩家名": "walid",
      "文本_玩家说明": "Inomoov",
      "文本_分数": "26"
    }
  }
```

`extract_components._collect_text_and_ref_overrides` 自动比对模板与实例，把差异提取到 INSTANCE.overrides。手写 JSON 时也要每个 INSTANCE 自带 overrides。

**已支持的 override 类型**：
- `TEXT` 节点的 `content` 文本差异
- `component_ref` 节点的 `overrides` 字段差异（嵌套结构）

**不支持的 override 类型**（差异需另作 Variant 处理）：
- 节点 size / position 差异
- fill / corner_radius / 视觉属性差异
- visible 差异（这种应该是不同 Variant，不是同 Variant 的实例差异）

---

## INSTANCE 尺寸同步铁律（v20.7+，与 Figma "Push to main component" 工作流对齐）

### 问题背景

设计师在屏幕里直接拖动 INSTANCE 边框改尺寸时，**Figma 默认不会把改动同步回 Component Set 本体**（这是 Figma "实例 vs 主版" 的设计哲学）。结果：

- `components[].w/h` = Component Set 本体尺寸（如 1020×479）
- `screens[].layers[INSTANCE].w/h` = 各自被拖过的尺寸（如 499/438/360）
- 引擎按数据如实生成 .red：父 CCNode 用 INSTANCE 尺寸，子 CCB 用 Component 尺寸
- → **父子尺寸不匹配，渲染视觉错位**

### 工作流铁律（每次改 INSTANCE 后必做）

1. 设计师在屏幕里直接改 INSTANCE 尺寸（直观）
2. 改完选中 INSTANCE
3. 右键 → **Push changes to main component**（中文："推送变更到主组件"）
   或快捷键 `⌥⌘Y`（macOS）/ `Alt+Ctrl+Y`（Windows）
4. 验证：所有引用同一 Component 的 INSTANCE 应**立即自动同步**到新尺寸；只有当前选中的变了说明没生效

### 生成 JSON 前自检（Claude 在 S5/S6 必查）

对 scene.json 里**每一个** `type: "INSTANCE"` 节点：

```
□ 同 component_name 的所有 INSTANCE 的 w/h 是否一致?
   不一致 → 设计师在屏幕里拖过尺寸但没 Push,要求设计师 Push 后重新导出

□ INSTANCE 的 w/h 是否等于对应 components[].w/h?
   不一致 → 同上,要求 Push
```

### 自检脚本（粘贴到终端跑）

```bash
python3 -c "
import json
d = json.load(open('flat_scene.json'))   # 或 final_scene.json
comp_size = {c['name']:(c['w'],c['h']) for c in d.get('components',[])}
by_comp = {}
def walk(n):
    if n.get('type')=='INSTANCE':
        cn = n.get('component_name','')
        by_comp.setdefault(cn,[]).append((n.get('name'),n.get('w'),n.get('h')))
    for ch in (n.get('children') or n.get('layers') or []): walk(ch)
for s in d.get('screens',[]):
    for L in s.get('layers',[]): walk(L)
issues=[]
for cn, insts in by_comp.items():
    sizes = set((w,h) for _,w,h in insts)
    if len(sizes)>1:
        issues.append(f'❌ {cn} 的 INSTANCE 尺寸不一致: {sizes}')
    cw,ch = comp_size.get(cn,(None,None))
    for nm,w,h in insts:
        if (cw,ch)!=(None,None) and (w,h)!=(cw,ch):
            issues.append(f'❌ {cn}/{nm} ({w}x{h}) 与 Component 本体 ({cw}x{ch}) 不一致 → Push 主版')
print('✅ 全部一致' if not issues else '\n'.join(issues))
"
```

### 引擎侧不修改

引擎按数据如实生成,**不做"猜测设计意图"的逻辑**(改起来风险大,容易把别的搞坏)。
这个问题必须从 Figma 端工作流解决,Claude/插件/extractor 三层都做检查并报错,但**不自动改尺寸**。

---

## S7 后必须 100% 嵌套化(v20.7.x+,从 RoyalPass 教训得来)

跑完 `extract_components.py` 后,主屏 `screens.layers` + 所有 Component `Variant.layers` 内部
**禁止存在 FRAME 是"应该被复用的结构"**(列表行/卡片/重复按钮组)。

### 现象(踩过的坑)

第一次 S7 输出 6 个 Component 抽出来时,部分行(如 RoyalPass 视频里的行 19/20)被算法判定为
"无法归类的特殊形态",直接保留成扁平 FRAME 留在主屏,跟其他 5/6 行的 INSTANCE 形态混在一起。
设计师粘到 Figma 后看到"前 2 行扁平 + 后 6 行引用"的奇怪混合结构。

### 自检脚本(交付前必跑)

```python
# 对每个"预期 ≥2 实例"的结构指纹,扫描 final_scene.json
# 主屏 list_inner.children 全部 type=INSTANCE  ✅
# 出现 type=FRAME 但跟某个 Component 结构指纹相同 → ❌ 漏网平铺
def find_orphan_frames(d):
    list_inner_candidates = [...]
    for parent in list_inner_candidates:
        for ch in parent.get('children', []):
            if ch.get('type') == 'FRAME':
                # 这是漏网的复用结构
                yield (parent, ch)
```

### 漏网时的修复路径(铁律)

| 处理 | 状态 |
|---|---|
| ✅ 把 FRAME 抽成新 Variant,转成 INSTANCE 引用 | **正确** |
| ✅ Variant 之间用 `visible` / `fill` 表达差异(SKILL 子 CCB 显隐铁律)| **正确** |
| ❌ 删除 Component,把所有 INSTANCE 还原为内嵌 FRAME | **禁止**(违反用户原始设计意图)|

### 为什么不能删 Component

`extract_components.py` 算法只识别 N 种主流"显隐组合",边缘组合(比如 RoyalPass 行 19 的"双侧对勾",
行 20 的"对勾+锁混合")会留作 FRAME。如果遇到 FRAME 漏网就走"删 Component"路径,会:

1. 违反用户最初对哪些做 Component 的设计决策
2. 引发后续 `combineAsVariants` 在其他 Component 上失败的连锁问题
   (因为引用关系变了,Variant 结构变了,触发新的"视觉签名相同"等问题)
3. 设计师在 Figma 看到组件库变少,又要回头复盘

正确做法是**加 Variant 让模型覆盖所有真实显隐组合**,Component 数量保持稳定。

---

## Component 修复铁律(combineAsVariants 失败时,v20.7.x+)

Figma `combineAsVariants` 是硬性约束:**至少 2 个 component + 视觉签名各不相同**。
违反任一就失败,Component Set 不创建,registry 里没有这个 Component,
引用它的外层 Component 也会连带失败(整个组件库渲染塌陷)。

### 失败的三种典型场景 + 正确修复

#### 场景 1:Component 只有 1 个 Variant

```
❌ 错误修复: 删除 Component,降级为内嵌 FRAME
✅ 正确修复: 加 dummy 第 2 Variant,用 fill / visible 制造视觉差异

例: 组_进度_行_tb (1 Variant 常态)
   → 加 2 个 Variant: 已达 fill=#7BC847 / 未达 fill=#888888
   → 进度条本体永远画 100% 满(SKILL 进度条铁律不变)
   → Variant 表达"已达 vs 未达"两个视觉状态,引擎按等级选 Variant
```

#### 场景 2:多个 Variant 视觉签名相同

```
现象: Variant A 和 Variant B 内部 layers 相同(types/names/fills 全等)
原因: _filter_invisible 把 visible=false 节点物理删了,本来差异就在 visible,过滤后变成完全一样

❌ 错误修复: 把两个 Variant 合并/删除
✅ 正确修复:
   - "显示/隐藏" 类差异 → 改成 INSTANCE.visible=false(SKILL 子 CCB 显隐铁律)
   - "格式不同/文字不同" → 用 fill 或 icon 添加视觉差异

例: 数量徽章 (显示/隐藏 → _filter 后内容相同)
   方案 A: 删除"隐藏"Variant,改成 INSTANCE.visible=false
   方案 B: 改成"x格式/m格式"两个真有视觉差异的 Variant(m格式底板红色,因为对应红心计时)
```

#### 场景 3:引用了未创建的 Component

```
原因: components[] 数组里子 Component 排在外层 Component 后面,buildV20_6_ComponentSets
     按数组顺序处理,处理外层时子 Component 还没注册到 registry,引用失败。

✅ 修复: 子 Component 必须排在引用它的 Component 前面。
   一般顺序: 最深的叶子 Component → 中层 Component → 最外层 Component
```

### 元铁律:删 Component 必须先和用户确认

Component 列表是用户的**设计决策**(哪些是可复用单元,哪些不是),工具限制是次要约束。

遇到 `combineAsVariants` 失败时:
1. 先尝试**加 Variant** 让 Component 能 combine
2. 不行才考虑跟用户讨论是否降级为内嵌 FRAME
3. **不擅自删除 Component** — 用户的"省事修复"标准跟工具的不一样

### Component 交付前自检脚本(必跑)

```python
# 对每个 Component 验证:
# 1. variants 数量 ≥ 2(否则 combineAsVariants 失败)
# 2. 每个 Variant 的视觉签名 hash 唯一(否则 combineAsVariants 失败)
# 3. INSTANCE 引用的 component_name 都在 components[] 里
# 4. components[] 顺序: 子 Component 在前,外层在后

import hashlib
def variant_signature(layers):
    parts = []
    def collect(L):
        for n in L:
            if isinstance(n, dict):
                parts.append(f"{n.get('type')}|{n.get('name')}|{n.get('fill','')}|{n.get('visible',True)}")
                if n.get('type')=='INSTANCE':
                    parts.append(f"INST|{n.get('component_name')}|{n.get('variant')}")
                for k in ('children','layers'):
                    if k in n: collect(n[k])
    collect(layers or [])
    return hashlib.md5(''.join(parts).encode()).hexdigest()[:8]

for c in d['components']:
    assert len(c['variants']) >= 2, f"{c['name']} 只有 {len(c['variants'])} Variant — combineAsVariants 会失败"
    sigs = set()
    for v in c['variants']:
        sig = variant_signature(v.get('layers'))
        assert sig not in sigs, f"{c['name']} 的 Variant '{v['name']}' 跟其他 Variant 视觉签名相同"
        sigs.add(sig)
```

---

## 组团识别 + Variant 抽取最小化(v20.7.x+,RoyalPass 教训)

**前置:** 这套原则由 RoyalPass 视频生成 + 同事评审反馈沉淀。具体执行流程见 `03_skeleton.md` 第二步"组团识别(5 步法)"。

### 5 大设计原则

1. **变化下沉到最小单元** — 不在大容器(网格行/奖励格/卡片)上做"通用/对勾型/锁型..."这种排列组合 Variant。变化必须下沉到最小可独立变化的视觉单元(底板/角标/底标/icon),每个单元各自带独立 Variant。

2. **大组团不抽 Component,只是 FRAME 结构** — 网格行 / 奖励格 / 中央组等中间结构层是 FRAME 包装层。N 行各异通过子 INSTANCE 各自引用不同 Variant 表达,不通过外层 Variant 排列组合表达。

3. **数据驱动 vs 状态多态分离**:
   - 数据驱动(代码运行时填,需求频繁变,种类无法穷尽枚举)→ 占位 RECT,不做 Component / Variant
   - 状态多态(屏幕里枚举可数,2~10 种)→ 做 Component + Variant

4. **"该状态不显示"做空 Variant(0 layers,语义名"空")**
   - 角标这类 Component 加一个 `layers=[]` 的 Variant,Variant 名约定为 `空`(不带其他前缀后缀)
   - 设计师在 INSTANCE 的"状态"下拉选"空"即不显示
   - 不用 `visible=false` 表达(那是临时显隐,Variant 是状态切换)
   - 引擎实现细节(空 Variant 仍生成 sequence,内部无 keyframe → 视觉空)见**引擎 SKILL `/Users/red/Desktop/引擎最新skill/SKILL.md` 8.12 节"空 Variant 处理"**

5. **运行时数值不进 Variant** — 进度条的"满/空"是引擎运行时按 percentage 切割,**不做 Variant**;但进度条 icon 的"已完成/未完成"是状态多态,**做 Variant**。区分:数值连续 vs 状态离散。

### 不做 Variant 的两类例外

#### 1. 奖励物图片(道具/宝箱/任务奖励等"内容图")

- 屏幕里出现的种类多 + 需求频繁变 + 设计师无法穷尽枚举
- 做成占位 RECT,程序运行时按数据 setSpriteFrame 替换图片
- 不做 Variant,占位 RECT 名字用 `图片_xxx` / `图标_xxx` 前缀

#### 2. 进度条本体(进度条 RECT 的"当前填充百分比")

- 视觉永远画 100% 满模板(SKILL 进度条铁律)
- 引擎运行时按 percentage 切割(CCProgressTimer)
- 不做"50% / 80%"这种 Variant
- 但进度条 **图标/状态指示器** 的"已完成/未完成"是状态多态,**做 Variant**

### 边界场景决策流程图

```
这个视觉变化点:
├── 是大容器(行/卡/格 包装层)还是最小单元(底板/角标/icon)?
│   ├── 大容器 → 不抽 Component,FRAME 包装层。变化下沉到子单元
│   └── 最小单元 → 进入下一判断
│
├── 屏幕里这个单元能枚举可数(2~10 种)吗?
│   ├── 是 → 做 Component + Variant
│   │       ├── 状态包含"不显示" → 加"空 frame" Variant
│   │       └── 各 Variant 视觉签名必须唯一(否则 combineAsVariants 失败)
│   └── 否 → 进入下一判断
│
└── 是数值连续(满/空、百分比)还是种类无穷(图片资源)?
    ├── 数值连续 → 引擎运行时计算(CCProgressTimer 等)
    └── 种类无穷 → 占位 RECT,程序运行时填图
```

### 反面案例(踩过的坑)

❌ **网格行_等级 = 通用 / 宝箱型 / 对勾型 / 对勾锁型 4 Variant**
   - 原因: 排列组合,违反原则 1 + 2
   - 正确: 网格行只 1-2 真实视觉差异 Variant(常态 / 当前用户高亮),
     每行的对勾/锁/数量差异通过内部子 INSTANCE(角标/底标 INSTANCE)各自引用对应 Variant 表达

✅ **角标/底标/黄色高亮条 做"常态空" Variant(空 frame)— Figma 侧合规**
   - Figma 侧:常态空 Variant 0 layers,设计师在 INSTANCE 下拉选"常态空"即不显示
   - 翻译工具自动在引擎侧把这种 INSTANCE 转成 wrapper.visible=false(详见原则 4)

❌ **奖励物做了 7 个 Variant 列举所有道具**
   - 原因: 违反原则 3 + 例外 1(种类无穷,程序填)
   - 正确: 占位 `图片_奖励物` RECT,程序 setSpriteFrame

❌ **看到 1 Variant Component 就删掉降级 FRAME**
   - 原因: 擅自改用户原始设计意图(详见前面"Component 修复铁律")
   - 正确: 加 dummy 第 2 Variant 制造视觉差异(fill / corner_radius)

---

⛔ 本文件为全局参考，不单独执行。每个步骤开始时必须先读取本文件。
