---
name: ui_pattern_按钮_纯文本
description: 纯文本按钮 — 圆角矩形 + 文本(1-2 行)居中, 无 icon, 不同游戏边框色变化
type: project
originSessionId: 266a40b7-0aa3-436f-ae8c-03b7c50d6515
---
# 按钮_纯文本 pattern

独立的纯文本按钮, **没有 icon**。最常见的"动作触发按钮"形态(Start / Play / Claim / Request / 关卡名 / 难度名 / ...)。

## 5 维特征

| 维度 | 规律 |
|---|---|
| 形状 | **圆角矩形**(中等圆角, corner_radius 约 h/4 ~ h/3)|
| 构成 | 底板 + 描边 + (可选高光装饰) + 文本(1-2 行)|
| 位置 | 文本**始终居中**(垂直+水平双向居中, **不论 1 行 2 行**)|
| 量级 | 宽 **200~400 px**, 高 **100~200 px**, 长宽比 **2:1 ~ 3:1** |
| 底板 | 必有(底色 + 边框描边)|

## 识别信号(≥3 命中)

- [ ] 圆角矩形(corner_radius ≈ h/4 ~ h/3)
- [ ] **纯文本**(无 icon, 无图形装饰)
- [ ] 文本**居中**(垂直水平双向)
- [ ] 通常 **绿色底 + 鲜艳边框描边**(底色一致, 边框色随游戏/上下文)
- [ ] 文本带**描边阴影**(白/米黄字 + 深色描边)
- [ ] 1 或 2 行均可(不区分 Variant, 由 content 决定)

## Component 设计

```
按钮_<语义> (FRAME, 触控层 REDNodeButton)
├── 底板_按钮_<语义> (RECT, 圆角矩形, 绿色填充, 边框描边)
├── (可选) 高光_按钮_<语义> (RECT, 顶部半透明亮色月牙形, 装饰)
└── 文本_按钮_<语义> (TEXT, dynamic 内容, 居中)
```

**注意**:
- 1 行 vs 2 行**不是 Variant**, 由 text content 决定(`"Start"` vs `"King's\nNightmare"`)
- 文本 TEXT 节点的 alignHorizontal / Vertical 都设 CENTER
- 文本高度按 1-2 行计算(可用 hug 高度)

## ⚠️ Variant 维度(2026-05-12 用户教学补充)

- **按钮一般没有 icon 位置的多态**(本 pattern 无 icon, 不存在)
- **真正的 Variant**:
  - 状态(常态 / 未激活态)— 如果按钮有点击前后变化, S7 不同实例 fill 视觉不同, S11 自动切 Variant
  - **附加角标/底标的多态**(同位置带 vs 不带)— S7 阶段一: 都画完整角标 FRAME, 不显示的实例 `visible: false`; S11 自动切空 Variant

如果识别到**多个按钮中有的带角标/底标 有的不带** → S7 阶段每个按钮 children 都画完整角标 FRAME (name 100% 一致), 不显示的写 `visible: false`。

## Variants 设计 (S11 抽完后的预期形态)

> S7 阶段一不直接写 Variant。 不同状态的按钮各自画扁平 FRAME, fill 视觉不同, S11 自动切 Variant。

| Variant (S11 自动产物) | 来源 — S7 阶段对应实例长啥样 |
|---|---|
| 常态 | 扁平 FRAME, 绿色底 + 边框 + 文本 |
| 禁用 (若场景有) | 扁平 FRAME, 灰色底 + 灰文本 |

## 区分相邻 pattern

| 看着像但不是 | 区别 |
|---|---|
| `横排徽章_左图右文` | 那个左 icon + 右数字, **这个无 icon** |
| `单图标_无角标 按钮型` | 那个是单 icon 按钮(关闭/设置 等), 这个是**文字主导** |
| `icon 带底部文本_C 按钮型` | 那个挂在 icon 下方(进度条节点下), 这个**独立** |
| 倒计时胶囊 | 那个是 钟表+时间, 这个是纯文本 |

## 文本字体推荐(低保真占位)

- 字号: **40 ~ 70 px**(看尺寸)
- 字重: **Bold / Heavy**(粗体)
- 字色: 白色 / 米黄
- 描边: 深色描边(stroke)+ 阴影(shadow), 但低保真**不写**(占位文本)
- 行高: 1.0 ~ 1.2(2 行时控制紧凑)

## 入 JSON 模板

```json
{
  "type": "FRAME",
  "name": "按钮_Start",
  "x": ..., "y": ..., "w": 280, "h": 120,
  "element_class": "static",
  "constraints": {"horizontal": "CENTER", "vertical": "TOP"},
  "children": [
    {
      "type": "RECTANGLE",
      "name": "底板_按钮_Start",
      "x": 0, "y": 0, "w": 280, "h": 120,
      "corner_radius": 35
    },
    {
      "type": "TEXT",
      "name": "文本_按钮_Start",
      "x": 0, "y": 0, "w": 280, "h": 120,
      "element_class": "dynamic",
      "content": "Start",
      "font_size": 56,
      "font_weight": "Bold",
      "textAlignHorizontal": "CENTER",
      "textAlignVertical": "CENTER"
    }
  ]
}
```

2 行示例(只换 content):
```json
"content": "King's\nNightmare"  // \n 换行
"font_size": 42                 // 略小一点适配两行
```

## 来源

2026-05-12 用户 5 张截图(纯文本按钮):
- "Level 146"(1 行, 橙边)
- "Start"(1 行, 蓝/青边, 含高光月牙)
- "Level 385 / Super Hard"(2 行, 紫边)
- "Request"(1 行, 深蓝边)
- "King's / Nightmare"(2 行, 橙边)

用户核心 teaching:
- **纯文本按钮 = 没 icon, 只文字**
- **1 行 / 2 行不区分 Variant**, 文本始终**居中**
- 边框色变化是上下文(游戏不同 section 用不同边框色), 底色都是绿
