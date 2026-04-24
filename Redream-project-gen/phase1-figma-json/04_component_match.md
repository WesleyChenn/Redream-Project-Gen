# S4 · JSON 生成
> 骨架和组件匹配均确认后执行。
> **逐屏生成，每屏生成后立即验证，✅ 后才生成下一屏。**

---

## 核心规则（全部遵守，不得遗漏）

### 规则1：fill 省略规则（手搓节点）
JSON 中手搓节点不写任何 fill 字段，包括 `"transparent"`。插件按命名自动分灰。
**component_ref 节点不受此规则约束**，组件库内部 fill 由 Figma 组件自身维护。

### 规则2：constraints 分三场景
| 场景 | constraints |
|---|---|
| `screen.layers` 直接子节点 | ✅ 必须写 |
| `NONE` 父容器的子节点 | ✅ 必须写 |
| `HORIZONTAL/VERTICAL` 父容器子节点 | ❌ 不写 |

**constraints 值按语义位置枚举（必须写时参照此表）：**

| 语义 | 位置 | horizontal | vertical | 说明 |
|---|---|---|---|---|
| 顶部固定区（HUD/标题栏） | 贴顶全宽 | SCALE | TOP | 屏幕宽度变化时跟随拉伸 |
| 底部固定区（导航栏/操作栏） | 贴底全宽 | SCALE | BOTTOM | 屏幕宽度变化时跟随拉伸 |
| 全屏背景/底板 | 铺满 | SCALE | SCALE | 双向拉伸 |
| 中间弹性区（地图/滚动区） | 占满剩余高度 | SCALE | SCALE | 双向拉伸 |
| 贴左固定图标（头像/金币图标） | 贴左 | LEFT | TOP | 宽度不变，锚定左边 |
| 贴右功能按钮（关闭/设置） | 贴右 | RIGHT | TOP | 宽度不变，锚定右边 |
| 单个居中按钮（弹窗内/标题区） | 水平居中 | CENTER | TOP | 宽度不变，始终居中 |
| 单个居中 + 贴底 | 居中贴底 | CENTER | BOTTOM | 宽度不变，居中贴底 |
| 进度条跟随容器宽度 | 拉满横向 | SCALE | TOP | 跟随父容器宽度拉伸 |
| 右对齐数值（分数/数值） | 贴右 | RIGHT | TOP | 锚定右边，宽度不变 |
| 弹窗主体 | 居中浮层 | CENTER | CENTER | 双向居中 |

**响应式行为补充（AL 容器内，不写 constraints，用 layoutSizing 控制）：**

| 语义 | layoutSizingHorizontal | layoutSizingVertical | 说明 |
|---|---|---|---|
| 列表行（排行榜行/消息行） | FILL | — | 撑满父容器宽度 |
| 列表行内名字/内容区 | FILL | — | 占满剩余宽度 |
| 列表行内固定元素（头像/序号） | 不写（FIXED） | — | 保持量测宽度 |
| AL容器内均分按钮 | FILL | — | 均分容器宽度 |
| AL容器内固定宽按钮 | 不写（FIXED） | — | 保持量测宽度 |
| 网格项 | FILL | — | 均分行宽度 |
| VERTICAL容器内任意子FRAME | FILL | — | 必填，防止文字竖排 |

### 规则2.5：AL 容器对齐意图默认值表

> **生成前必须查此表。** S3 布局意图确认表已由用户确认，S4 直接按确认结论写，不再自行判断。

| 场景 | 典型容器 | primaryAxisAlignItems | 是否可用弹性缝隙 |
|---|---|---|---|
| 屏幕顶层 HUD / 标题栏 | 组_顶部HUD、组_标题栏 | MIN | 标题需居中时可用×2 |
| 屏幕底层导航 / 操作栏 | 组_底部导航、组_底部操作栏 | SPACE_BETWEEN | 否 |
| 外侧大组内容区（非 HUD）| 组_底部按钮区、弹窗主内容 | **CENTER** | 否 |
| 响应式中间区内各行 | 滚动区内列表行、网格行 | MIN 或 SPACE_BETWEEN | 靠右单元素时可用 |
| 列表行内部 | 列表项_xxx | MIN + 内容区FILL | 靠右单元素时可用 |
| 卡片底部行（名称+按钮）| 组_底部行 | MIN | 是，名称靠左按钮靠右 |
| 网格行 | 网格行_第N行 | SPACE_BETWEEN | 否 |
| 弹窗内容 VERTICAL | 内容区_弹窗 | MIN | 否 |

