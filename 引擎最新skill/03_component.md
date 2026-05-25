# 封装方案(Component / Variant / 组级 keyframe / 空 Variant)

> 引擎 SKILL 拆分文档(v20.7.x+,2026-05-11) · 索引见 SKILL.md

---

## 八、封装方案（V1 完整规范）

### 8.1 何时做成 Component Set(ccb 抽取 3 标准, 2026-05-15)

#### 引擎护栏:`_detect_repeated_inline_structures` (app.py, 2026-05-15)

`generate_red()` 在 `register_component_variants` 之后跑一次,扫主屏 inline 节点找"同结构签名 ≥3 次但没在 `components[]` 声明的"。

签名:`(name 前缀去尾部数字, type, 直接 children 的 (name 前缀, type) 序列)`。`列表项_19 / 列表项_20 / ...` 都归到 `列表项` 这一签名。

命中后日志输出:
```
━━━ 重复 inline 结构检测 (视觉缩窄机制护栏) ━━━
  ⚠️  inline 结构 "列表项" 在主屏出现 8 次但未在 components[] 声明
      节点样本: ['列表项_19', '列表项_20', ...]
      建议:Claude 在 S6 阶段按 4.22 SKILL 00f ccb 3 标准 #1 (复用) 抽为子 ccb
```

**不自动抽**(避免误判),只 warning 提示 Claude/设计师在 4.22 SKILL S3-S6 阶段补抽。

跳过条件:
- `name in PREFAB_NAMES`(已走预制路径)
- `name in declared`(已在 components[] 声明)
- `type == 'INSTANCE'` 或带 `component_ref`(已是组件引用)
- 直接 children 数 < 2(避免叶子节点误判)

---

#### 抽取标准

满足任一即做(参考 [`4.22最新skill/00f_视觉缩窄_ccb_3标准.md`](/Users/red/Desktop/4.22最新skill/00f_视觉缩窄_ccb_3标准.md)):

- **复用**:同一节点结构在 Figma 多处出现(`列表项 / 组_气泡底板 / 组_奖励` 等)
- **动态**:运行时代码动态实例化(背包格子、列表 cell 等)
- **独立**:有独立动画或行为(`钟表_指针动画` 走预制特例;其他 spine 动画等)

**判断方法**:Claude 在 4.22 SKILL S3 阶段按 **视觉缩窄机制**(递归下钻找重复结构)走,每一层稳定结构用 3 标准判断;**不限缩窄层数,该抽就抽**。

注:**ccb 嵌套层数 ≠ Variant 粒度**(两者不是同一回事)。一句话核心原则(2026-05-17):
- **多态(Variant)= 最小化** — 抽 Variant 让被复用组件**尽可能小**(差异下沉到最小变化单元),见 [`4.22最新skill/00d`](/Users/red/Desktop/4.22最新skill/00d_Variant抽取与修复.md)
- **子 ccb = 最大化** — 抽子 ccb 让复用**尽可能多次发生**(能复用就抽,层数不限),见 [`4.22最新skill/00f`](/Users/red/Desktop/4.22最新skill/00f_视觉缩窄_ccb_3标准.md)
- ccb 决定"抽什么出来反复用",Variant 决定"这个被反复用的东西内部差异压到多小"

### 8.2 何时给 Component Set 加 Variants

- **状态多态**：同一节点结构有有限离散视觉差异

**不算多态**（不做 Variant，运行时填数据）：

- 文本字符串
- 数字
- 图片资源（url 驱动 / 列表数据）
- 进度条百分比

判断"图片是不是多态"：能在 Figma 设计稿枚举完 → Variant；枚举不完 → 数据。

### 8.3 Variant 命名约束

- **每个 Component Set 只能有 1 个 Variant Property**（多 Property 报错）
- **Property 名固定为"状态"**
- **Property 取值数量不限**（"常态/选中/禁用/已领取/未解锁" 5 个值都允许）
- **默认 Variant 必须叫"常态"**（对应 sequenceId=0）

### 8.4 Component → 子 CCB 文件名映射 (v20.7.x+ 2026-05-15 重构后)

```
Figma Component Set "排行榜行"   →  ccb/<module>/排行榜行.red
                                     (module = 主屏 scene_name, 跟主屏放同一目录)

Figma 内部 Variant "排行榜行=常态"
                  "排行榜行=带徽章"   →  同一个 .red 内的多条 sequence
                  "排行榜行=带道具"
```

