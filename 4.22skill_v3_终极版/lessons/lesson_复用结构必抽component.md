# Lesson · 复用结构必抽 component (inline 重复 = ccb 抽取失败)

## 一句话
复用 ≥3 次的结构必抽 component, S7 写 inline FRAME N 次重复 = ccb 抽取失败 — 失去复用语义 + S11 抽不出统一 Component + 设计师改一处要改 N 处。

## 触发条件 (Trigger)
- **S6/S7 阶段**, 视频里某结构连续重复 ≥3 次 (如关卡奖励行 / 排行榜行 / 卡片网格项)
- S6 决议表标了 `reuse_count ≥ 3`
- 但 S7 输出时写成 N 个 inline `FRAME` 重复 (每行结构内联定义), 而不是抽 1 个 `component` + N 个 `INSTANCE`

## 失败模式 (What goes wrong)

### 反例: 5 行关卡奖励 inline 5 次 (RP 5.22)

```json
"screens[0].layers[xxx]": [
  // 行 1
  { "type": "FRAME", "name": "列表项_关卡奖励",  // ❌ 不是 INSTANCE
    "children": [...5 个子节点...] },
  // 行 2 - 内容跟行 1 几乎一样
  { "type": "FRAME", "name": "列表项_关卡奖励",
    "children": [...同样 5 个子节点, 重复定义...] },
  // 行 3, 4, 5 - 同样的事
  ...
]
"components": []   // ❌ 列表项没抽成 component
```

### 后果
- S11 抽 Component 时**抽不出**统一组件 — 5 个独立 FRAME, 引擎当 5 个不同物件处理
- 复用率丢失: scene.json 体积 5x, 数据驱动跑不通
- 设计师改 1 行样式 → 要改 5 处, 不一致风险

## 正确做法

### 抽 component + 5 个 INSTANCE 引用

```json
"screens[0].layers[xxx]": [
  // 5 个 INSTANCE 引用, 数据靠 overrides 差异化
  { "type": "INSTANCE", "name": "列表项_关卡奖励_20",
    "component_name": "列表项_关卡奖励", "variant": "常态",
    "w": 1080, "h": 368,
    "overrides": { "文本_关卡号": "20", "组_宝箱": "金", ... } },
  { "type": "INSTANCE", "name": "列表项_关卡奖励_21", ... },
  ...
],
"components": [
  // ✅ 1 个 component, 定义 1 次
  { "name": "列表项_关卡奖励",
    "w": 1080, "h": 368,
    "variant_property": "状态",
    "variants": [{
      "name": "常态",
      "is_default": true,
      "layers": [...所有 5 个子节点定义在这里...]
    }]
  }
]
```

## 自检方法

### 机器查 (S10)
```python
# 扫 screens[].layers 找 FRAME with same name 重复 ≥3 次
from collections import Counter
def find_inline_repeat(layers):
    names = [l.name for l in layers if l.type == "FRAME"]
    cnt = Counter(names)
    return [name for name, c in cnt.items() if c >= 3]

# 任一 inline 重复 ≥3 次 → ❌ 该抽 component
```

### S6 决议时
S6 决议表必明确写 `reuse_count: N` + `abstract_ccb: true`。S7 看到 `abstract_ccb: true` → 必抽 component, 不能写 inline。

## 关联铁律 / 文档

- **铁律 11** (ccb 维度 ≠ 多态维度) — 复用 ≥3 必抽 ccb
- **lesson_ccb维度vs多态.md** — 同主题, 更详细判据
- **06a_S6_ccb抽取标准.md** — ccb 抽取 3 标准
- **lesson_规则11.5_子节点name一致.md** — 抽 component 后, 跨实例 children name 必一致

## 实证案例

| 日期 | 屏 | 现象 | 修法 |
|---|---|---|---|
| 2026-05-22 | Royal Pass | 5 个关卡奖励行 inline 5 次重复, 没抽 component | 加本 lesson + S10 自检脚本 |

## 生命周期
- **创建**: 2026-05-22
- **状态**: active
