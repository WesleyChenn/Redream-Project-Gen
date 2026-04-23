---
name: Redream-project-gen
description: 游戏录屏/截图/PRD/Figma/Cocos 工程 → Redream 可运行工程（.red + .rebolt + 资源）端到端生成。当用户要求"从录屏/截图生成 Redream 工程"、"复刻游戏为 Redream 项目"、"Cocos 项目转 Redream"、"Figma 转 .red/.rebolt"、"给 Redream 项目出工程结构图"、"分析游戏 UI 并落地 Redream"时激活此 skill。涵盖三阶段管线：游戏分析（Figma 低保真原型 + 骨架清单）、工程结构图（HTML CCB 卡片图）、CLI 落地（.red/.rebolt/资源/动画/发布）。
---

> **2026-04-22 更新**：同步引擎组 `ai_dev_skill` commit `9a8b53f`（2026-04-09 基线）。CLI 版本锚定 **Redream CLI 1.3.4**（DMG `Redream-9.6.0.0-alpha`）。核心规范已与引擎组权威版对齐。
>
> **2026-04-21**：CLI 表面、selector 硬规则、new-scene 工作流、rebolt 校验语义升级。详见 `references/test-results-rebolt-commands.md`。

## 目录

### 核心路由（必读）

| 文件 | 内容 | 何时加载 |
|------|------|---------|
| **SKILL.md**（本文件） | 阶段路由 + 通用铁律 + 工程约定 | 始终 |
| **phases/phase1-analyze-game.md** | 游戏分析（录屏 → Figma 原型 + skeleton.json + ccb-split-plan.md） | 用户要求"分析游戏/出低保真原型" |
| **phases/phase2-structure-diagram.md** | HTML 工程结构图（CCB 卡片 + stub/dyn 连线） | 用户要求"出结构图/画 CCB 层级图" |
| **phases/phase3-implement-redream.md** | Redream CLI 落地（.red/.rebolt/资源/发布） | 用户要求"生成 .red / 落地 Redream 工程 / 发布" |

### CLI 权威文档（阶段 3 必查）

| 文件 | 内容 |
|------|------|
| **references/cli-inspect.md** | 所有 inspect / rebolt / rebolt-modify 只读命令（172 行） |
| **references/cli-modify.md** | 所有 modify / rebolt-modify 写入命令（755 行；含属性值格式表、paired .red 合同） |
| **references/test-results-rebolt-commands.md** | CLI 表面审计基线（当记忆/旧文档与当前 binary 冲突时的仲裁源） |

### 文件格式权威（查格式/字段）

| 文件 | 内容 |
|------|------|
| **references/redream.md** | .red XML plist 完整字段定义 + 关键帧格式 |
| **references/rebolt.md** | .rebolt JSON 行为树完整格式 + §3.29 六个常用 block 组合模式 |
| **references/cocosbase.md** | 坐标系/单位/锚点基础 |
| **references/red-node-patterns.md** | 节点类型选择规则 + 骨架模式（CCLayer/CCNode/弹窗）+ 按钮 B1-B4 + Label/REDFile 规范 |

### 生产规范与红线

| 文件 | 内容 |
|------|------|
| **references/rebolt-standards.md** | Rebolt 必要函数、测试逻辑、selector CLI 硬规则、通知工程师、按钮逻辑 |
| **references/project-standards.md** | 项目目录/CCB 命名/节点命名/reboltName/工程搭建（官方整合版） |
| **references/asset-standards.md** | 图片 / 字体 / 音效 / 商店图 / 美术管线（官方整合版，替代 font/image/sound/ui/store-standards） |
| **references/i18n-standards.md** | 多语言字体/占位符/动态文本 |
| **references/must-not-and-blockers.md** | 阻断式红线（缺契约就停，不猜测） |

### 工作流与速查（按任务调阅）