**小游戏专项规则（高优先级，覆盖上表）：**
- 顶部 HUD（生命值/金币栏）以外的**所有外侧大组**，默认 `CENTER`
- 响应式中间弹性区以外的固定高度容器，优先 `CENTER`
- 底部双按钮区：两个按钮作为整体居中，用 `CENTER`，不用弹性缝隙

### 规则3：格式铁律
| 字段 | 正确 | 错误 |
|---|---|---|
| 矩形 | `"type": "RECTANGLE"` | ~~`"RECT"`~~ |
| 文字内容 | `"content"` | ~~`"text"`~~ |
| 文字对齐 | `"textAlignHorizontal"` | ~~`"text_align"`~~ |
| 交互数组 | `"flow"` | ~~`"flows"`~~ |
| 屏幕子列表 | `"layers"` | ~~`"children"`~~ |
| 内部子节点 | `"children"` | ~~`"layers"`~~ |
| 每条 flow | 必须含 `"trigger": "ON_CLICK"` | |

### 规则4：component_ref 格式
```json
✅ { "component_ref": "进度条_宽", "name": "进度_经验", "w": 547, "h": 38, "overrides": {"文本_进度": "5/600"} }
❌ { "type": "component_ref", "name": "进度条_宽" }
```
component_ref 节点不写 layoutSizingHorizontal/Vertical。

**component_ref 等比缩放写法：**
- 输出 w/h = 截图量测 × scale（不使用组件库原始尺寸）
- 非正方形组件以高度为基准：`scale = 目标h / 原始h`，宽度 = `原始w × scale`
- 前提：S3 已确认组件库内部 constraints 为 SCALE/SCALE（可缩放）

### 规则4.5：component_ref 叠加结构（v20 做法 B 唯一版）

当 component_ref 视觉上有「贴边附加元素」（角标、倒计时条、徽章等）时，**统一使用做法 B**：

**做法 B：`按钮_xxx` FRAME 包装**
- component_ref 和装饰都作为外层 `按钮_xxx` FRAME 的 children
- 外层按钮 FRAME 是真正的触控层，装饰随按钮一起响应点击反馈
- 无论主体 component_ref 是"按钮类组件"（椭圆按钮/方形按钮/圆形按钮/矩形按钮）还是"Tab 状态切换类组件"（导航栏_状态切换_选中等），一律用此包装法

**命名规则：**
- 包装层一律用 `按钮_[主体名]`（如 `按钮_活动紫罐`、`按钮_Tab_Weekly`）
- **禁止**用 `组_xxx` NONE 容器包裹按钮+装饰（装饰不会响应点击反馈）

**包装层尺寸原则（核心）：**

```
包装层对外 w/h = 主体组件 w/h（与同行/同列其他元素对齐的尺寸）
附加元素溢出靠绝对坐标实现,不撑大包装层
主体组件通过 x/y 偏移给附加元素让出空间
```

验证方式：包装层的 h/w 填入父 AL 容器后,所有同行/同列兄弟元素对齐是否正确。

**附加元素约束铁律：**
```
❌ 禁止：附加元素使用 RIGHT、CENTER 约束,或写负数坐标
✅ 强制：附加元素一律 LEFT/TOP,x/y 全部为正数
         Figma 的 RIGHT/CENTER 约束会覆盖 x 值导致元素飞出
```

**附加元素位置确认方法（居中验证,防止误判）：**
```
同时量测：父本宽度 W_parent、附加元素宽度 W_child
居中期望值 x = (W_parent - W_child) / 2
实际量测 x_actual（相对父本左边缘）
若 |x_actual - x| < 10px → 居中,x 用计算值
若偏差 > 10px → 左/右对齐,x 用量测值
（无论哪种情况,constraints 都写 LEFT/TOP）
```

