# RED Tool Memory（引擎相关）

> 导出日期：2026-04-29 · 版本：v20.7.2
> 已写入 Claude 系统 Memory，本文件为存档备份

---

## 1. RED Tool 架构 v20.7（当前）

流程：Figma 插件 → fetch localhost:5001 → Flask app.py → Python 生成中间 .red → Redream CLI build-scene 规范化 → inspect check 校验。

- Redream CLI: `/Applications/Redream.app/Contents/MacOS/Redream` (v1.3.4)
- Python 端代码在 `~/Desktop/red_tool/app.py`（不是 red_tool 14 子目录）
- 启动：`cd ~/Desktop/red_tool && python3 app.py`
- 输出根：`~/Desktop/red_output/`
- 端口 5001（之前 5000）
- 子 CCB 集中放 `Resources/控件库/`

---

## 2. 坐标规则（Coord Rules）

- Fullwidth = SCALE 或 LEFT+right<10
- TOP: pos=[50%, 100% u=2,2], anchor=(0.5, 1.0), size=[100%, px u=2,0]
- BOTTOM: pos=[50%, 0% u=2,2], anchor=(0.5, 0.0)
- 固定宽: x=L/R 对称%, y=50/100/0% u=2
- 多个 TOP/BOTTOM 节点：合并到 组_顶部/底部合并，内层节点 100% 宽 u=2
- 父全宽 → 子 x=% u=2, 子 y=px u=0
- 父固定 → 子 x/y=px u=0

---

## 3. 按钮命名 v20

- `按钮_XXX FRAME` = 触控层 REDNodeButton（v20 新）
- `底板_XXX RECT`（父非按钮）= 外层容器 CCSprite
- `底板_XXX RECT`（父是按钮）= 按钮内层装饰 CCSprite
- 兼容：v19 `底板_XXX FRAME` = 触控层；v18 `切图_底板_XXX` = 触控层
- REDNodeButton 7 属性：position/contentSize/anchorPoint/opacity/color/ccControl(['',1,32])/preferedSize
- ccControl 值：''=Selector 空, 1=启用, 32=Up inside
- auto_btn：组_按钮_/按钮_ 无触控层子节点时自动补 REDNodeButton，并把其他内容放进 children
- 按钮容器识别：看是否有 baseClass='REDNodeButton' 子节点，不看名字

---

## 4. 放穿透层规则

- 所有屏幕（界面_/浮层_）都要添加放穿透层，不只是浮层
- 位置：scene_root 的 children[0]（CCLayer > scene_root 下面）
- 尺寸：100%×100%（contentSize 和 preferedSize 都要 [100,100,2,2]，两个单位必须一致）
- 坑：preferedSize 之前写成 [100,100,0,0]（100像素）导致渲染成小方块
- 浮层_ 还要加 遮罩_背景（CCLayerColor，opacity=178 黑），顺序：放穿透层 → 遮罩 → 弹窗

---

## 5. Redream CLI 关键命令

- 参数顺序：`Redream [options] action`，action 必须放最后
- `--json` 帮助写了但当前版本不支持，去掉就能用
- 新建项目：`modify new-project --project xxx.redproj --resolution 1080x2400`
- 加资源路径：`modify --project xxx --add-resource-path Resources project`
- build-scene 克隆规范化：`modify build-scene --project xxx --scene Resources/xxx.red --config 源.red`
- 校验：`inspect check --project xxx`（输出 ok.= 通过）
- Position 格式：`x,y,z,unitX,unitY`（帮助里的 anchorX/Y/Z 是误导）

---

## 6. 两种 JSON 区别（关键）

- **生成 JSON**（Import：JSON → Figma）：不含 x/y，AL 容器内靠 Figma 自动排
- **导出 JSON**（Export：Figma → JSON）：含真实 x/y（Figma 算好的）
- RED Tool 只认导出 JSON，必须先在 Figma 画布用插件「导出 JSON」按钮拿含 x/y 的
- 喂生成 JSON 给 RED Tool 的症状：所有子节点挤在左上角
- AL 子节点在 Figma 里 node.x/node.y 是 Figma 自动计算的相对父节点坐标，插件 code.js v20 L701-702 无条件写入

---

## 7. RED Tool 启动 & 端口排查

