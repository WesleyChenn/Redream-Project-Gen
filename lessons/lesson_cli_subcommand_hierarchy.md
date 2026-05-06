---
name: CLI 子命令层级（list-node-types 不是顶层）
date: 2026-04-24
status: ✅ 已落地
source: RED Tool CLI 迁移
---

# Lesson: CLI 子命令是层级结构

## 事件

首次试 `Redream list-node-types` 查看支持的节点类型，报 `Unknown command`。

## 根因

`list-node-types` **不是顶层命令**，而是 `modify` 下的子 action。

```bash
❌ Redream list-node-types
✅ Redream modify list-node-types
```

## 规则

CLI 子命令是层级结构的：

```
Redream
├── inspect              # 只读命令
│   ├── check
│   ├── scene
│   ├── timeline
│   └── ...
├── modify               # 写命令
│   ├── new-project
│   ├── new-scene
│   ├── build-scene
│   ├── add-node
│   ├── set-property
│   ├── list-node-types  ← 在这里
│   └── ...
├── rebolt               # rebolt 项目级命令
│   ├── list
│   ├── export
│   └── validate
└── rebolt-modify        # rebolt 单文件命令
    ├── read
    ├── validate
    └── ...
```

## 排查方法

- 顶层 `--help` 不列 action 的时候，要查它属于哪个父命令
- 可以先跑 `Redream modify --help` / `Redream inspect --help` 看子 action 列表
- 或者查 `references/cli-modify.md` / `references/cli-inspect.md`

## 关联

- `references/cli-inspect.md`
- `references/cli-modify.md`
