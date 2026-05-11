# S6 · 自检清单【强制，有 ❌ 必须修正后才能交付】

> 每次生成 JSON 后必须逐项执行，不能只做格式浅检查。

---

## 【第一层：骨架完整性】

```
✅/❌ 【仅录屏】S1 全帧扫描完成（含触摸点识别与翻页类型判断）
✅/❌ 【仅录屏】S2 滚动菜单识别完成（已区分固定区/滚动区/viewport）
✅/❌ S3 骨架表格已输出（含组件库匹配标注）
✅/❌ 骨架无重叠，所有大区 h 加总 = 2400（算术闭环）
✅/❌ 贴底区域从下往上计算 y，未从上往下叠加估算
✅/❌ 所有 h/w 已量测后 × scale（非估算值）
```

## 【第二层：尺寸精度】

```
✅/❌ 所有 w/h/x/y 从截图量测后 × scale，非直接写量测值
✅/❌ 同组控件尺寸一致；对称布局两个按钮 w 相同
✅/❌ 允许误差 ±5%，超出说明量测有误
✅/❌ screens 尺寸用 "w"/"h"（非 width/height）
✅/❌ 录屏帧：H 已排除播放器 UI
✅/❌ 异构列表：每种行类型已分别量测 h
```

## 【第三层：组件合规性】

```
✅/❌ 开始前已加载组件库 JSON，S3 逐一比对后才标注匹配结论
✅/❌ 识别到库组件 → component_ref，未退化为手搓
✅/❌ component_ref 使用前已在 S3 确认组件内部 constraints 为 SCALE/SCALE（可缩放）
✅/❌ 组件内部 constraints 非 SCALE 时，已改为手搓或要求用户先更新组件库
✅/❌ component_ref 输出 w/h = 截图量测 × scale（不使用组件库原始尺寸）
✅/❌ 导航栏 item 数量已通过像素扫描逐个确认，未用「屏幕宽÷估算宽」推断
✅/❌ 骨架表中已备注导航每项名称（项1=xxx, 项2=xxx...），与 JSON 中 导航_项N 一一对应
✅/❌ 导航按钮：导航_项N 命名 + overrides 写入实际文字
✅/❌ 导航双态：当前页用 _选中，其他用 _未选中，未使用旧组件
✅/❌ component_ref 是独立 key
✅/❌ component_ref 未写 layoutSizingHorizontal/Vertical
✅/❌ overrides 字段名与组件内文字节点名 100% 匹配
✅/❌ RECTANGLE 仅用于无组件的纯图片/装饰色块
✅/❌ 角标均已找到父本,并按 v20 按钮分组规则归属：
      - 父本是按钮(按钮_xxx FRAME 或按钮类 component_ref)→ 角标作为按钮 children
      - 非按钮 component_ref(如 Tab 状态切换)+ 装饰 → 统一用 按钮_xxx FRAME 包装(做法 B)
✅/❌ 叠加结构父容器 h/w = 主体组件 h/w（不含附加元素高度）
```

## 【第四层：按钮与底板分离（v20）】

```
✅/❌ 手搓按钮外壳命名为 按钮_xxx FRAME（不是 底板_xxx FRAME, 不是 RECT）
✅/❌ 按钮内层底板为 底板_xxx RECTANGLE（不加"形状"后缀,父节点是 按钮_xxx FRAME）
✅/❌ 外层容器底板（卡片/弹窗）为 底板_xxx RECTANGLE,父节点非按钮（组_/容器_/弹窗_）
✅/❌ 装按钮的容器命名为 组_xxx / 容器_xxx / 弹窗_xxx（禁止用 底板_ 开头）
✅/❌ 组件库按钮（圆形按钮_/方形按钮_/椭圆按钮_）通过 component_ref 引用,未走 按钮_ 前缀
✅/❌ 按钮内子元素（文字/图标/装饰）全部作为按钮 FRAME 的 children
✅/❌ 装饰附件（角标/徽章/底标/倒计时）与按钮兄弟平级错误,必须在按钮 children 内
✅/❌ component_ref + 装饰场景用做法 B（父按钮 FRAME 包装 component_ref + 装饰）
✅/❌ 内容区_ FRAME 的 w/h 与按钮底板完全一致（如使用）
✅/❌ 无"一层底"（FRAME 同时有 fill 和 children）
✅/❌ layoutPositioning: ABSOLUTE 仅在 AL 容器内
✅/❌ 无嵌套按钮：任何 按钮_xxx FRAME 的 children 递归里不再出现 按钮_ 开头的 FRAME
✅/❌ 手搓替换 component_ref 后,所有 底板_xxx 仍为 RECTANGLE,无 底板_xxx FRAME
✅/❌ 所有 按钮_xxx FRAME 尺寸 = 主体尺寸(不为装饰溢出而扩大),同组按钮 FRAME 尺寸统一便于对齐
✅/❌ 装饰（角标/徽章/底标）允许视觉溢出按钮 FRAME(负坐标或 y+h 超出按钮h 都 OK),溢出区域不触发点击是可接受的
```