- 启动：`cd ~/Desktop/red_tool && python3 app.py`
- 必须用 `http://localhost:5001`
- 端口 5001 被占：`lsof -i :5001` 找 PID → `kill -9 PID` 或 `killall python3`
- 停服务 Ctrl+C；改代码必须重启才生效
- Internal Server Error 看终端 Traceback；Failed to fetch 通常是 Flask 没启动
- Figma 插件用 manifest.json 的 networkAccess.devAllowedDomains 才能跨域 fetch（`http://localhost:5001/` 末尾必须带斜杠，不能用 127.0.0.1，必须加 reasoning 字段）

---

## 8. 封装方案核心机制（plan 模式定型）

- Figma Component → 子 CCB .red 文件（`Resources/控件库/<name>.red`）
- Component Set 名 = 文件名（不带 =Variant 后缀）
- 每个 Variant → 一条 sequence
- "常态"必填且强制 sequenceId=0
- 其他 Variant sequenceId 递增
- 常态属性写进节点 properties
- 其他 Variant 视觉差异写 animatedProperties[sequenceId] 的 keyframe（time=0 单帧静态快照）
- sequence length=0.067 秒，autoPlay=false，chainedSequenceId=-1

---

## 9. 封装判断规则（V1）

满足任一即做 Component Set：

1. 复用：同结构多处出现
2. 动态：运行时代码动态实例化

Component Set 内做多 Variant 的判断：状态多态（同结构有有限离散视觉差异）。

不算多态（不做 Variant，运行时填数据）：

- 文本字符串
- 数字
- 图片 url
- 进度条百分比

判断"图片是不是多态"：能在 Figma 设计稿枚举完 → Variant；枚举不完 → 数据。

---

## 10. 封装规则约束（V1）

- 单 Variant Property 强制（多 Property 报错，Property 名固定"状态"，但取值数量不限）
- 默认 Variant 强制叫"常态"对应 sequenceId=0
- Component 重名自动加序号后缀（_2/_3）
- Component 内部不能嵌套 Instance（V1 不支持嵌套封装，遇到直接展开成普通节点）
- 顶层 Frame 必须 `界面_xxx` 或 `浮层_xxx`，否则报错
- Component 放置位置不限（任何 Page 都行，工具 A 自动识别定义 vs 使用）

---

## 11. REDFile 节点格式（主场景里引用子 CCB，v20.7.x 改两层结构）

主场景里 INSTANCE 不再扁平化成单个 REDFile，而是 **父 CCNode + 子 REDFile 两层**：

**父 CCNode**（外层，承载布局）：
- baseClass = CCNode
- displayName = INSTANCE.name（如"列表项_排名6"）
- properties: position / contentSize（**写真实 w/h**，响应式 constraints 依赖）/ anchorPoint=(0.5,0.5) / ignoreAP / opacity / color
- 子节点：子 REDFile

**子 REDFile**（内层，引用 CCB）：
- baseClass = REDFile
- displayName = **组件名**（如"列表项_排名"，所有同组件实例的子 REDFile displayName 一致）
- properties:
  - position = (w/2, h/2)（父中心，锚点对齐）
  - anchorPoint = (0.5, 0.5)
  - opacity = 255
  - color = [255,255,255]
  - redFile（路径字符串如 `控件库/列表项_排名.red`）
  - **animation = sequence_id**（按 INSTANCE.variant 映射，0=常态/1/2/3/...）
- 可选 visible（默认 true）
- reboltId 12 位随机字符串
- reboltName = INSTANCE.name（保留 Figma 语义命名，行为树用 reboltName 定位）
- children 永远空数组
- **不写 contentSize**（由子 CCB 自己决定渲染尺寸）

**variant 映射表**（主屏生成前由 `register_component_variants(components)` 填充）：

```python
_COMPONENT_VARIANT_SEQID = {
    '列表项_排名': {
        '常态':         0,   # is_default → seqId 0
        '有头衔无道具': 1,
        '无头衔有道具': 2,
        '有头衔有道具': 3,
        '当前用户':     4,
    },
}
```

build_child 处理 INSTANCE 时：`seq_id = lookup_variant_seqid(comp_name, variant)` → 写入子 REDFile.animation。

V1 仍简化：sequence 1/N 的 keyframe 是空的，加载后视觉跟"常态"一致（V2 解析 variant_diffs 写 animatedProperties 后才会有差异）。

---

## 12. 子 CCB 文件结构（vs 主场景，v20.7.x 单层 CCNode 根）

