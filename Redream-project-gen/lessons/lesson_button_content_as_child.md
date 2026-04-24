---
name: 按钮内容必须作为触控层的子节点
date: 2026-04-21
status: ✅ 已落地（交互规则）
source: Mengmeng plistlib 实战
---

# Lesson: 按钮点击缩放时内容要跟随

## 事件

按钮做点击缩放动画时发现：图标和文字**不跟随**触控层缩放，视觉上只有底板缩小，图标/文字位置不变。

## 根因

Redream 的缩放是对节点自身 + 其子树的 transform 操作。
若图标/文字与触控层（REDNodeButton）是**兄弟节点**，触控层缩放时它们不会一起缩。

## 规则

**按钮内容（图标 + 文字）必须作为触控层（REDNodeButton）的子节点，不是兄弟。**

### ✅ 正确结构

```
CCNode 容器（任意名称，内有触控层）
└── 底板_XXX (REDNodeButton)
    ├── 图标_XXX (CCSprite)     ← 子节点，缩放跟随
    └── 文本_XXX (CCRedLabel)   ← 子节点，缩放跟随
```

### ❌ 错误结构

```
CCNode 容器
├── 底板_XXX (REDNodeButton)
├── 图标_XXX (CCSprite)    ← 兄弟节点，缩放不跟随
└── 文本_XXX (CCRedLabel)  ← 兄弟节点，缩放不跟随
```

## 自动合并规则（plistlib 工具 app.py）

`app.py` 识别到 CCNode 容器内含 `is_btn_layer` 子节点时：
1. 判定为按钮容器
2. **自动把其他同级内容并入触控层下做子节点**

## 触控层识别（is_btn_layer）

```python
def is_btn_layer(name, node_type=''):
    if name.startswith('切图_底板_'):       # 老命名（任意 type）
        return True
    if (name.startswith('底板_')
            and not name.endswith('形状')
            and node_type.upper() == 'FRAME'):  # v19 新命名
        return True
    return False
```

**按钮容器识别**：不看名字前缀，看是否有 is_btn_layer 子节点。
- 有 → 是按钮容器（即使名字是 `组_Toggle_XXX` 也适用）
- 其他内容自动并入触控层

## CLI 下的处理

使用 CLI 构建时，需要**手动**保证按钮内容是 REDNodeButton 的子节点（通过 `modify add-node --parent` 指定父节点为触控层）。

CLI 不会自动合并兄弟节点 → 触控层子节点。构建 Figma → .red 映射逻辑时必须显式处理。

## 关联

- `references/figma-to-red-plistlib.md` — 按钮结构章节
- `references/red-node-patterns.md` — 按钮节点模式 B1-B4
- `lessons/lesson_button_as_container.md` — 按钮作为容器节点
