# Lessons 目录

本目录用于累积 Redream-project-gen 管线执行过程中**踩过的坑 + 已修复的 Bug**，供后续会话快速规避。

## 命名规范

- `bug-archive.md` — 历史 Bug 的汇总清单（含状态：✅ 已修复 / ⚠️ 仍需警惕）
- `lesson_<topic>.md` — 针对某个话题的独立教训（格式参考 `cocos-project-gen/lessons/lesson_*.md`）

## 何时写入

- 用户反馈某处有问题，修复后提炼规则（"每轮反思沉淀"铁律的落地）
- 某类错误反复出现，值得单独立档
- 某个 CLI 行为 / `.red` / `.rebolt` 字段语义与预期不符

## 何时读取

- 执行 phase3 前扫一眼 bug-archive，避免重复踩坑
- 用户报告问题，先检索 lessons/ 是否已有同类记录
- 新会话激活 skill 时，若任务涉及某话题（如 Spine、stub 嵌套、发布），加载对应 lesson

## 与全局 memory 的分工

| 场景 | 落盘位置 |
|------|---------|
| 本 skill 内的具体实现细节（CLI 字段、HTML 结构图某规则） | `lessons/` |
| 通用 agent 规则（跨 skill 的教训，如"禁止靠猜"、"尺寸按视觉"） | `~/.claude/projects/-Users-liuying/memory/_global/feedback_*.md` |
