# Lesson: 结构图卡片布局规则（R1–R6）

**日期:** 2026-04-15
**状态:** ✅ 已落地（Cozy Shapes 生成器 `_card_total_h()` + col_order 堆叠逻辑）
**适用范围:** Redream-project-gen + cocos-project-gen（两个 skill 共用同一 HTML 模板 `FruitTruck_structure.html` / `BeadsOut_structure.html`）

## 事件

Cozy Shapes 第一版结构图布局混乱：L2 列按字母序排、L1 main 贴顶导致连线大幅斜拉、L3 四张卡堆在同一列但 `数字标签 / 数字标签_进度版 / 教学引导手指` 三张的 ref 源都是 `dot.圆点位置定位点`，线段从 dot 右侧凹槽拐回左侧同列，形成反折。

用户对照参考布局图反馈："线段之间的交叉最少，从左至右的创建/引用关系清晰"，要求把这三张卡移到 dot 的**更右一列**。

## 根因

之前我把"列号 = level"写死：level 由 BFS(stub+dyn) 自动算，x 坐标直接映射到 COL{level}。但**ref 连线**是同列时会让目标卡的入线必须向左走再回右，与 L→R 单向主流背道而驰。

layout 规则没把"ref 同列必右移"纳入，所以反折问题必然出现。

## 规则（R1–R6，生成结构图时强制执行）

| 规则 | 名称 | 内容 |
|------|------|------|
| **R1** | 分列按 level | 卡片 x = `COL{level}`（固定 step，默认 680px） |
| **R2** | 同列纵序按父级索引 | 同列内卡片的 Y 序与其 stub/dyn 上游父级的 `nodes[]` 索引序一致；多张卡共享一个 parent 节点时按创建逻辑顺序 |
| **R3** | 主干连线不交叉，ref 可交叉 | stub/dyn 是视觉父级主干，必须尽量无交叉；ref 是语义引用，允许交叉 |
| **R4** | L1 根节点纵向居中 | L1 main 的 y = L2 列 Y 跨度的中点 − 自身高度/2 |
| **R5** | 叶节点对齐 ref 加权中点 | 只有 ref 入线的叶卡（如反馈特效），y = 所有 ref 源的 Y 中心平均值 − 自身高度/2 |
| **R6** | ref 同列必右移 | **若卡 X 存在 ref 入线，其源卡 Y 与 X 处在同一自动算列，则 X 必须物理右移到 `COL{Y.col+1}`**（level 标签保持自动算值不变，只改 x） |

## Why

- **视觉 ≠ 语义层级**：level 描述"创建父子"，x 描述"读者眼球的 L→R 扫描方向"。这两个维度在大多数情况下重合，但遇到 ref（只读坐标）时分家。硬绑会让 ref 连线反折。
- **反折 = 信息熵爆炸**：读者扫一张图默认 L→R 推理，看到连线从右列拐回左列再拐回右列，脑内需要重建 3 次方向切换，图就失去了"一眼看懂"的意义。
- **R6 不改 level 标签**：level 反映的是"创建层级"，强行改标签会误导（例如 `number_label` 本来就是 board.dyn 的孩子，level=L3 是正确的）。只挪 x 既保持语义又修视觉。

## How to apply

### 生成器实现步骤

```python
# 1. 固定列宽
COL1, COL2, COL3, COL4, COL5 = 80, 760, 1440, 2120, 2800  # step=680

# 2. 定义 card_h() 估算高度
def card_h(tl, nd, fn, vr, nf):
    HDR, SEC, ROW = 62, 24, 34
    h = HDR + 4
    for n in (tl, nd, fn, vr, nf):
        if n > 0: h += SEC + n * ROW
    return h

# 3. 分列 order，按 R2 排（父 nodes[] 索引）
col2_order = [board, top_hud, download_guide, ad_banner, loading_screen]
#            ← 对应 main.nodes 中 [操作区定位区, 顶部HUD定位区, 下载引导层, 广告横幅定位区, 加载界面定位区] 索引序

# 4. R6 扫描：若卡 X 有 ref 入线且源卡在其自动列，则挪到右一列
#    典型：dot 在 COL3，number_label / number_label_progress / tutorial_finger 自动算出 L3 但都 ref dot，
#    → 三张卡统一挪到 COL4
col3_order = [dot]
col4_order = [number_label_progress, number_label, tutorial_finger]
col5_order = [text_fb]  # text_fb ref number_label*（在 COL4），继续右移到 COL5

# 5. 堆叠 y = 前一卡底 + GAP(24)
for col_list, col_x in [(col2_order, COL2), (col3_order, COL3), ...]:
    y = 72
    for c in col_list:
        c["x"], c["y"] = col_x, y
        y += card_h(...) + GAP

# 6. R4/R5 居中调整
main["y"] = l2_center - card_h(main) / 2
text_fb["y"] = ref_weighted_center - card_h(text_fb) / 2
```

### 自检清单（生成后肉眼或脚本核对）

1. 所有 stub/dyn 连线是否 L→R 单向推进（无回折）？
2. 所有 ref 连线源卡是否位于目标卡的**左**侧（x 严格小于）？
3. L1 根节点 Y 是否大致居中于 L2 跨度？
4. 同列卡片 Y 序是否与其上游 nodes[] 索引序一致？
5. 叶节点（纯 ref 入线）是否接近 ref 源的 Y 中点？

### 反模式

- ❌ 把所有同 level 卡放同列（无论是否 ref 源在同列）
- ❌ L1 main 贴顶 y=72（如 L2 跨度很大，会拉出 40°+ 的斜线）
- ❌ 用 level 标签决定 x（应由 col 决定 x，level 只是徽章）
- ❌ 为了"结构对称"把 ref 源主动挪到 ref 目标右侧（违反 L→R 阅读方向）

## 参考实现

- 生成器：`/tmp/gen_cozy_shapes_data.py` — `_card_total_h()` + col{2-5}_order 堆叠
- 输出：`CozyShapes_structure.html`（11 卡 / 15 连线 / stub=5 dyn=5 ref=5，R1–R6 全部落地）

## 关联

- `lesson_ref_connection_type.md`：ref 连线语义（R6 的前置，没有 ref 就没有 R6 的必要）
- `lesson_gp_group_indent.md`：同属结构图语义/视觉规则
- `references/structure-diagram-reference.md`：HTML 模板/数据结构总参考
- `phases/phase2-structure-diagram.md`：生成流程，应在 Step 7（layout）前执行 R6 扫描