注意 (2026-05-15): 之前是 `Resources/ccb/排行榜行.red` (Resources 中间层), 现已对齐生产 `res_juice_pro/ccb/<模块>/<name>.red` 结构. 主屏 .red 也在同模块目录下。
INSTANCE 引用子 CCB 时, redFile 写 `<module>/<comp>.red`(相对 ccb resource path).

- Component Set 名字 = 子 CCB 文件名（去掉 `=Variant` 后缀）
- 命名禁止字符：`/ \ : * ? " < > |` 和空格
- 重名自动加序号后缀（`_2` / `_3`）

### 8.5 Variant → sequence 映射

每个 Variant 对应一条 sequence：

- 默认 Variant → sequenceId=0, name="常态"
- 其他 Variant 按顺序递增 sequenceId
- 所有 sequence: `length=0.067` 秒（2 帧/30fps），`autoPlay=false`，`chainedSequenceId=-1`
- 5 个 channel（callback/shake/shake2/sound/wise）keyframes 都为空

### 8.6 V1 实装的差异属性（v20.7.x）

| 属性 | 状态 | 触发条件 | type |
|---|---|---|---|
| `visible` | ✅ V1 实装 | layer 的 `visible: true/false` 字段 | 1 |
| `color` / `fill` | ✅ V1 实装 | layer 的 `fill: "#RRGGBB"` 字段 | 6 |
| `opacity` | ⏸️ 未实装 | (V1 暂无典型用例) | 5 |
| `position` | ⏸️ 不实装 | Figma Variants 结构强制一致 | 3 |
| `scale` | ⏸️ 不实装 | 同上 | 4 |
| `rotation` | ⏸️ 不实装 | V1 限制 | 2 |
| `displayFrame` | ⏸️ 不实装 | 图片走数据驱动 | 7 |

**完全不支持**（属于运行时数据，不进 sequence）：
- TEXT.content 字符串差异（运行时由代码注入）
- 数字、图片 url
- size (w/h) 差异

### 8.7 keyframe 数据格式（v20.7.x 已实施）

动画数据挂在节点上而非 sequence 上：

```python
节点的 animatedProperties = {
    "<sequenceId>": {                # 字符串化的 seqId
        "<属性名>": {
            "keyframes": [
                {
                    "easing":     {"type": 0},
                    "name":       "<属性名>",
                    "pathValues": [],            # 仅 position 用
                    "time":       0.0,
                    "type":       <type 编号>,
                    "value":      <属性值>,
                }
            ],
            "name": "<属性名>",
            "type": <type 编号>,
        }
    }
}
```

**Keyframe type 编号**（从生产样本 res_juice_pro 提取）：

```
visible       type=1, value=True/False
rotation      type=2, value=float
position      type=3, value=[x, y]
scale         type=4, value=[sx, sy]
opacity       type=5, value=int(0-255)
color         type=6, value=[r, g, b]      # 推断（生产样本无现成）
displayFrame  type=7, value=[png_file, plist_file]
animation     type=15
```

**Easing type**：0=无 / 1=linear / 12=用户自定义（in-out cubic 等）/ 18=自定义贝塞尔（opt=参数）。
V1 variant 切换都是 time=0 单帧静态快照，统一用 `easing.type=0`。

### 8.8 主场景里 INSTANCE → 父 CCNode + 子 REDFile 两层（v20.7.x）

INSTANCE 不再扁平化成单个 REDFile，而是**父 CCNode + 子 REDFile** 两层：

```
列表项_排名6 (CCNode)              ← 父节点，承载坐标/尺寸/约束
├── position = INSTANCE 在场景里的位置
├── contentSize = (w, h)           ← 真实尺寸（响应式 constraints 依赖这个）
├── anchorPoint = (0.5, 0.5)
└── 子节点：
    列表项_排名 (REDFile)            ← displayName = 组件名（一眼看出引用哪个 CCB）
    ├── position = (w/2, h/2)      ← 父中心，锚点对齐
    ├── anchorPoint = (0.5, 0.5)
    ├── opacity = 255
    ├── color = [255, 255, 255]
    ├── redFile = "ccb/列表项_排名.red"
    ├── animation = 4              ← 按 INSTANCE.variant 映射 sequenceId（"当前用户"→4）
    ├── reboltId = {12位随机ID}
    └── reboltName = INSTANCE.name   ← "列表项_排名6"，留给行为树定位用
```

