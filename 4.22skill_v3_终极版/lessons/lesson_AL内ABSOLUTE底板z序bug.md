# Lesson · AL 容器内 ABSOLUTE 底板的 z 序 bug

## 一句话

`layoutPositioning: ABSOLUTE` 的子节点在 AL 容器内被 Figma 拉到 z 最顶层，**底板放 AL 容器内 + ABSOLUTE 会覆盖 AL flow 内容** → 改用 **NONE 外层 + 内层 AL 容器** 模式。

## 触发条件 (Trigger)

S7 阶段，对"列表项 / 网格项 / 卡片"类复用 component 写结构时：
- 该 component 有 **底板** (铺满整行/整卡)
- 该 component 内含多个子节点需要 **横向/竖向 AL 排版**
- 该 component 可能有 **角标 / 装饰溢出**

## 失败模式 (What goes wrong)

### 旧写法 (⛔ 已废)

```json
{
  "name": "列表项_journey",
  "w": 980, "h": 200,
  "layoutMode": "HORIZONTAL",                  // ← AL 外层
  "children": [
    { "name": "底板_行", "layoutPositioning": "ABSOLUTE",  // ❌ 拉到顶层
      "x": 0, "y": 0, "w": 980, "h": 200 },
    { "name": "内容_行", ... },                            // AL flow
    { "name": "组_金币堆_行", ... },                       // AL flow
    { "name": "角标_行", "layoutPositioning": "ABSOLUTE" } // 也被拉顶层
  ]
}
```

### 渲染结果

底板 ABSOLUTE 被 Figma 自动拉到 z 顶层 → **底板覆盖了 AL flow 内的所有子节点** → 截图里整行空白，看不到任何内容。

把底板手动拖出去 → 底下的内容露出来 → 证实是 z 序问题。

## 正确做法 (NONE 外层 + AL 内层, 3 层 z 序)

```json
{
  "name": "列表项_journey",
  "w": 980, "h": 200,
  "variants": [{
    "name": "常态",
    "layers": [
      // ── 底层: 底板 ──
      { "type": "RECTANGLE", "name": "底板_行",
        "x": 0, "y": 0, "w": 980, "h": 200,
        "corner_radius": 25 },                              // ✅ 不写 layoutPositioning

      // ── 中层: 内容容器 (AL 排版) ──
      { "type": "FRAME", "name": "组_内容容器",
        "x": 0, "y": 0, "w": 980, "h": 200,
        "layoutMode": "HORIZONTAL",                          // ✅ AL 在内层 wrapper
        "primaryAxisAlignItems": "MIN",
        "counterAxisAlignItems": "CENTER",
        "itemSpacing": 15, "paddingLeft": 30, "paddingRight": 30,
        "children": [
          { "name": "内容_行", "w": 580, "h": 170 },
          { "name": "组_金币堆_行", "w": 320, "h": 200 }
          // AL 接管 — 子节点不写 x/y/constraints
        ]
      },

      // ── 顶层: 角标 / 附加溢出 ──
      { "type": "INSTANCE", "name": "角标_行",
        "x": 905, "y": 30, "w": 75, "h": 75 }              // ✅ 不写 layoutPositioning
    ]
  }]
  // ⚠️ component 顶层不写 layoutMode — 外层是 NONE
}
```

### 3 层 z 序 (按 children[] 顺序)

| children[] 位置 | 内容 | z 序 |
|---|---|---|
| `[0]` | 底板 RECT | 底层 |
| `[1]` | 内容容器 (内层 AL) | 中层 |
| `[2]` (or `[-1]`) | 角标 / 附加溢出 | 顶层 |

## 自检方法 (Verification)

### 机器查 (S10 加一条)

对每个 component 的 layers (or variant.layers)：
1. 如果 component 是 NONE 外层（顶层无 `layoutMode` 或为 `NONE`）→ ✅ 通过
2. 如果 component 是 HORIZONTAL/VERTICAL AL（顶层有 AL `layoutMode`）→ 扫 children：
   - 任一 children 有 `layoutPositioning: ABSOLUTE` + name 含 `底板_` → ❌ **z 序 bug, 改 NONE 外层**

### 人工查 (S6 决议时)

S6 决议表里如果某 component 同时满足：
- 有底板 (children[0] 是 `底板_xxx` RECT)
- 有多个子 INSTANCE 需要 AL 排版

→ S7 必用 **NONE 外层 + 内层 AL 容器** 模式（详见 07e §"复用类 component 内部布局"）。

## 关联铁律 / 文档

- **铁律 15** (AL = S3 layoutMode 合约) — AL 在哪一层做的具体化
- **07e §"⛔ AL 父容器内的 ABSOLUTE 底板"** — 旧 ABSOLUTE 写法废弃说明
- **07e §"复用类 component 内部布局"** — 新 NONE 外层 + AL 内层 标准结构
- **lesson_视觉缩窄即AL.md** — AL 防出框的元规则 (这条 lesson 是它的 z 序补丁)

## 实证案例

| 日期 | 屏 | 现象 | 原因 |
|---|---|---|---|
| 2026-05-22 | 浮层_Journey_Offer | 5 行列表项渲染全空白 (Claim / Win N Levels / 数字 / 锁全不见)，拉开底板才露出 | `组_行底板` ABSOLUTE 在 HORIZONTAL AL 容器内 → Figma 拉底板到 z 顶层 → 覆盖 AL flow 内容 |

## 生命周期

- **2026-05-22** 创建
- **状态**: active
