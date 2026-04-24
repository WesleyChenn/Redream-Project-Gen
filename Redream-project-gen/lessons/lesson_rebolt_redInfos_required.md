---
name: rebolt 字典必须包含 redInfos
date: 2026-04-20
status: ✅ 已落地（崩溃规则）
source: Mengmeng plistlib 实战
---

# Lesson: rebolt.redInfos 缺失导致崩溃

## 事件

手写 .red 文件时漏了 `rebolt.redInfos` 字段，Redream 打开**崩溃**。

## 规则

`.red` 文件顶层 `rebolt` 字典必须包含 `redInfos` 字段（即使是空字典 `{}`）：

```python
'rebolt': {
    'isRebolted': False,
    'redInfos': {}       # ← 必须有，即使空
}
```

## 正确示例

```python
red = {
    'centeredOrigin': True,
    'currentResolution': 2,
    # ... 其他字段
    'rebolt': {
        'isRebolted': False,
        'redInfos': {}
    },
    # ...
}
```

## CLI 下的处理

使用 CLI `modify new-scene --enable-rebolt` 时，引擎**自动写入** rebolt 结构，包含 redInfos。不用手动维护。

## 关联

- `references/figma-to-red-plistlib.md`
- `references/redream.md` — .red 文件完整格式定义