**为什么分两层**：

- 父 CCNode 承载布局责任（constraints / 坐标 / 尺寸），子 REDFile 只管引用
- Redream 编辑器里能看到父 CCNode 的边界框（响应式 SCALE/TOP/LEFT 才有尺寸基准）
- 未来要在父 CCNode 上加额外装饰节点（姊妹节点）也方便

**关键约定**：

- 父 CCNode `displayName` = INSTANCE.name（保留 Figma 语义命名）
- 子 REDFile `displayName` = **组件名**（如"列表项_排名"，所有同组件实例的子 REDFile displayName 一致，方便对照引用）
- 子 REDFile 不写 `contentSize`（由子 CCB 自己决定渲染尺寸）
- `animation` = INSTANCE.variant 对应的 sequenceId（v20.7.x 加：按 variant 映射，详见 8.9）
- `reboltName` 写在子 REDFile 上，等于 INSTANCE.name，行为树通过 reboltName 定位 instance

### 8.9 INSTANCE.variant → sequenceId 映射（v20.7.x）

主屏生成时，每个 INSTANCE 的 `animation` 字段不再统一写 0，而是**按 INSTANCE.variant 映射成对应的 sequenceId**：

```python
# app.py 模块级映射，主屏生成前由 register_component_variants(components) 填充
_COMPONENT_VARIANT_SEQID = {
    '列表项_排名': {
        '常态':         0,   # is_default → sequenceId 0
        '有头衔无道具': 1,
        '无头衔有道具': 2,
        '有头衔有道具': 3,
        '当前用户':     4,
    },
    ...
}
```

映射规则与 `generate_red_component()` 里 sequences 的构造严格一致：

- `is_default=True` 的 Variant → sequenceId = 0
- 若无 is_default 标记，第一个 Variant 视为默认 → sequenceId = 0
- 其他 Variants 按出现顺序递增 sequenceId
- INSTANCE.variant 在表里查不到 → 回退 0（常态）

**实例**（17 个 INSTANCE 引用同一个 `列表项_排名.red`）：

| INSTANCE | variant | 子 REDFile.animation |
|---|---|---|
| 列表项_排名5 | 常态 | 0 |
| 列表项_排名6 | 当前用户 | 4 |
| 列表项_排名2 | 有头衔有道具 | 3 |
| 列表项_排名4 | 有头衔无道具 | 1 |
| ... | ... | ... |

### 8.10 variant_diffs 解析（v20.7.x，③ 已实装）

子 CCB 生成时，对每个非默认 Variant，跟默认 Variant 按节点 name 一一比对，把属性差异写入对应 sequence 的 keyframe。切换 sequence 时视觉差异立即生效。

**V1 实装的差异属性**：

| 属性 | type 编号 | 触发 | value 格式 |
|---|---|---|---|
| `visible` | **1** | layer 的 `visible` 字段 true/false | bool |
| `color` | **6** | layer 的 `fill` 字段 `#RRGGBB` | `[r, g, b]` int 列表 |

**V1 暂未实装**（生产样本无现成样式或属于运行时数据）：

- `opacity` (type=5) — 没有典型用例
- `position` (type=3) — Figma Variants 强制结构一致，position 通常不变
- `scale` (type=4) — 同上
- `rotation` (type=2) — V1 限制
- `displayFrame` (type=7) — 图片资源 V1 走数据驱动
- `TEXT.content` — 字符串差异属于运行时数据，不编译进 sequence

**Keyframe type 编号清单**（从生产样本 res_juice_pro 提取）：

```
visible       type=1, value=True/False
rotation      type=2, value=float
position      type=3, value=[x, y]
scale         type=4, value=[sx, sy]
opacity       type=5, value=int(0-255)
color         type=6, value=[r, g, b]
displayFrame  type=7, value=[png_filename, plist_filename]
animation     type=15
```

**算法**（`generate_red_component()` 里实施）：

1. **`merge_variants_layers(variants, default_variant)`**：合并所有 variant 的 layers 取全集
   - 先按 default variant 的 layers 顺序收节点（保留原始 visible 字段）
   - 其他 variant 里 default 没有的节点 → 加到全集末尾，强制 visible=False
   - **为什么需要**：Figma 端导出 variant 时只导"该 variant 实际可见的节点"，导致每个 variant.layers 的节点数不一样（"常态"6 个、"有头衔无道具"8 个、"有头衔有道具"10 个）。
     合并全集让引擎能对每个节点都生成 keyframe，无论它在哪个 variant 出现。
