---
name: 预制组件库机制
description: red_tool/prefabs/ 直接复用稳定不变的 Component .red, 跳过 generate_red_component
type: project
originSessionId: 70bc1608-42c0-462e-8555-2dab97c0d9d7
---
预制组件库:稳定不变的 Component(典型 `底标_倒计时`)直接拿成品 `.red` 复用,跳过引擎重新生成。

**Why**:多次复用 + 视觉零变化的模块,每次重生成既浪费又容易踩生成管线迭代引入的回归 bug。沉淀已验证的 .red 即可。

**How to apply**(2026-05-15 升级 — 单一钟表特例,`预制_` C 方案已回退):
- 预制三件套:`red_tool/prefabs/钟表_指针动画.{red,plist,webp}`(沿用旧命名,无 `预制_` 前缀)
- 触发集合:`PREFAB_NAMES = {'钟表_指针动画'}` — 唯一一个,其他子 ccb 都走 `components[]` 普通生成(用视觉缩窄机制 + ccb 3 标准 决定怎么抽,见 `4.22最新skill/00f_视觉缩窄_ccb_3标准.md` 待 C 阶段新建)
- 预制内容:Scale9 长条底板+钟面+指针 360° 旋转+CCLabelPlus 占位文本("11:59"/"Finished")+2 sequence(进行中/已结束),**沉淀 v3**(85KB red + 1800b plist + 14192b webp)
- Figma 端命名规约权威文档:`4.22最新skill/00e_预制组件命名.md` (含 4 条边界澄清:00a 命名锁/component_ref 同名/按钮装饰铁律/scale 公式)
- 触发逻辑:**`_collect_prefab_refs(scene)` 递归扫整个 scene.json**,任意 `component_ref` / `component_name` 命中 `PREFAB_NAMES` 即触发。**不需要 scene.json 的 `components[]` 数组里再声明** — 开箱即用
- 处理流程 4 步(见 `引擎最新skill/03_component.md` 8.13):
   1. `register_component_variants` 后自动把命中预制名注册到 `_COMPONENT_VARIANT_SEQID`(避开兜底)
   2. 独立预制循环(先于 components 循环跑):拷 .red + 同步 .plist/.webp;源缺则 `pop` 注册撤销 → 走兜底空 CCNode 避免破引用
   3. components 循环防覆盖:`cname in prefab_refs_in_use` 跳过
   4. L1229 老体系 component_ref 兜底改:命中已注册预制走 REDFile,否则空 CCNode
- 预制 .red displayFrame 规约:`["<cname>.plist", "<cname>_<layer>.png"]` — 跨项目零冲突
- 完整 spec:`引擎最新skill/03_component.md` 8.13
