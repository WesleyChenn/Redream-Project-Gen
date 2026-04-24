# phase1-figma-json · 截图/录屏 → Figma JSON 规范

本目录是 **phase1 分析阶段**的**具体 JSON 格式规范与执行步骤**，用于把截图/录屏/PRD 转换成 Figma 低保真原型所需的 JSON 数据。

## 与 phases/phase1-analyze-game.md 的关系

- `phases/phase1-analyze-game.md` — phase1 **方法论**（9 步管线 / Elsa Analyzer 思路）
- `phase1-figma-json/*.md`（本目录） — phase1 **具体实施**（命名白名单 / 底板分离规则 / JSON 格式 / 组件匹配 / 自检清单）

两者**互补使用**：先读方法论了解思路，再查本目录拿具体规则。

## 执行顺序

| 步骤 | 文件 | 职责 |
|------|------|------|
| S0 | `00_core_rules.md` | 贯穿全流程的核心铁律（命名白名单 / fill 规则 / 底板分离 / 屏幕类型判断 / 浮层遮罩 / 界面背景） |
| S1 | `01_frame_scan.md` | Frame 扫描 |
| S2 | `02_scroll_detect.md` | 滚动区域识别 |
| S3 | `03_skeleton.md` | 骨架生成 |
| S4 | `04_component_match.md` | 组件库匹配（component_ref） |
| S5 | `05_json_generate.md` | 最终 JSON 输出 |
| S6 | `06_selfcheck.md` | 自检清单 |

## 何时读取

- 用户要求"分析截图/出 Figma 低保真原型/生成 Figma JSON"
- 与 `phases/phase1-analyze-game.md` 一起读（方法论 + 具体规则）
- 做 phase2/phase3 遇到 Figma 命名/结构疑问时，回查 S0 核心铁律

## 与 elsa-analyzer-line 的关系

本目录是 **elsa-analyzer-line 方法论**的**最新 JSON 格式规范版**（2026-04-22）。
若方法论与本目录有差异，以本目录为准（后者是实操迭代版）。