**四种常见叠加场景的包装层写法：**

| 场景 | 包装层 w/h | 主体 x/y | 附加元素 x/y | 附加元素 constraints |
|---|---|---|---|---|
| 右上角角标溢出顶部 | w=主体w, h=主体h | x=0, y=角标h/2 | x=主体w-角标w/2, y=0 | LEFT/TOP |
| 角标正上方居中 | w=主体w, h=主体h | x=0, y=溢出量 | x=(主体w-角标w)/2, y=0 | LEFT/TOP |
| 底标/倒计时下方居中 | w=主体w, h=主体h | x=0, y=0 | x=(主体w-附加w)/2, y=主体h+间距 | LEFT/TOP |
| 右上角内侧（不溢出）| w=主体w, h=主体h | x=0, y=0 | x=主体w-角标w-偏移, y=偏移 | LEFT/TOP |

**正确示例（右上角角标）：**
```json
✅ 按钮_xxx FRAME 包装（做法 B），装饰与按钮一起响应点击反馈
{
  "type": "FRAME", "name": "按钮_活动花朵", "w": 170, "h": 231,
  "layoutMode": "NONE",
  "children": [
    {
      "component_ref": "椭圆按钮_活动", "name": "活动_花朵",
      "x": 0, "y": 17,
      "w": 170, "h": 231,
      "constraints": { "horizontal": "LEFT", "vertical": "TOP" }
    },
    {
      "type": "FRAME", "name": "角标_数字1",
      "x": 136, "y": 0, "w": 34, "h": 34,
      "layoutMode": "NONE", "corner_radius": 17,
      "constraints": { "horizontal": "LEFT", "vertical": "TOP" },
      "children": [
        { "type": "RECTANGLE", "name": "底板_角标", "x": 0, "y": 0, "w": 34, "h": 34, "corner_radius": 17,
          "constraints": { "horizontal": "SCALE", "vertical": "SCALE" } },
        { "type": "TEXT", "name": "文本_角标", "x": 8, "y": 5, "content": "1",
          "font_size": 22, "font_weight": "Bold", "textAlignHorizontal": "CENTER",
          "constraints": { "horizontal": "CENTER", "vertical": "CENTER" } }
      ]
    }
  ]
}
```

**正确示例（Tab 状态切换 + 倒计时底标）：**
```json
✅ 按钮_xxx FRAME 包装（做法 B），倒计时底标作为按钮 children
{
  "type": "FRAME", "name": "按钮_Tab_Weekly", "w": 219, "h": 99,
  "layoutMode": "NONE",
  "children": [
    {
      "component_ref": "导航栏_状态切换_选中", "name": "Tab_Weekly",
      "x": 0, "y": 0, "w": 219, "h": 99,
      "overrides": { "文本_Selected": "Weekly" },
      "constraints": { "horizontal": "LEFT", "vertical": "TOP" }
    },
    {
      "component_ref": "底标_倒计时", "name": "底标_4d22h",
      "x": 17, "y": 103, "w": 185, "h": 48,
      "overrides": { "文本_时间": "4d 22h" },
      "constraints": { "horizontal": "LEFT", "vertical": "TOP" }
    }
  ]
}
```

```json
❌ 错误1：包装层 h 包含附加元素（撑大了,破坏同行对齐）
{ "type": "FRAME", "name": "按钮_Tab_Weekly", "w": 219, "h": 147 }

❌ 错误2：用 组_xxx 普通容器包裹,装饰不响应点击反馈
{ "type": "FRAME", "name": "组_活动_花朵", "children": [
  { "component_ref": "椭圆按钮_活动", "name": "活动_花朵" },
  { "name": "角标_数字1" }   ← 应改用 按钮_活动花朵 FRAME 包装
]}

❌ 错误3：附加元素与主体裸放在大NONE容器（没有包装层）
"组_地图内容".children: [
  { "component_ref": "椭圆按钮_活动", "name": "活动_花朵" },
  { "name": "角标_数字1" }   ← 必须在 按钮_ 包装层内,不能平级
]

❌ 错误4：附加元素用了负数坐标或 RIGHT/CENTER 约束
{ "name": "角标_数字1", "x": 148, "y": -17,
  "constraints": { "horizontal": "RIGHT", "vertical": "TOP" } }
```

