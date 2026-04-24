---
name: uniqueNodeId 必须唯一且非零
date: 2026-04-20
status: ✅ 已落地（崩溃规则）
source: Mengmeng plistlib 实战
---

# Lesson: uniqueNodeId 崩溃

## 事件

首次用 plistlib 生成 .red 时，所有节点的 `uniqueNodeId` 都填了 `0` 或未设置，Redream 打开立刻**崩溃**。

## 规则

每个节点必须分配**唯一的非零 uniqueNodeId**。

## 推荐做法（plistlib）

```python
import random

_used_ids = set()

def new_id():
    while True:
        i = random.randint(100_000_000, 999_999_999)
        if i not in _used_ids:
            _used_ids.add(i)
            return i
```

ID 范围建议 `100_000_000 ~ 999_999_999`（9 位数），避开引擎保留的小整数。

## CLI 下的处理

使用 CLI `modify add-node` 时，引擎**自动分配** uniqueNodeId，不用手动管。

本规则仅对 plistlib 直接生成 .red 的流程有效（见 `references/figma-to-red-plistlib.md`）。

## 关联

- `references/figma-to-red-plistlib.md`
- `lessons/lesson_rebolt_redInfos_required.md`
