#!/usr/bin/env python3
"""
S7 阶段构造 scene.json (扁平 FRAME, 无 INSTANCE 节点, 无 components[]).
严格遵守 07a/07b/07c/07d/07e 所有铁律.
用户锁定: 2 父 ccb + 8 子 ccb, 见 S6 表 H + s6_coverage.json.
"""
import json

# ============================================================
# 列表数据 (frame_00-25 观察值, scale_y = 1.875)
# ============================================================
USERS = [
    # (排名, 名字, 等级variant, 装饰前variant, 装饰后variant, 头像variant, 收集物数, 主variant)
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

# 列表项常量(目标坐标 1080×2400, 完整子节点闸: 外侧约束, 内部不写)
ROW_H = 169
ROW_PADDING_X = 15
ROW_W = 1080 - 2*ROW_PADDING_X  # 1050

# ============================================================
# 排名 子 ccb (4 variant 金/银/铜/普通) — children 100% 一致, visible 切换
# ============================================================
def build_rank(rank_num, variant):
    """variant in {金, 银, 铜, 普通}"""
    show_gold   = variant == "金"
    show_silver = variant == "银"
    show_bronze = variant == "铜"
    return {
        "type": "FRAME", "name": "排名",
        "w": 95, "h": 95, "layoutMode": "NONE",
        "children": [
            {"type": "RECTANGLE", "name": "底板_排名_金",
             "x": 0, "y": 0, "w": 95, "h": 95, "corner_radius": 47,
             "visible": show_gold},
            {"type": "RECTANGLE", "name": "底板_排名_银",
             "x": 0, "y": 0, "w": 95, "h": 95, "corner_radius": 47,
             "visible": show_silver},
            {"type": "RECTANGLE", "name": "底板_排名_铜",
             "x": 0, "y": 0, "w": 95, "h": 95, "corner_radius": 47,
             "visible": show_bronze},
            {"type": "TEXT", "name": "文本_排名",
             "x": 0, "y": 25, "h": 45, "content": str(rank_num),
             "font_size": 42, "font_weight": "Bold",
             "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"}
        ]
    }

def rank_variant(rank_num):
    if rank_num == 1: return "金"
    if rank_num == 2: return "银"
    if rank_num == 3: return "铜"
    return "普通"

# ============================================================
# 头像 子 ccb (2 variant: 带装饰/不带装饰)
# ============================================================
def build_avatar(variant):
    """variant in {带装饰, 不带装饰}"""
    show_decor = variant == "带装饰"
    return {
        "type": "FRAME", "name": "头像",
        "w": 146, "h": 135, "layoutMode": "NONE",
        "children": [
            {"type": "RECTANGLE", "name": "图片_头像",
             "x": 23, "y": 12, "w": 100, "h": 110},
            {"type": "RECTANGLE", "name": "图片_帘子装饰",
             "x": 0, "y": 0, "w": 146, "h": 135,
             "visible": show_decor}
        ]
    }

# ============================================================
# 装饰物前 子 ccb (2 variant: 有/空) — wrapper visible 切换
# ============================================================
def build_decor_before(variant):
    """variant in {有, 空}"""
    show = variant == "有"
    return {
        "type": "FRAME", "name": "装饰物前",
        "w": 84, "h": 75, "layoutMode": "NONE",
        "visible": show,
        "children": [
            {"type": "RECTANGLE", "name": "图片_装饰物前",
             "x": 0, "y": 0, "w": 84, "h": 75}
        ]
    }

# ============================================================
# 等级 子 ccb (3 variant: Knight/GrandKnight/空)
# 文本内容差异 + 用 corner_radius 微差让 S11 切出 3 Variant
# ============================================================
def build_level(variant):
    """variant in {Knight, GrandKnight, 空}"""
    show_wrapper = variant != "空"
    content = "Knight" if variant == "Knight" else ("Grand Knight" if variant == "GrandKnight" else "")
    # corner_radius 微差 (让 S11 切出 Knight vs GrandKnight)
    shield_cr = 5 if variant == "Knight" else 6
    return {
        "type": "FRAME", "name": "等级",
        "w": 240, "h": 56,
        "layoutMode": "HORIZONTAL",
        "primaryAxisSizingMode": "FIXED",
        "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "MIN",
        "counterAxisAlignItems": "CENTER",
        "itemSpacing": 10,
        "visible": show_wrapper,
        "children": [
            {"type": "TEXT", "name": "文本_等级",
             "content": content, "h": 38,
             "font_size": 30, "font_weight": "Bold",
             "textAlignHorizontal": "LEFT", "textAlignVertical": "CENTER"},
            {"type": "RECTANGLE", "name": "图片_盾",
             "w": 40, "h": 50, "corner_radius": shield_cr}
        ]
    }

# ============================================================
# 装饰物后 子 ccb (2 variant: 有/空)
# ============================================================
def build_decor_after(variant):
    """variant in {有, 空}"""
    show = variant == "有"
    return {
        "type": "FRAME", "name": "装饰物后",
        "w": 157, "h": 113,
        "layoutMode": "HORIZONTAL",
        "primaryAxisSizingMode": "FIXED",
        "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "MIN",
        "counterAxisAlignItems": "CENTER",
        "itemSpacing": 8,
        "visible": show,
        "children": [
            {"type": "RECTANGLE", "name": "图片_道具",
             "w": 90, "h": 90},
            {"type": "TEXT", "name": "文本_道具数",
             "content": "x2", "h": 38,
             "font_size": 30, "font_weight": "Bold",
             "textAlignHorizontal": "LEFT", "textAlignVertical": "CENTER"}
        ]
    }

# ============================================================
# 收集物数量 子 ccb (1 variant, 底板+icon+文本)
# ============================================================
def build_collect(count):
    return {
        "type": "FRAME", "name": "收集物数量",
        "w": 197, "h": 97, "layoutMode": "NONE",
        "children": [
            {"type": "RECTANGLE", "name": "底板_收集物",
             "x": 0, "y": 18, "w": 197, "h": 60, "corner_radius": 30},
            {"type": "RECTANGLE", "name": "图标_舵轮",
             "x": 0, "y": 0, "w": 95, "h": 97},
            {"type": "TEXT", "name": "文本_数量",
             "x": 95, "y": 30, "w": 95, "h": 36, "content": str(count),
             "font_size": 32, "font_weight": "Bold",
             "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"}
        ]
    }

# ============================================================
# 组_名字 wrapper (VERTICAL): 名字 TEXT + 等级 子 ccb
# ============================================================
def build_name_group(user_name, level_variant):
    return {
        "type": "FRAME", "name": "组_名字",
        "w": 280, "h": 113,
        "layoutMode": "VERTICAL",
        "primaryAxisSizingMode": "FIXED",
        "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "MIN",
        "counterAxisAlignItems": "MIN",
        "itemSpacing": 8,
        "children": [
            {"type": "TEXT", "name": "文本_玩家名",
             "content": user_name, "h": 45,
             "font_size": 40, "font_weight": "Bold",
             "textAlignHorizontal": "LEFT", "textAlignVertical": "CENTER"},
            build_level(level_variant)
        ]
    }

# ============================================================
# 列表项 父 ccb (2 variant: 常态/当前用户)
# ============================================================
def build_list_row(user):
    rank, name, level, decor_before, decor_after, avatar, count, main_variant = user
    # 主 variant 视觉差异: 底板 corner_radius 微差
    row_cr = 21 if main_variant == "当前用户" else 20
    return {
        "type": "FRAME", "name": f"列表项_排名{rank}",
        "w": ROW_W, "h": ROW_H,
        "layoutMode": "HORIZONTAL",
        "primaryAxisSizingMode": "FIXED",
        "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "MIN",
        "counterAxisAlignItems": "CENTER",
        "itemSpacing": 12,
        "paddingLeft": 20, "paddingRight": 20,
        "children": [
            # 底板用 ABSOLUTE 脱离 AL 流, 在 children[0]
            {"type": "RECTANGLE", "name": "底板_列表项",
             "x": 0, "y": 0, "w": ROW_W, "h": ROW_H,
             "corner_radius": row_cr,
             "layoutPositioning": "ABSOLUTE"},
            build_rank(rank, rank_variant(rank)),
            build_avatar(avatar),
            build_decor_before(decor_before),
            build_name_group(name, level),
            build_decor_after(decor_after),
            build_collect(count)
        ]
    }

# ============================================================
# 顶部固定区
# ============================================================
def build_top_banner():
    """顶 banner 区 — 木质拱底 + 标题 + X 关闭"""
    return {
        "type": "FRAME", "name": "组_顶banner区",
        "x": 0, "y": 0, "w": 1080, "h": 281,
        "layoutMode": "NONE",
        "constraints": {"horizontal": "SCALE", "vertical": "TOP"},
        "children": [
            {"type": "RECTANGLE", "name": "底板_banner",
             "x": 0, "y": 0, "w": 1080, "h": 281,
             "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
            {"type": "TEXT", "name": "文本_标题",
             "x": 219, "y": 90, "h": 90, "content": "Team Treasure",
             "font_size": 70, "font_weight": "Bold",
             "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
             "constraints": {"horizontal": "CENTER", "vertical": "TOP"}},
            {"type": "FRAME", "name": "按钮_关闭",
             "x": 952, "y": 56, "w": 109, "h": 113,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "RIGHT", "vertical": "TOP"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_关闭",
                  "x": 0, "y": 0, "w": 109, "h": 113, "corner_radius": 55}
             ]}
        ]
    }

