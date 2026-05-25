# S5 · flow

## 表 F · 屏幕清单

| # | screen | type | layers[0] | 备注 |
|---|---|---|---|---|
| 1 | `浮层_Jungle_Treasure` | OVERLAY 浮层 | `遮罩_浮层背景` (全屏 RECT) | 唯一屏 |

## 表 G · flow 连线

视频只有这 1 个屏,无切屏。**没有实证 flow**。

但按 S6 包装类型决议会产生几个 `按钮_xxx`,S9 会按 **零幻觉** 原则:
- `按钮_关闭` → **没拍到目标屏** → S9 flow 只写 `trigger: ON_CLICK`, `to` 留 `__TODO__` 或不写, 留待业务方补
- `按钮_offer_N` (6 个) → 同理, 无目标屏

> 决定: S9 不强行编 flow, 保留 `flow: []` 或简版自闭跳转, 详 S9.md。
