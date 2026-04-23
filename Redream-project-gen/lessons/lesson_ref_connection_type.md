# Lesson: 新增 `ref` 灰虚线连线 — 坐标引用 ≠ 创建父级

**日期:** 2026-04-15
**状态:** ✅ 已落地（BeadsOut/FruitTruck 模板 + phase2 文档 + Cozy Shapes 结构图）

## 事件

Cozy Shapes 结构图里，教学引导手指和成功特效的 dyn 起点都被画成了 `dot.圆点位置定位点` / `dot.完成反馈定位点`。用户反馈：

> 教学引导手指不是创建在圆点位置定位点上，而是引用该定位点的坐标参数，创建在游戏主界面的引导层上，所以可以引入一条灰色的虚线，表示读取所连节点的坐标而不创建于该节点上

同时数字标签从 dot 里拆出成独立 prefab 后，也同样满足这个模式：创建在 board.数字标签层，坐标读 dot.圆点位置定位点。

## 根因

在原来的 2 种连线类型里（stub 嵌套 + dyn 动态创建），**"创建父级"** 和 **"坐标源"** 被混为一谈。真实项目里这两者经常分家：
- 反馈特效/教学手指必须挂在全局层（引导层/特效层），**不能**挂在 dot 下，否则 dot 销毁时它们跟着销毁；
- 但它们的**坐标**又要对齐 dot 上的定位点。

只用 dyn 表达这类关系会误导：看图的人以为 dyn 目标就是视觉父级。

## 规则

### 三种连线类型（此后的全部结构图适用）

| type | 语义 | 颜色/线型 | 允许多条入线？ |
|------|------|-----------|---------------|
| `stub` | 嵌入式子 prefab（nested） | 蓝实线 | ❌ 唯一视觉父级 |
| `dyn` | 运行时 instantiate（动态视觉父级） | 橙实线 | ❌ 唯一视觉父级 |
| `ref` | **只读坐标**（不是父级） | 灰虚线 | ✅ 可多条 |

**子卡片的视觉父级入线 = dyn + stub 合计必须恰好 1 条**（L1 除外）；ref 可 0 可多。

### 渲染规则（BeadsOut/FruitTruck 模板已实现）

- 颜色变量：`--line-ref:#9ca3af`
- 线型：`stroke-dasharray:5 4`，opacity 0.75（hover 1）
- 端点小灯：灰色
- **incomingType 计算跳过 ref** — 横条色条只反映视觉父级（stub/dyn），不会因 ref 入线被染灰
- 连线面板多一个 `坐标引用` 按钮

### 数据驱动

生成器里：
```python
conns = [
    # 视觉父级：dyn
    {"fromCard": "main", "fromNode": 3, "toCard": "tutorial_finger", "type": "dyn"},
    # 坐标源：ref
    {"fromCard": "dot",  "fromNode": 1, "toCard": "tutorial_finger", "type": "ref"},
]
```

自检脚本断言：
1. type ∈ {stub, dyn, ref}
2. 每张非 L1 卡片的 stub+dyn 入线数 = 1

## 何时用 ref

典型场景三件套：
1. **反馈特效**（"酷!"/星星/+1金币）：挂特效层，坐标读触发点定位点
2. **教学引导**（手指/箭头）：挂引导层，坐标读目标按钮/圆点定位点
3. **动态标签**（数字/血条/名字）：挂独立标签层，坐标读主体定位点

共同特征："这个对象是否需要独立于主体的生命周期？"是 → 父级应该是全局层 + ref 坐标。

## How to apply

1. 画结构图前，对每个 dyn 候选先问："这个目标节点真的会作为运行时 parent 吗？还是只提供坐标？"
2. 是运行时 parent → dyn；只提供坐标 → ref
3. ref 目标卡片必须**另有**一条 dyn/stub 入线（真正的父级）
4. 生成后肉眼确认：
   - ref 线是灰虚线
   - 色条仍按视觉父级（stub 蓝 / dyn 橙 / 无父级白）

## 关联

- `templates/BeadsOut_structure.html` / `FruitTruck_structure.html`：renderer 已加 ref 支持
- `phases/phase2-structure-diagram.md`：连线类型表 + Step 8 第 5、6 条断言
- `lesson_gp_group_indent.md`：同样是结构图语义升级类 lesson 的姐妹篇
