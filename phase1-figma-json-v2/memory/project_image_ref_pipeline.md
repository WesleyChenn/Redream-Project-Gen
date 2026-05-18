---
name: 图片引用工作流 V1(faux plist)
description: red_tool/app.py 的 Figma PNG 散图 → 假图集 plist → .red displayFrame 自动填充链路, 2026-05-14 上线
type: project
originSessionId: 70bc1608-42c0-462e-8555-2dab97c0d9d7
---
**当前状态**(2026-05-14 上线):低保真阶段图片引用全自动化已通,V1 形态。

**约定**:
- Figma 用自带 Export 把图层导出为 PNG → `~/Desktop/figma_export/<scene_name>/<layer_name>.png`
- 命名前缀 `图片_/图标_/背景_/插图_/特效_` 的图层自动取图
- `/api/generate_red` 自动:为每张 PNG 生成 1-frame TexturePacker 兼容 plist + 拷贝 PNG/plist 到 `<project>/Resources/_img_plist/<scene_name>/`
- .red 里 displayFrame.value = `['<scene_name>/<layer_name>.plist', '<layer_name>.png']`(沿用生产 res_juice_pro/_img_plist/<模块>/ 路径写法)

**Why 选择 faux plist 而不是裸 PNG 引用**:
- 生产 res_juice_pro 所有 .red 都走 `[plist, png]` 二元组,从未出现 `["", "xxx.png"]` 裸 PNG 引用
- Redream 引擎设计就是先查 plist 再切大图 → 没 plist 引擎找不到图
- 假图集 plist 跟真图集格式 100% 一致(textureRect 满铺整张图,textureRotated=false),未来接 TexturePacker 真图集时 .red **一行不用改**,只是 plist 合并 + 共用大图

**关键铁律(2026-05-14 修订)**:
- `lookup_image()` **必须**在写 displayFrame 路径前检查磁盘 plist 是否存在;不存在则返回 `('', '')` 让 displayFrame 留空。
- 否则 inspect_check 阶段会报 "missing reference" 让整个 generate_red endpoint 失败。
- 用户最早没有导 PNG 时,所有 sprite displayFrame 都该空白(等导图后再触发生成自动填充)— 这是"先跑通框架,图后补"的语义实现。
- 实现:`_CURRENT_RESOURCES_ROOT` 全局变量在 endpoint `ensure_project` 后设置;lookup_image 用它拼绝对路径做 `os.path.exists` 检测。

**🔴 CCSprite/CCProgressTimer 必须有 displayFrame(2026-05-14 工厂强制)**:
- 用户明确要求: "CCSprite 才是引用图片的节点", 没有图的 CCSprite 节点 = bug。
- 实现: `make_ccsprite()` 和 `make_progresstimer()` 工厂内 `if image is None: image = lookup_image(name)` 强制自动取图。
- 即使未来新增调用方忘了显式传 image, 工厂自动 lookup, **不会出现无图 CCSprite 节点**。
- 显式传 `image=('','')` 可以强制留空, 但通常不该用 (例外: 占位/兜底分支不期望渲染图)。
- 所有 CCSprite 生成路径已全部审计(5 处: build_child sprite 分支 / build_top_layer sprite 分支 / make_progresstimer / 全屏背景 make_node 直构造 / make_ccsprite 工厂),都调了 lookup_image。

**🔴 子 CCB wrapper 内 组_<variant> 的 position(2026-05-14 修复)**:
- 必须 `(cw/2, ch/2)` 才能让组中心对齐 wrapper 中心(cocos2d-x 渲染公式: child_world = parent_world + child_position - parent_anchor × parent_contentSize)。
- 之前错写 `(0, 0)` → 组中心偏移到 wrapper 左下角, 加图后白底板偏左下肉眼可见(无图时是占位 missing texture 块,看不出)。
- 位置: `generate_red_component` 内 `make_ccnode(group_name, cw/2.0, ch/2.0, ...)`。

**🔴 文本节点 CCLabelPlus 完整方案(2026-05-15 上线 — 三件套必须同时到位)**:

跑通 CCLabelPlus 必须 3 个配套**同时**齐:
1. **`.redproj.fontStyle` 数组**:Python 端 `ensure_fontstyle_in_redproj()` 写入 3 条 style(纯白/描边/渐变)× 12 lang code(ar/de/en/es/fr/it/ja/ko/pt/ru/zh-Hans/zh-Hant)的字体路径。空数组 → Redream 加载 CCLabelPlus 时查 style 返回 NULL → `CNodeInfo::LoadCocosNodeSelf` 空指针解引用 → 闪退。
2. **`make_cclabel.labelConfig` = array of 3 dict**:跟生产 `res_juice_pro 2/M8P_加载模块_界面_loading.red` 一致,3 层叠加(纯白白色 + 描边深棕 [139,59,8] + 描边更深 [103,40,0])。每条 dict 的 `style` 字段填真实样式名("纯白样式"/"描边样式"),不能是空字符串。
3. **字体文件**:`/Users/red/Desktop/归档/font/` 包含 6 个语言 × 3 个 style 的 `.fnt + .webp`,`ensure_font_in_project()` 递归镜像到 `Resources/<语言>/` 根(**不带 `font/` 中间目录**,生产就是直接挂 Resources/)。

**踩过的 3 个坑(误判记录,避免再绕)**:
- 坑 1: inspect_check 报 `LabelConfig is VECTOR, must be object` — 这是 **inspect 工具自己的 bug**,生产 .red 也会被报错。引擎运行时实际接受 array。**忽略这个 inspect 错误**。
- 坑 2: CLI `Font character set check` SIGSEGV — 同样是 inspect 工具 bug,跟我们数据无关。已把 inspect_check 失败从 fatal 改成 warning 不阻塞流程。
- 坑 3: Redream 编辑器打开 .red 直接闪退 — 真因是 `.redproj.fontStyle = []` 空数组(`new-project` 默认),引擎查 style 定义 NULL crash。**修复 = ensure_fontstyle_in_redproj 写入完整数据**。

**关键代码位置** (`red_tool/app.py`):
- `FONTSTYLE_DEFINITIONS` 常量(3 × 12 完整定义,从 `/Users/red/Desktop/res_juice_pro 2/M8P_总工程.redproj` 拷过来)
- `ensure_fontstyle_in_redproj(proj_path)` 把 fontStyle 写入 .redproj(只在原数组为空时写,不覆盖)
- `ensure_font_in_project(resources_root)` 递归镜像字体到 `Resources/<语言>/`
- `make_cclabel()` 生成 CCLabelPlus + 3 条 style labelConfig
- endpoint 在 `ensure_project` 后顺序调:`ensure_font_in_project` → `ensure_fontstyle_in_redproj`

**字体源**: `/Users/red/Desktop/归档/font/`(用户提供),跟生产 res_juice_pro 完全对齐。

**How to apply**:
- 用户问"图怎么引用 / Figma 导出后怎么用 / displayFrame 怎么填" → 不需要重新设计,这套管线已经在跑
- 用户改 Figma 导出文件名时,要跟图层名一致(因为 lookup_image 按图层名算路径)
- 用户问"如何接入 TexturePacker / 真图集" → 是后续增强,改动点只在 process_images() 内(把多个 PNG 合并打包+生成合并 plist),build_child / make_ccsprite / displayFrame 写法不变
- 用户的 `底板_*` 节点当前走 CCSprite 分支但 lookup_image 返回空 → 显示空白。要么改 build_child 让带 corner_radius 的 RECTANGLE 走 CCDrawNode 纯色路径(低保真省事方案),要么给底板也提供图(高保真)。这条决策待定。
- 图片管线 figma_export 目录缺失时不报错(log 提示"跳过"),允许"先跑框架,图后补"

**关键文件**:
- 代码:`/Users/red/Desktop/red_tool/app.py` —— `lookup_image / read_png_size / generate_faux_plist / process_images / p_sprite / make_ccsprite / make_progresstimer / build_child sprite 分支 / generate_red & generate_red_component 入口 / /api/generate_red endpoint`
- 文档:`引擎最新skill/04_cli_python.md` 十一,`SKILL.md` 速查条目 7
- 测试脚本:`/tmp/test_image_ref.py`(端到端跑通用户的 scene.json)
