#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S4+S5: 生成 界面_TeamTreasure 的扁平 scene.json
- 17 个排行榜行老老实实展开 (规则 11.5 内部命名严格一致)
- Row 6 (mmmmm) 绿底 = 当前用户态, 仅靠 底板_行 fill 区分
- X/i/倒计时 用 component_ref + 父按钮包装 (做法 B)
- 进度条用 S0 双层 RECT 铁律
"""
import json

# ========== 排行榜数据 ==========
# (排名, 名字, 头衔, 道具数, 分数, 是否当前用户)
# 实际视频中的视觉状态:
#   - has_title  = 头衔徽章 + 头衔文字 显隐 (state-driven, 算 Variant)
#   - has_item   = 道具图标 + 道具数 显隐 (state-driven, 算 Variant)
#   - is_current = 底板_行 绿色 (state-driven, 算 Variant)
#   - 其他文字内容 (名字/分数) = 数据驱动, 不算 Variant
LEADERBOARD = [
    (1,  "mails",     "",            "x2", 356, False),  # 无头衔 + 有道具
    (2,  "Choy",      "Knight",      "x2", 343, False),  # 有头衔 + 有道具
    (3,  "Kkk",       "",            "x2", 275, False),  # 无头衔 + 有道具
    (4,  "onon",      "Grand Knight","",   209, False),  # 有头衔 + 无道具
    (5,  "GrandKn",   "",            "",   180, False),  # 无头衔 + 无道具 (default)
    (6,  "mmmmm",     "",            "",   126, True),   # 当前用户绿底
    (7,  "hshen",     "Grand Knight","",   122, False),  # 有头衔 + 无道具
    (8,  "Csl",       "Knight",      "",   114, False),  # 有头衔 + 无道具
    (9,  "lllll",     "",            "",    93, False),  # 无头衔 + 无道具
    (10, "luk",       "Knight",      "",    59, False),  # 有头衔 + 无道具
    (11, "Arthur",    "",            "",    49, False),  # 无头衔 + 无道具
    (12, "Teresa",    "Knight",      "",    28, False),  # 有头衔 + 无道具
    (13, "Lokwan",    "Knight",      "x2", 26, False),   # 有头衔 + 有道具 (Lokwan 行有 10000 道具)
    (14, "fiona",     "",            "",    24, False),  # 无头衔 + 无道具
    (15, "Cassandra", "",            "",    18, False),  # 无头衔 + 无道具
    (16, "789",       "",            "",    12, False),  # 无头衔 + 无道具
    (17, "Hanna",     "",            "",     5, False),  # 无头衔 + 无道具
]

ROW_H = 177
LIST_X = 0
LIST_W = 1080
LIST_Y = 1385       # 滚动 viewport 起点
LIST_H = 952        # 滚动 viewport 高度
ROW_COUNT = len(LEADERBOARD)
CONTENT_H = ROW_COUNT * ROW_H  # 17 * 177 = 3009


# ========== 节点工厂 ==========
def make_row(rank, name, title, item_count, score, is_current):
    """
    生成一个排行榜行 FRAME.
    规则 11.5: 所有行内部子节点命名 100% 一致, 共 10 个固定槽位.
    实例间差异:
      - TEXT.content (名字/排名/分数/头衔/道具数) = 数据驱动, 不算 Variant
      - 底板_行.fill (绿/默认) = 状态多态
      - 图标_头衔徽章.visible (T/F) = 状态多态
      - 文本_头衔.visible        (T/F) = 状态多态
      - 图标_道具.visible        (T/F) = 状态多态
      - 文本_道具数.visible      (T/F) = 状态多态
    """
    has_title = bool(title)
    has_item = bool(item_count)

    base = {
        "type": "FRAME",
        "name": f"列表项_排名{rank}",
        "w": LIST_W, "h": ROW_H,
        "layoutMode": "NONE",
        "children": [
            # 1. 底板_行 (当前用户绿底)
            {
                "type": "RECTANGLE",
                "name": "底板_行",
                "x": 0, "y": 0, "w": LIST_W, "h": ROW_H,
                "corner_radius": 30,
                "constraints": {"horizontal": "SCALE", "vertical": "SCALE"},
                **({"fill": "#88c870"} if is_current else {})
            },
            # 2. 文本_排名 (数字)
            {
                "type": "TEXT",
                "name": "文本_排名",
                "x": 50, "y": 60,
                "content": str(rank),
                "font_size": 60, "font_weight": "Bold",
                "textAlignHorizontal": "CENTER",
                "constraints": {"horizontal": "LEFT", "vertical": "CENTER"}
            },
            # 3. 图标_头像
            {
                "type": "RECTANGLE",
                "name": "图标_头像",
                "x": 130, "y": 35, "w": 105, "h": 105,
                "corner_radius": 20,
                "constraints": {"horizontal": "LEFT", "vertical": "CENTER"}
            },
            # 4. 文本_名字
            {
                "type": "TEXT",
                "name": "文本_名字",
                "x": 260, "y": 60,
                "content": name,
                "font_size": 50, "font_weight": "Bold",
                "constraints": {"horizontal": "LEFT", "vertical": "CENTER"}
            },
            # 5. 文本_头衔 (Knight/Grand Knight, visible 由 has_title 控制)
            {
                "type": "TEXT",
                "name": "文本_头衔",
                "x": 260, "y": 115,
                "content": title or "Knight",      # 空时仍写占位, visible 控显隐
                "font_size": 32, "font_weight": "Regular",
                "visible": has_title,
                "constraints": {"horizontal": "LEFT", "vertical": "CENTER"}
            },
            # 6. 图标_头衔徽章 (visible 由 has_title 控制)
            {
                "type": "RECTANGLE",
                "name": "图标_头衔徽章",
                "x": 420, "y": 110, "w": 40, "h": 40,
                "corner_radius": 10,
                "visible": has_title,
                "constraints": {"horizontal": "LEFT", "vertical": "CENTER"}
            },
            # 7. 图标_道具 (visible 由 has_item 控制)
            {
                "type": "RECTANGLE",
                "name": "图标_道具",
                "x": 700, "y": 50, "w": 80, "h": 80,
                "corner_radius": 15,
                "visible": has_item,
                "constraints": {"horizontal": "LEFT", "vertical": "CENTER"}
            },
            # 8. 文本_道具数 (visible 由 has_item 控制)
            {
                "type": "TEXT",
                "name": "文本_道具数",
                "x": 790, "y": 70,
                "content": item_count or "x1",
                "font_size": 36, "font_weight": "Bold",
                "visible": has_item,
                "constraints": {"horizontal": "LEFT", "vertical": "CENTER"}
            },
            # 9. 图标_舵盘
            {
                "type": "RECTANGLE",
                "name": "图标_舵盘",
                "x": 870, "y": 60, "w": 64, "h": 64,
                "constraints": {"horizontal": "RIGHT", "vertical": "CENTER"}
            },
            # 10. 文本_分数
            {
                "type": "TEXT",
                "name": "文本_分数",
                "x": 950, "y": 70,
                "content": str(score),
                "font_size": 40, "font_weight": "Bold",
                "textAlignHorizontal": "RIGHT",
                "constraints": {"horizontal": "RIGHT", "vertical": "CENTER"}
            }
        ]
    }
    return base


# ========== 排行榜列表(滚动容器) ==========
def make_leaderboard_scroll():
    """S5 滚动容器三条件: 父 overflow+clip+FIXED, 子 AUTO+HUG+显式w"""
    rows = [make_row(*r) for r in LEADERBOARD]
    return {
        "type": "FRAME",
        "name": "容器_排行榜列表",
        "x": LIST_X, "y": LIST_Y, "w": LIST_W, "h": LIST_H,
        "layoutMode": "NONE",
        "primaryAxisSizingMode": "FIXED",
        "counterAxisSizingMode": "FIXED",
        "clip_content": True,           # 下划线! 不要写成 clipsContent
        "overflow": "VERTICAL",
        "constraints": {"horizontal": "SCALE", "vertical": "BOTTOM"},
        "children": [
            {
                "type": "FRAME",
                "name": "内容_排行榜列表",
                "x": 0, "y": 0, "w": LIST_W, "h": CONTENT_H,
                "layoutMode": "VERTICAL",
                "primaryAxisSizingMode": "AUTO",       # 滚动子: AUTO
                "counterAxisSizingMode": "FIXED",
                "primaryAxisAlignItems": "MIN",
                "counterAxisAlignItems": "MIN",
                "itemSpacing": 0,
                "layoutSizingHorizontal": "FIXED",
                "layoutSizingVertical": "HUG",          # 滚动子: HUG
                "children": rows
            }
        ]
    }


# ========== Team Treasure 标题区 ==========
def make_header():
    return {
        "type": "FRAME",
        "name": "组_Team Treasure标题",
        "x": 0, "y": 78, "w": 1080, "h": 863,
        "layoutMode": "NONE",
        "constraints": {"horizontal": "SCALE", "vertical": "TOP"},
        "children": [
            # 主底板
            {"type": "RECTANGLE", "name": "底板_主标题",
             "x": 0, "y": 0, "w": 1080, "h": 863, "corner_radius": 0,
             "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
            # 海盗插画
            {"type": "RECTANGLE", "name": "图片_海盗插画",
             "x": 0, "y": 50, "w": 1080, "h": 740,
             "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
            # 标题文字
            {"type": "TEXT", "name": "文本_标题",
             "x": 157, "y": 90, "content": "Team Treasure",
             "font_size": 80, "font_weight": "Bold",
             "textAlignHorizontal": "CENTER",
             "constraints": {"horizontal": "CENTER", "vertical": "TOP"}},
            # X 关闭按钮 - 父按钮 FRAME 包装 component_ref (做法 B)
            {"type": "FRAME", "name": "按钮_关闭",
             "x": 921, "y": 13, "w": 132, "h": 124,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "RIGHT", "vertical": "TOP"},
             "children": [
                 {"component_ref": "圆形按钮_关闭",
                  "name": "组件_关闭",
                  "x": 0, "y": 0, "w": 132, "h": 124,
                  "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}}
             ]},
            # i 信息按钮
            {"type": "FRAME", "name": "按钮_信息",
             "x": 30, "y": 251, "w": 102, "h": 102,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "LEFT", "vertical": "TOP"},
             "children": [
                 {"component_ref": "圆形按钮_信息",
                  "name": "组件_信息",
                  "x": 0, "y": 0, "w": 102, "h": 102,
                  "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}}
             ]},
            # 2d 5h 倒计时 - 父按钮包装 component_ref
            {"type": "FRAME", "name": "按钮_倒计时",
             "x": 406, "y": 660, "w": 268, "h": 74,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "CENTER", "vertical": "TOP"},
             "children": [
                 {"component_ref": "底标_倒计时",
                  "name": "组件_倒计时",
                  "x": 0, "y": 0, "w": 268, "h": 74,
                  "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}}
             ]}
        ]
    }


# ========== Choisss 横幅 ==========
def make_choisss_banner():
    return {
        "type": "FRAME",
        "name": "组_Choisss横幅",
        "x": 0, "y": 941, "w": 1080, "h": 167,
        "layoutMode": "NONE",
        "constraints": {"horizontal": "SCALE", "vertical": "TOP"},
        "children": [
            {"type": "RECTANGLE", "name": "底板_Choisss横幅",
             "x": 0, "y": 0, "w": 1080, "h": 167,
             "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
            {"type": "TEXT", "name": "文本_Choisss",
             "x": 130, "y": 50, "content": "Choisss",
             "font_size": 60, "font_weight": "Bold",
             "constraints": {"horizontal": "LEFT", "vertical": "CENTER"}},
            {"type": "RECTANGLE", "name": "图标_横幅舵盘",
             "x": 740, "y": 50, "w": 64, "h": 64,
             "constraints": {"horizontal": "RIGHT", "vertical": "CENTER"}},
            {"type": "TEXT", "name": "文本_Choisss进度数",
             "x": 820, "y": 60, "content": "1997/5000",
             "font_size": 40, "font_weight": "Bold",
             "constraints": {"horizontal": "RIGHT", "vertical": "CENTER"}}
        ]
    }


# ========== Choisss 进度区 (S0 进度条三层结构) ==========
def make_choisss_progress():
    return {
        "type": "FRAME",
        "name": "组_Choisss进度",
        "x": 0, "y": 1108, "w": 1080, "h": 277,
        "layoutMode": "NONE",
        "constraints": {"horizontal": "SCALE", "vertical": "TOP"},
        "children": [
            {"type": "RECTANGLE", "name": "底板_Choisss进度",
             "x": 0, "y": 0, "w": 1080, "h": 277,
             "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
            # 进度条三层 (S0 铁律)
            {"type": "FRAME", "name": "组_进度_Choisss",
             "x": 140, "y": 122, "w": 812, "h": 37,
             "layoutMode": "NONE",
             "constraints": {"horizontal": "SCALE", "vertical": "CENTER"},
             "children": [
                 {"type": "RECTANGLE", "name": "底板_Choisss",
                  "x": 0, "y": 0, "w": 812, "h": 37, "corner_radius": 18,
                  "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
                 {"type": "RECTANGLE", "name": "进度条_Choisss",
                  "x": 10, "y": 10, "w": 792, "h": 17, "corner_radius": 8,
                  "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}}
             ]},
            # 4 chest 标记 + 舵盘 + 勾 + 数字 (兄弟,不进进度条包装)
            {"type": "RECTANGLE", "name": "图标_进度舵盘",
             "x": 20, "y": 67, "w": 129, "h": 129,
             "constraints": {"horizontal": "LEFT", "vertical": "CENTER"}},
            {"type": "RECTANGLE", "name": "图标_宝箱_棕",
             "x": 240, "y": 72, "w": 102, "h": 102,
             "constraints": {"horizontal": "LEFT", "vertical": "CENTER"}},
            {"type": "RECTANGLE", "name": "图标_宝箱_蓝",
             "x": 540, "y": 72, "w": 102, "h": 102,
             "constraints": {"horizontal": "CENTER", "vertical": "CENTER"}},
            {"type": "RECTANGLE", "name": "图标_宝箱_紫",
             "x": 850, "y": 72, "w": 102, "h": 102,
             "constraints": {"horizontal": "RIGHT", "vertical": "CENTER"}},
            {"type": "RECTANGLE", "name": "图标_勾",
             "x": 260, "y": 182, "w": 64, "h": 55,
             "constraints": {"horizontal": "LEFT", "vertical": "CENTER"}},
            {"type": "TEXT", "name": "文本_3000",
             "x": 560, "y": 195, "content": "3000",
             "font_size": 36, "font_weight": "Bold",
             "constraints": {"horizontal": "CENTER", "vertical": "CENTER"}},
            {"type": "TEXT", "name": "文本_5000",
             "x": 870, "y": 195, "content": "5000",
             "font_size": 36, "font_weight": "Bold",
             "constraints": {"horizontal": "RIGHT", "vertical": "CENTER"}}
        ]
    }


# ========== 主屏 ==========
def make_screen():
    return {
        "name": "界面_TeamTreasure",
        "w": 1080, "h": 2400,
        "layers": [
            # 顶部黑边 0~78 (无内容,可省略)
            make_header(),                    # 1. Team Treasure 标题区
            make_choisss_banner(),            # 2. Choisss 横幅
            make_choisss_progress(),          # 3. Choisss 进度区
            make_leaderboard_scroll(),        # 4. 排行榜滚动列表
        ]
    }


# ========== 顶层 scene ==========
scene = {
    "screens": [make_screen()],
    "flow": []   # 视频内只有滚动,无屏幕跳转
}

# 输出
OUT = '/Users/red/Desktop/component_extractor/scene_flat.json'
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(scene, f, ensure_ascii=False, indent=2)

print(f"✅ 输出: {OUT}")
print(f"   屏幕数: 1 (界面_TeamTreasure)")
print(f"   排行榜行数: {ROW_COUNT}")
print(f"   当前用户行: 第 6 行 (mmmmm, 绿底)")
print(f"   滚动容器: 容器_排行榜列表 (y={LIST_Y} h={LIST_H})")
print(f"   滚动子: 内容_排行榜列表 (h={CONTENT_H} > {LIST_H} = 滚动条件✓)")
