---
name: CCNode 0×0 + constraints V2 整体重构
description: red_tool/app.py 把 CCNode wrapper 改 0×0 + anchor=(0,0) + children 绝对左下定位的方案,跟 constraints 字段读取一起在 V2 阶段做,V1 不做
type: project
originSessionId: 70bc1608-42c0-462e-8555-2dab97c0d9d7
---
**决策**(2026-05-14,用户口头确认):红框 .red 文件里 wrapper CCNode 改 0×0 的改造,延后到 V2 跟 constraints 字段读取一起做。

**Why**:
- 生产样本(`ui_clock.red` 等)所有 wrapper CCNode 都是 `contentSize=(0,0)` + `anchor=(0,0)` + children 用绝对像素相对父左下角定位 — 这是 Redream/cocos2d-x 项目的标准模式,不是激进重构。
- 但当前 `red_tool/app.py` 的 `build_children` / `build_top_layer` / `merge_edge_nodes` 都按 `anchor=(0.5,0.5)` + children 相对父中心定位算 px/py,跟 Figma constraints 字段(LEFT/RIGHT/SCALE/CENTER 等)的真正读取是同一套坐标体系的事。
- 单独改 CCNode 0×0 必须同时重写 children position 算法 → 跟 constraints V2 改动 100% 重叠,合并做更省事。
- 之前(2026-05-14 当天)尝试"无差别改 0×0 保留 anchor=(0.5,0.5)"失败 — `界面_Royal_Pass.red` 节点飞散到 +X 4000px 外。失败的根因记录在 `引擎最新skill/01_schema_coord.md` 六(已删,因决策回滚后不再相关)。

**How to apply**:
- 当用户提到"做 constraints V2 / V2 坐标 / 子节点 constraints 字段"时,把 CCNode 0×0 改造**捆绑一起做**,不要单独推进一边。
- 当用户问"为什么生成的 CCNode 大多有尺寸而不是 0×0"时,先解释这是 cocos2d-x 渲染原点公式 + 当前 anchor=(0.5,0.5) 体系的必然结果,然后指向 V2 整体重构。
- 不要单独改 wrapper 的 contentSize 而不改 anchor + children position — 已实测会让节点飞。
- 已实现:`red_tool/app.py` 主屏 resolutions 4 套预设(设计 1080×2400 / 正常 1080×2080 / 偏宽 1560×2080 / 偏高 1080×2800),这条独立于 V2,2026-05-14 已上线,不在延后范围内。
