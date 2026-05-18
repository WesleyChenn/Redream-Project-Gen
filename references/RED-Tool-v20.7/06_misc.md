# 文件管理 / 行为树 / V1 排除 / 踩坑 / 附录

> 引擎 SKILL 拆分文档(v20.7.x+,2026-05-11) · 索引见 SKILL.md

---

## 十三、文件管理 (v20.7.x+ 2026-05-15 重构, 跟生产 res_juice_pro 100% 对齐)

### 当前 V1 输出结构

```
~/Desktop/red_output5.15.X/
├── red_project.redproj              ← 项目文件 (含 fontStyle 数组 × 3 style × 12 lang)
├── ccb/
│   └── <主屏名>/                    ← 一个 scene.json = 一个模块, 用主屏名作模块名
│       ├── <主屏>.red               ← 主屏
│       └── <comp>.red               ← 子 CCB (跟主屏同目录)
├── _img_plist/
│   └── <主屏名>/
│       ├── <主屏>_图片资源.plist + .webp  ← UI 类真图集
│       └── <主屏>_背景大图.plist + .webp  ← 仅在有 背景_ 命名时
└── font/                            ← 6 语言 BMFont
    ├── 拉丁语/
    │   ├── 通用_字体_拉丁语_纯白字体.fnt + .webp
    │   ├── 通用_字体_拉丁语_描边字体.fnt + .webp
    │   └── ... 渐变 / 数字
    └── 阿拉伯语 / 韩语 / 日语 / 俄语 / 繁体中文/
```

**.redproj resourcePaths 配置**: `_img_plist / _img_single / font / _language` 4 条 (加上 CLI 默认的 `ccb` 共 5 条)。

### 生产项目结构 (参考 res_juice_pro)

```
res_juice_pro/                       ← 顶层项目根 (无 Resources 中间层!)
├── M8P_总工程.redproj
├── _ccbi/                           ← Redream 编译产物 .redream
├── _img_plist/<模块>/               ← 真图集 plist + webp
├── _img_single/<模块>/              ← 单图 (不进图集的大图)
├── _language/                       ← .lan 多语言
├── _spine/  _wise_安卓/             ← 动画/音频
├── _公共资源/
├── ccb/<模块>/<name>.red            ← .red 按模块分目录
├── cfg/  image/  spine/  资源打包/  ← 其他资源
└── (字体在外部共享 ../res_xxx_common/font/)
```

**对齐情况** (2026-05-15):
| 项 | 之前 | 现在 |
|---|---|---|
| Resources/ 中间层 | 有 | **去掉**, 资源直接挂顶层 |
| .red 文件位置 | Resources/ccb/ 扁平 | ccb/<模块>/ 模块子目录 (跟生产一致) |
| 图集 plist | Resources/image/ 散 plist | _img_plist/<模块>/ 真图集 (跟生产一致) |
| 字体 | Resources/<语言>/ | font/<语言>/ (中间层 font, .redproj 加 resourcePath) |

### 命名规范（生产项目）

`<前缀>_<模块>_<子分类>_<功能>.red`

前缀：

- `CS_` = C-Scene 主界面
- `OSG_` = Object/SubGroup 子模块
- `JB_` = Job 任务模块
- `PC_` = P-Component 纯素材

### 注意事项

- 同名文件直接覆盖
- 改 RED Tool 代码后，删除旧的 red_output 重新生成
- Redream 里关掉项目重新打开 .redproj 才能看到更新

---

## 十四、.rebolt 行为树（V1 不实现）

`.rebolt` 文件是 JSON 格式，含：

- `CustomFunc` — 函数表
- `CustomVar` — 变量表
- `RedFileList` — 子 CCB 引用（reboltId → DisplayName）
- `TreeList` — 行为树本体

### 关键节点类型

- `BTCustomFuncHeadAction` — 函数入口
- `BTPlaySceneTimeLineWaitAction` — 播某个子节点的指定 timeline 并等待结束
  - `redSelect`: 操作哪个子 CCB
  - `baseSelect`: 播哪条 timeline（Value=sequenceId）
