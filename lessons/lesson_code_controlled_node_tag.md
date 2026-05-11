---
name: 程控节点独立 tag（Cocos 专用）
description: Cocos 工程中代码直接读写 props 的节点必须用独立 </> tag 标注；Redream 用 Rebolt 变量/函数间接访问，不需要标
type: feedback
---

# Lesson: 结构图节点"程控"维度（Cocos 专用）

**日期:** 2026-04-15
**状态:** ✅ 已落地（Cozy Shapes 7 个节点加标：board.毛线/填充绘制层、top_hud.文本_关卡进度、number_label(_progress).文本_数字、number_label_progress.进度条_连线进度、text_feedback.文本_反馈文字）
**更新:** 2026-04-15 二次修订 — 限定为 Cocos 项目专用；tag 文案 "程控" → "</>"

## 适用范围

**仅 Cocos 工程需要 </> tag，Redream 不需要。**

原因：Cocos 没有 Rebolt 这样的行为层脚本系统，所有状态变化都要求代码 `getChildByName`/直接 setString/setProgress/Graphics 绘制访问节点 props。不标注则接手工程师要么翻脚本反推、要么把所有叶子节点当候选绑定点处理。

Redream 则有 Rebolt 提供变量/函数间接层（数据驱动）：结构图节点不会被代码直接引用，只会被 Rebolt **函数** 通过 **变量** 间接修改。因此 Redream 结构图里不出现 </> 标注。

### 对照示例：关卡进度文本

| 引擎 | 实现 | 结构图标注 |
|------|------|----------|
| **Cocos** | 脚本 `topHud.getChildByName('文本_关卡进度').getComponent(Label).string = "LEVEL 1/3"` | `{"label":"文本_关卡进度","type":"Lb","ctrl":True}` → 渲染出 `</>` badge |
| **Redream** | Rebolt 添加变量 `关卡进度值:String` + 函数 `更新关卡进度(值)`；时间线/事件调用函数；节点绑定变量自动显示 | `{"label":"文本_关卡进度","type":"Lb"}` → 不加 ctrl，Rebolt 侧 vars/funcs 承担程控契约 |

两种实现都让文本变化，但节点在脚本中的暴露面不同：Cocos 暴露节点，Redream 暴露变量。

## 事件

用户指出：
> 需要程序控制的节点也需要用独立的 tag 标注出来，例如数字标签中的「文本_数字」、「进度条_连线进度」、关卡进度中的「文本_关卡进度」等。

后续又限定：
> 这个程序控制标签的规则是对于 Cocos 项目而言的，因为 Cocos 没有 Rebolt 的程序变量来让程序间接地控制节点属性。Redream 项目中只需要在 Rebolt 里添加一个更新进度的函数以及一个进度值的程序变量即可。程序控制的 Tag 用「</>」表示。

之前结构图只有一个 type tag（S/Lb/Sp/N/La/Ly/Pos/Gp/Pb/Btn）。这条维度只回答"这是什么技术类型"，不回答"**代码是否直接访问这个节点**"。

## 根因

**type tag 和"程控"是正交维度，且仅在 Cocos 场景出现**：

- 两个 `Lb` 节点看起来一样，但一个可能是"纯美术固定文案"（"点击开始"），另一个是代码 `setString` 驱动（"7/10"）——type 一样、运行时语义天差地别
- 两个 `Ly` 层一个是挂载 prefab 的定位层，另一个是代码 Graphics 动态绘制——type 一样，但后者工程必须引用
- Cocos 接手的工程师如果不翻脚本，看不出哪些节点是"代码的锚点"
- Redream 则不存在这个问题：没有 Rebolt 变量/函数绑定的节点，代码根本够不到它

结果是：结构图作为 Cocos 工程交付物时，缺一维工程信息；迁移到 Redream 时，这一维自动失效。

## 规则

### R0 — 仅 Cocos 项目启用 </> 标注

- Redream 项目生成结构图时不使用 `ctrl` 字段，面板/badge 不显示
- Cocos 项目或 Cocos→Redream 迁移前的源结构图，按 R1-R3 标注
- 结构图 meta 信息里可加 `project_type: "Cocos"` 触发 </> 渲染（可选实现）

### R1 — 独立 ctrl 布尔字段，badge 渲染为 </>

节点对象扩展：
```python
{"label": "文本_数字", "type": "Lb", "ctrl": True}  # 代码 setString 驱动
```

渲染：type badge 右侧追加一个 "</>" badge，使用 monospace 字体，pink 底色（`rgba(244,114,182,.18)`，前景 `#f9a8d4`），与 type tag 分开显示。

文案选择理由：
- "</>"是代码/标签的通用视觉符号，一眼可辨"这是程序入口"
- monospace 字体强化"代码"语义
- 比中文"程控"更国际化、更短、更像工程标签

