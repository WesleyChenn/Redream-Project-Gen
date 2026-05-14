# Changelog

## v8.3.0 (2026-05-14)

main 分支首次直接迭代（v8-5.11 已合并）。引入两套新 Skill 组织结构供横向对比。

### 新增目录

- **`phase1-figma-json-v2/`**：4.22skill_v2 整套（按 S0–S11 分步组织，19 个 .md + memory/）
  - 11 主步骤：00_S0_context → 11_S11_抽取导出
  - S7 子拆 5 文件（基础铁律 / 按钮 / 进度条 / 嵌套 / 布局）
  - `memory/`：17 个本地内存档案（UI pattern + feedback + visual priors）
- **`phase1-figma-json-v3/`**：4.22skill_v3 整套（用子目录组织）
  - `SKILL.md`（入口，18 KB）+ `命名_参考.md`
  - `steps/`（17 步骤文件，与 v2 同名）
  - `lessons/`（5 个教训档案，bug-archive + 4 个 lesson）
  - `memory/`（已解引用 symlink，17 个文件）

⚠️ v2/v3 是两种组织哲学的对比版本，旧的 `phase1-figma-json/` 保留供参考，**下次迭代选定后再清理**。

### 升级

- **`references/RED-Tool-v20.7/01_schema_coord.md`**：160 → 177 行
- **`references/RED-Tool-v20.7/SKILL.md`**：55 → 56 行（索引微调）
- **`plugin/code.js`**：76 KB → 84 KB
- **`plugin/ui.html`**：30 KB → 33 KB
- **`red_tool/app.py`**：1725 → 1732 行

### component_extractor 重构（新增 3 文件）

- **`component_library_normalized.json`**（42 KB）：归一化后的组件库（set 重构产物）
- **`component_library_plugin.json`**（40 KB）：插件可消费版本
- **`normalization_spec.json`**（5 KB）：归一化规则定义

### 未变化（无需操作）

- 顶层 `MEMORY.md`、`SKILL.md`
- 引擎 skill 7 文件中的 6 个（00 / 02 / 03 / 04 / 05 / 06_misc）
- `red_tool/templates/index.html`、`plugin/manifest.json`
- 旧 `phase1-figma-json/`（v8-5.11 的 9 文件）暂保留

---

## v8.2.0 / v8-5.11 (2026-05-11)

在 v8-5.9 基础上的增量更新，重点：引擎 SKILL 文档重构 + 工具链小修。

### 重构（破坏性变更）

- **`references/RED-Tool-v20.7-guide.md` → `references/RED-Tool-v20.7/`**
  原单文件 1102 行的 RED Tool 引擎指南，由引擎组重构为 7 主题分文件 + 1 索引：
  - `SKILL.md`（55 行，索引）
  - `00_overview.md`（74 行，工具概述 + 启动 + 输入输出 + 整体管线）
  - `01_schema_coord.md`（160 行，scene.json schema + 坐标规则）
  - `02_naming.md`（80 行，命名规则）
  - `03_component.md`（367 行，组件提取 + Variant 分类）
  - `04_cli_python.md`（143 行，CLI 调用 + Python 集成）
  - `05_figma_plugin.md`（145 行，Figma 插件交互）
  - `06_misc.md`（263 行，杂项与排错）

### 升级

- **`MEMORY.md`**（顶层）：554 → **615 行**（引擎最新内存规则）
- **`phase1-figma-json/00_core_rules.md`**：997 → **1074 行**
- **`phase1-figma-json/03_skeleton.md`**：472 → **547 行**
- **`plugin/code.js`**：75045 → **75795 B**（小修）
- **`red_tool/app.py`**：1631 → **1725 行**

### 无变化

- `component_extractor/`（全部跳过）
- `phase1-figma-json/` 的 04、06、07
- `plugin/ui.html`、`manifest.json`
- `red_tool/templates/index.html`
- `lessons/lesson_component_no_delete.md`（4.22最新skill/MEMORY.md 内容未变）

### 跳过未集成

- `引擎最新skill/SKILL.md.bak`（备份文件）
- `最新插件/code.js.bak.*`（备份文件）
- `4.22最新skill/output/`（项目生成产物）

---

## v8.1.0 / v8-5.9 (2026-05-09)

在 v8-5.6 基础上的增量更新，覆盖 RoyalPass 项目实战教训 + 工具/规范同步。

### 升级（覆盖式替换，新版 WIN）

