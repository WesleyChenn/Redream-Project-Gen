#!/usr/bin/env python3
"""
S11 主路径 — Claude 直接产 v20.6 schema final_scene.json.
跳过 extract_components.py.
"""
import json
from copy import deepcopy

# ============================================================
# 加载 flat scene (用于主屏的 13 列表项实例数据)
# ============================================================
flat = json.load(open('scene.json'))

# 13 用户数据 (跟 build_scene.py 一致)
USERS = [
    (1,  "Choisss", "GrandKnight", "有", "有", "带装饰", "529", "当前用户"),
    (2,  "onon",    "GrandKnight", "有", "有", "带装饰", "419", "常态"),
    (3,  "Choy",    "GrandKnight", "有", "有", "带装饰", "244", "常态"),
    (4,  "luk",     "GrandKnight", "空", "空", "带装饰", "129", "常态"),
    (5,  "Kkk",     "Knight",      "空", "空", "带装饰", "127", "常态"),
    (6,  "mmmmm",   "Knight",      "空", "空", "不带装饰", "108", "常态"),
    (7,  "Csl",     "Knight",      "空", "空", "不带装饰", "95",  "常态"),
    (8,  "Arthur",  "空",          "空", "空", "不带装饰", "65",  "常态"),
    (9,  "TTeresa", "空",          "空", "空", "不带装饰", "64",  "常态"),
    (10, "hshen",   "Knight",      "有", "空", "不带装饰", "58",  "常态"),
    (11, "Cassandra","空",         "空", "空", "不带装饰", "25",  "常态"),
    (12, "cyrax",   "空",          "空", "空", "不带装饰", "25",  "常态"),
    (13, "789",     "Knight",      "有", "空", "不带装饰", "12",  "常态"),
]

def rank_variant(n):
    return {1:"金", 2:"银", 3:"铜"}.get(n, "普通")

# ============================================================
# 工具: 给 layer 加 element_class (v20.6 必填)
# ============================================================
DYNAMIC_NAMES = {
    '图片_头像', '图片_帘子装饰', '图片_装饰物前', '图片_道具', '图片_盾',
    '图片_海盗主图', '图片_装饰_金币堆', '图片_盾头像',
    '图片_宝箱_金', '图片_宝箱_银', '图片_宝箱_铜',
    '文本_玩家名', '文本_玩家名_Choisss', '文本_总进度', '文本_等级',
    '文本_排名', '文本_道具数', '文本_数量', '文本_状态_数字', '文本_时间',
    '图标_对勾', '图标_舵轮', '图标_沙漏', '图标_进度起点',
}
def add_element_class(node):
    if isinstance(node, dict):
        if node.get('type') in ('RECTANGLE', 'TEXT'):
            if 'element_class' not in node:
                node['element_class'] = 'dynamic' if node.get('name') in DYNAMIC_NAMES else 'static'
        for k in ('children', 'layers'):
            if k in node:
                for c in node[k]: add_element_class(c)

# ============================================================
# Component 定义 (按依赖序: 子在前, 外层在后)
# ============================================================

# ---------- 1. 宝箱 (3 variant: 金/银/铜) ----------
COMP_BAOXIANG = {
    "name": "宝箱", "w": 164, "h": 188,
    "variant_property": "色",
    "variants": [
        {"name": "金", "is_default": True,
         "layers": [
             {"type": "RECTANGLE", "name": "图片_宝箱_金",
              "x": 0, "y": 0, "w": 164, "h": 188, "element_class": "dynamic"}
         ]},
        {"name": "银",
         "layers": [
             {"type": "RECTANGLE", "name": "图片_宝箱_银",
              "x": 0, "y": 0, "w": 164, "h": 188, "element_class": "dynamic"}
         ]},
        {"name": "铜",
         "layers": [
             {"type": "RECTANGLE", "name": "图片_宝箱_铜",
              "x": 0, "y": 0, "w": 164, "h": 188, "element_class": "dynamic"}
         ]},
    ]
}

