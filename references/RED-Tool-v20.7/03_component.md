# 封装方案(Component / Variant / 组级 keyframe / 空 Variant)

> 引擎 SKILL 拆分文档(v20.7.x+,2026-05-11) · 索引见 SKILL.md

---

## 八、封装方案（V1 完整规范）

### 8.1 何时做成 Component Set

满足任一即做：

- **复用**：同一节点结构在 Figma 多处出现
- **动态**：运行时代码动态实例化（背包格子、列表 cell 等）

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

### 8.4 Component → 子 CCB 文件名映射

```
Figma Component Set "排行榜行"   →  Resources/控件库/排行榜行.red

Figma 内部 Variant "排行榜行=常态"
                  "排行榜行=带徽章"   →  同一个 .red 内的多条 sequence
                  "排行榜行=带道具"
```

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
    ├── redFile = "控件库/列表项_排名.red"
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

