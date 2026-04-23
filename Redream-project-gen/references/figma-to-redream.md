# Figma-to-Redream Conversion

Convert a Figma "工程结构说明文档" into a complete Redream project.

## Critical Rules

1. **Never directly read/write `.red` or `.rebolt` files** — always use Redream CLI commands. CLI 操作可能触发关联更新（如数据库同步、redInfos 联动），直接改 JSON/XML 会绕过这些副作用，导致数据不一致。仅在 CLI 明确不支持某操作时才可直接编辑文件，且编辑后必须用 `inspect check` / `rebolt-modify validate` 验证。
2. **Use CLI reference** (`references/cli-inspect.md` / `references/cli-modify.md`) to look up CLI command syntax when unsure.
3. **All names come from Figma** — never invent file names, node names, timeline names, etc.
4. **Only set `reboltName`** — NEVER set `memberVarAssignmentName` or `memberVarAssignmentType`.
5. **Confirm project config** with the developer before creating anything.

---

## Tools Used

| Tool | Purpose |
|---|---|
| **`mcp__figma__get_metadata`** | Get Figma page node tree (frame IDs, names) |
| **`mcp__figma__get_design_context`** | Get detailed card content (text, timelines, rebolt) |
| **`mcp__figma__get_screenshot`** | Optional visual verification |
| **AskUserQuestion** | Confirm project settings with developer |

## CLI Commands Used

All commands require `-p <project.redproj>`. Binary: `build/bin/Redream/Redream.app/Contents/MacOS/Redream`

| Phase | CLI Command | Purpose |
|---|---|---|
| 3 | `modify new-scene --scene <file> --enable-rebolt --no-default-timeline` | Create `.red` scene with Rebolt stub |
| 4 | `modify add-node --scene <file> --parent <path> --type <type> --name <name>` | Add node to scene |
| 4 | `modify set-property --scene <file> --node <path> --property redFile --value <child.red>` | Link REDFile to child scene (property name is `redFile`, NOT `REDFile`) |
| 4 | `modify set-property --scene <file> --node <path> --property reboltName --value <name>` | Set reboltName on node |
| 5 | `modify add-timeline --scene <file> --name <name> --length <s> --fps 30` | Create timeline |
| 6 | `modify set-rebolt-public --scene <file> --value true` | Set sub-red isPublic |
| 6 | `rebolt-modify add-func --rebolt <file> --func-name <name>` | Add custom function |
| 6 | `rebolt-modify add-var --rebolt <file> --var-name <name>` | Add program variable |
| 6 | `rebolt-modify add-block --rebolt <file> --tree <tree> --path <slot> --type <class>` | Add block to rebolt tree |
| 6 | `rebolt-modify set-prop --rebolt <file> --block-id <id> --prop <prop> --value <val>` | Set block property |
| 7 | `inspect scene --scene <file> --summary [--json]` | Verify scene structure |
| 7 | `inspect check -p <proj> [--json]` | Validate project |

---

## Phase 0: Confirm Project Configuration

Use **AskUserQuestion** to collect:
- Design resolution (e.g., 750x1334)
- Export path (e.g., `test/my_project/`)
- Project name / `.redproj` path
- Resource subdirectory (e.g., `ccb/`)

## Phase 1: Parse Figma Design

### Step 1.1 — Extract page structure

Call **`mcp__figma__get_metadata`** with `nodeId` and `fileKey` from the Figma URL.

URL: `https://figma.com/design/:fileKey/:fileName?node-id=:nodeId` → convert `node-id` `-` to `:`

From the XML result, find all template cards:

| Frame name pattern | Type | Output |
|---|---|---|
| `工程结构说明文档_CCB模板` | Project scene | `.red` file |
| `工程结构说明文档_公库CCB模板` | Common/shared scene | `.red` file |
| `工程结构说明文档_Anim模板` | Animation speed curve | `.anim` file (需要创建) |

Each card is wrapped in a parent frame whose `name` = the file name (e.g., `FP_订单模块_订单区.red`).

### Step 1.2 — Extract card details

For each card, call **`mcp__figma__get_design_context`** with its `nodeId`. Extract text from the returned code:

