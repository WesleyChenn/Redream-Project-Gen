# S0 · 上下文 / 世界观

> 这个文件是**最先读的**, 给后续 S1-S11 步骤铺地基。
> 它**不是操作铁律清单** — 操作铁律在 00a-00d。
> 读完这里, 你应该建立完整的心智模型: 我在做什么、给谁做、产出什么、有哪些角色、用什么节点表达。

---

## 1. 我们在做什么

Claude 在这个工作流里担任**视觉识别 + JSON 生成**的角色。
输入是设计师录的 **Figma 视频或截图**; 输出是 **`scene.json`** — 一份描述屏幕结构、节点、布局、交互的中间产物。
这不是终端产品 — scene.json 还要经过 Figma 插件粘贴、设计师在 Figma 调整、导出回 JSON、再经工具链转 `.red` 给引擎运行。
Claude 是流水线的**第一站**, 不是终点。

---

## 2. 最终目的: .red 文件

scene.json 是中间产物, 最终目标是给 **Redream 引擎**运行的 `.red` 二进制文件。整个流水线:

```text
Figma 视频/截图
    ↓ Claude (S0-S11)
scene.json (扁平, 无 Component)
    ↓ Figma 插件粘贴
可编辑 Figma 文件
    ↓ 设计师调整 (Variant / overrides / Push to main component)
更新后的 scene.json (导出回)
    ↓ extract_components.py
v20.6 schema (含 components + INSTANCE)
    ↓ red_tool (Flask, /api/generate_red)
.red 文件 (Resources/控件库/<name>.red)
    ↓ Redream 引擎加载
运行时画面
```

Claude 生成的 JSON 越准确, 后续每一站需要返工的概率越低。

---

## 3. 协作的几方角色

| 角色 | 做什么 |
|---|---|
| **设计师** | 在 Figma 操作: 粘贴 JSON / 调整 Component Set / 操作 Variant / 导出回 JSON |
| **Claude (你)** | 看 Figma 视频或截图, 识别视觉 + 交互, 生成 scene.json |
| **工具链** | Figma 插件 / `extract_components.py` / `red_tool` (Flask) / `build-scene` CLI / `inspect check` |
| **引擎 (Redream)** | 运行时按 .red 文件渲染, 认 CCNode / CCSprite / CCProgressTimer / REDNodeButton 等 cocos2d-x 节点 |

---

## 4. 视觉模板的两个来源 (memory 主 / 组件库辅)

Claude 在 S6 识别视觉单元时, 需要参考两个模板源:

- **主参考: memory** — 项目积累的可复用视觉 pattern + 项目特定视觉先验。memory 由 Claude Code 自动加载, 它是 Claude 跨会话的"记忆库"。S6 步骤要逐一匹配每个视觉单元跟 memory 里的 pattern。
- **辅助: 旧组件库** — 历史遗留的 Figma 组件库 JSON 文件 (用户提供)。实际能 100% 命中的条目已不多, 仅作为补充。

**关键**: 旧组件库不是主要匹配源。
- 命中 memory pattern → 套模板生成 JSON 子树
- 命中旧组件库 100% → 用 `component_ref` 引用
- 都不命中 → 按操作铁律手搓

(memory 里具体有哪些 pattern, S6 步骤会详细告诉你。)

---

## 5. 项目固定参数

- **输出尺寸固定**: `1080 × 2400` (所有屏幕)
- **scale 计算**: `scale_x = 1080 / W`, `scale_y = 2400 / H` (W/H 是源视频/截图尺寸)
- **坐标量测**: 所有 x/y/w/h = 截图量测 × scale, **取整, 不估算**
- **录屏 H 注意**: 必须排除视频播放器自身 UI (顶部状态栏 / 底部控制条)

---

## 6. 核心哲学 (三条贯穿全程的最高原则)

### 6.1 零幻觉

图里看不到的元素, 绝对不写进 JSON。不脑补、不推断、不"为了完整性补一个"。

- ✅ 看到圆形按钮 → 写按钮节点
- ❌ "通常这种页面应该有返回按钮, 我加一个" → 即使常见也禁止

### 6.2 数据驱动 vs 状态多态分离

两种"变化"截然不同, 处理方式必须分清:

- **数据驱动**(种类无穷, 程序运行时填): 头像 / 玩家名 / 奖励物图标 — 占位 RECT, **不做 Variant**
- **状态多态**(屏幕里 2-10 种可枚举): 按钮的常态 / 激活 / 灰态 — Component + Variant

判断标准: 这个变化能枚举数完吗? 能 → Variant; 不能 → 占位 RECT。

### 6.3 不估算坐标