| 文件 | 场景 |
|------|------|
| **references/figma-to-redream.md** | Figma 工程文档 → .red + .rebolt 端到端流程（7 phase） |
| **references/redream-development-workflow.md** | 一般性开发流程（inspect → standards → modify → validate） |
| **references/scene-creation-checklist.md** | 从零建一个 .red 的可复制 CLI 序列（含 batch 模式） |
| **references/rebolt-block-cheatsheet.md** | 常用 Block 速查（时间线/通知/条件/变量/节点操作 + selector 规则） |
| **references/redream-use-cases.md** | 常见任务配方 |
| **references/cross-project-port.md** | 跨项目模块移植（Rebolt_BT ID 冲突 / 资源打包 / 崩溃排查） |
| **references/redream-handbook.md** / **references/rebolt-handbook.md** | 引擎/行为树概念手册 |
| **references/workflow-config.md** | Figma 流程询问白名单（最多中断 3 次） |
| **references/project-patterns.md** | 常见工程模式库 |

### 阶段 1-2 专用

| 文件 | 阶段 |
|------|------|
| **references/analyze-\*.md**（5 份） | 阶段 1 方法论（9 步管线/骨架规则/节点模式/命名/动画原型） |
| **references/structure-diagram-reference.md** | 阶段 2 HTML 结构图规范（卡片 schema/连线类型/level） |
| **references/figma-naming-standards.md** / **figma-auto-export.md** | Figma 侧命名/切图 |

### 历史细分规范（仍可查，已被上方整合版覆盖）

`building-standards.md / font-standards.md / image-resource-standards.md / multilang-standards.md / naming-standards.md / node-tree-standards.md / sound-standards.md / store-assets-standards.md / ui-production-standards.md` — 内容被 `asset-standards.md` + `project-standards.md` + `i18n-standards.md` 取代，新任务优先查整合版。

### 模板 / 脚本 / 教训

