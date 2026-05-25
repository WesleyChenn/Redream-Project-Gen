# Lesson: 扁平 scene.json vs v20.6 schema (S7-S9 vs S11)

## 一句话

S7-S9 阶段输出**扁平 scene.json**, 没有 `type: INSTANCE` / `component_name` / `variant` / `overrides` / `components[]` 字段。 这些是 **S11 抽取后**才有的 v20.6 schema 字段。

## 易犯错的场景

- 看 memory `ui_pattern_*.md` 的 JSON 例子里有 `type: INSTANCE` / `variant: 锁`, 以为 S7 阶段也要这么写
- 看 S6 标了"角标_状态 Variants: 锁/对勾/空", S7 阶段就直接写 `variant: 空` 字段
- 写 8 个列表行时, 直接想"列表项 Component 含 8 个 INSTANCE", 不走"8 个独立完整 FRAME 扁平"

## 正确做法 (S7 阶段)

```json
✅ S7 扁平 scene.json:
{
  "screens": [
    {
      "name": "界面_排行榜",
      "type": "FRAME",
      "layers": [
        {
          "type": "FRAME", "name": "列表项_排名1",
          "children": [
            { "type": "RECTANGLE", "name": "底板_行" },
            { "type": "TEXT", "name": "文本_玩家名", "content": "Dennis" },
            { "type": "FRAME", "name": "角标_王冠", "visible": true, "children": [...] }
          ]
        },
        {
          "type": "FRAME", "name": "列表项_排名2",
          "children": [
            { "type": "RECTANGLE", "name": "底板_行" },
            { "type": "TEXT", "name": "文本_玩家名", "content": "Eva" },
            { "type": "FRAME", "name": "角标_王冠", "visible": false, "children": [...] }
          ]
        }
      ]
    }
  ],
  "components": []  // S7 阶段空数组
}
```

8 个 `列表项_排名N` 是**独立完整 FRAME**, 各自含完整 children, 实例间差异:
- TEXT.content 直接写实际名字
- 不显示的子节点 wrapper 写 `visible: false` (不是 `variant: 空`)
- 视觉差异写 `corner_radius` 微差 (不写 fill, fill 一律省略)

## 错误做法 (S7 阶段抢跑写成 v20.6)

```json
❌ S7 阶段错写 v20.6 schema:
{
  "screens": [
    {
      "layers": [
        {
          "type": "INSTANCE",          ← ❌ S7 没有 INSTANCE 节点
          "component_name": "列表项_排名",
          "variant": "常态",            ← ❌ S7 没有 variant 字段
          "overrides": {                ← ❌ S7 没有 overrides
            "文本_玩家名": "Dennis"
          }
        }
      ]
    }
  ],
  "components": [                       ← ❌ S7 阶段 components[] 是空数组
    {
      "name": "列表项_排名",
      "variants": [...]
    }
  ]
}
```

## S11 抽取后自动产生 (v20.6 schema)

```json
S11 跑 extract_components.py 后:
{
  "screens": [...含 INSTANCE 节点...],
  "components": [
    {
      "name": "列表项_排名",
      "property_name": "状态",
      "variants": [
        { "name": "常态", "is_default": true, "layers": [...] },
        { "name": "变体2", "layers": [...] }
      ]
    }
  ]
}
```

## 主路径例外 (来自 11_S11 主路径)

复杂场景 (奖励物枚举+占位混合 / Variant 内部异构), Claude **跳过脚本直接在 S11 阶段写 v20.6 schema**。 但这是 **S11 阶段** 的事, 不是 S7。

S7 阶段无论复杂简单都是**扁平 FRAME** (即使后续 S11 走主路径手工构造)。

## 字段对照表

| S7 阶段写 | S11 自动产生 |
|---|---|
| `type: FRAME` (列表项扁平) | `type: INSTANCE` |
| (无 `component_name`) | `component_name: "列表项_排名"` |
| `visible: false` | `variant: "空"` (Variant.layers=[]) |
| 实例 TEXT.content 直接写 | `overrides: { "文本_玩家名": "Eva" }` |
| `components: []` | `components: [{ "name": ..., "variants": [...] }]` |

## 来源

- 旧 00d skill: "8 个列表行写扁平 FRAME, 每个独立完整 children"
- RoyalPass 测试 (2026-04~05) 反复混淆 S7/S11 形态
- 07d 新 skill #1: "S7 阶段只用 `visible: false`, 不写 `variant: 空`"
