# S7 · 阶段二导出（v20.6 schema 转换）

> ⚠️ **覆盖 S6 末尾的"交付 JSON"指令**
>
> S6 自检通过后,**不要直接把扁平 JSON 交付给用户**。
> 必须先跑阶段二脚本把扁平 JSON 转成 v20.6 schema (含 `components` + `INSTANCE`),
> 把转换后的 `final.json` 交付给用户用于粘贴到 Figma 插件。

---

## 何时进入这一步

S6 自检全 ✅ → 本步骤 → 交付

---

## 为什么需要这一步

S0~S6 阶段一只生成**扁平 JSON**(所有重复结构展开,17 个排行榜行就是 17 个独立 FRAME)。
Figma 插件 v20.6+ 需要的是**带 components + INSTANCE 的 schema**,才能在画布同时产出:
- 主屏 (界面_xxx / 浮层_xxx)
- 右侧 `📦_组件库` Frame (含所有 Component Set)

阶段二脚本 `extract_components.py` 用算法把扁平 JSON 自动转成插件需要的格式。

---

## 标准动作

### 1. 写出阶段一的扁平 JSON

把 S6 自检通过的扁平 JSON 写到 `flat_scene.json`。**这一步不变**,该写什么字段还写什么字段。

### 2. 跑阶段二脚本

```bash
python3 /Users/red/Desktop/component_extractor/extract_components.py \
    flat_scene.json \
    final_scene.json
```

脚本输出会报告:
- 抽取了几个 Component
- 每个 Component 几个 Variant
- 每个 Variant 的实例数

### 3. 检查脚本输出

#### ✅ 正常情况

```
✅ 抽取了 3 个 Component:
  • 排行榜行  (997×203, 17 实例 → 5 Variant: 常态, 变体2, 变体3, 变体4, 变体5)
  • 活动按钮  (215×175, 8 实例 → 1 Variant: 常态)
  • 导航项    (215×170, 5 实例 → 2 Variant: 常态, 变体2)
```

#### ⚠️ 没有 Component

```
⚠️ 没有发现可抽取的 Component
```

如果出现这种情况,通常是阶段一在生成扁平 JSON 时**公共节点命名漂移**了
(比如 17 个排行榜行内部的"底板"分别叫 `底板_行` / `底板_排行` / `底板_第N行`)。

回到 S3 检查命名一致性:**结构相同的 FRAME,内部子节点必须严格同名**。
修正后重跑 S6 → S7。

#### ⚠️ Variant 名是占位的 (变体N)

脚本只能给 Variant 占位名。**这一步可以人工/Claude 重命名**:
- 看 `final_scene.json` 里 `components[].variants[]` 数组
- 对每个 `变体N`,看其 layers 与 `常态` 的视觉差异 (颜色/显隐/形状)
- 改成语义名 (`已完成` / `当前用户` / `带徽章` 等)

INSTANCE 节点引用同步改:
- 找 `screens.layers` 里所有 `variant: "变体N"` 的 INSTANCE
- 改成对应的语义名

#### 🔴 Variant 命名铁律 (v20.6+, 与 Figma combineAsVariants 行为对齐)

**Variant 名字禁止包含下划线 `_`。**

**原因**: Figma `combineAsVariants` 在解析 `<ComponentName>/<VariantValue>` 命名时,如果
VariantValue 含下划线,会误把一组"对称下划线"的 Variant 互相归并/吞掉。
具体表现: 5 个 tile 在 Component Set 里都画出来了,但右侧"状态"下拉只显示 3 个,
设计师没法在 INSTANCE 上完整切换状态。

**❌ 错误命名**:
- `有头衔_无道具`
- `无头衔_有道具`
- `有头衔_有道具`
- `状态_选中` / `状态_未选中` (任何含下划线的都不行)

**✅ 正确命名**:
- `有头衔无道具`
- `无头衔有道具`
- `有头衔有道具`
- `选中` / `未选中` (单词)
- `已完成` / `可领取` / `进行中` / `当前用户` (短语)
- `变体2` / `变体3` (占位名,不带下划线)

**应用范围**: 阶段二脚本输出的 `components[].variants[].name` 和
`screens.layers[].variant` 引用,**两边都不能含下划线**。

**自检**: 交付 final_scene.json 前,grep 检查:

```bash
python3 -c "
import json
d = json.load(open('final_scene.json'))
for c in d.get('components', []):
    for v in c['variants']:
        if '_' in v['name']:
            print(f'❌ Variant 名含下划线: {c[\"name\"]} → {v[\"name\"]}')
"
```

任何 `_` 都报红 → 改名 → 重检。

### 4. 交付

把 `final_scene.json` 交付给用户:

```
✅ 转换完成

📄 阶段一扁平 JSON: flat_scene.json (XX KB)
📄 阶段二最终 JSON: final_scene.json (XX KB) ← 粘到 Figma 插件 ▶生成

抽取出的 Component:
  • 排行榜行: 5 Variant (常态/带徽章/带道具/带徽章和道具/当前用户)
  • 活动按钮: 1 Variant (常态)
  • 导航项: 2 Variant (常态/选中)

下一步: 把 final_scene.json 全文粘贴到 Figma 插件 'Elsa UI 生成器' 的 ▶生成 tab
        画布上会同时出现主屏 + 右侧 📦_组件库 Frame
```

---

## 算法能力 (v20.7+)

### ✅ 支持 — 二层嵌套抽取 (Multi-pass)

阶段二脚本会做以下 4 步:

```
Pass 1: 收集所有 FRAME 候选 + 评分 + 分类
        - cross_cutting ≥ 2 → promoted (内层提级,跨多个外层共享)
        - cross_cutting = 1 → embedded (外层 Component 自身)

Pass 2: 抽 promoted 内层 Component 先
        - 在 mutable_scene 里替换为 INSTANCE

Pass 3: 抽 embedded 外层 Component 后
        - 模板从 mutable_scene 取 (此时模板内部含已替换的 INSTANCE 引用 ✓)

Pass 4: 输出 components 数组按 promoted → embedded 排序
        (内层在前,满足 Figma 插件依赖序: 外层引用内层时,内层已注册)
```

**实例**: Shop 屏含 3 张大卡片,每张内部有 4 道具 + 3 限时道具 + 价格按钮 + Popular 角标
→ 抽出 5 个 Component: 4 个 promoted (道具数量徽章/限时道具/按钮_价格/角标_Popular) + 1 个 embedded (金币购买卡片)
→ 金币购买卡片的 Variant.layers 内部正确含 7 个 INSTANCE 引用

### ✅ 支持 — 视觉差异生成 Variant

阶段二自动按视觉签名(visible / fill / corner_radius / opacity 等)分 Variant,
TEXT.content 不算视觉差异(归数据驱动)。

**实例**: 4 个道具图标(宝箱/大炮/锤子/小丑帽)如果 fill 不同,会被分成 4 个 Variant。

### ⚠️ 局限 — Variant 名只给占位

脚本输出 `常态` / `变体2` / `变体3` 等占位名,**必须由 Claude/人工重命名**为语义名:
- 看 `final_scene.json` 里 `components[].variants[]` 的 layers 视觉差异
- 改成语义名 (`已完成` / `当前用户` / `宝箱` / `大炮` / `TNT` 等)
- INSTANCE 节点引用同步更新 `variant` 字段

### ⚠️ 局限 — 数据驱动判断颗粒度

只看 TEXT.content + 视觉属性二分。如果同 Component 实例的图片 url / image_ref 差异
是"语义状态"(应为 Variant)而非"数据驱动",脚本会误判为同 Variant。
解决: 在 Stage 1 生成 JSON 时显式标 `visible` 或 `fill` 来表达状态多态。

### ⚠️ 局限 — 暂不支持三层及以上嵌套

promoted 候选自身内部如果还有可抽 FRAME (三层嵌套),当前脚本不会再递归抽。
通常游戏 UI 不超过两层,够用。三层场景需手工拆。

---

## 自检清单

- [ ] 跑完脚本后 `final_scene.json` 存在
- [ ] 脚本报告至少抽取了 1 个 Component (无 Component 是异常,回 S3 排查命名)
- [ ] 占位 Variant 名 (变体_N) 已改为语义名
- [ ] 交付时同时给 flat_scene.json (供调试) 和 final_scene.json (用于粘贴)

---

## 常见错误

- ❌ S6 通过就直接给用户 flat JSON → 设计师粘到插件出来的是扁平结构,没有 Component Set
- ❌ 跑完脚本不审 Variant 名就交付 → 用户看到 "变体_2" 不知道是什么状态
- ❌ flat_scene.json 里公共节点命名漂移 → 脚本抽不出 Component,回 S3 查命名

---

## 5. S7 后处理:漏网 FRAME 检测 + 修复(v20.7.x+,RoyalPass 教训)

**对应 00_core_rules.md 末尾"S7 后必须 100% 嵌套化"铁律,必读。**

### 5.1 为什么需要后处理

`extract_components.py` 算法只识别 N 种**主流**"显隐组合"(常态 / 宝箱型 等),**边缘组合会留作 FRAME**。
例如 RoyalPass 视频里的行 19/20:
- 行 19:左对勾 + 右对勾(双侧对勾)
- 行 20:左对勾 + 右锁(对勾锁混合)

这两种组合不在算法识别的 2 种主流形态里,所以没被替换为 INSTANCE,留作扁平 FRAME 在主屏。
设计师粘到 Figma 后看到"前 2 行扁平 + 后 6 行引用"的奇怪混合结构,要回头来问。