2. 用合并后的全集 `inner_layers` 生成内部节点（`build_children`）
3. **`apply_default_visible(inner_layers, inner_kids)`**：把全集中 visible=False 的节点写入 properties.visible=False，
   让 sequence 0（常态）加载时这些节点真的隐藏（否则节点默认 visible=True 显示出来，跟"常态"视觉相反）
4. 对每个非默认 Variant：
   - `diff_variant_against_default(inner_layers, variant_layers)` 按 name 匹配，提取 visible / fill 差异
     - case 1：variant 里有该节点，visible 跟 default 不同 → 写 keyframe
     - case 2：variant 里没该节点（全集有）→ 写 visible=False keyframe（variant 隐藏该节点）
     - fill 颜色不同 → 写 color keyframe
   - `write_variant_keyframes(inner_kids, diffs, seq_id)` 写入对应节点 `animatedProperties[seq_id]` keyframe

**示例**（列表项_排名 5 个 Variant）：

```
默认 Variant（常态）:
  文本_头衔 properties: visible=False (默认隐藏)
  图标_头衔徽章 properties: visible=False
  图标_道具 properties: visible=False
  文本_道具数 properties: visible=False

非默认 Variant 的 keyframe：
  seq 1 (有头衔无道具):
    文本_头衔 → visible=True
    图标_头衔徽章 → visible=True
  seq 2 (无头衔有道具):
    图标_道具 → visible=True
    文本_道具数 → visible=True
  seq 3 (有头衔有道具):
    文本_头衔 → visible=True
    图标_头衔徽章 → visible=True
    图标_道具 → visible=True
    文本_道具数 → visible=True
  seq 4 (当前用户):
    底板_行 → color=[136, 200, 112]   # #88c870 绿色
```

加载行为：

- INSTANCE.variant="常态" → animation=0 → 节点全部用 properties 默认值（头衔/道具隐藏）
- INSTANCE.variant="当前用户" → animation=4 → 节点 properties 默认 + seq4 keyframe 覆盖（底板变绿色）

**注意**：`color` 的 type=6 是按 cocos2d-x 编号顺序推断的（生产样本里没有现成的 color keyframe）。如果 Redream 加载报错或显示异常，按 5/7/8 试探调整。

### 8.11 Variant 组级 visible 切换建模(v20.7.x+,2026-05-11 修订)

引擎设计哲学:**每个非空 Variant 对应一个 CCNode 组容器(displayName = `组_<Variant名>`), Variant 之间通过给组打 visible keyframe 切换**。

#### 标准结构

```
进度条icon Component:
  外侧 wrapper [CCNode] 进度条icon (default visible=True,不动)
    │
    ├── [CCNode] 组_已完成 (default visible=False)        ← KF seq=0 visible=True
    │     ├── 底板_进度icon_已完成
    │     └── 文本_等级数字   (共享图层副本 1)
    │
    └── [CCNode] 组_未完成 (default visible=False)        ← KF seq=1 visible=True
          ├── 底板_进度icon_未完成
          └── 文本_等级数字   (共享图层副本 2)

  sequences:
    "已完成" (seq 0):   组_已完成 → visible=true keyframe
                       组_未完成 → 不打 (保持 default False)
    "未完成" (seq 1):   组_未完成 → visible=true keyframe
                       组_已完成 → 不打
```

引擎加载 INSTANCE 时按 `animation` 字段(= variant 对应的 sequenceId)播 sequence,sequence 给对应组打 visible=true,该组下所有图层一起渲染。其他组保持 default invisible → 不显示。

#### 关键设计点

1. **每个非空 Variant 一组**(组名 = `组_<Variant名>`)
2. **共享图层(无尾缀)在每组内复制一份**
   - 进度条icon 的 `文本_等级数字` 在 `组_已完成` 和 `组_未完成` 内各占一份
   - cocos2d-x 节点树不能复用,所以独立 instance(同名,不同 ptr)
   - 复制是为了"什么时间线就让什么组显示,共享内容跟着组走"
3. **组 default visible=False**(由 app.py 写入 properties),sequence 通过 keyframe 打开
4. **外侧 wrapper(根 CCNode)default visible=True**(不动)— wrapper 不渲染内容,不需 keyframe
5. **空 Variant 不创建组**,详见 8.12

