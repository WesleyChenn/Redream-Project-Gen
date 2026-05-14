---
name: video-to-figma-json
description: 视频/截图 → Figma 插件 JSON 端到端工作流 (Redream 游戏引擎). 当用户说"把视频转成 Figma JSON"、"做 scene.json"、"识别 UI"、"抽 Component"、"跑 S1-S11"、"翻译游戏界面"、"做组件库"时激活此 skill. 11 步严格流水线 (S1 抽帧 → S11 抽 Component + 导出 v20.6 schema). 输出可直接粘到 Figma 插件 '▶ 生成' tab 一键出 Component Set + 屏幕.
---

## 工作流模式

**严格流水线** — S1 → S11 顺序执行, **不能跳步**. 每步前置依赖明确, 跳了下游崩。

跟 macOS / 通用任务 skill 的"按需加载 phases" 不同: 这里 S 步骤之间是**强依赖链**:
- S5 的 flow 是 S9 字段补全的输入
- S6 的 pattern 命中是 S7 生成骨架的依据
- S10 通过才能进 S11 抽 Component

---

## 完整流程图

```
┌── 识别阶段 (S1-S6, 只看不写) ──────────────────────────────┐
│                                                              │
│  S1 抽帧 ───→ S2 识别页面内容 ───→ S3 识别布局              │
│  (3 fps PNG)   (元素清单 + 量测)    (表 A/B/C 骨架/AL/组团)  │
│                                                              │
│  ───→ S4 识别交互 ───→ S5 提取 flow ───→ S6 pattern 命中    │
│       (滚动+触摸点)    (屏幕跳转表 F/G)   (表 H Variant)     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌── 生成阶段 (S7-S9, 写扁平 scene.json) ──────────────────────┐
│                                                              │
│  S7 生成骨架 ───→ S8 component_ref ───→ S9 字段补全 + flow  │
│  (扁平 FRAME)     (旧组件库引用)        (TEXT.content/flow)  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌── 校验导出阶段 (S10-S11) ────────────────────────────────────┐
│                                                              │
│  S10 自检 (9 层) ───→ S11 抽 Component + 导出 final_scene   │
│  全 ✅ 才进 S11        (v20.6 schema, 粘 Figma 插件)         │
│                                                              │
└──────────────────────────────────────────────────────────────┘

输出: final_scene.json → Figma 插件 '▶ 生成' → Component Set + 屏幕
```

---

## 步骤索引 (按顺序加载)

| 步骤 | 阶段 | 文件 (现位于 4.22skill_v2/) | 输入 | 输出 |
|---|---|---|---|---|
| S0 | 上下文 | [`00_S0_context.md`](steps/00_S0_context.md) | (始终首读) | 引擎/Figma/历史背景 |
| S1 | 识别 | [`01_S1_抽帧.md`](steps/01_S1_抽帧.md) | `.mp4` / `.mov` | N 帧 PNG (3 fps) |
| S2 | 识别 | [`02_S2_识别页面内容.md`](steps/02_S2_识别页面内容.md) | S1 帧 / 截图 | 元素清单 + 量测 |
| S3 | 识别 | [`03_S3_识别布局.md`](steps/03_S3_识别布局.md) | S2 元素清单 | 表 A 骨架 + 表 B AL + 表 C 组团 |
| S4 | 识别 | [`04_S4_识别交互.md`](steps/04_S4_识别交互.md) | S1+S2+S3 | 表 D 滚动区 + 表 E 触摸点 |
| S5 | 识别 | [`05_S5_提取flow.md`](steps/05_S5_提取flow.md) | S1+S4 | 表 F 屏幕清单 + 表 G flow 连线 |
| S6 | 识别 | [`06_S6_pattern命中.md`](steps/06_S6_pattern命中.md) | S3+memory pattern | 表 H pattern + Variant + 节点类型 + 包装类型 |
| S7 | 生成 | [`07_S7_生成骨架.md`](steps/07_S7_生成骨架.md) (主索引) | S6 表 H | 扁平 scene.json (无 INSTANCE/components[]) |
| S7a | 生成 | [`07a_S7_基础铁律.md`](steps/07a_S7_基础铁律.md) (必读) | 命名/JSON/fill/children/卡片底板 |
| S7b | 生成 | [`07b_S7_按钮.md`](steps/07b_S7_按钮.md) (按场景) | 按钮外壳/分组/触控范围/嵌套禁忌 |
| S7c | 生成 | [`07c_S7_进度条角标.md`](steps/07c_S7_进度条角标.md) (按场景) | 进度条三层/角标做法 B/`component_ref` 占位 |
| S7d | 生成 | [`07d_S7_嵌套占位背景.md`](steps/07d_S7_嵌套占位背景.md) (按场景) | 子 CCB 显隐/规则 11.5/visible 映射/占位/浮层 |
| S7e | 生成 | [`07e_S7_布局.md`](steps/07e_S7_布局.md) (必读) | constraints/AL 字段/弹性缝隙/滚动 |
| S8 | 生成 | [`08_S8_组件库引用.md`](steps/08_S8_组件库引用.md) | S7 含 `component_ref` 时跑, 否则跳过 |
| S9 | 生成 | [`09_S9_字段补全.md`](steps/09_S9_字段补全.md) | S7+S8 | TEXT.content + flow 数组 |
| S10 | 校验 | [`10_S10_自检.md`](steps/10_S10_自检.md) | S9 完整 scene.json | 9 层 verification 报告 |
| S11 | 导出 | [`11_S11_抽取导出.md`](steps/11_S11_抽取导出.md) | S10 全 ✅ | final_scene.json (v20.6 schema) |

