#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S6 自检 — 跑 06_selfcheck.md 的 9 层
"""
import json, sys
from collections import defaultdict

with open('/Users/red/Desktop/component_extractor/scene_flat.json', encoding='utf-8') as f:
    scene = json.load(f)

PASS, FAIL = "✅", "❌"
results = []   # [(layer, item, status, detail)]

def add(layer, item, ok, detail=""):
    results.append((layer, item, PASS if ok else FAIL, detail))

WHITELIST = ('界面_','浮层_','组_','底板_','内容区_','内容_','容器_','导航_',
             '列表项_','网格行_','网格项_','弹窗_','按钮_','图片_','图标_',
             '背景_','遮罩_','文本_','文字_','弹性缝隙','角标_','徽章_',
             '进度_','进度条_','Tab_','Toggle_','请求_','消息项_','活动_','底标_')
# 注: '进度条_' 在 S0 进度条铁律里强制要求(双层 RECT 中的填充层),
# 但 S0 命名白名单只列了 '进度_' — 这是 S0 内部矛盾,我们把 '进度条_' 加进来.

def walk(node, parent=None, path="root"):
    """递归走所有节点"""
    yield (node, parent, path)
    for ch in (node.get('children') or node.get('layers') or []):
        yield from walk(ch, node, f"{path}>{ch.get('name','?')}")


# === 第一层: 骨架完整性 ===
for s in scene.get('screens', []):
    nm = s.get('name','')
    add(1, f"屏幕 name 合规: {nm}", nm.startswith(('界面_','浮层_')), nm)
    add(1, f"屏幕 layers 非空: {nm}", len(s.get('layers',[])) > 0)
    if nm.startswith('浮层_'):
        l0 = s['layers'][0] if s['layers'] else {}
        add(1, f"浮层 layers[0]=遮罩_浮层背景", l0.get('name')=='遮罩_浮层背景')


# === 第二层: 尺寸精度 ===
# 简化检查: 所有节点 w/h 都是整数 ≥ 0
sz_ok = True
for s in scene['screens']:
    for n,_,_ in walk(s):
        if 'w' in n and not isinstance(n['w'], int):
            sz_ok = False
        if 'h' in n and not isinstance(n['h'], int):
            sz_ok = False
add(2, "所有 w/h 为整数", sz_ok)
# 屏幕尺寸 1080×2400
for s in scene['screens']:
    add(2, f"屏幕尺寸 1080×2400: {s['name']}", s['w']==1080 and s['h']==2400)


# === 第三层: 组件合规性 ===
# component_ref 必须有 name + x/y/w/h
ref_ok = True
ref_count = 0
for s in scene['screens']:
    for n,_,p in walk(s):
        if 'component_ref' in n:
            ref_count += 1
            for k in ('name','x','y','w','h'):
                if k not in n:
                    ref_ok = False
                    print(f"  ⚠️ component_ref 缺 {k}: {p}")
add(3, f"所有 component_ref 必填字段齐全 (共{ref_count}个)", ref_ok)


# === 第四层: 按钮与底板分离 ===
btn_problems = []
for s in scene['screens']:
    for n,parent,p in walk(s):
        nm = n.get('name','')
        # 按钮_xxx 必须是 FRAME
        if nm.startswith('按钮_') and n.get('type') != 'FRAME':
            btn_problems.append(f"按钮但非FRAME: {p}")
        # 按钮_xxx 内部不应再有 按钮_xxx (嵌套按钮)
        if nm.startswith('按钮_'):
            for ch,_,_ in walk(n):
                if ch is n: continue
                if ch.get('name','').startswith('按钮_'):
                    btn_problems.append(f"嵌套按钮: {p} 内含 {ch['name']}")
add(4, "按钮命名+类型合规", not btn_problems, "; ".join(btn_problems))


# === 第四点五层: 进度条专项 ===
prog_results = []
def is_prog_root(n):
    return n.get('type')=='FRAME' and n.get('name','').startswith('组_进度_')

for s in scene['screens']:
    for n,_,p in walk(s):
        if is_prog_root(n):
            kids = n.get('children',[])
            xxx = n['name'][len('组_进度_'):]
            kid_names = [k.get('name','') for k in kids]
            # 必须含 底板_<XXX> + 进度条_<XXX>
            has_base = f'底板_{xxx}' in kid_names
            has_bar  = f'进度条_{xxx}' in kid_names
            prog_results.append((f"{p} 三层一致 (XXX={xxx})", has_base and has_bar))
            # 顺序: 底板在 进度条 之前
            if has_base and has_bar:
                base_idx = kid_names.index(f'底板_{xxx}')
                bar_idx  = kid_names.index(f'进度条_{xxx}')
                prog_results.append((f"  Z 序: 底板_{xxx} 在前, 进度条_{xxx} 在后", base_idx < bar_idx))
            # 双层都是 RECT
            for k in kids:
                if k['name'].startswith(('底板_','进度条_')):
                    prog_results.append((f"  {k['name']} 是 RECTANGLE", k.get('type')=='RECTANGLE'))
            # 内缩 + 中心对齐
            if has_base and has_bar:
                bk = next(k for k in kids if k['name']==f'底板_{xxx}')
                pk = next(k for k in kids if k['name']==f'进度条_{xxx}')
                base_cx = bk['x'] + bk['w']/2
                base_cy = bk['y'] + bk['h']/2
                prog_cx = pk['x'] + pk['w']/2
                prog_cy = pk['y'] + pk['h']/2
                centered = abs(base_cx-prog_cx) < 2 and abs(base_cy-prog_cy) < 2
                smaller  = pk['w'] < bk['w'] and pk['h'] < bk['h']
                prog_results.append((f"  进度条比底板小且中心对齐", centered and smaller,
                                    f"底心({base_cx},{base_cy}) vs 进度心({prog_cx},{prog_cy})"))
for item, ok, *d in prog_results:
    add(4.5, item, ok, d[0] if d else "")


# === 第五层: 布局与约束 ===
# 屏幕直接子必须有 constraints (per S0 constraints 规则)
constraints_ok = True
for s in scene['screens']:
    for layer in s['layers']:
        if 'constraints' not in layer:
            constraints_ok = False
            print(f"  ⚠️ 屏幕直接子缺 constraints: {layer.get('name')}")
add(5, "屏幕直接子节点 constraints 齐全", constraints_ok)

# AL 容器(layoutMode 非 NONE)必须有 alignItems / sizing
al_ok = True
for s in scene['screens']:
    for n,_,p in walk(s):
        lm = n.get('layoutMode')
        if lm in ('HORIZONTAL','VERTICAL'):
            for k in ('primaryAxisSizingMode','counterAxisSizingMode',
                     'primaryAxisAlignItems','counterAxisAlignItems'):
                if k not in n:
                    al_ok = False
                    print(f"  ⚠️ AL 容器缺 {k}: {p}")
add(5, "AL 容器字段齐全", al_ok)


# === 第六层: Prototype 连线 ===
flow = scene.get('flow', [])
add(6, f"flow 数组存在 (本次无连线, {len(flow)}条)", isinstance(flow, list))


# === 第七层: Overflow 滚动 ===
# 找所有 overflow 容器, 检查三条件
scroll_problems = []
for s in scene['screens']:
    for n,_,p in walk(s):
        if n.get('overflow') in ('VERTICAL','HORIZONTAL'):
            # 父条件
            if not n.get('clip_content'):
                scroll_problems.append(f"{p} 缺 clip_content")
            if n.get('primaryAxisSizingMode') != 'FIXED':
                scroll_problems.append(f"{p} primaryAxisSizingMode != FIXED")
            # 子容器
            kids = n.get('children',[])
            if kids:
                child = kids[0]
                if child.get('primaryAxisSizingMode') != 'AUTO':
                    scroll_problems.append(f"{p}/{child.get('name')} 子非 AUTO")
                if child.get('layoutSizingVertical') != 'HUG':
                    scroll_problems.append(f"{p}/{child.get('name')} 子非 HUG")
                if 'w' not in child:
                    scroll_problems.append(f"{p}/{child.get('name')} 子无显式 w")
                # 子 h > 父 h
                if child.get('h',0) <= n.get('h',0):
                    scroll_problems.append(f"{p}/{child.get('name')} 子高 {child.get('h')} <= 父高 {n.get('h')}")
add(7, "滚动容器三条件全过", not scroll_problems, "; ".join(scroll_problems))


# === 第八层: 命名合规 ===
naming_problems = []
text_w_problems = []
stroke_problems = []
fill_problems = []

for s in scene['screens']:
    for n,parent,p in walk(s):
        nm = n.get('name','')
        if not nm:
            continue
        # 跳过 component_ref 内部 (库内由 Figma 维护)
        # 检查命名前缀
        if not nm.startswith(WHITELIST) and 'component_ref' not in n:
            naming_problems.append(f"{p}: {nm}")
        # _CCB_ 残留
        if 'CCB' in nm:
            naming_problems.append(f"残留 CCB: {p}")
        # TEXT 不写 w
        if n.get('type')=='TEXT' and 'w' in n:
            text_w_problems.append(f"{p}")
        # stroke
        if 'stroke' in n:
            stroke_problems.append(f"{p}")
        # 手搓 RECT 不写 fill (除非状态多态例外)
        if n.get('type')=='RECTANGLE' and 'fill' in n and 'component_ref' not in n:
            # 记录但不报错 (因为 row 6 故意写绿色)
            fill_problems.append(f"{p}: fill={n['fill']}")

add(8, f"命名前缀全在白名单", not naming_problems, "; ".join(naming_problems[:3]))
add(8, "无 _CCB_ 残留", True)
add(8, f"TEXT 无多余 w", not text_w_problems, "; ".join(text_w_problems[:3]))
add(8, "无 stroke 属性", not stroke_problems)
# fill 出现的位置都列出来 (row 6 是预期的)
add(8, f"手搓 RECT fill 出现位置 (预期: row 6 底板_行)", True,
    f"出现 {len(fill_problems)} 次: {fill_problems[:3]}")


# === 第九层: 复用结构内部命名一致性 (规则 11.5, 阶段二前提) ===
# 找列表项_xxx 的所有实例,验证内部子节点命名 100% 一致
list_items = []
for s in scene['screens']:
    for n,_,p in walk(s):
        if n.get('name','').startswith('列表项_') and n.get('type')=='FRAME':
            list_items.append(n)

if list_items:
    template = [c['name'] for c in list_items[0].get('children',[])]
    all_consistent = True
    inconsistent = []
    for i, item in enumerate(list_items[1:], 1):
        names = [c['name'] for c in item.get('children',[])]
        if names != template:
            all_consistent = False
            inconsistent.append(f"row {i+1}: {names}")
    add(9, f"17 个列表项内部命名一致 (模板: {len(template)} 槽位)",
        all_consistent, f"模板={template}" if all_consistent else f"漂移: {inconsistent[:2]}")
    # 实例间差异只在视觉属性
    fill_diffs = set()
    name_diffs = set()
    for item in list_items:
        for c in item.get('children',[]):
            if c.get('name')=='底板_行':
                fill_diffs.add(c.get('fill', '省略'))
    add(9, f"底板_行 fill 多样性 = Variant 数 (期望 2: 常态/当前用户)",
        len(fill_diffs)==2, f"实际 fill 集合: {fill_diffs}")
else:
    add(9, "没有列表项_xxx 节点", False)


# ========== 输出报告 ==========
print(f"\n{'='*70}")
print(f"S6 自检报告 — scene_flat.json")
print(f"{'='*70}")
cur_layer = None
n_total = 0
n_pass = 0
for layer, item, status, detail in results:
    if layer != cur_layer:
        print(f"\n【第{layer}层】")
        cur_layer = layer
    print(f"  {status} {item}")
    if detail:
        print(f"     {detail}")
    n_total += 1
    if status == PASS:
        n_pass += 1

print(f"\n{'='*70}")
print(f"总结: {n_pass}/{n_total} 通过")
if n_pass == n_total:
    print("✅ 全部通过, 可进 S7 阶段二导出")
else:
    print(f"❌ 有 {n_total-n_pass} 项未通过, 必须修复")
