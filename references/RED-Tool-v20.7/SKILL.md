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
