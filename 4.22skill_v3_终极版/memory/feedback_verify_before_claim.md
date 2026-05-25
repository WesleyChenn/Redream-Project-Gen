---
name: 下结论前先用工具验证,不要凭印象说"已改完"
description: 涉及"代码是否改过 / 服务是否运行 / 文件是否存在"等事实声明前,必须 grep/ls/lsof/cat 验证,不要凭对话记忆下结论
type: feedback
originSessionId: dfb7fa16-bf22-4721-a9bf-80258af3655e
---
任何关于**事实状态**的声明(代码是否改过 / 服务是否运行 / 文件内容如何 / 函数是否存在),**做声明前必须用工具验证一次**,不要凭对话记忆或印象。

**Why**:
- RoyalPass 项目里反复出现:用户问"X 改了吗",我答"改了/已实现",但实际可能没改完整或根本没改。
- 2026-05-09 晚:用户问"Flask 改了吗",我推断"插件加载旧版"但当时没 lsof 验证 → 后来对的(用户确认),但下次可能不对。
- 同晚:用户问"引擎 python 改了吗",我先答"已实现完毕"再 grep 验证才发现确实改了 — 这次运气好但顺序不对。
- 没验证就下结论 → 用户必须再问一遍 → 浪费时间 + 让用户不信任。

**How to apply**:
触发场景(以下任意一项,必须先用工具验证):
- 用户问"X 改了吗 / 跑了吗 / 存在吗 / 输出是 Y 吗"
- 自己想说"X 已实现 / 已改 / 已修复 / 应该是 Y"
- 涉及 plan 里的"实现指向" / "已实现"等措辞前

工具:
- 代码是否含函数 / 字段 / 字符串: `grep -n "X" /path/to/file`
- 服务是否运行: `lsof -i :PORT` 或 `ps aux | grep`
- 文件是否存在 / mtime: `ls -la /path/` / `stat -f "%Sm" /path`
- JSON / 配置内容: `python3 -c "import json; print(json.load(open('x'))[...])"` 或 `cat | jq`

**正确流程**:
1. 用户问 → 立即 grep/ls/stat 验证 → 看到证据后再回答
2. 自己想下结论前 → 同上

**反面**:
- ❌ "X 已实现完毕,详细见 ..."(没验证)
- ❌ "Flask 加载旧版"(没 lsof 验证就推断)
- ❌ "代码里有 is_empty_variant 函数"(没 grep)
- ❌ **2026-05-15 Royal Pass `组_奖励` Variant 给错**:用户问"哪些有多态",我凭印象答 `组_奖励 = 普通/限时 2 Variant`,**没 grep SKILL** 看奖励物现成规则。用户提醒"宝箱和道具分开看 + 内部异构 + 道具程序换图"我才 grep,发现 SKILL 早就完整定义了"枚举+占位混合 Variant"模式(4.22skill_v2/06_S6 #3 例外 1 + 07d §2.5),正确方案是 `组_奖励 = 灰宝箱/红宝箱/金宝箱(无文本) + 道具(占位含 icon+文本) 4 Variants 内部异构`,我给的方案完全错。

**正面**:
- ✅ 先 grep `is_empty_variant`, 看到 line 391 后再说"在 line 391"
- ✅ 先 `lsof -i :5001` 看到 PID, 再说"Flask 在跑且 PID=29385"

**特别针对"手写 v20.6 schema"(2026-05-18 Team Battle 错位事故)**:
- ❌ 走主路径(Claude 直接产 v20.6 schema,跳过 extract_components.py)时,我凭"component=name+variants"直觉写,**没 cat output 正确样本对照字段**,漏了 component 顶层 `w/h/variant_property` → 设计师粘进 Figma 全错位(元素飘移/重叠/巨大),用户截图才发现。
- **铁律**:**写任何 v20.6 schema 前,先 `cat /Users/red/Desktop/4.22最新skill/output/team_battle_final.json` 对照字段**。权威必填:
  - component = `[name, w, h, variant_property, variants]`(**w/h/variant_property 必须有,否则 Figma 无固定画板 → 错位**)
  - variant = `[name, is_default, layers]`
  - layer = `[type, name, x, y, w, h, fill, element_class, constraints, corner_radius]`(element_class: static/dynamic)
  - INSTANCE = `[type, name, component_name, variant, x, y, w, h, constraints, overrides]`,且 **INSTANCE w/h == 引用的 component w/h**(不缩放)
  - 主路径无脚本兜底,字段必须手写齐全。详见 `4.22最新skill/06_selfcheck.md` 第十二层。

**特别针对"推翻用户指示 / 重大修正"(2026-05-18 加)**:
- ❌ **Team Battle 排名标记事故**:用户最初说"排名金银铜+数字 4 Variant",我看视频高清帧**把右侧蓝色盾牌分误当成左侧排名标记**,据此宣布"⚠️ 重大修正:视频里没金银铜,排名全是统一蓝徽章",错误推翻用户正确指示。用户纠正"金银铜是左侧排名,蓝色是右侧盾牌分"后,像素抽样证实排名1偏金/排名2偏银 —— 用户一直是对的。
- **铁律**:要"推翻用户指示 / 宣布重大修正 / 跟用户说的不符"前,**必须先精确定位是哪个区域**(像素坐标 bbox + 抽样主色),确认我看的就是用户说的那个元素,再下结论。粗看一眼就喊"重大修正"= 高风险打脸 + 误导用户改对的东西。用户是产品方,对自己界面的认知优先级 > 我对一帧的粗读。

**特别针对 Variant 方案 / pattern 命中(2026-05-15 加)**:
给任何 component 的 Variant 方案前,**必须先 grep SKILL 关键词**(`component 名 / 奖励物 / 角标 / 异构 / 占位 / 程序换图 / 数据驱动 / 例外` 等),查 4.22 SKILL `06_S6_pattern命中.md` + `07d_S7_嵌套占位背景.md` + `00d_Variant抽取与修复.md` 有没有该类型现成规则。**这些铁律比我的"视觉直觉"权威**,违反会被同事评审挑出。