**主场景**：
- 根 **CCLayer** + 总组 + 组_背景层 + 防穿透层 + 遮罩（仅浮层）
- resolutions 5 种
- sequences 1 条占位

**子 CCB（v20.7.x 起）**：
- 根 **CCNode**（单层，displayName = 组件名如"列表项_排名"）
- 不再多包一层"内层 CCNode"
- 控件原始尺寸 cw × ch，position (cw/2, ch/2)，anchor (0.5, 0.5)
- customClass = ''（不再是 CoreLayer 的子类）
- expand: True（编辑器里默认展开）
- resolutions 1 种（控件自身尺寸）
- sequences N 条（每个 Variant 一条，sequenceId 与 _COMPONENT_VARIANT_SEQID 对齐）
- 不要总组/背景层/穿透层/遮罩
- currentResolution=0
- 子 CCB 内部节点 properties 写默认 Variant 的属性值，加载即呈现常态

**为什么从 CCLayer 改成 CCNode**：
- 子 CCB 作为被引用的组件，被嵌入主场景时不应出现 CCLayer 嵌套（CCLayer 只在场景根）
- CCNode 更轻量（没有 touch 处理），子 CCB 不需要独立处理触控
- 单层根节点结构清爽，displayName 直接是组件名

---

## 13. animatedProperties keyframe 格式（v20.7.x 已实施）

动画数据挂在节点上而非 sequence 上：

```python
节点的 animatedProperties = {
    "<sequenceId>": {                # 字符串化的 seqId
        "<属性名>": {
            "keyframes": [{
                "easing":     {"type": 0},
                "name":       "<属性名>",
                "pathValues": [],
                "time":       0.0,
                "type":       <type 编号>,
                "value":      <属性值>,
            }],
            "name": "<属性名>",
            "type": <type 编号>,
        }
    }
}
```

**Keyframe type 编号**（从生产 res_juice_pro 提取）：

```
visible       type=1, value=True/False
rotation      type=2
position      type=3, value=[x, y]
scale         type=4, value=[sx, sy]
opacity       type=5, value=int(0-255)
color         type=6, value=[r, g, b]    # 推断
displayFrame  type=7, value=[png, plist]
animation     type=15
```

Easing type：0=无 / 1=linear / 12=用户曲线 / 18=贝塞尔(opt=参数)。V1 variant 切换都用 type=0。

---

## 14. V1 实装的 Variant 差异属性（v20.7.x）

✅ **已实装**：
- `visible` (true/false) — 触发：layer 的 `visible` 字段
- `color/fill` (RGB) — 触发：layer 的 `fill: "#RRGGBB"` 字段

⏸️ **未实装**（V1 暂无典型用例 / 不需要）：
- `opacity` / `position` / `scale` / `rotation` / `displayFrame`

❌ **完全不支持**（属于运行时数据，不进 sequence）：
- TEXT.content 字符串差异（运行时由代码注入）
- 数字、图片 url
- size (w/h) 差异

Variant 之间结构不变（Figma Variants 强制约束）。"加节点"实现方式：在常态画上目标节点然后 visible=false，不能真加节点。

**实施函数**（app.py）：

- `diff_variant_against_default(default_layers, variant_layers)` 按 name 匹配提取 diff
- `write_variant_keyframes(generated_kids, diffs, seq_id)` 写入 animatedProperties keyframe
- `apply_default_visible(default_layers, generated_kids)` 默认 Variant visible=False 写入 properties

---

## 15. scene.json 数据结构（v20.6 schema）

顶层：`meta.design_size` / `components[]` / `screens[]` / `flow[]`

INSTANCE 节点字段：

```
type: "INSTANCE"
name
component_name
variant
x / y / w / h
constraints
visible
```

Component Set 字段：

```
name, w, h, property_name, variants[]
```

每个 variant：`name, is_default(bool), layers[]`

- INSTANCE 命名按 Figma 实际格式（如"列表项_排名6"语义命名 + 独立 variant 字段），不带 _Variant 后缀
- screens.id 字段 V1 忽略
- component_ref 节点 V1 当空 CCNode 占位（老组件库不规范暂不展开）
- flow 字段保留但 V1 不消费

---

## 16. V1 排除项（V2 再做）

