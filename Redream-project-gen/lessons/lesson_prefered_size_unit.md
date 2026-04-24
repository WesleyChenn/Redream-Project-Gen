---
name: REDNodeButton 的 preferedSize 单位必须和 contentSize 一致
date: 2026-04-24
status: ✅ 已落地（渲染规则）
source: RED Tool 放穿透层 bug
---

# Lesson: preferedSize 和 contentSize 单位必须一致

## 事件

放穿透层最初写成：

```python
contentSize:  [100, 100, 2, 2]   # 100% × 100% ✅
preferedSize: [100, 100, 0, 0]   # 100 像素 ❌
```

Redream 打开后**放穿透层只有 100×100 像素的小方块**，不是全屏覆盖。

## 根因

REDNodeButton 有**多个尺寸属性**：
- `contentSize` — 逻辑内容尺寸
- `preferedSize` — 渲染用的尺寸

Redream 渲染时用的是 `preferedSize`。所以即使 contentSize 写对了（100% × 100%），preferedSize 单位错误（0=像素）还是会只渲染成小方块。

## 规则

**REDNodeButton 的 preferedSize 和 contentSize 必须单位一致。**

```python
# ✅ 正确
contentSize:  [100, 100, 2, 2]    # 100% × 100%
preferedSize: [100, 100, 2, 2]    # 100% × 100%

# ❌ 错误
contentSize:  [100, 100, 2, 2]
preferedSize: [100, 100, 0, 0]    # 100 像素（小方块）
```

## 代码实现

```python
p_preferedsize(100.0, 100.0, 2, 2)    # 两个单位都是 2
```

## 教训

1. REDNodeButton 有多个尺寸属性，**必须全部同步**
2. 生成 plist 前**用 Redream 打开检查实际渲染效果**，不能只看 children 结构对不对
3. 单位（unit）是容易忽略的隐藏字段，错了很难发现（因为树结构看着正常）

## 关联

- `references/figma-to-red-cli-driven.md` — 放穿透层规则章节
- `references/red-node-patterns.md` — REDNodeButton 完整属性
- `lessons/lesson_unit2_auto_convert.md` — unit=2 vs unit=0 的基础知识
