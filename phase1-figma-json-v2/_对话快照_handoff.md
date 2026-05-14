# 对话快照 / Handoff (2026-05-13)

> 这份是对话上下文压缩前的快照, 方便新 session 接续。
> **下次启动时**: 用户会让你继续讨论 **memory 同步问题** (方向 A + 简化版 B)。

---

## 项目背景

- **项目目录**: `/Users/red/Desktop/4.22skill_v2/` (新 skill v2)
- **旧 skill**: `/Users/red/Desktop/4.22最新skill/` — ⛔ **绝对不覆盖**
- **目标**: 把旧 skill (13 文件, 3700 行, "狗熊掰棒子" 痛点) 重构成新 skill (按 S0-S11 性质拆分)
- **工作流**: 视频/截图 → scene.json (Claude 阶段一扁平) → Figma 插件 → 设计师调整 → extract_components.py → v20.6 schema → red_tool → .red → Redream 引擎

---

## 新 skill v2 当前结构 (18 文件)

| 文件 | 行 | 内容 |
|---|---|---|
| `00_S0_context.md` | 349 | 世界观 (15 节, 含嵌套 CCB 三层模型) |
| `01_S1_抽帧.md` | 91 | 【录屏专用】 |
| `02_S2_识别页面内容.md` | 160 | 量测 + 双重核查 |
| `03_S3_识别布局.md` | 328 | 组团化递归 + 角标依附 |
| `04_S4_识别交互.md` | 258 | 滚动 + 触摸点 + 装饰归父按钮 |
| `05_S5_提取flow.md` | 182 | 屏幕清单 + 转场回溯 |
| `06_S6_pattern命中.md` | 549 | 🔴 核心 — pattern + 子 CCB 4 步法 + 包装类型 3 并列 |
| `07_S7_生成骨架.md` | 157 | S7 主索引 (跳转 7a-7e) |
| `07a_S7_基础铁律.md` | 212 | 命名白名单 + JSON 格式 + 字段命名 + fill + children 顺序 + 卡片底板 + 一层底 + 额外约束 |
| `07b_S7_按钮.md` | 117 | 按钮 + 内容居中 |
| `07c_S7_进度条角标.md` | 172 | 进度条三层 + 角标做法 B + component_ref 占位 |
| `07d_S7_嵌套占位背景.md` | 210 | 子 CCB 扁平 FRAME + 规则 11.5 + 占位 RECT + 浮层背景 |
| `07e_S7_布局.md` | 254 | constraints + AL + 滚动 |
| `08_S8_组件库引用.md` | 336 | component_ref 缩放 + Push 同步 |
| `09_S9_字段补全.md` | 335 | TEXT.content + flow (from_node + 导航全量连线) |
| `10_S10_自检.md` | 287 | 阶段一 9 层 verification |
| `11_S11_抽取导出.md` | 512 | 阶段二 4 层 + extract_components + Component 修复 |
| `命名_参考.md` | 229 | 命名规范跨步骤索引 (10 节) |
| **总计** | **~4738** | 所有文件 ≤ 550 行, 模型可完整读 |

---

## 关键决策 / 用户偏好

### 用户的核心反馈

