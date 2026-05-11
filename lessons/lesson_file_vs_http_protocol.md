---
name: RED Tool 不能双击 HTML 打开，必须用 http://
date: 2026-04-24
status: ✅ 已落地（用户操作）
source: RED Tool 使用问题
---

# Lesson: 浏览器协议 file:// vs http://

## 事件

用户双击 RED Tool 的 HTML 文件打开，地址栏是 `file:///...`。浏览器里点按钮报：

```
Failed to fetch
```

## 根因

HTML 里的 JavaScript 要向 Python 后端（Flask 跑在 `http://localhost:5000`）发 fetch 请求。

- `file://` 协议下打开的页面 → JavaScript 的 fetch 请求**跨协议**发不出去
- 浏览器出于安全考虑会拦截 file:// → http:// 的跨协议请求

## 规则

**必须用 `http://localhost:5000` 打开 RED Tool**，不能双击 HTML 文件。

## 正确启动流程

```bash
# 1. 启动 Flask 服务
cd ~/Desktop/red_tool/red_tool\ 14
python3 app.py

# 2. 浏览器打开
http://localhost:5000
```

**不要** 双击 `index.html` / 用 Finder 打开。

## 排查

- 看地址栏：如果是 `file:///...` → 协议错了
- 看终端：Flask 没启动的话 fetch 请求根本没到后端
- 所以"Failed to fetch"要**优先看终端**：
  - 终端没显示 `Running on http://127.0.0.1:5000` → Flask 没启动
  - 终端有日志但请求没到 → 前端协议错了

## 教训

第一次告诉用户的时候要**特别强调**"不要双击 HTML"，不然很多人会自然地双击打开。

## 关联

- `references/figma-to-red-cli-driven.md` — 启动流程章节