### 规则5：按钮与底板分离（v20 核心规则）

**命名规范（节点类型 + 命名前缀共同决定角色和灰度，必须严格遵守）：**

| 节点类型 | 命名形式 | 用途 | 引擎识别 | 插件上色 |
|---|---|---|---|---|
| `FRAME` | `按钮_xxx` | **真正的按钮触控层** | REDNodeButton | 透明 |
| `RECTANGLE` | `底板_xxx`（父是按钮）| **按钮内层装饰底板** | CCSprite | 最浅灰（按按钮后缀可分级） |
| `RECTANGLE` | `底板_xxx`（父非按钮）| **外层容器底板** | CCSprite | 中深灰 |
| `FRAME` | `组_xxx` / `容器_xxx` / `弹窗_xxx` | **装按钮的容器**（纯分组） | CCNode | 透明 |

⚠️ **核心识别逻辑**：
- 引擎只识别 `按钮_xxx` **FRAME** 为触控层，其他任何命名都不是按钮
- 两种 `底板_xxx` RECT（按钮内层 vs 外层容器）**靠父节点类型区分灰度**
- **装按钮的容器禁止用 `底板_` 开头**（否则引擎没法识别）
- **卡片 / 弹窗外壳禁止用 FRAME**，必须是 `底板_xxx` RECT

**手搓按钮（v20 新结构）：**
```json
{
  "type": "FRAME", "name": "按钮_开始", "w": 446, "h": 150,
  "layoutMode": "NONE", "corner_radius": 75,
  "children": [
    { "type": "RECTANGLE", "name": "底板_开始", "x": 0, "y": 0, "w": 446, "h": 150,
      "corner_radius": 75,
      "constraints": { "horizontal": "SCALE", "vertical": "SCALE" } },
    { "type": "FRAME", "name": "内容区_开始",
      "x": 0, "y": 0, "w": 446, "h": 150,
      "layoutMode": "HORIZONTAL",
      "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
      "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "CENTER",
      "constraints": { "horizontal": "SCALE", "vertical": "SCALE" },
      "children": [
        { "type": "TEXT", "name": "文本_开始", "content": "Action",
          "font_size": 56, "font_weight": "Bold", "textAlignHorizontal": "CENTER" }
      ]
    }
  ]
}
```

**外层容器底板（卡片 / 弹窗外壳，不走按钮结构）：**
```json
{
  "type": "FRAME", "name": "容器_EasterPass卡",
  "w": 1042, "h": 544, "layoutMode": "NONE",
  "children": [
    { "type": "RECTANGLE", "name": "底板_EasterPass卡", "x": 0, "y": 0, "w": 1042, "h": 544,
      "corner_radius": 30, "constraints": { "horizontal": "SCALE", "vertical": "SCALE" } },
    { "type": "TEXT", "name": "文本_EasterPass标题", ... },
    { "type": "FRAME", "name": "按钮_Activate", ... }   ← 卡内按钮,与外层容器形成层次差
  ]
}
```

### 规则5.5：按钮分组（装饰一起响应按钮变换）

**装饰附件必须作为按钮 FRAME 的 children**，角标、徽章、底标（倒计时 / 进度）、Popular 标签等都算。

**正确（装饰作为按钮 children,一起响应点击反馈）：**
```json
{
  "type": "FRAME", "name": "按钮_活动紫罐",
  "w": 163, "h": 213, "layoutMode": "NONE",
  "children": [
    { "component_ref": "椭圆按钮_活动", "name": "活动_紫罐",
      "x": 0, "y": 0, "w": 163, "h": 213,
      "overrides": { "文本_时间": "2d 4h" },
      "constraints": { "horizontal": "SCALE", "vertical": "SCALE" } },
    { "type": "FRAME", "name": "角标_感叹号",
      "x": 115, "y": 0, "w": 56, "h": 58, ... }
  ]
}
```