1. **不在旧文件夹覆盖** — 新建 `4.22skill_v2/` (硬约束)
2. **包含旧 skill 全部内容,只是重新布局**
3. **每个文件 < 400 行**(模型可完整读)
4. **识别阶段独立成层**(S1-S6 全是"看")
5. **memory 主 / 组件库辅** — 旧组件库基本不可用,memory 11 pattern 为主
6. **S0 = 世界观, 不是操作铁律堆叠**
7. **协作角色靠前 (#3 协作角色 → S0)**
8. **识别布局也是"看"的一部分** (并入 S0 第 12 节识别阶段)
9. **CCB 抽取判定**: 多处复用 → CCB; 抽到最小变化粒度; 同 Component 多 Variant; 父级类似但部分缺子集 → 空 Variant
10. **memory 是教学/参考不是铁律** — 命中 ≠ 完全一致, 视频实际优先
11. **按钮/进度条独立识别** — 命名要在底板层 / 进度条内容层表明 (S6 5.1 + 5.2 + 5.3 三并列)
12. **删 Component 必须先问用户**
13. **滚动区基于 S4 表 D 识别**, 不靠"子 h > 父 h"
14. **Toggle → 切换** (中文化, 已替换 5 处)

---

## 重要修补汇总 (28 处)

### 第一批 致命字段错误 (7 处, 已修)

1. ✓ `screens` 用 `w/h` 不是 `width/height`
2. ✓ `flow.from_node` 字段 (`from` = 源屏, `from_node` = 触发节点)
3. ✓ 弹性缝隙 `layoutSizingHorizontal: FILL + w:0 h:0` (不是 `layoutGrow: 1`)
4. ✓ `primaryAxisSizingMode` 取值 FIXED/AUTO (不是 HUG/FILL)
5. ✓ 滚动子容器 `primaryAxisSizingMode: AUTO`
6. ✓ 字段命名铁律 (下划线 vs 驼峰 + code.js grep)
7. ✓ `layoutPositioning: ABSOLUTE`

### 第二批 关键铁律 (8 处, 已修)

8. ✓ 规则 11.5 子节点 name 100% 一致
9. ✓ children 排序铁律 (底到顶 / 关闭按钮最后)
10. ✓ component_ref 替换手搓陷阱 (`底板_` 必须 RECT)
11. ✓ 导航栏双态组件 (S6 #2)
12. ✓ 导航栏全量连线 N×(N-1) (S9 #4)
13. ✓ 角标位置 LEFT/TOP + 正坐标 (Figma RIGHT/CENTER 飞出 bug)
14. ✓ 卡片/弹窗外壳必须 RECT
15. ✓ wrapper visible/opacity 映射 + 实例间差异类型限制

### 第三批 字段细节 (9 处, 已修)

16-24 ✓ TEXT 不写 w / 禁 stroke / AL 禁用 SPACE_AROUND·STRETCH / 同组尺寸一致 / 量测容差 ±5% / 同屏 name 唯一 / 无"一层底" / 老命名禁止 (v18/v19) / 滚动不进 flow / override 类型限制

### Explore agent 二次审计补 (4 处, 已修)

25. ✓ 进度条 constraints `SCALE/TOP` + 顶部/底部固定区 `SCALE/TOP·BOTTOM`
26. ✓ code.js grep 查证方法论
27. ✓ 滚动区基于 S4 表 D 识别 (S10 删 "子 h > 父 h" 铁律)
28. ✓ S11 "为什么需要阶段二" 背景

---

## 🔴 待办: memory 同步问题 (用户选了 A + 简化版 B)

### 问题诊断

**Memory 9 个 ui_pattern.md 的 JSON 例子全是阶段二 v20.6 schema 形态** (含 `type: INSTANCE` / `component_name` / `variant` / `overrides`), 跟新 S7 阶段一扁平 FRAME 铁律**直接冲突**。

具体冲突点:

- `ui_pattern_横排徽章_左图右文` Line 128-139: 例子用 `"type": "INSTANCE", "component_name": "横排徽章_左图右文", "variant": "默认", "overrides": {...}`
- `ui_pattern_角标_状态` Line 94-105: Variants 模板 (锁/对勾/数字/空/...) — 教模型直接生成 Variant 节点
- `ui_pattern_角标_状态` Line 116-121: 包装结构用 `INSTANCE <主体> / INSTANCE <角标>`
- 进度条命名 `文本_体力_进度` (双下划线分隔, 风格不一致)

### 用户选了"方向 A + 简化版 B"

- **方向 A**: 改 memory — 把所有 9 个 ui_pattern.md 的 JSON 例子改成 S7 阶段一**扁平 FRAME** 形态 (每实例独立 + `visible: false` 切换)
- **简化版 B**: S6 #1 顶部加一句明示警告 — "memory 例子是 v20.6 schema 形态, 你在 S7 阶段必须**翻译成扁平 FRAME 版本**, 具体扁平形态见 07d"

### Memory 文件路径

- 真实位置: `/Users/red/.claude/projects/-Users-red-Desktop-4-22--skill/memory/`
- 软链接: `/Users/red/Desktop/4.22最新skill/memory/`

### 9 个 ui_pattern 文件清单 (要改)

1. `ui_pattern_使用通则.md` — 元规则 4 提到"做空 Variant"是阶段二概念, 加注阶段一用 `visible: false`
2. `ui_pattern_横排徽章_左图右文.md` — JSON 例子 (Line 128-139, 142-152) 改扁平
3. `ui_pattern_角标_状态.md` — Variants 模板 + 包装结构例子改扁平
4. `ui_pattern_进度条_横向.md` — 检查 + 命名风格 (`文本_体力_进度` → `文本_体力进度`?)
5. `ui_pattern_进度条_多节点.md`
6. `ui_pattern_单图标_无角标.md`
7. `ui_pattern_按钮_纯文本.md`
8. `ui_pattern_按钮_文本加icon.md`
9. `ui_pattern_icon_带底部文本.md`
10. `ui_pattern_浮层_活动入口.md`
11. `user_visual_priors_盾牌等级.md`
12. `user_visual_priors_金币堆.md`

(Memory 共 15 个文件, 含 3 个 feedback + 2 个 user_visual_priors)

---

## 下次启动 (接续时这样做)

新 session 启动后, 跟用户简短确认:

1. 当前要继续 **memory 同步**任务 (方向 A + 简化版 B)
2. 先做 **简化版 B** (改 S6 #1 顶部加警告 — 工作量小, 立即收益)
3. 再做 **方向 A** (依次改 11 个 memory pattern 文件的 JSON 例子)
4. 改完后 grep 验证 memory 里没有 `"type": "INSTANCE"` 例子 (除非明确标"S11 抽取后形态")

---

## Plan File 路径 (历史参考)

`/Users/red/.claude/plans/skill-json-skill-skill-abundant-haven.md` — 最初的设计计划 (S0 锁定 + S1-S11 分层), 后续大量演进, 实际以新 skill 文件夹为准。
