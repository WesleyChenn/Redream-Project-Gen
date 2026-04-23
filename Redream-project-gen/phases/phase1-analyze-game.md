# 阶段 1：游戏分析与原型

> **触发时机**：用户要求"分析游戏录屏/截图"、"出低保真原型"、"识别 UI 结构"时加载此文件。

---

## 目标

把原始资料（录屏 / 截图 / PRD / Cocos 工程）转为结构化的 UI 骨架 + Figma 低保真原型，为阶段 2 的工程结构图提供语义来源。

**产出物**（归档到 `~/JarvisPark/output/ada/<project>/01-analysis/`）：
1. Figma 低保真原型链接（含所有关键帧/场景/弹窗）
2. `skeleton.json` — UI 骨架清单（每个区域 bbox / 节点类型 / 命名 / 语义角色）
3. `ccb-split-plan.md` — CCB 拆分建议（列出需要拆成几个 CCB、哪些 stub 嵌入、哪些 dyn 生成）

---

## 执行流程

本阶段**完全复用 elsa-analyzer-line 的 9 步管线**。读取 `references/analyze-pipeline-reference.md` 作为主手册，辅以：
- `references/analyze-structural-rules.md` — 骨架规则（HORIZONTAL/VERTICAL 计分、约束传播 P-1~P-5）
- `references/analyze-node-patterns.md` — 节点模式识别
- `references/analyze-naming.md` — 命名规范
- `references/analyze-animation-prototype.md` — 动画原型导出

### 关键变更：针对 Redream 管线的输出要求

elsa-analyzer-line 原流程终点是"Figma 原型 + 自检"。Redream-project-gen 要求在此基础上**额外产出 2 份文件**，用于交接阶段 2：

#### 1. skeleton.json（骨架清单，JSON 格式）

```json
{
  "project": "SixGridBBQ",
  "resolution": {"w": 1080, "h": 2400},
  "scenes": [
    {
      "name": "main",
      "regions": [
        {
          "id": "hud_area",
          "bbox": [0, 0, 1080, 240],
          "role": "HUD",
          "nodes": [
            {"type": "sprite", "name": "bg_hud", "bbox": [0,0,1080,240]},
            {"type": "label", "name": "score_text", "bbox": [40, 80, 400, 80]}
          ]
        },
        {
          "id": "board_area",
          "bbox": [0, 240, 1080, 1800],
          "role": "GAMEPLAY",
          "children_kind": "container",
          "children_count": 5,
          "nodes": []
        }
      ]
    }
  ]
}
```

**字段要求**：
- `role` ∈ {`HUD`, `GAMEPLAY`, `AD`, `RESULT`, `DECOR`, `OVERLAY`}
- `children_kind` / `children_count`：若为动态生成的重复单元，必须标注元素类型和数量，驱动阶段 2 的 dyn 连线

#### 2. ccb-split-plan.md（CCB 拆分建议，Markdown）

```markdown
# <Project> CCB 拆分建议

## 顶层 CCB（L1）
- **main.red** — 根场景，包含所有 L2 定位区

## L2 CCB（嵌入式，stub 连线）
- **hud.red** — HUD 区块
- **board.red** — 棋盘区块（静态布局层）
- **ad_banner.red** — 广告横幅
- **result_panel.red** — 结果面板（默认 active=false）

## 动态单元（dyn 连线，运行时 instantiate）
- **container.red** — 容器单元，由 board 在运行时按 spawn 规则生成 N 个
- **food_element.red** — 食物元素，由 container 按玩法规则生成 6 个

## 关键设计决策
- 为什么 container 走 dyn 而非 stub：数量不固定 / 需要运行时位置计算 / 有状态机
- 为什么 result_panel 走 stub：固定存在于场景，只切 active
```

---

## 针对"Cocos 工程转 Redream"的变体流程

如果输入源是现有 Cocos 工程（`.prefab` / `.scene`），则**跳过录屏分析**，直接：

1. 递归扫描 `assets/prefabs/` 和 `assets/scenes/`，列出所有 prefab 层级
2. 用 `Read` 工具读 `.prefab` JSON，提取 `_children` / `_components` 字段
3. 按 Cocos 的 Prefab 引用关系（`prefab` 组件 = stub、`instantiate` 调用 = dyn）反推 CCB 拆分
4. 仍需输出 skeleton.json + ccb-split-plan.md 供阶段 2 使用

---

## 完成门禁（Done Criteria）

✅ Figma 原型已通过 elsa-analyzer-line 9 层自检
✅ skeleton.json 覆盖所有可见区域，无 "TODO" 占位
✅ ccb-split-plan.md 明确标注每个 CCB 的 stub / dyn 归属
✅ 每个 dyn 单元都有 `children_count` 或运行时规则说明

---

## 下一步

→ `phases/phase2-structure-diagram.md`
