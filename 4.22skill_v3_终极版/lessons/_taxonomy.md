# Lessons 分类法 (2026-05-22 系统化引入)

> Lessons 按 **主题** 分类。每条 lesson 归 1 个主题。新加 lesson 时先选主题, 再写。

---

## 5 大主题

### A. Schema 类
**关注**: scene.json / final_scene.json 的 schema 合规性 (字段命名 / 必填字段 / 结构嵌套)
**典型适用阶段**: S7-S9 (扁平 scene.json), S11 (v20.6 schema)

### B. ccb / 组团 / 多态类
**关注**: Phase A 决议 — 抽不抽 ccb, 几个 variant, 子节点 name 一致性
**典型适用阶段**: S3 (组团识别), S6 (ccb/多态决议), S7 (variant 输出)

### C. AL / 布局类
**关注**: layoutMode 选择 / AL 字段 / 约束 / z 序
**典型适用阶段**: S3 (layoutMode 识别), S7 (AL 字段写), S10 (布局自检)

### D. Pattern 命中 / 视觉识别类
**关注**: memory ui_pattern 命中, 视觉特征 → 结构推断
**典型适用阶段**: S2 (视觉识别), S6 (pattern 命中)

### E. 工作流 / 反 satisficing 类 (元类)
**关注**: Claude 跑流程时的认知陷阱, 防止"自动连跑"导致的注意力分散 / from-exemplar 类比 / 列表行漏识别等
**典型适用阶段**: 跨步骤

---

## 命名规范

- 文件名: `lesson_<关键短语>.md` (中文 + 下划线, 避免歧义)
- 文件内 # 一级标题: `Lesson · <一句话标题>`
- SKILL.md 索引表的一句话: 跟 lesson 内的 `## 一句话` 完全一致 (同步)

---

## Lesson 库 (按主题)

### A. Schema 类
| 文件 | 一句话 |
|---|---|
| `lesson_扁平vs_v206_schema.md` | S7-S9 是扁平 scene.json, INSTANCE/components[] 是 S11 自动产物 |
| `lesson_v206schema必填字段.md` | 主路径手写 v20.6: component 必有 w/h/variant_property, INSTANCE w/h==component, layer 必有 element_class |

### B. ccb / 组团 / 多态类
| 文件 | 一句话 |
|---|---|
| `lesson_ccb维度vs多态.md` | 抽 ccb 看复用/动态/独立 ≠ 看多态; 有多态必是 ccb; 同一差异只在唯一最小单元做一次 |
| `lesson_规则11.5_子节点name一致.md` | 同结构多实例 children name 100% 一致, 否则 S11 抽不出 |
| `lesson_组团内layout单一化.md` | 一 FRAME 内不能既横排又竖排, 混合拆 wrapper |
| `lesson_复用结构必抽component.md` ⭐ 新 | 复用 ≥3 必抽 component; inline FRAME 重复 N 次 = ccb 抽取失败 |

### C. AL / 布局类
| 文件 | 一句话 |
|---|---|
| `lesson_视觉缩窄即AL.md` | S3 标 HORIZONTAL/VERTICAL → S7 必 AL, 严禁退化 NONE+绝对坐标 (跨层级一致) |
| `lesson_AL内ABSOLUTE底板z序bug.md` | AL 容器内 ABSOLUTE 底板被 Figma 拉到 z 顶层覆盖内容 → 改用 NONE 外层 + 内层 AL 容器 |

### D. Pattern 命中 / 视觉识别类
| 文件 | 一句话 |
|---|---|
| `lesson_进度条本体一整根.md` | 进度条本体永远画一整根 100%, 不按节点拆段 |
| `lesson_列表行数完整性.md` ⭐ 新 | 滚动列表识别必逐帧扫描全部行, 不能只识别首屏可见数 |

### E. 工作流 / 反 satisficing 类
| 文件 | 一句话 |
|---|---|
| `lesson_反from-exemplar.md` ⭐ 新 | 上下文里有相似项目 scene.json = 风险信号不是捷径, 禁照搬, 必每组团独立从视频+memory 重推 |

---

## 维护流程

1. 每次发现新 bug → 入 `bug-archive.md`
2. bug 复现 ≥ 2 次或可预防 → 写新 lesson (按模板)
3. lesson 写完 → 更新 `_taxonomy.md` (本文件) + `SKILL.md` Lessons 索引表 + `_coverage.md` 覆盖度地图
4. 跑 SKILL 时 Claude 读完 SKILL.md 索引 → 触发条件命中 → 读对应 lesson 全文 → 应用
