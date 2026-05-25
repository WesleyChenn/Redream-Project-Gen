# Redream CLI + Python 服务端

> 引擎 SKILL 拆分文档(v20.7.x+) · 索引见 SKILL.md

## 九、Redream CLI 关键命令

### 命令格式铁律

```
Redream [options] action
```

**action 必须在最后**，所有参数前置。

### 常用命令

- 创建项目：`modify new-project --project xxx.redproj --resolution 1080x2400`
- 添加资源路径：`modify --project xxx --add-resource-path <path> project`
- Build-scene：`modify build-scene --project xxx --scene ccb/<module>/<scene>.red --config 源.red`
- 校验：`inspect check --project xxx`（输出 `ok.` = 通过）
- 路径：`/Applications/Redream.app/Contents/MacOS/Redream`（v1.3.4）

### 注意事项

- `--json` 参数文档列了但实际不支持，不要加
- 新项目要多个 `--add-resource-path`（默认只加 ccb,我们加 `_img_plist / _img_single / font / _language` 4 条对齐生产）
- 同名 .red 直接覆盖(实际 build-scene 在目标已存在时报错, app.py `build_scene_via_cli` 会先 `os.unlink` 旧文件)
- Position 格式：`x,y,z,unitX,unitY`（帮助里的 anchorX/Y/Z 是误导）
- **inspect check 在含 CCLabelPlus 的项目里必 SIGSEGV crash**(CLI bug, 生产数据也复现) — endpoint 里改成 warning 不阻塞

---

## 十、Redream 节点类型清单

V1 用到的 baseClass：

- **CCNode**（容器；v20.7.x 起也用作**子 CCB 根节点**和 INSTANCE 父节点）
- **CCSprite**（图片;displayFrame 引用 `<scene>/<scene>_图片资源.plist + frame_name`）
- **CCLayer**（**仅主场景根节点**；v20.7.x 起子 CCB 不再用 CCLayer）
- **CCLayerColor**（占位/遮罩色块）
- **REDNodeButton**（按钮触控层）
- **CCRedLabel**（简单文本, v20.7.x 早期默认 — 当字体未就绪时用, 单层 BMFont）
- **CCLabelPlus**（v20.7.x+ 2026-05-15 默认, 多 style 叠加 BMFont,对齐生产, 需要 .redproj.fontStyle 数组定义 + Resources 字体文件齐备,否则引擎闪退)
- **CCProgressTimer**（进度条;同 CCSprite 走 displayFrame）
- **REDFile**（CCB 引用;父 CCNode + 子 REDFile 两层,redFile = `<module>/<comp>.red`）
- **RedSafeAreaLayer**（安全区）
- **ReferenceImageNode**（参考图）

---

## 十二、Python 端 /api/generate_red 流程

### 端点

- `GET /api/ping` — 连通性检测
- `POST /api/generate_red` — 主入口
- `POST /api/open_finder` — Finder 中打开路径

### 请求 body

```json
{
  "output_path": "~/Desktop/red_output",
  "scene": {
    "meta": {...},
    "components": [...],
    "screens": [...],
    "flow": [...]
  }
}
```

### 处理流程(v20.7.x+ 2026-05-15 重构 — 对齐生产 res_juice_pro 目录结构)

```
0. CORS 头允许跨域
1. 解析 body
2. 校验 schema（screens 必填）
3. ensure_project — new-project + 加 4 个资源路径 (_img_plist / _img_single / font / _language)
   _CURRENT_RESOURCES_ROOT = output_path (不再 Resources/, 直接顶层)
3.1 ensure_font_in_project(output_path) — 拷字体到 <output>/font/<语言>/
3.2 ensure_fontstyle_in_redproj(proj_path) — 写 fontStyle 数组到 .redproj (3 style × 12 lang)
3.5 反查被引用的 component_name (BFS 传递引用,见下方"防御过滤"章节)
4. _CURRENT_MODULE_NAME = screens[0].name (我们的场景一个 scene.json = 一个模块)
4.5 按界面打真图集 (必须在 component .red 生成之前, 让 _IMAGE_INDEX 就绪):
   for screen in screens:
     source_names = [sname] + [c.name for c in components]
     process_images(sname, source_names, output_path):
       - 收集所有 source 下的 PNG (按 variant 分子目录)
       - 按 classify_sprite_kind 分 bg / ui 两类
       - 各类调 pack_atlas: shelf packing 装箱 → 合成 .webp 大图 + 写 .plist (TexturePacker 兼容)
       - 输出 <output>/_img_plist/<scene>/<scene>_{图片资源,背景大图}.{plist,webp}
       - 填 _IMAGE_INDEX[(source, variant, layer)] = (atlas_rel, frame_name)
5. register_component_variants(components) — 填 _COMPONENT_VARIANT_SEQID
6. 子 CCB 生成 → <output>/ccb/<module>/<comp>.red
   - generate_red_component(component) (根 = CCNode wrapper, 内含 组_<variant> 子节点)
   - build_scene_via_cli(proj, cname, tmp, module=_CURRENT_MODULE_NAME)
7. 主屏生成 → <output>/ccb/<module>/<scene>.red
   - generate_red(screen)
   - 主屏内 INSTANCE → make_redfile() 生成"父 CCNode + 子 REDFile"两层
     - redFile = "<module>/<comp>.red" (带模块前缀, 相对 ccb resource path)
   - build_scene_via_cli(proj, sname, tmp, module=sname)
8. inspect check 校验 — 失败不阻塞 (CLI 在 CCLabelPlus 项目里有 SIGSEGV bug)
9. 返回 {ok, output_dir, files[], log, error?, stage?}
```