## 【第四点五层：进度条专项（v20.4）】

```
✅/❌ 三层结构: 组_进度_XXX (FRAME) 包含 底板_XXX (RECT) + 进度条_XXX (RECT)
✅/❌ 三层 XXX 完全一致(含方向后缀): 组_进度_xxx_tb + 底板_xxx_tb + 进度条_xxx_tb
✅/❌ 🔴 "进度"二字只出现在外层包装 FRAME (组_进度_xxx),内部底板/进度条 XXX 保持简洁
       - ✅ 组_进度_活动 + 底板_活动 + 进度条_活动
       - ❌ 组_进度_活动进度 + 底板_活动进度 + 进度条_活动进度 (内部冗余)
✅/❌ 包装 FRAME (组_进度_XXX) w/h = 底板 w/h(包装层和底板一样大)
✅/❌ 无 component_ref 引用 进度条_短 / 进度条_宽（一律手搓双层 RECT）
✅/❌ 双层都是 RECTANGLE,不是 FRAME 包装
✅/❌ children 数组里 进度条_XXX 的 index > 底板_XXX 的 index（Z 序高,进度条覆盖底板）
✅/❌ 同屏内进度条 XXX 唯一,不与按钮内层底板的 XXX 重名
✅/❌ 节点名后缀仅编码 direction:
       - 不加后缀: horizontal_lr 水平左→右(默认,99% 场景)
       - _rl/_bt/_tb 表示 horizontal_rl / vertical_bt / vertical_tb
       - 环形暂不支持
       - **不写 _p<数字> 后缀**(百分比由引擎运行时控制)
✅/❌ JSON 中**没有** percentage / direction 字段(命名编码方案,字段冗余)
✅/❌ 🔴 进度条 RECT **比底板 RECT 小**(内缩,不是同尺寸):
       - 大尺寸(w≥200, h≥80): 横纵各内缩 10px
       - 中尺寸(100≤w<200, 50≤h<80): 横 8px / 纵 5px
       - 小尺寸(w<100, h<50): 横 5px / 纵 3-5px
✅/❌ 🔴 进度条中心 = 底板中心(中心点重合验证):
       进度条 x + 进度条 w/2 == 底板 x + 底板 w/2
       进度条 y + 进度条 h/2 == 底板 y + 底板 h/2
✅/❌ 进度条 RECT 视觉**永远画 100% 满的样子**(不画当前进度,运行时由引擎按玩家数据切割)
✅/❌ 文本/图标作为**外层容器**的兄弟元素,不放进 组_进度_XXX 包装内
✅/❌ 外层容器命名：不可点击用 组_xxx,可点击用 按钮_xxx
✅/❌ 两侧 icon 作为兄弟元素（与 组_进度_XXX 平级,不嵌入进度条内）
✅/❌ 两侧 icon 优先用 component_ref（如 图标_金币、图标_锁）,匹配不到才手搓
```

## 【第五层：布局与约束】

