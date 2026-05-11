---
name: structure-diagram-reference
description: >
  Redream-project-gen 管线第 2 阶段参考资料：生成 Redream 项目工程结构图（CCB 卡片风格）。
  作为 Redream-project-gen 的子参考，被 guides/2-generate-structure-diagram.md 引用。
---

# Redream 工程结构图 参考资料

## 交付物说明

**主要交付物：HTML 交互式工程结构图**（取代旧版 Python→PNG 方案）

文件位置：`skills/redream-structure-diagram/FruitTruck_structure.html`

这是一个单文件 HTML 工具，包含：
- 无限画布（缩放/平移）
- CCB 卡片可视化（拖拽移动、属性编辑）
- 连线可视化（支持 stub/dyn 两种类型）
- 交互式连线编辑（从凹槽拖拽新建连线、重连端点）
- 自动排版、导出 HTML

新项目复用方式：直接修改 HTML 文件底部的 `<script type="application/json" id="app-data">` 数据块。

---

## 核心概念

### Redream 与 CocosCreator 的区别

| 概念 | CocosCreator | Redream |
|---|---|---|
| 场景/UI 单元 | Prefab (.prefab) | **CCB** (.red + .rebolt) |
| 脚本逻辑 | TypeScript (.ts) | **Rebolt** (.rebolt，美术逻辑 DSL) |
| 引擎 | CocosCreator 3.x | Redream（基于 Cocos2d-x）|
| 动画 | AnimationClip (.anim) | Timeline（在 .red 文件中定义）|

**Rebolt = 美术可编辑的行为脚本**，暴露三类接口给工程师：
- **自定义函数**：工程师可调用的函数（标注 "程序" / "本地"）
- **程序变量**：工程师读写的变量（带类型：整型/枚举/布尔等）
- **通知工程师**：CCB 内部事件触发时通知外部

---

## JSON 数据结构（app-data）

HTML 底部数据块格式：

```json
{
  "cards": [
    {
      "id": "main",
      "level": 1,
      "x": 80, "y": 100,
      "name": "游戏主界面",
      "desc": "核心界面，管理所有子模块生命周期",
      "timelines": [
        { "name": "常态", "desc": "游戏运行时", "audio": false, "loop": false }
      ],
      "nodes": [
        { "label": "图片_背景", "type": "S" },
        { "label": "HUD区定位区", "type": "La" }
      ],
      "funcs": [
        ["初始化", "程序"],
        ["加载关卡", "程序"]
      ],
      "vars": [
        ["当前关卡", "整型", []],
        ["桶颜色", "枚举", ["红", "橙", "黄"]]
      ],
      "notifs": ["关卡开始", "关卡通过"]
    }
  ],
  "conns": [
    { "fromCard": "main", "fromNode": 1, "toCard": "hud", "type": "stub" },
    { "fromCard": "board", "fromNode": 2, "toCard": "fruit", "type": "dyn" }
  ]
}
```

### 节点类型（type 字段）

| type | 含义 | 颜色 |
|---|---|---|
| S | 图片/Sprite | 蓝 `#60a5fa` |
| Lb | 文本/Label | 橙 `#fb923c` |
| Sp | 动画/Spine | 紫 `#c084fc` |
| N | 定位点（空节点）| 灰 |
| La | 定位区/Layer | 灰 |
| Ly | 定位层 | 灰 |
| Pos | 坐标点 | 黄 `#fde047` |

### 连线类型（type 字段）

| type | 颜色 | 含义 |
|---|---|---|
| stub | 蓝 `#60a5fa` | 父 CCB 持有子 CCB 引用，随父加载 |
| dyn | 橙 `#fb923c` | 运行时代码动态生成 |

---

## 🔴 设计规范（强制，所有项目通用）

### 顶部横条颜色 = 入射连线颜色

| 入射连线类型 | 横条颜色 | 说明 |
|---|---|---|
| stub 嵌套 | `#60a5fa`（蓝）| 与连线颜色相同 |
| dyn 动态创建 | `#fb923c`（橙）| 与连线颜色相同 |
| 无入射（根节点）| `rgba(255,255,255,.72)`（白）| L1 根节点 |

**禁止**按层级（L1/L2/L3/L4）给横条指定颜色，颜色语义是连线关系，不是层级深度。

### Level 标签不使用颜色

Level 标签（L1/L2/L3/L4）统一灰色背景灰色文字，不区分层级颜色。层级信息由横条颜色和位置传达，标签只作数字标识。

### 层级自动计算规则

- **stub 连线**传递层级：`child.level = parent.level + 1`
- **dyn 连线不继承**父级层级：目标 CCB 在 stub-only 图里从 L1 独立计算
- 算法：BFS from 根节点（无 stub 入边）→ 逐层 +1，最大 L4