**White section (top):**
- File name (bold title)
- Description (text below title)
- Timeline table: rows of `时间线名称 | 说明 | 音频(有//) | 循环(自循环//)`

**Dark section (bottom) — Rebolt:**
- **自定义函数** (pink dot): function name + caller tag (`程序` or `自本地`)
- **程序变量** (orange dot): variable name + type (e.g., `是否是队首: 是/否`)
- **通知工程师** (yellow dot): see Section 1.3

**Right sidebar — Node Dock:**
- **子节点置入**: child `.red` names → create as REDFile nodes
- **程序创建**: positioning point names → create as CCNode nodes
- **Anim动画**: animation speed curve references → 对应的 .anim 文件需要在 Phase 3 中创建

### Step 1.3 — Understand 通知工程师 entries

Two types:

**Type A — Event notification (plain text)**

Examples: `普通反馈动画播完`, `弹窗退出动画播完`

→ Becomes a `BTNotificationToCoderAction` in the corresponding rebolt function.

**Type B — Node binding (`【绑定节点】` or `【设置程序节点】`)**

Pattern: `【绑定节点】-【<displayName>】-【<reboltName>】`

Examples: `【绑定节点】-【订单气泡定位点】-【订单气泡定位点】`

→ Requires action in BOTH `.red` and `.rebolt`:
1. `.red`: Create CCNode with `<displayName>`, set its `reboltName` to `<reboltName>`
2. `.rebolt`: In `初始化` function, add `BTNotificationNodeToCoderAction` with:
   - `conditionA` = `<displayName>` (notification name)
   - `baseSelect` = reference to the node (`Value = reboltId`, `DisplayName = reboltName`)

### Step 1.4 — Build scene hierarchy

From "子节点置入" entries, determine parent→child relationships. Sort: **leaf scenes first** (no children), then parents.

## Phase 2: Plan and Confirm

Present creation plan to user:
1. File list in creation order
2. Per file: nodes, timelines, rebolt config
3. Wait for confirmation

## Phase 3: Create Project and Scenes

### 3.1 Create project

```bash
mkdir -p <project-dir>/<resource-subdir>
```

Write `.redproj` as XML plist (designSizeWidth, designSizeHeight, publishDirectory, resourcePaths, fileVersion).

**`publishDirectory` 必须设为 `_ccbi`**（不是默认的 `Published`），导出内容存放在 `_ccbi` 文件夹中。

### 3.2 Create scenes (leaves first)

```bash
Redream modify new-scene --scene <subdir>/<file>.red -p <project> --enable-rebolt --no-default-timeline
```

默认对新的 `.red` 场景同时开启 rebolt，并避免生成后续还要手动删除的 `Default Timeline`。只有在修复旧流程/旧文件时，才回退到“先创建，再手动补 `rebolt.isRebolted` / 删除默认时间线”的做法。

### 3.3 修改根节点类型

`new-scene` 默认创建的根节点类型为 `CCNode`。需要根据 .red 文件名判断是否改为 `CCLayer`：

**规则：文件名包含以下关键词时，根节点类型为 `CCLayer`：**
- 弹窗
- 浮层
- 全屏反馈
- 界面

**其他情况根节点保持 `CCNode`。**

**重要：`new-scene` 后必须立即用 python 一次性完成 baseClass + displayName + resolutions 三项替换，不要分步操作，不要用 sed（sed 在此场景容易匹配失败）。**

对每个新建的 .red 文件，在 `new-scene` 后立即执行以下 python 脚本，一次性完成根节点类型（baseClass + displayName）和分辨率设置：