---

## S7 子文件按场景加载路由

| S7 阶段碰到 | 加载文件 |
|---|---|
| 任何节点 (命名/JSON 格式/fill 规则) | **07a 必读** |
| 任何节点的布局 (constraints/AL/滚动) | **07e 必读** |
| 处理按钮 (手搓按钮/做法 B 包装) | 07b 按场景读 |
| 处理进度条 / 角标 | 07c 按场景读 |
| 处理嵌套实例 / 浮层背景 / 占位 RECT | 07d 按场景读 |
| 命中 component_ref (旧组件库) | S8 |

---

## Lessons 归档 (跨步骤踩坑教训)

跟 S 文件内的"违规信号"表互补 — 违规信号是该步内规则, lessons 是**跨步骤反复出现**的踩坑:

| 文件 | 一句话 |
|---|---|
| [`lessons/bug-archive.md`](lessons/bug-archive.md) | Bug 归档索引 + 状态标记 |
| [`lessons/lesson_扁平vs_v206_schema.md`](lessons/lesson_扁平vs_v206_schema.md) | S7-S9 是扁平 scene.json, INSTANCE/components[] 是 S11 自动产物 |
| [`lessons/lesson_规则11.5_子节点name一致.md`](lessons/lesson_规则11.5_子节点name一致.md) | 同结构多实例 children name 100% 一致, 否则 S11 抽不出 |
| [`lessons/lesson_进度条本体一整根.md`](lessons/lesson_进度条本体一整根.md) | 进度条本体永远画一整根 100% 满, 不按节点拆段 |
| [`lessons/lesson_组团内layout单一化.md`](lessons/lesson_组团内layout单一化.md) | 一个 FRAME 内子节点不能既横排又竖排, 混合时拆 wrapper |

Claude 看新视频前**扫一遍** lessons/, 把这些坑预防到识别 + 生成阶段。 用户跑完发现新坑 → 加新 lesson + 更新索引。

---

## memory ui_pattern 索引 (skill 一部分, S6 命中时按需读)

memory 路径: `memory/` (软链接到 `~/.claude/projects/-Users-red-Desktop-4-22--skill/memory/`)

通用 ui_pattern (9 个) — S6 pattern 命中时按需读对应文件:

| Pattern | 文件 |
|---|---|
| 元规则 | `ui_pattern_使用通则.md` (任何 icon 都可能有角标 / "该状态不显示" 用 visible:false) |
| 横排徽章_左图右文 | `ui_pattern_横排徽章_左图右文.md` |
| 角标_状态 | `ui_pattern_角标_状态.md` |
| 单图标_无角标 | `ui_pattern_单图标_无角标.md` |
| 进度条_横向 (单节点) | `ui_pattern_进度条_横向.md` |
| 进度条_多节点 (≥3 节点) | `ui_pattern_进度条_多节点.md` |
| 浮层_活动入口 | `ui_pattern_浮层_活动入口.md` |
| icon 带底部文本 | `ui_pattern_icon_带底部文本.md` |
| 按钮_纯文本 | `ui_pattern_按钮_纯文本.md` |
| 按钮_文本加icon | `ui_pattern_按钮_文本加icon.md` |