def build_pirate_decor():
    """海盗装饰区 — NONE 自由布局"""
    return {
        "type": "FRAME", "name": "组_海盗装饰",
        "x": 0, "y": 281, "w": 1080, "h": 694,
        "layoutMode": "NONE",
        "constraints": {"horizontal": "SCALE", "vertical": "TOP"},
        "children": [
            {"type": "RECTANGLE", "name": "图片_海盗主图",
             "x": 0, "y": 0, "w": 1080, "h": 600,
             "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
            {"type": "FRAME", "name": "按钮_信息",
             "x": 40, "y": 0, "w": 91, "h": 94,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_信息",
                  "x": 0, "y": 0, "w": 91, "h": 94, "corner_radius": 47}
             ]},
            {"type": "FRAME", "name": "组_时间徽章",
             "x": 358, "y": 559, "w": 365, "h": 135,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "CENTER", "vertical": "TOP"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_时间徽章",
                  "x": 0, "y": 0, "w": 365, "h": 135, "corner_radius": 67},
                 {"type": "RECTANGLE", "name": "图标_沙漏",
                  "x": -10, "y": -10, "w": 130, "h": 155},
                 {"type": "TEXT", "name": "文本_时间",
                  "x": 130, "y": 40, "h": 55, "content": "2d 1h",
                  "font_size": 48, "font_weight": "Bold",
                  "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"}
             ]},
            {"type": "RECTANGLE", "name": "图片_装饰_金币堆",
             "x": 100, "y": 544, "w": 200, "h": 150,
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"}}
        ]
    }

