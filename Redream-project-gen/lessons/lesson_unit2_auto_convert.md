---
name: 子节点不能用 unit=2（Redream 自动转 unit=0）
date: 2026-04-23
status: ✅ 已落地（红灯规则）
source: Mengmeng plistlib 实战
---

# Lesson: 子节点不能用 unit=2

## 事件

在用 plistlib 生成 .red 文件时发现：子节点若用 `unit=2`（相对父节点 contentSize 的百分比），Redream 打开文件后会**自动转为 `unit=0`（绝对像素）**，文件体积翻倍。

## 根因

Redream 对 unit 的处理规则：
- `unit=2` 意为"相对父节点 contentSize 的百分比"
- 当父节点是固定尺寸时，百分比 = 固定像素，实际意义等价 `unit=0`
- Redream 打开时做归一化，把**非必要的 unit=2 自动改写成 unit=0**

## 规则：unit=2 只用于以下位置

| 节点 | 字段 | 示例 |
|------|------|------|
| CCLayer | contentSize | `size=[100,100 u=2,2]` |
| scene_root CCNode | position + contentSize | `pos=[50,50 u=2,2]  size=[100,100 u=2,2]` |
| 遮罩_背景 / 放穿透层 | position + contentSize | `pos=[50,50 u=2,2]  size=[100,100 u=2,2]` |
| 全宽节点 | position.x + contentSize.w | `x=50% u=2, size w=100% u=2` |

## 其他所有子节点

**一律用 `unit=0`（绝对像素）**，不要图省事写百分比。

## 子节点坐标换算公式

```python
# Figma 坐标系（左上为原点）→ Cocos 坐标系（左下为原点）
cx = fx + w / 2.0
cy = parent_h - fy - h / 2.0    # y 轴翻转
anchor = (0.5, 0.5)

# 父节点全宽时：
px = cx / parent_w * 100.0  # u=2
py = cy                      # u=0

# 父节点固定尺寸时：
px = cx  # u=0
py = cy  # u=0
```

## 关联

- `references/cocosbase.md` — 坐标系/单位/锚点基础
- `references/figma-to-red-plistlib.md` — plistlib 生成规范
- `lessons/lesson_unit3_content_size_only.md` — unit=3 只能用于 contentSize
