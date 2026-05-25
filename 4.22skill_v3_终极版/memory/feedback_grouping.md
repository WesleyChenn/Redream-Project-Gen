---
name: 组团识别和 Variant 差异下沉到最小单元
description: S3 按 5 步法识别组团; **Variant 差异下沉到最小单元(粒度,不是 ccb 嵌套层数)**, 大组团不做排列组合 Variant; ccb 嵌套按 00f 视觉缩窄机制 + 3 标准决定, 不限层数
type: feedback
originSessionId: dfb7fa16-bf22-4721-a9bf-80258af3655e
---
S3 骨架分析时,在量测元素边界后、物理分组前,**必须按 5 步法识别组团**:

1. 分高度相似的大组(列表行/卡片/导航项等复用单元)
2. 大组内部分平行组团(并列视觉块)
3. 横向对比所有大组的相同组团找差异点
4. 把组团拆到最小变化粒度(底板/角标/icon)
5. 最小单元的状态枚举做 Variant

**Why:** RoyalPass 项目踩坑教训。Claude 第一版没识别出"奖励格/中央"组团,所有元素直接是网格行扁平 children;后续抽 Variant 时做了"通用/宝箱型/对勾型/对勾锁型"4 个排列组合 Variant,违反"变化下沉到最小单元"原则,被同事评审挑出。用户明确指示"按视频出现的种类枚举,不允许屏幕里没有的物件排列组合"。

**How to apply:**

- 任何屏走 S3 时严格执行 5 步法,先识别组团再画骨架
- **Variant 抽取(差异下沉到最小单元)**:底板/角标/icon 各自带独立 Variant,**不要**在大组(行/卡/格)上做组合 Variant
- ⚠️ **"最小化" ≠ "ccb 嵌套层数最小化"** — Variant 粒度最小化只管"某个组件内部 Variant 怎么抽得最小";ccb 嵌套(抽不抽子 ccb)按 4.22最新skill/00f 视觉缩窄机制 + 3 标准决定,**不限层数**,该抽就抽
- 🔑 **一句话核心原则(2026-05-17)**:**多态(Variant)= 最小化**(抽 Variant 让被复用组件尽可能小,差异下沉到最小变化单元);**子 ccb = 最大化**(抽子 ccb 让复用尽可能多次发生,能复用就抽,层数不限)。ccb 决定"抽什么出来反复用",Variant 决定"这个被反复用的东西内部差异压到多小"
  - ⚠️ **别停留在"差异下沉"手段**:目的是**压小被复用组件本身体积**。复杂结构先把不变大部分 inline / 抽别的 ccb,Variant 组件只保留"真正会变的那一小块"。反面:3 态卡片只下沉差异点却抽出仍偏大的 Variant 组件(不变底板也包进去)
  - 🔴 **ccb 维度 ≠ 多态维度(2026-05-18 Team Battle 复盘,我反复栽的高频错,完整见 4.22最新skill/00f 边界1.5)**:
    - 判据1:抽不抽 ccb 只看 00f 3 标准(复用/动态/独立),**跟有没有多态无关**。反面:把"列表项不做排列组合多态"误当"列表项不抽 ccb"→ 做成 FRAME 平铺。正:列表项复用 10 次**必抽 ccb**,可 0 多态(1 默认 Variant),差异下沉子 ccb
    - 判据2:**有多态 → 必然是 ccb**(Variant 只能挂 components[].variants[],裸 FRAME/RECT/TEXT 无 variants 字段)。反面:用"两个不同命名裸 RECT"表达 组_行底板 常态/高亮。正:要离散多态先抽成 ccb component
    - 判据3:同一差异只在**唯一最小单元 ccb** 做一次多态,外层不重复包。反面:列表项 2V + 组_行底板 2V 同一"当前用户高亮"做两遍。正:只在 组_行底板,外层列表项 1 默认 Variant + 主屏 INSTANCE override
    - 口诀:**子 ccb 不一定有多态,但有多态的一定是子 ccb** — 可反用作判据(看到要离散多态 → 必须抽 ccb)
- 数据驱动内容 → 占位 RECT 或运行时实现, 不做 Variant:
  - 奖励物图片(种类无穷)→ 占位 RECT,程序 setSpriteFrame
  - 进度条满/空(数值连续)→ 引擎 CCProgressTimer 切割
- **"空状态" 用 `visible: false` 表达**(新 workflow, 2026-05-13 更新): S7 阶段画完整扁平 FRAME (children name 100% 一致), 不显示的实例写 `visible: false`; S11 extract_components.py 自动 `_filter_invisible` 切出空 Variant。 ⚠️ 旧记录里"不要用 visible=false / 应做空 frame Variant"是 v20.6 schema 时代的写法, 已废止。
- 新 skill 详细规则:
  - 组团识别 5 步法: `/Users/red/Desktop/4.22skill_v2/03_S3_识别布局.md`
  - 子 CCB 显隐铁律 + visible:false 阶段一写法: `/Users/red/Desktop/4.22skill_v2/07d_S7_嵌套占位背景.md`
  - Variant 抽取范围 + 例外: `/Users/red/Desktop/4.22skill_v2/06_S6_pattern命中.md` #3
  - S11 extract_components.py 抽取逻辑: `/Users/red/Desktop/4.22skill_v2/11_S11_抽取导出.md`

**反面案例(已踩,以后避开):**

- ❌ 网格行 4 Variant(通用/宝箱型/对勾型/对勾锁型)= 排列组合
- ❌ S7 阶段一直接写 `type: INSTANCE` / `variant: 空` = 抢跑到 S11 形态; 应画扁平 FRAME + visible:false
- ❌ 奖励物做 7 Variant 列举道具 = 应占位 RECT 程序填
- ✅ 网格行: S7 每行画扁平 FRAME (children 100% 一致, 视觉/visible 不同); S11 自动切 Variant

**Component 修复反面**(同上次 RoyalPass 经验):
- ❌ 1 Variant 过不了 combineAsVariants → 删 Component 降级 FRAME(违反用户设计意图)
- ✅ 加 dummy 第 2 Variant 制造视觉差异(fill / corner_radius)
