# Bug 归档索引

这里归档跨步骤反复出现的踩坑教训 (跟 S 文件内的"违规信号"表互补 — 违规信号是该步内的, lessons 是跨步骤的)。

## 索引

| 文件 | 一句话总结 | 来源 / 触发场景 |
|---|---|---|
| [`lesson_扁平vs_v206_schema.md`](lesson_扁平vs_v206_schema.md) | S7-S9 阶段是扁平 scene.json, 没有 INSTANCE/components[]/variant 字段 — 这些是 S11 自动产物 | RoyalPass 测试 + 多次混淆 S7/S11 形态 |
| [`lesson_规则11.5_子节点name一致.md`](lesson_规则11.5_子节点name一致.md) | 同结构多实例 FRAME (列表行/网格项) 内部子节点 name 100% 一致, 否则 S11 抽不出 Component | RoyalPass 8 行实例命名漂移踩坑 |
| [`lesson_进度条本体一整根.md`](lesson_进度条本体一整根.md) | 进度条本体 RECT 永远画一整根 100% 满, 即使条上有节点 icon 也不分段 — 引擎运行时切割 | 2026-05-14 用户补强 (07c 新加) |
| [`lesson_组团内layout单一化.md`](lesson_组团内layout单一化.md) | 一个 FRAME 内子节点不能既横排又竖排; 混合时拆 wrapper 子 FRAME, 父用 NONE | 2026-05-14 RoyalPass 行 AL 一刀切踩坑 (S3 #3.1 新加) |
| [`lesson_ccb维度vs多态.md`](lesson_ccb维度vs多态.md) | "抽不抽 ccb" 与 "有几个多态" 是独立维度; 复用必抽 ccb (可 0 多态), 有多态必是 ccb, 同一差异只在唯一最小单元做一次 | 2026-05-18 Team Battle 用户反复纠正 4+ 次 |
| [`lesson_v206schema必填字段.md`](lesson_v206schema必填字段.md) | 主路径手写 v20.6: component 必有 w/h/variant_property, INSTANCE w/h==component, layer 必有 element_class; 写前 cat 样本 | 2026-05-18 Team Battle Figma 全错位事故 |

## 状态标记

- 🟢 已沉淀进 skill 主流程 (S 文件 + skill 顶层铁律已经覆盖)
- 🟡 仅 lessons 归档, 主流程未集中提示
- 🔴 反复踩坑, 主流程也覆盖了但仍易犯 (高警惕)

| Lesson | 状态 |
|---|---|
| 扁平 vs v20.6 schema | 🔴 (S6/S7/S11 都强调过, 仍易犯) |
| 规则 11.5 子节点 name 一致 | 🟢 (07d 显著标红) |
| 进度条本体一整根 | 🟢 (07c + memory 都标红) |
| 组团内 layout 单一化 | 🟢 (S3 #3.1 + #9 checklist) |
| ccb 维度 vs 多态 | 🔴 (00f 边界1.5 + 06a + memory 都覆盖, 我仍反复栽 4+ 次) |
| v20.6 schema 必填字段 | 🔴 (11_S11 主路径自检 + 10_S10 都覆盖, 主路径手写仍易漏 w/h) |

## 用途

- Claude 看新视频前**扫一遍** lessons/, 把这些坑预防到识别 + 生成阶段
- 用户跑完一次发现新坑 → **加新 lesson** + 更新索引
