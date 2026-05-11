# Changelog

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