#### 设计哲学(推荐 / 不推荐)

- ✅ **推荐**:每个 Variant 内部图层带尾缀(如 `_常态` / `_激活` / `_锁` / `_对勾`),共享图层无尾缀
  - app.py 按 Variant 名分组,创建 `组_<Variant名>` 容器
  - keyframe 干净:时间线只在自己对应组上打 visible=true
- ❌ **不推荐**:同图层(同名)在不同 Variant 改 fill / corner_radius
  - 虽然 app.py 旧版 diff 算法也支持(走 color keyframe),向后兼容旧 JSON
  - 但语义模糊,组级模式下无法工作(同名图层只会创建一份)
  - **不强制**:extract_components.py 不加检测,这只是文字规则

#### app.py 已实现的支持函数(代码即文档)

- `generate_red_component`(2026-05-11 重写) — 主入口
  - 每个非空 Variant 深拷贝其 layers 创建 CCNode 组容器
  - 组 default visible=False
  - sequence 给对应组打 visible=True keyframe
- `make_visible_diffs_for_variant` — 现在返回组名而不是图层名
- `write_variant_keyframes` — 给指定 displayName 节点(组)打 keyframe

#### 历史

- v1(2026-05-09):图层级 keyframe — 给每个图层直接打 visible=true,共享图层在两个 sequence 都打
- v2(2026-05-11):**组级 keyframe**(当前)— 每个 Variant 一组,给组打 keyframe,共享图层在每组内复制一份。设计师 Redream 编辑器里看时间线更清晰

### 8.12 空 Variant 处理(v20.7.x+,2026-05-11 修订)

#### 触发条件

某个 Component.Variant 名为 `空` 或 `layers=[]`(等价空)。

#### 处理逻辑(8.11 组级模式下的自然结果,无需特例分支)

**子 CCB 生成 sequences 时**:
- 空 Variant 仍生成一条 sequence(序号 = `_COMPONENT_VARIANT_SEQID` 登记的 seq_id)
- 但**不创建 `组_<Variant名>` 容器**(因为 Variant.layers=[],没有图层可组)
- 该 sequence **不打任何 keyframe**
- 加载该 sequence 时,所有其他组保持 default invisible → 视觉全空

**主屏 INSTANCE 引用空 Variant 时**:
- 走正常 REDFile 路径(跟普通 Variant 一样)
- `animation` 字段 = 空 Variant 对应的 sequence id
- 引擎加载子 CCB 切到该 sequence → 所有组 invisible → 视觉空

#### 跟 8.11 的关系

- 8.11 描述非空 Variant 怎么处理(创建组 + 给组打 keyframe)
- 8.12 描述空 Variant 怎么处理(**不创建组,不打 keyframe**)
- 两者是同一套机制的两面,空 Variant 是非空 Variant 的"零情况"

#### app.py 实现指向

- `generate_red_component` 内 `for v in variants: ... if not v_layers: continue` — 空 Variant 不进入组创建循环
- sequence 循环里检查 `组_<v_name> in group_name_to_node` — 空 Variant 没对应组,跳过 keyframe
- `_COMPONENT_EMPTY_VARIANTS` / `is_empty_variant_ref` 登记表保留(自检 / 文档用),但**主流程不再依赖**

#### 设计师 / Claude 视角

设计师/Claude 在 Figma 端做空 Variant(`layers=[]`,语义名"空")。引擎自动按上述流程处理,**不需要手写 INSTANCE.visible=false**。

---

### 8.13 预制组件库(v20.7.x+,2026-05-15)

#### 动机

部分 Component 在所有 scene 复用,且**视觉/结构毫无变化**(典型:`预制_钟表指针动画`、`预制_底标倒计时` 这种)。每次生成都跑一遍 `generate_red_component` + `build-scene` 是浪费,且生成管线还在迭代,容易引入回归 bug。

预制组件库的思路:**已经验证 OK 的 .red 沉淀到工程目录 → 之后命中即复用,绕开生成流程**。

#### 目录与触发

- 预制库目录:`red_tool/prefabs/`(跟 `app.py` 同级,纳入工程)
- 预制源**三件套**:
  - `prefabs/<cname>.red` — 预制场景文件,文件名 = 组件名
  - `prefabs/<cname>.plist` — 预制自带独立小图集 plist(可选,无图组件可省)
  - `prefabs/<cname>.webp` — 预制自带独立小图集 webp(跟 plist 配对)