# ---------- 2. 状态 (3 variant: 已完成/未完成/可领取, 内部异构) ----------
COMP_ZHUANGTAI = {
    "name": "状态", "w": 164, "h": 113,
    "variant_property": "状态",
    "variants": [
        {"name": "已完成",
         "layers": [
             {"type": "RECTANGLE", "name": "图标_对勾",
              "x": 40, "y": 20, "w": 84, "h": 68, "element_class": "static"}
         ]},
        {"name": "未完成", "is_default": True,
         "layers": [
             {"type": "RECTANGLE", "name": "底板_状态_未完成",
              "x": 0, "y": 20, "w": 164, "h": 79, "corner_radius": 39, "element_class": "static"},
             {"type": "TEXT", "name": "文本_状态_数字",
              "x": 0, "y": 35, "w": 164, "h": 45, "content": "3000",
              "font_size": 38, "font_weight": "Bold",
              "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
              "element_class": "dynamic"}
         ]},
        {"name": "可领取",
         "layers": [
             {"type": "FRAME", "name": "按钮_claim",
              "x": 0, "y": 10, "w": 164, "h": 95, "layoutMode": "NONE",
              "children": [
                  {"type": "RECTANGLE", "name": "底板_claim",
                   "x": 0, "y": 0, "w": 164, "h": 95, "corner_radius": 47,
                   "element_class": "static"},
                  {"type": "TEXT", "name": "文本_claim",
                   "x": 0, "y": 25, "w": 164, "h": 45, "content": "claim",
                   "font_size": 38, "font_weight": "Bold",
                   "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
                   "element_class": "static"}
              ]}
         ]},
    ]
}

# ---------- 3. 排名 (4 variant: 金/银/铜/普通) ----------
def rank_layers(variant):
    layers = []
    if variant in ("金", "银", "铜"):
        layers.append({"type": "RECTANGLE", "name": f"底板_排名_{variant}",
                       "x": 0, "y": 0, "w": 95, "h": 95, "corner_radius": 47,
                       "element_class": "static"})
    layers.append({"type": "TEXT", "name": "文本_排名",
                   "x": 0, "y": 25, "w": 95, "h": 45, "content": "1",
                   "font_size": 42, "font_weight": "Bold",
                   "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
                   "element_class": "dynamic"})
    return layers

COMP_PAIMING = {
    "name": "排名", "w": 95, "h": 95,
    "variant_property": "排名等级",
    "variants": [
        {"name": "金", "layers": rank_layers("金")},
        {"name": "银", "layers": rank_layers("银")},
        {"name": "铜", "layers": rank_layers("铜")},
        {"name": "普通", "is_default": True, "layers": rank_layers("普通")},
    ]
}

# ---------- 4. 头像 (2 variant: 带装饰/不带装饰) ----------
COMP_TOUXIANG = {
    "name": "头像", "w": 146, "h": 135,
    "variant_property": "装饰",
    "variants": [
        {"name": "带装饰",
         "layers": [
             {"type": "RECTANGLE", "name": "图片_头像",
              "x": 23, "y": 12, "w": 100, "h": 110, "element_class": "dynamic"},
             {"type": "RECTANGLE", "name": "图片_帘子装饰",
              "x": 0, "y": 0, "w": 146, "h": 135, "element_class": "dynamic"}
         ]},
        {"name": "不带装饰", "is_default": True,
         "layers": [
             {"type": "RECTANGLE", "name": "图片_头像",
              "x": 23, "y": 12, "w": 100, "h": 110, "element_class": "dynamic"}
         ]},
    ]
}

# ---------- 5. 装饰物前 (2 variant: 有/空) ----------
COMP_ZSWQ = {
    "name": "装饰物前", "w": 84, "h": 75,
    "variant_property": "状态",
    "variants": [
        {"name": "有",
         "layers": [
             {"type": "RECTANGLE", "name": "图片_装饰物前",
              "x": 0, "y": 0, "w": 84, "h": 75, "element_class": "dynamic"}
         ]},
        {"name": "空", "is_default": True, "layers": []},
    ]
}

# ---------- 6. 等级 (3 variant: Knight / GrandKnight / 空) ----------
def level_layers(variant):
    if variant == "空":
        return []
    content = "Knight" if variant == "Knight" else "Grand Knight"
    shield_cr = 5 if variant == "Knight" else 6
    return [
        {"type": "TEXT", "name": "文本_等级",
         "content": content, "x": 0, "y": 0, "w": 180, "h": 38,
         "font_size": 30, "font_weight": "Bold",
         "textAlignHorizontal": "LEFT", "textAlignVertical": "CENTER",
         "element_class": "dynamic"},
        {"type": "RECTANGLE", "name": "图片_盾",
         "x": 190, "y": 3, "w": 40, "h": 50,
         "corner_radius": shield_cr, "element_class": "dynamic"}
    ]

