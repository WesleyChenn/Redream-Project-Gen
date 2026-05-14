---
name: 组团识别和 Variant 最小化抽取
description: S3 骨架分析时按 5 步法识别组团; Variant 必须下沉到最小单元,大组团不做排列组合 Variant
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
- Variant 抽取必须下沉到最小单元(底板/角标/icon),**不要**在大组(行/卡/格)上做组合 Variant
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