🔥 **V2 第一批（绝对要做）**：
- **4.3 嵌套子 CCB**（component A 内部 INSTANCE 引用 component B）
  - 实施关键：传递引用追溯（A → B → C 链路全部生成）
  - V1 兜底：未注册引用降级空 CCNode 占位（已实装）
  - V2 改造点：api_generate_red 加传递追溯过滤；build_child INSTANCE 分支去掉"未注册降级"
- 4.12 Instance 缩放（待 Redream 测试）
- 嵌套子节点 constraints 处理（响应式补全）
- 4.6 多分辨率配置（5 种：设计/正常/偏宽/偏高/Node）

⚠️ **V2 第二批**：
- 4.11 状态切换（接 .rebolt 行为树）
- 4.1 行为树本体
- 4.5 多语言 fontStyle
- 4.4 Prototype Flow

❄️ **长期**：
- 4.2 复杂动画 Variant
- 4.10 Instance 镜像
- 4.13 rotation 差异
- 老 component_ref 体系迁移

---

## 17. .rebolt 行为树（V1 不实现）

- .rebolt 文件是 JSON 格式，含 CustomFunc / CustomVar / RedFileList / TreeList
- 生产项目用 BTPlaySceneTimeLineWaitAction 节点切换状态：
  - redSelect 指定哪个子 CCB
  - baseSelect 指定播哪条 timeline（Value=sequenceId）
- .rebolt 只在"有逻辑的协调容器"那级生成（如底部导航栏），单个图标子 CCB 没有同名 .rebolt
- RED Tool V1 不生成 .rebolt，所以 animation=-2 加载后视觉冻结在常态

---

## 18. Figma 插件 v20.7 集成（合并 RED Tool）

新增 Tab "🚀 生成 .red"：

- 选中一个或多个 `界面_/浮层_` Frame
- `buildSceneForRed()` 反查 Component
- POST `/api/generate_red`
- manifest.json 用 `networkAccess.devAllowedDomains: ["http://localhost:5001/"]` + reasoning 字段
- code.js 加 `buildSceneForRed` / `nodeToJsonForRed` / `componentSetToJsonForRed` / `cleanComponentName` / `getInstanceVariant` / `getInstanceMainComponent`
- INSTANCE 节点 → REDFile 节点
- 多余非屏幕选中静默忽略
- clientStorage 持久化输出路径

---

## 19. Python /api/generate_red 流程（v20.7.x 加过滤步骤）

0. CORS 头允许跨域
1. 解析 body `{output_path, scene{components, screens, flow}}`
2. ensure_project（new-project + add-resource-path Resources）
3. **v20.7.x: 反查屏幕 INSTANCE 直接引用的 component_name（V1 不做嵌套追溯）**
   - 只扫 screens.layers 收集屏幕直接 INSTANCE 引用
   - 跳过所有未被屏幕直接引用的（Figma _组件库 误传 / component_ref 老体系 / 自动占位等）
   - V1 不做传递引用追溯（嵌套子 CCB → V2 必做）
   - V1 兜底：build_child 处理 INSTANCE 时，未注册的 component 引用降级空 CCNode 占位，
     避免 inspect_check 报 broken reference
4. 先生成所有子 CCB → `Resources/控件库/<name>.red`（用过滤后的 components）
5. register_component_variants(components_filtered) 填充 variant→seqId 映射
6. 再生成主屏 → `Resources/<name>.red`
7. inspect check 整体校验
8. 返回 `{ok, output_dir, files[], log, error?, stage?}`

**过滤设计意图**：引擎控件库 = 主场景 INSTANCE 引用的 Component 集合（与 Figma _组件库 frame 解耦）。
Figma _组件库 frame 是给设计师看的视觉文档，不是引擎要导出的资产。

其他端点：

- `/api/ping` 用于 Figma 插件检测连通
- `/api/open_finder` 接受 POST {path} 在 Finder 中显示

---

## 20. Redream 节点类型（V1 用到的）

- CCNode（容器）
- CCSprite（图片）
- CCLayer（场景根）
- CCLayerColor（占位/遮罩色块）
- REDNodeButton（按钮触控层）
- CCRedLabel（文本）
- CCProgressTimer（进度条）
- REDFile（CCB 引用）
- RedSafeAreaLayer（安全区）
- ReferenceImageNode（参考图）

属性单位：position / contentSize 5 元数组 `[x, y, z, unitX, unitY]`

