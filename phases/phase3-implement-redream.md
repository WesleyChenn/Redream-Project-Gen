# 阶段 3：Redream CLI 落地

> **触发时机**：用户要求"生成 Redream 工程"、"落地 .red/.rebolt"、"写 rebolt 行为树"、"发布 Redream 包"时加载此文件。

---

## 目标

基于阶段 2 的工程结构图 HTML（含 `app-data` JSON），用 Redream CLI 生成完整可运行的 `.red` + `.rebolt` + 资源工程。

**产出物**（归档到 `~/JarvisPark/output/ada/<project>/03-project/`）：
- `.redproj` 项目文件
- 所有 `.red` 场景文件（对应阶段 2 的每个卡片）
- 所有 `.rebolt` 行为树文件
- `res/` 资源目录（图片、字体、音效、Spine）

---

## 执行流程

**CLI First 原则**：一律先用 CLI，CLI 做不到再读源文件回退。

### Step 0 — 读取阶段 2 产出

```python
import json, re
html = open('<path>/02-structure-diagram/<Project>_structure.html').read()
data = json.loads(re.search(r'<script type="application/json" id="app-data">(.*?)</script>', html, re.S).group(1))
# data['cards'] — 每张卡片对应一个 .red
# data['conns'] — 连线告诉我们 stub vs dyn 关系
```

### Step 1 — 初始化 Redream 项目

CLI 二进制：`/Applications/Redream.app/Contents/MacOS/Redream`

读 `references/project-structure.md` 了解文件夹命名约定（通常 `ccb/` 放源文件、`res/` 放资源）。
读 `references/workflow-config.md` 了解项目创建询问白名单。

```bash
REDREAM=/Applications/Redream.app/Contents/MacOS/Redream
mkdir -p ~/JarvisPark/output/ada/<project>/03-project/<Project>/{ccb,res}
cd ~/JarvisPark/output/ada/<project>/03-project/<Project>
# 新建 .redproj 可通过 Redream GUI 或沿用模板
```

### Step 2 — 为每张卡片生成 `.red` 场景

按 `data['cards']` 遍历，每个 card 创建一个 `.red`（文件名通常 PascalCase，如 `main` → `Main.red`；命名严格按 `references/naming-standards.md`）。

**关键参考**：
- `references/redream.md` — `.red` XML 完整格式
- `references/redream-handbook.md` — 节点类型/快捷键/文件结构
- `references/cocosbase.md` — 坐标系 / 锚点 / 单位（Redream 基于 Cocos2d-x，坐标以左下为原点）
- `references/building-standards.md` — 分辨率 / 总组 / 节点 / 时间线 / 背景组规范
- `references/node-tree-standards.md` — 节点树层级规范

对每个 card 内的 nodes 数组：
- `La`（LayerArea）→ 在 `.red` 中生成 Layer 节点，并预留子节点位置
- `S`/`Lb`/`Sp`/`N` → 按对应节点类型生成

### Step 3 — stub 连线：写 REDFile 引用

对 `data['conns']` 中 `type: "stub"` 的连线：

```bash
# 在父 .red 的对应 fromNode 位置添加 REDFile 组件，指向子 .red
$REDREAM -p <project>.redproj modify add-node \
  --scene Main.red \
  --parent "HUD区定位区" \
  --type REDFile \
  --name HUD \
  --property src=HUD.red
```

具体 add-node 用法参考 `references/cli-modify.md`。

### Step 4 — dyn 连线：在父 .rebolt 中写 instantiate 行为树

对 `data['conns']` 中 `type: "dyn"` 的连线：

```bash
# 在父场景的 .rebolt 行为树中添加"运行时生成子 CCB"的积木块
$REDREAM -p <project>.redproj rebolt-modify add-block \
  --rebolt Board.rebolt \
  --tree onLoad \
  --path "spawn_containers" \
  --type InstantiateRed \
  --props '{"src":"Container.red","count":5,"parent":"容器生成层"}'
```

**关键参考**：
- `references/rebolt.md` — `.rebolt` JSON schema
- `references/rebolt-handbook.md` — 积木块分类（事件/控制/时间线/变量/运算/函数/UI/动画）
- `references/rebolt-standards.md` — Rebolt 制作规范（换图/函数/嵌套/按钮/测试）
- `references/project-patterns.md` — 标准工程模式库（弹窗结构/节点命名/实际案例）

### Step 5 — 资源装填

- 图片：按 `references/image-resource-standards.md` + `references/ui-production-standards.md`
- 字体：按 `references/font-standards.md`
- 音效：按 `references/sound-standards.md`（分类/视觉事件/堆叠）
- 多语言：按 `references/multilang-standards.md`
- Figma 原图批量导出：用 `tools/figma_auto_export.py`（参考 `references/figma-auto-export.md`）

### Step 6 — 动画与时间线

参考 `references/redream-handbook.md` 动画章节 + `references/analyze-animation-prototype.md`（如果阶段 1 标注了动画原型）。

CLI 创建时间线：
```bash
$REDREAM -p <project>.redproj modify add-timeline \
  --scene Main.red --name "intro" --length 2 --fps 30
```

### Step 7 — 验证

```bash
# 结构完整性检查
$REDREAM -p <project>.redproj inspect check

# 场景节点树确认
$REDREAM -p <project>.redproj inspect scene Main.red --properties

# Rebolt 行为树确认
$REDREAM -p <project>.redproj rebolt-modify read --rebolt Main.rebolt
```

### Step 8 — 发布

```bash
# 发布为 CCB + Rebolt BSON + ZIP
$REDREAM -p <project>.redproj publish
```

### Step 9 — 商店宣传图（若需要）

按 `references/store-assets-standards.md` 出安卓/苹果/内购尺寸图。

---

## Figma → Redream 专用路径

如果用户直接从 Figma 转（跳过阶段 1 的录屏分析），读 `references/figma-to-redream.md` 获取完整 Figma → Redream 自动化流程（含 `figma_auto_export.py` 工具使用）。

图层命名必须先按 `references/figma-naming-standards.md` 规范化（类型前缀 + 元素分类 + 布局约束）。

---

## 完成门禁（Done Criteria）

✅ `inspect check` 通过，无 broken reference
✅ 所有 stub 子 CCB 在父场景中可见（GUI 预览或 `inspect scene`）
✅ 所有 dyn 单元在 rebolt 中有 instantiate 逻辑
✅ 资源路径可解析，无缺失
✅ `publish` 成功产出 .redream 包
✅ 在 Redream GUI / 模拟器中运行，核心玩法可走通

---

## 回流到阶段 2

如果落地过程中发现结构设计不合理（例如某个原本 stub 的子 CCB 实际上需要动态数量 → 应改为 dyn），**不要强行在 Redream 里 hack**，回到阶段 2 修改 HTML 结构图，然后重新执行阶段 3 的对应 Step。

---

## 每轮反思（全局 CLAUDE.md 强制）

每次用户反馈后，主动执行：
1. 修了什么
2. 根因是什么（遗漏规则？理解偏差？未验证假设？）
3. 是否可沉淀到 `~/.claude/projects/-Users-liuying/memory/_global/feedback_*.md`
