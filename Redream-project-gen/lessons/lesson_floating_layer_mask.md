---
name: 浮层屏幕必须有放穿透层 + 遮罩_背景
date: 2026-04-23
status: ✅ 已落地（结构规则）
source: Mengmeng plistlib 实战
---

# Lesson: 浮层屏幕必须屏蔽底层交互

## 事件

浮层屏幕（如 `浮层_設定`）显示时，**底层界面的按钮仍然可点**，导致误触；背景也**不够暗**，与主界面视觉没拉开对比。

## 根因

浮层屏幕默认只渲染弹窗内容，没有：
1. **防穿透层** — 覆盖全屏的透明点击响应，拦截所有底层交互
2. **半透明遮罩** — 降低底层视觉存在感

## 规则

所有以 `浮层_` 开头的屏幕，`scene_root` 下必须有这两个节点，**在弹窗内容之前**：

```
scene_root (浮层_XXX)
├── 放穿透层 REDNodeButton
│   pos=[50%, 50% u=2, 2]
│   size=[100%, 100% u=2, 2]
│   ccControl=['', 1, 32]
│   preferedSize=[100%, 100% u=2, 2]
│
├── 遮罩_背景 CCLayerColor
│   pos=[50%, 50% u=2, 2]
│   size=[100%, 100% u=2, 2]
│   color=[0, 0, 0]
│   opacity=178       # ~70%，可调
│
└── 弹窗_XXX CCNode   ← 实际弹窗内容
    pos=[50%, 50% u=2, 2]
    size=[固定 px, 固定 px u=0, 0]
```

## 节点分工

| 节点 | 类型 | 职责 |
|------|------|------|
| 放穿透层 | REDNodeButton | 拦截触摸，让底层按钮不响应 |
| 遮罩_背景 | CCLayerColor | 视觉半透明遮罩，黑色 opacity=178 |
| 弹窗_XXX | CCNode | 实际弹窗内容 |

## 渲染顺序

三个节点的**先后顺序很重要**：放穿透层 → 遮罩_背景 → 弹窗。
Cocos 渲染按加入顺序从下往上，后加入的压在上面。

## 自动生成规则（plistlib 工具 app.py）

`app.py` 识别屏幕名以 `浮层_` 开头时，**自动**在 scene_root 最底层注入这两个节点。用户在 Figma 里不需要手动画防穿透层。

## CLI 下的处理

使用 CLI 构建浮层时，需要**手动**加这两个节点：

```bash
# 1. 放穿透层
modify add-node --scene 浮层_XXX.red --parent CCLayer/浮层_XXX \
    --type REDNodeButton --name 放穿透层 \
    --property "position=50,50,2,2,0" \
    --property "contentSize=100,100,2,2" \
    --property "ccControl=,1,32" \
    --property "preferedSize=100,100,2,2"

# 2. 遮罩_背景
modify add-node --scene 浮层_XXX.red --parent CCLayer/浮层_XXX \
    --type CCLayerColor --name 遮罩_背景 \
    --property "position=50,50,2,2,0" \
    --property "contentSize=100,100,2,2" \
    --property "color=0,0,0" \
    --property "opacity=178"

# 3. 弹窗内容 ...
```

CLI 命令格式以 `references/cli-modify.md` 为准。

## 关联

- `references/figma-to-red-plistlib.md` — 浮层屏幕章节
- `references/node-tree-standards.md` — 弹窗标准结构（3.2 节）
- `phase1-figma-json/00_core_rules.md` — 浮层遮罩铁律