### R2 — 判定标准：代码"直接写 props"（仅 Cocos）

Cocos 场景下标 `ctrl: True` 的典型：
- `Lb` — 代码 `setString` / 国际化切换文案
- `Pb` — 代码 `progress = x`
- `S` — 代码 `spriteFrame = SpriteFrame.xxx`（换图）
- `Ly` / `Gp` — 代码 `Graphics.moveTo/lineTo/fill`（动态绘制）
- `N` — 代码 `instantiate(...)` 作为运行时实例化父（若非已有 dyn conn 标注时）

**不**标 `ctrl`：
- **由 timeline 驱动**的 `active` / `alpha` / `scale`（时间线本身是"数据驱动"，不是脚本侵入）
- **定位区/挂载父 La**（stub/dyn conn 已经表达这层关系）
- **ref 坐标源 N/Pos**（ref 连线已经表达这层关系）
- **纯美术装饰节点**（背景、装饰图、呼吸动画由 timeline 管的图片）

判定一句话：**工程师是否需要在脚本里 `getChildByName` / 绑定属性引用这个节点？** 需要 → 标。

### R3 — 工程契约

结构图里带 `</>` 标的节点 = **脚本强契约** = 重命名/删除必须同步改代码。

命名改动时，`grep -n "nb-ctrl" <structure.html>` 即可一次列出所有工程强引用点。

## Why

- 三种受众读结构图：
  1. 策划看功能/交互 → 用 name/desc/timeline/func/notif
  2. 美术看视觉层级 → 用 type tag + indent
  3. **Cocos 工程看代码锚点 → 需要 </> tag**（之前缺失）
- 没有 </> 标注时，Cocos 工程同学要么翻脚本反推，要么把所有叶子节点当可能的绑定点处理，都是浪费
- 加一个布尔 + pink badge 成本极低，但把"代码强引用"从隐性知识变成显性契约
- Redream 的 Rebolt 天然用"变量/函数"两层把"脚本侵入"转成"数据契约"，节点侧无需再标

## How to apply

### 设计结构时（Cocos 项目）

写 prefab nodes 的同时，对每个叶子节点自问："这个节点的 props 是由 timeline 还是代码写的？" 代码 → 加 `ctrl: True`。

### 设计结构时（Redream 项目）

不写 ctrl 字段。凡是需要动态变化的值，在 Rebolt 侧建变量，用函数更新，节点只要绑定变量即可。

### 跨引擎迁移（Cocos → Redream）

- 源结构图（Cocos 视角）保留 `ctrl` 标注，用作"这些节点必须在 Redream 用 Rebolt 变量+函数包装"的 checklist
- 目标结构图（Redream 视角）去掉 `ctrl`，把每个原标注节点的"代码行为"在 Rebolt 侧落为变量+函数对
- 关联：`~/.claude/projects/-Users-liuying/memory/_global/feedback_cross_engine_terminology.md`

### 自检（生成器）

```bash
# Cocos 项目：列出所有 </> 节点
grep -o '"ctrl": True' gen.py | wc -l

# 反查：所有 Lb/Pb 是否该标 ctrl
grep -nE '"type": "(Lb|Pb)"' gen.py  # 逐行复核

# Redream 项目：不应有 ctrl 字段
grep -n '"ctrl"' redream_gen.py && echo "ERROR: Redream 项目不应有 ctrl 字段"
```

### 模板要件

结构图 HTML 模板需要：
1. CSS `.nb-ctrl { background:rgba(244,114,182,.18); color:#f9a8d4; font-family:ui-monospace,...; ... }`
2. 节点渲染：`${nd.ctrl?'<span class="nd-badge nb-ctrl" title="Cocos 工程：代码直接读写...">&lt;/&gt;</span>':''}`
3. 属性面板勾选框（编辑态），label 用 `&lt;/&gt;`（monospace）

已落地的模板：
- `skills/Redream-project-gen/templates/BeadsOut_structure.html`
- `skills/Redream-project-gen/templates/FruitTruck_structure.html`

## 关联

- `lesson_button_as_container.md` — 同样是"type 系统扩展"的姐妹 lesson（Btn 作为一级 type）
- `~/.claude/projects/-Users-liuying/memory/_global/feedback_node_naming_by_function.md` — label vs type tag 的分工契约；本规则引入第三维 ctrl tag，与前两维正交
- `~/.claude/projects/-Users-liuying/memory/_global/feedback_cross_engine_terminology.md` — Cocos→Redream 迁移时产物不应泄漏源引擎概念；本规则是跨引擎差异的具体表现
- `~/.claude/projects/-Users-liuying/memory/_global/feedback_rebolt_lifecycle_via_notif.md` — prefab 不直接访问外部状态；Rebolt 层承担了 Cocos 结构图里 </> 所描述的职责