**错误（装饰和按钮兄弟关系，点击不跟随）：**
```json
{
  "type": "FRAME", "name": "组_活动_紫罐",
  "children": [
    { "component_ref": "椭圆按钮_活动", "name": "活动_紫罐" },
    { "type": "FRAME", "name": "角标_感叹号" }      ← ❌ 兄弟平级
  ]
}
```

> ⚠️ 内容区_ FRAME 的 w/h 必须与按钮底板完全一致，子元素不写 x/y，由 CENTER 自动居中。

**AL 父容器内，底板用 ABSOLUTE：**
```json
{ "type": "RECTANGLE", "name": "底板_背景", "x": 0, "y": 0, "w": 1000, "h": 80,
  "corner_radius": 12, "layoutPositioning": "ABSOLUTE" }
```
⚠️ `layoutPositioning: "ABSOLUTE"` 仅在 HORIZONTAL/VERTICAL 父容器内有效，NONE 父容器内不写。

### 规则6：AL 容器必填字段
每个 layoutMode 为 HORIZONTAL/VERTICAL 的 FRAME 必须写：
- `primaryAxisSizingMode`（FIXED 或 AUTO）
- `counterAxisSizingMode`（FIXED 或 AUTO）
- `primaryAxisAlignItems`（MIN / MAX / CENTER / SPACE_BETWEEN）
- `counterAxisAlignItems`（MIN / MAX / CENTER）

VERTICAL 容器内的子 FRAME 必须加：`"layoutSizingHorizontal": "FILL"`

### 规则7：滚动容器（三条件缺一不可）
```json
父容器：overflow + clip_content:true + primaryAxisSizingMode:"FIXED"
子容器：primaryAxisSizingMode:"AUTO" + 显式写 w + layoutSizingHorizontal:"FILL"
子容器 h 必须大于父容器 h
```

### 规则8：弹性缝隙
```json
{ "type": "FRAME", "name": "弹性缝隙", "w": 0, "h": 0, "layoutMode": "NONE", "layoutSizingHorizontal": "FILL" }
```

**弹性缝隙三条强制规则（违反即错误）：**

**规则8-1：只能放在两个实体元素之间，禁止放在 children 列表首位或末位。**
```
❌ [按钮_皮肤, 按钮_Level3, 弹性缝隙]   ← 缝隙在末位，两按钮全部靠左
❌ [弹性缝隙, 按钮_皮肤, 按钮_Level3]   ← 缝隙在首位，两按钮全部靠右
✅ [按钮_返回, 弹性缝隙, 按钮_关闭]     ← 缝隙在中间，返回靠左，关闭靠右
```

**规则8-2：使用前必须已在 S3 布局意图确认表中说明意图。**
必须写明：缝隙左侧是什么元素，右侧是什么元素，实现什么视觉效果。未经 S3 确认不得在 S4 中直接写入弹性缝隙。

**规则8-3：以下场景禁止用弹性缝隙，改用对应方案。**

| 场景 | ❌ 禁止 | ✅ 正确方案 |
|---|---|---|
| 多个元素整体居中 | 缝隙放首位或末位 | `primaryAxisAlignItems: CENTER` |
| 均匀分布 | 缝隙放元素之间 | `primaryAxisAlignItems: SPACE_BETWEEN` |
| 靠右单个元素 | — | 弹性缝隙放在该元素左侧（此情况允许） |
| 标题居中+两端按钮 | — | 弹性缝隙×2，分别放标题两侧 |

⚠️ 有弹性缝隙时容器 `primaryAxisAlignItems` 用 `MIN`。
⚠️ VERTICAL 容器的弹性缝隙需同时写 `"layoutSizingVertical": "FILL"`，去掉 `layoutSizingHorizontal`。

