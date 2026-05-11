---
name: macOS AirPlay Receiver 占用 5000 端口
date: 2026-04-24
status: ✅ 已落地（环境配置）
source: RED Tool 启动问题
platform: macOS Monterey+
---

# Lesson: AirPlay Receiver 默认占用 5000 端口

## 事件

启动 RED Tool（Flask 默认端口 5000）报错：

```
Address already in use
Port 5000 is in use by another program
```

但明明没开别的 Flask 服务。

## 根因

**macOS Monterey+ 默认开启 AirPlay Receiver**，监听 5000 端口。这和 Flask 默认端口冲突。

## 解决方法

### 方法 A：关掉 AirPlay Receiver（推荐）

1. 系统设置（System Settings）
2. 通用（General） → 隔空投送与接力（AirDrop & Handoff）
3. 关掉 **隔空投送接收器**（AirPlay Receiver）

### 方法 B：改 Flask 端口

修改 `app.py` 末尾：
```python
app.run(port=5001)    # 从 5000 改 5001
```

RED Tool v13b 已经内置了这个方案。

## 排查命令

```bash
lsof -i :5000
```

看是什么进程占着端口：
- `ControlCenter` / `rapportd` → AirPlay Receiver，关掉它
- `Python` → 之前的 Flask 进程没清理（见下一条 lesson）

## 教训

Mac 开发 Flask / Node / 其他服务之前，**先关 AirPlay Receiver**，避免踩坑。

## 关联

- `lessons/lesson_zombie_python_process.md` — 另一个端口占用原因
- `references/figma-to-red-cli-driven.md` — "端口被占用"章节
