# RED Tool 概述 + 启动

> 引擎 SKILL 拆分文档(v20.7.x+,2026-05-11) · 索引见 SKILL.md
>
> **v20.7.x 主要改动**:子 CCB 根节点 CCLayer→CCNode、主屏 INSTANCE 拆成父 CCNode + 子 REDFile 两层、
> INSTANCE.variant→sequenceId 映射、variant_diffs 解析(visible/color keyframe)、
> components 防御过滤、Figma 端 code.js 三处 bug 修复、
> **2026-05-11 改组级 keyframe 模式(详见 03_component.md 8.11)**

---

## 一、工具概述

RED Tool 是 Figma → Redream `.red` 文件的转换工具，CLI 驱动版本。当前 v20.7 已集成进 Figma 插件，单一入口完成全流程。

**整体管线**：

```
录屏视频 ─┐
         ├─→ [工具 A：Claude 看视频] → scene.json → [Figma 插件 ▶ 生成] → Figma 画布
         ↓                                                                   ↓
                                              设计师在 Figma 里整理图层、抽 Component、做 Variants
                                                                              ↓
                              [工具 B：Figma 插件 🚀 生成 .red] ─POST→ [Python Flask app.py] → .red 文件
```

**两套工具**：

- **工具 A（录屏 → Figma）**：Claude 看视频 → 生成 scene.json → Figma 插件 ▶生成 在画布渲染
- **工具 B（Figma → RED Tool）**：Figma 插件 🚀按钮 → POST `localhost:5001` → Python 生成 `.red`

视频识别阶段拍不到多态信息，**设计师在 Figma 里手动整理图层 + 做 Component + 做 Variants 是必经环节**。两个工具间数据靠 scene.json 流转。

---

## 二、启动与基本操作

### 启动 Python 服务

```bash
cd ~/Desktop/red_tool
python3 app.py
```

正常启动后看到：

```
============================================================
  🔴 RED Tool v20.7 启动（CLI 驱动 + Figma 插件接口）
  浏览器打开: http://localhost:5001
  输出目录:   ~/Desktop/red_output
  Redream CLI: /Applications/Redream.app/Contents/MacOS/Redream
  CLI 就绪:   ✅
------------------------------------------------------------
  Figma 插件接口:
    GET  /api/ping             连通性检测
    POST /api/generate_red     生成 .red（v20.6 schema）
    POST /api/open_finder      在 Finder 中打开路径
============================================================
```

### 端口冲突排查

- 端口 5001 被占：`lsof -i :5001` 找 PID → `kill -9 PID` 或 `killall python3`
- 改代码后必须 `Ctrl+C` 重启服务才生效
- Internal Server Error → 看终端 Traceback
- Failed to fetch → 检查 Flask 是否启动

### 输入输出

- **输入**：Figma 插件 🚀按钮 POST 的 v20.6 schema JSON（含 `meta` / `components` / `screens` / `flow`）
- **输出**：`~/Desktop/red_output/` 单项目结构

---