```
✅/❌ 所有 FRAME 设置了 layoutMode
✅/❌ primaryAxisSizingMode / counterAxisSizingMode 只用 FIXED / AUTO
✅/❌ 所有 AL FRAME 有 primaryAxisAlignItems
✅/❌ constraints 只在屏幕顶层直接子节点 和 NONE 父容器子节点
✅/❌ VERTICAL 容器内底板 layoutPositioning: ABSOLUTE
✅/❌ VERTICAL 容器内子 FRAME 有 layoutSizingHorizontal: FILL
✅/❌ 弹性缝隙 / SPACE_BETWEEN 使用正确
✅/❌ 无 SPACE_AROUND；无 STRETCH
✅/❌ children 从底到顶排序
```

## 【第六层：Prototype 连线】

```
✅/❌ 导航_页面切换：N×(N-1) 条 slide 连线（全量，每个屏幕的每个非激活Tab都已连线）
✅/❌ 只写视频中实际出现的屏幕，未出现的屏幕不写连线
✅/❌ 导航_状态切换：未生成任何 flow
✅/❌ from_node 名称与 JSON 节点 name 100% 一致
✅/❌ flow 的 from/to 屏幕名在 screens 中存在
✅/❌ 全屏跳转 dissolve，浮层 overlay，浮层关闭 CLOSE
✅/❌ 屏幕类型正确：全屏替换用 界面_，弹窗覆盖用 浮层_
✅/❌ 同一屏幕内无重名节点
✅/❌ 零幻觉：未生成不存在的屏幕或连线
```

## 【第七层：Overflow 滚动】

```
✅/❌ 父容器：overflow + clip_content: true + primaryAxisSizingMode: FIXED
✅/❌ 子容器：primaryAxisSizingMode: AUTO，是父容器直接 child
✅/❌ 子容器 h > 父容器 h
✅/❌ 子容器 w 已显式指定
✅/❌ 滚动未写进 flow
```

## 【第八层：命名合规】

```
✅/❌ 所有 name 前缀在枚举白名单内
✅/❌ 无非白名单前缀（顶部_/底部_/主体_/区域_/面板_/切图_ 等）
✅/❌ 无残留 切图_底板_ 前缀（v18 老命名）
✅/❌ 无残留 底板_xxx 形状后缀（v19 老命名,v20 不需要）
✅/❌ 无"底板_xxx FRAME"当按钮用（v19 老命名,v20 改为 按钮_xxx）
✅/❌ 浮层_ 屏幕 layers[0] = 遮罩_浮层背景 RECTANGLE 1080×2400
✅/❌ 界面_ 屏幕有全屏背景时 layers[0] = 背景_xxx RECTANGLE 1080×2400
✅/❌ 背景/遮罩未被放进中间弹性区容器内部
✅/❌ 导航按钮统一 导航_项N（每项独立按钮,不整栏合并）
✅/❌ TEXT 无多余 w
✅/❌ 无 stroke 属性
✅/❌ 手搓节点 fill 全部省略（无 hex、无 transparent）
✅/❌ component_ref 节点未被错误添加 fill 字段
```

## 【第九层：复用结构内部命名一致性（v20.6 阶段二前提）】

> 对应 S4 规则 11.5。此层失败 → S7 阶段二脚本抽不出 Component。

```
✅/❌ 同结构多实例 FRAME(列表行/网格项/重复按钮组)内部子节点命名 100% 一致
✅/❌ 实例间差异只出现在视觉属性(fill/corner_radius/opacity/visible),不出现在 name
✅/❌ "排行榜行_1"内部叫"底板_行","排行榜行_2"内部不叫"底板_排行行"
✅/❌ "活动按钮_奖杯"内部叫"图标_装饰","活动按钮_盾牌"内部也叫"图标_装饰"(不是"图标_盾牌图")
✅/❌ 状态多态实例(如"列表项_当前用户")只在 fill/visible 上和默认实例不同,内部命名仍一致
```

**自检方法**: 列出每组同结构 FRAME,把每个实例的 children name 对照一遍,逐字段确认完全相同。

## 【第十层：Variant 命名合规（v20.6+ 阶段二导出后必检）】

> 仅在 S7 跑完阶段二脚本、拿到 final_scene.json 后执行。
> 对应 S7 文档"Variant 命名铁律"。此层失败 → Figma combineAsVariants 会
> 把"对称下划线"的 Variant 互相归并/吞掉,设计师在 INSTANCE 上没法切换。