- 触发集合(2026-05-15,**单一钟表特例**,`预制_` 前缀 C 方案已回退):
  ```python
  PREFAB_NAMES = {'钟表_指针动画'}  # 钟面+指针旋转动画+Scale9 底板+CCLabelPlus 占位文本
  ```
  其他子 ccb 都走 `components[]` + `generate_red_component` 普通生成。Figma 端命名规约见 [`4.22最新skill/00e_预制组件命名.md`](/Users/red/Desktop/4.22最新skill/00e_预制组件命名.md)。ccb 3 标准抽取参考 [`4.22最新skill/00f_视觉缩窄_ccb_3标准.md`](/Users/red/Desktop/4.22最新skill/00f_视觉缩窄_ccb_3标准.md)(待 C 阶段新建)。
- 触发条件(2026-05-15 升级):**`_collect_prefab_refs(scene)` 递归扫整个 scene.json**,任意位置出现 `component_ref` / `component_name` / **`name`** 命中 `PREFAB_NAMES` 即触发 — **不再要求 scene.json 的 `components[]` 数组里也声明一遍**。这是"开箱即用预制"的关键 — 设计师/Claude 在 Figma 端把 frame **命名**为预制名(精确字符串匹配),引擎自动拷预制,无需重复声明、无需 component_ref。
- Figma 端命名规约权威文档:[`4.22最新skill/00e_预制组件命名.md`](/Users/red/Desktop/4.22最新skill/00e_预制组件命名.md)(给设计师/Claude 看)

#### 预制 .red 的 frame 命名规约

预制自带图集时,`.red` 里的 `displayFrame` 必须用**通用化命名**,避免跟项目内 scene 图集 frame 名冲突:

```
displayFrame.value = [
    "<cname>.plist",                 # 指向自带图集 (不带模块前缀)
    "<cname>_<layer>.png",           # frame 名以预制名打头,自动 namespace
]
```

**例**(`钟表_指针动画`):
```
["钟表_指针动画.plist", "钟表_指针动画_图标_时钟.png"]
["钟表_指针动画.plist", "钟表_指针动画_图标_指针.png"]
["钟表_指针动画.plist", "钟表_指针动画_时效组_底板.png"]
```

⚠️ **不要**用 `M8P_<模块>_xxx.png` 这种生产项目的具体模块前缀 — 跨项目复用时会找不到 frame。沉淀新预制时,必须重写源 .red 的 spriteFrame 引用为预制专用 frame 名。

#### 拦截逻辑

`app.py` 在 `generate_red()` 里分 3 步处理(2026-05-15 升级):

**步骤 1**:在 `register_component_variants(components)` 后扫预制引用 + 自动注册:

```python
prefab_refs_in_use = _collect_prefab_refs(scene)
for pname in prefab_refs_in_use:
    if pname not in _COMPONENT_VARIANT_SEQID:
        _COMPONENT_VARIANT_SEQID[pname] = {'default': 0, '常态': 0, '': 0}
```

注册后 `build_top_layer` 处理 INSTANCE 时,L1208 / L1229 兜底不再触发,直接走 REDFile 引用 `<module>/<pname>.red`。

**步骤 2**:独立预制循环(在 `for comp in components` 之前):

```python
if prefab_refs_in_use:
    for pname in sorted(prefab_refs_in_use):
        prefab_src = prefabs/<pname>.red
        if not prefab_src 存在:
            log "💡 预制源不存在 → 跳过"
            _COMPONENT_VARIANT_SEQID.pop(pname)  # 撤销注册避免破引用 → 走兜底空 CCNode
            continue
        shutil.copyfile(prefab_src, ccb/<module>/<pname>.red)
        for ext in (plist, webp):
            if prefabs/<pname>.<ext> 存在:
                shutil.copyfile(..., _img_plist/<module>/<pname>.<ext>)
        log "♻️ 拷预制 .red + ↳ 同步图集"
```

**步骤 3**:`for comp in components` 循环里防覆盖:

```python
for comp in components:
    cname = comp.get('name')
    if cname in prefab_refs_in_use:
        log "(跳过常规生成, 已走预制)"
        continue   # 避免 components[] 同名声明覆盖预制 .red
```

