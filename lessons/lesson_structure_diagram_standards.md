# Lesson: 工程结构图必须遵循 cocos 三铁律（Rebolt 部分除外）

**日期:** 2026-04-14
**状态:** ✅ 已修复

## 事件

为六格烧烤生成 Redream 结构图时，仅凭借 elsa + redream 两个 skill 的规范产出，结果粒度过粗：

- CCB 拆分不足（7 张卡片，缺 boost_bar / tutorial_layer / boost_button / tutorial_hand，通关/失败未分）
- 节点是占位名（"HUD区定位区"、"结果面板定位区"）而非具体 S/Lb/Sp
- 有卡片时间线为空，违反铁律一
- 食材串（可移动 CCB）缺 `动画_移动`，违反铁律二
- 命名含隐含数量描述（`food_element` 代指"6个一组"），该信息应该在 desc

## 根因

合并 skill 时只搬了 elsa-analyzer-line（阶段 1 骨架分析）和 redream-skill（阶段 3 CLI 落地），**没把 cocos-project-gen 的 phase1-structure-diagram 标准搬进来**。阶段 2 的"工程结构图规范"在 cocos 和 Redream 两个管线里本质是**同一组规则**（铁律一/二/三 + 命名禁括号 + 一对多显式 + 三列布局），只是节点类型和时间线表达形式不同。

## 规则

在 Redream 阶段 2（HTML 结构图）生成时必须套用 cocos 的三铁律：

1. **铁律一**：每张卡片 `timelines` 数组 ≥ 1（最小 `常态`）
2. **铁律二**：可移动 CCB（被 Rebolt 驱动移动的）必含 `常态` + `动画_移动`
3. **铁律三**：同列卡片 y 按累计高度+GAP(24) 排布，防重叠

命名规范：
- ❌ `food_element（dyn×6）` ✅ `食材串` + desc 写"dyn 6 个"
- 节点用前缀：图片_xxx / 文本_xxx / Spine_xxx / 按钮_xxx定位点 / xxx区定位区 / xxx定位层 / xxx生成层

连线规范：
- 一对多必须逐一显式（通关/失败两个面板就是两张独立卡片 + 两条独立连线，不能塞进一个 result_panel）

**Why：** Redream 虽然是 Redream 引擎，但"工程结构图"本质上是组件拆分+状态机+时序的可视化文档，与引擎无关。三铁律是"把不完整设计暴露出来"的工具，不套用会产出看似完整但实际不可施工的蓝图。

**How to apply：** 下次执行 phase2-structure-diagram 时，先打开 cocos-project-gen/phases/phase1-structure-diagram.md 确认三铁律，再生成 JSON。生成后跑 phase2 文档里的自检脚本（含铁律一/连线引用/fromNode 序号），铁律二需人工 review。

## 例外：Rebolt 部分保持 Redream 自有规范

`funcs` `vars` `notifs` 三个段属于 `.rebolt` 行为树体系，**不要**套用 cocos 的 Controller `Ct` + `</>` 程序徽标（那是 CC3 的 TS 脚本组件概念）。Rebolt 部分始终参照 `references/rebolt*.md`。

---

## 二次教训（2026-04-14 同日）：结构图输入必须来自 ground truth，不是想象

第一次重生成后，我把六格烧烤做成 12 卡（加了 boost_bar / tutorial_layer / hud / result_win / result_lose / boost_button / tutorial_hand），但 PDF 里**根本没提**道具栏/引导层/步数，原 Cocos 工程里也**只有 6 个 prefab**（主界面/棋盘/容器/元素/完成反馈特效/广告横幅）。

**根因**：我凭"典型休闲游戏都有道具栏+引导"的经验扩展，违反了全局 memory `feedback_no_guessing.md`（禁止靠猜）。铁律本身没错，但应用对象必须对齐真实工程。

**规则**：阶段 2 生成结构图前，必须先确认三个 ground truth 源，按优先级：

1. **原工程源码**（`.prefab` / `.scene` / `.red`）— 最权威，反映实际实现
2. **产品 PDF / PRD**（仅用于补充状态/流程语义，不作为拆 prefab 依据）
3. **游戏录屏**（用于视觉细节，最低优先级）

**禁止来源**：
- ❌ "类似游戏通常都有"的经验推测
- ❌ PDF 里提到但源码未实现的模块（如本项目的"结果面板"）— 若跨引擎迁移且目标需补齐，必须明确告知用户并等确认

**How to apply**：拿到需求后，先跑一轮 inventory：
```bash
find <project_root>/assets -name "*.prefab" -type f   # 枚举真 prefab
# 或派 Explore agent 抽取每个 prefab 的节点树 + 动画 + 脚本实例化关系
```
再据此决定 cards 数量，不能先画再找依据。

**关联记忆**：`~/.claude/projects/-Users-liuying/memory/_global/feedback_no_guessing.md`
