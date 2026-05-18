# Lesson: 主路径手写 v20.6 schema 的必填字段 (Figma 全错位事故)

## 一句话

主路径 (复杂场景跳过脚本, S11 阶段 Claude 手写 v20.6 schema) 时, **每个 component 必须有 `w / h / variant_property`, 每个 INSTANCE 的 `w/h` 必须 == 对应 component 的 `w/h`, 每个 layer 必须有 `element_class`**。漏任一字段 → Figma 导入后全画面错位。

## 事故 (2026-05-18 Team Battle 全错位)

手写的 `components[]` 只有 `name + variants`, 没写 `w / h / variant_property`:

```json
❌ 事故现场:
{
  "components": [
    { "name": "组_行底板", "variants": [ {...}, {...} ] }   ← 缺 w/h/variant_property
  ]
}
```

后果: 用户截图——Figma 里**大量 frame 散开 + 内容全错位**。

根因: component 没 `w/h` → Figma 没有固定 artboard 尺寸 → INSTANCE 无法对齐, Figma 不会自动缩放 instance, 所有子节点按各自绝对坐标乱摆。

## 正确做法 (主路径手写 v20.6 必带字段)

```json
✅ 正确:
{
  "components": [
    {
      "name": "组_行底板",
      "w": 980, "h": 132,                  ← 必填
      "variant_property": "状态",           ← 必填 (variants 的区分维度名)
      "variants": [
        { "name": "常态", "is_default": true, "layers": [...] },
        { "name": "当前用户高亮", "layers": [...] }
      ]
    }
  ],
  "screens": [{
    "layers": [{
      "type": "INSTANCE",
      "component_name": "组_行底板",
      "w": 980, "h": 132,                   ← 必须 == component 的 w/h (Figma 不缩放 instance)
      "variant": "常态",
      "element_class": "static"             ← 每个 layer 必填 static/dynamic
    }]
  }]
}
```

## 3 条必检

| # | 规则 | 漏掉的后果 |
|---|---|---|
| ① | 每个 component 有 `w` `h` `variant_property` | Figma 无固定 artboard → 全错位 |
| ② | 每个 INSTANCE 的 `w/h` == 对应 component 的 `w/h` | Figma 不缩放 instance → 该实例错位 |
| ③ | 每个 layer (含 component 内部 layer) 有 `element_class` (static/dynamic) | 引擎侧 static/dynamic 判定缺失 |

⚠️ **遍历盲区**: 自检脚本遍历 key 必须含 `components` (不只 `screens`)。只遍历 `screens` → component 内部 layer 漏检, 自检会假阳性通过。

## 写之前必做

**cat 一份权威样本** (`team_battle_final.json` 这类引擎跑通过的 v20.6 文件), 逐字段对照, 不要凭记忆手写 schema。凭记忆 = 必漏字段 (本次就是凭记忆漏 w/h)。

## 预防到哪个阶段

- **S11 主路径**: 手写 component 时立刻补全 `w/h/variant_property`; 写 INSTANCE 时回查对应 component 的 w/h 抄一致
- **S10/S11 自检**: 跑 v20.6 schema 完整性脚本 (遍历 `screens` + `components` 两个 key), 检 ①②③ 三条
- 见 `steps/11_S11_抽取导出.md` 主路径自检清单 "#### 🔴 v20.6 schema 完整性" 小节

## 来源

- 2026-05-18 Team Battle 视频生成, 主路径手写 schema 漏 w/h → 用户截图全错位
- 对照样本: `team_battle_final.json`
- 完整自检: `steps/11_S11_抽取导出.md` 主路径自检清单 + `steps/10_S10_自检.md`

## 关联

- lesson_扁平vs_v206_schema (S7 扁平 vs S11 schema — 这条讲 S11 schema *内部* 必填字段)
- lesson_ccb维度vs多态 (有多态必是 component → component 必须有 w/h)
- feedback_verify_before_claim (写 schema 前必 cat 样本对照)