### 防御过滤的设计意图（v20.7.x，核心约定）

**最终的"引擎ccb" = 屏幕 INSTANCE 直接引用的 Component 集合**，跟 Figma `📦_组件库` frame 解耦：

| 来源 | Figma 端 | 引擎处理 |
|---|---|---|
| 主屏幕 INSTANCE | 屏幕里的实例 | ✅ 反查 component_name → 生成对应 .red |
| `📦_组件库` frame 内的 variant 实例 | 给设计师看的视觉文档（5 个 variant 横向并排，不可切换）| ⏭️ 引擎过滤跳过 |
| `🐭_可切换预览` frame 内的实例 | 给设计师看的可切换 variant 预览 | ⏭️ 引擎过滤跳过 |
| `component_ref`（老体系） | 旧组件库节点 | ⏭️ V1 走空 CCNode 占位，不生成 .red |
| 未命名/未使用 Component | Figma 自动占位（"Component 2" / "Rectangle 39"）| ⏭️ 引擎过滤跳过 |
| 被嵌套引用的 component（V1） | component A 内部 INSTANCE 引用 B | ⏭️ V1 跳过（嵌套 INSTANCE → 空占位）；V2 才支持 |

**为什么这么设计**：

- Figma `📦_组件库` / `🐭_可切换预览` frame 是**给设计师的视觉文档**，不是引擎要导出的资产
- 引擎要导出的子 CCB 集合实质上由"屏幕需要什么子 CCB"决定,跟 Figma 视觉布局解耦
- 即使 Figma 端 buildSceneForRed() 误传了多余 Component，引擎也只生成被实际使用的
- V1 阶段不做嵌套子 CCB（component A 内部嵌套引用 component B 的链路），V2 必做

**V1 嵌套兜底（避免 inspect 报错）**：

build_child 处理 INSTANCE 节点时，先查 `_COMPONENT_VARIANT_SEQID`：

- 命中 → 正常生成"父 CCNode + 子 REDFile"两层
- 未命中（被过滤掉的孤儿引用） → 降级为空 CCNode 占位，不生成 REDFile

这样既保持 V1 不做嵌套的简化，又避免 inspect_check 报缺失引用。

### 失败 stage 编码

- `parse` — JSON 解析失败
- `validate` — schema 校验失败
- `generate` — 中间 .red 生成失败
- `build_scene` — CLI build-scene 失败
- `inspect_check` — CLI inspect check 失败

---

## 十一、图片引用管线 — 真图集 + 按界面合并 + 按大组拆 (v20.7.x+ 2026-05-15)

对齐生产 `res_juice_pro/_img_plist/<模块>/<模块>_图片资源.{plist,webp}` 格式 — 一个模块 1 个或多个真图集。

### 目录约定

| 角色 | 路径 |
|---|---|
| 上传 PNG(插件 exportAllSprites) | `~/Desktop/figma_export/<source>/[<variant>/]<layer>.png` |
| 大组归属 sidecar(插件上传时一并写) | `~/Desktop/figma_export/<source>/_groups.json` = `{"<variant>/<layer>": "<group_name>"}` |
| Python 输出真图集 | `<output>/_img_plist/<scene>/<scene>_图片资源.{plist,webp}` |
| 多 bin 文件名 | `<scene>_图片资源_1.plist / _2.plist / ...`(单 bin 时不加序号) |
| 背景大图独立(命名 `背景_`) | `<output>/_img_plist/<scene>/<scene>_背景大图.{plist,webp}` |
| `.red` displayFrame.value | `['<scene>/<scene>_图片资源.plist', '<source>_<variant>_<layer>.png']` |

### SPRITE_NAME_PREFIXES + 分类

```python
SPRITE_NAME_PREFIXES = ('图片_', '图标_', '背景_', '插图_', '特效_', '底板_', '进度条_')

def classify_sprite_kind(layer_name):
    return 'bg' if layer_name.startswith('背景_') else 'ui'
```

`bg` → `<scene>_背景大图.{plist,webp}`;`ui` → `<scene>_图片资源.{plist,webp}`。

### Frame 命名(加 source namespace 避免冲突)

- 屏幕级:`<scene>_<layer>.png` 例 `浮层_Journey_Offer_底板_浮层.png`
- 组件 variant:`<source>_<variant>_<layer>.png` 例 `金币堆_小_图标_金币.png`

