---
name: Component 修复时绝不擅自删除 Component
description: S7 后处理 / combineAsVariants 失败时,优先加 Variant 而不是删 Component;遇到工具限制先问用户
type: feedback
originSessionId: dfb7fa16-bf22-4721-a9bf-80258af3655e
---
遇到 Figma `combineAsVariants` 失败 / S7 抽不出多 Variant / Component 数量不够时,**绝不擅自删除 Component 降级为内嵌 FRAME**。优先做法:加 dummy Variant(用 fill / visible 制造视觉签名差异)让 Component 能 combine。

**Why:** 用户在 RoyalPass 项目里反馈过这个教训。第一次 S7 输出时,只是行 19/20 没被替换为 INSTANCE(平铺残留),组件库 + 可切换预览都正常。我擅自删 `组_进度_行_tb` Component(只 1 Variant)、删 数量徽章 Component(显示/隐藏 Variant 视觉签名相同)来"修 combineAsVariants",结果用户连发"你怎么把进度条删了"、"30m 和 x1 的组件没有啦"两次抱怨。用户的判断是:**先解决平铺,Component 数量保持稳定**,后面的问题就不会出现。Component 列表是用户的**设计决策**,我不该把工具限制下的"省事修复"凌驾于用户原始意图之上。

**How to apply:**
- S7 后第一件事:扫描 final_scene.json 里有没有 type=FRAME 但跟某个 Component 结构指纹相同的"漏网平铺",有的话**加 Variant + 转 INSTANCE**
- 遇到 `combineAsVariants` 限制(Variant <2 / 视觉签名相同 / 引用顺序错)→ 优先加 Variant 修
  - 1 Variant → 加 dummy 第 2 Variant,fill 不同
  - 视觉签名相同 → "显隐"类改 INSTANCE.visible=false / 其他类用 fill 或 icon 添加视觉差异
- 决定删 Component 前必须问用户("我可以删 X Component 降级为内嵌 FRAME 吗?这样会让它不再出现在 📦_组件库 里")
- 修完任何 Component 改动,跑 sanity check:每个 Component ≥2 Variant + 视觉签名 hash 唯一
- 详细规则见新 skill `/Users/red/Desktop/4.22skill_v2/11_S11_抽取导出.md` (Component 修复 / Variant 抽取 / 删 Component 必问用户)
