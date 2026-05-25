# v3 视觉缩窄即 AL 版 (2026-05-21)

> 基线 = `/Users/red/Desktop/5.21工作流/4.22skill_v3_只停S6/`
> 主改: **S3 layoutMode 跟 S7 AL 字段统一成一个合约**, 不再分两次判断
> 目的: 修上版"列表项内部退化成 NONE+绝对坐标" 的根因 (而不是补丁)

## 关键改动 (4 处)

| 文件 | 改动 |
|---|---|
| `SKILL.md` 铁律 14 | **删** "复用类 component 内部也必须用 AL" 补丁段 (并入新铁律 15) |
| `SKILL.md` 铁律 15 (**新加**) | **AL = S3 layoutMode 合约 (视觉缩窄即 AL, 跨层级一致)** 元规则 |
| `steps/03_S3_识别布局.md` | 加 §"layoutMode 合约 → S7" 小节, 把 S3 layoutMode 判定升级为 S7 硬合约 |
| `steps/07e_S7_布局.md` §复用类 component 内部布局 | 头部改写为"S3 layoutMode 合约的实现样例", 不再当独立规则 |
| `lessons/lesson_视觉缩窄即AL.md` (**新建**) | 概念解释 + 实证失败 + 正确做法 + 跨层级一致表 |

## 跟上版的核心差异

| 维度 | 上版 (只停S6) | 本版 (视觉缩窄即AL) |
|---|---|---|
| S3 layoutMode 角色 | 给出 layout 建议 | **S7 的硬合约** |
| S7 写 component 时 | 重新判一次, 倾向 NONE | **直接执行 S3 合约, 必 AL** |
| 内部 AL 规则 | 07e §复用类 当独立补丁 | 03_S3 §"layoutMode 合约" 作根源元规则 |
| 铁律 14/15 | 14 含"复用类 AL"补丁 | 14 干净 + 15 新加元规则 |
| 跨层级一致性 | 外侧大组团 vs 内部 component 不一致 | **所有层级用同一规则** |

## 实证 bug 修法演化

| Bug | 上版 (补丁修法) | 本版 (根因修法) |
|---|---|---|
| TT 列表项 收集物出底板 20px | 加规则"复用类 component 内部用 AL" (补丁) | S3 已标 HORIZONTAL → S7 必 AL (合约) |
| JO 列表项 角标出 75px | 同上 | 同上 |
| 列表项内部嵌套 (组_名字 / 组_名字行) | 没明确说也要 AL | **跨层级合约自动覆盖** |

## 副作用预期 (好的)

**认知简化** → Claude 不用在 S7 再决策"内部要不要 AL", S3 已经判好, 注意力释放出来给 Phase A 内容识别 → **可能缓解上版"列表 13→6 行"的丢件问题**。

## 验证方法

新 session 在 `/Users/red/Desktop/5.21工作流/4.22skill_v3_视觉缩窄即AL/` 开, 跑同样的视频 + prompt, 看:

| 项 | 期望 |
|---|---|
| 列表项 component layoutMode | HORIZONTAL (不是 NONE) |
| 列表项 内部子节点 | 不写 x/y, 用 AL itemSpacing 接管 |
| 组_名字 内部 | VERTICAL AL |
| 组_名字行 内部 | HORIZONTAL AL |
| 溢出 | 无 |
| 列表行数 | 完整 (TT 13 行 / JO 5 行) |

## 五个工作目录的关系

| 路径 | 状态 |
|---|---|
| `/Users/red/Desktop/4.22skill_v3/` | 老老版 — 完全不动 |
| `/Users/red/Desktop/5.18工作流/4.22skill_v3/` | 5.18 保存版 — 完全不动 |
| `/Users/red/Desktop/5.21工作流/4.22skill_v3/` | 5.21 大组团语义表版 — 完全不动 |
| `/Users/red/Desktop/5.21工作流/4.22skill_v3_只停S6/` | 提速 + 内部 AL 补丁 — 完全不动 (上版) |
| `/Users/red/Desktop/5.21工作流/4.22skill_v3_视觉缩窄即AL/` | **本目录** — 根因修法, 验证后再决定要不要正式启用 |
