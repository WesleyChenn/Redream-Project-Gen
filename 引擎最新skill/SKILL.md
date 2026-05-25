# RED Tool 引擎 SKILL(v20.7.x+,2026-05-11 拆分)

> 引擎侧规则集 · 跟 Figma SKILL(`/Users/red/Desktop/4.22最新skill/`)对照看
> · 之前是单文件 1199 行,现按主题拆成 7 个文件 + 1 索引

## 文档结构

| 文件 | 行数 | 主题 |
|---|---|---|
| **[00_overview.md](00_overview.md)** | ~80 | 工具概述 + 启动 + 输入输出 + 整体管线 |
| **[01_schema_coord.md](01_schema_coord.md)** | ~160 | scene.json schema(v20.6)+ 节点结构(v16+)+ 坐标规则 + 单位约定 |
| **[02_naming.md](02_naming.md)** | ~80 | 按钮命名规则(v20)+ 进度条规范(v20.4)+ 命名约定 |
| **[03_component.md](03_component.md)** ⭐ | ~370 | **核心**:封装方案(Component / Variant / 子 CCB / sequence / 组级 keyframe / 空 Variant)|
| **[04_cli_python.md](04_cli_python.md)** | ~145 | Redream CLI 命令 + 节点类型清单 + Python `/api/generate_red` 流程 |
| **[05_figma_plugin.md](05_figma_plugin.md)** | ~145 | Figma 插件 v20.7 集成(code.js / 4 个 Tab)|
| **[06_misc.md](06_misc.md)** | ~265 | 文件管理 + 行为树 + V1 排除项 + 术语 + 踩坑清单 + 进度 + 附录 |
| **[MEMORY.md](MEMORY.md)** | ~615 | 教训记录(30 条,按时间排,跟 SKILL 配套读)|

## 按场景找文档

| 你要做什么 | 主要看哪几个文件 |
|---|---|
| 给同事讲整体架构 | `00_overview.md` |
| 写 / 改 scene.json | `01_schema_coord.md` + `02_naming.md` |
| 改 Component / Variant 实现 | `03_component.md` ⭐ |
| 调 .red 生成 | `04_cli_python.md` + `03_component.md` |
| 改 Figma 插件 | `05_figma_plugin.md` |
| 看踩坑历史 | `MEMORY.md` |

## v20.7.x 关键规则(速查)

跨多个文件的高频规则:

1. **8.11 Variant 组级 keyframe**(详见 `03_component.md`):每个非空 Variant 一个 `组_<Variant名>` CCNode 容器,共享图层在每组复制一份,sequence 给对应组打 visible=True
2. **8.12 空 Variant**:不创建组,不打 keyframe,sequence 仍生成 → 视觉空
3. **REDFile 节点格式**(`03_component.md` 8.8):父 CCNode + 子 REDFile 两层,**不写 anchorPoint**(写了 Redream 崩溃)
4. **INSTANCE.variant → sequenceId**(`03_component.md` 8.9):主屏 INSTANCE 按 variant 查表得到 animation 字段
5. **空变体登记表保留**(`_COMPONENT_EMPTY_VARIANTS`):自检 / 文档用,主流程不依赖
6. **主屏 4 套 resolutions**(v20.7.x+ 2026-05-14,详见 `01_schema_coord.md` 六):主屏 .red 预置 设计(1080×2400)/正常(1080×2080)/偏宽(1560×2080)/偏高(1080×2800) 4 条分辨率, currentResolution=0 默认进入设计分辨率
7. **图片引用管线 — 真图集 + 按界面合并**(v20.7.x+ 2026-05-15 重构,详见 `04_cli_python.md` 十一):
   - **Figma 端**:插件 `exportAllSprites` 走 scene.json 驱动 + INSTANCE.mainComponent 引用链找节点, 按 variant 分子目录上传 PNG 到 `~/Desktop/figma_export/<source>/[<variant>/]<layer>.png`
   - **Python 端**:`process_images(scene, source_names, output_path)` 用 Pillow + 自写 shelf 装箱算法把多个 source 的 PNG 真打包成 1 个 webp 大图 + 1 个 plist (TexturePacker 兼容). 按界面合并 = 一个屏幕 + 它引用的所有 component 的 PNG 合到一个图集
   - **分类**:命名 `背景_` → `<scene>_背景大图.{plist,webp}`;其他 sprite 前缀 → `<scene>_图片资源.{plist,webp}`
   - **命名前缀**:`图片_/图标_/背景_/插图_/特效_/底板_/进度条_`(2026-05-15 加 底板_ 进度条_)
   - **frame 命名**:屏幕级 `<scene>_<layer>.png`;component variant `<source>_<variant>_<layer>.png`(加 namespace 避免冲突)
   - **`_IMAGE_INDEX` 全局 dict**:`{(source, variant, layer): (atlas_rel, frame_name)}` 装箱完填, `lookup_image` 直接查
