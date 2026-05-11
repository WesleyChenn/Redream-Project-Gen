# Lesson: "xx组" 类型节点必须用 Gp + 子节点 indent

**日期:** 2026-04-15
**状态:** ✅ 已落地（BeadsOut/FruitTruck 模板 + phase2 文档 + Cozy Shapes 结构图）

## 事件

Cozy Shapes 结构图 v1 里，顶部 HUD 卡片写了：
```json
{"label": "计数组", "type": "La"},
{"label": "图片_徽章底板", "type": "S"},
{"label": "文本_当前数", "type": "Lb"},
...
{"label": "进度条组", "type": "La"},
...
```

用户反馈：
> 对于节点中的 xx组（分组这个做得很好），我希望组节点后面的 tag 不再是定位区，而是新增一个**群组**tag，并且图中某个群组下的子节点**稍微往里缩进一些**，以表示父子级关系。

## 根因

"xx组" 是设计上的父子聚合关系（UI 设计常见），但我默认套用 `La`（定位区）导致两个问题：
1. 语义错误：群组 ≠ LayerArea；La 是运行时实际存在的容器节点，群组只是"结构图里的逻辑分组"
2. 视觉扁平：不缩进子节点，一眼看不出从属关系

## 规则（硬性）

### 规则 A：结构图里出现"xx组"命名 → 父必须 `Gp`

节点 label 含 "组"（如 `计数组` / `进度条组` / `按钮组`）→ `type: "Gp"`，tag 显示为 `群组`（淡紫色粗体）。

### 规则 B：Gp 父节点必须紧跟至少一个 `indent:1` 子节点

```json
{"label": "计数组", "type": "Gp"},
{"label": "图片_徽章底板", "type": "S",  "indent": 1},
{"label": "文本_当前数",   "type": "Lb", "indent": 1}
```

renderer 会自动渲染：
- 紫色 tag
- 子节点左边留 16px 缩进
- 子节点左边一条淡紫色竖线指示隶属

### 规则 C：目前只支持 1 层 indent

设计考量：结构图不是完整节点树，嵌套 2 层以上就该拆成独立 prefab 或用 desc 补说明。脚本自检断言 `indent >= 1` 的父必须是 `indent=0` 且 type=Gp。

## 何时用 Gp vs La/Ly

| 候选 | 选 Gp | 选 La/Ly |
|------|-------|----------|
| "按钮组/计数组/数据组" 这类 UI 聚合 | ✅ | ❌ |
| LayerArea 实际容器（限定区域） | ❌ | ✅ La |
| 全屏层（结果面板/蒙层） | ❌ | ✅ Ly |

判据：**"这个节点在运行时 Cocos/Redream 节点树里是不是一个真实的容器 Node？"** 是 → La/Ly；只是结构图里为了阅读分块 → Gp。

## How to apply

1. 画结构图前，对每张卡片的 nodes 列表扫一遍，所有 label 含"组"的条目标记为候选 Gp
2. 确定它是"逻辑聚合"而非"运行时容器"后改 type=Gp
3. 紧跟的聚合成员加 `indent: 1`
4. 生成 HTML 后肉眼确认子节点缩进渲染正常
5. 自检脚本（phase2 Step 8 第 4 条）会断言 indent 层级正确

## 实现细节

renderer 改动（BeadsOut/FruitTruck 模板同步）：
- `ND_LABELS['Gp'] = '群组'`, `ND_COLOR['Gp'] = '#a78bfa'`
- `.nb-Gp` CSS：淡紫色背景 + 粗体
- `.nd-row.nd-indent`：左侧淡紫竖线 + padding-left 16px
- 节点循环内读 `nd.indent`，存在时附加 class + inline padding

## 关联

- `templates/BeadsOut_structure.html` / `FruitTruck_structure.html`：已加 Gp 支持
- `phases/phase2-structure-diagram.md`：节点类型速查表已列 Gp；Step 8 自检加 indent 断言