```
✅/❌ 所有 components[].variants[].name 不含下划线 _
✅/❌ 所有 screens.layers[].variant 引用不含下划线 _
✅/❌ default Variant 标 is_default: true,且名字常用 "常态"
✅/❌ Variant 名字语义清晰(已完成/当前用户/带徽章 等),不留 "变体2/3/4" 占位
```

**自检方法**:

```bash
python3 -c "
import json
d = json.load(open('final_scene.json'))
issues = []
for c in d.get('components', []):
    for v in c['variants']:
        if '_' in v['name']:
            issues.append(f'Variant 名含下划线: {c[\"name\"]} → {v[\"name\"]}')
def walk(n):
    if n.get('type')=='INSTANCE' and '_' in n.get('variant',''):
        issues.append(f'INSTANCE 引用 variant 含下划线: {n.get(\"name\")} → {n[\"variant\"]}')
    for ch in (n.get('children') or n.get('layers') or []): walk(ch)
for s in d.get('screens', []):
    for L in s.get('layers', []): walk(L)
print('❌ 发现' if issues else '✅ 全部合规')
for i in issues: print(' ', i)
"
```

任何 `_` 报红 → 改名(去下划线) → 重跑自检。

## 【第十层半：Variant 内部建模合规（v20.7+ 阶段二导出后必检）】

> 对应 S0 文档"Variant 内部建模铁律"。此层失败 → 引擎渲染丢数据或时间线污染。

```
✅/❌ 每个 Variant.layers 内不含 visible=false 节点(应被 _filter_invisible 物理删除)
✅/❌ 子 CCB 整个隐藏的场景,wrapper 的 visible / opacity 已传到父 Variant 内的 INSTANCE 节点
✅/❌ 同 Variant 内多个实例的 TEXT.content / component_ref.overrides 差异,
       已作为每个 INSTANCE 节点的 overrides 字段输出(不能只保留模板的内容)
✅/❌ INSTANCE.overrides 的 key 都对应到 Variant.layers 里实际存在的子节点 name
       (不能 override 不存在的字段)
```

**自检方法**:

```bash
python3 -c "
import json
d = json.load(open('final_scene.json'))
issues = []

# 检查 1: Variant.layers 不含 visible=false
def walk_check_visible(layers, ctx):
    for L in layers or []:
        if L.get('visible') is False:
            issues.append(f'{ctx} 含 visible=false 节点: {L.get(\"name\")}')
        for k in ('children','layers'):
            if k in L: walk_check_visible(L[k], ctx + '/' + L.get('name','?'))
for c in d.get('components',[]):
    for v in c.get('variants',[]):
        walk_check_visible(v.get('layers'), f'{c[\"name\"]}/{v[\"name\"]}')

# 检查 2: 屏幕里同 component_name 的 INSTANCE 是否有数据 override(非模板实例必须有)
by_comp = {}
def walk(n):
    if n.get('type')=='INSTANCE':
        cn = n.get('component_name','')
        by_comp.setdefault(cn,[]).append(n)
    for c in (n.get('children') or n.get('layers') or []): walk(c)
for s in d.get('screens',[]):
    for L in s.get('layers',[]): walk(L)
for cn, insts in by_comp.items():
    if len(insts) <= 1: continue   # 单实例无须 override
    n_with_override = sum(1 for i in insts if i.get('overrides'))
    if n_with_override == 0:
        issues.append(f'{cn} 有 {len(insts)} 个 INSTANCE 但全部无 overrides — 可能数据丢失')

print('✅ 全部合规' if not issues else '❌ ' + str(len(issues)) + ' 项问题')
for i in issues[:10]: print(' ', i)
"
```

任何 ❌ 必须修后重跑。

## 【第十一层：INSTANCE 尺寸同步合规（v20.7+ 阶段二导出后必检）】

> 仅在 S7 跑完阶段二脚本、拿到 final_scene.json 后执行。
> 对应 S0 文档"INSTANCE 尺寸同步铁律"。此层失败 → 引擎生成的 .red 文件父 CCNode 与子 CCB 尺寸不匹配,**视觉错位**。