def build_choisss_row():
    """Choisss 总进度行 HORIZONTAL + 弹性缝隙"""
    return {
        "type": "FRAME", "name": "组_Choisss总进度行",
        "x": 0, "y": 1013, "w": 1080, "h": 112,
        "layoutMode": "HORIZONTAL",
        "primaryAxisSizingMode": "FIXED",
        "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "MIN",
        "counterAxisAlignItems": "CENTER",
        "itemSpacing": 15,
        "paddingLeft": 20, "paddingRight": 20,
        "constraints": {"horizontal": "SCALE", "vertical": "TOP"},
        "children": [
            # ABSOLUTE 底板
            {"type": "RECTANGLE", "name": "底板_Choisss行",
             "x": 0, "y": 0, "w": 1080, "h": 112, "corner_radius": 40,
             "layoutPositioning": "ABSOLUTE"},
            # 头像名 wrapper
            {"type": "FRAME", "name": "组_头像名",
             "w": 350, "h": 95,
             "layoutMode": "HORIZONTAL",
             "primaryAxisSizingMode": "FIXED",
             "counterAxisSizingMode": "FIXED",
             "primaryAxisAlignItems": "MIN",
             "counterAxisAlignItems": "CENTER",
             "itemSpacing": 12,
             "children": [
                 {"type": "RECTANGLE", "name": "图片_盾头像",
                  "w": 95, "h": 95, "corner_radius": 12},
                 {"type": "TEXT", "name": "文本_玩家名_Choisss",
                  "content": "Choisss", "h": 60,
                  "font_size": 50, "font_weight": "Bold",
                  "textAlignHorizontal": "LEFT", "textAlignVertical": "CENTER"}
             ]},
            # 弹性缝隙
            {"type": "FRAME", "name": "弹性缝隙",
             "w": 0, "h": 0, "layoutMode": "NONE",
             "layoutSizingHorizontal": "FILL"},
            # 数字组 wrapper (横排徽章: 底板+icon+文本)
            {"type": "FRAME", "name": "组_数字进度",
             "w": 340, "h": 97, "layoutMode": "NONE",
             "children": [
                 {"type": "RECTANGLE", "name": "底板_数字进度",
                  "x": 80, "y": 18, "w": 260, "h": 60, "corner_radius": 30},
                 {"type": "RECTANGLE", "name": "图标_舵轮",
                  "x": 0, "y": 0, "w": 95, "h": 97},
                 {"type": "TEXT", "name": "文本_总进度",
                  "x": 110, "y": 30, "h": 36, "content": "1906/5000",
                  "font_size": 32, "font_weight": "Bold",
                  "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"}
             ]}
        ]
    }

