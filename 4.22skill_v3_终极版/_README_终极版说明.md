# SKILL v3 终极版 — 2026-05-22

> 合并: 视觉缩窄即AL版 + lessons 系统化 + 分步确认

## 3 大特性

### 1. 分步确认工作流 (恢复)
- S1 → S2 → ... → S10 **每步完成必停下等用户回复「继续 SX」**
- 不再"只停 S6", 也不再"一气呵成"
- 理由 (5.21-5.22 实证): 分步确认产物质量 > 一气呵成 / 只停 S6 — 用户每步 review 拦截错误

### 2. AL 全套改进 (从 视觉缩窄即AL 版继承)
- 铁律 14: 大组团语义表 (CENTER/TOP 默认, 11 行典型 + 1 fallback)
- 铁律 15: AL = S3 layoutMode 合约 (视觉缩窄即 AL, 跨层级一致)
- 铁律 16: 按钮命名 = S6 包装类型合约 (动作词必识 `按钮_xxx`)
- 07e §"复用类 component 内部布局" 新结构: NONE 外层 + AL 内层 + 3 层 z 序
- S10 自检加 AL 内 ABSOLUTE 底板 z 序 bug 检查

### 3. Lessons 系统化 (Step 1+2 完整执行)
- 新建 3 个基础设施文件:
  - `_template.md` — 7 字段统一模板
  - `_taxonomy.md` — 5 大主题分类 + 命名规范 + 维护流程
  - `_coverage.md` — 阶段 × 错误类型覆盖度地图 + gap 标记
- 新加 3 个 lessons (按模板):
  - `lesson_列表行数完整性.md`
  - `lesson_复用结构必抽component.md`
  - `lesson_反from-exemplar.md`
- 修 1 个索引漏: `lesson_视觉缩窄即AL.md` 已加入 SKILL 索引

## 测试期待

1. **时间**: ~2 小时 (vs 只停 S6 的 40 min) — 用换质量
2. **Phase A 质量** 应该明显 > 视觉缩窄即AL 版 (因为每步停下来用户能 review)
3. **观察点**: 列表行数完整 / 副标识别准 / Choisss 不被复制到列表 / 没有从 历史 final_scene.json 对照

## 跑法

新开 Claude Code session:
- cwd: `/Users/red/Desktop/5.21工作流/4.22skill_v3_终极版/`
- 用 prompt + 视频 + ccb 描述
- 等每步停下来 → 回 "继续 SX"
- S6 决议表停时 review 仔细一点

## 旧版状态

- `4.22skill_v3/` (老老版): 不动
- `5.18工作流/4.22skill_v3/` (5.18 备份): 不动
- `5.21工作流/4.22skill_v3/` (大组团语义表版): 不动
- `5.21工作流/4.22skill_v3_只停S6/` (加速版): 不动
- `5.21工作流/4.22skill_v3_视觉缩窄即AL/` (AL改进版): 不动
- **`5.21工作流/4.22skill_v3_终极版/`** (本版): 测试中
