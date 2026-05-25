# Lesson 模板 (统一格式, 2026-05-22 系统化引入)

> 每个新 lesson 必按本模板的 7 字段写; 老 lesson 逐步迁移到此模板。

---

# Lesson · <一句话标题>

## 一句话
<1 句话概括 lesson 核心 — 写到 SKILL.md Lessons 索引表的就是这句>

## 触发条件 (Trigger)
<这条 lesson 在哪个 S 步骤 / 看到什么视觉特征 / JSON 检查到什么模式时触发; 尽量可机器检查>

例:
- `S6 阶段, 视频里出现某组团连续重复 ≥3 次`
- `S7 阶段, component variant 字段只差 corner_radius ±1 或 opacity ±0.01`
- `S2 阶段, 视频是滚动列表 (有滚动行为)`

## 失败模式 (What goes wrong)
<不遵守这条 lesson 会出什么错? 给反例 — 具体 JSON 片段 / 截图描述 / 引擎渲染结果>

## 正确做法 (Correct approach)
<怎么做才对? 给正例 — 具体 JSON 片段 / 操作步骤>

## 自检方法 (Verification)
<怎么检查这条 lesson 被遵守? 优先机器查, 次选 S10 自检清单条目, 再次人工 review>

例:
- **机器查 (S10)**: `for variant in component.variants: if 仅有 corner_radius diff → ❌`
- **人工查**: S6 决议表 review 时问"variant 视觉差异是什么?"

## 关联铁律 / 文档
<跟哪些 SKILL.md 铁律 / 步骤 §章节 / 其他 lesson 互相引用?>

例:
- **铁律 N** (xxx 合约) — 这条 lesson 是该铁律的具体化
- **07e §xxx** — 标准写法
- **lesson_yyy** — 相邻 lesson, 处理近似问题

## 实证案例 (Evidence)
<这条 lesson 是从哪些具体 run / bug 总结来的? 列出 (日期 + 屏 + 现象 + 修法验证)>

| 日期 | 屏 | 现象 | 修法 |
|---|---|---|---|
| 2026-XX-XX | XXX | XXX | XXX |

## 生命周期
- **创建**: <date>
- **状态**: active / merged / deprecated
- **更新历史**: <date>: <修改了什么>
