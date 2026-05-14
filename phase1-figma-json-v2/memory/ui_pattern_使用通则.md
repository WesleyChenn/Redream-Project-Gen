---
name: ui_pattern_使用通则
description: 所有 ui_pattern_*.md 的元规则 — 通则是"通常情况", 实际以视频为准; 任何 icon 都可能附加角标
type: project
originSessionId: 266a40b7-0aa3-436f-ae8c-03b7c50d6515
---
# UI Pattern 使用通则(元规则, 必读)

所有 `ui_pattern_*.md` 抽出的规则是**通常情况**, 不是绝对。

## 元规则 1: **以视频实际为准, 不要硬套**

memory 里的 pattern 规则**是经验归纳**, 不能盖过实际视频证据。

### 正确用法

```
看截图 → 候选 pattern 匹配 → 再看截图细节 →
  ✅ 匹配:套 pattern
  ⚠️ 部分匹配:套 pattern 框架 + 局部调整(memory 没覆盖的部分按实际看)
  ❌ 不匹配:用 SKILL 通用规则, 不强套 pattern
```

### 反面案例(强套 pattern 的错误)

- 看到"长条 + 数字"就一定套 `横排徽章_左图右文` → 错(可能是进度条 / 按钮 / 别的)
- 角标看到"红色圆形"就一定是 `角标_红点` → 错(可能是状态指示器 / 装饰)
- 看到"圆形 + icon"就一定是 `单图标_无角标` 按钮型 → 错(可能是头像 / 大型奖杯 等)

## 元规则 2: **任何 icon 都可能附加角标**

```
icon 上常见角标位置(2 处高频):
  右上角:数字 / 红点 / 感叹号 (通知 / 数量 / 新内容)
  右下角:+ / 倍率 / 锁 / 对勾 (充值入口 / 加成 / 锁定 / 已完成)

其他位置(较少):
  左下角:等级 / 标签
  下边框中:阈值数字
  左上角(罕见)
```

**判断时永远多看一眼 icon 角落**:有可能漏识角标。

## 元规则 3: **Variant 的判断核心 — "同位置 + 多内容"**

跨多个 INSTANCE 在同一位置出现, 内容不同 = **同 Component 多 Variants**。

不是按"内容"分独立 Component, 是按"位置 + 角色"分。

### 例

```
排行榜 10 行, 每行右上角都有"状态角标"位置:
  行 1: 内容=锁
  行 2: 内容=对勾
  行 3: 内容=数字"5"
  行 4: 没显示 (visible: false)
  ...

→ S7 阶段一: 10 行都画完整 FRAME, children 100% 一致, 显示的实例 visible:true, 没显示的 visible:false
→ S11 自动抽: 同 Component `角标_状态_行`, Variants = [常态(锁/对勾/数字 实例视觉签名不同 → 多 Variant), 空 (从 visible:false 切出)]

→ ❌ 不是 4 个独立 Component(角标_锁 / 角标_对勾 / ...)
→ ❌ S7 阶段不要直接写 `variant: 空` (那是 S11 抽完的形态)
```

## 元规则 4: **"该状态不显示" 阶段一用 `visible: false`, S11 抽取自动转空 Variant**

> ⚠️ **重要更新 (新 workflow)**: 阶段一 Claude 写 scene.json 时 **永远不直接写 Variant**, 包括"空 Variant"。
>
> - **阶段一 (S7)**: 同结构多实例每个实例都画完整 FRAME (children 100% 一致), 该位置不显示的实例写 `visible: false`
> - **阶段二 (S11, extract_components.py)**: 自动按 `visible: false` 切分出"空 Variant" (脚本 `_filter_invisible` 把 visible:false 节点的 layers 过滤成空 → 空 Variant)
>
> 也就是说: memory 教学里"做空 Variant"是 **S11 之后的结果**, **不是 S7 应该写的形态**。

### 阶段一具体写法 (S7)

```json
✅ 第 4 行有角标:
{ "type": "FRAME", "name": "角标_状态",
  "visible": true,
  "children": [ {"type":"RECTANGLE","name":"底板_圆角标"}, {"type":"TEXT","name":"文本_数字","content":"5"} ]
}

✅ 第 7 行无角标 (隐藏但 children 完整, 跟显示实例 100% 一致):
{ "type": "FRAME", "name": "角标_状态",
  "visible": false,
  "children": [ {"type":"RECTANGLE","name":"底板_圆角标"}, {"type":"TEXT","name":"文本_数字","content":""} ]
}

❌ 错误 (阶段一不要写):
{ "type": "INSTANCE", "name": "角标_状态", "variant": "空" }
```

### 子节点 name 必须 100% 一致 (规则 11.5)

同结构多实例 (8 行列表项 / 多状态角标位置), children 数组里**每个子节点 name 必须一致**, 否则 S11 抽不出统一 Component。

实例间差异**只允许**: TEXT.content / 视觉属性 (fill / corner_radius / opacity / visible)。

### 典型场景 (都用 `visible: false`)

- 角标在某些行不显示 → 角标 FRAME `visible: false`
- 道具组在某些行没道具 → 道具组 FRAME `visible: false`
- 底标在某些情况不显示 → 底标 FRAME `visible: false`
- 按钮上附加状态提示偶尔显示 → 状态提示 FRAME `visible: false`

## 元规则 5: **不该做 Variant 的(常见误区)**

| 不该做 | 原因 | 该怎么处理 |
|---|---|---|
| icon 内容(金币/盾牌/钟表)| 数据驱动 | 占位 RECT, 程序填图 |
| 文本内容(数字/时间/x/y)| dynamic | overrides 文本字段 |
| 颜色差异(底板色不同)| 上下文决定 | 占位 fill, S5 阶段从截图取色 |
| 尺寸差异(同 layout 不同大小)| INSTANCE 缩放 | INSTANCE w/h 调整 |
| layout 差异(icon 左 vs 右)| Component 设计 | 不同 Component 或层位置调整, 不是 Variant |
| 数量差异(2 道具 vs 3 道具)| 结构变化 | 多个独立 INSTANCE 各自 [默认, 空] |

## 元规则 6: **Variant 的"按视频实际数量"** (针对 S11 抽完之后的结果)

> S7 阶段一: 每个实例画扁平 FRAME, 不想 Variant; S11 自动按视觉签名抽 Variant。 本规则描述的是 S11 抽完后 **预期看到的 Variant 数量**。

- **S11 抽完不会出现"未来可能有几种"** — 只会装视频里**实际看到的形态**
- 每见新形态 (新一段视频), 重新跑一次 extract_components.py 增量沉淀
- "常态 / 空" 是基本对 (几乎所有显示性 Component 都有 — 来自 S7 visible:true / visible:false 的切分)

## 来源 / 教学背景

2026-05-12 用户在抽 9 个 ui_pattern 后的元规则总结:
- "我说的都是通常情况，还是以实际视频为准"
- "任何 icon 都有可能有角标, 通常位于右上角和右下角"
- 角标 / 底标 / 按钮 / 进度条节点 等的 Variant 抽取核心是"位置 + 状态切换", 不是内容差异
- (旧 workflow 写法) "空 frame Variant 是表达该状态不显示的正确方式" → **新 workflow**: S7 用 `visible: false`, S11 自动转空 Variant