- `BTNotificationToCoderAction` — 通知客户端代码

### V1 现状

`.rebolt` 只在"有逻辑的协调容器"那级生成（如底部导航栏）。单个图标子 CCB 没有同名 `.rebolt`。

RED Tool V1 不生成 `.rebolt`，所以 `animation=-2` 加载后视觉冻结在常态。

---

## 十五、V1 排除项（V2 优先级）

### 🔥 V2 第一批要做（绝对要做）

- ✅ **4.3 嵌套子 CCB（已实装 v20.7.x V2 / 2026-05-06）**
  - api_generate_red BFS 传递追溯：第 1 轮扫屏幕，第 N 轮扫已收集 component 内部 INSTANCE，收敛即停
  - 嵌套深度由 BFS 轮数自动确定（屏幕→A→B→C 4 层）
  - 自动去重防循环引用（A→B→A 仍能收敛）
  - build_child INSTANCE 分支保留"未注册降级空 CCNode"作为兜底防御
  - 已测试:Shop 模型 4 层嵌套追溯通过
- 4.12 Instance 缩放（待 Redream 测试是否支持 contentSize 覆盖）
- **嵌套子节点 constraints 处理**（V2 第一批,响应式完整翻译,跟约束完全翻译合并）
- 4.6 多分辨率配置（5 种：设计/正常/偏宽/偏高/Node）

### ⚠️ V2 第二批

- 4.11 状态切换（接 .rebolt 行为树）
- 4.1 .rebolt 行为树本体生成
- 4.5 多语言 / 字体样式
- 4.4 Prototype Flow 页面跳转

### ❄️ 长期

- 4.2 复杂动画 Variant（带运动的状态切换）
- 4.10 Instance 镜像翻转
- 4.13 Variant rotation 差异
- 老 component_ref 体系迁移到新体系

---

## 十六、术语区分

### "状态" vs "多态"

| 术语 | 含义 | V1 是否限制 |
|---|---|---|
| Variant 取值数量 | 同 Property 内多少个值（"常态/选中/禁用"3 个值）| 不限 |
| Variant Property 维度 | 几个状态轴（"状态"轴 + "尺寸"轴 = 2 维度）| 强制 1 个 |

讨论时谨慎用"多态"避免歧义。用户语境下"多态" = "Variant 取值数量"。

---

## 十七、踩坑清单

### 早期踩坑

| 错误 | 原因 |
|---|---|
| Internal Server Error | 看终端 Traceback |
| Failed to fetch | Flask 没启动 |
| 所有节点挤在左上角 | 喂错 JSON（用了生成 JSON 不是导出 JSON）|
| 防穿透层渲染成小方块 | preferedSize 单位错误（应为 `[100,100,2,2]`）|
| 顶层背景没有 Sprite | v15 之前的 bug，v16 已修 |
| 进度条节点不识别 | type 不是 RECTANGLE，或 name 没以 `进度条_` 开头 |
| 多个 TOP 节点重叠 | merge_edge_nodes 合并算法没生效 |
| Figma 插件 manifest 报错 | URL 末尾要带 `/`，不能用 IP，要加 reasoning 字段 |
| 改代码不重启服务 | Flask 不自动重载，必须 Ctrl+C 重启 |

### v20.7.x 踩坑（2026-05-06）