```
✅/❌ 同一 component_name 的所有 INSTANCE 的 w/h 完全一致
✅/❌ 每个 INSTANCE 的 w/h 等于对应 components[].w/h
✅/❌ 不一致时,要求设计师选中 INSTANCE → ⌥⌘Y(macOS)/Alt+Ctrl+Y(Windows) Push 到主版后重新导出
```

**自检方法**:

```bash
python3 -c "
import json
d = json.load(open('final_scene.json'))
comp_size = {c['name']:(c['w'],c['h']) for c in d.get('components',[])}
by_comp = {}
def walk(n):
    if n.get('type')=='INSTANCE':
        cn = n.get('component_name','')
        by_comp.setdefault(cn,[]).append((n.get('name'),n.get('w'),n.get('h')))
    for ch in (n.get('children') or n.get('layers') or []): walk(ch)
for s in d.get('screens',[]):
    for L in s.get('layers',[]): walk(L)
issues=[]
for cn, insts in by_comp.items():
    sizes = set((w,h) for _,w,h in insts)
    if len(sizes)>1:
        issues.append(f'❌ {cn} 的 INSTANCE 尺寸不一致: {sizes}')
    cw,ch = comp_size.get(cn,(None,None))
    for nm,w,h in insts:
        if (cw,ch)!=(None,None) and (w,h)!=(cw,ch):
            issues.append(f'❌ {cn}/{nm} ({w}x{h}) 与 Component 本体 ({cw}x{ch}) 不一致 → Push 主版')
print('✅ 全部一致' if not issues else '\n'.join(issues))
"
```

**不一致时的处理流程**(三步):

1. 识别问题 INSTANCE: 脚本输出哪些 component_name 的 INSTANCE 尺寸不一致 / 与本体不一致
2. **要求设计师在 Figma 里**: 选中**任意一个目标尺寸**的 INSTANCE → 右键 `Push changes to main component`(或 `⌥⌘Y`) → 所有同 component 的 INSTANCE 自动同步到新尺寸
3. 重新导出 scene.json → 重跑阶段二脚本 → 重跑本层自检直到全部 ✅

⚠️ Claude / 插件 / extractor **不自动改尺寸**:引擎按数据如实生成,猜测设计意图风险大。
   这是工作流铁律,设计师必须在 Figma 端手动 Push,不存在自动修复。

## 【第十二层:S7 后嵌套化 + Component 修复合规(v20.7.x+,RoyalPass 教训)】

> 仅在 S7 跑完阶段二脚本、拿到 final_scene.json 后执行。
> 对应 `00_core_rules.md` 末尾两节:"S7 后必须 100% 嵌套化" + "Component 修复铁律"。
> **此层失败时绝不能交付** — 设计师粘进 Figma 后会看到组件库不全 / 主屏前几行扁平后几行引用 的奇怪混合形态,
> 触发后续连锁问题(combineAsVariants 失败 → registry 不全 → 预览 Frame 不创建)。

```
✅/❌ 主屏 list_inner / 网格行 / 卡片容器 内**没有"漏网平铺 FRAME"**
       (即所有跟某个 Component 结构指纹相同的 FRAME 都已转为 INSTANCE)
✅/❌ 每个 Component 至少 2 个 Variant(< 2 会让 Figma combineAsVariants 失败)
✅/❌ 每个 Component 内的 Variants 视觉签名 hash 唯一(相同会让 combineAsVariants 失败)
✅/❌ 所有 INSTANCE.component_name 都能在 components[] 数组里找到对应 Component
✅/❌ components[] 顺序: 子 Component 在前,引用它的外层 Component 在后
       (避免 buildV20_6_ComponentSets 处理外层时子还没注册)
✅/❌ 修 Component 时未走"删 Component 降级 FRAME"路径(违反用户原始设计意图)
✅/❌ 用户最初定的 Component 列表数量没变(气泡/内容/数量徽章/状态徽章/进度条/网格行 一个不少)
```

**自检脚本**(对应 00_core_rules.md "Component 交付前自检脚本"):