```python
import re

with open(red_file, 'r') as f:
    content = f.read()

if is_cclayer:
    # 1. 替换根节点 baseClass: CCNode → CCLayer（仅第一个）
    content = content.replace(
        '<key>baseClass</key>\n            <string>CCNode</string>',
        '<key>baseClass</key>\n            <string>CCLayer</string>', 1)
    # 2. 替换根节点 displayName: CCNode → CCLayer（仅第一个）
    content = content.replace(
        '<key>displayName</key>\n            <string>CCNode</string>',
        '<key>displayName</key>\n            <string>CCLayer</string>', 1)
    # 3. 替换 resolutions 为 4 条 CCLayer 分辨率
    new_res = CCLAYER_RESOLUTIONS  # 设计1080x2400, 正常1080x2080, 偏宽1560x2080, 偏高1080x2800
else:
    # CCNode: 替换 resolutions 为 1 条 Node分辨率 0x0
    new_res = CCNODE_RESOLUTION  # Node分辨率 width=0 height=0

content = re.sub(
    r'<key>resolutions</key>\s*<array>.*?</array>',
    '<key>resolutions</key>\n            ' + new_res,
    content, flags=re.DOTALL)

with open(red_file, 'w') as f:
    f.write(content)
```

**CCLayer 分辨率（4 条）：**

| 序号 | 名称 | 宽 | 高 |
|------|------|-----|------|
| 1 | 设计分辨率 | 1080 | 2400 |
| 2 | 正常分辨率 | 1080 | 2080 |
| 3 | 偏宽分辨率 | 1560 | 2080 |
| 4 | 偏高分辨率 | 1080 | 2800 |

**CCNode 分辨率（1 条）：**

| 名称 | 宽 | 高 |
|------|-----|------|
| Node分辨率 | 0 | 0 |

### 3.5 Create .anim files

对于 Figma 中 `工程结构说明文档_Anim模板` 类型的卡片，需要创建 .anim 速度曲线文件。

.anim 文件本质上是 .red 格式的 XML plist，固定结构如下：
- **根节点**: `CCNode`（无属性）
- **子节点**: `CCSprite`（displayName = "动画节点"），带 position 关键帧动画
- **分辨率**: 1 条，`0x0`
- **时间线**: 1 条，名称从 Figma 卡片标题提取（去掉文件名前缀，如 `FP_XXX_入场动画速度曲线.anim` → 时间线名 `入场动画速度曲线`）
- **关键帧**: position 属性上 3 个关键帧（time=0, 1.0, 1.667），带贝塞尔 easing（type=35）
- **rebolt**: isRebolted = false

创建方式：直接写入 XML plist 文件（CLI 的 `new-scene` 不支持 .anim 后缀）。使用样例模板，替换时间线名称即可。

**样例模板路径**: 参考任意已有项目中的 .anim 文件结构。

### 3.6 Enable rebolt on all scenes

**Preferred path for new `.red` scenes:** create them with `--enable-rebolt` in Phase 3.2, so `isRebolted` is correct from the start.

**Fallback for legacy scenes / old scripts:** if a `.red` scene was already created without `--enable-rebolt`, repair it with:

```bash
Redream modify scene --scene <subdir>/<file>.red --property rebolt.isRebolted --value true -p <project>
```

`.anim` files remain `isRebolted = false`. Omitting rebolt enablement on a `.red` scene is a common cause of "rebolt not working" in the GUI.

## Phase 4: Build Node Hierarchy

> 节点类型和层级规范详见 `references/red-node-patterns.md`

Figma 交互图只描述逻辑结构，不描述完整的视觉节点树。Phase 4 需要根据 Figma 卡片 **推断** 完整节点树：

### 4.1 子节点置入 → REDFile 嵌入

每个 REDFile 需要包裹在同名 CCNode 中：

```bash
# 先创建定位容器
Redream modify add-node --scene <file>.red --parent <root> --type CCNode --name <child-name> -p <project>
# 再创建 REDFile 子节点
Redream modify add-node --scene <file>.red --parent <root>/<child-name> --type REDFile --name <child-name> -p <project>
Redream modify set-property --scene <file>.red --node <root>/<child-name>/<child-name> --property redFile --value <child>.red -p <project>
```

### 4.2 程序创建 → 定位点节点

程序创建的节点命名建议加 `程序-` 前缀：

```bash
Redream modify add-node --scene <file>.red --parent <root> --type CCNode --name <node-name> --rebolt-name <node-name> -p <project>
```

### 4.3 从程序变量推断 UI 节点

Figma 卡片的「程序变量」列暗示了需要创建的 UI 节点：

