# Lesson · 反 from-exemplar (相似项目 scene.json = 风险信号不是捷径)

## 一句话
上下文里有相似项目 scene.json (`royal_pass_final.json` 等) = **风险信号不是捷径**, 禁照搬, 必每组团独立从视频 + memory 重推 — 80% 像恰恰掩盖那 20% 不一样的。

## 触发条件 (Trigger)
- **S0-S6 任一阶段**, Claude 工作目录或上下文里存在历史 `*final_scene.json` / `*scene.json` / 别的项目产物文件
- Claude 主动 `Read` / `Glob` 这些文件 → 当"权威样本"或"参考"对照
- S6 决议表里写"参考 XXX 项目" / "类似 YYY" / "对照 ZZZ"

## 失败模式 (What goes wrong)

### 反例 (2026-05-22 RP 跑出来观察到)

Claude S6 时主动找到 `royal_pass_final.json` + `royalpass_final.json`, 当成"权威样本"对照, 在 S6 决议表里写:

```
> 直接对照 royal_pass_final.json 和 royalpass_final.json (跟本次任务同名, 绝佳参考):
> 权威样本 royalpass_final.json 只抽 4 个最小单元 Component (不抽气泡/列表项)。
> 但用户决议明确"气泡 ccb + 列表项 ccb"。看另一个权威样本 royal_pass_final.json 怎么处理嵌套...
```

→ Claude 拿历史样本当"答案", 跟用户当前的决议冲突时不知道听谁的。

### 后果
- **当前任务被历史样本带偏** — 历史样本里没的元素, 当前任务也漏识别
- **错误传递** — 历史样本里的 bug 被复制到新产物
- **认知扁平化** — Claude 不再独立从视频识别, 只做"差异比较"

## 正确做法

### S0 阶段就声明
S0 加载时明确: **不读取工作目录下的其他 `final_scene.json` / `scene.json` 历史产物**。

### S6 决议表 写作时
- S6 决议表里**禁出现** "对照 / 类比 / 借鉴 XXX" 这类措辞
- 每个组团决议必基于:
  1. 用户当前 prompt 给的视频 + ccb 描述
  2. `memory/ui_pattern_*.md` (memory A 表)
  3. `steps/` 内的 SKILL 文档

### 万一意外读了历史产物
- Claude 必须**忽略**该信息, 不能影响 ccb / variant / layout 决议
- 在 S6 报告里**显式声明**: "已忽略历史产物 XXX, 本决议独立从视频识别"

## 自检方法

### 机器查 (S6 报告)
- grep S6 报告中是否出现"对照"/"参考"/"权威样本"/"类比"/"借鉴" 等措辞 → ❌ 失败
- grep S6 报告中是否引用 `*_final.json` 文件名 → ❌ 失败

### 人工查 (review S6 决议表)
- 用户 review 时直接问 Claude: "你这次有没有读其他项目的 scene.json?"
- 如果有 → 让 Claude 重做 S6, 这次显式忽略

## 关联铁律 / 文档

- **铁律 13** (S6 决议表 + 反 from-exemplar 锚定) — 本 lesson 是该铁律的具体化
- **06_S6_pattern命中.md** §"反 from-exemplar" — 主文档
- **memory/feedback_s6_pattern_must_scan_memory.md** — 元规则: S6 必扫 memory A 表, 不靠类比
- **lesson_列表行数完整性.md** — 相邻 lesson, 都防 Phase A 错位

## 实证案例

| 日期 | 屏 | 现象 | 修法 |
|---|---|---|---|
| 2026-05-22 | Royal Pass | Claude 主动找 royal_pass_final.json 当"权威样本"对照 → S6 决议跟用户冲突 | 用户打断 + 加本 lesson |

## 生命周期
- **创建**: 2026-05-22
- **状态**: active
- **优先级**: 高 — Claude 在新 session 里特别容易做这种事 (本能找 reference)