- unit=0 绝对像素
- unit=2 百分比
- unit=3 仅 contentSize 高度（剩余空间）
- position 永远不能 u=3

---

## 21. 进度条规范 v20.4

三层结构：

- 组_进度_XXX (CCNode 容器)
- 底板_XXX (CCSprite 永远满)
- 进度条_XXX (CCProgressTimer 默认 100%)

识别条件：type='RECTANGLE' 且 name 以 `进度条_` 开头。

Direction 通过命名末尾后缀编码：

- 无后缀 = horizontal_lr 默认
- `_rl` = horizontal_rl
- `_tb` = vertical_tb
- `_bt` = vertical_bt
- `_cw` 或 `_ccw` = 不识别按默认

Direction 对应 barType + midpoint + barChangeRate。percentage 默认 100（视觉满，运行时控制）。displayName 保留原名含后缀。

---

## 22. 节点结构规范 v16+（主场景）

```
CCLayer
└── 总组 (CCNode 100%×100%, 固定 displayName="总组")
    ├── 组_背景层 (CCNode 100%×100%) ← scene_kids[0]
    │   ├── 全屏防点击穿透层 (REDNodeButton 100%×100%)
    │   └── 背景_XXX (CCSprite 100%×100%, 仅界面_有)
    ├── 遮罩_背景 (CCLayerColor opacity=178 黑, 仅浮层_有)
    └── 中间内容 / 组_顶部合并 / 组_底部合并
```

顶层全屏背景（名以"背景_"开头 + 接近屏幕尺寸）自动提取到背景层作为 CCSprite。屏幕名靠 .red 文件名表达（如 `界面_主菜单.red`）。

---

## 23. RED Tool 当前进度（v20.7.x / 2026-05-06）

✅ Plan 模式 6 条规范全部确认
✅ Figma 插件 v20.7 加 🚀 Tab
✅ Python `/api/generate_red` 完整流程通
✅ 子 CCB 生成实装（`Resources/控件库/<name>.red`）
✅ 主场景 INSTANCE → REDFile 引用

**v20.7.x 调优完整 changelog（2026-05-06）：**

引擎端（`~/Desktop/red_tool/app.py`）：

✅ 子 CCB 根节点 **CCLayer → CCNode**（单层结构，displayName=组件名，position=(0,0)）
✅ 主场景 INSTANCE → **父 CCNode + 子 REDFile 两层**
✅ REDFile 节点格式严格对齐生产样本（不写 anchorPoint，position 用百分比 [50,50,0,2,2]）
✅ file-level + resolution-level centeredOrigin 都设 False（对齐生产 shop_buy_btn）
✅ ② INSTANCE.variant → sequenceId 映射（_COMPONENT_VARIANT_SEQID + register_component_variants）
✅ ③ variant_diffs 解析实装：merge_variants_layers + diff_variant_against_default + apply_default_visible + write_variant_keyframes
✅ V1 实装属性：visible (type=1) / color (type=6 推断)
✅ components 防御过滤：只生成屏幕 INSTANCE 直接引用的 component
✅ V1 兜底：孤儿引用降级空 CCNode 占位（嵌套子 CCB → V2 必做）

Figma 插件端（`~/Desktop/最新插件/code.js`）：

✅ 加 figmaFillsToHex 工具函数（提取 SOLID fill 为 #RRGGBB）
✅ nodeToJsonForRed 加 keepInvisible 参数 + RECTANGLE/TEXT/FRAME 三处加 fill 字段输出
✅ componentSetToJsonForRed 传 keepInvisible=true + w/h 用 compSet.children[0]（单 variant 尺寸）
✅ 备份：code.js.bak.before_v207x

⚠️ 已知问题：
- color keyframe type=6 是推断的，Redream 报错则按 5/7/8 试调
- 子 CCB 在 Redream 9.6.0-alpha 编辑器单独打开 CCSprite 视觉偏右上（数据已对齐生产，疑为编辑器视图问题）
- V1 主场景 `rebolt.redInfos` 字典为空（如 Redream 报错再补）

最新打包：`plugin_v20.7.x.zip`

---

## 24. 生产项目结构参考（OSG_总工程 / M8P_总工程）

- 所有 .red 放 `ccb/<模块名>/` 下
- 按模块分子目录（如 `ccb/M8P_主页模块/` `ccb/M8P_导航页模块/`）
- 命名 `<前缀>_<模块>_<子>_<功能>.red`