COMP_DENGJI = {
    "name": "等级", "w": 240, "h": 56,
    "variant_property": "等级",
    "variants": [
        {"name": "Knight", "layers": level_layers("Knight")},
        {"name": "GrandKnight", "layers": level_layers("GrandKnight")},
        {"name": "空", "is_default": True, "layers": []},
    ]
}

# ---------- 7. 装饰物后 (2 variant: 有/空) ----------
COMP_ZSWH = {
    "name": "装饰物后", "w": 157, "h": 113,
    "variant_property": "状态",
    "variants": [
        {"name": "有",
         "layers": [
             {"type": "RECTANGLE", "name": "图片_道具",
              "x": 0, "y": 12, "w": 90, "h": 90, "element_class": "dynamic"},
             {"type": "TEXT", "name": "文本_道具数",
              "x": 98, "y": 37, "w": 59, "h": 38, "content": "x2",
              "font_size": 30, "font_weight": "Bold",
              "textAlignHorizontal": "LEFT", "textAlignVertical": "CENTER",
              "element_class": "dynamic"}
         ]},
        {"name": "空", "is_default": True, "layers": []},
    ]
}

# ---------- 8. 收集物数量 (1 variant + dummy 凑 ≥2) ----------
COMP_SJWSL = {
    "name": "收集物数量", "w": 197, "h": 97,
    "variant_property": "状态",
    "variants": [
        {"name": "常态", "is_default": True,
         "layers": [
             {"type": "RECTANGLE", "name": "底板_收集物",
              "x": 0, "y": 18, "w": 197, "h": 60, "corner_radius": 30,
              "element_class": "static"},
             {"type": "RECTANGLE", "name": "图标_舵轮",
              "x": 0, "y": 0, "w": 95, "h": 97, "element_class": "static"},
             {"type": "TEXT", "name": "文本_数量",
              "x": 95, "y": 30, "w": 95, "h": 36, "content": "529",
              "font_size": 32, "font_weight": "Bold",
              "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
              "element_class": "dynamic"}
         ]},
        # dummy 第 2 variant 凑 ≥2 (combineAsVariants 要求)
        {"name": "变体2",
         "layers": [
             {"type": "RECTANGLE", "name": "底板_收集物",
              "x": 0, "y": 18, "w": 197, "h": 60, "corner_radius": 31,
              "element_class": "static"},
             {"type": "RECTANGLE", "name": "图标_舵轮",
              "x": 0, "y": 0, "w": 95, "h": 97, "element_class": "static"},
             {"type": "TEXT", "name": "文本_数量",
              "x": 95, "y": 30, "w": 95, "h": 36, "content": "529",
              "font_size": 32, "font_weight": "Bold",
              "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
              "element_class": "dynamic"}
         ]}
    ]
}

# ---------- 9. 列表项_排名 (2 variant: 常态/当前用户) ----------
# 内部含 6 子 ccb INSTANCE + 1 名字组 wrapper FRAME + 1 底板
def listitem_layers(main_variant):
    cr = 21 if main_variant == "当前用户" else 20
    return [
        {"type": "RECTANGLE", "name": "底板_列表项",
         "x": 0, "y": 0, "w": 1050, "h": 169, "corner_radius": cr,
         "layoutPositioning": "ABSOLUTE", "element_class": "static"},
        {"type": "INSTANCE", "name": "排名",
         "component_name": "排名", "variant": "普通",
         "x": 20, "y": 37, "w": 95, "h": 95},
        {"type": "INSTANCE", "name": "头像",
         "component_name": "头像", "variant": "不带装饰",
         "x": 130, "y": 17, "w": 146, "h": 135},
        {"type": "INSTANCE", "name": "装饰物前",
         "component_name": "装饰物前", "variant": "空",
         "x": 290, "y": 47, "w": 84, "h": 75},
        # 组_名字 wrapper (扁平 FRAME, 含 文本_玩家名 + 等级 INSTANCE)
        {"type": "FRAME", "name": "组_名字",
         "x": 385, "y": 28, "w": 280, "h": 113,
         "layoutMode": "VERTICAL",
         "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
         "primaryAxisAlignItems": "MIN", "counterAxisAlignItems": "MIN",
         "itemSpacing": 8,
         "children": [
             {"type": "TEXT", "name": "文本_玩家名",
              "content": "PLAYER_NAME", "w": 280, "h": 45,
              "font_size": 40, "font_weight": "Bold",
              "textAlignHorizontal": "LEFT", "textAlignVertical": "CENTER",
              "element_class": "dynamic"},
             {"type": "INSTANCE", "name": "等级",
              "component_name": "等级", "variant": "空",
              "w": 240, "h": 56}
         ]},
        {"type": "INSTANCE", "name": "装饰物后",
         "component_name": "装饰物后", "variant": "空",
         "x": 690, "y": 28, "w": 157, "h": 113},
        {"type": "INSTANCE", "name": "收集物数量",
         "component_name": "收集物数量", "variant": "常态",
         "x": 853, "y": 36, "w": 197, "h": 97}
    ]

