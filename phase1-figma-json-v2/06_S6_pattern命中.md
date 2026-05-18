# S6 · 识别 pattern 命中 (核心新增步骤)

> **阶段**: 识别阶段, 最后一步 — 把 S3 最小组团跟视觉模板库匹配
> **前置**: S0 上下文已读, S1-S5 已完成
> - S3 表 C 给出最小组团清单 (组件级 FRAME)
> - memory 索引 (跨会话自动注入)
> - 旧组件库 JSON (用户提供, S1 前必须拿到)

---

## 这一步做什么

把 S3 输出的**每个最小组团**, 跟视觉模板库匹配, 打 pattern 命中标签 + Variant + 节点类型 + 包装类型 4 类标签:

1. **匹配 memory ui_pattern** (主) — 9 个通用 pattern + 1 使用通则 + 2 个项目先验, **memory 是教学参考不是铁律**
2. **匹配旧组件库** (辅) — 仅 100% 命中才用 `component_ref` (含三项预检)
3. **Variant 抽取** — 按 5 大原则 + 不做 Variant 的两类例外
4. **子 CCB 单元识别** — 4 步法判定每个最小组团的 S11 抽取意图 (是否被抽成 INSTANCE)
5. **包装类型综合判定** — 基于前 4 节产物, 决定外层包装 (按钮 / 组 / 进度条可点性 / 角标做法 B)

**这一步不做**:
- 写 JSON (S7)
- 把 pattern 模板套出来变成 JSON 节点 (S7)
- 把装饰挂进按钮 children (S7)
- 按命名白名单 (`按钮_xxx` / `底板_xxx`) 命名 (S7)
- 进度条建模铁律操作 (识别"是进度条"是 S6, 怎么建模是 S7)

---

## 输入