# ============================================================
# 进度条父 ccb #1: 进度条本体 + 起点装饰 + 宝箱×3 + 状态×3
# ============================================================
def build_treasure_box(variant, x):
    """variant in {金, 银, 铜}; 同 children 不同 visible"""
    return {
        "type": "FRAME", "name": "宝箱",
        "x": x, "y": 80, "w": 164, "h": 188, "layoutMode": "NONE",
        "constraints": {"horizontal": "LEFT", "vertical": "TOP"},
        "children": [
            {"type": "RECTANGLE", "name": "图片_宝箱_金",
             "x": 0, "y": 0, "w": 164, "h": 188,
             "visible": variant == "金"},
            {"type": "RECTANGLE", "name": "图片_宝箱_银",
             "x": 0, "y": 0, "w": 164, "h": 188,
             "visible": variant == "银"},
            {"type": "RECTANGLE", "name": "图片_宝箱_铜",
             "x": 0, "y": 0, "w": 164, "h": 188,
             "visible": variant == "铜"}
        ]
    }

def build_status(variant, x, threshold=""):
    """variant in {已完成, 未完成, 可领取}"""
    return {
        "type": "FRAME", "name": "状态",
        "x": x, "y": 315, "w": 164, "h": 113, "layoutMode": "NONE",
        "constraints": {"horizontal": "LEFT", "vertical": "TOP"},
        "children": [
            # 已完成 variant: 图标_对勾 单元素
            {"type": "RECTANGLE", "name": "图标_对勾",
             "x": 40, "y": 20, "w": 84, "h": 68,
             "visible": variant == "已完成"},
            # 未完成 variant: 底板 + 文本_数字
            {"type": "RECTANGLE", "name": "底板_状态_未完成",
             "x": 0, "y": 20, "w": 164, "h": 79, "corner_radius": 39,
             "visible": variant == "未完成"},
            {"type": "TEXT", "name": "文本_状态_数字",
             "x": 0, "y": 35, "w": 164, "h": 45, "content": threshold,
             "font_size": 38, "font_weight": "Bold",
             "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
             "visible": variant == "未完成"},
            # 可领取 variant: claim 按钮
            {"type": "FRAME", "name": "按钮_claim",
             "x": 0, "y": 10, "w": 164, "h": 95, "layoutMode": "NONE",
             "visible": variant == "可领取",
             "children": [
                 {"type": "RECTANGLE", "name": "底板_claim",
                  "x": 0, "y": 0, "w": 164, "h": 95, "corner_radius": 47},
                 {"type": "TEXT", "name": "文本_claim",
                  "x": 0, "y": 25, "w": 164, "h": 45, "content": "claim",
                  "font_size": 38, "font_weight": "Bold",
                  "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"}
             ]}
        ]
    }