前缀含义：

- `CS_` = 主场景
- `OSG_` = 子模块
- `JB_` = 任务
- `PC_` = 纯素材

设计尺寸：1080×2400 或 1080×2080 或 640×1136。

RED Tool V1 用扁平 `Resources/` 而非生产项目的 `ccb/<模块>/`，是 V1 简化决策。生产项目用 reboltName 作为运行时挂载点标识。

---

## 25. 工具 A vs 工具 B（两套独立工具）

**工具 A**：录屏 → Figma 还原稿
- Claude 看视频生成 scene.json
- Figma 插件 ▶ 生成在画布渲染

**工具 B**：Figma → RED Tool
- Figma 插件 🚀按钮
- POST localhost:5001
- Python 生成 .red

**关键约束**：

- 视频识别阶段拍不到多态信息，工具 A 不能自动建 Component Variants
- 设计师在 Figma 里手动整理图层 + 做 Component + 做 Variants 是必经环节
- 两个工具间数据靠 scene.json 流转
- v20.7 把工具 B 集成到 Figma 插件里（以前是独立 RED Tool 网页 UI）

---

## 26. 重要踩坑（RED Tool）

### 早期踩坑

1. preferedSize 单位错误致防穿透层渲染成小方块（必须 [100,100,2,2] 不是 0,0）
2. 顶层背景没生成 CCSprite（v15 之前 build_top_layer 不走 sprite 分支，v16 修）
3. 改代码不重启服务无效（Flask 不自动重载）
4. 进度条 percentage/direction 字段位置最终决定：percentage=100 固定写节点，direction 通过命名末尾后缀编码
5. 主场景文件可能完全没 REDFile 节点（生产项目活动入口位是空 CCNode 占位 + reboltName，运行时填）
6. Figma manifest networkAccess URL 校验严格：必须末尾带 `/`，不能用 IP，必须加 reasoning 字段

### v20.7.x 踩坑（2026-05-06）

7. **REDFile 节点写 anchorPoint 字段会让 Redream 加载主屏闪退** — 生产样本不写 anchorPoint，移除即可
8. **REDFile position 必须用百分比 [50, 50, 0, 2, 2]**（而不是绝对像素 [w/2, h/2, 0, 0, 0]），跟生产样本对齐
9. **子 CCB 根 CCNode position 必须 (0, 0)**（之前误写 (cw/2, ch/2) 导致主屏引用偏右上）；生产 shop_buy_btn 也是 (0, 0)
10. **file-level + resolution-level centeredOrigin 必须一致**（都 False，对齐生产）；不一致会让 Redream 渲染坐标错乱
11. **Figma 端 buildSceneForRed() 默认会让 visible=false 节点丢失 + fill 字段不传 + ComponentSet w/h 用合并尺寸** — code.js 必须加 `figmaFillsToHex` + `keepInvisible` + `compSet.children[0]` 三处修复
12. **scene.json 里 component 的 variant.layers 节点数可能不一致**（Figma 端只导出"该 variant 实际可见的节点"），引擎用 `merge_variants_layers` 合并全集兜底
13. **嵌套子 CCB 的孤儿引用** — 底标_倒计时 内部嵌套 INSTANCE 引用 Component 2 但 V1 不传递追溯；修复:build_child INSTANCE 分支兜底,未注册降级空 CCNode 占位
14. **color keyframe type=6** 是从 cocos2d 编号顺序推断的(生产无现成),不一定对,Redream 报错就改 5/7/8 试
15. **未解之谜**:子 CCB 在 Redream 9.6.0-alpha 编辑器单独打开时 CCSprite 视觉偏右上;数据格式跟生产严格对齐了,试过改 anchor=(0,0)+左下角 position 反而更糟,可能是 Redream 编辑器视图问题

---

## 27. "状态"和"多态"术语区分

| 术语 | 含义 | V1 是否限制 |
|---|---|---|
| 多态（用户语境）| Variant 取值数量（同 Property 内多个状态值）| 不限 |
| 多个状态维度 | 多 Variant Property | 强制 1 个 |

例：

- "常态/选中/禁用/已领取/未解锁" = 1 个 Property 5 个值（V1 允许）
- "状态 × 尺寸" = 2 个 Property（V1 报错让用户拆成多个 Component Set）

讨论时谨慎用"多态"避免歧义。