**步骤 4**:`build_top_layer` L1229 老体系兜底改成:

```python
if n.get('component_ref'):
    comp_name = n.get('component_ref')
    if comp_name in _COMPONENT_VARIANT_SEQID:  # 预制已通过步骤 1 注册
        # 走 REDFile 引用 <module>/<comp_name>.red
        return make_redfile(...)
    return make_ccnode(...)  # 否则原空 CCNode 路径
```

资源命中:`_img_plist/` 已在 `.redproj.resourcePaths` 里,同步过去的 `<pname>.plist` 自动被 Redream 加载,跟 `<scene>_图片资源.plist` 平级共存。

#### 与 INSTANCE 映射的关系

主屏 INSTANCE 引用 `钟表_指针动画` 时:
- `register_component_variants(components)` 仍按 scene.json 注册 variant 列表(预制路径下这个表用不上但跑一遍无害)
- `lookup_variant_seqid('钟表_指针动画', variant)`:
  - 如果 variant 在表里 → 返回对应 seqid
  - 不在 / 没声明 → 返回 0(默认)
- 预制 .red 必含 sequence 0(default sequence),所以**无 variant / 单 variant 的预制**总能正确回放

⚠️ **多 variant 预制超出本期范围** — 因为预制 .red 里的 sequence ID 跟 scene.json 注册的 seqid 必须**人工对齐**,出错率高。多 variant 组件目前老老实实走 generate。

#### 如何沉淀预制

**路径 A — 从当前管线生成结果沉淀**(组件结构 OK,只复用):

1. 用当前管线跑一次生成,得到 `ccb/<module>/<cname>.red`
2. 用 Redream 打开主屏验证该组件渲染正确
3. 拷贝:`cp red_output<X>/ccb/<module>/<cname>.red red_tool/prefabs/<cname>.red`
4. 该 .red 引用的 frame 都在 `<scene>_图片资源.plist` 里 → **图集复用 scene 自己的**,不需要单独打小图集

**路径 B — 从生产 res_juice_pro 手搓 .red 沉淀**(2026-05-15 引入,自带独立图集):

1. 锁定生产 .red(典型:`res_juice_pro 2/ccb/<模块>/<comp>.red`)
2. 锁定它引用的所有 PNG 源(在 `res_juice_pro 2/image/<模块>/...`)
3. 写一次性脚本(参考 `2026-05-15 沉淀 钟表_指针动画`):
   - 调 `app.pack_atlas(png_entries, prefabs/<cname>.plist, prefabs/<cname>.webp)`,frame 名通用化为 `<cname>_<layer>.png`
   - 用 `plistlib` 加载源 .red,递归找所有 `displayFrame` 改写:plist 路径 → `<cname>.plist`,frame 名 → `<cname>_<layer>.png`
   - 保存到 `prefabs/<cname>.red`
4. 交叉验证:.red 引用的每个 frame 都在生成的 plist 里

⚠️ **不自动沉淀** — 避免把一份带 bug 的生成结果缓存进预制。沉淀必须人工确认。

#### 适用判定

加入 `PREFAB_NAMES` 的标准:
- ✅ 视觉跨 scene 完全一致(钟表 icon 形状/颜色不变)
- ✅ 内容由运行时数据驱动(倒计时数字),**不由设计 / scene.json 切换**
- ✅ 无 variant 或仅 1 个默认 variant
- ❌ 多 variant + 视觉差异(那叫"组件",不叫"预制")
- ❌ 跨项目复用但每个项目美术皮肤不同(那需要 variant 或独立组件)

#### app.py 实现指向(2026-05-15 升级版)

- 常量:`PREFAB_DIR` / `PREFAB_NAMES`(L249 附近,紧跟 `ATLAS_MAX_SIZE`)
- 工具:`_collect_prefab_refs(scene)`(L257 附近,递归扫 scene.json 找预制引用)
- 自动注册:`generate_red()` 内 `register_component_variants(components)` 之后(L2387 附近)
- 独立预制循环:`for comp in components` 循环之前(L2418 附近,先于常规生成)
- 防覆盖:`for comp in components` 循环里 `if cname in prefab_refs_in_use: continue`
- L1229 老体系兜底:`component_ref` 命中已注册预制时走 REDFile,否则空 CCNode
- 复用 `pack_atlas(png_entries, plist_path, webp_path)` 工具函数沉淀新预制图集

---