### 规则9：导航栏写法
```json
{ "component_ref": "导航栏_页面切换_选中", "name": "导航_项3", "w": 170, "h": 165, "overrides": {"内容_标签": "Home"} }
{ "component_ref": "导航栏_页面切换_未选中", "name": "导航_项4", "w": 170, "h": 165, "overrides": {"数字_角标": "1"} }
```

### 规则10：flow 写法
```json
全屏跳转：{ "from": "界面_A", "from_node": "按钮_xxx", "to": "界面_B", "trigger": "ON_CLICK", "animation": "dissolve 300ms" }
浮层打开：{ "from": "界面_A", "from_node": "按钮_xxx", "to": "浮层_xxx", "trigger": "ON_CLICK", "animation": "dissolve 300ms" }
浮层关闭：{ "from": "浮层_xxx", "from_node": "按钮_关闭", "to": "", "trigger": "ON_CLICK" }
Tab切换：{ "from": "界面_A", "from_node": "导航_项K", "to": "界面_B", "trigger": "ON_CLICK", "animation": "slide 300ms" }
```
导航_状态切换_* 不生成任何 flow。

**导航栏全量连线原则：** 每个屏幕底部导航栏中，所有非激活 Tab 项必须写 flow 指向对应目标屏幕。只写视频中实际出现的目标屏幕，未出现的不写。N 个已识别屏幕之间生成 N×(N-1) 条 slide 连线。

### 规则11：命名枚举锁
合法前缀（只能用这些）：
`界面_` `浮层_` `组_` `底板_` `内容区_` `内容_` `容器_` `导航_` `列表项_` `网格行_` `网格项_` `弹窗_` `按钮_` `图片_` `图标_` `背景_` `遮罩_` `文本_` `文字_` `弹性缝隙` `角标_` `徽章_` `进度_` `Tab_` `Toggle_` `请求_` `消息项_` `活动_` `底标_`

### 规则12：浮层遮罩铁律

所有 `浮层_` 屏幕的 `layers[0]` 必须是全屏半透明黑色遮罩：

```json
{ "type": "RECTANGLE", "name": "遮罩_浮层背景",
  "x": 0, "y": 0, "w": 1080, "h": 2400,
  "constraints": { "horizontal": "SCALE", "vertical": "SCALE" } }
```

插件识别 `遮罩_` 前缀后自动加深灰 + opacity=0.7，覆盖底层界面形成浮层视觉。遮罩必须占满整屏（h=2400），其上的卡片/按钮正常绝对定位。

### 规则13：界面背景铁律

`界面_` 屏幕的全屏背景（地图/场景/天空等）**必须作为屏幕 `layers[0]` 的全屏 `背景_xxx` RECTANGLE**，不得放进中间弹性区容器：

```json
{ "type": "RECTANGLE", "name": "背景_地图场景",
  "x": 0, "y": 0, "w": 1080, "h": 2400,
  "constraints": { "horizontal": "SCALE", "vertical": "SCALE" } }
```

背景作为图层最底，HUD / 进度条 / 中间内容 / 双按钮 / 导航浮在背景之上，透明部分自然透出背景。

---

## 执行顺序

```
① 生成第1个屏幕 JSON
② 立即输出该屏幕验证（见下方格式）
③ ✅ 通过 → 生成第2个屏幕
   ❌ 失败 → 修正 → 重新验证 → 通过后继续
④ 重复直到所有屏幕完成
⑤ 输出完整 flow 数组
⑥ 停止
```

## 每屏验证格式

```
【屏幕验证 · 界面_主地图】

骨架闭环：
  组_顶部HUD(66) + 组_进度条区(49) + 组_地图内容(1931)
  + 组_底部双按钮(103) + 组_底部导航(251) = 2400 ✅

from_node 对照：
  活动_花朵 → 存在于 组_地图活动按钮.children ✅
  活动_剑盾 → 存在于 组_地图活动按钮.children ✅

命名白名单：全部合规 ✅
fill 字段：手搓节点无 fill ✅
手搓按钮内容区：按需使用 内容区_ FRAME(多子元素居中时) 或子元素直接作为按钮 children ✅
```

---

## ⛔ 所有屏幕和 flow 生成完毕后立即停止，等待回复「继续S5」
