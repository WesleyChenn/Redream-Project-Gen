---
name: 生成 JSON vs 导出 JSON（RED Tool 输入类型区分）
date: 2026-04-24
status: ✅ 已落地（输入契约）
source: RED Tool CLI 迁移
---

# Lesson: Figma 插件的两种 JSON 不能混用

## 事件

把 Figma 插件的"生成 JSON"（用于从 JSON 画 Figma 的那份）喂给 RED Tool，结果**所有子节点都挤在左上角**（x=0, y=0）。

## 根因

Figma 插件同时支持两种 JSON：

| 类型 | 方向 | 是否含 x/y | 用途 |
|------|------|----------|------|
| **生成 JSON** | JSON → Figma | ❌ 不含 | 在 Figma 画布上画出界面，AL 容器子节点靠 Figma 自动排 |
| **导出 JSON** | Figma → JSON | ✅ 含（Figma 自动算好的）| 把画布现状导出，用于下游工具 |

**RED Tool 只认导出 JSON**（需要 x/y 做坐标映射）。

把"生成 JSON"喂给 RED Tool → Python 读不到 x/y → 按 0 处理 → 所有子节点挤在左上角。

## 诊断过程（踩过的弯路）

1. 以为是 Python 规则问题，对照代码确认所有规则都在 ✗
2. 以为插件没写 x/y，看 `code.js` 第 701-702 行 `layer.x = node.x` 是无条件的 ✗
3. 最后发现用户给的 JSON 里就是没 x/y —— 那是生成 JSON ✓

## 规则

### 正确流程

1. 用**生成 JSON** 在 Figma 画出界面（从 PRD/设计稿输入）
2. 在 Figma 里点插件「**导出 JSON**」按钮
3. 把导出的 JSON 粘进 RED Tool

### 识别方法

- **导出 JSON**：节点带 `x` / `y` 字段，数值是 Figma 自动算好的相对父节点坐标
- **生成 JSON**：节点没有 `x` / `y`（或全是 0）

### 前置验证（理想做法）

RED Tool 可以加个输入验证：如果子节点没 x/y 又不在 NONE 容器里，直接报错让用户换 JSON，而不是默默按 0 处理。

## 教训

- **测试样本要确认来源**（是生成用还是导出的）
- Python 规则没错但输入数据错了，定位会走弯路
- 把输入验证做前置，错得明确比错得隐蔽好

## 关联

- `references/figma-to-red-cli-driven.md` — "两种 JSON 区别"章节
- `phase1-figma-json/05_json_generate.md` — 导出 JSON 的生成规范
