---
name: Btn 作为按钮容器节点的规范
description: 按钮是一等节点类型 (Btn)，点击响应区不再用 La 借位；按钮图片默认作为 Btn 子节点（indent=1），广告横幅为特例
type: feedback
---

# Lesson: Btn 按钮节点 — 一等类型 + 容器模式

**日期:** 2026-04-15
**状态:** ✅ 已落地（Cozy Shapes download_guide + ad_banner，节点类型 Btn 已加入 BeadsOut/FruitTruck 模板）

## 事件

Cozy Shapes 原设计里：
- `download_guide.按钮_下载定位点(N)` + 运行时 instantiate 按钮 prefab
- `ad_banner.广告点击响应区(La)` 借用"定位区"类型做点击响应

用户反馈：
> 广告点击响应区应该做成按钮，节点 tag 添加按钮类型；按钮的图片应该作为按钮节点的子节点（广告横幅除外）

## 规则

### R1 — Btn 是一等节点类型

所有"可点击响应区"都用 `Btn`，不要借 `La / N / Ly` 类型。Btn 在模板中的视觉:
```css
.nb-Btn{background:rgba(34,211,238,.14); color:#67e8f9; font-weight:700;}
```
在 `ND_TYPES` / `ND_LABELS` / `ND_COLOR` 三张表里都要登记（`Btn:'按钮'` / `#67e8f9`）。

### R2 — 按钮图片默认作为 Btn 子节点

```
默认模式：
按钮_下载 (Btn)          ← 点击响应 + 容器
└─ 图片_按钮 (S, indent=1)  ← 视觉
```

按钮与图片的 transform 一起缩放/移动，交互区域=图片区域，代码只需抓 Btn 即可。

### R3 — 广告横幅特例：按钮与图片保持兄弟

```
广告横幅特例：
图片_横幅 (S)
图片_按钮 (S)          ← 独立做呼吸缩放动画，不受按钮交互层影响
按钮 (Btn)             ← 仅作为点击响应区，与图片_按钮 同级
```

**Why:** 广告横幅的图片_按钮要独立做"吸睛呼吸"循环动画；若做成 Btn 子节点，按钮本身因缩放会导致响应区抖动。规范上把这类"按钮图片 = 独立动画对象"与"按钮 = 纯响应层"解耦。

### R4 — indent 断言接受 Btn 作父

```python
assert parent["type"] in ("Gp", "Btn"), \
    f"node[{i}] 父节点 {parent['label']} 不是 Gp 群组 / Btn 按钮"
```

## How to apply

画 prefab 结构时对每个"可点击的东西"问：
- 需要响应点击吗？→ 用 Btn
- 响应区=图片区域？→ `Btn > 图片(indent=1)`（R2）
- 图片需要独立做呼吸/抖动/飘动等装饰动画？→ Btn 与图片同级兄弟（R3，广告横幅模式）

## 关联

- `_global/feedback_node_naming_by_function.md` — Btn 的 label 按功能（`按钮_下载` / `按钮_关闭`）
- `_global/feedback_playable_default_prefabs.md` — 试玩三件套 ad_banner 沿用 R3 特例