| 变量类型 | 需要创建的节点 | 节点类型 |
|---------|--------------|---------|
| 数值/时间/数量 | 显示该变量的标签 | `CCRedLabel` |
| 图集名·plist / 图片名·png | 显示图片的精灵 | `CCSprite` |
| 是/否 | 状态容器（visible 切换） | `CCNode`（分已/未状态组） |

```bash
# 创建标签节点（用于程序变量显示）
Redream modify add-node --scene <file>.red --parent <root>/总组 --type CCRedLabel --name <变量对应的显示名> --rebolt-name <显示名> -p <project>

# 创建精灵节点（用于换图逻辑）
Redream modify add-node --scene <file>.red --parent <root>/总组 --type CCSprite --name <图片节点名> --rebolt-name <图片节点名> -p <project>
```

### 4.4 从通知推断按钮节点

「通知工程师: XXX按钮被点击」暗示需要 `REDNodeButton`：

```bash
Redream modify add-node --scene <file>.red --parent <root>/总组 --type REDNodeButton --name <按钮名> --rebolt-name <按钮名> -p <project>
```

### 4.5 总组节点

每个场景的第一个子节点应该是「总组」CCNode：

```bash
Redream modify add-node --scene <file>.red --parent <root> --type CCNode --name 总组 --index 0 -p <project>
```

### 4.6 Set reboltName on bound nodes

对于 4.1-4.4 中已通过 `--rebolt-name` 设置的节点，无需额外操作。对于需要后续设置的：

```bash
Redream modify set-property --scene <file>.red --node <root>/<node-name> --property reboltName --value <reboltName> -p <project>
```

**NEVER set `memberVarAssignmentName` or `memberVarAssignmentType`.**

## Phase 5: Configure Timelines

From the timeline table in each card:

**Step 1 — 添加自定义时间线：**

```bash
Redream modify add-timeline --scene <subdir>/<file>.red --name "<timeline-name>" --length 1 --fps 30 -p <project>
```

`--chain` 既可以写 sequence ID，也可以直接写时间线名字，或写 `-1` 表示不串联。

**Step 2 — 默认流程无需删除 Default Timeline：** 如果场景在 Phase 3.2 使用了 `--no-default-timeline` 创建，这一步可以直接跳过，也不需要修 `currentSequenceId`。

**仅旧场景修复时使用：** 如果目标场景已经带有 `Default Timeline`（例如旧 CLI 产物或历史文件），再执行删除：

```bash
Redream modify delete-timeline --scene <subdir>/<file>.red --timeline "Default Timeline" -p <project>
```

**Step 3 — 仅旧场景修复时修复 currentSequenceId：** 删除 Default Timeline（id=0）后，文件头部的 `currentSequenceId` 仍可能指向 0，会导致 Redream 无法打开文件。只有在上一步实际删除了默认时间线时，才需要将它改为第一条有效时间线的 id（通常为 1）：

```bash
# 用 sed 将 currentSequenceId 从 0 改为 1
sed -i '' '/<key>currentSequenceId<\/key>/{n;s/<integer>0<\/integer>/<integer>1<\/integer>/;}' <subdir>/<file>.red
```

- `循环 = 自循环` → add `--auto-play true` and chain to self
- `循环 = /` → no auto-play
- `音频 = 有` → note for developer (audio is bound in code)
- Default length 1s — developer adjusts in GUI

## Phase 6: Configure Rebolt

> Block 类型和 JSON 结构详见 `references/rebolt.md` (§3.29 Common Block Patterns)

### 6.1 Set isPublic for parent scenes

For scenes containing REDFile child references:

```bash
Redream modify set-rebolt-public --scene <subdir>/<file>.red --value true -p <project>
```

### 6.2 Add functions and variables

```bash
# Custom functions (from 自定义函数 column)
Redream rebolt-modify add-func --rebolt <subdir>/<file>.rebolt --func-name "<func-name>" -p <project>

# Program variables (from 程序变量 column) — must use P- prefix
Redream rebolt-modify add-var --rebolt <subdir>/<file>.rebolt --var-name "P-<var-name>" -p <project>
```