所有 x/y/w/h 必须从截图量测得出, 不允许"看起来差不多 30" 这种估算。

- ✅ 量了图, 写 32
- ❌ "应该 30 左右, 写 30"

### 6.4 相似项目产物不是捷径 (反 from-exemplar 锚定)

上下文里若已载入**某个相似项目的 scene.json / final_scene**(为复用结构而读入), 这是**风险信号**:

- ❌ "这屏跟 X 项目 80% 像, 照搬结构改增量" — 80% 像恰恰掩盖那 20% 它没有的(本次 Team Tournament 进度条事故根因)
- ✅ S3 表 C 每个组团**独立**从视频 + memory 重推, 相似样本只在字段写法 / 坐标体系层面借鉴
- 强制点: S6 完成后 inline 输出 ccb/多态决议表给用户 review, 逐组团过 memory A 表带 Read 凭证, 用户回 "决议 OK" 才进 S7 (这是 S0→S11 唯一停点, 其他 S 一气呵成不停)

---

## 7. 工作流总览 (S1→S11)

```text
S0  上下文 (你正在读的这个文件) — 装载世界观和心智模型
│
├─ 识别阶段 (全是"看", 输出"识别报告", 不写最终 JSON)
│   ├─ S1   抽帧
│   ├─ S2   识别页面内容
│   ├─ S3   识别布局 (按 06a 视觉缩窄机制递归找重复组团)
│   ├─ S4   识别交互
│   ├─ S5   提取 flow
│   ├─ S6   识别 pattern 命中
│   └─ S6a  ccb 抽取 3 标准判断 (复用/动态/独立, 不限嵌套层数)
│
├─ 生成阶段 (按识别 + pattern 模板组装 JSON)
│   ├─ S7   套 pattern 模板生成骨架
│   ├─ S8   少量组件库引用 (component_ref 字段精确化)
│   ├─ S8a  预制组件 (单一钟表特例 → frame 起名 `钟表_指针动画` 引擎自动复用)
│   ├─ S8b  组件库理论模型 (决策优先级 + 默认不需要"组件库" page)
│   └─ S9   字段补全 + overrides + flow 写入
│
└─ 校验 + 导出阶段
    ├─ S10  自检
    └─ S11  抽 Component + 导出
```

每步该做 / 不该做的具体契约在各步骤的独立 md 文件里 (S1.md ~ S11.md)。S0 只给你总览。

🔴 **分步确认工作流 (终极版 2026-05-22)**: **每个 S 步骤完成后必停下来等用户回复「继续 SX」**, 不要主动连跑。理由: 实证 (5.21-5.22 多轮测试) 证明分步确认的产物质量明显高于一气呵成 —— 每步用户 review 一眼能拦截 Phase A 识别错误 / S6 ccb 多态判断错 / S7 退化等问题, 避免错误连锁放大到下游导致整轮重跑。S6 决议表是最关键的停点 (ccb/多态判断), 但**S1/S2/.../S10 每步都停**, 不要只停 S6。详见 SKILL.md §工作流模式。

---

## 8. 需要包含什么内容

scene.json 最终要表达三类信息, 一个都不能少:

- **视觉**: 节点类型 (FRAME/RECT/TEXT/INSTANCE) / 嵌套层级 / 尺寸 / 颜色 / 命名
- **交互**: 哪些是按钮 (`按钮_xxx` FRAME) / 按钮跳转关系 (`flow` 数组, 含 `trigger: "ON_CLICK"`)
- **数据驱动占位**: 头像 / 奖励物图标 / 玩家名 等运行时填的位置, 用占位 RECT 标记

---

## 9. Figma 上的输出形态

scene.json 的顶层 schema (简化版):

```json
{
  "screens": [
    {
      "name": "界面_主菜单",
      "type": "FRAME",
      "w": 1080, "h": 2400,
      "layers": [ /* 屏幕顶层节点, 用 layers 不是 children */ ],
      "flow": [
        { "trigger": "ON_CLICK", "from": "按钮_开始", "to": "界面_关卡选择" }
      ]
    }
  ],
  "components": [ /* 阶段一 Claude 输出此项为空; 阶段二 extract_components.py 抽出后填充 */ ]
}
```

阶段一 Claude 输出**扁平 scene.json** (无 `components[]`); 阶段二经 `extract_components.py` 抽 Component 后变成 v20.6 schema。

---

## 10. 什么是界面 vs 浮层

| | `界面_` 屏幕 | `浮层_` 屏幕 |
|---|---|---|
| **视觉效果** | 全屏替换, 原画面完全消失 | 浮在原画面之上, 原画面变暗仍可见 |
| **转场动画** | `dissolve 300ms` | `OVERLAY` |
| **layers[0] 要求** | 可选全屏 `背景_xxx` RECT (有背景图时) | **必须**全屏 `遮罩_浮层背景` RECT |
| **典型 case** | 主菜单 / 关卡列表 / 活动页 | 确认弹窗 / 详情面板 / 设置 |

