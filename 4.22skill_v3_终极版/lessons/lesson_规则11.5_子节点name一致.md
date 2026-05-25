# Lesson: 规则 11.5 — 同结构多实例子节点 name 100% 一致

## 一句话

同结构多实例 FRAME (列表行 / 网格项 / 重复按钮组) 内部子节点 name **必须 100% 严格一致**, 否则 S11 `extract_components.py` 用 structural_fingerprint + 子节点命名判"是不是同一个 Component" 时**指纹不匹配**, 抽不出统一 Component。

## 易犯错的场景

8 个列表行实例, 每行写 children 时**手滑改了命名**:

```text
列表项_排名1            列表项_排名2            列表项_排名3
├── 底板_行             ├── 底板_排行行     ← name 漂移
├── 文本_排名           ├── 文本_排名号     ← name 漂移
├── 图标_头像框         ├── 图标_头像       ← name 漂移
└── 文本_名字           └── 文本_玩家名     ← name 漂移
```

### 后果

- 17 个排行榜行被识别成 **17 个独立 FRAME** (不抽 Component)
- 或部分聚类失败, 出现 `列表项_排名` + `列表项_排名_2` 两个独立 Component
- 设计师粘到 Figma 看到"看起来一样但是分散"的多个 Component Set

## 正确做法

```text
列表项_排名1            列表项_排名2            列表项_排名3
├── 底板_行             ├── 底板_行             ├── 底板_行
├── 文本_排名           ├── 文本_排名           ├── 文本_排名
├── 图标_头像框         ├── 图标_头像框         ├── 图标_头像框
└── 文本_名字           └── 文本_名字           └── 文本_名字
        ↑↑↑ 三个实例内部 name 100% 一致 ↑↑↑
```

实例间允许的差异**只能是视觉属性** (`fill` / `corner_radius` / `opacity` / `visible` / TEXT.content), **不能是命名差异**:

```text
✅ 列表项_排名6_当前用户          ❌ 列表项_当前
├── 底板_行 (fill: 绿色)          ├── 底板_当前用户行    ← name 变了
├── 文本_排名                      ├── 文本_排名
└── 图标_头像框                    └── 图标_当前头像框   ← name 变了
```

颜色 / 形状变 → ✅ S11 归到不同 Variant
**命名变 → ❌ S11 判成不同 Component**

## 怎么避免

决定一种 Component 的内部结构时, **先在心里固定一套命名模板**:

```text
列表项_xxx (模板, 写一次, 8 行复用)
├── 底板_行
├── 文本_排名
├── 图标_头像框
├── 文本_名字
└── 文本_分数
```

**所有实例都严格按这套模板填**, 不要每画一个就重起名。

## 跨节点情况: 子节点结构整体增删

如果某行 row 5 多了"角标_王冠" 而 row 6 没有:

❌ **错** (增删 children 表达显隐):
```
row 5 children: [底板_行, 文本_排名, 图标_头像框, 文本_名字, 角标_王冠]
row 6 children: [底板_行, 文本_排名, 图标_头像框, 文本_名字]   ← 缺一项
```

后果: row 5 / row 6 的 structural_fingerprint 不一致 → S11 抽不出统一 `列表项_排名` Component。

✅ **对** (children 数组结构一致, 用 visible:false 隐藏):
```
row 5 children: [底板_行, 文本_排名, 图标_头像框, 文本_名字, 角标_王冠]
                                                            ↑ visible:true
row 6 children: [底板_行, 文本_排名, 图标_头像框, 文本_名字, 角标_王冠]
                                                            ↑ visible:false
```

8 行 structural_fingerprint 一致 → S11 抽出统一 Component, visible 差异自动切多 Variant (含"空 Variant")。

## 来源

- 旧 04 skill 规则 11.5 (子 CCB 显隐铁律)
- 07d #1 (S7 阶段一禁止增删 children 表达显隐)
- RoyalPass 8 行命名漂移事件

## 关联

- `lesson_扁平vs_v206_schema.md` — 怎么扁平写 8 行
- 07d 文件 #1-#2 — 详细 children 结构铁律