8. **目录结构对齐生产 res_juice_pro**(v20.7.x+ 2026-05-15 重构,详见 `06_misc.md` 十三):**去 Resources/ 中间层**,所有资源直接挂顶层:
   - `<output>/ccb/<module>/<scene>.red + <comp>.red` (主屏 + 子 CCB 同模块目录, module = 主屏 scene_name)
   - `<output>/_img_plist/<module>/<module>_图片资源.{plist,webp}` (真图集)
   - `<output>/font/<语言>/通用_字体_<语言>_纯白/描边/渐变字体.fnt + .webp` (6 语言)
   - `.redproj.resourcePaths` 配 `_img_plist / _img_single / font / _language` 4 条
   - **redFile 引用格式**:`<module>/<comp>.red` (带模块前缀,相对 ccb resource path)
9. **CCLabelPlus 文本节点三件套**(v20.7.x+ 2026-05-15,详见 `04_cli_python.md` 十二):
   - **labelConfig** array of 3 dict(纯白主字 + 描边深棕 + 描边更深),非空 dict (`is VECTOR must be object` 是 inspect 工具 bug,引擎运行时接受 array)
   - **.redproj.fontStyle** array(3 style × 12 lang),`ensure_fontstyle_in_redproj()` 写入,**空数组会让 Redream 加载 .red 时 NULL 解引用闪退**
   - **font 文件**:`ensure_font_in_project()` 拷贝 6 语言字体到 `<output>/font/<语言>/`
   - 字体源:`/Users/red/Desktop/归档/font/`,跟生产 res_juice_pro `M8P_总工程.redproj` fontStyle 100% 对齐
10. **单图增量更新**(v20.7.x+ 2026-05-15,详见 `04_cli_python.md` 十三):Figma 选单图层 → 插件按钮 → `/api/update_image` → 替换 figma_export PNG + 重打所有受影响 scene 图集,**不重建 .red 文件**
11. **按大组拆 plist + 4096 上限**(v20.7.x+ 2026-05-15,详见 `04_cli_python.md` 十一):
    - 单 webp 上限 **4096×4096**(`ATLAS_MAX_SIZE`),装得下就 1 个 plist;装不下按"大组"拆多 plist
    - **大组定义**:屏幕级 = 屏幕的直接子 frame name(`组_顶部条 / 组_装饰区 / ...`);组件级 = 整个 component 一组 — **不拆开同一组**
    - 插件 exportAllSprites 上传时带 `group_name` 字段;Python 写 sidecar `figma_export/<source>/_groups.json`
    - 装箱算法 `shelf_pack_grouped`:先试单 bin,装不下用 First Fit Decreasing greedy 合并 group 进现有 bin
    - 文件命名:1 个 bin → `<scene>_图片资源.plist`;多 bin → `<scene>_图片资源_1.plist / _2.plist / ...`
12. **预制组件库(单一钟表特例)**(v20.7.x+ 2026-05-15,详见 `03_component.md` 8.13,Figma 端规约见 `4.22最新skill/00e_预制组件命名.md`):稳定不变 Component 直接复用 .red + 自带独立小图集
    - **命名规约**:`预制_` 前缀 C 方案 2026-05-15 已回退,当前 `PREFAB_NAMES = {钟表_指针动画}`(单一特例,沿用旧命名);其他子 ccb 都走 `components[]` 普通生成 + 视觉缩窄 / ccb 3 标准(见 `4.22最新skill/00f_视觉缩窄_ccb_3标准.md`)
    - **预制三件套**:`red_tool/prefabs/钟表_指针动画.{red,plist,webp}`(2026-05-15 升级 v3:Scale9 preferedSize + 完整 labelConfig + 总组/底板组/文本组/时钟组分类)
    - **触发**:`_collect_prefab_refs(scene)` 递归扫整个 scene.json 的 `name` / `component_ref` / `component_name` 字段,命中 `PREFAB_NAMES` 即触发 — **不要求 `components[]` 数组里声明**
    - **拦截 4 步**(app.py:2385+):自动注册 → 独立预制循环(拷 .red+.plist+.webp,加 `<module>/` 前缀) → components 防覆盖 → L1229 老体系兜底改走 REDFile
    - **单层 REDFile**:`make_redfile_single` 跟生产对齐(不包外层 CCNode,position 用百分比 unit=2,2),避免两层结构改变预制内部坐标基准
    - **INSTANCE.variant**:`lookup_variant_seqid` 默认 0 → 只支持无 variant / 单默认 variant

## 历史版本

- v1(单文件,1199 行,2026-05-09 之前)→ 备份在 `SKILL.md.bak`
- v2(7 文件拆分,2026-05-11)→ 当前

## 跨 SKILL 文档关系

```
Figma SKILL(设计师/Claude 怎么写 JSON)
    ↓ 产出 final.json
引擎 SKILL(引擎怎么把 final.json 翻译成 .red)
    ↓ 产出 .red 文件
Redream 引擎渲染
```

Figma SKILL 不感知"组_<Variant名>"这类引擎内部结构 — 那是 `app.py` 生成 .red 时的中间表现。设计师/Claude 只写 `components[].variants[].layers`,引擎自动转。