| 错误 | 原因 / 修复 |
|---|---|
| Redream 加载主屏后闪退 | REDFile 节点写了 `anchorPoint` 字段；生产样本无此字段 → 移除 anchorPoint，position 改百分比 `[50, 50, 0, 2, 2]` |
| ccb出现 `Component 2.red` / `Rectangle 39.red` | Figma 端 buildSceneForRed() 把 _组件库 frame 误识别成 component；引擎做防御过滤（只生成屏幕 INSTANCE 直接引用的）|
| 子 CCB 切 sequence 视觉无变化（5 条 sequence 一样）| ① keyframe 没生成（Figma 端 visible/fill 字段没传）→ 修 code.js: `figmaFillsToHex` 提取颜色 + `keepInvisible` 保留隐藏节点；② 引擎合并 variants 全集 + diff 算法扩展 |
| Component w=5520 不是 1080 | Figma 端 buildSceneForRed() 用 `compSet.width`（=N variants 横向并排合并宽度）；改用 `compSet.children[0].width`（单 variant 宽度）|
| 主屏内容右偏 | 子 CCB 根节点 position 写成 `(cw/2, ch/2)`；生产样本是 `(0, 0)` → 改 |
| inspect_check 报缺失引用 | `底标_倒计时.red → Component 2.red` 嵌套引用，但 Component 2 被过滤了；V1 不做嵌套传递追溯 → build_child INSTANCE 分支加兜底：未注册的 component 引用降级空 CCNode 占位 |
| INSTANCE 节点空白（旧 V1 行为）| `animation = -2` 不播任何 sequence；v20.7.x 改成按 INSTANCE.variant 映射 sequenceId |
| 子 CCB 在 Redream 编辑器里看似错位（CCSprite 黑块偏右上）| **未解之谜**：试过改 anchor=(0,0) + 左下角 position 反而更糟；可能是 Redream 9.6.0-alpha 编辑器视图问题，不是数据问题。需进一步验证主屏渲染是否正常 |

### Redream 节点格式注意事项（v20.7.x 总结）

| 节点 | position | anchorPoint | contentSize | 备注 |
|---|---|---|---|---|
| 子 CCB 根 CCNode | `[0, 0, 0, 0, 0]` 绝对像素 | `[0.5, 0.5]` | 真实 cw × ch | 严格对齐生产样本 shop_buy_btn |
| 主屏 INSTANCE 父 CCNode | INSTANCE 在场景的位置 | `[0.5, 0.5]` | INSTANCE 真实 w × h | 承载坐标/约束 |
| 子 REDFile（v20.7.x 关键）| `[50, 50, 0, 2, 2]` **百分比** | **不写**（用默认）| **不写**（由子 CCB 决定）| 写了 anchorPoint 会让 Redream 加载崩溃 |
| 子 CCB file 设置 | — | — | — | `centeredOrigin: False` + `resolutions[0].centeredOrigin: False`（两层一致，对齐生产）|

---

## 十八、关键文件路径

### Python 端

- `~/Desktop/red_tool/app.py`（主代码）

### Figma 插件

- 插件源码（不固定，自己管理目录）
- `manifest.json` / `code.js` / `ui.html`

### 输出

- `~/Desktop/red_output/`（默认）

### 真实样本（参考）

- `OSG_总工程.redproj`（1080×2080，12 语言，3 字体）
- `M8P_总工程.redproj`（640×1136，老分辨率项目）

### 当前打包

- `plugin_v20.7.2.zip`（最新）

---

## 十九、当前进度（2026-05-06，v20.7.x）

✅ Plan 模式 6 条规范全部确认
✅ Figma 插件 v20.7 加 🚀 Tab
✅ Python `/api/generate_red` 完整流程通
✅ 子 CCB 生成实装(`ccb/<module>/<name>.red`,v20.7.x+ 2026-05-15 重构后)
✅ 主场景 INSTANCE → REDFile 引用

### v20.7.x 调优完整 changelog（2026-05-06）

**引擎端**（`~/Desktop/red_tool/app.py`）：

✅ **节点结构改造**
- 子 CCB 根节点 CCLayer → **CCNode 单层**（displayName = 组件名，position=(0,0)）
- 主场景 INSTANCE → **父 CCNode + 子 REDFile 两层**（父承载坐标/约束，子 REDFile 引用 CCB）
- file-level / resolution-level `centeredOrigin` 都设 False（对齐生产样本 shop_buy_btn / shop_gold）

✅ **REDFile 节点格式严格化**（避免 Redream 加载崩溃）
- properties 仅 5 个：position / opacity / color / redFile / animation
- position 用百分比 `[50, 50, 0, 2, 2]` 居中
- **不写 anchorPoint**（显式写会让 Redream 加载崩溃）
- **不写 contentSize**（由子 CCB 自决）