- **`MEMORY.md`**（顶层）：22 KB → 含 RoyalPass 项目最新内存规则
- **`references/RED-Tool-v20.7-guide.md`**：来自引擎组最新 SKILL.md（替换旧版）
- **`phase1-figma-json/00_core_rules.md`**：638 → **997 行**
- **`phase1-figma-json/04_component_match.md`**：527 → **530 行**
- **`phase1-figma-json/06_selfcheck.md`**：215 → **421 行**
- **`phase1-figma-json/07_export_v20_6.md`**：183 → **348 行**
- **`plugin/code.js`**：57 KB → **75 KB**（v20.6 → 后续修复）
- **`plugin/ui.html`**：22 KB → **30 KB**
- **`red_tool/app.py`**：1631 行（实战修复版）
- **`red_tool/templates/index.html`**：634 行
- **`component_extractor/`** 全部 .py 与 .json 同步最新

### 新增

- **`lessons/lesson_component_no_delete.md`**：RoyalPass 项目教训档案
  - 教训："Component 修复时绝不擅自删除 Component"（2026-05-09）
- **`component_extractor/build_scene_v2.py`**：第二代场景构建脚本
- **`component_extractor/test_nested.json`**：嵌套结构测试用例
- **`component_extractor/video_frames_v2/`**：第二批参考帧（已加入 `.gitignore`，不上传 GitHub）

### 配置变更

- **`.gitignore`**：新增 `component_extractor/video_frames_v2/` 排除规则

### 跳过未集成

- `4.22最新skill/output/`（项目生成产物，不属于 Skill 内容）
- `最新插件/*.bak.*`（plugin 备份文件）
- `red_tool/__pycache__/`（Python 运行时缓存）

---

## v8.0.0 (2026-05-06)

从 v7 升级到 v8，整合了 5 个外部更新源，覆盖规范升级 + 完整工具栈。

### 新增

- **`MEMORY.md`**（顶层）：RED Tool v20.7 关键内存规则（坐标规则、按钮命名 v20、放穿透层规则）
- **`plugin/`**：Figma 插件「Elsa UI 生成器 v20.6」
  - `manifest.json`、`code.js`、`ui.html`
  - 功能：将 v20.6 schema JSON 转为 Figma Component Set + INSTANCE
- **`red_tool/`**：Flask 后端服务 v20.7
  - `app.py` + `templates/index.html`
  - 端口 5001，提供 `/api/generate_red`、`/api/ping`、`/api/open_finder`
- **`component_extractor/`**：组件提取与场景构建管线
  - `extract_components.py`、`build_scene.py`、`selfcheck.py`、`fix_constraints.py`
  - 含测试 JSON 数据（`test_input.json`、`scene_flat.json`、`scene_final.json` 等）
  - `video_frames/` 已加入 `.gitignore`（本地保留参考帧，不上传仓库）
- **`references/RED-Tool-v20.7-guide.md`**：RED Tool 完整使用指南（来自引擎组最新 SKILL.md）
- **`phase1-figma-json/07_export_v20_6.md`**：阶段二导出脚本规范

### 升级

- **`phase1-figma-json/00_core_rules.md`**：424 → 638 行，新增进度条建模铁律 (v20.4)
- **`phase1-figma-json/03_skeleton.md`**：271 → 472 行，新增子 CCB 根节点 CCLayer→CCNode 规则 (v20.7 breaking change)
- **`phase1-figma-json/04_component_match.md`**：433 → 527 行，新增 Variant 视觉权重规则
- **`phase1-figma-json/06_selfcheck.md`**：129 → 215 行，新增 9 层自检框架

### 保留（无变化）

- `SKILL.md`（项目级导航文档）
- `phase1-figma-json/01_frame_scan.md`、`02_scroll_detect.md`、`05_json_generate.md`、`README.md`
- `phases/`、`lessons/`、`scripts/`、`templates/`、`references/`（除新增文件外）
- `上传说明_v2.md`

### 数据流（v8 完整管线）

```
视频 → scene_flat.json
    ↓ [component_extractor/extract_components.py]
scene_final.json (v20.6 schema)
    ↓ [粘贴进 Figma 插件]
Figma 插件 (plugin/code.js) → combineAsVariants() → Component Set + INSTANCE
    ↓ [设计师整理]
插件 ▶生成 → POST /api/generate_red → red_tool/app.py
    ↓ [Redream CLI 1.3.4]
.red 文件
```

### 版本依赖

- Redream CLI: 1.3.4 (`/Applications/Redream.app/Contents/MacOS/Redream`)
- RED Tool schema: v20.6
- Flask: 端口 5001
- Python: 3.x（plistlib 系统内置）

### 文件清单变更概览

| 类别 | v7 | v8 | 增量 |
|------|----|----|------|
| 顶层文档 | 2 | 4 | +MEMORY.md、CHANGELOG.md |
| 顶层目录 | 5 | 8 | +plugin/、red_tool/、component_extractor/ |
| phase1 文件 | 8 | 9 | +07_export_v20_6.md |
| references | 40 | 41 | +RED-Tool-v20.7-guide.md |