### 6.3 Add node binding notifications in `初始化`

For each `【绑定节点】`/`【设置程序节点】` entry, add a **`BTNotificationNodeToCoderAction`** in the `初始化` function:

```bash
# 1. Add the block (returns randomID)
Redream rebolt-modify add-block --rebolt <subdir>/<file>.rebolt --tree <treeName> --path stepSlot --type BTNotificationNodeToCoderAction -p <project>

# 2. Set notification name = node's displayName
Redream rebolt-modify set-prop --rebolt <subdir>/<file>.rebolt --block-id <randomID> --prop conditionA --value "<displayName>" -p <project>

# 3. Set node reference via baseSelect. Pass the live reboltId; CLI will sync DisplayName from the paired .red scene.
Redream rebolt-modify set-prop --rebolt <subdir>/<file>.rebolt --block-id <randomID> --prop baseSelect --value "<reboltId>" -p <project>
```

- `<treeName>`: the tree key for the `初始化` function (e.g., `Tree0`). Use `rebolt-modify read` to find it.
- `<randomID>`: returned by `add-block` command.
- 先确认 paired `.red` 里的目标节点已经存在，且 `reboltName` 非空；如果节点元数据还没补齐，先回到 scene 侧修好再写 `.rebolt`
- Multiple bindings chain in stepSlot (linked list).

### 6.4 Add event notifications in functions

For Type A entries (plain text like `动画播完`), add **`BTNotificationToCoderAction`** in the relevant function:

```bash
Redream rebolt-modify add-block --rebolt <subdir>/<file>.rebolt --tree <treeName> --path stepSlot --type BTNotificationToCoderAction -p <project>
Redream rebolt-modify set-prop --rebolt <subdir>/<file>.rebolt --block-id <randomID> --prop conditionA --value "<notification-text>" -p <project>
```

### Notification types summary

| 通知工程师 entry | Action type | conditionA | baseSelect |
|---|---|---|---|
| Plain text (`动画播完`) | `BTNotificationToCoderAction` | notification text | — |
| `【绑定节点】-【A】-【B】` | `BTNotificationNodeToCoderAction` | A (displayName) | `Value = reboltId`, `DisplayName = reboltName` |
| `【设置程序节点】-【A】-【B】` | `BTNotificationNodeToCoderAction` | A (displayName) | `Value = reboltId`, `DisplayName = reboltName` |

### 6.5 Populate function logic (timeline playback + conditions)

After creating functions and notifications, infer and populate the behavior tree logic for each function based on:
1. **Function name ↔ Timeline name** keyword matching
2. **Variables** determine which timeline variant to play
3. **Notifications** fire after timeline playback

#### Step 1 — Infer function→timeline mapping

Match function names to timelines by shared keywords:

| Function | Matching timelines | Condition variable | Logic |
|---|---|---|---|
| `入场` | `动画_入场_突出`, `动画_入场_非突出` | `是否是队首` | if 队首 → 突出, else → 非突出 |
| `等待` | `动画_等待_突出`, `动画_等待_非突出` | `是否是队首` | if 队首 → 突出, else → 非突出 |
| `收集反馈` | `动画_普通反馈`, `动画_完成反馈` | `是否完成订单` | if 完成 → 完成反馈+通知, else → 普通反馈+通知 |
| `离场` | `动画_离场` | — | play directly |

**Present this mapping to the user for confirmation before implementing.**

#### Step 2 — Build the block structure

Each function's logic uses these rebolt block types (refer to `references/rebolt.md`):

**Conditional branch:**
```
BTIFElseControlAction
├─ conditionA (BTBoolSlot) → BTEqualOperatorAction (compare variable value)
├─ sectionA (BTSectionSlot) → action if true
├─ sectionB (BTSectionSlot) → action if false
└─ stepSlot → next action (chain)
```

**Variable comparison (inside BTBoolSlot):**
```
BTEqualOperatorAction
├─ conditionA (BTInputSlot) → BTVariableAction (read variable, VarScope="Scene")
└─ conditionB (BTInputSlot) → StringValue "1" (or target value)
```

