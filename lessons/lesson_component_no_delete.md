# 项目本地 Memory(给 Claude / 设计师 / 自己读的备忘)

> 本文件是 `/Users/red/.claude/projects/-Users-red-Desktop-4-22--skill/memory/` 的本地副本。
> Claude 实际读的是 `~/.claude/projects/.../memory/`,这里同步一份方便人类查看 + git 追踪。

---

## 教训记录

### Component 修复时绝不擅自删除 Component(2026-05-09 RoyalPass 项目教训)

**现象**:在 RoyalPass 视频生成全流程中,S7 抽出 6 个 Component 后,只有行 19/20 平铺残留(没被替换为 INSTANCE)。
我为了修 `combineAsVariants` 失败问题,擅自删了 `组_进度_行_tb` 和 `数量徽章` 两个 Component
(理由是"1 Variant 过不了 combineAsVariants"和"视觉签名相同"),结果连续被用户抱怨:
- "你怎么把进度条删了"
- "怎么可切换预览又不见啦"
- "30m 和 x1 的组件没有啦"

**根因**:Component 列表是用户的**设计决策**(哪些做 Component,哪些不做),不是工具限制下我可以决定的。
用户的洞察:**第一次 S7 输出时组件库和预览都好,只是 19/20 平铺。先解决平铺(让所有行都嵌套),
其他问题就不会出现**。

**正确做法**:

| 场景 | 错误修复 | 正确修复 |
|---|---|---|
| Component 只有 1 Variant | 删 Component 降级 FRAME | 加 dummy 第 2 Variant,用 fill 制造视觉差异 |
| 多个 Variant 视觉签名相同 | 合并/删 Variant | "显隐"类改 INSTANCE.visible=false / 其他用 fill 或 icon 加差异 |
| 行 19/20 这种"边缘显隐组合" 留作 FRAME | 删 Component 让 FRAME 合规 | 把 FRAME 抽成新 Variant,转 INSTANCE 引用 |
| 任何删 Component 操作 | 擅自决定 | **必须先问用户** |

**详细铁律**:见 `00_core_rules.md` 末尾两节:
- "S7 后必须 100% 嵌套化"
- "Component 修复铁律(combineAsVariants 失败时)"

**自检脚本**(交付前必跑,见 `00_core_rules.md` 内嵌):
```python
# 1. 每个 Component variants 数量 ≥ 2
# 2. 每个 Variant 的视觉签名 hash 唯一
# 3. 主屏 / Variant.layers 内无"漏网平铺 FRAME"(跟某 Component 结构指纹相同)
```

---

### 组团识别 + Variant 最小化(2026-05-09 RoyalPass 教训续)

**现象**:同事评审 RoyalPass Figma 输出后指出"结构过于扁平,缺少组团包装层"。
Claude 第一版直接把所有元素(气泡/内容/数量徽章/状态徽章/进度条/等级菱形)
当作网格行的扁平 children,没有"奖励格"等组团 FRAME。

视频原图实际由清晰组团构成:
- 每行 = 4 个并列组团(左气泡 / 中间进度条 / 右气泡 / 黄色高亮条)
- 顶部 = 3 个并列组团(标题 / 倒计时 / Pass进度条)

**根因**:SKILL 没明文规则告诉 Claude **如何识别视觉组团** + **如何最小化 Variant 颗粒度**,Claude 临场判断容易看走眼。

**5 步识别法则**(已写入 `03_skeleton.md` 第二步):

1. 先分高度相似的大组(列表行/卡片/导航项)
2. 大组内部分平行组团(并列视觉块)
3. 横向对比所有大组的相同组团找差异点
4. 把组团拆到最小变化粒度(底板/角标/icon)
5. 最小单元的状态枚举做 Variant

**5 大设计原则**(已写入 `00_core_rules.md`):

| 原则 | 内容 |
|---|---|
| 1. 变化下沉到最小单元 | 不在大容器(行/卡/格)上做"通用/对勾型/锁型"排列组合 Variant |
| 2. 大组团不抽 Component | FRAME 包装层,N 行各异通过子 INSTANCE 各自引用对应 Variant |
| 3. 数据驱动 vs 状态多态分离 | 频繁更新无穷尽 → 占位 RECT;枚举可数 → Component+Variant |
| 4. "空"也是一个 Variant | "常态空" Variant(空 frame),不用 visible=false |
| 5. 运行时数值不进 Variant | 进度条满/空 → CCProgressTimer 切割,不做 Variant |

**两类不做 Variant 的例外**:
- 奖励物图片 — 种类无穷,程序 setSpriteFrame 填
- 进度条本体 — 满/空运行时按 percentage 切

**反面案例(已踩)**:
- ❌ 网格行 4 Variant(通用/宝箱型/对勾型/对勾锁型)= 排列组合
- ❌ 用 visible=false 表达"无显示" = 应做"空 frame" Variant
- ❌ 奖励物做 7 Variant 列举道具 = 应占位 RECT 程序填

**详细规则**:
- `00_core_rules.md` "组团识别 + Variant 抽取最小化" 节(原则 + 例外 + 决策流程图)
- `03_skeleton.md` 第二步"组团识别(5 步法)" + 输出表 + 铁律
