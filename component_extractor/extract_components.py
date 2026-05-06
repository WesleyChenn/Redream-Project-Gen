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

def extract_components(scene, min_instances):
    # 1) 收集所有 FRAME 候选
    candidates = []
    for screen in scene.get('screens', []):
        sid = screen.get('id') or screen.get('name', '')
        collect_frames(screen.get('layers', []), sid, (), candidates)

    # 2) 按结构指纹分组
    groups = defaultdict(list)
    for c in candidates:
        groups[c['fp']].append(c)

    # 3) 过滤: 实例数达标
    valid = [(fp, insts) for fp, insts in groups.items()
             if len(insts) >= min_instances]

    # 4) 排序: 优先抽"高复用 + 外层"的(避免嵌套冲突)
    valid.sort(key=lambda x: (-len(x[1]),
                              min(c['depth'] for c in x[1])))

    # 5) 提取 + 跳过被外层 Component 吞掉的内层
    extracted = []   # [(comp_def, [instances], vsig_to_name)]
    used_names = set()
    extracted_paths = []   # [(screen_id, path)] 已被抽走的位置

    for fp, insts in valid:
        # 任意实例落在已抽外层 Component 的内部 → 跳过
        skip = False
        for c in insts:
            for sid, p in extracted_paths:
                if c['screen_id'] == sid and is_descendant(c['path'], p):
                    skip = True
                    break
            if skip:
                break
        if skip:
            continue

        comp_name = derive_component_name(insts, used_names)

        # Variant 聚类
        vgroups = defaultdict(list)
        for c in insts:
            vgroups[wrapper_signature(c['node'])].append(c)

        # 默认 Variant = 实例数最多的
        sorted_vs = sorted(vgroups.items(), key=lambda x: -len(x[1]))
        variants_def = []
        vsig_to_name = {}
        for idx, (vsig, vins) in enumerate(sorted_vs):
            is_default = (idx == 0)
            # 注: Variant 名字禁止含下划线 _ (Figma combineAsVariants 对"下划线分隔"
            # 的对称命名会误解析,导致同 Component 内部分 Variant 在右侧下拉里互相吞掉)
            vname = '常态' if is_default else f'变体{idx + 1}'
            vsig_to_name[vsig] = vname
            template = vins[0]['node']
            v_def = {
                'name': vname,
                'layers': [deepcopy(c) for c in get_kids(template)],
            }
            if is_default:
                v_def['is_default'] = True
            variants_def.append(v_def)

        # Component 尺寸 = 各 Variant 最大值 (兼容尺寸不一致)
        max_w = max(c['node'].get('w', 0) for c in insts)
        max_h = max(c['node'].get('h', 0) for c in insts)

        comp_def = {
            'name': comp_name,
            'w': max_w,
            'h': max_h,
            'property_name': '状态',
            'variants': variants_def,
        }
        extracted.append((comp_def, insts, vsig_to_name))
        for c in insts:
            extracted_paths.append((c['screen_id'], c['path']))

    if not extracted:
        new_scene = deepcopy(scene)
        new_scene.setdefault('components', [])
        return new_scene, []

    # 6) 构造替换 map: 原 FRAME → INSTANCE 节点
    repl_map = {}
    for comp_def, insts, vsig_to_name in extracted:
        for c in insts:
            orig = c['node']
            inst_node = {
                'type': 'INSTANCE',
                'name': orig.get('name', ''),
                'component_name': comp_def['name'],
                'variant': vsig_to_name[wrapper_signature(orig)],
                'x': orig.get('x', 0),
                'y': orig.get('y', 0),
                'w': orig.get('w', 0),
                'h': orig.get('h', 0),
            }
            if 'constraints' in orig:
                inst_node['constraints'] = orig['constraints']
            # AL 内子节点的 layoutSizing 字段也要保留
            for k in ('layoutSizingHorizontal', 'layoutSizingVertical', 'layoutGrow'):
                if k in orig:
                    inst_node[k] = orig[k]
            repl_map[(c['screen_id'], c['path'])] = inst_node

    # 7) 重写 scene
    new_scene = deepcopy(scene)
    new_scene['components'] = [c[0] for c in extracted]

    for screen in new_scene.get('screens', []):
        sid = screen.get('id') or screen.get('name', '')
        replace_in_layers(screen.get('layers', []), (), sid, repl_map)

    # 报告数据
    report = []
    for comp_def, insts, _ in extracted:
        report.append({
            'name': comp_def['name'],
            'w': comp_def['w'],
            'h': comp_def['h'],
            'variants': [v['name'] for v in comp_def['variants']],
            'instance_count': len(insts),
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


# ========== CLI ==========

def main():
    ap = argparse.ArgumentParser(
        description='阶段二: 把扁平 scene.json 转成 v20.6 schema (含 components + INSTANCE)')
    ap.add_argument('input', help='输入: 扁平 scene.json (阶段一输出)')
    ap.add_argument('output', help='输出: v20.6 scene.json (粘贴到 Figma 插件)')
    ap.add_argument('--min-instances', type=int, default=DEFAULT_MIN_INSTANCES,
                    help=f'最少复用次数 (默认 {DEFAULT_MIN_INSTANCES})')
    args = ap.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        scene = json.load(f)

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
    print()
    print(f"📄 输出: {args.output}")
    print("   → 直接粘贴到 Figma 插件 '▶ 生成' tab,一键出 Component Set + 屏幕")


if __name__ == '__main__':
    main()
