---
name: Figma AL 容器内子节点的 x/y 是已计算好的
date: 2026-04-24
status: ✅ 已落地（Figma API 理解）
source: RED Tool Figma 插件开发
---

# Lesson: Figma API 比想象的智能

## 误解

之前以为：Figma 里 `layoutMode: HORIZONTAL/VERTICAL`（Auto Layout）容器内的子节点**没有具体 x/y**，需要 Python 模拟 AL 算法算出来。

## 真相

Figma API 里，AL 容器内子节点的 `node.x` / `node.y` **是 Figma 自动计算好的相对父节点坐标**：

- 不是 `undefined`
- 不是 `0`
- 是 Figma 根据 AL 规则（primaryAxisAlignItems、itemSpacing、padding 等）**实时算出的具体数值**

所以插件只要写 `layer.x = node.x` 就能拿到正确坐标，**不需要在 Python 里模拟 AL 算法**。

## 验证

Figma 插件 `code.js` 第 701-702 行：
```javascript
layer.x = node.x;
layer.y = node.y;
```

这是**无条件**赋值，对 AL 子节点也能拿到数值。

## 教训

1. **Figma API 比想象中智能**，很多"自动"特性其实都有具体数值可读
2. 不要假设"Auto Layout 的东西读不出来"，先试试 `node.x` 看有没有值
3. Python 端不需要模拟 AL 算法 → **Figma 已经算好了**，直接读结果

## 实际用途

这让 RED Tool 的 Python 层变简单：
- 只需要识别屏幕级布局（哪些是全宽、哪些固定、贴顶贴底判断）
- 子节点一律读 Figma 给的 x/y，乘以 scale 换算到 Redream 坐标系
- 不用处理 AL 的复杂布局计算

**前提**：输入必须是**导出 JSON**（含 x/y），不是生成 JSON（见 `lesson_export_vs_generate_json.md`）。

## 关联

- `lessons/lesson_export_vs_generate_json.md` — 两种 JSON 的区别
- `references/figma-to-red-cli-driven.md` — 约束 → Redream 对应规则
