---
name: unit=3 只能用于 contentSize 的高度
date: 2026-04-23
status: ✅ 已落地（硬规则）
source: Mengmeng plistlib 实战
---

# Lesson: unit=3 的使用范围

## unit=3 的语义

`unit=3` 表示 **"父节点高度 - 该值"**（减去模式）。

例如父节点高 `2080`，子节点 contentSize.h 配 `[200, 3]` → 实际高度 = `2080 - 200 = 1880`。

## 规则

### ✅ 允许的使用

**只能用于 `contentSize` 的高度（h 字段）：**

```python
contentSize = [w, h_value, w_unit, h_unit, ...]
#              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#                   只有 h_unit 可以是 3
```

常见场景：全宽内容区需要"总高 - 顶部安全区高度"时。

### ❌ 禁止的使用

**不能用于 position（无论 x 还是 y）：**

```python
# ❌ 错误
position = [x, y, 3, 2, 0]   # x_unit=3 非法
position = [x, y, 0, 3, 0]   # y_unit=3 非法
```

**不能用于 contentSize 的宽度：**

```python
# ❌ 错误
contentSize = [w, h, 3, 2, ...]   # w_unit=3 非法
```

## 正确示例

```python
# 全宽节点，高度 = 父高 - 200
contentSize = [100, 200, 2, 3, F, F]
#              ^^^^^^^^^^^^^^^^^^^^^^^
#              宽 100% (u=2)，高 = parent_h - 200 (u=3)
```

## position 只能用两种 unit

| unit | 含义 |
|------|------|
| `0` | 绝对像素 |
| `2` | 相对父节点 contentSize 的百分比 |

## 关联

- `references/cocosbase.md` — unit 定义与坐标系
- `references/figma-to-red-plistlib.md` — 坐标系统规则
- `lessons/lesson_unit2_auto_convert.md` — unit=2 的自动归一化