### 真图集打包(pack_atlas + shelf_pack)

Pillow 合成 + 自写 shelf packing(无 rectpack 依赖):
1. 按高降序排矩形
2. 一行一行装,行内 x 累加,行高 = 行内最高矩形
3. 宽度超 max_width 就开新行
4. 输出:.webp(lossless) + .plist(TexturePacker 兼容 frames + metadata)

### 按界面合并(per-scene merged atlas)

`process_images(scene_name, source_names, output_path)` 的 `source_names = [sname] + comp_names_all` — 主屏 + 所有 component 的 PNG 一锅煮到一个 plist。

时序约束:**必须在** generate_red_component / generate_red 之前调用,否则 lookup_image 查不到 _IMAGE_INDEX。

endpoint 顺序:`ensure_project → ensure_font → ensure_fontstyle → process_images (per screen) → generate_red_component → generate_red → inspect_check`。

### 按大组拆 plist + 4096×4096 上限 ⭐

单 webp 图集尺寸有上限,**`ATLAS_MAX_SIZE = 4096`**(常量)。装得下就 1 个 plist;装不下按 Figma 大组拆多 plist。

**大组定义**:
- 屏幕级:屏幕 frame 的**直接子节点**作为大组(`组_顶部条 / 组_装饰区 / 底板_浮层` 等)
- 组件级:整个 component 作为 1 个大组

**约束**:同一大组的所有 PNG 必须打到同一个 plist(不能跨 plist 拆)。

**实现链**:
1. 插件 `exportAllSprites` 每张 PNG 带 `group_name` 字段(屏幕直接子 name / component name)
2. `/api/upload_images` 写 sidecar `figma_export/<source>/_groups.json`
3. `process_images` 读 sidecar → 按 group 分桶 → 调 `shelf_pack_grouped`
4. `shelf_pack_grouped` 算法:
   - 阶段 1:先试单 bin 装所有(小项目短路)
   - 阶段 2:装不下,每个 group 单独算尺寸 → 按面积降序 → greedy 合并 group 进现有 bin(每加 1 个 group 重装箱判断 ≤ 4096)
   - 现有 bin 装不下就开新 bin
   - **单个 group 自身装箱后 > 4096 直接报错**(我们目前不实现拆组)
5. 输出:1 bin → `<scene>_图片资源.plist`;多 bin → `<scene>_图片资源_1.plist / _2.plist / ...`
6. `_IMAGE_INDEX` 按实际 bin 填(同一 layer 落到哪个 plist 取决于装箱结果)

### 无字体兜底

`lookup_image()` 命中 _IMAGE_INDEX 才返回路径,否则返回 ('', '') 让 displayFrame 空,**避免 inspect_check 报 missing reference**。

---

## 十二、CCLabelPlus 文本节点三件套 (v20.7.x+ 2026-05-15)

跑通 CCLabelPlus 必须 3 个配套**同时**齐, 任一缺失都让 Redream 加载 .red 时空指针解引用闪退:

1. **`.redproj.fontStyle` 数组** — `ensure_fontstyle_in_redproj()` 写入 3 style × 12 lang 完整定义
2. **`make_cclabel` 的 labelConfig = array of 3 dict**(纯白主字 + 描边深棕 + 描边更深)— `inspect_check` 报"is VECTOR, must be object" 是它自己的 bug,引擎运行时接受 array
3. **字体文件** — `ensure_font_in_project()` 拷贝 `/Users/red/Desktop/归档/font/` 到 `<output>/font/<语言>/`

历史教训(避免再走):
- CLI inspect check 在含 CCLabelPlus 的 .red 上必 SIGSEGV(生产数据也复现)— endpoint 已把 inspect 失败从 fatal 改 warning 不阻塞
- fntFile 空字符串让 Font check 阶段 CLI crash
- `.redproj.fontStyle` 空数组会让 Redream 编辑器打开 .red 闪退(根因)

---

## 十三、单图增量更新 `/api/update_image` (v20.7.x+ 2026-05-15)

设计师改一张图后**不需要重生成整个 .red 工程**,只需要替换 PNG + 重打受影响图集。

### Figma 端

- 插件 UI 加按钮 "🔄 更新选中图层(单图换图)"
- code.js `_findUpdateContext(node)` 反查祖先链拿 `source / variant / layer / group_name`
- exportAsync + base64 + postMessage

### Flask 端 `/api/update_image`

```
1. 解 base64 → 替换 ~/Desktop/figma_export/<source>/[<variant>/]<layer>.png
2. 同时更新 sidecar (figma_export/<source>/_groups.json) 那一条记录
3. 扫 <output>/_img_plist/ 下所有 scene 目录
4. 对每个 scene 调 process_images(scene, all_figma_export_sources, output_path) 重打图集
5. 返回 {ok, replaced_png, rebuilt: [scene 列表]}
```

设计师在 Redream 关闭再打开 .red 看新图(Redream 缓存图集,需要重载)。

---