### 5.2 漏网 FRAME 检测脚本

```bash
python3 -c "
import json
d = json.load(open('final_scene.json'))

# 收集主屏 list_inner.children 类型分布
def find_lists(n, results=[]):
    if isinstance(n, dict):
        # 启发式: VERTICAL 容器 + ≥4 children + 子里既有 INSTANCE 又有 FRAME → 可能是漏网混合
        if n.get('layoutMode')=='VERTICAL' and len(n.get('children',[]))>=4:
            ts = [c.get('type') for c in n['children']]
            if 'INSTANCE' in ts and 'FRAME' in ts:
                results.append((n.get('name','?'), ts))
        for k in ('children','layers'):
            if k in n: find_lists(n[k], results)
    elif isinstance(n, list):
        for x in n: find_lists(x, results)
    return results

mixed = find_lists(d['screens'])
if mixed:
    print('⚠️ 发现漏网混合容器:')
    for name, ts in mixed:
        print(f'  {name}: {ts}')
    print('→ 需要把 FRAME 类型项抽成新 Variant 转 INSTANCE')
else:
    print('✅ 所有列表/网格容器内全部 INSTANCE,无漏网平铺')
"
```

### 5.3 修复路径(铁律)

**对每个漏网 FRAME**:

1. 抽出 FRAME 的内部 children 作为新 Variant 模板
2. 添加到对应 Component 的 variants 数组里(语义命名,如"对勾型"/"对勾锁型")
3. 把主屏的 FRAME 替换为 INSTANCE 引用新 Variant
4. 验证:对应 Component variants ≥2 + 视觉签名唯一(过 第 12 层自检)

**严禁**:
- ❌ 删除 Component 让 FRAME"合规"(违反用户原始设计意图,引发 combineAsVariants 连锁失败)
- ❌ 不抽 Variant,直接保留 FRAME(设计师粘到 Figma 看到混合形态)

### 5.4 修复参考实现

```python
# 把行 N 的 FRAME 转成 INSTANCE,引用新 Variant
import copy

def frame_to_variant_layers(row_frame):
    """把 FRAME 的 children 转成 Variant.layers,过滤 visible=false 节点"""
    out = []
    for ch in row_frame.get('children', []):
        if ch.get('visible') is False: continue
        ch_copy = copy.deepcopy(ch)
        def filter_invisible(n):
            if isinstance(n, dict):
                kids = n.get('children')
                if kids is not None:
                    n['children'] = [c for c in kids if c.get('visible') is not False]
                    for k in n['children']: filter_invisible(k)
            elif isinstance(n, list):
                for x in n: filter_invisible(x)
        filter_invisible(ch_copy)
        out.append(ch_copy)
    return out

# 用法
new_variant = {
    "name": "对勾型",  # 语义名,不含下划线
    "is_default": False,
    "layers": frame_to_variant_layers(row19_frame)
}
target_component['variants'].append(new_variant)

# 替换主屏的 FRAME 为 INSTANCE
list_inner['children'][i] = {
    "type": "INSTANCE",
    "name": row19_frame['name'],
    "component_name": target_component['name'],
    "variant": "对勾型",
    "x": row19_frame['x'], "y": row19_frame['y'],
    "w": row19_frame['w'], "h": row19_frame['h'],
    "constraints": {"horizontal":"LEFT","vertical":"TOP"},
}
```

### 5.5 完整后处理流程

```
S7 脚本输出 final_scene.json
    ↓
跑漏网 FRAME 检测脚本(5.2)
    ↓
有漏网 → 5.3 修复 → 跑 06 第 12 层自检(变体≥2 + 签名唯一 + 引用合法)
    ↓
全 ✅ → 重命名 Variant 占位为语义名 → 交付
```

### 5.6 严禁的错误修复

历史教训(RoyalPass 项目):

| 时机 | 错误操作 | 正确做法 | 后果 |
|---|---|---|---|
| 看到 1 Variant Component | 删 Component 内嵌 FRAME | 加 dummy 第 2 Variant fill 不同 | 用户看不到组件库里有进度条,反馈"你怎么把进度条删了" |
| 看到 Variant 视觉签名相同 | 删其中一个 Variant | "显隐"改 INSTANCE.visible=false / 其他加视觉差异 | 后续连锁失败,组件库 / 预览 多次"消失" |
| 看到漏网 FRAME 混合形态 | 删整个 Component 让 FRAME 合规 | 加 Variant 转 INSTANCE | 用户原始设计被擅自改变 |

**元铁律**: 任何 Component 删除操作前**必须先问用户**。Component 列表是用户的设计决策,不是工具限制下我可以决定的。

---

## 脚本位置参考

```
/Users/red/Desktop/component_extractor/extract_components.py
```

可选参数:
- `--min-instances N` 改最少复用次数 (默认 2)
