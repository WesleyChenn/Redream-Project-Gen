# 阶段 2：工程结构图

> **触发时机**：用户要求"出工程结构图"、"画 CCB 层级图"、"画 .red 场景结构图"时加载此文件。

---

## 目标

基于阶段 1 的 `skeleton.json` + `ccb-split-plan.md`，生成 HTML 交互式 CCB 工程结构图，作为阶段 3 CLI 落地的"蓝图"。

**产出物**（归档到 `~/JarvisPark/output/ada/<project>/02-structure-diagram/`）：
1. `<Project>_structure.html` — 单文件 HTML（含画布、卡片、连线、app-data JSON）

---

## 执行流程

主手册：`references/structure-diagram-reference.md`（含完整规范：卡片 schema、连线类型、顶部横条颜色规则、level 自动计算等）

辅助模板（直接复制修改）：
- `templates/BeadsOut_structure.html` — 简洁示例
- `templates/FruitTruck_structure.html` — 含时间线/函数/变量的完整示例

### Step 1 — 选择模板并复制

```bash
cp templates/BeadsOut_structure.html ~/JarvisPark/output/ada/<project>/02-structure-diagram/<Project>_structure.html
```

### Step 2 — 修改 3 处固定标识

Edit 新文件，替换：
1. `<title>...</title>` → `<title><Project> 工程结构图</title>`
2. `<span class="tb-logo-name">...</span>` → `<span class="tb-logo-name"><Project></span>`
3. 下载按钮脚本里的 `a.download='...'` → `a.download='<Project>_structure.html'`

### Step 3 — 替换 `app-data` JSON 数据块

找到 `<script type="application/json" id="app-data">` 块（通常在 HTML 中段），替换为基于 `ccb-split-plan.md` 生成的数据。

**完整字段示例**（参考 `templates/FruitTruck_structure.html`）：

```json
{
  "cards": [
    {
      "id": "main", "level": 1, "x": 80, "y": 600,
      "name": "游戏主界面",
      "desc": "核心界面，管理全局状态、加载关卡数据、协调所有子模块生命周期",
      "timelines": [
        {"name": "常态", "desc": "界面正常运行时", "audio": false, "loop": false},
        {"name": "动画_关卡开始", "desc": "关卡开始入场动画", "audio": true, "loop": false}
      ],
      "nodes": [
        {"label": "图片_背景", "type": "S"},
        {"label": "HUD区定位区", "type": "La"},
        {"label": "棋盘区定位区", "type": "La"},
        {"label": "结果面板定位层", "type": "Ly"}
      ],
      "funcs": [["初始化关卡", "程序"], ["通关结算", "程序"]],
      "vars": [["当前关卡", "整型", []], ["游戏状态", "枚举", ["准备", "进行中", "通关", "失败"]]],
      "notifs": ["游戏开始", "关卡通关"]
    }
  ],
  "conns": [
    {"fromCard": "main", "fromNode": 2, "toCard": "hud", "type": "stub"},
    {"fromCard": "board", "fromNode": 3, "toCard": "container", "type": "dyn"}
  ]
}
```

> **`fromNode` 是 0-indexed 节点序号**（不是 name 字符串），按 `nodes[]` 数组顺序计数，从 0 起。
>
> ⚠️ 这条与 HTML renderer 的 `forEach(nd, ni=0,1,...)` 对齐：端口 id 为 `pa-${cardId}-${ni}`。若某条 conn 指向不存在的 ni（例如 fromNode=len(nodes) 越界），**整条线不会渲染也不报错** —— 写完必须用浏览器目视 + Step 8 自检双重校验。

### Step 4 — 节点类型速查（`type` 字段）

| type | 含义 | 颜色 | 何时使用 |
|------|------|------|---------|
| `S`  | Sprite（图像） | 蓝 | 所有静态/动态贴图 |
| `Lb` | Label（文本） | 橙 | 数字、文案、计数 |
| `Sp` | Spine 动画 | 紫 | 庆祝特效、循环装饰、复杂角色 |
| `N`  | 定位点（空 Node） | 灰 | 按钮锚点、子 CCB 挂载锚点 |
| `La` | 定位区（Layer） | 灰空心 | 容器节点（限定区域） |
| `Ly` | 定位层（无形状层） | 灰空心 | 全屏覆盖层（结果面板/弹窗） |
| `Pos`| 坐标点 | 黄 | 飞行起终点、引导坐标 |
| `Gp` | 群组（子元素聚合） | 淡紫粗体 | 表示 "xx组" 的父节点，后续子节点必须带 `indent:1` |