- S3 表 A (骨架) + 表 B (AL 对齐) + 表 C (组团结构)
- memory 索引 (自动注入, 含 9 个 ui_pattern + 1 使用通则 + 2 个项目先验)
- 旧组件库 JSON (S1 前用户提供; **如果未提供** → 跳过 #2, 走 memory + 手搓, 同时告知用户后续如有合适组件可补充)

---

## 输出: 表 H pattern + Variant + 节点类型 + 包装类型

```text
【pattern 命中清单】

组团 (S3 表 C 引用)         | pattern / 来源        | Variant 状态 (S11 用)  | 抽取意图 (S11 用)            | 包装类型 (S7 用)
---------------------------|---------------------|----------------------|----------------------------|----------------------
顶部 HUD / 生命栏           | memory 横排徽章       | (一般无 Variant)       | 子 CCB 单元 / 手搓           | 组_xxx (纯展示)
顶部 HUD / 设置按钮         | memory 单图标_无角标   | 常态 / 未激活          | 子 CCB 单元                  | 按钮_xxx (REDNodeButton)
顶部 HUD / 设置按钮 / 红点  | memory 角标_状态       | 显示 / 空 (含空)        | 子 CCB 单元                  | 角标依附按钮 children
进度条区 / 经验进度条       | memory 进度条_横向     | (不抽 Variant)         | 手搓双层 RECT (不抽 Component) | 组_xxx (用户答: 不可点)
列表 / 列表行 ×8           | (无 pattern)         | 常态 / 激活             | 大 CCB FRAME                 | 组_xxx (子元素各自处理)
底部导航 / 导航项 ×5        | 旧组件库 圆形按钮_导航 | 常态 / 激活             | component_ref (引用旧库)     | 按钮_xxx 做法 B 包装
活动入口 / 活动框           | memory 浮层_活动入口   | 单 Variant             | 子 CCB 单元                  | 浮层屏 layers[0] 遮罩
```

---

## 执行顺序 (5 节按以下流转)

```text
S3 表 C 最小组团 (输入)
    │
    ▼
┌──────────────────────────────────────────────┐
│  #1 memory pattern 命中   +   #2 旧组件库匹配   │ ← 并行匹配 (主参考 + 辅参考)
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│  #3 Variant 抽取          +   #4 子 CCB 识别    │ ← 基于命中, 抽状态 + 判节点类型
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│  #5 包装类型识别 (5.1 按钮 + 5.2 进度条 + 5.3 角标)         │ ← 3 个并列判定, 输出给 S7
└──────────────────────────────────────────────────────────┘
    │
    ▼
表 H 输出 (5 列: 组团 + pattern来源 + Variant + 节点类型 + 包装类型)
```

**关键触发关系**:
- #1 命中 memory `进度条_横向 / 多节点` → **必须触发 5.2 进度条独立判定** (主动问用户可点性)
- #1 / #2 命中按钮类 pattern → 进 5.1 按钮判定 (确认 + 5 步清单兜底)
- S3 已识别的角标 → 进 5.3 包装规则
- #4 Step D 识别出"父级高度类似但部分父级缺子集" → **必须**给该 CCB 加空 Variant

---

## 该步做的事

### 1. memory pattern 命中 (主)

> 🔴 **memory 的定位 — memory 是教学 / 参考, 不是铁律**
>
> - memory 提供 **"有可能出现的情况"** (典型形态 / 典型 Variant 模式 / 典型视觉结构)
> - **命中 memory ≠ 和 memory 完全一致** — 必须**以视频实际为准逐项检查**, 不一致以视频为准修正, 不强行套 pattern
> - **不命中 memory ≠ 不能这么做** — 只是这个组件不在 memory 沉淀的常见 pattern 里, Step A-D 满足就可以抽 CCB
>
> 简单说: memory 是"参考答案", 不是"标准答案"。视频实际形态永远优先。

> 🔴 **memory 例子的 JSON 形态注意 — 阶段一 vs 阶段二翻译**
>
> memory 9 个 ui_pattern.md + 1 使用通则的 JSON 例子里如果出现下列字段, **那是 S11 抽取之后的 v20.6 schema 形态, 不是你 S7 应该写的**:
>
> | memory 出现 | S7 阶段你要翻译成 |
> |---|---|
> | `type: INSTANCE` / `component_name` / `variant: xxx` / `overrides` | **扁平 FRAME** (每实例独立完整 children, 见 07d) |
> | `Variant = [常态, 激活, 空]` 的"空 Variant"教学 | **`visible: false`** (S11 自动识别为空 Variant) |
> | "按 SKILL 00d 原则 4" / "按 SKILL 04 规则 4.5" 等旧引用 | 见 新 skill: 角标包装 → 07c; 子 CCB 显隐 → 07d; Variant 抽取 → S11 |
>
> **简单说**: 你 S7 永远写扁平 FRAME, **不写** `type: INSTANCE`, **不写** `variant: 空`, 实例间差异直接写在每个 FRAME 内部, 隐藏用 `visible: false`。所有"INSTANCE / Variant"概念都是 S11 自动产物, 跟你 S7 无关。

> 🔴 **元铁律 — 上下文里有相似项目产物 = 风险信号, 不是捷径 (2026-05-18 Team Tournament 复盘)**
>
> 当上下文里已载入**某个相似项目的 scene.json / final_scene** (为复用结构而读入), 这是**高危信号**, 不是省力捷径:
> - ❌ **禁止 from-exemplar 改增量** — "这屏跟 X 项目 80% 像, 照搬结构改差异"。80% 像恰恰掩盖那 20% 不一样的(它没有的那块)
> - ✅ **必须逐组团从视频 + memory 重推** — S3 表 C 每个组团**独立**走 #1 memory 命中 + Step 3 Read pattern.md, 跟"那个项目怎么做的"无关
> - 相似样本只能在**字段写法 / 坐标体系**层面借鉴, **不能替代逐组团识别**
> - 教训: Team Tournament 中部多节点进度条被照搬 Team Battle(无此面板)结构 → 进度条本体整根丢失。详 memory `feedback_s6_pattern_must_scan_memory.md`

#### Step 1: 先按 `ui_pattern_使用通则` (元规则) 校准

**使用通则**是 memory 的**元规则**, 永远先看它:
- **以视频为准** — 实际形态优先, 不能按 pattern 强行套
- **任何 icon 都可能带角标** — 识别时关注右上 / 右下高频位置
- **同位置多内容 = 同 Comp 多 Variants 含空 frame**
- (其余具体内容: Read `memory/ui_pattern_使用通则.md`)

#### Step 2: 对照 9 个 ui_pattern + 2 个项目先验

| Pattern (memory 文件) | 典型视觉 | 一般 Variant 模式 |
|---|---|---|
| **横排徽章_左图右文** | 长胶囊底板 + 左 icon (上下溢出) + 右数字 | 一般**无 Variant** (数字数据驱动) |
| **角标_状态** | 主体边缘小角标 (位置 4 处固定: 右上/右下/左下/左上) | **同 Component 多 Variants, 含空 frame** |
| **单图标_无角标** | 独立 icon, 近正方形, 无附加 | 按钮型 (底板+icon) / 纯物品 (占位 RECT) 两类 |
| **进度条_横向** (单节点) | 长条 + 双层 RECT + X/Y 文本居中 | **不抽 Variant** (运行时切割) |
| **进度条_多节点** | 长条 + 节点沿条分布 (嵌入式/底标式/上标式 3 类) | 节点是 Comp 多 Variants (完成/待激活/未激活) |
| **浮层_活动入口** | 全屏弹窗: 顶 i+X + 中装饰 + 标题 + 倒计时 + 副标题 | 单 Variant 一般 |
| **icon 带底部文本** | icon 正下方挂文本 (丝带/圆角数字/按钮/纯文本 4 子形态) | 视具体子形态 |
| **按钮_纯文本** | 圆角矩形 + 文本 (1-2 行) 居中, 无 icon | **行数不抽 Variant** |
| **按钮_文本加icon** | 文本 + icon 按钮 | **icon 左/右是 layout 不是 Variant**; 真 Variant 在角标/底标多态 (含空 frame) |
| 项目先验: **金币堆** | 竖排带丝带 / 顶图标+中丝带+下数字嵌丝带 | 项目专属形态 |
| 项目先验: **盾牌等级** | 大盾牌外凸 + 右胶囊数字 | 项目专属形态 |

#### Step 3: 命中后 Read 对应 pattern.md → **以视频为准验证**

每个 pattern 文件有: 视觉特征精确描述 / 节点结构 / Variant 模式 / 反例。

Read 完后 **逐项对照视频实际形态** (不强行套 pattern):

| 对照结果 | 处理 |
|---|---|
| 完全一致 | ✅ 命中, 套 pattern 结构 |
| 部分一致 (主体一致, 细节有差异) | ✅ 命中, 标记差异部分, **以视频为准** |
| 形态相似但细节差异大 | ⚠️ 可命中, 标"参考 pattern, 实际以视频为准" |
| 实际跟 pattern 描述差异显著 | ❌ **不命中**, 标"手搓 / 可考虑沉淀新 pattern" |

S6 阶段**只识别命中 + 验证**, **节点结构 / Variant JSON 生成是 S7 的事**。

> ⛔ **禁止**: 看到 memory 提了某 pattern, 就**强行把视频里的组件按 pattern 结构套** — 视频实际形态优先于 memory 描述。

### 2. 旧组件库匹配 (辅, 仅 100% 命中)

旧组件库实际可用条目已不多, 仅**严格 100% 视觉匹配**时用 `component_ref`。

🔴 **强制铁律 (来自 旧 00a)**: **100% 匹配时, 必须使用 `component_ref`, 不得退化为手搓**。

- ✅ 视觉 100% 匹配旧组件库条目 → **强制** `component_ref` 引用 (走 S8 处理)
- ❌ 视觉 100% 匹配但"觉得手搓更简单"就退化为手搓 → 违规, 必须 `component_ref`
- ✅ 视觉**不是** 100% 匹配 (差异显著) → 不用 `component_ref`, 走 memory pattern 或手搓
- 边界情况 "看起来很像但不完全一致" → **主动问用户**, 不擅自决定 (#5 通用机制)

#### 匹配 4 维度 (旧 03 第五步识别顺序)

**一、看区域类型**
- 贴底全宽 + 均分 3~5 个图标/文字 → 导航栏 (走导航组件)
- 贴底全宽 + 2 个横排切换按钮 → 状态切换导航

**二、看整体形状**
- 椭圆头像区 + 底部时间条 → `椭圆按钮_活动`
- 正圆底板 + 单图标 → `圆形按钮_xxx`
- 圆角方形 + 消息气泡 → `方形按钮_消息_激活/禁用`

**三、看内部结构**
- 只有文字 → `矩形按钮_纯文本`
- 圆角矩形 + 时间 (无时钟图标) → `底标_时间`
- 圆角矩形 + 时间 (有时钟图标) → `底标_倒计时`
- ⚠️ **进度条不用 component_ref** (FRAME 包装与引擎不兼容) → S7 手搓双层 RECT

**四、看叠加附件**
- 右上角小圆 + "!" 或数字 → `角标_感叹号`
- 右上角矩形 + "×2" → `角标_倍数` (仅 ×N 格式; 普通数字角标手搓)
- 好友头像框 → `头像_朋友`

#### component_ref 三项预检 (S6 命中旧组件库后强制)

S6 标记某组团 = `component_ref xxx` 之前, 必须先对**整个组件库**做三项预检:

**预检 1: constraints 必须全是 SCALE/SCALE**

| 内部子元素 constraints | 缩放行为 | 处理 |
|---|---|---|
| `SCALE/SCALE` | ✅ 随 frame 等比拉伸 | 正常使用 |
| `LEFT/TOP` / `CENTER/CENTER` / 混合 | ❌ 内容错位 | ⛔ **停下让用户改组件库** |

执行: 读入组件库 JSON, 遍历每个组件子节点递归到最深, 统计 constraints 分布。任一组件内部不是 SCALE/SCALE → **立即停下**, 列出问题组件让用户改完再继续 S6。

⛔ **禁止"方案 A/B/C 凑活"混合方案** (不允许"用原始尺寸不缩放" / "强制缩放明知错位" / "部分手搓部分 ref")。

**预检 2: 组件库尺寸基准一致性**

组件库原始尺寸应该按 **1080×2400 设计稿比例**。若有明显小尺寸组件 (h < 50px 的按钮等), 说明组件库设计基准不是 1080×2400。

| 缩放比 | 处理 |
|---|---|
| < 2x | 正常使用, 按 v20 规则等比缩放 |
| **≥ 2x** | **停下问用户**: 组件库是按小尺寸设计的还是 1080×2400? |

典型值参考 (1080×2400 目标屏):
- 圆形按钮 (icon 级): 60–100 px
- 椭圆按钮_活动: 200–300 px
- 矩形按钮_纯文本: 120–200 px
- 角标 / 底标类: 40–80 px

⛔ **禁止绕过**: 不允许自己"强制缩放"而不确认。

**预检 3: 组件库内部禁止嵌套 `按钮_` 前缀** 🔴 (旧 00a 嵌套按钮冲突警告)

一个 `按钮_xxx` FRAME 内部**禁止再嵌套**另一个 `按钮_` 前缀的 FRAME — 通过 `component_ref` 间接嵌套也不行。否则引擎行为不可预测 (可能只识别外层 / 只识别内层 / 两层都触发冲突)。

执行: 读组件库 JSON, 对每个 `component_ref` 引用的组件做递归检查 → 任何 `按钮_xxx` FRAME 的 children 递归里再出现 `按钮_` 前缀 → ⛔ 停下让用户改组件库内部命名。

组件库内部子节点的**安全命名替代**:
- ✅ `活动按钮_xxx` / `按钮组_xxx` / `按钮_底板` (作为 key 名被引用, 不进入按钮识别路径)
- ❌ 纯 `按钮_xxx`

#### 导航栏双态组件特殊处理 🔴 (来自 旧 04 规则 9 + 旧 05 导航栏建模)

命中"导航栏"组件时, 必须按**双态**处理 (区分 选中 / 未选中):

##### 页面切换导航 (底部 Nav, **跨屏跳转**)

| Tab 状态 | component_ref | overrides | name |
|---|---|---|---|
| **当前页** (高亮) | `导航栏_页面切换_选中` | `{"内容_标签": "Home"}` | `导航_项N` |
| **其他 Tab** | `导航栏_页面切换_未选中` | `{"内容_标签": "Activities"}` (有角标时加 `{"数字_角标": "1"}`) | `导航_项N` |

##### 状态切换导航 (屏内 Tab, **不跨屏**)

| Tab 状态 | component_ref | overrides |
|---|---|---|
| **选中** | `导航栏_状态切换_选中` | `{"文本_Selected": "Weekly"}` |
| **未选中** | `导航栏_状态切换_未选中` | `{"文本_Selected": "Monthly"}` |

状态切换 Tab 若有附加元素 (倒计时底标等) → 用 **`按钮_xxx` FRAME 做法 B 包装** (S7 #10)。

##### S9 flow 跟它的关系

- **页面切换**: 写 flow 跳转到对应目标屏 (S9 #4 导航栏全量连线 N×(N-1) slide)
- **状态切换**: **不生成 flow** (屏内切换, 不跨屏)

### 3. Variant 抽取 (5 大原则 + 两类例外)

> **2026-05-15 措辞修正**:之前用"Variant 抽取最小化"易被误读为"ccb 嵌套层数也最小化"。**Variant 粒度最小化(差异下沉) ≠ ccb 嵌套层数最小化** — ccb 嵌套按 [06a_S6_ccb抽取标准.md](./06a_S6_ccb抽取标准.md)(待新建)决定,**不限制层数**。本节只管"Variant 在某个组件内部怎么抽得最小粒度"。

#### 5 大设计原则 (vs RoyalPass 教训, 来自旧 00d)

1. **变化下沉到最小单元** — 不在大容器 (网格行/奖励格/卡片) 上做"通用/对勾型/锁型..."排列组合 Variant。变化必须下沉到**最小可独立变化的视觉单元** (底板 / 角标 / 底标 / icon), 每个单元各自带独立 Variant。

2. **大组团不抽 Component, 只是 FRAME 包装** — 网格行 / 奖励格 / 中央组等中间结构层是 FRAME (S3 已组团化, 空 FRAME)。N 行各异通过**子 INSTANCE 各自引用不同 Variant** 表达, 不通过外层 Variant 排列组合表达。

3. **数据驱动 vs 状态多态分离** (S0 第 6.2 节核心哲学):
   - **数据驱动** (代码运行时填, 种类无穷) → 占位 RECT, **不做 Component / Variant**
   - **状态多态** (屏幕里枚举可数 2~10 种) → 做 Component + Variant

4. **"该状态不显示" 做空 Variant** (layers=[], 语义名"空"):
   - 角标这类 Component 加一个 `layers=[]` Variant, **名约定 `空`** (不带其他前缀后缀)
   - 设计师在 INSTANCE 选 "空" 即不显示
   - **不用 `visible=false`** 表达 (那是临时显隐; Variant 是状态切换)
   - 引擎实现细节 (空 Variant 仍生成 sequence 内部无 keyframe → 视觉空) 在引擎 SKILL

5. **运行时数值不进 Variant** — 进度条的"满/空"是引擎运行时按 percentage 切割, **不做 Variant**; 但进度条 **图标/状态指示器**的"已完成/未完成"是状态多态, **做 Variant**。区分: **数值连续 vs 状态离散**。

#### 不做 Variant 的两类例外

**例外 1: 奖励物图片** (道具/宝箱/任务奖励等"内容图")
- 屏幕里出现的种类多 + 需求频繁变 + 设计师无法穷尽枚举
- 做成占位 RECT, 程序运行时 `setSpriteFrame` 替换图片
- 占位 RECT 名字用 `图片_xxx` / `图标_xxx` 前缀

##### 🔴 Variants 数量阈值 (规则 5+6, 奖励物专属)

视频读到 **N 种同类语义**:

| N | 处理 |
|---|---|
| **N ≤ 5** | 抽 N Variants (枚举) |
| **N > 5** | 不抽枚举, 用 **1 个"占位 Variant"** 代表 (引擎程序换图) |

**同一 Component 内, 不同子类各自计数** (例: 奖励物):

| 子类语义 | 视频实例数 | 处理 | 结果 |
|---|---|---|---|
| 宝箱类 (紫/灰/蓝) | 3 种 ≤ 5 | 枚举 | 3 Variants |
| 道具类 (大炮/炸弹/TNT/桶/紫罐/爱心/龙卷风/蛋糕...) | 8+ 种 > 5 | 占位 | 1 Variant ("大炮" 代表道具大类) |
| **合计** | | | **4 Variants** |

##### 🌟 "枚举 + 占位混合 Variant" 模式 (奖励物专属)

同一 Component 内 **多个枚举 Variants + 1 个占位 Variant 混合**:
- 枚举 Variants: Figma 端设计师能看到具体视觉差异 (紫箱/灰箱/蓝箱不同 icon)
- 占位 Variant: 引擎运行时根据数据换实际 icon + (可能) 文本

INSTANCE 引用时:
- 视频里看到的"紫箱"节点 → INSTANCE.variant = "紫箱"
- 视频里看到的"爱心 / 桶 / TNT"等节点 → INSTANCE.variant = "大炮" (占位代表), 引擎数据换图

⚠️ **这种"枚举+占位混合 Variant"模式 极度适用于奖励物**, 其他多态 (角标/底板/进度条 icon)
   通常各 Variant 结构一致, 单纯枚举即可, 不需要这种复杂判断。

**例外 2: 进度条本体** (进度条 RECT 的"当前填充百分比")
- 视觉永远画 **100% 满模板** (S7 进度条铁律)
- 引擎运行时按 percentage 切割 (CCProgressTimer)
- **不做 "50%/80%" 这种 Variant**, **不做 "已完成/未完成" 这种 Variant**
- 但进度条**图标/状态指示器**的"已完成/未完成"是状态多态, 做 Variant

🔴 **进度条本体 vs 进度条 icon — 严格区分铁律**

下面这张表必须背熟, 别再搞反:

| 类型 | 例子 | 抽 Component? | 抽 Variant? | 实现方式 |
|---|---|---|---|---|
| **进度条本体 (横向)** | key 进度条 / 体力进度条 / 经验进度条 (整条) | 通常不抽 (单实例) | ❌ 不做 | `底板_xxx` + `进度条_xxx` 双层 RECT, 引擎 CCProgressTimer |
| **进度条本体 (纵向多段)** | 节点之间的纵向短进度段 (例: RoyalPass 节点间连接段) | ❌ 不抽 | ❌ 不做 | 同上 (`底板_短进度` + `进度条_短进度`), 引擎切割每段 |
| **进度条 icon / 里程碑节点** | 节点六边形 (沿条分布的里程碑) / 进度条端点装饰 icon | ✅ 抽 (跨多实例) | ✅ 多 Variants (已完成 / 未完成 / 当前 / ...) | 子节点 visible 切换 / corner_radius 微差 (07d #3 方法 A/C) |
| **进度条数值文本** | "39/40" / "x/y" 中央覆盖文字 | ❌ 不抽 | ❌ 不做 (dynamic) | TEXT.content 直接写, S11 自动 INSTANCE.overrides |
| **进度条左/右奖励 icon** | 进度条左端 key 图 / 右端 chest 图 | 看是否跨多实例 (单实例不抽) | 看是否枚举可数 | 跟普通 icon 一样 |

#### 常见错误 (我踩过的)

| ❌ 错 | ✅ 对 |
|---|---|
| 把"短进度段"抽成 Component, 做 "已完成/未完成" 2 Variants | 短进度段也是进度条本体, **不抽**, 引擎按每段数据切割 |
| 把"进度条本体"抽 Component 做 Variant | 整条进度条是本体, 引擎处理, **不抽** |
| 把"节点六边形"当装饰不抽 Variant | 节点六边形是进度条 **icon (里程碑)**, 抽 + 多 Variants |

#### 区分关键

"进度条 icon" 不是"进度条本体的一部分", 是**沿着进度条分布的独立 icon 单元** (里程碑/节点/状态指示器), 各自有独立 Component。 节点之间的连接段 (纵向短进度) 是**进度条本体**, 引擎渲染。

#### 边界场景决策流程图

```text
这个视觉变化点:
├── 大容器 (行/卡/格 包装层) 还是最小单元 (底板/角标/icon)?
│   ├── 大容器 → 不抽 Component, FRAME 包装层。变化下沉到子单元
│   └── 最小单元 ↓
│
├── 屏幕里这个单元枚举可数 (2~10 种) 吗?
│   ├── 是 → 做 Component + Variant
│   │       ├── 状态包含"不显示" → 加空 Variant (layers=[], 名"空")
│   │       └── 各 Variant 视觉签名必须唯一 (否则 combineAsVariants 失败 → S11 修复)
│   └── 否 ↓
│
└── 数值连续 (满/空、百分比) 还是种类无穷 (图片资源)?
    ├── 数值连续 → 引擎运行时计算 (CCProgressTimer 等)
    └── 种类无穷 → 占位 RECT, 程序运行时填图
```

#### 反面案例 (踩过的坑)

| 错例 | 错在哪 | 正确做法 |
|---|---|---|
| 网格行_等级 = 通用 / 宝箱型 / 对勾型 / 对勾锁型 4 Variant | 排列组合, 违反原则 1+2 | 网格行只 1-2 真实视觉差异 Variant (常态/当前用户高亮), 每行的对勾/锁/数量差异通过内部子 INSTANCE 各自引用对应 Variant 表达 |
| 奖励物做了 7 个 Variant 列举所有道具 | 违反原则 3 + 例外 1 (种类无穷) | 占位 `图片_奖励物` RECT, 程序 setSpriteFrame |
| 1 Variant Component 被删降级 FRAME | 擅自改用户原始设计意图 | 加 dummy 第 2 Variant 制造视觉差异 (fill / corner_radius) — Component 修复铁律在 S11 |

### 4. 子 CCB 单元识别 🔴 (S11 抽取意图, 不是给 S7 直接生成 INSTANCE)

> 🔴 **关键 — Claude 阶段一不直接生成 INSTANCE 节点**
>
> S0 第 13 节嵌套 CCB 三层模型 (**大 CCB / 子 CCB INSTANCE / 占位 RECT**) 是 **S11 `extract_components.py` 抽取后的 v20.6 schema 形态**, **不是 S7 直接写的**。
>
> Claude 阶段一 (S7-S9) 输出**扁平 scene.json** — 8 个列表行就写 8 个独立完整的 FRAME, **没有 INSTANCE 节点**, **没有 components[] 数组**。S11 自动扫 structural_fingerprint 抽 Component + 生成 INSTANCE + 提取 overrides。

S6 在这步**标记每个最小组团的"S11 抽取意图"** (给 S11 的提示, 不是给 S7 生成 INSTANCE):

| S6 标记 (抽取意图) | S7 输出形态 (扁平 scene.json) | S11 抽取后 (v20.6 schema) |
|---|---|---|
| **子 CCB 单元** | `type: FRAME` 扁平 (每实例独立完整 children, 隐藏用 `visible: false`) | 抽成 Component + N 个 INSTANCE 引用 (overrides 自动提取) |
| **占位 RECT** (数据驱动) | `type: RECTANGLE` + 命名 `图片_xxx` / `图标_xxx` | 不抽 Component (保持占位 RECT) |
| **component_ref** (命中旧库) | `component_ref` 字段引用 (S7 直接写, S8 校准缩放) | 保持 `component_ref` (引用旧库) |
| **手搓节点** | `type: FRAME/RECT/TEXT` 按操作铁律手搓 | 不抽 Component (保持原结构) |
| **大 CCB FRAME** (S3 组团化的包装层) | `type: FRAME` 扁平 (空 FRAME 包装) | 抽成 Component, 内含子 INSTANCE 引用 |

#### 🔴 抽取层级三层区分 (Step A 前必先分层)

**对齐旧 skill `03_skeleton` 表 B**: Component 抽取**必须按层级筛选**, 不是所有跨多实例的 FRAME 都抽。

| 层级 | 例子 | S11 是否抽 Component? | 在 S7 阶段以什么形态出现 |
|---|---|---|---|
| **大组团** (跨整屏复用的最大单元) | 节点行 / 列表项 / 卡片 / 网格行 | ❌ **默认不抽** (用户特别要求才抽) | `组_xxx` 扁平 FRAME |
| **中间组团** (大组团内的组织 FRAME) | 组_左奖励 / 组_右奖励 / 组_节点列 / 组_顶部 HUD | ❌ **绝对不抽** (S3 组团化的包装层, FRAME 透明) | `组_xxx` 扁平 FRAME |
| **最小单元** (不可再拆的视觉单元) | 底板 / 角标 / 底标 / 进度条 icon / 单 icon | ✅ **抽 Component** (Step A-D 走完) | 单独 `组_xxx` FRAME 包装 (见 07d 最小单元 FRAME 包装铁律) |
| **数据驱动占位** (旧 00d 例外 1/2) | 奖励物图片 / 进度条本体 RECT | ❌ 不抽, 占位 RECT 数据换图 | `图片_xxx` / `图标_xxx` / `进度条_xxx` |

**判定优先级 (从上往下走)**:
1. 这个 FRAME 是不是**大组团** (跨整屏的列表行 / 卡片)? → 默认不抽, 跳过 Step A-D
2. 是不是**中间组团** (S3 组团化的纯包装 FRAME, 内含多个并列子单元)? → 绝对不抽, 跳过 Step A-D
3. 是不是**数据驱动占位** (奖励物图片 / 进度条本体)? → 占位 RECT, 不抽
4. 否则 → 进入 4 步法 (Step A-D) 判定是不是子 CCB 单元

⚠️ **关键提醒**: `extract_components.py` 脚本**默认会抽**所有跨多实例同结构 FRAME, **包括中间组团**。 必须在 **S11 后处理时手动删除中间组团 Component** (见 `11_S11_抽取导出.md` "中间组团后处理删除")。

#### 区分大组团 vs 中间组团 vs 最小单元的具体方法

| 看几个特征 | 大组团 | 中间组团 | 最小单元 |
|---|---|---|---|
| 子节点数 | 通常 3-10 (含多个最小单元 + 装饰) | 通常 2-5 (并列子单元) | 通常 1-3 (单 RECT/TEXT 底板 + 装饰) |
| 视觉职能 | 一行/一卡的整体 | 一行内的"左半部分"等子区 | 单个可独立变化的视觉块 |
| 在视频里复用 | 跨整屏 ×N (例: 8 行) | 跨大组团 ×2 (例: 左/右奖励) | 跨多个组团 (例: 16 个角标 = 8 行 × 2 侧) |
| FRAME children 内容 | 多个中间组团 + 装饰 | 多个最小单元 + 装饰 | 装饰底板 + (可选) 子节点切换 |
| 抽 Component? | 默认不抽 | 绝对不抽 | 抽 |

**例子: RoyalPass 风格屏幕**
```
界面_RoyalPass
└── 滚动列表
    └── 节点行 ×8  (大组团 — 不抽)
        ├── 组_左奖励  (中间组团 — 不抽)
        │   ├── 组_奖励卡底板  ← 最小单元 (抽! 2 Variants: 常态/待激活)
        │   ├── 图片_奖励      ← 数据驱动占位 (不抽)
        │   ├── 文本_数量      ← TEXT (不抽, dynamic)
        │   └── 角标_状态      ← 最小单元 (抽! 3 Variants: 锁/对勾/空)
        ├── 组_节点列  (中间组团 — 不抽)
        │   ├── 组_短进度_上   ← 最小单元 (抽! 2 Variants: 已完成/未完成)
        │   ├── 组_节点六边形  ← 最小单元 (抽)
        │   └── 组_短进度_下   ← 最小单元 (抽, 跟上同 Component)
        └── 组_右奖励  (中间组团 — 不抽, 跟左奖励同结构)
```

抽出 Component 数 = **4 个最小单元 Component** (不含大组团/中间组团)。

---

#### 判定的核心逻辑 (4 步, 按顺序走)

**Step A: 多处复用判定** (核心入口)

这个元素在页面内有**多个类似内容 / 位置的复用**吗 (跨多个父级 / 或在同一父级里多次出现)?

| 答 | 结论 |
|---|---|
| ✅ 有多个类似复用 | → 标记为**子 CCB 单元** (S11 抽成 INSTANCE), 继续 Step B |
| ❌ 只出现一次 | → **不抽 CCB**, 走手搓 / 占位 RECT / 普通节点 |

**Step B: 抽到最小变化粒度** 🔴 (旧 00d 原则 1)

CCB 抽取必须**下沉到最小变化单元**:

- ❌ 不在大组团 (网格行 / 卡片 / 格) 上抽 CCB — 大组团是 FRAME 包装, 不是 Component
- ✅ 拆到**最小可独立变化的单元** (底板 / 角标 / 底标 / icon) 抽 CCB
- 例: `列表项_排名` 不抽 CCB (是 FRAME 包装层, S3 组团化的大 CCB FRAME), 但内部的 `角标_王冠` / `排名圆` 抽 CCB

**Step C: 把所有样子抽成同一 Component 的多个 Variant**

同一最小单元在页面里出现的**不同视觉状态** → **同一 Component 的多个 Variant** (**不是**多个独立 Component):

- 例: 角标在不同行表现为 王冠 / 对勾 / 锁 / (空, 没显示) → `角标_xxx` Component, 4 个 Variant
- 例: 按钮在不同处表现为 常态 / 激活 → `按钮_xxx` Component, 2 个 Variant

**Step D: 空 Variant 判定** 🔴 (旧 00d 原则 4 + 旧 00c 子 CCB 显隐铁律)

检查 CCB 的父级 (大 CCB):

- **父级内容高度类似** (多个父级结构基本一致, 例: 8 行列表行都是 "头像 + 名字 + 分数 + (可选) 角标")
- 但**部分父级里没有这个 CCB 的某个子集** (有的行有"角标_王冠", 有的行没有)
- → S7 阶段每个父级都写完整 children, **缺失子集的父级用 `visible: false`** 标记该 CCB
- → S11 抽取时, 这些 `visible=false` 的实例自动归为"空 Variant" (`layers=[]`, 名约定 `空`), v20.6 schema 里设计师看到的 INSTANCE 状态名为"空"

⚠️ **S7 阶段只用 `visible: false` 表达隐藏**, **不写** `variant: "空"` 字段 — variant 是 v20.6 schema (S11 抽取后) 才有的命名。S7 阶段没有 INSTANCE 节点也没有 variant 字段。

##### 🔴 子 CCB 显隐铁律: 禁止用增删 children 表达显隐 (旧 00c)

❌ **错误**: 父级 row 5 children 数组里加 `角标_王冠` FRAME (含完整 children), row 6 直接不放 (children 数组不含此 FRAME)
- 后果: row 5 / row 6 的 structural_fingerprint 不一致 → S11 `extract_components` 无法抽出统一 `列表项` Component → 整个 Component 抽取链失败

✅ **正确**: 所有父级 row 的 children 数组**结构一致**, 都包含完整的 `角标_王冠` FRAME (含 children), 需要隐藏的**统一用 `visible: false`** (S7 阶段表达)
- 8 行 structural_fingerprint 一致 → S11 抽出统一 `列表项_排名` Component
- visual_signature 因 `visible` 差异 → S11 自动分成多 Variant (含"空 Variant")
- 实例间数据差异 (TEXT.content / 图片) → S11 自动提取到 `INSTANCE.overrides`

> 这条是 CCB 抽取的**最常见踩坑点** — 设计师/Claude 容易"行 6 不需要角标就直接不放角标", 后果是整个 Component 抽不出来。S6 必须在 Step D 标记好"**哪些扁平 FRAME 实例在该父级用 `visible: false` 隐藏**", 而不是用增删 children。S11 抽取后, 这些 visible=false 的实例自动归为"空 Variant"。

#### memory pattern 的辅助作用 (不是判定依据)

memory 9 个 ui_pattern + 1 使用通则 + 2 个项目先验是**辅助识别工具**, 帮你**快速识别这种视觉是常见的可复用形态**, **不是 CCB 抽取的判定依据**。

最终判定还是看 **Step A 多处复用 + Step B 最小粒度 + Step C/D Variant 抽取**。

memory pattern 的作用:
- 提供**典型 Variant 模式参考** (如 `角标_状态` 提示通常有"显示 / 空"两类)
- 提供**典型视觉结构参考** (如 `进度条_横向` 的双层 RECT 结构)
- **不命中 memory 不代表"不是 CCB"** — Step A-D 满足就抽 CCB

#### 不是子 CCB 单元的 (不抽 Component)

- **占位 RECT** (奖励物图片 / 头像 — 数据驱动): 命中 memory `单图标_无角标 (纯物品)` 子形态 / 旧 00d 例外 1
- **单纯文本** (玩家名 / 数字 — 数据驱动, S11 抽取后变成 overrides)
- **手搓节点** (只出现一次的元素, 不复用 — Step A 不通过)
- **进度条本体 RECT** (引擎运行时切割 — 旧 00d 例外 2)

#### 进度条节点的抽取意图 (单节点 vs 多节点 不同)

| 进度条类型 | S7 输出形态 | S11 抽取意图 |
|---|---|---|
| **单节点进度条** (memory `进度条_横向`) | 手搓双层 RECT (`底板_xxx` + `进度条_xxx`) 扁平 | **不抽 Component**, 引擎运行时切割 |
| **多节点进度条 节点** (memory `进度条_多节点` 的节点, 完成/待激活/未激活) | 多个完整 FRAME 扁平 (每节点独立完整 children) | 抽成 Component + 多 Variant + N 个 INSTANCE 引用 |
| **多节点进度条 外层组装** (FRAME 包装 + 长条贯穿) | 手搓 FRAME (大 CCB 包装层) 扁平 | 抽成 Component (大 CCB), 内含子 INSTANCE |

**通用**: 进度条**本体 RECT** (底板 + 进度条填充) 永远是手搓双层 RECT — 引擎运行时切割, **不抽 Component**。

---

#### 🔴 内部含 INSTANCE 的 FRAME 本身不抽 Variant (规则 7)

如果一个 FRAME 内部已经含**多个子 INSTANCE** (各自带 Variant), 这个 FRAME **本身不抽 Variant** — 因为外层视觉变化已经被内部子 INSTANCE 的 Variants 表达, 再抽外层 Variant **= 排列组合, 引擎枚举无意义**。

**例**: 节点行 FRAME 内含:
```
节点行_N FRAME (大组团, 扁平):
├── 紫色行底板 RECT
├── 奖励物 INSTANCE (variant: 紫箱/灰箱/...)
├── 角标_状态 INSTANCE (variant: 锁/对勾/空)
├── 底板_奖励卡 INSTANCE (variant: 常态/待激活)
└── 节点六边形 INSTANCE (variant: 已完成/未完成)
```

节点行 FRAME **保持扁平, 不进 components[] 数组**。 8 行视觉差异已经被内部 4 个 INSTANCE 的 Variant 字段表达 (每行 INSTANCE.variant 不同)。

如果硬要抽节点行 Variants:
- 8 行 × (4 INSTANCE 各自 2-3 Variant) = 排列组合数十种 Variant
- 引擎枚举这么多 Variant 没意义 (设计意图就是内部独立切换, 不是外层切换)

### 5. 包装类型识别 (3 个并列判定)

> 这一节是 S6 的**输出层** — 给每个组团打"外层包装类型"标签, 留给 S7 决定具体命名前缀。
>
> 🔴 **通用机制 — 不确定时主动问用户, 不猜测**
>
> 5.1 / 5.2 / 5.3 三个判定**任何一处不确定**, 都必须**主动问用户**, 禁止自己猜:
> - 5.1 按钮判定: 5 步清单走完仍不能判定按钮 vs 装饰 → 问用户
> - 5.2 进度条: 直接默认问用户 (语义不明显)
> - 5.3 角标: 父本归属不明 (依附 A 还是 B 的按钮) → 问用户
>
> ---
>
> **S6 / S7 的命名分工**:
> - **S6 输出包装类型标签** (按钮 / 组 / 进度条可点性 / 角标做法 B) → 暗示 S7 用什么前缀 (`按钮_` / `组_` / `底板_` / `进度条_`)
> - **S7 写具体命名** — `按钮_活动紫罐` / `底板_活动紫罐` / `进度条_经验` 等, 按命名白名单和进度条建模铁律
> - **引擎按命名识别** — `按钮_xxx` FRAME → REDNodeButton, `进度条_xxx` RECT → CCProgressTimer 填充层。S7 命名正确, 引擎识别就对
>
> 大部分情况, #1-#4 已隐含给出包装类型:
> - 命中 memory `按钮_*` pattern / 旧组件库按钮类 → 按钮
> - 命中 memory `角标_状态` / `单图标 (纯物品)` → 非按钮装饰
> - 命中 memory `进度条_*` → 走进度条专项判定 (5.2)
>
> 不确定时, 走 5.1 的 5 步清单 fallback。

#### 5.1 按钮独立判定 🔴 (输出: `按钮_xxx` / 非按钮)

##### 5 步清单 (fallback, 仅当 #1-#4 不能下结论时用)

对每个 S2 #5 标记的"按钮边界候选" + 命中 memory 的"看起来像按钮的 pattern", 走 5 步清单做最终判定:

```text
□ 有独立视觉边界 (底板 / 描边 / 色块对比)?
    └ 无 → 不是按钮, 是装饰 / 显示
    └ 有 ↓

□ 是规则形状 (矩形 / 圆 / 胶囊 / 圆角方)?
    └ 否 (自由形状 / 场景图 / 大插图) → 装饰图, 不是按钮
    └ 是 ↓

□ 和相邻元素紧贴? (间距 < 元素自身宽度)
    └ 紧贴 → 与相邻元素**合并为一个**按钮 (HUD 资源栏 / 进度条整条 / 活动按钮)
    └ 独立 ↓

□ 在导航栏里?
    └ 是 → **每项独立按钮** (反例规则)
    └ 否 ↓

□ 有可操作语义? (Claim / Start / Action / Level xxx / 数字+号 / OPEN 等)
    └ 有 → **按钮**
    └ 纯显示 (单纯数字 / 图标 / 标题文字) → 不是按钮
```

##### 合并 vs 独立判断示例

| 场景 | 处理 | 示例 |
|---|---|---|
| HUD 资源栏 (金币图标+数字+加号紧贴) | **整栏合并为 1 个按钮** | 按钮_金币栏 (含 图标_金币 + 文本_860 + 角标_加) |
| HUD 心栏 (心+数字+加号+倒计时) | **整栏合并为 1 个按钮** | 按钮_心栏 (含 心图标 + 4 + 加 + 22:00) |
| 大进度条 (胶囊+文字+倍数角标+倒计时) | **整条合并为 1 个按钮** | 按钮_活动进度 (含 小火车 + 873/1000 + ×2 + 22:43) |
| 地图活动按钮 (椭圆+角标+底标) | **一个大按钮** | 按钮_活动紫罐 (含主体 + 角标 + 倒计时) |
| 导航栏 5 个 Tab | **每个独立按钮** (反例) | 导航_项1 / 导航_项2 / ... |
| Stage 1-5 Tab | **每个独立按钮** (反例) | 按钮_Tab_Stage1 / 按钮_Tab_Stage2 / ... |

##### 合并 vs 独立的本质

- **紧贴元素组合 = 合并为 1 个按钮** (HUD 资源栏 / 进度条 / 活动按钮)
- **平行排列的同类切换项 = 每个独立** (导航栏 / Tab 栏 / 页签)

**识别方法**: 这一组元素**语义上是一体的** ("我要充金币就点金币栏整条") → 合并; **每项有独立语义** ("我要切到 Weekly Tab") → 独立。

**遇到不确定的按钮边界, 主动问用户, 不猜测**。

#### 5.2 进度条独立判定 🔴 — 主动问用户 (输出: `组_xxx` / `按钮_xxx` 外层 + 三层命名信号)

进度条**跟按钮判定独立, 不走 5.1 的 5 步清单** — 进度条语义不明显 (单独看视觉不能判断是不是可点), 5 步会误判。

遇到进度条时, **必须主动问用户**:

> 这个进度条整条可点吗?

| 用户回答 | 外层包装 (S7 用) | 三层命名 (S7 用) |
|---|---|---|
| ✅ 整条可点 (跳到活动详情等) | `按钮_xxx` FRAME (REDNodeButton) | `按钮_活动进度` 外层 + `组_进度_活动` + `底板_活动` + `进度条_活动` |
| ❌ 纯展示 (HP 条 / 经验条 / 关卡进度) | `组_xxx` FRAME (CCNode 容器) | `组_xxx` 外层 + `组_进度_经验` + `底板_经验` + `进度条_经验` |

**S6 输出的包装类型标签 → 引擎按命名识别**:
- 外层 `按钮_xxx` FRAME → REDNodeButton (引擎做触控)
- 填充层 `进度条_xxx` RECT → CCProgressTimer (引擎做按 percentage 切割)
- 底板 `底板_xxx` RECT → CCSprite (引擎做底板渲染)

⛔ **禁止**: 看到进度条就默认是按钮 (或默认是组) — **必须问**, 不能猜。

具体的三层命名结构(组_进度_XXX + 底板_XXX + 进度条_XXX,XXX 一致,"进度"二字只在外层) → S7 进度条建模铁律操作。

#### 5.3 角标包装规则 🔴 — 做法 B (输出: 角标的父本类型, 跟 S3 衔接)

S3 #2 已识别"角标依附哪个主元素 → 主元素所在的组件 FRAME"。S6 这一步进一步识别**包装规则做法 B**:

| 父本类型 (S6 5.1 综合判定后已知) | 包装规则 (留给 S7 执行) |
|---|---|
| **手搓按钮** (5.1 判定 = 按钮, 没命中 component_ref) | 角标作为该按钮 FRAME 的 children |
| **component_ref** (5.1 判定 = 按钮 + 命中旧组件库的按钮组件) | **外层包一个 `按钮_xxx` FRAME**, 把 component_ref + 角标都作为该 FRAME 的 children (**做法 B**) |
| **非按钮 (纯展示)** | 角标作为父组件 FRAME 的 children (跟主元素同级, S3 已识别) |

S6 阶段只**识别**用哪种包装规则, **不写 JSON / 不挂 children** — 那是 S7。

---

### 6. S7 落地预演 🔴 (输出表 H 前必走的一步)

表 H 输出前, 对每个**抽 Component 的最小单元**, 必须**预演 S7 阶段视觉差异**怎么落地。否则 S7 阶段会写出 "N Variants 视觉签名相同" 的形态, S11 抽不出 N Variants → combineAsVariants 失败 → Figma 看不到 Variants 切换。

### 预演表 (每个抽 Component 的最小单元都填)

```
Component | S6 期望 Variants 数 | S7 children 设计 (视觉差异表达方法)
----------|---------------------|--------------------------------------
角标_状态  | 3 (锁/对勾/空)      | children: [底板_角标, 图标_锁, 图标_对勾]
                                 跨实例 visible 切换:
                                 - 锁: 图标_锁 visible:true, 图标_对勾 visible:false
                                 - 对勾: 图标_锁 visible:false, 图标_对勾 visible:true
                                 - 空: wrapper visible:false
                                 → S11 切 3 Variants ✓
奖励卡底板 | 2 (常态/待激活)     | children: [底板_奖励卡 RECT (corner_radius=30 常态 / 31 待激活)]
                                 跨实例 corner_radius 微差
                                 → S11 切 2 Variants ✓
短进度条   | 2 (已完成/未完成)   | children: [底板_短进度, 进度条_短进度]
                                 跨实例 进度条_短进度 visible 切换:
                                 - 已完成: 进度条_短进度 visible:true → Variant.layers=[底板, 进度条]
                                 - 未完成: 进度条_短进度 visible:false → Variant.layers=[底板] (过滤后)
                                 → S11 切 2 Variants ✓
节点六边形 | 1 (单态)            | children: [底板_六边形, 文本_节点号]
                                 单 Variant, S11 自动 dummy 凑 ≥2 (见 11_S11)
                                 → S11 切 1 Variant + 1 dummy ✓
奖励物    | 4 (3 宝箱枚举 + 1 道具占位) | 🔴 **Variant 内部异构** (规则 4, 07d #2.5):
                                 - 紫/灰/蓝箱 Variants: [图片_奖励 RECT] (单 icon)
                                 - 大炮 Variant: [组_奖励单元 FRAME 含 [icon + dynamic TEXT]]
                                 视频里宝箱实例: 紫箱 2, 灰箱 1, 蓝箱 1 (≤5 → 枚举)
                                 视频里道具实例 8+ (>5 → "大炮"占位 Variant 代表)
                                 → S11 用主路径 (Claude 直接构造 final_scene.json,
                                   不调脚本, 见 11_S11 主路径) ✓
```

### 4 种视觉差异表达方法 (映射到 07d #3)

| Variant 数 | 跨实例视觉如何区分 | 表达方法 |
|---|---|---|
| 2: 显示 vs 不显示 | wrapper 整体显隐 | wrapper visible:true/false |
| 2: 同结构不同视觉 (常态 vs 高亮) | 子节点 fill / corner_radius / opacity 微差 | 微差表达 |
| ≥3: 同位置不同内容 (锁/对勾/数字) | 多个子节点 visible 切换 | 子节点 visible 切换 + (可选) wrapper visible 空 |
| 1: 单态 (节点六边形) | 无差异 | S11 自动加 dummy (S7 不需操作) |

### 违规信号 (S6 表 H 输出前必查)

| ❌ 表 H 写法 | 问题 |
|---|---|
| 某 Component 期望 3 Variants, 但 S7 落地表只写"用 wrapper visible 切换" | 只能切 2 Variants (显示 vs 不显示), 缺第 3 个 |
| 某 Component 期望 N Variants, S7 落地未填 | S6 抢跑 S11 后才发现没视觉差异 |
| 落地方法依赖 `fill: "#xxx"` | 违反 S7a #3 (手搓 fill 省略) |
| 落地方法依赖增删 children | 违反规则 11.5 (S11 抽不出 Component) |

### 跟 S7 / S11 的衔接

- S6 这一节预演 → **写进表 H 备注列**
- S7 阶段按此预演逐字段写 children (见 07d #3)
- S11 抽取后 → 验证 Variants 数 = 预演 N 数, 否则回 S6 修

---

## 该步绝对不做的事

| ❌ 越界 | 这是哪一步的事 |
|---|---|
| 写 JSON 任何字段 | S7-S9 |
| 把 pattern 模板套出来变成 JSON 节点结构 | S7 (套 pattern 模板生成骨架) |
| 给组件按命名白名单 (`按钮_xxx` / `底板_xxx`) 命名 | S7 |
| 挂 children (角标 → 按钮 children 内) | S7 |
| 写进度条 双层 RECT 内缩量 / 中心对齐 / 方向后缀 | S7 |
| 自检 / 验证 JSON 字段 | S10 |
| 抽 Component / 调用 extract_components | S11 |
| 修复 Component (combineAsVariants 失败) | S11 |

---

## 违规信号

| 出现的行为 | 说明 |
|---|---|
| 表 H 出现 `按钮_紫罐` / `底板_活动` 这种白名单命名 | 抢跑 S7; 表 H 用 pattern 名 + 描述性标签 |
| **S6 自己写 memory 文件 / 修改 memory pattern 内容** | 越界; S6 可以**标记建议**"建议沉淀新 pattern" (Step 3), 但**是否真的写 memory** 由用户决策 |
| 写 component_ref 但没做三项预检 | 违反 #2 预检铁律, 立即停下 |
| **看到 1 Variant Component 就标"删了降级 FRAME"** | 违反 Component 修复元铁律; **删 Component 必须先问用户** (Component 列表是用户的设计决策), 优先加 dummy 第 2 Variant |
| 网格行/卡片 抽了"通用/对勾型/锁型"排列组合 Variant | 违反原则 1 + 2, 变化下沉到子 INSTANCE |
| 进度条本体抽了 "50%/80%" Variant | 违反例外 2, 视觉画 100% 满, 引擎切割 |
| 奖励物抽了多个 Variant 列举 | 违反例外 1, 用占位 RECT |
| 自己造个新 Variant 加进 Component | 越界, S6 只**识别**状态, 不创造 |
| 命中旧组件库的视觉**不是 100% 一致** | 不能用 component_ref; 改命中 memory pattern 或手搓 |
| 看到进度条就默认是按钮 / 组, 没主动问用户 | 违反 5.2 |
| 不同扁平 FRAME 实例用增删 children 表达显隐 (row 6 不放角标 FRAME) | 违反 #4 Step D 子 CCB 显隐铁律, S11 抽不出统一 Component |

---

## 验证 (S6 输出前必过)

1. **覆盖率**: S3 表 C 里**每个**最小组团, 表 H 都有对应行 (pattern / 组件库 / 手搓 / 无 Variant 都标清楚)
2. **memory pattern 命中必 Read**: 命中的 pattern 在 memory 里真实存在; **命中即 Read 对应 pattern.md** 逐项对照视频 (**不是"必要时"**), 表 H + `s6_coverage.json` 注明 Read 凭证 (文件名)
3. **三项预检通过**: 用 component_ref 的, 组件库 constraints + 尺寸基准 + 嵌套按钮 三项预检都通过 (否则停下让用户改)
4. **Variant 抽取符合 5 原则 + 例外**: 没有大组团排列组合 / 没有数据驱动做 Variant / 没有运行时数值做 Variant / 不显示用空 Variant
5. **子 CCB 显隐合规**: 所有同形态父级的 children 结构一致, 没有用增删 children 表达显隐
6. **进度条主动问过用户**: 凡是进度条都明确了"可点 / 不可点" 包装类型
7. **S6 覆盖闸门通过** 🔴: `s6_coverage.json` 已产出, gate 脚本退出码 0 (每组团一行 / 命中带 Read 凭证 / S3 表 C 无遗漏) — 见下方"S6 强制覆盖闸门"

---

## 🔴 S6 强制覆盖闸门 (forcing function — 杜绝静默跳步, 2026-05-18 新增)

> 根因: S6 此前只有散文自述 ("memory pattern 真实存在 ✓"), 没有机器可校验产物 → 在"相似样本在场 + 自主连跑"下被类比替代, 静默漏匹配 (Team Tournament 进度条事故)。
> 对策: S6 必须额外产出**结构化覆盖产物**, 跑 gate 脚本, ❌ 不得进 S7 (跟 S10/S11 的 python 自检**同级强制**)。

### 必产物: `s6_coverage.json` (跟 scene.json 同目录) + `s3_groups.txt` (S3 表 C 组团名, 空白分隔)

S3 表 C 每个组团**一行**, 无遗漏:

```json
{
  "groupings": [
    {
      "group": "组_奖励进度面板",
      "scanned_A_table": true,
      "pattern_hit": "ui_pattern_进度条_多节点",
      "read_evidence": "ui_pattern_进度条_多节点.md",
      "subclass_or_note": "上标式C类(+横排徽章)",
      "conclusion": "组_进度_奖励三层+4节点占位+4横排徽章标签"
    }
  ]
}
```

字段约定:
- `group`: 必来自 S3 表 C
- `scanned_A_table`: 是否逐项过了 SKILL 路由 A 表 12 视觉特征 (true/false)
- `pattern_hit`: 命中的 memory pattern 名; 无命中写 `无(手搓)` 或 `component_ref:xxx`
- `read_evidence`: 命中 ui_pattern 则**必填实际 Read 的 memory 文件名**; 未命中写 `""`
- `subclass_or_note`: 命中子类 / 差异点 / 手搓理由
- `conclusion`: 该组团最终结构结论

### Gate 脚本 (S6 输出后必跑, ❌ 卡死, 自述不算数)

```bash
python3 -c "
import json,os,sys
MEM='/Users/red/.claude/projects/-Users-red-Desktop-4-22--skill/memory'
cov=json.load(open('s6_coverage.json'))
EXPECT=set(open('s3_groups.txt').read().split()) if os.path.exists('s3_groups.txt') else None
iss=[]; seen=set()
for r in cov['groupings']:
    g=r.get('group','?'); seen.add(g)
    if not r.get('scanned_A_table'): iss.append(f'{g}: scanned_A_table!=true (没扫A表)')
    ph=r.get('pattern_hit','')
    if not ph: iss.append(f'{g}: pattern_hit 空 (未判定)')
    if str(ph).startswith('ui_pattern'):
        ev=r.get('read_evidence','')
        if not ev: iss.append(f'{g}: 命中{ph}但read_evidence空(没Read正文)')
        elif not os.path.exists(os.path.join(MEM,ev)): iss.append(f'{g}: read_evidence {ev} 文件不存在(凭证伪造/拼错)')
if EXPECT:
    miss=EXPECT-seen
    if miss: iss.append(f'S3表C组团未覆盖: {sorted(miss)}')
print('✅ S6 覆盖闸门通过' if not iss else '❌ S6 闸门未过:\n'+'\n'.join(iss))
sys.exit(0 if not iss else 1)
"
```

⛔ **gate 输出 ❌ → 必须回 S6 补全 (扫 A 表 / Read pattern.md / 补组团行), 重跑直到 ✅, 才允许进 S7。** 自述"我扫过了"不算数, 以 gate 退出码为准。

> gate 消灭**静默跳步**(没产物 / 没凭证 / 漏组团 → 机器卡死), 但**消灭不了判断错**(填了行但 pattern 归类错, gate 照样放行)。判断错靠 ① S6 #6 S7 落地预演 + ② 用户/复核抓。gate 是地板不是天花板。

---

⛔ 表 H + `s6_coverage.json` 输出 + gate ✅ 后立即停止, 等待用户回复"继续 S7"。