```bash
python3 -c "
import json, hashlib
d = json.load(open('final_scene.json'))

issues = []

# 1. Component 数量 ≥ 2 + 视觉签名唯一
def variant_signature(layers):
    parts = []
    def collect(L):
        for n in L or []:
            if isinstance(n, dict):
                parts.append(f'{n.get(\"type\")}|{n.get(\"name\")}|{n.get(\"fill\",\"\")}|{n.get(\"visible\",True)}')
                if n.get('type')=='INSTANCE':
                    parts.append(f'INST|{n.get(\"component_name\")}|{n.get(\"variant\")}')
                for k in ('children','layers'):
                    if k in n: collect(n[k])
    collect(layers)
    return hashlib.md5(''.join(parts).encode()).hexdigest()[:8]

for c in d.get('components', []):
    if len(c['variants']) < 2:
        issues.append(f'{c[\"name\"]} 只有 {len(c[\"variants\"])} Variant — combineAsVariants 会失败')
    sigs = {}
    for v in c['variants']:
        sig = variant_signature(v.get('layers'))
        if sig in sigs:
            issues.append(f'{c[\"name\"]} 的 Variant \"{v[\"name\"]}\" 跟 \"{sigs[sig]}\" 视觉签名相同 ({sig})')
        sigs[sig] = v['name']

# 2. INSTANCE 引用合法性
all_comp_names = {c['name'] for c in d.get('components', [])}
def walk(n, ctx):
    if isinstance(n, dict):
        if n.get('type')=='INSTANCE':
            cn = n.get('component_name','')
            if cn not in all_comp_names:
                issues.append(f'{ctx}/{n.get(\"name\")} → component_name \"{cn}\" 不在 components[] 里')
        for k in ('children','layers'):
            if k in n: walk(n[k], ctx+'/'+(n.get('name','?')))
    elif isinstance(n, list):
        for x in n: walk(x, ctx)
walk(d.get('screens'), 'screen')
for c in d.get('components', []):
    for v in c['variants']: walk(v.get('layers'), f'{c[\"name\"]}/{v[\"name\"]}')

# 3. components[] 顺序: 子在前,外层在后
seen = set()
for c in d.get('components', []):
    walk_inst = []
    def collect_refs(layers):
        for n in layers or []:
            if isinstance(n, dict):
                if n.get('type')=='INSTANCE':
                    walk_inst.append(n.get('component_name'))
                for k in ('children','layers'):
                    if k in n: collect_refs(n[k])
    for v in c['variants']: collect_refs(v.get('layers'))
    for ref in walk_inst:
        if ref not in seen and ref in all_comp_names:
            issues.append(f'components[] 顺序错: {c[\"name\"]} 引用了还未注册的 {ref}')
    seen.add(c['name'])

print('✅ 第12层全部合规' if not issues else f'❌ {len(issues)} 项问题:')
for i in issues[:20]: print(f'  {i}')
"
```

**修复路径(任何 ❌ 都按此走)**:

| 失败项 | 错误修复 | 正确修复 |
|---|---|---|
| 漏网平铺 FRAME | 删 Component 让 FRAME 合规 | 加 Variant 转 INSTANCE 引用 |
| Variant 数量 < 2 | 删 Component | 加 dummy 第 2 Variant(fill 不同)|
| Variant 视觉签名相同 | 合并/删 Variant | "显隐"用 INSTANCE.visible=false / 其他加 fill 或 icon 差异 |
| INSTANCE 引用不存在的 component | 删 INSTANCE | 把缺失 Component 加回 components[] |
| components[] 顺序错 | (不会出现自动错) | 按依赖关系重排:子 → 外层 |

**元铁律**: 删 Component 必须**先和用户确认**,不擅自决定。Component 列表是用户的设计决策。

---

⛔ 全部 ✅ 后才能交付 final_scene.json。有任何 ❌ 必须修正后重新自检,直到全部通过。
⛔ 第九层失败时**绝不能直接交付 JSON**,因为 S7 脚本会抽不出 Component。
⛔ 第十层失败时**绝不能粘到 Figma 插件**,因为下拉切换会缺项,设计师没法用。
⛔ 第十一层失败时**绝不能跑 .red 生成**,因为引擎渲染会父子尺寸不匹配视觉错位。
⛔ 第十二层失败时**绝不能粘到 Figma 插件**,因为组件库 Set 会创建失败 / 漏网 FRAME 让设计师困惑。