> **Redream 节点类型语义** = Cocos 节点 + Redream 自有命名约定。`L1` 根场景的所有子模块挂载点都用 `La`，全屏蒙层用 `Ly`，飞行轨迹起终点用 `Pos`。

### 子节点缩进（group hierarchy）

对 `Gp` 群组下的子节点，在 node 对象里加 `"indent": 1`，renderer 会自动绘制左侧紫色竖线 + 16px 缩进。约束：
- `indent` 子节点前必须紧跟 `Gp` 父节点（脚本自检会断言）
- 目前只支持 1 层缩进（深度限制，避免结构图可读性下降）

```json
"nodes": [
  {"label": "计数组", "type": "Gp"},
  {"label": "图片_徽章底板", "type": "S",  "indent": 1},
  {"label": "文本_当前数",   "type": "Lb", "indent": 1},
  {"label": "进度条组",     "type": "Gp"},
  {"label": "图片_进度槽",   "type": "S",  "indent": 1}
]
```

---

## ⚠️ 三条铁律（来自 cocos-project-gen，**Redream 同样适用**）

### 铁律一：每个 CCB 至少一条时间线

- 有明确状态 → 为每个状态创建对应时间线（`常态_空` / `常态_满` / `动画_xxx`）
- 有动画 → 创建对应动画时间线
- 以上都没有 → 添加一条 `常态` 时间线（`audio:false, loop:false`）

```json
// ❌ 错误：节点丰富但无时间线
{"id": "tip", "nodes": [...], "timelines": []}

// ✅ 正确：至少一条 常态
{"id": "tip", "nodes": [...], "timelines": [{"name":"常态","desc":"提示静态展示","audio":false,"loop":false}]}
```

### 铁律二：可移动 CCB 必须有 `常态` + `动画_移动`

凡是会被 Rebolt 行为树驱动移动的 CCB（拖拽元素、飞行单位、可拾取道具等），时间线必须**同时**包含：
- `常态`（`loop:false`）— 静止默认状态
- `动画_移动`（`loop:false`）— 移动过程的属性变化（起终点由 Rebolt 决定，时间线只控过渡属性）

> 例：`food_skewer.red` 被拖拽 → timelines 必含 `常态` + `动画_移动`，可再加 `动画_选中` `动画_消除`。

### 铁律三：布局防重叠（自动布局算法）

```
HDR_H = 62  # 卡片头部高（含 level 徽标 + name + desc）
SEC_H = 24  # 段头高（"时间线"/"节点"/"函数"分隔条）
ROW_H = 34  # 单行高（每条 timeline / node / func / var）
GAP   = 24  # 同列卡片间距
```

`card_h = HDR + Σ(SEC + count × ROW + 8)`

同列卡片必须用累计高度+GAP 排布，**不能任意写 y**，否则会重叠。

---

## ⚠️ 命名规范

### 禁止括号占位

❌ `烧烤架.red（×6）` / `槽位区（6格）` / `food_element（dyn）`
✅ `烧烤架.red` + 在 `desc` 字段写"6 个，由 board dyn 实例化"

> 数量、约束、说明全部走 `desc` 字段，不污染 `name`。

### 节点命名前缀（与 Redream 节点树规范一致）

| 前缀 | 用途 |
|------|------|
| `图片_xxx` | Sprite 节点 |
| `文本_xxx` | Label 节点 |
| `Spine_xxx` | Spine 动画节点 |
| `按钮_xxx定位点` | 按钮挂载点（不是按钮本体，本体是 stub 进来的） |
| `xxx区定位区` | LayerArea 容器 |
| `xxx定位层` | Layer 全屏层 |
| `xxx生成层` / `xxx生成区` | dyn instantiate 落地容器 |

### 时间线命名

| 模式 | 示例 |
|------|------|
| `常态` | 默认状态 |
| `常态_<状态名>` | 多个常态，如 `常态_空` `常态_满` |
| `动画_<动作名>` | 单次播放，如 `动画_弹出` `动画_消除` |
| `常态_<循环>` | 循环常态，如 `常态_呼吸` (`loop:true`) |