| 文件 | 用途 |
|------|------|
| **templates/BeadsOut_structure.html** / **FruitTruck_structure.html** | 阶段 2 结构图模板 |
| **scripts/figma_auto_export.py** | Figma 批量切图 |
| **scripts/gen_fruittruck_v5.py** | 阶段 2 渲染参考 |
| **lessons/** | 历史 Bug 归档 |

> **⚠️ `redream-cli-reference.md` 已废弃**，内容已拆分为 cli-inspect.md + cli-modify.md + test-results-rebolt-commands.md。

---

## 阶段路由

```
用户请求                                       → 加载文件
──────────────────────────────────────────────────────────────
"分析游戏/出低保真原型/识别 UI"                → phase1
"出工程结构图/画 CCB 结构图/画 .red 场景结构图"  → phase2
"从 Figma 转 .red/.rebolt"                     → phase2 + phase3（+ figma-to-redream.md）
"生成 Redream 工程/落地 .red/写 rebolt"        → phase3
"Cocos 工程转 Redream"                          → phase1（读 Cocos 源）+ phase2 + phase3
"发布 Redream 包"                               → phase3（Step 8）
"修复 XX 问题"                                 → 按问题类型选择 phase + lessons/
"CLI 命令不确定"                               → cli-inspect.md / cli-modify.md（先 `actions --json` / `--help`）
```

### 完整生产流程

```
阶段 1：分析 & 原型         → 阶段 2：工程结构图        → 阶段 3：CLI 落地
录屏/截图/PRD 拆解              HTML CCB 卡片图              .red / .rebolt
Figma 低保真原型                stub / dyn 连线              资源装填 / 发布
skeleton.json                   每卡片 = 一个 .red           inspect check 通过
ccb-split-plan.md               level 自动计算               在模拟器跑通
```

---

## 通用铁律（所有阶段强制执行）

### 铁律 1：零幻觉（Zero Hallucination）

任何看不清 / 不确定的视觉元素，必须先向用户确认或重新量测，**禁止猜测后当事实输出**。

- 阶段 1：Figma 上的坐标/颜色/图层归属模糊 → 先用 Python OpenCV 量测，或向用户索要高清源文件
- 阶段 2：结构图的连线类型（stub/dyn）模糊 → 回到阶段 1 的 ccb-split-plan.md 确认语义
- 阶段 3：CLI 某字段含义不明 → 读 `references/redream.md` 或 `references/rebolt.md`，不要凭直觉写值；CLI 动作不确定时先跑 `actions --json` / `--help`

### 铁律 2：CLI First（2026-04 更新）

阶段 3 所有 `.red` / `.rebolt` 修改**一律优先用 Redream CLI**。当前 CLI 表面已大幅扩展，很多旧的"手改源文件"工作流已被 CLI 直接支持：

- `modify new-scene --enable-rebolt --no-default-timeline` 一条命令建好场景，**不再**需要后续删 `Default Timeline` / sed 改 `currentSequenceId`
- `modify scene --property rebolt.isRebolted --value true` 可改 scene shell 字段
- `modify batch` + `rebolt-modify batch` 支持原子多操作
- `modify add-node --properties '{...}'` 一条命令创建节点 + 设属性
- `modify timeline-channel` / `modify timeline` 新增多个回放控制字段
- `rebolt-modify set-section / set-entry / remove-entry / add-tree / batch` 均已 public

CLI 能做 → 必须用 CLI（不准直接改源文件）。CLI 做不到 → 读 `references/redream.md` / `rebolt.md` 回退到直接编辑源文件，编辑后必须 `inspect check` + `rebolt validate` 验证。

**CLI 表面与记忆冲突时** → 按 `test-results-rebolt-commands.md` 的优先级链仲裁。

**⚠️ 顶层 `rebolt` 子命令仅三个 action**（`list` / `export` / `validate`），且**没有** `actions` 子命令可列表。要枚举 rebolt 相关能力请用 `rebolt-modify actions --json`（26 个 action），不要对顶层 rebolt 跑 `actions`（会报 `Unknown rebolt action`）。

### 铁律 3：stub vs dyn 决策单点

CCB 连线类型（stub 嵌入 vs dyn 动态生成）必须在**阶段 1 的 ccb-split-plan.md** 中确定，阶段 2 和阶段 3 只做映射，**禁止在阶段 3 临时改决策**。

| 类型 | 颜色 | 语义 | 典型场景 |
|------|------|------|---------|
| `stub` | 蓝 | 父 CCB 通过 REDFile 嵌入子 CCB（布局期决定） | HUD / 结果面板 / 广告横幅 / 固定模块 |
| `dyn`  | 橙 | 父 rebolt 运行时 instantiate 子 CCB（数量不定/状态机） | 关卡格子 / 消除元素 / 可变列表项 |

若阶段 3 发现决策错误，必须**回流阶段 2** 修改 HTML 结构图，再重走阶段 3，不在 CLI 层 hack。

### 铁律 4：数据驱动尺寸

尺寸 / 容器 / 布局 / 间距一律从真实量测推导，**禁止硬编码占位常量**。

- 阶段 1：bbox 必须从 Python 量测结果读取，不写"估计 100×200"
- 阶段 2：卡片 x/y 可暂时估计，但连线端点的 fromNode 名必须精确匹配 card.nodes 中的 name
- 阶段 3：`.red` 中的 contentSize = 图片实际像素（不压缩为屏幕宽）；多实例间距 = 单元宽 + GAP (≥12px)

### 铁律 5：Selector / 类型绑定硬规则（CLI 2026-04 强制）

写 `.rebolt` 时，以下规则会在 CLI 保存前校验失败：

- **Selector 值格式**：`Value = live reboltId`（非 reboltName/别名），`DisplayName = live reboltName`（非 raw ID）
- **按钮点击块**用 `mathSelector`；**其他节点块**用 `baseSelect`；两者同一套 Value/DisplayName 规则
- **reboltName 必须唯一**（ambiguous alias 直接失败，不再回退 DisplayName 或 first-match）
- **节点类型绑定**：
  - 按钮 → `CCControlButton` / `REDNodeButton`
  - Label → `CCLabelTTF` / `CCLabelBMFont` / `CCRedLabel` / `CCLabelPlus`
  - Sprite → `CCSprite` / `CCScale9Sprite` / `SpritePlus`
  - 进度条 → `CCProgressTimer`
- **换图块二分**：单图路径 → `BTSpriteImageAction.TitleInput`；plist+frame → `BTSpritePlistAction.pathInput + frameNameInput`（CLI 不允许互换）
- **`RedFileList` key 必须指向真实 `REDFile` 节点**；普通 CCNode 会报错
- 写前必须读 paired `.red` 确认节点存在且 `reboltName` 非空；`rebolt.redInfos[*].alias` 为空时先修 scene 元数据

详见 `references/rebolt-standards.md` + `references/rebolt-block-cheatsheet.md`。

### 铁律 6：产出归档规范

所有交付物落盘到 `~/JarvisPark/output/ada/<project>/`，按三阶段分层：

```
~/JarvisPark/output/ada/<project>/
├── 01-analysis/
│   ├── figma-url.txt              # 阶段 1 Figma 链接
│   ├── skeleton.json              # 骨架清单
│   └── ccb-split-plan.md          # CCB 拆分建议
├── 02-structure-diagram/
│   └── <Project>_structure.html   # 阶段 2 单文件 HTML
└── 03-project/
    └── <Project>/                 # 阶段 3 Redream 工程（.redproj + ccb/ + res/）
```

### 铁律 7：阶段数据契约不可跳过

- 阶段 1 → 阶段 2：必须提交 **skeleton.json + ccb-split-plan.md**，阶段 2 只读这两份文件，不回读原始录屏
- 阶段 2 → 阶段 3：阶段 3 脚本只读 HTML 底部 `<script id="app-data">` JSON 块，不读阶段 1 产物
- 若跳过阶段（如"已有 Figma 稿直接生成工程"），**必须先补齐下一阶段所需的数据契约文件**

### 铁律 8：写前必 inspect、写后必 validate

- **写前** → `inspect scene --json` / `rebolt-modify read --json` 确认目标路径与当前字段值
- **写后** → 
  - `.red` 改动 → `inspect check`（当前版本已强化关键帧/属性值类型校验）
  - `.rebolt` 单文件 → `rebolt-modify validate`（硬校验空 reboltName / selector 失配 / class 不匹配）
  - `.rebolt` 工程级批改 → `rebolt validate`（全工程结构 + paired .red 交叉引用）

契约缺失时停在 `references/must-not-and-blockers.md` 的阻断清单上，不要硬上。

### 铁律 9：每轮反思沉淀（全局 CLAUDE.md 强制）

每次用户反馈后，主动执行：
1. **修了什么** — 一句话概括本轮改动
2. **根因是什么** — 遗漏规则？理解偏差？未验证假设？
3. **是否可沉淀** — 写入 `lessons/` 或 `~/.claude/projects/-Users-liuying/memory/_global/feedback_*.md`

---

## 工程约定默认值

| 项目 | 默认值 |
|------|--------|
| 设计分辨率 | **1080×2400**（竖屏试玩广告主流） |
| 引擎 | **Redream**（基于 Cocos2d-x，坐标左下为原点） |
| CLI 二进制（首选） | `"/Applications/Redream 1.0/Redream.app/Contents/MacOS/Redream"`（装完 `Redream-9.6.0.0-alpha.dmg` 后的实际路径，**注意目录名含空格，shell 必须加引号**）|
| CLI 二进制（源码构建） | `build/bin/Redream/Redream.app/Contents/MacOS/Redream` |
| CLI 版本锚定 | **1.3.4**（`Redream --help` 首行；actions 总数：inspect=11 / modify=27 / rebolt-modify=26 / rebolt 顶层=3）|
| 项目文件 | `.redproj`（项目入口）+ `ccb/*.red`（场景）+ `ccb/*.rebolt`（行为树）|
| **新建场景** | `modify new-scene --scene <f>.red --enable-rebolt --no-default-timeline`（**一条命令搞定**；旧的"建→删默认时间线→sed 改 currentSequenceId" 三步流仅修 legacy 时使用）|
| **CCLayer 分辨率** | 设计 1080×2400 / 正常 1080×2080 / 偏宽 **1560**×2080 / 偏高 1080×2800 |
| **CCNode 分辨率** | Node 分辨率 0×0（单条）|
| 根节点类型规则 | 文件名含「弹窗/浮层/全屏反馈/界面」→ `CCLayer`；其他 → `CCNode` |
| 命名规范 | `project-standards.md`（官方整合版）为主；细分规则查 `naming-standards.md` |
| 图片尺寸 | `contentSize` = 图片文件实际像素（禁止压缩为屏幕宽） |
| 超宽图处理 | 居中裁切（不拉伸压缩） |
| 主入口场景 | `Main.red`（单一总组根节点，所有 L2 走 REDFile 嵌入） |
| 动态单元 | 必须在 `<Parent>.rebolt` 的 onLoad 里 InstantiateRed |
| Spine 动画 | 默认 defaultAnimation 必须真实存在，或运行时 autoPlay 选首个非空动画 |
| 反馈 Spine | 必须条件触发，不能 autoPlay（收集/完成/失败类） |
| 程序变量命名 | `P-` 前缀 |
| publishDirectory | `_ccbi` |
| REDFile 属性名 | `redFile`（小写 r），值相对资源根不带 `ccb/` 前缀，`animation = -2` |

### 开工前必须澄清的模糊信息

触发条件（以下任一未明确时，先列出待确认事项）：
- 交互方式（点击？拖拽？长按？滑动？）
- 元素访问规则（顺序栈？任意取放？匹配规则？）
- 关卡进度 / 步数限制 / 时间限制
- 音效 / 震动需求
- 广告落地（Google Play / App Store / 内购）

参考 `references/workflow-config.md` 的询问白名单（当前最多中断 3 次：分辨率 / 项目目录 / 创建计划确认）。

---

## 交付检查清单

### 阶段 1 完成门禁
- [ ] Figma 低保真原型通过 9 层自检（elsa-analyzer-line 方法）
- [ ] skeleton.json 覆盖所有可见区域，无 "TODO" 占位
- [ ] ccb-split-plan.md 明确每个 CCB 的 stub / dyn 归属
- [ ] 所有 dyn 单元标注 `children_count` 或运行时规则

### 阶段 2 完成门禁
- [ ] 所有 L1 / L2 CCB 都有对应卡片
- [ ] 所有 dyn 单元有独立卡片
- [ ] 连线无孤儿（fromCard/toCard/fromNode 都实际存在）
- [ ] 卡片布局无重叠，连线无穿插
- [ ] JSON 自检脚本通过（见 phase2 Step 8）

### 阶段 3 完成门禁
- [ ] `inspect check` 通过，无 broken reference
- [ ] `rebolt validate`（工程级）通过，无 selector / reboltName 失配
- [ ] 所有 stub 子 CCB 在父场景中可见
- [ ] 所有 dyn 单元在 rebolt 中有 InstantiateRed 逻辑
- [ ] 资源路径可解析，无缺失
- [ ] 所有 Spine `defaultAnimation` 非空 或 运行时 autoPlay 生效
- [ ] 图片 `contentSize` = 实际像素，9-slice 走 stretch 不回写原图尺寸
- [ ] `publish` 成功产出 `.redream` 包
- [ ] 模拟器 / GUI 运行核心玩法走通

---

## 快速启动

**全流程**（录屏 → 工程）：
1. 读 `phases/phase1-analyze-game.md` 做分析
2. 读 `phases/phase2-structure-diagram.md` 出 HTML
3. 读 `phases/phase3-implement-redream.md` 落地 CLI

**从 Figma 直入**：跳过 phase1，从 phase2 开始，额外读 `references/figma-to-redream.md`

**Cocos 转 Redream**：phase1 的输入源换成 Cocos `.prefab`/`.scene`，其余流程不变

**只出结构图**：只走 phase2，落盘到 `02-structure-diagram/`，不进 phase3

**只改/只查一个已有工程**：读 `references/redream-development-workflow.md` → `cli-inspect.md` → `cli-modify.md`，不走三阶段

---

## FAQ

**Q：与 redream-skill / elsa-analyzer-line / redream-structure-diagram 的关系？**
A：本 skill 合并三者为端到端管线。原三 skill 仍独立可用（纯 CLI 操作用 redream-skill，纯分析用 elsa-analyzer-line，纯结构图用 redream-structure-diagram）。本 skill 适合"从零复刻一个游戏"的场景。

**Q：为什么不和 cocos-project-gen 合并？**
A：目标引擎不同。cocos-project-gen 产出 CocosCreator 3.8.x 工程（`.prefab`/`.scene` JSON flat-array），Redream-project-gen 产出 Redream 工程（`.red` XML + `.rebolt` JSON）。两个引擎的文件格式、构建规则、运行时都不兼容。

**Q：结构图非要 HTML 吗？能否 PNG？**
A：必须 HTML。HTML 可交互（拖拽卡片、重连端点、导出 JSON），并且阶段 3 CLI 脚本直接读 HTML 中 `app-data` JSON，PNG 无结构化数据无法对接。

**Q：引擎组的 C++/Cocos 逻辑代码生成（MVVM + delegate + FindDifferenceGame）为什么没合进来？**
A：那是另一个域——从 Redream 资产生成 C++ 业务逻辑，与本 skill "出资产/工程"职责不同。应另起一个 `Redream-logic-code-gen` skill 承接，不混进本 skill。

**Q：CLI 命令和我记忆的不一样怎么办？**
A：按 `references/test-results-rebolt-commands.md` 仲裁链：当前 binary `actions --json` → `--help` → 源码 → 本文档 → 历史记忆。不要靠"之前文档这样说"硬推。

---

## 已验证规范来源

- Redream CLI：`"/Applications/Redream 1.0/Redream.app/Contents/MacOS/Redream"`（DMG 安装路径，含空格）或 `build/bin/Redream/...`（源码构建）
- CLI 版本：**1.3.4**（2026-04-22 实测，`Redream --help` 首行）
- 官方权威来源：引擎组 `ai_dev_skill` commit `9a8b53f`（2026-04-09 基线），对应 `Redream-9.6.0.0-alpha.dmg`
- 结构图模板：BeadsOut（简洁）/ FruitTruck（完整）
- 分析方法论：elsa-analyzer-line v1 (2026-04-02)
- 六格烧烤项目：`~/JarvisPark/output/ada/sixgrid_bbq_redream/SixGridBBQ_structure.html`（2026-04-14 交付）

---

## 版本日志

- **2026-04-22**：对齐 `ai_dev_skill` commit `9a8b53f` + 实测 `Redream CLI 1.3.4`（装在 `/Applications/Redream 1.0/`）。CLI 表面 / 格式 / 标准文档与引擎组权威版**零语义差异**（仅目录布局不同：本地扁平 vs 引擎组分层）。
  - 更正 CLI 二进制路径为 `/Applications/Redream 1.0/Redream.app/...`（含空格，shell 需加引号）。
  - 补录实测 action 计数：inspect=11 / modify=27 / rebolt-modify=26 / rebolt 顶层=3。
  - 铁律 2 补充 rebolt 顶层不支持 `actions` 子命令。
  - **未引入** `ai_dev_skill/references/code/`（C++/MVVM 业务逻辑生成），按 FAQ 判断应由独立 `Redream-logic-code-gen` skill 承接，避免混入资产生成职责。
  - **未采用**分层目录（common/redream/code），本地扁平布局不动，内部路径指针保持扁平。
- **2026-04-21**：同步引擎组 `ai_dev_skill` 基线。新增/替换 19 份 references（cli-inspect/cli-modify/test-results/rebolt/redream/rebolt-standards/must-not-and-blockers/figma-to-redream/workflow-config/rebolt-block-cheatsheet/scene-creation-checklist/red-node-patterns/asset-standards/i18n-standards/project-standards/redream-development-workflow/redream-use-cases/cross-project-port/rebolt-handbook）。铁律新增 selector 硬规则、new-scene 单步流、写前/写后校验。`redream-cli-reference.md` 标记废弃。
- **2026-04-14**：SixGridBBQ 交付，phases/ 管线定稿。