项目专属先验 (2 个):

| 先验 | 文件 |
|---|---|
| 用户项目金币堆视觉先验 | `user_visual_priors_金币堆.md` |
| 用户项目盾牌等级视觉先验 | `user_visual_priors_盾牌等级.md` |

---

## 跨步骤通用铁律 (摘自各 S 文件, 跨步骤都用)

1. **扁平 FRAME**: S7-S9 阶段输出**扁平 scene.json**, 没有 `type: INSTANCE` / `component_name` / `variant` / `overrides` / `components[]` (S11 抽取后才有)
2. **命名白名单 30 前缀**: 所有节点 `name` 前缀必须来自 `界面_/浮层_/组_/底板_/容器_/导航_/列表项_/...` 30 前缀 (详: 07a #1 / `命名_参考.md`)
3. **手搓节点 fill 一律省略**: FRAME 永远不填色; RECTANGLE 由插件按命名前缀自动分配灰色 (07a #3)
4. **字段命名 — 下划线 vs 驼峰**: `clip_content / corner_radius / font_size / font_weight / component_ref` 下划线; `layoutMode / primaryAxisSizingMode / textAlignHorizontal` 驼峰 (07a #2)
5. **隐藏用 `visible: false`, 不写 `variant: 空`**: variant/overrides 是 S11 抽取后才有 (07d #2.5)
6. **规则 11.5**: 同结构多实例 FRAME (列表行/网格项) 内部子节点 name **100% 一致**, 否则 S11 抽不出统一 Component
7. **嵌套按钮禁忌**: `按钮_xxx` FRAME 的 children 递归内**禁止再嵌套** `按钮_` 前缀 (07b #6)
8. **进度条本体永远画 100% 满**: 不写 percentage / `_p<数字>` 后缀, 引擎运行时按 percentage 切割 (07c #1)
9. **进度条本体永远是一整根**: 即使条上压有节点 icon, `进度条_XXX` RECT 仍画一整根, 不按节点位置拆段 (07c #1)
10. **角标允许视觉溢出**: 负坐标 / x+w 超出父本边界 OK, 但 constraints 用 LEFT/TOP + 正坐标 (07e #1)

---

## 工程默认值

| 项目 | 默认值 | 备注 |
|---|---|---|
| 目标设计稿 | **1080 × 2400** | 所有量测 × scale 到这个尺寸 |
| 源帧典型尺寸 | 1170 × 2532 (iPhone 13/14) | scale_x ≈ 0.923, scale_y ≈ 0.948 |
| 抽帧 fps | **3 fps** (每 333ms 一帧) | S1 不得跳帧 |
| flow 默认动画 | `dissolve 300ms` / `slide 300ms` / `OVERLAY` / `CLOSE` | S5 表 G + S9 flow 字段 |
| 命名前缀白名单数 | 30 | 详: `命名_参考.md` |
| Component 抽取脚本 | `/Users/red/Desktop/component_extractor/extract_components.py` | S11 备选路径用, 主路径绕开 |
| 输出 schema | v20.6 (含 INSTANCE + components[] + Variants) | S11 终产物 |

---

## S11 抽取路径选择

| 场景 | 路径 |
|---|---|
| 主屏有**奖励物**这种"枚举+占位混合 Variant" Component | 🔴 **主路径** — Claude 直接产 v20.6 (跳过 extract_components.py) |
| 主屏有 Variant 内部异构 (例: 大炮 Variant 含 FRAME) | 🔴 主路径 |
| 主屏全是同结构枚举 (例: 排行榜 8 行同构) + 各 Variant 内部同构 | 备选路径 (跑脚本 + 后处理删中间组团 + FRAME→INSTANCE 转换) |
| 简单主屏单 Component (无大/中间组团复杂度) | 备选路径 |

详: `11_S11_抽取导出.md` "主路径自检清单" + "标准动作 (备选路径)"

---

## 阶段路由

```
用户请求                                             → 加载文件
─────────────────────────────────────────────────────────────────
"把视频转成 Figma JSON" / "做 scene.json"             → S0 → S1 → ... → S11 (全跑)
"我有截图, 跳过抽帧"                                   → S0 → S2 → ... → S11 (跳过 S1)
"重跑 S6 修 pattern"                                  → 单独跑 S6 (基于已有 S3 输出)
"S7 阶段碰到进度条"                                    → 07c 进度条角标
"S7 阶段碰到按钮"                                      → 07b 按钮
"S6 pattern 命中"                                     → memory ui_pattern_xxx.md (按 pattern 名读)
"S10 自检不过"                                        → 回失败层对应的 S 步骤修, 重新 S10
"我要换组件库"                                        → S8 + 三项预检
```

---

## 完整加载路由表 (Claude 内部按需查阅, 现象 → 文件)

S7 子文件路由已在前面 (按钮 → 07b / 进度条角标 → 07c 等)。 下面是**更细颗粒度**的 3 张表 — 让 Claude 在跑视频时, 看到具体视觉 / 风险 / 疑问就知道翻哪个文件, 不再凭经验。

### A. S6 视觉命中路由 (看到 X 视觉 → 加载 Y 文件)

| Claude 在 S6 阶段看到的视觉特征 | 加载主文件 | 配套预防 lesson |
|---|---|---|
| 全屏弹窗 (顶 i+X + 中装饰 + 标题 + 倒计时) | [`memory/ui_pattern_浮层_活动入口.md`](memory/ui_pattern_浮层_活动入口.md) | — |
| 长条横向进度条 + 双层 RECT + X/Y 文本居中 | [`memory/ui_pattern_进度条_横向.md`](memory/ui_pattern_进度条_横向.md) | [`lessons/lesson_进度条本体一整根.md`](lessons/lesson_进度条本体一整根.md) |
| 长条进度条 + ≥3 节点沿条分布 | [`memory/ui_pattern_进度条_多节点.md`](memory/ui_pattern_进度条_多节点.md) | [`lessons/lesson_进度条本体一整根.md`](lessons/lesson_进度条本体一整根.md) |
| 长胶囊底板 + 左 icon (上下溢出) + 右数字 | [`memory/ui_pattern_横排徽章_左图右文.md`](memory/ui_pattern_横排徽章_左图右文.md) | — |
| 主体边缘小角标 (右上/右下/左下/左上 4 处) | [`memory/ui_pattern_角标_状态.md`](memory/ui_pattern_角标_状态.md) | — |
| 独立 icon, 近正方形, 无附加 | [`memory/ui_pattern_单图标_无角标.md`](memory/ui_pattern_单图标_无角标.md) | — |
| icon 正下方挂文本 (丝带/圆角数字/按钮/纯文本) | [`memory/ui_pattern_icon_带底部文本.md`](memory/ui_pattern_icon_带底部文本.md) | — |
| 圆角矩形 + 文本居中, 无 icon | [`memory/ui_pattern_按钮_纯文本.md`](memory/ui_pattern_按钮_纯文本.md) | — |
| 文本 + icon 按钮 | [`memory/ui_pattern_按钮_文本加icon.md`](memory/ui_pattern_按钮_文本加icon.md) | — |
| 项目专属: 顶图标 + 中丝带 + 下数字嵌丝带 | [`memory/user_visual_priors_金币堆.md`](memory/user_visual_priors_金币堆.md) | — |
| 项目专属: 大盾牌外凸 + 右胶囊数字 | [`memory/user_visual_priors_盾牌等级.md`](memory/user_visual_priors_盾牌等级.md) | — |
| (S6 命中前先读元规则) | [`memory/ui_pattern_使用通则.md`](memory/ui_pattern_使用通则.md) | — |

### B. Lessons 预防触发 (看到 X 风险场景 → 翻 lesson 预防)

| 看到风险场景 (S2-S6 阶段) | 加载 lesson |
|---|---|
| 视频里有 8 行 / N 行高度重复结构 | [`lessons/lesson_规则11.5_子节点name一致.md`](lessons/lesson_规则11.5_子节点name一致.md) — **写之前**就固定命名模板, 8 行严格按模板 |
| 视频里某 FRAME 内同时含横排 + 竖排元素 | [`lessons/lesson_组团内layout单一化.md`](lessons/lesson_组团内layout单一化.md) — 拆 wrapper, 不一刀切 AL |
| 准备在 S7 写 INSTANCE / `variant: 空` / `overrides` 字段 | [`lessons/lesson_扁平vs_v206_schema.md`](lessons/lesson_扁平vs_v206_schema.md) — **不要写**, 那是 S11 自动产物 |
| 多节点进度条想"按节点位置拆段画" | [`lessons/lesson_进度条本体一整根.md`](lessons/lesson_进度条本体一整根.md) — 永远画一整根 |

### C. 字段 / 命名疑问 → 查阅文件

| 疑问 | 翻哪 |
|---|---|
| 这个节点命名前缀对不对 / 30 前缀白名单 | [`命名_参考.md`](命名_参考.md) |
| 字段名是下划线还是驼峰 (clip_content vs clipsContent) | [`steps/07a_S7_基础铁律.md`](steps/07a_S7_基础铁律.md) #2 字段命名铁律 |
| AL 容器要写什么字段 (primaryAxisSizingMode 等) | [`steps/07e_S7_布局.md`](steps/07e_S7_布局.md) #2 |
| 进度条三层怎么命名 (组_进度_X / 底板_X / 进度条_X) | [`steps/07c_S7_进度条角标.md`](steps/07c_S7_进度条角标.md) #1 |
| 角标包装做法 B (按钮 FRAME 外壳) | [`steps/07c_S7_进度条角标.md`](steps/07c_S7_进度条角标.md) #2 |
| flow 字段写法 (trigger/from/to/animation) | [`steps/09_S9_字段补全.md`](steps/09_S9_字段补全.md) #4 |
| `component_ref` 缩放计算 / 三项预检 | [`steps/08_S8_组件库引用.md`](steps/08_S8_组件库引用.md) |
| S11 抽取后处理 / 中间组团删除 / 主路径 vs 备选 | [`steps/11_S11_抽取导出.md`](steps/11_S11_抽取导出.md) |
| S10 9 层自检具体每层查什么 | [`steps/10_S10_自检.md`](steps/10_S10_自检.md) |
| S3 #3.1 layout 单一化具体怎么跑 | [`steps/03_S3_识别布局.md`](steps/03_S3_识别布局.md) #3.1 (Step 1-6) |

### 路由表使用方式

- **S6 阶段必扫 A 表** — 每个组团对照 12 个视觉特征, 命中即读对应 memory pattern 文件
- **S2-S6 阶段持续扫 B 表** — 看到 4 个风险场景就翻对应 lesson, **写之前**先预防
- **写 JSON / 自检碰到疑问扫 C 表** — 不在记忆里就查 C 表对应文件

---

## 文件结构

```
4.22skill_v3/
├── SKILL.md              ← 顶层入口 (本文件, frontmatter + 流程图 + 路由 + 铁律)
├── steps/                ← 17 个 S 文件 (从 v2 复制, 内容相同)
│   ├── 00_S0_context.md
│   ├── 01_S1_抽帧.md ... 11_S11_抽取导出.md
│   └── 07a_*.md ... 07e_*.md (S7 子文件)
├── lessons/              ← 跨步骤踩坑归档 (新加, 跟 S 文件违规信号互补)
│   ├── bug-archive.md (索引)
│   └── lesson_*.md (4 个核心 lesson)
├── memory/               ← 软链接到 ~/.claude/projects/.../memory (跟 v2 共享)
└── 命名_参考.md           ← 命名白名单参考 (从 v2 复制)
```

## 跟 v2 的关系

- **v3 已独立化** — 不依赖 v2, 可以单独工作 (steps/ 含全部 17 个 S 文件)
- **v2 内容完全不动** — 所有原 S 文件原位保留在 `/Users/red/Desktop/4.22skill_v2/`, 作为 backup
- **memory 是软链接共享** — v2 和 v3 都指向同一个 `~/.claude/projects/.../memory/`, 改任何一边的 memory 互通
- v3 改 SKILL.md / 加新 lessons / 调整 steps/ 内某 S 文件, 都不影响 v2

## 借鉴来源

参考 `/Users/red/Desktop/macos-native-app/` skill 结构, 借鉴这些元素:

- ✅ SKILL.md 顶层入口 + frontmatter (触发关键词)
- ✅ ASCII 流程图概览
- ✅ lessons/ 跨步骤踩坑归档
- ✅ 通用铁律集中化 (10 条)
- ✅ 工程默认值表
- ✅ 阶段路由表 (用户说 X → 加载 Y)

保留我们项目的内核:

- 🔴 严格流水线 (S1-S11 顺序不能跳, 不是 macOS 那种任务路由)
- 🔴 memory 机制 (项目专属先验 + ui_pattern 11 个)
- 🔴 component_extractor 外部脚本依赖