def build_progress_panel():
    """父 ccb #1: 进度条 + 3 宝箱 + 3 状态 (NONE 绝对定位)"""
    # 进度条本体 x 范围: 55 ~ 1040 (985 wide)
    # 3 节点位置 (沿条 25% / 60% / 98%):
    NODE_X = [55 + int(985*0.16), 55 + int(985*0.57), 55 + int(985*0.93)]  # 节点中心位置
    return {
        "type": "FRAME", "name": "组_进度条与宝箱",
        "x": 0, "y": 1125, "w": 1080, "h": 506,
        "layoutMode": "NONE",
        "constraints": {"horizontal": "SCALE", "vertical": "TOP"},
        "children": [
            # 起点装饰 大舵轮
            {"type": "RECTANGLE", "name": "图标_进度起点",
             "x": 27, "y": 50, "w": 164, "h": 169,
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"}},
            # 进度条三层
            {"type": "FRAME", "name": "组_进度_团队",
             "x": 55, "y": 100, "w": 985, "h": 75,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "SCALE", "vertical": "TOP"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_团队",
                  "x": 0, "y": 0, "w": 985, "h": 75, "corner_radius": 37},
                 {"type": "RECTANGLE", "name": "进度条_团队",
                  "x": 10, "y": 10, "w": 965, "h": 55, "corner_radius": 27}
             ]},
            # 3 宝箱 (沿进度条压上, 25%/60%/98%)
            build_treasure_box("金", NODE_X[0] - 82),
            build_treasure_box("银", NODE_X[1] - 82),
            build_treasure_box("铜", NODE_X[2] - 82),
            # 3 状态 (在宝箱下方)
            build_status("已完成", NODE_X[0] - 82, ""),
            build_status("未完成", NODE_X[1] - 82, "3000"),
            build_status("未完成", NODE_X[2] - 82, "5000")
        ]
    }

# ============================================================
# 列表滚动区
# ============================================================
def build_scroll_list():
    return {
        "type": "FRAME", "name": "容器_列表滚动区",
        "x": 0, "y": 1650, "w": 1080, "h": 750,
        "layoutMode": "VERTICAL",
        "primaryAxisSizingMode": "FIXED",
        "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "MIN",
        "counterAxisAlignItems": "MIN",
        "clip_content": True,
        "overflow": "VERTICAL",
        "constraints": {"horizontal": "SCALE", "vertical": "SCALE"},
        "children": [
            {"type": "FRAME", "name": "组_滚动内容",
             "layoutMode": "VERTICAL",
             "primaryAxisSizingMode": "AUTO",
             "counterAxisSizingMode": "FIXED",
             "layoutSizingHorizontal": "FIXED",
             "layoutSizingVertical": "HUG",
             "primaryAxisAlignItems": "MIN",
             "counterAxisAlignItems": "MIN",
             "itemSpacing": 18,
             "paddingLeft": ROW_PADDING_X, "paddingRight": ROW_PADDING_X,
             "w": 1080,
             "children": [build_list_row(u) for u in USERS]}
        ]
    }

# ============================================================
# 屏幕根
# ============================================================
scene = {
    "screens": [
        {
            "name": "界面_Team_Treasure",
            "type": "FRAME",
            "w": 1080, "h": 2400,
            "layoutMode": "NONE",
            "flow": [],
            "layers": [
                build_top_banner(),
                build_pirate_decor(),
                build_choisss_row(),
                build_progress_panel(),
                build_scroll_list()
            ]
        }
    ],
    "components": []
}

with open('scene.json', 'w', encoding='utf-8') as f:
    json.dump(scene, f, ensure_ascii=False, indent=2)

print(f"✅ scene.json 生成完毕")
print(f"   屏幕: 1 ({scene['screens'][0]['name']})")
print(f"   顶层 layers: {len(scene['screens'][0]['layers'])}")
print(f"   列表项数: {len(USERS)}")
print(f"   components[]: {len(scene['components'])} (S7 阶段空, S11 抽)")
import os
print(f"   文件大小: {os.path.getsize('scene.json')/1024:.1f} KB")
