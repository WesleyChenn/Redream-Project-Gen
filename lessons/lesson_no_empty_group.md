# Lesson: 空壳 Gp 禁令 — 组外无兄弟节点时组本身无意义

**日期:** 2026-04-15
**状态:** ✅ 已落地（Cozy Shapes top_hud 去 `计数组` Gp）
**适用范围:** Redream-project-gen + cocos-project-gen（cocos 尤其敏感，因节点层级是运行时开销）

## 事件

Cozy Shapes 关卡进度 prefab (`top_hud`) 原结构：

```
计数组 (Gp)
├─ 图片_徽章底板 (S, indent=1)
├─ 文本_当前数 (Lb, indent=1)
├─ 文本_分隔符 (Lb, indent=1)
└─ 文本_总数 (Lb, indent=1)
```

组的兄弟节点只有它自己，组外没有其他内容。用户反馈：

> 关卡进度prefab不需要计数组，因为组之外没有别的节点，那么组就没有意义（特别是在cocos项目）

## 根因

`Gp`（Group）在结构图里的唯一价值是**把一组节点圈起来与组外其它节点区分**。当 prefab 里所有节点都是这个组的子节点时：
- 视觉上等价于"prefab 根节点本身就是这个组"
- cocos 工程里会多一层空层，浪费一个节点对象（影响少量性能 + 增加 transform 计算）
- 结构图上占一行 indent 噪声，阅读脑力成本高

## 规则

**结构图的 `type:"Gp"` 节点必须满足以下之一：**

1. **有兄弟节点**：该组节点的同级（组外）至少还有一个其它节点 / 组，说明此组承担"圈选一块内容与其他并列"的职责
2. **有分组复用语义**：组表示"可开关的子结构"（如 HUD 的某一区域可整体隐藏/切换），cocos 里确实需要一个空层做 active toggle 的锚点

**否则必须拆散**：Gp 节点删除，子节点全部 indent-1 直接挂 prefab 根。

## Why

- **cocos 性能敏感**：空分组节点每帧都参与 transform 计算与 batch 判定，海量空层会显著影响渲染批次合并
- **信号降噪**：prefab 的 nodes[] 列出来就是给读者梳理视觉/交互元素，多一层空壳是信息噪音
- **结构图一致性**：Gp 在读者眼里是"这里有一组独立单元"，空壳 Gp 会误导读者以为组外还有内容，读完发现没有就感觉被骗

## How to apply

### 生成器自检

prefab 的 nodes 列表生成后扫一遍：

```python
for card in cards_list:
    gps = [i for i, n in enumerate(card["nodes"]) if n["type"] == "Gp"]
    for gp_idx in gps:
        # 组的范围 = 自 gp_idx+1 起所有 indent>gp.indent 的连续节点
        gp_indent = card["nodes"][gp_idx].get("indent", 0)
        children_end = gp_idx + 1
        while children_end < len(card["nodes"]) and \
              card["nodes"][children_end].get("indent", 0) > gp_indent:
            children_end += 1
        # 组外（同 indent 或更低）是否有兄弟节点？
        siblings = [n for n in card["nodes"]
                    if n.get("indent", 0) == gp_indent and n is not card["nodes"][gp_idx]]
        if not siblings:
            print(f"⚠️  {card['id']}.{card['nodes'][gp_idx]['label']} 空壳 Gp，组外无兄弟")
```

### 设计侧的自问

画 prefab 结构时，对每个想用 Gp 的节点问一次：
- 组外还有别的节点/组吗？→ 没有则删组
- 这个组有单独的 active/visible 开关需求吗？→ 没有则删组

### 反模式

```
❌  prefab_foo
    └─ UI组 (Gp)
        ├─ 图片_底 (S)
        └─ 文本_标题 (Lb)
```

```
✅  prefab_foo
    ├─ 图片_底 (S)
    └─ 文本_标题 (Lb)
```

## 关联

- `feedback_node_naming_by_function.md`（全局）：Gp 名字也按功能，但首先得问这个组该不该存在
- `feedback_fix_then_audit_similar.md`（全局）：应用本规则时全项目 grep `"type":"Gp"` 逐个复核
- cocos-project-gen/lessons/lesson_no_empty_group.md：指针（两个 skill 共享同一结构图模板）
