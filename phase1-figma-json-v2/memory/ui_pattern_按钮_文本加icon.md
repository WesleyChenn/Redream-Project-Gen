---
name: ui_pattern_按钮_文本加icon
description: 文本 + icon 组合按钮 — icon 可左可右(2 子形态), 文本是动作词
type: project
originSessionId: 266a40b7-0aa3-436f-ae8c-03b7c50d6515
---
# 按钮_文本加icon pattern

按钮内含**文本 + icon**, 跟纯文本按钮区分。**icon 位置可左可右**, 是 Variant 维度。

## 5 维特征

| 维度 | 规律 |
|---|---|
| 形状 | **圆角矩形按钮**(跟纯文本按钮形态一致)|
| 构成 | 底板 + 文本(动作词)+ icon |
| 位置 | icon 在文本左或右(横向并列), icon 可能上下/左右溢出底板 |
| 量级 | 宽 **200~400 px**, 高 **100~200 px** |
| 底板 | 必有(圆角矩形, 通常绿色)|

## ⚠️ Variant 维度(2026-05-12 用户教学**修正**)

**之前错的方向**(我抽错了):把"icon 左 vs icon 右"做成 2 个 Variants → ❌

**正确**(用户教学):
- **按钮一般没有 icon 位置的多态** — icon 在左还是右是**Component 设计选择**, 不同设计就用不同 Component, 不是 Variant 维度
- **按钮真正的 Variant 通常是角标/底标的多态**(类似 `ui_pattern_角标_状态` 同位置多内容规则)
- 如果识别到**有的按钮带角标/底标 有的不带** → S7 阶段一: 都画完整 FRAME, 不显示的实例 `visible: false` (新 skill 07d); S11 自动切空 Variant

### 例:同界面多个 "Start ❤️" 按钮 — S7 阶段一写法

```
按钮 1: 按钮_Start FRAME, children=[底板, 文本, icon, 角标_新内容 FRAME visible:true]
按钮 2: 按钮_Start FRAME, children=[底板, 文本, icon, 角标_新内容 FRAME visible:false]
                                                       ↑ children 跟按钮 1 的角标 100% 一致, 只是隐藏

→ S11 自动抽: 按钮主体共 Component; 角标_新内容 共 Component 含空 Variant
```

## 2 个 子形态(layout, 不是 Variant)

### A. text 左 + icon 右

```
┌──────────────────┐
│  Start    [icon] │ ← icon 可能右溢出
└──────────────────┘
```

例: "Start ❤️∞" / "FREE 🔒"

### B. icon 左 + text 右

```
┌──────────────────┐
│ [icon]    Request│ ← icon 可能左溢出
└──────────────────┘
```

例: "🃏 Request" / "❤️ Request"

## 识别信号(≥3 命中)

- [ ] 圆角矩形按钮形态
- [ ] **同时有 文本和 icon**(不是纯文本, 不是纯 icon)
- [ ] 文本是**动作词**(Start / Request / FREE / Claim 等), 不是数字/资源量
- [ ] icon 在文本一侧(左或右), 不是上下
- [ ] icon 可能轻微溢出按钮边界

## 跟相邻 pattern 严格区分

| 看着像 | 区别 |
|---|---|
| **按钮_纯文本** | 无 icon |
| **横排徽章_左图右文** | 是**显示量**(数字"6000")), 这个是**按钮动作**(动词"Start") |
| **单图标_无角标 按钮型** | 无文字 |

### ⚠️ 跟 `横排徽章_左图右文` 视觉极相似

判断方法:
- 看**文本内容**:数字/时间 → 横排徽章;动词 → 按钮
- 看**整体语义**:显示量(余额/进度) → 横排徽章;触发动作(Start/Claim) → 按钮
- 看**底板长宽比**:2:1~4:1 长条 → 横排徽章常见;2:1~3:1 偏方 → 按钮常见
- 看**含义**:不可点击只显示数据 → 横排徽章;可点击触发 → 按钮

实际上**结构 99% 一样**, 区别在用途。 引擎侧:
- 横排徽章用 `组_xxx` 包装(展示)
- 按钮用 `按钮_xxx` FRAME 包装(REDNodeButton 触控层)

## Component 设计

```
按钮_<语义> (FRAME, REDNodeButton 触控层)
├── 底板_按钮_<语义> (RECT, 圆角矩形, 绿色)
├── 图标_按钮_<语义> (RECT 占位, 数据驱动)
└── 文本_按钮_<语义> (TEXT, 内容是动词)
```

## Variants 设计 (S11 抽完后的预期形态)

> S7 阶段一你**不直接写 Variant**。 S7 时每个按钮画扁平 FRAME, icon 位置不同 = 不同视觉签名, S11 自动切多 Variant。

| Variant (S11 自动产物) | 来源 — S7 阶段对应实例长啥样 |
|---|---|
| icon右 | 扁平 FRAME, children=[底板, 文本(左), icon(右)] |
| icon左 | 扁平 FRAME, children=[底板, icon(左), 文本(右)] |

S11 看到子节点位置不同 → wrapper_signature 不同 → 自动切 2 个 Variant。

## 入 JSON 模板

### A 子形态(text 左 icon 右)

```json
{
  "type": "FRAME",
  "name": "按钮_Start",
  "x": ..., "y": ..., "w": 320, "h": 130,
  "children": [
    {"type": "RECTANGLE", "name": "底板_按钮_Start",
     "x": 0, "y": 0, "w": 320, "h": 130, "corner_radius": 40},
    {"type": "TEXT", "name": "文本_按钮_Start",
     "x": 30, "y": 35, "w": 180, "h": 60,
     "content": "Start", "font_size": 50, "font_weight": "Bold",
     "textAlignHorizontal": "CENTER"},
    {"type": "RECTANGLE", "name": "图标_按钮_Start",
     "x": 225, "y": 15, "w": 100, "h": 100,
     "element_class": "static"}    // icon 右, 可能右溢出
  ]
}
```

### B 子形态(icon 左 text 右)

```json
{
  "type": "FRAME",
  "name": "按钮_Request",
  "x": ..., "y": ..., "w": 280, "h": 110,
  "children": [
    {"type": "RECTANGLE", "name": "底板_按钮_Request",
     "x": 0, "y": 0, "w": 280, "h": 110, "corner_radius": 35},
    {"type": "RECTANGLE", "name": "图标_按钮_Request",
     "x": -15, "y": 10, "w": 90, "h": 90},   // icon 左, 可能左溢出
    {"type": "TEXT", "name": "文本_按钮_Request",
     "x": 80, "y": 30, "w": 180, "h": 50,
     "content": "Request", "font_size": 44, "font_weight": "Bold",
     "textAlignHorizontal": "CENTER"}
  ]
}
```

## 来源

2026-05-12 用户 4 张截图:
- "Start" + 红心∞(右)
- 紫卡片 + "Request"(左)
- 红心 + "Request"(左)
- "FREE" + 金锁(右)

用户核心 teaching:
- **文本 + icon 按钮**, icon 可能左可能右(2 子形态)
- 跟纯文本按钮 / 横排徽章 区分(语义: 动作词 vs 数字, 用途: 按钮 vs 显示)