COMP_LISTITEM = {
    "name": "列表项_排名", "w": 1050, "h": 169,
    "variant_property": "主状态",
    "variants": [
        {"name": "常态", "is_default": True, "layers": listitem_layers("常态")},
        {"name": "当前用户", "layers": listitem_layers("当前用户")},
    ]
}

# ============================================================
# 主屏构造
# ============================================================
def build_screen():
    layers = []

    # ① 顶 banner 区 (扁平 FRAME, 含 X 关闭手搓按钮)
    layers.append({
        "type": "FRAME", "name": "组_顶banner区",
        "x": 0, "y": 0, "w": 1080, "h": 281, "layoutMode": "NONE",
        "constraints": {"horizontal": "SCALE", "vertical": "TOP"},
        "children": [
            {"type": "RECTANGLE", "name": "底板_banner",
             "x": 0, "y": 0, "w": 1080, "h": 281, "element_class": "static",
             "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
            {"type": "TEXT", "name": "文本_标题",
             "x": 219, "y": 90, "w": 642, "h": 90, "content": "Team Treasure",
             "font_size": 70, "font_weight": "Bold",
             "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
             "element_class": "static",
             "constraints": {"horizontal": "CENTER", "vertical": "TOP"}},
            {"type": "FRAME", "name": "按钮_关闭",
             "x": 952, "y": 56, "w": 109, "h": 113, "layoutMode": "NONE",
             "constraints": {"horizontal": "RIGHT", "vertical": "TOP"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_关闭",
                  "x": 0, "y": 0, "w": 109, "h": 113, "corner_radius": 55,
                  "element_class": "static"}
             ]}
        ]
    })

    # ② 海盗装饰区
    layers.append({
        "type": "FRAME", "name": "组_海盗装饰",
        "x": 0, "y": 281, "w": 1080, "h": 694, "layoutMode": "NONE",
        "constraints": {"horizontal": "SCALE", "vertical": "TOP"},
        "children": [
            {"type": "RECTANGLE", "name": "图片_海盗主图",
             "x": 0, "y": 0, "w": 1080, "h": 600, "element_class": "dynamic",
             "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
            {"type": "FRAME", "name": "按钮_信息",
             "x": 40, "y": 0, "w": 91, "h": 94, "layoutMode": "NONE",
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_信息",
                  "x": 0, "y": 0, "w": 91, "h": 94, "corner_radius": 47,
                  "element_class": "static"}
             ]},
            {"type": "FRAME", "name": "组_时间徽章",
             "x": 358, "y": 559, "w": 365, "h": 135, "layoutMode": "NONE",
             "constraints": {"horizontal": "CENTER", "vertical": "TOP"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_时间徽章",
                  "x": 0, "y": 0, "w": 365, "h": 135, "corner_radius": 67,
                  "element_class": "static"},
                 {"type": "RECTANGLE", "name": "图标_沙漏",
                  "x": -10, "y": -10, "w": 130, "h": 155, "element_class": "static"},
                 {"type": "TEXT", "name": "文本_时间",
                  "x": 130, "y": 40, "w": 235, "h": 55, "content": "2d 1h",
                  "font_size": 48, "font_weight": "Bold",
                  "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
                  "element_class": "dynamic"}
             ]},
            {"type": "RECTANGLE", "name": "图片_装饰_金币堆",
             "x": 100, "y": 544, "w": 200, "h": 150, "element_class": "dynamic",
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"}}
        ]
    })

    # ③ Choisss 总进度行 (扁平 FRAME, 单实例不抽 ccb)
    layers.append({
        "type": "FRAME", "name": "组_Choisss总进度行",
        "x": 0, "y": 1013, "w": 1080, "h": 112,
        "layoutMode": "HORIZONTAL",
        "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "MIN", "counterAxisAlignItems": "CENTER",
        "itemSpacing": 15, "paddingLeft": 20, "paddingRight": 20,
        "constraints": {"horizontal": "SCALE", "vertical": "TOP"},
        "children": [
            {"type": "RECTANGLE", "name": "底板_Choisss行",
             "x": 0, "y": 0, "w": 1080, "h": 112, "corner_radius": 40,
             "layoutPositioning": "ABSOLUTE", "element_class": "static"},
            {"type": "FRAME", "name": "组_头像名",
             "w": 350, "h": 95, "layoutMode": "HORIZONTAL",
             "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
             "primaryAxisAlignItems": "MIN", "counterAxisAlignItems": "CENTER",
             "itemSpacing": 12,
             "children": [
                 {"type": "RECTANGLE", "name": "图片_盾头像",
                  "w": 95, "h": 95, "corner_radius": 12, "element_class": "dynamic"},
                 {"type": "TEXT", "name": "文本_玩家名_Choisss",
                  "content": "Choisss", "w": 243, "h": 60,
                  "font_size": 50, "font_weight": "Bold",
                  "textAlignHorizontal": "LEFT", "textAlignVertical": "CENTER",
                  "element_class": "dynamic"}
             ]},
            {"type": "FRAME", "name": "弹性缝隙",
             "w": 0, "h": 0, "layoutMode": "NONE", "layoutSizingHorizontal": "FILL"},
            {"type": "FRAME", "name": "组_数字进度",
             "w": 340, "h": 97, "layoutMode": "NONE",
             "children": [
                 {"type": "RECTANGLE", "name": "底板_数字进度",
                  "x": 80, "y": 18, "w": 260, "h": 60, "corner_radius": 30,
                  "element_class": "static"},
                 {"type": "RECTANGLE", "name": "图标_舵轮",
                  "x": 0, "y": 0, "w": 95, "h": 97, "element_class": "static"},
                 {"type": "TEXT", "name": "文本_总进度",
                  "x": 110, "y": 30, "w": 200, "h": 36, "content": "1906/5000",
                  "font_size": 32, "font_weight": "Bold",
                  "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
                  "element_class": "dynamic"}
             ]}
        ]
    })

    # ④ 进度条父 ccb (扁平 FRAME, 内含 INSTANCE 引用宝箱/状态)
    NODE_X = [55 + int(985*0.16), 55 + int(985*0.57), 55 + int(985*0.93)]
    layers.append({
        "type": "FRAME", "name": "组_进度条与宝箱",
        "x": 0, "y": 1125, "w": 1080, "h": 506, "layoutMode": "NONE",
        "constraints": {"horizontal": "SCALE", "vertical": "TOP"},
        "children": [
            {"type": "RECTANGLE", "name": "图标_进度起点",
             "x": 27, "y": 50, "w": 164, "h": 169, "element_class": "static",
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"}},
            {"type": "FRAME", "name": "组_进度_团队",
             "x": 55, "y": 100, "w": 985, "h": 75, "layoutMode": "NONE",
             "constraints": {"horizontal": "SCALE", "vertical": "TOP"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_团队",
                  "x": 0, "y": 0, "w": 985, "h": 75, "corner_radius": 37,
                  "element_class": "static"},
                 {"type": "RECTANGLE", "name": "进度条_团队",
                  "x": 10, "y": 10, "w": 965, "h": 55, "corner_radius": 27,
                  "element_class": "static"}
             ]},
            # 3 宝箱 INSTANCE
            {"type": "INSTANCE", "name": "宝箱", "component_name": "宝箱", "variant": "金",
             "x": NODE_X[0]-82, "y": 80, "w": 164, "h": 188,
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"}},
            {"type": "INSTANCE", "name": "宝箱", "component_name": "宝箱", "variant": "银",
             "x": NODE_X[1]-82, "y": 80, "w": 164, "h": 188,
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"}},
            {"type": "INSTANCE", "name": "宝箱", "component_name": "宝箱", "variant": "铜",
             "x": NODE_X[2]-82, "y": 80, "w": 164, "h": 188,
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"}},
            # 3 状态 INSTANCE
            {"type": "INSTANCE", "name": "状态", "component_name": "状态", "variant": "已完成",
             "x": NODE_X[0]-82, "y": 315, "w": 164, "h": 113,
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"}},
            {"type": "INSTANCE", "name": "状态", "component_name": "状态", "variant": "未完成",
             "x": NODE_X[1]-82, "y": 315, "w": 164, "h": 113,
             "overrides": {"文本_状态_数字": "3000"},
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"}},
            {"type": "INSTANCE", "name": "状态", "component_name": "状态", "variant": "未完成",
             "x": NODE_X[2]-82, "y": 315, "w": 164, "h": 113,
             "overrides": {"文本_状态_数字": "5000"},
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"}}
        ]
    })

    # ⑤ 列表滚动区 (内含 13 个 列表项_排名 INSTANCE)
    list_instances = []
    for u in USERS:
        rank_num, name, level, db, da, av, count, main_var = u
        list_instances.append({
            "type": "INSTANCE", "name": f"列表项_{rank_num}",
            "component_name": "列表项_排名",
            "variant": main_var,
            "x": 15, "y": 0, "w": 1050, "h": 169,
            "overrides": {
                "排名": rank_variant(rank_num),
                "头像": av,
                "装饰物前": db,
                "装饰物后": da,
                "等级": level,
                "文本_玩家名": name,
                "文本_排名": str(rank_num),
                "文本_数量": count
            }
        })

    layers.append({
        "type": "FRAME", "name": "容器_列表滚动区",
        "x": 0, "y": 1650, "w": 1080, "h": 750,
        "layoutMode": "VERTICAL",
        "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "MIN", "counterAxisAlignItems": "MIN",
        "clip_content": True, "overflow": "VERTICAL",
        "constraints": {"horizontal": "SCALE", "vertical": "SCALE"},
        "children": [
            {"type": "FRAME", "name": "组_滚动内容",
             "layoutMode": "VERTICAL",
             "primaryAxisSizingMode": "AUTO", "counterAxisSizingMode": "FIXED",
             "layoutSizingHorizontal": "FIXED", "layoutSizingVertical": "HUG",
             "primaryAxisAlignItems": "MIN", "counterAxisAlignItems": "MIN",
             "itemSpacing": 18, "paddingLeft": 15, "paddingRight": 15, "w": 1080,
             "children": list_instances}
        ]
    })

    return layers

# ============================================================
# 主屏 + components 数组组装
# ============================================================
final_scene = {
    "screens": [
        {
            "name": "界面_Team_Treasure",
            "type": "FRAME",
            "w": 1080, "h": 2400,
            "layoutMode": "NONE",
            "flow": [],
            "layers": build_screen()
        }
    ],
    # 顺序: 子在前, 外层(列表项_排名)在后
    "components": [
        COMP_BAOXIANG,
        COMP_ZHUANGTAI,
        COMP_PAIMING,
        COMP_TOUXIANG,
        COMP_ZSWQ,
        COMP_DENGJI,
        COMP_ZSWH,
        COMP_SJWSL,
        COMP_LISTITEM,
    ]
}

# 给所有 layer 自动加 element_class (兜底)
for s in final_scene['screens']:
    for L in s['layers']: add_element_class(L)
for c in final_scene['components']:
    for v in c['variants']:
        for L in v.get('layers',[]): add_element_class(L)

with open('final_scene.json', 'w', encoding='utf-8') as f:
    json.dump(final_scene, f, ensure_ascii=False, indent=2)

import os
print(f"✅ final_scene.json 生成完毕")
print(f"   屏幕数: {len(final_scene['screens'])}")
print(f"   components 数: {len(final_scene['components'])}")
for c in final_scene['components']:
    print(f"     - {c['name']} ({c['w']}×{c['h']}, {len(c['variants'])} Variants: {', '.join(v['name'] for v in c['variants'])})")
print(f"   文件大小: {os.path.getsize('final_scene.json')/1024:.1f} KB")