✅ **② INSTANCE.variant → sequenceId 映射**
- 模块级 `_COMPONENT_VARIANT_SEQID` 映射
- 主屏生成前 `register_component_variants(components)` 填充
- build_child 处理 INSTANCE 时按 INSTANCE.variant 查表得到 animation 字段
- 默认 variant → 0；其他按出现顺序递增

✅ **③ variant_diffs 解析实装**
- `merge_variants_layers()` 合并所有 variant 的 layers 全集（兜底 Figma 端漏传节点）
- `diff_variant_against_default()` 按 name 匹配，提取 visible / fill 差异（三种 case）
- `write_variant_keyframes()` 写入对应节点 `animatedProperties[seqId]` keyframe
- `apply_default_visible()` 默认 Variant visible=False 写到节点 properties
- KEYFRAME_TYPE 表（从生产 res_juice_pro 提取）：visible=1, opacity=5, color=6, position=3 等

✅ **components 防御过滤**
- 扫描所有 screens 反查 INSTANCE.component_name
- 只生成被屏幕直接引用的 Component（跳过 Figma _组件库 误传 / component_ref 老体系）
- V1 不做传递追溯（嵌套子 CCB → V2 必做）
- V1 兜底：孤儿引用降级为空 CCNode 占位（避免 inspect_check 报缺失引用）

**Figma 插件端**（`~/Desktop/最新插件/code.js`）：

✅ **三处 bug 修复**（让 scene.json 包含完整 variant 数据）
- 加 `figmaFillsToHex(fills)` 工具函数（从 Figma node.fills 提取 #RRGGBB）
- `nodeToJsonForRed` 加 `keepInvisible` 参数：component variants 扫描时保留隐藏节点（写 visible:false）；RECTANGLE/TEXT/FRAME 三处加 fill 字段输出
- `componentSetToJsonForRed`：调用 nodeToJsonForRed 传 keepInvisible=true；w/h 用 `compSet.children[0]`（单 variant 尺寸，不是 ComponentSet 整体合并宽度 5520）
- 备份：`code.js.bak.before_v207x`

### 当前已知问题

⚠️ **color keyframe type=6** 是从 cocos2d 编号顺序推断的（生产样本无现成 color keyframe 可对照）。如果 Redream 加载报错或不生效，按 5/7/8 试调

⚠️ **子 CCB 在 Redream 9.6.0-alpha 编辑器单独打开**：CCSprite 黑块视觉偏右上（数据格式跟生产 shop_gold 严格对齐了，试过改 anchor=(0,0)+左下角 position 反而更糟）。可能是 Redream 编辑器视图问题。**主屏渲染是否受影响待 user 验证**

⚠️ V1 主场景 `rebolt.redInfos` 字典为空（如 Redream 报错再补）

⚠️ Figma 端 `_组件库` / `🐭_可切换预览` frame 内部仍可能误传 component（自动占位命名 Component 2 / Rectangle 39 等）；引擎防御过滤已经能挡掉，但根本治理在 Figma 端 buildSceneForRed 排除非屏幕 frame

---

## 附录：Plan 模式确认结论速查

1. **判断 Component**：复用 / 动态（V1 排除"独立"）
2. **判断 Variant**：状态多态（不含文本/数字/图片url 数据驱动差异）
3. **命名规范**：Component 名 = 文件名 / 默认 Variant = "常态" / 单 Property / "状态"
4. **路径**(v20.7.x+ 2026-05-15 后):`ccb/<module>/<name>.red`(主屏跟子 CCB 同模块目录)
5. **REDFile 节点**（v20.7.x）：父 CCNode（displayName=INSTANCE.name，含 contentSize+constraints）+ 子 REDFile（displayName=组件名，reboltName=INSTANCE.name，animation=按 variant 映射的 sequenceId）
6. **JSON 顶层**：screens + components + flow（meta 可选）
7. **Instance 限制**：不允许镜像 / 允许缩放（待测试）/ 不嵌套封装
8. **6 个差异属性**：visible / opacity / position / scale / displayFrame / color
9. **component_ref**：V1 空 CCNode 占位，老体系不展开
10. **多选支持**：选中多个屏幕 → 自动反查并连带生成子 CCB