**Play timeline:**
```
BTPlayTimeLineAction          — non-blocking, fire-and-forget
BTPlayTimeLineWaitAction      — blocking, waits for timeline to finish
BTPlayTimeLineActionWithCallBack — non-blocking with callback when done
```
- `baseSelect.Value` = **sequenceId as string** (e.g., `"3"`), NOT reboltId
- `baseSelect.DisplayName` = timeline name

**Play timeline then notify (callback pattern):**
```
BTPlayTimeLineActionWithCallBack
├─ baseSelect → { Value: "<sequenceId>", DisplayName: "<timeline-name>" }
├─ CallBackInfo → { Value: "<callbackTreeRandomID>" }
└─ stepSlot → next action

BTCallBackFuncAction (separate tree entry)
└─ stepSlot → BTNotificationToCoderAction (conditionA = "动画播完")
```

#### Step 3 — CLI commands to build the logic

```bash
# Add conditional branch
Redream rebolt-modify add-block --rebolt <file> --tree <tree> --path stepSlot --type BTIFElseControlAction -p <project>

# Add variable comparison inside the condition
Redream rebolt-modify add-block --rebolt <file> --tree <tree> --path <ifBlock>/conditionA --type BTEqualOperatorAction -p <project>

# Add variable reader inside comparison
Redream rebolt-modify add-block --rebolt <file> --tree <tree> --path <equalBlock>/conditionA --type BTVariableAction -p <project>
Redream rebolt-modify set-prop --rebolt <file> --block-id <varBlockId> --prop titleLabel --value "<variable-name>" -p <project>
Redream rebolt-modify set-prop --rebolt <file> --block-id <varBlockId> --prop VarScope --value "Scene" -p <project>

# Set comparison target value
Redream rebolt-modify set-prop --rebolt <file> --block-id <equalBlockId> --prop conditionB --value "1" -p <project>

# Add play timeline in sectionA (true branch)
Redream rebolt-modify add-block --rebolt <file> --tree <tree> --path <ifBlock>/sectionA --type BTPlayTimeLineAction -p <project>
Redream rebolt-modify set-prop --rebolt <file> --block-id <playBlockId> --prop baseSelect --value '{"Value":"<seqId>","DisplayName":"<timeline>","Type":"Action"}' -p <project>

# Add play timeline in sectionB (false branch)
Redream rebolt-modify add-block --rebolt <file> --tree <tree> --path <ifBlock>/sectionB --type BTPlayTimeLineAction -p <project>
```

#### Step 4 — Example: `收集反馈` function with notification after playback

```
收集反馈 (BTCustomFuncHeadAction)
└─ stepSlot → BTIFElseControlAction
                ├─ conditionA → BTEqualOperatorAction
                │                ├─ conditionA → BTVariableAction (是否完成订单)
                │                └─ conditionB → "1"
                ├─ sectionA → BTPlayTimeLineActionWithCallBack (动画_完成反馈)
                │              └─ callback → BTNotificationToCoderAction (完成反馈动画播完)
                └─ sectionB → BTPlayTimeLineActionWithCallBack (动画_普通反馈)
                               └─ callback → BTNotificationToCoderAction (普通反馈动画播完)
```

## Phase 7: Verify

```bash
# Check each scene structure
Redream inspect scene <subdir>/<file>.red --summary -p <project>

# Validate project integrity
Redream inspect check -p <project>
```

Prompt user to open in Redream GUI for visual confirmation.

## Error Handling

- CLI command fails → check error message, adjust parameters
- Scene can't be parsed → verify XML plist format (not binary plist)
- Unsure about a change → use `--dry-run` first
- Need CLI details → refer to `references/cli-inspect.md` / `references/cli-modify.md`

## Calibration Notes (verified corrections)

