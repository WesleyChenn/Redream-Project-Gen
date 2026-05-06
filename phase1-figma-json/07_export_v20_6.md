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

## 已知简化 (v1)

阶段二脚本目前不做的事 (后续可加):

1. **不做嵌套 Component 抽取**
   外层 Component 优先,内层不再独立抽
   (如"排行榜行"内部的"头像框"不会再被抽成独立 Component)

2. **Variant 名只给占位**
   `常态` / `变体_2` / `变体_3` ... 需人工/Claude 二次润色

3. **数据驱动判断只看 TEXT.content + 视觉属性**
   暂未处理图片 url / image_ref 字段

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

## 脚本位置参考

```
/Users/red/Desktop/component_extractor/extract_components.py
```

可选参数:
- `--min-instances N` 改最少复用次数 (默认 2)