---

## 11. 四类节点 (+ 引擎侧对应)

Figma/JSON 侧只有四类节点, 但每类对应到引擎侧 (cocos2d-x) 的特定节点类型:

| Figma/JSON 侧 | 引擎侧 | 备注 |
|---|---|---|
| `FRAME` | `CCNode` | 容器, 永远无 fill |
| `RECTANGLE` | `CCSprite` | 视觉单元, fill 由插件按命名上色 |
| `TEXT` | `CCLabel` | 文字 |
| `INSTANCE` | **父 `CCNode` + 子 `REDFile` 两层** (v20.7.x) | 详见下面图示 |
| (主场景根) | `CCLayer` (v20.7.x 起仅主场景根用) | 子 CCB 不用 CCLayer |
| (Component 定义) | **子 CCB** (独立 .red 文件, 在 `Resources/控件库/<name>.red`) | Component Set 名字 = .red 文件名 |
| 特殊: `按钮_xxx` FRAME | `REDNodeButton` | 引擎只识别 `按钮_` 前缀的 FRAME 为触控层 |
| 特殊: 进度条 | `CCProgressTimer` | 不允许 FRAME 包装, 必须双层 RECT |

### INSTANCE 在引擎侧的两层结构 (v20.7.x)

```text
INSTANCE (Figma/JSON 侧, 一个节点)
    │ 编译成 ↓
    ▼
父 CCNode (承载 INSTANCE.name / 坐标 / 尺寸 / 约束)
└── 子 REDFile (引用 .red 文件 = 子 CCB)
        ├── animation = INSTANCE.variant 对应的 sequenceId
        └── reboltName = INSTANCE.name (留给行为树定位)
```

v20.7.x 之前 INSTANCE 扁平化成单个 REDFile; v20.7.x 起改两层 — 父 CCNode 管布局, 子 REDFile 只管引用。

---

## 12. 识别阶段 (整个流程的"看")

S1 到 S6 是**识别阶段** — 这阶段全是"看", **不是"生成"**。输出是"我看到了什么"的中间报告, **不是最终 JSON**。

> ⚠️ **抢跑警示**: 如果你在 S3 识别布局时已经开始写 layout JSON 字段, 你已经越界了 — 那是生成阶段 (S7) 的事。

识别阶段的 6 个子步骤, 由浅到深:

1. **S1 抽帧** — 从视频取截图
2. **S2 识别页面内容** — 节点 / 文字 / 图标 / 按钮边界。回答"屏幕里有什么"
3. **S3 识别布局** — 节点之间的排列方式 (NONE / HORIZ AL / VERT AL) + 缩放约束 (constraints)。回答"它们怎么排"
4. **S4 识别交互** — 滚动区域 + 对比相邻帧, 推断哪些按钮被点了 (按钮被点时通常有缩放/位移)
5. **S5 提取 flow** — 谁点击 → 切到哪个屏。需要 S4 的"点击识别" + 抽多帧的"切屏对比"
6. **S6 识别 pattern 命中** — 把识别出的视觉单元跟 memory 的 ui_pattern 比对, 命中 → 打标签 (留给 S7 套模板); 不命中 → 标记"手搓"

识别阶段产物是给生成阶段 (S7-S9) 消费的中间报告。

---

## 13. Component / Variant / 实例

三个概念是 Figma 复用机制的核心, 模型必须分清:

- **Component**: 可复用单元的**定义**, 在 `components[]` 数组里。例: `按钮_活动` 是一个 Component
- **Variant**: 同 Component 的不同视觉**状态**。例: `按钮_活动` 有 `常态` / `激活` / `空` 三个 Variant
- **实例 (INSTANCE)**: 屏幕里**实际放的引用**, 指向 Component + 选哪个 Variant + 自带 overrides 覆盖差异

### 完整示例 (1 个 Component / 3 个 Variants: 常态 / 激活 / 空)

