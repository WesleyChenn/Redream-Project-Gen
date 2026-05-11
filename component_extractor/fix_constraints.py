#!/usr/bin/env python3
"""
把组件库 JSON 里所有 constraints 改成 SCALE/SCALE
(满足 S3 预检 1: component_ref 内部子节点必须 SCALE/SCALE 才能等比缩放)

用法: python3 fix_constraints.py <input.json> <output.json>
"""
import json, sys

def fix(node):
    if isinstance(node, dict):
        if 'constraints' in node and isinstance(node['constraints'], dict):
            node['constraints'] = {'horizontal': 'SCALE', 'vertical': 'SCALE'}
        for v in node.values():
            fix(v)
    elif isinstance(node, list):
        for v in node:
            fix(v)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("用法: python3 fix_constraints.py <input.json> <output.json>")
        sys.exit(1)
    with open(sys.argv[1], encoding='utf-8') as f:
        data = json.load(f)

    # 计数: 改前
    def count(node, total=0):
        if isinstance(node, dict):
            if 'constraints' in node:
                total += 1
            for v in node.values():
                total = count(v, total)
        elif isinstance(node, list):
            for v in node:
                total = count(v, total)
        return total

    n_before = count(data)
    fix(data)
    n_after = count(data)

    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 转换完成: 共 {n_after} 个 constraints 字段全部改为 SCALE/SCALE")
    print(f"📄 输出: {sys.argv[2]}")
