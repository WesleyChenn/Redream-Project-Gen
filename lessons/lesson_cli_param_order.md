---
name: Redream CLI 参数顺序（options 必须在 action 前）
date: 2026-04-24
status: ✅ 已落地
source: RED Tool CLI 迁移
---

# Lesson: CLI 参数顺序

## 事件

首次用 Redream CLI 时，按"习惯"把 `--json` 放在 action 后面，报 `Unknown option 'json'`：

```bash
❌ Redream -p xxx inspect check --json
```

## 规则

CLI 参数顺序：

```
Redream [options] action
```

**options 都放 action 前面**。

## 正确示例

```bash
✅ Redream --json -p xxx inspect check
✅ Redream -p xxx.redproj modify build-scene --scene xxx.red --config y.red
✅ Redream -p xxx.redproj inspect check
```

## 错误示例

```bash
❌ Redream -p xxx inspect check --json       # --json 在 action 后
❌ Redream inspect check --project xxx       # --project 在 action 后
```

## 关联

- `references/cli-inspect.md`
- `references/cli-modify.md`
- `references/figma-to-red-cli-driven.md`
