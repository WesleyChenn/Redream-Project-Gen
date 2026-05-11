#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阶段二: Component 识别 + JSON 重写

输入: 扁平 scene.json (阶段一无 Component skill 生成,所有重复结构展开)
输出: v20.6 schema scene.json (含 components 数组 + INSTANCE 节点)
       —— 直接粘贴到 Figma 插件 "▶ 生成" tab,一次性出 Component Set + 屏幕

用法:
    python3 extract_components.py input.json output.json
    python3 extract_components.py input.json output.json --min-instances 3

设计原则:
    - 算法层(确定性): 结构指纹找复用 + 视觉签名聚 Variant
    - 命名层(启发式): 公共前缀推 Component 名,Variant 占位名 (常态/变体_N)
    - 命名后续可由 Claude 重命名为更语义的名字 (已完成/可领取/...)

已知简化(v1):
    - 不做嵌套 Component 抽取 (外层 Component 优先,内层不再独立抽)
    - Variant 命名只给占位名,需人工/Claude 二次润色
    - 数据驱动 vs 状态多态 的判断只看 TEXT.content / 视觉属性 二分,
      没有图片url等更细的字段(后续可加)
"""

import json
import sys
import argparse
import hashlib
from collections import defaultdict
from copy import deepcopy

# ========== 配置 ==========

# 不当 Component 抽取的命名前缀(顶层屏幕 / 全屏背景 / 遮罩)
SKIP_PREFIXES = ('界面_', '浮层_', '遮罩_', '背景_')

# 位置/尺寸归一化容差 (像素)
POS_TOLERANCE = 10
SIZE_TOLERANCE = 10

# 最少复用次数(同结构 ≥ N 次才抽)
DEFAULT_MIN_INSTANCES = 2

# 视觉属性字段(参与 Variant 区分)
VISUAL_FIELDS = ('corner_radius', 'fill', 'opacity', 'font_size',
                 'font_weight', 'visible', 'textAlignHorizontal')


# ========== 评分配置 (普世性 PoC) ==========
# 通过 --debug-scoring / --simulate-nested 暴露
SCORING_CONFIG = {
    'min_value_threshold': 10,         # score 阈值 (实例数 × 子节点数)
    'cross_cutting_bonus_per_parent': 2,  # 跨父加分系数
    'depth_penalty_per_level': 1.5,    # 深度惩罚
    'variant_dim_warn_threshold': 6,   # Variant 数过多警告阈值
    'max_nesting_depth': 3,            # 嵌套深度硬上限
}


# ========== 工具 ==========

def round_to(x, step):
    return int(round(x / step) * step) if step > 0 else int(x or 0)


def get_kids(node):
    """FRAME 用 children, screen 用 layers,做兼容"""
    return node.get('children') or node.get('layers') or []


# ========== 指纹 ==========

def structural_fingerprint(node):
    """
    结构指纹 — 同结构的 FRAME 指纹相同
    忽略: 数据(content) / 视觉(颜色/圆角/字号)
    保留: 类型层级 + 尺寸 + 子节点相对位置 + 子节点命名

    注: wrapper FRAME 自身 name 不参与(实例名会变),但子节点 name 参与
        防止形状碰巧一样但语义无关的两个 FRAME 被错聚
    """
    parts = [node.get('type', '?')]
    parts.append(f"{round_to(node.get('w', 0), SIZE_TOLERANCE)}x"
                 f"{round_to(node.get('h', 0), SIZE_TOLERANCE)}")
    for child in get_kids(node):
        cx = round_to(child.get('x', 0), POS_TOLERANCE)
        cy = round_to(child.get('y', 0), POS_TOLERANCE)
        cn = child.get('name', '')
        parts.append(f"@{cx},{cy}/{cn}:{structural_fingerprint(child)}")
    return hashlib.md5('|'.join(parts).encode()).hexdigest()[:12]


def visual_signature(node, include_self_name=True):
    """
    视觉签名 — 同 Variant 的实例签名相同
    忽略: 数据驱动字段 (TEXT.content / image url 等)
    保留: 视觉属性 (颜色/圆角/字号/显隐) + 子节点结构 + 子节点命名

    include_self_name=False 时,顶层节点自身 name 不参与
    (用于 wrapper FRAME — 它的 name 是实例名,会变,不算视觉差异)
    """
    parts = [node.get('type', '?')]
    if include_self_name:
        parts.append(node.get('name', ''))
    parts.append(f"{round_to(node.get('w', 0), SIZE_TOLERANCE)}x"
                 f"{round_to(node.get('h', 0), SIZE_TOLERANCE)}")
    for k in VISUAL_FIELDS:
        if k in node:
            parts.append(f"{k}={node[k]}")
    for child in get_kids(node):
        cx = round_to(child.get('x', 0), POS_TOLERANCE)
        cy = round_to(child.get('y', 0), POS_TOLERANCE)
        # 子节点 name 始终参与(公共节点必须命名一致)
        parts.append(f"@{cx},{cy}:{visual_signature(child, include_self_name=True)}")
    return hashlib.md5('|'.join(parts).encode()).hexdigest()[:12]


def wrapper_signature(node):
    """专用于 Component 候选 FRAME 的视觉签名(忽略 wrapper 自身 name)"""
    return visual_signature(node, include_self_name=False)


# ========== 收集候选 ==========

def collect_frames(layers, screen_id, path, out):
    """递归收集所有 FRAME 节点 (跳过顶层框架/遮罩/背景)"""
    for i, layer in enumerate(layers):
        cur_path = path + (i,)
        if layer.get('type') == 'FRAME':
            name = layer.get('name', '')
            if not any(name.startswith(p) for p in SKIP_PREFIXES):
                out.append({
                    'screen_id': screen_id,
                    'path': cur_path,
                    'node': layer,
                    'fp': structural_fingerprint(layer),
                    'depth': len(cur_path),
                })
        kids = get_kids(layer)
        if kids:
            collect_frames(kids, screen_id, cur_path, out)


# ========== 命名启发式 ==========

def common_prefix(strs):
    if not strs:
        return ''
    s_min = min(strs)
    s_max = max(strs)
    for i, c in enumerate(s_min):
        if i >= len(s_max) or c != s_max[i]:
            return s_min[:i]
    return s_min


def derive_component_name(instances, used_names):
    """从实例命名推 Component 名 (公共前缀 - 数字/分隔符尾)"""
    names = [inst['node'].get('name', '') for inst in instances]
    prefix = common_prefix(names).rstrip('_-0123456789 ')
    if not prefix:
        prefix = f"Component_{instances[0]['fp'][:6]}"
    base = prefix
    n = 1
    while base in used_names:
        n += 1
        base = f"{prefix}_{n}"
    used_names.add(base)
    return base


# ========== 嵌套去重 ==========

def is_descendant(path_a, path_b):
    """path_a 是 path_b 的后代?"""
    return len(path_a) > len(path_b) and path_a[:len(path_b)] == path_b


# ========== 主流程 ==========

def _make_instance_node(orig, comp_def, variant_name, overrides=None):
    """从原始 FRAME 节点生成 INSTANCE 引用节点

    保留原 FRAME 上 wrapper 级别的字段(visible / opacity 等),
    避免替换为 INSTANCE 时丢失 "整个组件被父级隐藏" 的信息。

    overrides: 该实例与 Variant 模板之间 TEXT.content / component_ref.overrides
               的差异 (v20.7+ 修复, 防止"6 行只渲染同一个名字"的 bug)
    """
    inst_node = {
        'type': 'INSTANCE',
        'name': orig.get('name', ''),
        'component_name': comp_def['name'],
        'variant': variant_name,
        'x': orig.get('x', 0),
        'y': orig.get('y', 0),
        'w': orig.get('w', 0),
        'h': orig.get('h', 0),
    }
    if 'constraints' in orig:
        inst_node['constraints'] = orig['constraints']
    for k in ('layoutSizingHorizontal', 'layoutSizingVertical', 'layoutGrow'):
        if k in orig:
            inst_node[k] = orig[k]
    # 保留 wrapper 级别的视觉/状态字段,这些不属于 Variant 内部内容,
    # 而属于"这个 INSTANCE 实例本身的状态"(整个被隐藏 / 半透明等)。
    for k in ('visible', 'opacity'):
        if k in orig:
            inst_node[k] = orig[k]
    if overrides:
        inst_node['overrides'] = overrides
    return inst_node


def _filter_invisible(layers):
    """递归移除 visible=false 的节点(连同其所有 children)

    v20.7+ 修复: 之前 Variant.layers 把所有元素都塞进去靠 visible 字段切换显示,
    这会污染 Figma 时间线(看到一堆 invisible 占位元素)。改为按 Variant 实际可见性
    过滤,每个 Variant 的 layers 只包含真正要显示的层。
    """
    out = []
    for layer in layers:
        if layer.get('visible') is False:
            continue
        new_layer = dict(layer)
        for k in ('children', 'layers'):
            if k in layer:
                new_layer[k] = _filter_invisible(layer[k])
        out.append(new_layer)
    return out


def _collect_text_and_ref_overrides(template_kids, inst_kids):
    """对比 Variant 模板与某实例的直接 children,收集差异 → 实例级 overrides

    只看两类差异:
        1. TEXT 节点 content 不同 → overrides[<text_name>] = <content>
        2. component_ref 节点 overrides 不同 → overrides[<ref_name>] = <ref_overrides_dict>

    其它差异(visible / variant 等)由 visual_signature 切分到不同 Variant 上,
    不会出现在同 Variant 内的实例间, 这里不处理。

    限制: 只对比直接 children, 不递归进 FRAME (避免名字冲突 + 简化模型)。
          同 Variant 内的同名节点位置一致 → 按 index 对齐即可。
    """
    overrides = {}
    n = min(len(template_kids), len(inst_kids))
    for idx in range(n):
        t = template_kids[idx]
        v = inst_kids[idx]
        t_name = t.get('name', '')
        if not t_name:
            continue

        # TEXT.content 差异
        if t.get('type') == 'TEXT' and v.get('type') == 'TEXT':
            t_content = t.get('content', '')
            v_content = v.get('content', '')
            if t_content != v_content:
                overrides[t_name] = v_content
            continue

        # component_ref.overrides 差异
        if t.get('component_ref') and v.get('component_ref'):
            if t.get('component_ref') == v.get('component_ref'):
                t_ovr = t.get('overrides') or {}
                v_ovr = v.get('overrides') or {}
                if t_ovr != v_ovr:
                    overrides[t_name] = v_ovr
            continue
    return overrides


def _get_node_at_path(scene_root, sid, path):
    """从 scene 按 (screen_id, path) 取节点 (节点可能已被 mutate)"""
    for screen in scene_root.get('screens', []):
        if (screen.get('id') or screen.get('name', '')) != sid:
            continue
        cur = screen.get('layers', [])
        for i, idx in enumerate(path):
            if not isinstance(cur, list) or idx >= len(cur):
                return None
            node = cur[idx]
            if i == len(path) - 1:
                return node
            cur = node.get('children') or node.get('layers') or []
        return None
    return None


def extract_components(scene, min_instances):
    """
    Multi-pass 抽取 (v20.7+):
        Pass 1: 收集候选 + 评分 + 分类 (跨父≥2 → promoted, 否则 → embedded)
        Pass 2: 抽 promoted 内层 Components 先, 在 mutable_scene 里替换为 INSTANCE
        Pass 3: 抽 embedded 外层 Components, 模板从 mutable_scene 取
                (此时模板内部含已替换的 INSTANCE 引用 ✓)
        Pass 4: components 数组按 promoted -> embedded 顺序 (内层在前,满足
                Figma 插件依赖序: 内层 Component 先建, 外层引用)
    """
    # === Pass 1: 收集 + 评分 + 分类 ===
    candidates = []
    for screen in scene.get('screens', []):
        sid = screen.get('id') or screen.get('name', '')
        collect_frames(screen.get('layers', []), sid, (), candidates)

    groups = defaultdict(list)
    for c in candidates:
        groups[c['fp']].append(c)

    valid = [(fp, insts) for fp, insts in groups.items()
             if len(insts) >= min_instances]

    # 用评分把候选分到两类
    promoted = []   # 跨父 ≥2 → 顶级化 (Layer 1 内层提升,跨多个外层共享)
    embedded = []   # 跨父 = 1 → 留作外层 Component 自身
    for fp, insts in valid:
        s = compute_score(insts, SCORING_CONFIG)
        if not s or s['decision'] != 'extract':
            continue
        if s['cross_cutting'] >= 2:
            promoted.append((fp, insts, s))
        else:
            embedded.append((fp, insts, s))

    # promoted 按"实例数降序"排; embedded 按"深度升序"排(浅的先抽,避免 embedded 之间嵌套时模板取错)
    promoted.sort(key=lambda x: -len(x[1]))
    embedded.sort(key=lambda x: min(c['depth'] for c in x[1]))

    extracted = []   # [(comp_def, insts, vsig_to_name, kind, inst_overrides)]
    used_names = set()
    mutable_scene = deepcopy(scene)

    def _build_one(insts, kind):
        """提取一组候选, 模板从 mutable_scene 取(自然含 promoted 替换)

        v20.7+ 新增: 同 Variant 内每个实例与模板对比,收集 TEXT/component_ref
                     差异作为实例级 overrides, 避免"6 行渲染同一名字"的 bug。
        """
        comp_name = derive_component_name(insts, used_names)
        vgroups = defaultdict(list)
        # v20.7+ bug fix: wrapper_signature 必须基于 mutable_scene 的当前节点
        # (Pass 2 抽过 promoted 后,子 FRAME 已替换为 INSTANCE)。否则子级 fill
        # 差异会"漏"到父级,导致父 Component 错误分裂出过多 Variant。
        for c in insts:
            mut_inst = _get_node_at_path(
                mutable_scene, c['screen_id'], c['path']
            ) or c['node']
            vgroups[wrapper_signature(mut_inst)].append(c)

        sorted_vs = sorted(vgroups.items(), key=lambda x: -len(x[1]))
        variants_def = []
        vsig_to_name = {}
        inst_overrides = {}   # (screen_id, path_tuple) -> overrides dict

        for idx, (vsig, vins) in enumerate(sorted_vs):
            is_default = (idx == 0)
            # 占位名禁止下划线 (Figma combineAsVariants 解析问题)
            vname = '常态' if is_default else f'变体{idx + 1}'
            vsig_to_name[vsig] = vname

            # 关键: 模板从 mutable_scene 取
            # 如果 promoted 已经替换过, mutable 里 children 是 INSTANCE
            template_inst = vins[0]
            mut_template = _get_node_at_path(
                mutable_scene, template_inst['screen_id'], template_inst['path']
            )
            if mut_template is None:
                mut_template = template_inst['node']  # fallback

            # 用完整 children 计算 overrides(下面),但 Variant 存的 layers 只保留可见层
            # 避免 Figma 时间线里出现一堆 visible=false 的占位元素
            v_def = {
                'name': vname,
                'layers': _filter_invisible([deepcopy(c) for c in get_kids(mut_template)]),
            }
            if is_default:
                v_def['is_default'] = True
            variants_def.append(v_def)

            # 同 Variant 内每个实例对比模板, 收集 overrides 差异(基于完整 kids 按索引对齐)
            template_kids = get_kids(mut_template)
            for c in vins:
                mut_inst = _get_node_at_path(
                    mutable_scene, c['screen_id'], c['path']
                ) or c['node']
                # 模板自身不需要 overrides
                if mut_inst is mut_template:
                    continue
                inst_kids = get_kids(mut_inst)
                ovrs = _collect_text_and_ref_overrides(template_kids, inst_kids)
                if ovrs:
                    inst_overrides[(c['screen_id'], c['path'])] = ovrs

        max_w = max(c['node'].get('w', 0) for c in insts)
        max_h = max(c['node'].get('h', 0) for c in insts)

        comp_def = {
            'name': comp_name, 'w': max_w, 'h': max_h,
            'property_name': '状态',
            'variants': variants_def,
        }
        extracted.append((comp_def, insts, vsig_to_name, kind, inst_overrides))
        return comp_def, vsig_to_name, inst_overrides

    # === Pass 2: 抽 promoted 内层 ===
    for fp, insts, _ in promoted:
        comp_def, vsig_to_name, inst_overrides = _build_one(insts, 'promoted')
        # 立即在 mutable_scene 里替换 (供 embedded 抽取时的模板取用)
        repl = {}
        for c in insts:
            orig = c['node']
            mut_inst = _get_node_at_path(
                mutable_scene, c['screen_id'], c['path']
            ) or orig
            ovrs = inst_overrides.get((c['screen_id'], c['path']))
            inst_node = _make_instance_node(
                orig, comp_def, vsig_to_name[wrapper_signature(mut_inst)], ovrs)
            repl[(c['screen_id'], c['path'])] = inst_node
        for screen in mutable_scene.get('screens', []):
            sid = screen.get('id') or screen.get('name', '')
            replace_in_layers(screen.get('layers', []), (), sid, repl)

    # === Pass 3: 抽 embedded 外层 ===
    embedded_paths = []
    for fp, insts, _ in embedded:
        # embedded 之间允许嵌套 — 跳过被已抽 embedded 外层吞掉的情况
        skip = False
        for c in insts:
            for sid, p in embedded_paths:
                if c['screen_id'] == sid and is_descendant(c['path'], p):
                    skip = True
                    break
            if skip:
                break
        if skip:
            continue
        _build_one(insts, 'embedded')
        for c in insts:
            embedded_paths.append((c['screen_id'], c['path']))

    if not extracted:
        new_scene = deepcopy(scene)
        new_scene.setdefault('components', [])
        return new_scene, []

    # === Pass 4: 主屏替换 (只 embedded 还没在 mutable 替换过, promoted 已经处理) ===
    repl_map = {}
    for comp_def, insts, vsig_to_name, kind, inst_overrides in extracted:
        if kind == 'promoted':
            continue  # 已经在 mutable_scene 替换过
        for c in insts:
            orig = c['node']
            mut_inst = _get_node_at_path(
                mutable_scene, c['screen_id'], c['path']
            ) or orig
            ovrs = inst_overrides.get((c['screen_id'], c['path']))
            inst_node = _make_instance_node(
                orig, comp_def, vsig_to_name[wrapper_signature(mut_inst)], ovrs)
            repl_map[(c['screen_id'], c['path'])] = inst_node

    # 直接复用 mutable_scene (含 promoted 替换), 再叠加 embedded 替换
    new_scene = mutable_scene
    new_scene['components'] = [c[0] for c in extracted]

    for screen in new_scene.get('screens', []):
        sid = screen.get('id') or screen.get('name', '')
        replace_in_layers(screen.get('layers', []), (), sid, repl_map)

    # 报告数据
    report = []
    for comp_def, insts, _, kind, _o in extracted:
        report.append({
            'name': comp_def['name'],
            'w': comp_def['w'],
            'h': comp_def['h'],
            'variants': [v['name'] for v in comp_def['variants']],
            'instance_count': len(insts),
            'kind': kind,
        })
    return new_scene, report


def replace_in_layers(layers, path, sid, repl_map):
    """递归替换 layers 中匹配 path 的节点为 INSTANCE"""
    for i, layer in enumerate(layers):
        cur_path = path + (i,)
        key = (sid, cur_path)
        if key in repl_map:
            layers[i] = repl_map[key]
        else:
            kids = layer.get('children')
            if kids:
                replace_in_layers(kids, cur_path, sid, repl_map)


# ========== 评分函数 (普世性 PoC) ==========

def compute_score(instances, config=None):
    """
    给一组同结构指纹的候选实例打分.

    评分维度:
        - instance_count:   实例数 (越多越值得抽)
        - avg_children:     平均子节点数 (结构复杂度)
        - cross_cutting:    跨多少不同父路径出现 (多就建议顶级化)
        - variant_dim:      多少个 Variant (太多警告)
        - avg_depth:        平均嵌套深度 (深度惩罚)

    score = base_value + cross_bonus - depth_penalty
    base_value = instance_count × (avg_children + 1)
    """
    config = config or SCORING_CONFIG
    n = len(instances)
    if n == 0:
        return None

    children_counts = [len(get_kids(c['node'])) for c in instances]
    avg_children = sum(children_counts) / n
    max_children = max(children_counts)

    parent_paths = set()
    for c in instances:
        parent_paths.add((c['screen_id'], tuple(c['path'][:-1])))
    cross_cutting = len(parent_paths)

    visual_sigs = set(wrapper_signature(c['node']) for c in instances)
    variant_dim = len(visual_sigs)

    avg_depth = sum(c['depth'] for c in instances) / n

    base_value = n * (avg_children + 1)
    cross_bonus = (config['cross_cutting_bonus_per_parent'] * cross_cutting
                   if cross_cutting >= 2 else 0)
    depth_penalty = max(0, avg_depth - 1) * config['depth_penalty_per_level']

    score = base_value + cross_bonus - depth_penalty

    warnings = []
    if variant_dim > config['variant_dim_warn_threshold']:
        warnings.append(f'Variant 数过多 ({variant_dim} > {config["variant_dim_warn_threshold"]})')
    if avg_depth > 2:
        warnings.append(f'平均深度 {avg_depth:.1f} > 2')
    if cross_cutting >= 3:
        warnings.append(f'跨 {cross_cutting} 个父路径,建议顶级化')

    return {
        'score': round(score, 1),
        'instance_count': n,
        'avg_children': round(avg_children, 1),
        'max_children': max_children,
        'cross_cutting': cross_cutting,
        'variant_dim': variant_dim,
        'avg_depth': round(avg_depth, 1),
        'base_value': round(base_value, 1),
        'cross_bonus': cross_bonus,
        'depth_penalty': round(depth_penalty, 1),
        'warnings': warnings,
        'decision': 'extract' if score >= config['min_value_threshold'] else 'skip',
    }


def collect_candidates_in_layers(layers, sid_prefix, base_path=()):
    """通用收集器: 接受任意 layers,返回候选列表 (用于 layer 1 + layer 2 模拟)"""
    cands = []
    collect_frames(layers, sid_prefix, base_path, cands)
    return cands


def print_scoring_report(scene, config=None, simulate_nested=False, min_instances=2):
    """打印候选评分报告 (不修改 scene)"""
    config = config or SCORING_CONFIG

    # === Layer 1: 在屏幕里扫候选 ===
    candidates_l1 = []
    for screen in scene.get('screens', []):
        sid = screen.get('id') or screen.get('name', '')
        candidates_l1.extend(collect_candidates_in_layers(
            screen.get('layers', []), sid))

    # 按指纹分组
    groups_l1 = defaultdict(list)
    for c in candidates_l1:
        groups_l1[c['fp']].append(c)

    # 过滤实例数
    valid_l1 = [(fp, insts) for fp, insts in groups_l1.items()
                if len(insts) >= min_instances]

    # 评分 + 推断命名
    scored_l1 = []
    for fp, insts in valid_l1:
        s = compute_score(insts, config)
        if s:
            names = [c['node'].get('name', '') for c in insts]
            comp_name = common_prefix(names).rstrip('_-0123456789 ') or '?'
            s['name'] = comp_name
            s['fp'] = fp
            s['instances'] = insts
            s['layer'] = 1
            scored_l1.append(s)

    scored_l1.sort(key=lambda x: -x['score'])

    # === 输出 Layer 1 报告 ===
    print("=" * 90)
    print("【Component 候选评分报告 — Layer 1】")
    print("=" * 90)
    print()
    if not scored_l1:
        print("  (没有满足 min_instances 的候选)")
    else:
        print(f"{'rank':>4} | {'name':<24} | {'score':>5} | {'实例':>4} | "
              f"{'子节':>4} | {'跨父':>4} | {'V':>3} | {'深度':>4} | 决策 + 警告")
        print("-" * 90)
        for i, s in enumerate(scored_l1):
            decision = '✅ extract' if s['decision'] == 'extract' else '⚠️ skip'
            warn = ' '.join('⚠ ' + w for w in s['warnings'])
            print(f"{i+1:>4} | {s['name']:<24} | {s['score']:>5} | "
                  f"{s['instance_count']:>4} | {s['avg_children']:>4} | "
                  f"{s['cross_cutting']:>4} | {s['variant_dim']:>3} | "
                  f"{s['avg_depth']:>4} | {decision} {warn}")

    # === 当前算法决策模拟 (Layer 1) ===
    print()
    print("【当前算法 Layer 1 决策】(实例数排序 + 嵌套跳过)")
    print("-" * 90)
    extracted_paths = []
    for s in scored_l1:
        if s['decision'] != 'extract':
            continue
        skip = False
        for c in s['instances']:
            for sid, p in extracted_paths:
                if c['screen_id'] == sid and is_descendant(c['path'], p):
                    skip = True
                    break
            if skip:
                break
        if skip:
            print(f"  ⏭ 跳过 {s['name']:<24} score={s['score']:>5} "
                  f"({s['instance_count']} 实例) ← 落在已抽外层内")
        else:
            print(f"  ✅ 抽取 {s['name']:<24} score={s['score']:>5} "
                  f"({s['instance_count']} 实例 → {s['variant_dim']} Variant)")
            for c in s['instances']:
                extracted_paths.append((c['screen_id'], c['path']))

    # === Layer 2 模拟 ===
    if simulate_nested:
        print()
        print("=" * 90)
        print("【Layer 2 模拟】(在 Layer 1 抽出的 Component 内部再扫)")
        print("=" * 90)
        print()

        # 先做一次正式提取 (得到 Component 定义)
        new_scene, report = extract_components(scene, min_instances)
        if not new_scene.get('components'):
            print("  Layer 1 没抽出 Component,无法模拟 Layer 2")
            return

        # 对每个 Component 的 Variant.layers 扫候选 + 跨 Variant 聚合
        for comp in new_scene['components']:
            comp_name = comp['name']
            print(f"  ▶ 进入 Component: {comp_name}")
            # 把所有 Variant.layers 当作多个 mini-scene
            inner_cands = []
            for vi, v in enumerate(comp['variants']):
                v_layers = v.get('layers', [])
                vid = f"{comp_name}/{v['name']}"
                cands = collect_candidates_in_layers(v_layers, vid)
                inner_cands.extend(cands)

            if not inner_cands:
                print(f"      (Variant.layers 内无可抽 FRAME)")
                continue

            # 按指纹聚合 (跨 Variant)
            inner_groups = defaultdict(list)
            for c in inner_cands:
                inner_groups[c['fp']].append(c)

            inner_valid = [(fp, insts) for fp, insts in inner_groups.items()
                           if len(insts) >= min_instances]
            if not inner_valid:
                print(f"      (无满足 min_instances={min_instances} 的内层候选)")
                continue

            # 评分内层候选
            scored_l2 = []
            for fp, insts in inner_valid:
                s = compute_score(insts, config)
                if s:
                    names = [c['node'].get('name', '') for c in insts]
                    nm = common_prefix(names).rstrip('_-0123456789 ') or '?'
                    s['name'] = nm
                    scored_l2.append(s)
            scored_l2.sort(key=lambda x: -x['score'])

            # 输出
            for s in scored_l2:
                decision = '✅' if s['decision'] == 'extract' else '⚠'
                warn = ' '.join('⚠ ' + w for w in s['warnings'])
                print(f"      {decision} {s['name']:<24} score={s['score']:>5} "
                      f"实例={s['instance_count']} V={s['variant_dim']} "
                      f"跨父={s['cross_cutting']} 深度={s['avg_depth']} {warn}")

    # === 配置回显 ===
    print()
    print("【评分配置】")
    for k, v in (config or SCORING_CONFIG).items():
        print(f"  {k}: {v}")
    print(f"  min_instances: {min_instances}")


# ========== INSTANCE 尺寸同步检查 (v20.7+) ==========

def check_instance_size_consistency(scene):
    """
    检查 v20.6 schema 里 INSTANCE 节点的尺寸一致性。

    两条规则(对应 S0 文档"INSTANCE 尺寸同步铁律"):
        1. 同 component_name 的所有 INSTANCE w/h 必须一致
        2. 每个 INSTANCE 的 w/h 必须等于对应 components[].w/h

    任一规则违反 → 设计师在 Figma 屏幕里拖过 INSTANCE 但没 Push 到主版。
    返回 issue 列表(每条一个 dict),不修复(workflow 必须从 Figma 端解决)。
    """
    comp_size = {c.get('name'): (c.get('w'), c.get('h'))
                 for c in scene.get('components', [])}
    by_comp = defaultdict(list)

    def walk(n):
        if n.get('type') == 'INSTANCE':
            cn = n.get('component_name', '')
            by_comp[cn].append({
                'name': n.get('name'),
                'w': n.get('w'),
                'h': n.get('h'),
            })
        for ch in (n.get('children') or n.get('layers') or []):
            walk(ch)

    for s in scene.get('screens', []):
        for L in s.get('layers', []):
            walk(L)

    issues = []
    for cn, insts in by_comp.items():
        sizes = set((i['w'], i['h']) for i in insts)
        if len(sizes) > 1:
            issues.append({
                'kind': 'inconsistent_instance_sizes',
                'component': cn,
                'instances': insts,
                'sizes': sorted(sizes),
            })
        cw, ch = comp_size.get(cn, (None, None))
        if cw is None:
            continue
        for i in insts:
            if (i['w'], i['h']) != (cw, ch):
                issues.append({
                    'kind': 'instance_vs_component_mismatch',
                    'component': cn,
                    'instance_name': i['name'],
                    'instance_size': (i['w'], i['h']),
                    'component_size': (cw, ch),
                })
    return issues


def print_size_issues(issues):
    """打印尺寸不一致报告(终端友好格式)"""
    if not issues:
        print("✅ INSTANCE 尺寸同步检查全部通过")
        return
    print()
    print(f"⚠️  发现 {len(issues)} 条 INSTANCE 尺寸不一致问题:")
    print()
    for it in issues:
        if it['kind'] == 'inconsistent_instance_sizes':
            print(f"  ❌ Component '{it['component']}' 的 INSTANCE 尺寸不一致:")
            for i in it['instances']:
                print(f"        - {i['name']}: {i['w']}×{i['h']}")
            print(f"     出现尺寸集合: {it['sizes']}")
        elif it['kind'] == 'instance_vs_component_mismatch':
            cw, ch = it['component_size']
            iw, ih = it['instance_size']
            print(f"  ❌ {it['component']} / {it['instance_name']}: "
                  f"INSTANCE {iw}×{ih} ≠ Component 本体 {cw}×{ch}")
    print()
    print("  📌 修复方法:")
    print("     1. 在 Figma 里选中目标尺寸的 INSTANCE")
    print("     2. 右键 → Push changes to main component (⌥⌘Y / Alt+Ctrl+Y)")
    print("     3. 所有同 component 的 INSTANCE 自动同步,Component 本体也更新")
    print("     4. 重新导出 scene.json 重跑本脚本直到全部 ✅")
    print()
    print("  ⛔ 不修复直接生成 .red → 父子尺寸不匹配,渲染视觉错位")


# ========== CLI ==========

def main():
    ap = argparse.ArgumentParser(
        description='阶段二: 把扁平 scene.json 转成 v20.6 schema (含 components + INSTANCE)')
    ap.add_argument('input', help='输入: 扁平 scene.json (阶段一输出)')
    ap.add_argument('output', nargs='?', default=None,
                    help='输出: v20.6 scene.json (粘贴到 Figma 插件). '
                         '在 --debug-scoring / --check-sizes 模式下可省略')
    ap.add_argument('--min-instances', type=int, default=DEFAULT_MIN_INSTANCES,
                    help=f'最少复用次数 (默认 {DEFAULT_MIN_INSTANCES})')
    ap.add_argument('--debug-scoring', action='store_true',
                    help='只打印候选评分报告, 不修改 scene 不输出文件')
    ap.add_argument('--simulate-nested', action='store_true',
                    help='在评分模式下,模拟 Layer 2 嵌套抽取 (要先 --debug-scoring)')
    ap.add_argument('--check-sizes', action='store_true',
                    help='只对输入 v20.6 JSON 跑 INSTANCE 尺寸同步检查,不修改不输出')
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        scene = json.load(f)

    # === 评分模式 ===
    if args.debug_scoring:
        print_scoring_report(scene,
                              config=SCORING_CONFIG,
                              simulate_nested=args.simulate_nested,
                              min_instances=args.min_instances)
        return

    # === INSTANCE 尺寸同步检查模式 (输入应为 v20.6 schema) ===
    if args.check_sizes:
        issues = check_instance_size_consistency(scene)
        print_size_issues(issues)
        sys.exit(1 if issues else 0)

    # === 正常提取模式 ===
    if not args.output:
        print("❌ 正常提取模式需要 output 参数,"
              "加 --debug-scoring 跑评分预览或 --check-sizes 跑尺寸检查")
        sys.exit(1)

    new_scene, report = extract_components(scene, args.min_instances)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(new_scene, f, ensure_ascii=False, indent=2)

    # 终端报告
    if not report:
        print("⚠️  没有发现可抽取的 Component (尝试 --min-instances 1 看看)")
    else:
        print(f"✅ 抽取了 {len(report)} 个 Component:")
        for r in report:
            vs = ', '.join(r['variants'])
            print(f"  • {r['name']}  ({r['w']}×{r['h']}, "
                  f"{r['instance_count']} 实例 → {len(r['variants'])} Variant: {vs})")

    # INSTANCE 尺寸同步检查(每次抽取后自动跑)
    size_issues = check_instance_size_consistency(new_scene)
    print_size_issues(size_issues)

    print()
    print(f"📄 输出: {args.output}")
    print("   → 直接粘贴到 Figma 插件 '▶ 生成' tab,一键出 Component Set + 屏幕")
    if size_issues:
        print()
        print("⛔ 警告: 上方 INSTANCE 尺寸不一致问题未解决,"
              "粘到插件生成 .red 会父子尺寸错位。请先在 Figma 端 Push 到主版后重新导出。")


if __name__ == '__main__':
    main()