```javascript
// 例：FruitTruck
// board(L2) --dyn--> fruit → fruit 无 stub 父，所以 fruit = L1
// road(L2)  --stub-> sign  → sign = L3（继承）
// road(L2)  --dyn--> bus   → bus = L1（不继承）
```

---

## 卡片视觉结构

```
┌──────────────────────────────────────┐
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ ← 6px 彩条（=入射连线颜色）
│ ○ 游戏主界面                    [L1] │ ← 左侧凹槽 + 标题 + level tag
│   核心界面，管理所有子模块生命周期      │
├──────────────────────────────────────┤
│ ◷ 时间线                             │ ← 蓝色区块
│ 常态 / 游戏运行时                      │
├──────────────────────────────────────┤
│ ◈ 节点                               │ ← 灰色区块
│ 图片_背景              [图片]    ○    │ ← 右侧端口（凹槽，可拖出连线）
│ HUD区定位区            [定位区]  ○    │
├══════════════════════════════════════╡
│ ⬡ REBOLT 接口                        │ ← 深色底区块
│ 函数  初始化[程序] 加载关卡[程序]       │
│ 变量  当前关卡[整型]                   │
│ 通知  关卡开始 关卡通过                 │
└──────────────────────────────────────┘
```

**左侧凹槽（hdr-slot）**：连线的目标入口，10px 圆形，凹坑样式  
**右侧端口（nd-port）**：连线的起点，每个节点行一个，可从此拖出新连线

---

## 交互功能清单

| 操作 | 说明 |
|---|---|
| 拖拽卡片 | 自由移动位置 |
| 滚轮/双指 | 缩放画布 |
| 拖拽画布空白 | 平移视图 |
| 点击卡片 | 打开属性面板（右侧）|
| 点击线段 | 打开连线属性面板 |
| 选中卡片后拖拽右侧端口 | 从端口拖出新连线 |
| 拖拽线段端点手柄 | 重新连接端点 |
| 整理布局 | DFS 自动排版，相关卡片聚在一起 |
| 导出 | 下载当前状态的 HTML |
| ⌘Z / ⌘⇧Z | 撤销/重做 |
| Del | 删除选中卡片或连线 |
| ⌘0 | 适应窗口 |

### 磁吸凹槽交互

拖拽连线端点时：
- 进入槽 **70px** 范围：槽发蓝光（glow）
- 进入槽 **30px** 范围：磁吸对齐 + 强光晕（snapped）
- 全局只高亮**最近的一个槽**，不多槽同时发光

---

## 新项目制作流程

### 第一步：收集每个 CCB 的数据

```
□ CCB 名称
□ 简短说明（1句话）
□ 时间线：[(名称, 说明, 有无音频, 是否自循环), ...]
□ 节点：[(节点名, 类型), ...]
□ Rebolt 接口：
    □ 自定义函数：[(名称, "程序"/"本地"), ...]
    □ 程序变量：[(名称, 类型, 枚举值列表), ...]
    □ 通知工程师：[名称, ...]
□ 连线关系：哪个节点连到哪个 CCB，类型 stub/dyn
```

### 第二步：编写 JSON 数据

按上述数据结构填写 `cards` 和 `conns` 数组。`x/y` 初始可设为 0（点「整理布局」后自动排版）。`level` 字段可随意填，加载时会根据连线关系自动重算。

### 第三步：替换 HTML 文件数据块

打开 `FruitTruck_structure.html`，找到：
```html
<script type="application/json" id="app-data">
{ ... }
</script>
```
替换 JSON 内容，修改顶部工具栏的项目名称：
```html
<div class="tb-logo"><span class="tb-logo-name">新项目名</span></div>
```

### 第四步：打开 HTML，点「整理布局」

浏览器打开文件，点工具栏「整理布局」按钮，自动 DFS 排版，相关卡片聚在一起。

---

## FruitTruck 参考数据

### CCB 层级结构

```
游戏主界面 (L1)
├── 游戏板区 (L2) --dyn--> 水果单元 (L1, dyn不继承)
├── HUD区 (L2)
├── 公路区 (L2)
│   ├── --dyn--> 卡车_大巴 (L1)
│   ├── --dyn--> 卡车_货车 (L1)
│   └── --stub-> 路牌 (L3)
├── 等待槽 (L2)
├── 颜色桶 (L2)
├── 按钮_道具 (L2)
└── 广告Banner (L2)
水果单元 (L1) --dyn--> 点击引导 (L1)
```

### 完整 HTML 文件

`skills/redream-structure-diagram/FruitTruck_structure.html`

包含完整数据和所有交互功能，可直接在浏览器打开使用。

---

## 旧版方案（Python PNG，已弃用）

`gen_fruittruck_v5.py`：使用 Pillow 生成 PNG 静态图片。

当前不推荐使用，保留仅作参考。HTML 版功能更完整，支持交互编辑和导出。