```json
{
  "components": [
    {
      "name": "按钮_活动",
      "w": 200, "h": 200,
      "variants": [
        {
          "name": "常态",
          "layers": [
            { "type": "RECTANGLE", "name": "底板_活动",
              "x": 0, "y": 0, "w": 200, "h": 200, "corner_radius": 100 },
            { "type": "RECTANGLE", "name": "图标_活动",
              "x": 50, "y": 50, "w": 100, "h": 100 }
          ]
        },
        {
          "name": "激活",
          "layers": [
            { "type": "RECTANGLE", "name": "底板_活动",
              "x": 0, "y": 0, "w": 200, "h": 200, "corner_radius": 100 },
            { "type": "RECTANGLE", "name": "图标_活动",
              "x": 50, "y": 50, "w": 100, "h": 100 },
            { "type": "FRAME", "name": "角标_新",
              "x": 140, "y": 0, "w": 60, "h": 60, "layoutMode": "NONE",
              "children": [
                { "type": "RECTANGLE", "name": "底板_角标新",
                  "x": 0, "y": 0, "w": 60, "h": 60, "corner_radius": 30 }
              ]
            }
          ]
        },
        {
          "name": "空",
          "layers": []
        }
      ]
    }
  ],
  "screens": [{
    "name": "界面_主菜单",
    "layers": [
      {
        "type": "INSTANCE",
        "name": "按钮_活动1",
        "component_name": "按钮_活动",
        "variant": "激活",
        "w": 200, "h": 200,
        "overrides": {
          "图标_活动": "图标_活动金"
        }
      }
    ]
  }]
}
```

`空` Variant (`layers: []`) 用于"该位置该状态不显示", 比 `visible: false` 更语义化 — 引擎侧会生成空 sequence, 视觉空。

### 嵌套 CCB 三层模型

Component 内部可以嵌套引用其它 Component。复合视觉单元 (列表行 / 卡片 / 按钮组) 按三层建模:

| 层 | 是什么 | 例子 |
|---|---|---|
| **大 CCB** | 外层 Component, 被列表/网格复用的容器 | `列表项_排名` |
| **子 CCB INSTANCE** | 大 CCB 内部, 引用其它 Component 的实例 (自己也可能多 Variant) | `角标_王冠`, `排名圆` |
| **占位 RECT** | 单纯 `图片_xxx` / `图标_xxx` RECT, 运行时数据绑定 (**不做 Variant**) | `图片_头像` |

```text
列表项_排名 (大 CCB)
├─ 排名圆 (子 CCB INSTANCE)        ← 可独立复用, 自己也可能多 Variant
├─ 图片_头像 (占位 RECT)            ← 数据驱动, 不做 Variant
├─ 角标_王冠 (子 CCB INSTANCE)     ← 可隐藏: 用 INSTANCE.visible 或空 Variant
└─ 文本_玩家名 (TEXT 占位)
```

**子 CCB 显隐铁律 (概念级)**: 同 Component 的多个实例 children **必须结构一致**, 隐藏用 `visible: false` 或 `variant: "空"`, **禁止用增删 children 表达显隐** — 否则 extract_components 无法抽出统一 Component。

具体怎么按这个模型生成 JSON 的操作细则在 **S7 (套 pattern 模板生成骨架)** 里。

---

## 14. 触控 vs 装饰

引擎区分**可点击节点**和**视觉装饰**, 两者命名/位置规则不同:

| | 触控层 | 装饰 |
|---|---|---|
| **命名** | `按钮_xxx` FRAME (必须 `按钮_` 前缀) | `角标_` / `徽章_` / `底标_` / `图标_` 等 |
| **引擎类型** | `REDNodeButton` | 普通 CCNode / CCSprite |
| **可点击** | ✅ 可点击, 触发反馈 | ❌ 视觉跟随触控层, 但本身不响应点击 |
| **位置规则** | 自身是 FRAME | **必须**作为触控层 FRAME 的 `children`, 不可平级 |
| **触控范围** | = 自身 w×h, 装饰溢出部分不可点 | 跟随 children 视觉, 不扩大触控范围 |

---

## 15. Claude 不做的事

明确边界, 这些是 Claude 在任何步骤都禁止做的:

- ❌ **不写引擎代码** — Redream 引擎是别人的事, 不动 .red 内部、不改 cocos2d-x 节点实现
- ❌ **不改组件库内部** — 旧组件库结构由 Figma 维护, 不重写组件库条目
- ❌ **不擅自删 Component** — Component 列表是用户的设计决策, 想删必须先问
- ❌ **不脑补图里没有的元素** — 零幻觉 (见第 6.1 节)
- ❌ **不估算坐标** — 所有 x/y/w/h 必须量测, 不"看起来 30 左右就写 30" (见第 6.3 节)

---

> S0 结束。读完这 15 节, 你已经建立完整心智模型。
> 后续要做的: 跟着 S1 → S11 走, 每步只做该步性质的事 (识别 / 生成 / 校验), 不要抢跑。
> 操作铁律 (命名白名单、按钮分组、进度条建模、Variant 抽取 5 原则等) 在 00a-00d 里, 当前 S 步骤需要时再读对应铁律即可。
