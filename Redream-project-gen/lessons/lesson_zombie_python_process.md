---
name: 僵尸 Python 进程占用 Flask 端口
date: 2026-04-24
status: ✅ 已落地（环境配置）
source: RED Tool 启动问题
---

# Lesson: Flask 开发模式退出不干净

## 事件

关掉 AirPlay Receiver 之后，Flask 启动还是报：

```
Address already in use
```

## 根因

之前用 `Ctrl + C` 退出 Flask 时，**开发模式的 reloader 进程可能没清理干净**，有残留 Python 进程还占着端口。

## 诊断

```bash
lsof -i :5000
```

输出类似：
```
COMMAND  PID  USER   ...
Python   34603 red   ... LISTEN    ← 之前的进程
```

## 解决

### 方法 A：杀指定 PID

```bash
kill -9 34603
```

（PID 从 lsof 输出看到）

### 方法 B：杀所有 Python 进程

```bash
killall python3
```

⚠️ 注意：如果你有其他 Python 脚本在跑，会一起杀掉。

## 预防

- 退出 Flask 时**干净地 `Ctrl + C`**（而不是直接关终端窗口）
- 每次启动前先 `lsof -i :5000` 确认端口空闲

## 教训

Flask 开发模式（`debug=True` 或 `reloader` 开启）的退出**不一定清理干净**。下次遇到端口占用，除了 AirPlay 也要**查 Python 进程**。

## 关联

- `lessons/lesson_airplay_port_5000.md` — 另一个端口占用原因
- `references/figma-to-red-cli-driven.md` — 启动与排查章节
