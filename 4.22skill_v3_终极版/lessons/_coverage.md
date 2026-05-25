# Lessons 覆盖度地图 (2026-05-22)

> 按 S 步骤 × 错误类型 列出 high-freq 错误, 标注**已有 lesson** / **gap (没 lesson)**。
> 维护目的: 主动发现"经常错但没 lesson 防"的 gap, 不等到事故才加。

---

## 阶段 × 错误类型 矩阵

| 阶段 | 高频错误 | 已有 lesson | gap? |
|---|---|---|---|
| **S2 识别页面内容** | 滚动列表行数漏识别 (只看首屏) | `lesson_列表行数完整性.md` ⭐ 2026-05-22 新加 | ✅ 已盖 |
| S2 | 当前用户行被错认成自我条 / 复制 | (无独立 lesson) | 🟡 gap, 但 prompt 补强能盖 |
| S2 | 副标 vs 道具 在视频里看走眼 | (无) | 🟡 gap, 同上 |
| **S3 识别布局** | 一 FRAME 既横排又竖排 没拆 wrapper | `lesson_组团内layout单一化.md` | ✅ |
| S3 | S3 标 H/V 但 S7 退化成 NONE | `lesson_视觉缩窄即AL.md` | ✅ |
| **S6 pattern 命中** | 抽 ccb / 多态决议错位 (复用/动态/独立 vs 多态混淆) | `lesson_ccb维度vs多态.md` | ✅ |
| S6 | 进度条本体被当面板背景吞 | `lesson_进度条本体一整根.md` | ✅ |
| S6 | 复用 ≥3 没抽 component, 写 inline FRAME N 次 | `lesson_复用结构必抽component.md` ⭐ 2026-05-22 新加 | ✅ 已盖 |
| S6 | 从 royal_pass_final.json 等历史样本对照, 不独立识别 | `lesson_反from-exemplar.md` ⭐ 2026-05-22 新加 | ✅ 已盖 |
| **S7 生成骨架** | 写了 INSTANCE / `variant: 空` / `overrides` (扁平阶段不该有) | `lesson_扁平vs_v206_schema.md` | ✅ |
| S7 | 同结构多实例 children name 不一致 | `lesson_规则11.5_子节点name一致.md` | ✅ |
| S7 | 复用类 component 用 AL 外层 + 底板 ABSOLUTE (z 序 bug) | `lesson_AL内ABSOLUTE底板z序bug.md` | ✅ |
| S7 | 完整子节点内部用 SCALE 拉伸 (按钮内底板等) | (无独立 lesson, 但 SKILL 铁律 14 大组团语义表已覆盖) | ✅ 铁律覆盖 |
| S7 | claim/CLAIM/OPEN 等动作词没命名 `按钮_<动作>` | (无独立 lesson, 但 SKILL 铁律 16 + 07b §0 覆盖) | ✅ 铁律覆盖 |
| **S9 字段补全** | INSTANCE override 不全 (列表行 N 行都默认值) | (无) | 🔴 gap, 可加 lesson |
| **S10 自检** | 假 variant (仅 corner_radius ±1 / opacity ±0.01 凑数) | (无) | 🔴 gap, 可加 lesson |
| **S11 抽取导出** | 手写 v20.6 schema 漏字段 | `lesson_v206schema必填字段.md` | ✅ |

---

## 当前 lesson 数: 11 (含本次 5.22 新加 3 个)

按主题分布:
- A. Schema 类: 2
- B. ccb / 组团 / 多态类: 4
- C. AL / 布局类: 2
- D. Pattern 命中 / 视觉识别类: 2
- E. 工作流 / 反 satisficing 类: 1

---

## 标记的 gap (3 个, 优先级排序)

1. 🔴 **S10 假 variant 检查** — 高频, 建议下次写
2. 🔴 **S9 INSTANCE override 完整性** — 高频, 建议下次写
3. 🟡 S2 当前用户错位 / S2 副标vs道具 — 可 prompt 补强代替, 不一定要独立 lesson

---

## 更新历史

- 2026-05-22: 系统化引入 (template + taxonomy + coverage)
  - 新加 3 lessons: 列表行数完整性 / 复用结构必抽 component / 反 from-exemplar
- 2026-05-22: 之前漏的索引补全 (lesson_视觉缩窄即AL + lesson_AL内ABSOLUTE底板z序bug)