1. **Property name is `redFile`** (lowercase r), NOT `REDFile`. The node type is `REDFile`, but the property name is `redFile`.
2. **REDFile value path is relative to resource dir, without `ccb/` prefix.** Example: if scene is at `ccb/A.red` and child is at `ccb/B.red`, set `redFile` to `B.red` (not `ccb/B.red`).
3. **CLI binary path:** Primary path is `build/bin/Redream/Redream.app/Contents/MacOS/Redream` (source builds). Fallback: `/Applications/Redream.app/Contents/MacOS/Redream` (installed .app bundle).
4. **Figma 流程优先使用 `new-scene --no-default-timeline`。** 这样新场景不会生成 `Default Timeline`，也无需额外修 `currentSequenceId`。只有旧场景或旧 CLI 产物已经带默认时间线时，才执行 `modify delete-timeline --timeline "Default Timeline"` 并修复 `currentSequenceId`。
5. **`new-scene` 默认继承项目 `designSize` 作为初始分辨率。** 但 Figma 流程仍必须在创建场景后按目标根节点类型重写 `resolutions`：`CCLayer` 要替换为 4 条分辨率，`CCNode` 要替换为 `0x0` 的 Node 分辨率。使用 Python 脚本一次性完成 baseClass + displayName + resolutions 三项替换（见 Phase 3.3），不要用 sed（sed 在此场景容易匹配失败）。
6. **根节点类型按文件名判断。** 文件名包含「弹窗」「浮层」「全屏反馈」「界面」时根节点为 `CCLayer`，其他为 `CCNode`（默认）。
7. **Figma 流程优先使用 `new-scene --enable-rebolt`。** 这样新建 `.red` 场景会直接写入 `isRebolted = true`。只有修复旧场景或兼容旧脚本时，才补执行：
   ```bash
   Redream modify scene --scene <file>.red --property rebolt.isRebolted --value true -p <project>
   ```
8. **`baseSelect.Value` 必须使用 live `reboltId`（自动生成的随机 ID），不能使用 `reboltName`（别名）。** 获取方法：优先用 CLI 读取 scene/node 当前状态，或直接依赖 `rebolt-modify` 的 paired `.red` 校验链路；不要手工解析 `.red` 原文件，也不要根据 `reboltName` 猜 selector。
9. **`rebolt-modify add-block` 输出格式为 `Added <Type> (id: <randomID>) to <path>`。** 解析 randomID 时使用正则 `\(id:\s*([A-Za-z0-9_-]+)\)`，不要尝试 JSON 解析（默认非 JSON 格式，需加 `--json` 才返回 JSON）。
10. **`add-block` 后必须立即验证属性设置成功。** `add-block` 创建的通知 block 带默认 `conditionA = "通知名"`。如果后续属性设置失败，会残留占位 block，导致重复通知。必须在 `add-block` 后立即验证成功，否则用 `remove-block` 回滚。

## Appendix: Figma Card → .red Node Mapping

Figma 工程结构说明文档中的每个区域对应的 .red 构建规则：

| Figma 区域 | .red 构建动作 |
|-----------|--------------|
| **场景名 + 等级标签(L1/L2)** | 确定文件名 + 根节点类型（CCLayer/CCNode） |
| **参考截图** | 确定节点层级和视觉元素 |
| **时间线表** | `add-timeline` |
| **子节点置入** | CCNode → REDFile 嵌入（需要完整的节点树） |
| **程序创建** | CCNode 定位点，命名加 `程序-` 前缀 |
| **自定义函数** | rebolt `add-func` |
| **程序变量** | rebolt `add-var --var-name "P-<名称>"` |
| **通知工程师** | rebolt BTNotificationToCoderAction / BTNotificationNodeToCoderAction |

### Figma 中看不到但必须创建的节点

Figma 交互图只描述**逻辑结构**，不描述视觉节点树。以下节点需要根据功能推断创建：

1. **Label 节点** — 每个程序变量如果类型是「数值」「时间」「数量」，需要创建 CCRedLabel 来显示
2. **Button 节点** — 每个「通知工程师: XXX按钮被点击」暗示需要 REDNodeButton
3. **Sprite 节点** — 程序变量类型为「图集名·plist」「图片名·png」暗示需要 CCSprite
4. **状态容器** — 场景有多个「常态_XXX」时间线时，可能需要 visible 切换的 CCNode 容器
5. **总组** — 每个场景的第一个子节点应该是「总组」CCNode
6. **底板/背景** — 可视化组件通常有 CCScale9Sprite 底板
