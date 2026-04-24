---
name: 坐标约束判断流程（Figma → .red）
date: 2026-04-23
status: ✅ 已落地（处理流程）
source: RED Tool 实战（CLI 驱动版仍适用）
scope: 所有生成 .red 的工作流，映射逻辑由 Python/工具代码执行
---

# Lesson: 从 Figma 布局推导 .red 坐标约束

## 背景

Figma 的布局信息（constraints.horizontal / constraints.vertical + 绝对 x/y/w/h）需要正确映射到 Redream 的 position + contentSize + anchorPoint，多分辨率下才不会错位。

## 处理流程（四步法）

### Step 1 — 算所有顶层节点的绝对边距

```python
左边距 = x
右边距 = sw - (x + w)
上边距 = y
下边距 = sh - (y + h)
```

其中 `sw / sh` 是父容器（通常是屏幕，1080×2400）的尺寸。

### Step 2 — 判断全宽

```
horizontal == 'SCALE'             → 全宽
horizontal == 'LEFT' 且 右边距<10  → 视作全宽（容差）
其他                               → 固定宽
```

### Step 3 — 找贴边节点

扫描所有顶层节点：
- 找**上边距最小**的节点 → TOP 贴顶
- 找**下边距最小**的节点 → BOTTOM 贴底

### Step 4 — 多个同向贴边节点自动合并

如果有多个 TOP 节点（如顶部 UI 栏 + 状态栏）→ 合并成 `组_顶部合并`
如果有多个 BOTTOM 节点（如底部导航 + 进度条）→ 合并成 `组_底部合并`

**合并容器：**
```
组_顶部合并 / 组_底部合并
  宽 = 100% u=2
  高 = 所有子节点总高（固定 px u=0）
  贴顶/贴底
```

**合并后内部子节点：**
```
pos x = 50% u=2          # 居中
pos y = 绝对 px u=0      # 在合并容器内的位置
宽    = 100% u=2         # 必须全宽，不能写固定 1080px
高    = 固定 px u=0
```

## 输出映射表

### 全宽节点（宽=100% u=2，高=固定 px u=0）

| vertical | pos x | pos y | anchor |
|---|---|---|---|
| TOP | 50% u=2 | 100% u=2 | (0.5, 1.0) |
| BOTTOM | 50% u=2 | 0% u=2 | (0.5, 0.0) |
| SCALE/CENTER | 50% u=2 | 50% u=2 | (0.5, 0.5) |

### 固定宽节点（宽=固定 px u=0，高=固定 px u=0）

**水平方向（按绝对坐标对称性）：**

| 情况 | pos x | anchor x |
|------|-------|----------|
| 左 ≈ 右（差<10） | 50% u=2 | 0.5 |
| 左 < 右 | 左边距 u=0 | 0.0 |
| 左 > 右 | (100% - 右边距) u=0 | 1.0 |

**垂直方向：**

| vertical | pos y | anchor y |
|---|---|---|
| CENTER | 50% u=2 | 0.5 |
| TOP | 100% u=2 | 1.0 |
| BOTTOM | 0% u=2 | 0.0 |

## 子节点坐标

```python
# Cocos 坐标系（左下原点），从 Figma（左上原点）转换：
cx = fx + w / 2.0
cy = parent_h - fy - h / 2.0
anchor = (0.5, 0.5)

# 若父节点全宽 → x 用百分比，y 用绝对值
if parent_fullwidth:
    px = cx / parent_w * 100.0   # u=2
    py = cy                       # u=0
else:  # 父节点固定尺寸
    px = cx   # u=0
    py = cy   # u=0
```

## 合并容器内子节点的特殊规则

**内部子节点必须全宽**（即使视觉上没占满）：

```python
# ✅ 正确
pos x = 50% u=2
size w = 100% u=2

# ❌ 错误（偏宽分辨率 1560 时内容错位）
pos x = 540 u=0
size w = 1080 u=0
```

原因：合并容器本身是全宽，子节点若固定 1080px，在 1560×2080 分辨率下会偏左，无法跟随父宽度缩放。

## 调试技巧

- 设计分辨率（1080×2400）下看不出约束错误
- 必须切换到**偏宽（1560×2080）**或**偏高（1080×2800）**才能暴露问题
- 改完文件**必须重启 Redream**，不支持热重载

## CLI 下的处理

CLI 命令直接接受 `position` 和 `contentSize` 的 `"x,y,xUnit,yUnit,corner"` 格式字符串。映射逻辑（判断全宽、找贴边、合并同向）需要由**调用 CLI 的工具代码**完成，CLI 本身只是执行器。

## 关联

- `references/figma-to-red-cli-driven.md` — 坐标系统章节
- `references/cocosbase.md` — 坐标/单位基础
- `references/cli-modify.md` — position / contentSize 格式