---

## ⚠️ 卡片布局规则（左→右按依赖层次）

```
COL1 (x=80)    根 CCB（main）
COL2 (x=760)   stub 子 CCB（按 main.nodes 中定位区顺序从上到下）
COL3 (x=1440)  dyn 实例化 CCB（与触发它的 dyn 锚点上下对齐）
COL4 (x=2120)  更深层 dyn / 嵌套
```

不让连线穿越其他卡片。同列卡片按 GAP 累计 y，COL3+ 卡片可与父锚点 y 偏移对齐。

---

## ⚠️ 一对多连接必须逐一显式表达

当父 CCB 有 N 个定位点都指向同一子 CCB 时，每个定位点都要画一条独立连线，**禁止只连第一个**。

例：result_panel 同时承载"通关"和"失败"两种弹窗 → 应拆成 `result_win.red` 和 `result_lose.red` 两个独立卡片，不要塞进同一个。

---

## Step 5 — 连线类型规则

| type | 语义 | 颜色 | 使用场景 |
|-----|-----|-----|---------|
| `stub` | 嵌入式子 CCB（REDFile 组件引用） | 蓝（白实线） | 固定布局块（HUD / 结果面板 / 广告横幅 / 引导层 / 道具栏） |
| `dyn` | 运行时动态生成（rebolt instantiate） | 橙（虚线） | 数量不固定的单元（关卡格子 / 消除元素 / 道具按钮 / 引导手指） |
| `ref` | 坐标引用（不是创建父级） | 灰（虚线） | 读取目标节点的世界坐标作为位置输入，但实际视觉父级是别处（典型：教学手指读圆点坐标但挂在引导层；反馈特效读定位点坐标但挂在特效层） |

**重要**：阶段 1 的 `ccb-split-plan.md` 已经做了 stub vs dyn 的决策，这里直接映射即可。

### dyn vs ref 的判据

同一子卡片常常需要**两条**入线：

1. `dyn` / `stub`：**视觉父级**（运行时 parent，决定层级叠放和销毁生命周期）— 每个子卡片**有且只有一条** dyn/stub 入线。
2. `ref`：**坐标源**（只读世界坐标作为位置输入）— 可以**多条** ref 入线（如数字标签既读圆点位置、也可能读另一个锚点）。

判据问自己："这条线指向的节点，是运行时的 parent 还是仅仅提供坐标？"
- parent → dyn 或 stub
- 仅坐标 → ref（**ref 不计入视觉父级**，也不改变 incomingType 横条颜色）

---

## Step 6 — Level 自动计算

不要手动写 `level`。脚本读取 stub 连线后 BFS：
- 没有 stub 入线的卡片 = L1
- stub 子孙 = L(parent+1)
- dyn 子孙：参考 `templates/FruitTruck_structure.html` 中 `fruit` (L3) `bus` (L3) `guide` (L4) 的实际写法 — **dyn 也按视觉层级递增 level**，而不是从 1 重新计算（这与早期文档不同，以模板实现为准）。

### Step 7 — 生成器中应用布局规则 R1–R6（必读）

**先加载** `lessons/lesson_structure_diagram_layout.md`，按 R1–R6 在生成器里算好 x/y，再写入 HTML。重点记忆：

- R1: x = COL{level}（step=680px，COL1=80, COL2=760, COL3=1440…）
- R2: 同列纵序按父级 `nodes[]` 索引
- R3: stub/dyn 主干不交叉，ref 可交叉
- R4: L1 Y 居中于 L2 跨度
- R5: 叶节点 Y 对齐 ref 源加权中点
- **R6: ref 源在同列 → 目标卡右移一列（防反折，最易遗漏）**

然后浏览器打开 HTML 肉眼复核：
- 拖动微调（一般不需要）
- 检查连线是否 L→R 单向无回折
- 点右上角 "导出" 保存 x/y 坐标到新 HTML

### Step 8 — JSON 自检

读取 HTML 中段的 `<script id="app-data">`，用 Python 验证：

