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
- 添加资源路径：`modify --project xxx --add-resource-path Resources project`
- Build-scene：`modify build-scene --project xxx --scene Resources/xxx.red --config 源.red`
- Build-scene 子目录：`modify build-scene --project xxx --scene Resources/控件库/xxx.red --config 源.red`
- 校验：`inspect check --project xxx`（输出 `ok.` = 通过）
- 路径：`/Applications/Redream.app/Contents/MacOS/Redream`（v1.3.4）

### 注意事项

- `--json` 参数文档列了但实际不支持，不要加
- 新项目要两步：`new-project` + `--add-resource-path Resources`（默认只加 ccb）
- 同名 .red 直接覆盖
- Position 格式：`x,y,z,unitX,unitY`（帮助里的 anchorX/Y/Z 是误导）

---

## 十、Redream 节点类型清单

V1 用到的 baseClass：

- **CCNode**（容器；v20.7.x 起也用作**子 CCB 根节点**和 INSTANCE 父节点）
- **CCSprite**（图片）
- **CCLayer**（**仅主场景根节点**；v20.7.x 起子 CCB 不再用 CCLayer）
- **CCLayerColor**（占位/遮罩色块）
- **REDNodeButton**（按钮触控层）
- **CCRedLabel**（文本）
- **CCProgressTimer**（进度条）
- **REDFile**（CCB 引用；现作为父 CCNode 的子节点存在）
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

### 处理流程

```
0. CORS 头允许跨域
1. 解析 body
2. 校验 schema（screens 必填）
3. ensure_project（new-project + add-resource-path Resources）
3.5 v20.7.x V2: 反查被引用的 component_name（含传递引用追溯，支持多层嵌套）
   算法（BFS 直到收敛）：
     第 1 轮：扫 screens.layers，收集屏幕直接 INSTANCE 引用的 component
     第 N 轮：扫已收集 component 的 variants[*].layers 里的嵌套 INSTANCE
     收敛条件：某轮没有新 component 出现
   过滤：
     - 保留：被屏幕直接引用 + 通过嵌套传递引用追溯到的 component
     - 跳过：完全未被引用的孤立条目（Figma _组件库 frame 误传、component_ref 老体系、自动占位命名）
   嵌套深度由 BFS 轮数自动确定：
     - 轮数 = 嵌套层数（屏幕→A→B→C 是 4 层，BFS 跑 4 轮）
     - 自动去重防循环引用（A→B→A 这种结构 BFS 仍能收敛）
   build_child INSTANCE 分支保留"未注册降级空 CCNode 占位"作为防御兜底
4. 先生成所有子 CCB → Resources/控件库/<name>.red
   - generate_red_component(component) 生成中间结构（根节点为 CCNode，v20.7.x 改）
   - build_scene_via_cli(proj, name, tmp, subdir='控件库')
4.5 register_component_variants(components)  # 用过滤后的 components
   - 填充模块级映射 _COMPONENT_VARIANT_SEQID = {comp_name: {variant_name: seqId}}
   - 主屏 build_child 处理 INSTANCE 时按 INSTANCE.variant 查表得到 animation 字段值
5. 再生成主屏 → Resources/<name>.red
   - generate_red(screen) 生成中间结构
   - build_scene_via_cli(proj, name, tmp)
   - 主屏内 INSTANCE → make_redfile() 生成"父 CCNode + 子 REDFile"两层
6. inspect check 整体校验
7. 返回 {ok, output_dir, files[], log, error?, stage?}
```

### 防御过滤的设计意图（v20.7.x，核心约定）

**最终的"引擎控件库" = 屏幕 INSTANCE 直接引用的 Component 集合**，跟 Figma `📦_组件库` frame 解耦：

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
- 控件库实质上由"屏幕需要什么子 CCB"决定，跟 Figma 视觉布局解耦
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

