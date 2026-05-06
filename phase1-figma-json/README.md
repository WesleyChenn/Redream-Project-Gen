# phase1-figma-json · 截图/录屏 → Figma JSON 规范（v20）

> **2026-04-24 更新**：升级到 v20 按钮命名规则，与 Redream 引擎识别对齐。

本目录是 **phase1 分析阶段**的**具体 JSON 格式规范与执行步骤**，用于把截图/录屏/PRD 转换成 Figma 低保真原型所需的 JSON 数据。

## 与 phases/phase1-analyze-game.md 的关系

- `phases/phase1-analyze-game.md` — phase1 **方法论**（9 步管线 / Elsa Analyzer 思路）
- `phase1-figma-json/*.md`（本目录） — phase1 **具体实施**（命名白名单 / 按钮识别 / 组件匹配 / 字段命名铁律 / 自检清单）

两者**互补使用**：先读方法论了解思路，再查本目录拿具体规则。

## 执行顺序

| 步骤 | 文件 | 职责 |
|------|------|------|
| S0 | `00_core_rules.md` | 贯穿全流程的核心铁律（命名白名单 / v20 按钮识别 / 按钮分组 / fill 规则 / 屏幕类型 / 浮层遮罩 / 界面背景） |
| S1 | `01_frame_scan.md` | Frame 扫描（录屏专用：触摸点识别 + 转场回溯 + 不可见兜底）|
| S2 | `02_scroll_detect.md` | 滚动区识别 + 新屏幕回写 S1 清单 |
| S3 | `03_skeleton.md` | 骨架分析 + 组件匹配 + 角标归属 + AL 对齐意图确认 |
| S4 | `04_component_match.md` | 组件库匹配详细规则 |
| S5 | `05_json_generate.md` | 最终 JSON 输出 + **字段命名铁律**（下划线 vs 驼峰）|
| S6 | `06_selfcheck.md` | 8 层自检清单（必须全过）|

## v20 关键变化（对比 v19）

| 维度 | v19（老）| v20（新）✅ |
|------|----------|------------|
| 按钮外壳 | `底板_xxx` FRAME | **`按钮_xxx` FRAME** |
| 按钮内层底板 | `底板_xxx形状` RECT | **`底板_xxx` RECT**（不加后缀）|
| 识别方式 | 靠"形状"后缀区分 | **靠不同前缀区分**（更清晰）|
| 引擎识别 | 靠 FRAME 类型 + 后缀规则 | **严格以 `按钮_` 开头的 FRAME** |

**引擎对齐**：`按钮_xxx FRAME` → `REDNodeButton`（触控层）。v20 和 Redream 引擎的 `is_btn_layer` 规则完全一致。

## 何时读取

- 用户要求"分析截图/出 Figma 低保真原型/生成 Figma JSON/分析录屏"
- 与 `phases/phase1-analyze-game.md` 一起读
- 做 phase2/phase3 遇到 Figma 命名/结构疑问时，回查 S0 核心铁律
- 调试滚动容器 / 字段不生效问题时，查 S5 的字段命名铁律

## 和 elsa-analyzer-line 的关系

本目录是 **elsa-analyzer-line 方法论**的**最新 JSON 格式规范版**（2026-04-24）。
若方法论与本目录有差异，以本目录为准（后者是实操迭代版，包含 v20 按钮规则 + 字段命名铁律 + 触摸点不可见兜底 等新内容）。