```python
import json, re
with open('<Project>_structure.html') as f:
    html = f.read()
m = re.search(r'<script type="application/json" id="app-data">(.*?)</script>', html, re.S)
data = json.loads(m.group(1))

card_ids = {c['id'] for c in data['cards']}

# 1. 连线引用的 card 都存在
for conn in data['conns']:
    assert conn['fromCard'] in card_ids, f"missing fromCard: {conn['fromCard']}"
    assert conn['toCard'] in card_ids, f"missing toCard: {conn['toCard']}"

# 2. 每张卡片必有时间线（铁律一）
for c in data['cards']:
    assert c['timelines'], f"card {c['id']} 缺时间线，违反铁律一"

# 3. fromNode 序号合法（0-indexed，与 HTML renderer 的 forEach 索引一致）
for conn in data['conns']:
    fc = next(c for c in data['cards'] if c['id'] == conn['fromCard'])
    assert 0 <= conn['fromNode'] < len(fc['nodes']), \
        f"conn fromNode {conn['fromNode']} 越界 on {conn['fromCard']} (valid: 0..{len(fc['nodes'])-1})"

# 4. indent 子节点的父必须是 Gp 群组（父子关系校验）
for c in data['cards']:
    for i, nd in enumerate(c['nodes']):
        if nd.get('indent', 0) > 0:
            assert i > 0, f"card {c['id']} node[{i}] 带 indent 但无前置父节点"
            j = i - 1
            while j >= 0 and c['nodes'][j].get('indent', 0) > 0:
                j -= 1
            parent = c['nodes'][j]
            assert parent['type'] == 'Gp', \
                f"card {c['id']} node[{i}] 的父 {parent['label']} 不是 Gp 群组"

# 5. 连线 type 合法（stub / dyn / ref）
for conn in data['conns']:
    assert conn['type'] in ('stub', 'dyn', 'ref'), \
        f"未知连线 type: {conn['type']}"

# 6. 除 L1 外，每张卡片必须有且只有一个"视觉父级"入线 (dyn + stub 合计=1)
#    ref 入线不受限（可 0 可多），因为它只是坐标源
for c in data['cards']:
    if c.get('level', 1) == 1: continue
    parent_in = [cn for cn in data['conns']
                 if cn['toCard'] == c['id'] and cn['type'] in ('stub', 'dyn')]
    assert len(parent_in) == 1, \
        f"card {c['id']} 视觉父级入线={len(parent_in)}，应为 1 (stub+dyn 合计)"

print(f"OK | cards: {len(data['cards'])} conns: {len(data['conns'])}")
```

可移动 CCB 的铁律二需人工 review（脚本难判断"哪个 CCB 会被移动"）。

---

## 完成门禁（Done Criteria）

✅ 所有 L1/L2 CCB 都有对应卡片
✅ 所有 dyn 单元（动态生成的单元）都有卡片
✅ 每张卡片都有 ≥1 条时间线（**铁律一**）
✅ 可移动 CCB 都有 `常态` + `动画_移动`（**铁律二**）
✅ 所有命名无括号，数量/约束写在 `desc`
✅ 连线无孤儿（fromCard/toCard/fromNode 都合法）
✅ 卡片在画布上无重叠（同列按 GAP 累计 y）
✅ 一对多连线全部显式，无遗漏
✅ HTML 在浏览器中可拖拽、可导出、可缩放
✅ JSON 自检脚本通过

---

## 与 cocos-project-gen 的差异

本阶段的卡片/节点/时间线规范**直接复用** cocos-project-gen 的 phase1-structure-diagram，但有以下 Redream 特化点：

| 项 | Cocos 写法 | Redream 写法 |
|----|-----------|--------------|
| 时间线类型 | `("AS", "name")` / `("AL", "name")` 元组 | `{"name", "loop": bool}` 对象（loop=true ≈ AL） |
| 节点类型 | S/Lb/N/Ct/La/Ar/BF/Sp/AS/AL/S9 | S/Lb/Sp/N/La/Ly/Pos（Redream 不区分 Ar/BF/S9） |
| 程序控件 | `Ct` 控制器 + `</>` 徽标 | 行为树在 `.rebolt` 文件中，结构图只标 `funcs`/`vars`/`notifs` 三个段 |
| 容器节点 | LayerArea(`La`) | LayerArea(`La`) + Layer 全屏(`Ly`) |

**Rebolt 部分（funcs/vars/notifs/行为树 schema）保持 Redream 自有规范**，参考 `references/rebolt.md` `references/rebolt-handbook.md` `references/rebolt-standards.md`。

---

## 下一步

→ `phases/phase3-implement-redream.md`
