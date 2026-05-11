#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S4+S5: 生成 Shop 视频的扁平 scene.json
3 个屏幕:
  1. 界面_Shop_视图A (含小卡片 + More Offers! + 底部导航)
  2. 界面_Shop_视图B (3 张大卡片,2 层嵌套测试目标)
  3. 界面_主菜单    (Piano 房间过渡帧, 简化骨架)

Layer 2 嵌套结构(主要在视图B):
  金币购买卡片 (Layer 1)
   └── 道具数量徽章 (Layer 2: 图标_道具 + 文本_数量)  × 4 / 卡片
   └── 限时道具图标 (Layer 2: 图_道具 + 文本_时长)    × 3 / 卡片
"""
import json

OUT_PATH = '/Users/red/Desktop/component_extractor/scene_flat.json'


# ========== Layer 2 模板: 道具数量徽章 (图标 + ×N) ==========
# 4 种道具用不同 fill 表达视觉差异 (引擎里的 4 条独立时间线)
# 这样阶段二算法 wrapper_signature 会分裂出 4 个 Variant
ITEM_FILL_COLORS = {
    'royal':  '#9b6dff',   # 王冠装饰宝箱 紫
    'cannon': '#d54a3a',   # 大炮 红
    'hammer': '#3da8e0',   # 锤子 蓝
    'joker':  '#f0b419',   # 小丑帽 黄
}


def make_item_badge(idx, x, y, count_text, item_kind):
    """
    idx 用于实例命名区分(不影响结构指纹).
    item_kind 决定 inner RECT 的 fill 颜色 → 触发 wrapper_signature 分裂 → 4 Variant.
    """
    return {
        "type": "FRAME", "name": f"道具数量徽章_{idx}",
        "x": x, "y": y, "w": 110, "h": 100,
        "layoutMode": "NONE",
        "constraints": {"horizontal": "LEFT", "vertical": "TOP"},
        "children": [
            {"type": "RECTANGLE", "name": "图_道具",
             "x": 0, "y": 0, "w": 80, "h": 80, "corner_radius": 15,
             "fill": ITEM_FILL_COLORS[item_kind],
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"}},
            {"type": "TEXT", "name": "文本_数量",
             "x": 75, "y": 60, "content": count_text,
             "font_size": 32, "font_weight": "Bold",
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"}}
        ]
    }


# ========== Layer 2 模板: 限时道具图标 (图标 + ∞/时长) ==========
# 3 种限时道具,不同 fill 表达视觉差异 → 3 Variant
TIMED_FILL_COLORS = {
    'mushroom': '#7d4dbf',  # 紫蘑菇炸弹
    'tnt':      '#cc3a2e',  # 红色 TNT
    'topspin':  '#3a6dd9',  # 红蓝陀螺 (主色蓝)
}


def make_timed_item(idx, x, y, time_text, item_kind):
    return {
        "type": "FRAME", "name": f"限时道具_{idx}",
        "x": x, "y": y, "w": 110, "h": 100,
        "layoutMode": "NONE",
        "constraints": {"horizontal": "LEFT", "vertical": "TOP"},
        "children": [
            {"type": "RECTANGLE", "name": "图_限时",
             "x": 0, "y": 0, "w": 90, "h": 80, "corner_radius": 15,
             "fill": TIMED_FILL_COLORS[item_kind],
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"}},
            {"type": "TEXT", "name": "文本_时长",
             "x": 30, "y": 80, "content": time_text,
             "font_size": 28, "font_weight": "Bold",
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"}}
        ]
    }


# ========== Layer 1 模板: 金币购买卡片 ==========
def make_coin_card(coin_amount, item_counts, time_texts, label, price, has_popular, x, y):
    """
    生成一张大卡片 FRAME
    item_counts: ["x1","x1","x1","x1"] 等 4 个元素
    time_texts:  ["1h","∞","∞"] 等 3 个元素
    has_popular: 10000 卡片才有 'Popular' 角标
    """
    card_w, card_h = 1020, 360
    children = [
        # 卡片底板
        {"type": "RECTANGLE", "name": "底板_卡片",
         "x": 0, "y": 0, "w": card_w, "h": card_h, "corner_radius": 30,
         "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
        # 金币堆图
        {"type": "RECTANGLE", "name": "图_金币堆",
         "x": 30, "y": 30, "w": 220, "h": 200, "corner_radius": 0,
         "constraints": {"horizontal": "LEFT", "vertical": "TOP"}},
        # 金币数字
        {"type": "TEXT", "name": "文本_金额",
         "x": 90, "y": 230, "content": str(coin_amount),
         "font_size": 60, "font_weight": "Bold", "textAlignHorizontal": "CENTER",
         "constraints": {"horizontal": "LEFT", "vertical": "TOP"}},
    ]

    # 4 个 道具数量徽章 (2x2 网格)
    # 4 种道具固定顺序: 王冠/大炮/锤子/小丑 → 4 个不同 Variant
    badge_kinds = ['royal', 'cannon', 'hammer', 'joker']
    badge_xs = [320, 440]
    badge_ys = [40, 150]
    positions = [(x, y) for y in badge_ys for x in badge_xs]
    for i, (bx, by) in enumerate(positions):
        children.append(make_item_badge(i+1, bx, by, item_counts[i], badge_kinds[i]))

    # 3 个 限时道具 (横排, 3 种道具固定顺序: 蘑菇/TNT/陀螺 → 3 个 Variant)
    timed_kinds = ['mushroom', 'tnt', 'topspin']
    for i, tx in enumerate([620, 750, 880]):
        children.append(make_timed_item(i+1, tx, 80, time_texts[i], timed_kinds[i]))

    # 价格条(底部)
    children.append({
        "type": "RECTANGLE", "name": "底板_价格条",
        "x": 0, "y": 280, "w": card_w, "h": 80,
        "constraints": {"horizontal": "SCALE", "vertical": "BOTTOM"}
    })
    children.append({
        "type": "TEXT", "name": "文本_标签",
        "x": 30, "y": 305, "content": label,
        "font_size": 40, "font_weight": "Bold",
        "constraints": {"horizontal": "LEFT", "vertical": "BOTTOM"}
    })
    children.append({
        "type": "FRAME", "name": "按钮_价格",
        "x": 720, "y": 290, "w": 280, "h": 60,
        "layoutMode": "NONE",
        "constraints": {"horizontal": "RIGHT", "vertical": "BOTTOM"},
        "children": [
            {"type": "RECTANGLE", "name": "底板_价格按钮",
             "x": 0, "y": 0, "w": 280, "h": 60, "corner_radius": 30,
             "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
            {"type": "TEXT", "name": "文本_价格",
             "x": 80, "y": 15, "content": price,
             "font_size": 36, "font_weight": "Bold", "textAlignHorizontal": "CENTER",
             "constraints": {"horizontal": "CENTER", "vertical": "CENTER"}}
        ]
    })

    # Popular 角标
    children.append({
        "type": "FRAME", "name": "角标_Popular",
        "x": -10, "y": -10, "w": 130, "h": 50,
        "layoutMode": "NONE",
        "visible": has_popular,
        "constraints": {"horizontal": "LEFT", "vertical": "TOP"},
        "children": [
            {"type": "RECTANGLE", "name": "底板_角标",
             "x": 0, "y": 0, "w": 130, "h": 50, "corner_radius": 8,
             "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
            {"type": "TEXT", "name": "文本_角标",
             "x": 30, "y": 10, "content": "Popular",
             "font_size": 28, "font_weight": "Bold",
             "constraints": {"horizontal": "CENTER", "vertical": "CENTER"}}
        ]
    })

    return {
        "type": "FRAME", "name": f"金币购买卡片_{coin_amount}",
        "x": x, "y": y, "w": card_w, "h": card_h,
        "layoutMode": "NONE",
        "constraints": {"horizontal": "SCALE", "vertical": "TOP"},
        "children": children,
    }


# ========== 顶部 HUD (3 屏共用) ==========
def make_top_hud():
    return {
        "type": "FRAME", "name": "组_顶部HUD",
        "x": 0, "y": 138, "w": 1080, "h": 222,
        "layoutMode": "NONE",
        "constraints": {"horizontal": "SCALE", "vertical": "TOP"},
        "children": [
            {"type": "RECTANGLE", "name": "底板_HUD",
             "x": 0, "y": 0, "w": 1080, "h": 222,
             "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
            # 金币栏
            {"type": "FRAME", "name": "按钮_金币栏",
             "x": 30, "y": 80, "w": 220, "h": 90,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "LEFT", "vertical": "CENTER"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_金币栏",
                  "x": 0, "y": 0, "w": 220, "h": 90, "corner_radius": 45,
                  "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
                 {"type": "TEXT", "name": "文本_金币",
                  "x": 80, "y": 25, "content": "1107",
                  "font_size": 42, "font_weight": "Bold",
                  "constraints": {"horizontal": "LEFT", "vertical": "CENTER"}}
             ]},
            # Shop 标题
            {"type": "FRAME", "name": "组_标题",
             "x": 350, "y": 60, "w": 380, "h": 130,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "CENTER", "vertical": "CENTER"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_标题",
                  "x": 0, "y": 0, "w": 380, "h": 130, "corner_radius": 65,
                  "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
                 {"type": "TEXT", "name": "文本_标题",
                  "x": 80, "y": 30, "content": "Shop",
                  "font_size": 70, "font_weight": "Bold", "textAlignHorizontal": "CENTER",
                  "constraints": {"horizontal": "CENTER", "vertical": "CENTER"}}
             ]},
            # X 关闭按钮
            {"type": "FRAME", "name": "按钮_关闭",
             "x": 920, "y": 60, "w": 130, "h": 130,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "RIGHT", "vertical": "CENTER"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_关闭",
                  "x": 0, "y": 0, "w": 130, "h": 130, "corner_radius": 65,
                  "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}}
             ]}
        ]
    }


# ========== Royal Pass 卡片 (3 屏共用,简化) ==========
def make_royal_pass():
    return {
        "type": "FRAME", "name": "组_RoyalPass",
        "x": 30, "y": 380, "w": 1020, "h": 720,
        "layoutMode": "NONE",
        "constraints": {"horizontal": "SCALE", "vertical": "TOP"},
        "children": [
            {"type": "RECTANGLE", "name": "底板_RoyalPass",
             "x": 0, "y": 0, "w": 1020, "h": 720, "corner_radius": 30,
             "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
            {"type": "TEXT", "name": "文本_标题",
             "x": 60, "y": 50, "content": "Royal Pass",
             "font_size": 60, "font_weight": "Bold",
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"}},
            {"type": "RECTANGLE", "name": "图_宝箱",
             "x": 50, "y": 150, "w": 500, "h": 500,
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"}},
            {"type": "FRAME", "name": "按钮_Activate",
             "x": 600, "y": 500, "w": 380, "h": 120,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "RIGHT", "vertical": "BOTTOM"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_Activate",
                  "x": 0, "y": 0, "w": 380, "h": 120, "corner_radius": 60,
                  "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
                 {"type": "TEXT", "name": "文本_Activate",
                  "x": 100, "y": 35, "content": "Activate",
                  "font_size": 48, "font_weight": "Bold",
                  "constraints": {"horizontal": "CENTER", "vertical": "CENTER"}}
             ]}
        ]
    }


# ========== 视图A 屏幕 (紧凑版: 含小卡片 + More Offers!) ==========
def make_screen_view_a():
    return {
        "name": "界面_Shop_视图A",
        "w": 1080, "h": 2400,
        "layers": [
            make_top_hud(),
            make_royal_pass(),
            # 大卡片 #1 (2000 + Special Offer)
            make_coin_card(2000, ["x1","x1","x1","x1"], ["1h","∞","∞"],
                            "Special Offer", "£1.99", False, 30, 1130),
            # 3 张小金币卡片 (横排,简化为占位 FRAME)
            {"type": "FRAME", "name": "小卡_1000",
             "x": 30, "y": 1530, "w": 320, "h": 380,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_小卡",
                  "x": 0, "y": 0, "w": 320, "h": 380, "corner_radius": 30,
                  "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
                 {"type": "TEXT", "name": "文本_金额",
                  "x": 100, "y": 200, "content": "1000",
                  "font_size": 48, "font_weight": "Bold",
                  "constraints": {"horizontal": "CENTER", "vertical": "CENTER"}}
             ]},
            {"type": "FRAME", "name": "小卡_5000",
             "x": 380, "y": 1530, "w": 320, "h": 380,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_小卡",
                  "x": 0, "y": 0, "w": 320, "h": 380, "corner_radius": 30,
                  "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
                 {"type": "TEXT", "name": "文本_金额",
                  "x": 100, "y": 200, "content": "5000",
                  "font_size": 48, "font_weight": "Bold",
                  "constraints": {"horizontal": "CENTER", "vertical": "CENTER"}}
             ]},
            {"type": "FRAME", "name": "小卡_10000",
             "x": 730, "y": 1530, "w": 320, "h": 380,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_小卡",
                  "x": 0, "y": 0, "w": 320, "h": 380, "corner_radius": 30,
                  "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
                 {"type": "TEXT", "name": "文本_金额",
                  "x": 90, "y": 200, "content": "10000",
                  "font_size": 48, "font_weight": "Bold",
                  "constraints": {"horizontal": "CENTER", "vertical": "CENTER"}}
             ]},
            # More Offers! 按钮
            {"type": "FRAME", "name": "按钮_MoreOffers",
             "x": 320, "y": 2060, "w": 440, "h": 100,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "CENTER", "vertical": "BOTTOM"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_MoreOffers",
                  "x": 0, "y": 0, "w": 440, "h": 100, "corner_radius": 50,
                  "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
                 {"type": "TEXT", "name": "文本_MoreOffers",
                  "x": 90, "y": 30, "content": "More Offers!",
                  "font_size": 40, "font_weight": "Bold",
                  "constraints": {"horizontal": "CENTER", "vertical": "CENTER"}}
             ]},
            # 底部导航 (5 项, 简化为占位)
            {"type": "FRAME", "name": "组_底部导航",
             "x": 0, "y": 2200, "w": 1080, "h": 200,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "SCALE", "vertical": "BOTTOM"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_导航",
                  "x": 0, "y": 0, "w": 1080, "h": 200,
                  "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}}
             ]}
        ]
    }


# ========== 视图B 屏幕 (展开版: 3 张大卡片) ==========
def make_screen_view_b():
    return {
        "name": "界面_Shop_视图B",
        "w": 1080, "h": 2400,
        "layers": [
            make_top_hud(),
            make_royal_pass(),
            # 大卡片 #1 (2000 + Special Offer)
            make_coin_card(2000, ["x1","x1","x1","x1"], ["1h","∞","∞"],
                            "Special Offer", "£1.99", False, 30, 1130),
            # 大卡片 #2 (5000 + Prince's Treasure)
            make_coin_card(5000, ["x1","x1","x1","x1"], ["1h","∞","∞"],
                            "Prince's Treasure", "£9.99", False, 30, 1530),
            # 大卡片 #3 (10000 + Queen's Treasure + Popular 角标)
            make_coin_card(10000, ["x2","x2","x2","x2"], ["12h","∞","∞"],
                            "Queen's Treasure", "£19.99", True, 30, 1930),
        ]
    }


# ========== 主菜单屏幕 (简化骨架) ==========
def make_screen_main_menu():
    return {
        "name": "界面_主菜单",
        "w": 1080, "h": 2400,
        "layers": [
            {"type": "RECTANGLE", "name": "背景_钢琴房",
             "x": 0, "y": 0, "w": 1080, "h": 2400,
             "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
            # HUD 进度条
            {"type": "FRAME", "name": "组_顶部HUD",
             "x": 0, "y": 138, "w": 1080, "h": 220,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "SCALE", "vertical": "TOP"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_HUD",
                  "x": 0, "y": 0, "w": 1080, "h": 220,
                  "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}}
             ]},
            # 底部 Level / Area 按钮
            {"type": "FRAME", "name": "组_底部按钮",
             "x": 30, "y": 1900, "w": 1020, "h": 220,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "SCALE", "vertical": "BOTTOM"},
             "children": [
                 {"type": "FRAME", "name": "按钮_Level",
                  "x": 0, "y": 0, "w": 480, "h": 200,
                  "layoutMode": "NONE",
                  "constraints": {"horizontal": "LEFT", "vertical": "TOP"},
                  "children": [
                      {"type": "RECTANGLE", "name": "底板_Level",
                       "x": 0, "y": 0, "w": 480, "h": 200, "corner_radius": 100,
                       "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
                      {"type": "TEXT", "name": "文本_Level",
                       "x": 100, "y": 60, "content": "Level 537",
                       "font_size": 60, "font_weight": "Bold",
                       "constraints": {"horizontal": "CENTER", "vertical": "CENTER"}}
                  ]},
                 {"type": "FRAME", "name": "按钮_Area",
                  "x": 540, "y": 0, "w": 480, "h": 200,
                  "layoutMode": "NONE",
                  "constraints": {"horizontal": "RIGHT", "vertical": "TOP"},
                  "children": [
                      {"type": "RECTANGLE", "name": "底板_Area",
                       "x": 0, "y": 0, "w": 480, "h": 200, "corner_radius": 100,
                       "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
                      {"type": "TEXT", "name": "文本_Area",
                       "x": 130, "y": 60, "content": "Area 19",
                       "font_size": 60, "font_weight": "Bold",
                       "constraints": {"horizontal": "CENTER", "vertical": "CENTER"}}
                  ]}
             ]},
            # 底部导航
            {"type": "FRAME", "name": "组_底部导航",
             "x": 0, "y": 2200, "w": 1080, "h": 200,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "SCALE", "vertical": "BOTTOM"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_导航",
                  "x": 0, "y": 0, "w": 1080, "h": 200,
                  "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}}
             ]}
        ]
    }


# ========== 顶层 (B 方案: 删视图A,只保留视图B + 主菜单) ==========
# 视图B 改名为 界面_Shop (合并)
view_b = make_screen_view_b()
view_b['name'] = '界面_Shop'

scene = {
    "screens": [
        view_b,
        make_screen_main_menu(),
    ],
    "flow": [
        {"from": "界面_Shop", "from_node": "按钮_关闭",
         "to": "界面_主菜单", "trigger": "ON_CLICK", "animation": "dissolve 300ms"},
        {"from": "界面_主菜单", "from_node": "(来源未确认)",
         "to": "界面_Shop", "trigger": "ON_CLICK", "animation": "dissolve 300ms"},
    ]
}

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(scene, f, ensure_ascii=False, indent=2)

print(f"✅ 输出: {OUT_PATH}")
print(f"   屏幕数: {len(scene['screens'])}")
for s in scene['screens']:
    print(f"     • {s['name']}: {len(s['layers'])} 顶层 layer")
print(f"   flow: {len(scene['flow'])} 条")
