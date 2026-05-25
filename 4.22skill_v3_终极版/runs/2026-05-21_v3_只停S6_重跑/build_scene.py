#!/usr/bin/env python3
"""S7 生成扁平 scene.json (无 INSTANCE / variant / overrides / components[])"""
import json

# 视频提取的列表数据 (rank → name / subtitle / 头像装饰 / 装饰前 / 道具 / 数量)
ROWS = [
    {"rank":1,  "name":"mailo",     "subtitle":"",              "avatar_decor":True,  "front_decor":False, "item":"礼物", "item_x":"x2", "count":"529", "is_current":False},
    {"rank":2,  "name":"onon",      "subtitle":"Grand Knight",  "avatar_decor":True,  "front_decor":False, "item":"金币", "item_x":"x2", "count":"419", "is_current":False},
    {"rank":3,  "name":"choy",      "subtitle":"Grand Knight",  "avatar_decor":True,  "front_decor":False, "item":"大炮", "item_x":"x2", "count":"244", "is_current":False},
    {"rank":4,  "name":"luk",       "subtitle":"Grand Knight",  "avatar_decor":True,  "front_decor":False, "item":"",     "item_x":"",   "count":"129", "is_current":False},
    {"rank":5,  "name":"Kkk",       "subtitle":"Knight",        "avatar_decor":True,  "front_decor":False, "item":"",     "item_x":"",   "count":"127", "is_current":False},
    {"rank":6,  "name":"mmmmm",     "subtitle":"Knight",        "avatar_decor":False, "front_decor":False, "item":"",     "item_x":"",   "count":"108", "is_current":True},
    {"rank":7,  "name":"Csl",       "subtitle":"Grand Knight",  "avatar_decor":True,  "front_decor":False, "item":"",     "item_x":"",   "count":"95",  "is_current":False},
    {"rank":8,  "name":"Arthur",    "subtitle":"",              "avatar_decor":False, "front_decor":False, "item":"",     "item_x":"",   "count":"65",  "is_current":False},
    {"rank":9,  "name":"Tereo",     "subtitle":"",              "avatar_decor":False, "front_decor":True,  "item":"",     "item_x":"",   "count":"64",  "is_current":False},
    {"rank":10, "name":"hshen",     "subtitle":"Knight",        "avatar_decor":False, "front_decor":False, "item":"",     "item_x":"",   "count":"58",  "is_current":False},
    {"rank":11, "name":"Cassandra", "subtitle":"",              "avatar_decor":False, "front_decor":False, "item":"",     "item_x":"",   "count":"25",  "is_current":False},
    {"rank":12, "name":"cyrax",     "subtitle":"",              "avatar_decor":False, "front_decor":False, "item":"",     "item_x":"",   "count":"25",  "is_current":False},
    {"rank":13, "name":"789",       "subtitle":"Knight",        "avatar_decor":False, "front_decor":True,  "item":"",     "item_x":"",   "count":"12",  "is_current":False},
]

# 三个宝箱档位 (金/银/铜 visual variant — S7 阶段 children 100% 一致, 用 visible 切装饰)
BOXES = [
    {"index":1, "tier":"铜", "show_bronze":True,  "show_silver":False, "show_gold":False},
    {"index":2, "tier":"银", "show_bronze":False, "show_silver":True,  "show_gold":False},
    {"index":3, "tier":"金", "show_bronze":False, "show_silver":False, "show_gold":True},
]

# 三个状态 (已完成 / 未完成 / 未完成 — variant: done/pending/claimable)
# 视频可见: 状态1=绿勾完成, 状态2=数字3000未完成, 状态3=数字5000未完成
# 用户预声明第3 variant "可领取" 视频未触发, 此处用未完成填充, S11 自动按 visible 切
STATES = [
    {"index":1, "variant":"已完成", "show_done":True,  "show_pending":False, "show_claim":False, "number":""},
    {"index":2, "variant":"未完成", "show_done":False, "show_pending":True,  "show_claim":False, "number":"3000"},
    {"index":3, "variant":"未完成", "show_done":False, "show_pending":True,  "show_claim":False, "number":"5000"},
]


def make_rank(rank: int, is_current: bool):
    """子 ccb 排名号 (4 variant 金/银/铜/普通) — children 100% 一致, 底盘 visible/fill 切换"""
    tier = "金" if rank == 1 else ("银" if rank == 2 else ("铜" if rank == 3 else "普通"))
    show_bg = rank in (1, 2, 3)
    return {
        "type": "FRAME", "name": "组_排名号",
        "x": 25, "y": 35, "w": 80, "h": 120,
        "layoutMode": "NONE",
        "children": [
            {"type": "RECTANGLE", "name": "底盘_排名",
             "x": 0, "y": 0, "w": 80, "h": 100, "corner_radius": 18,
             "visible": show_bg},
            {"type": "TEXT", "name": "文本_排名",
             "x": 0, "y": 30, "h": 60, "content": str(rank),
             "font_size": 60, "font_weight": 700,
             "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"}
        ]
    }


def make_avatar(avatar_decor: bool):
    """子 ccb 头像 (2 variant 带装饰/无装饰)"""
    return {
        "type": "FRAME", "name": "组_头像",
        "x": 120, "y": 25, "w": 145, "h": 145,
        "layoutMode": "NONE",
        "children": [
            {"type": "RECTANGLE", "name": "图片_头像",
             "x": 0, "y": 0, "w": 145, "h": 145, "corner_radius": 15},
            {"type": "FRAME", "name": "装饰_红窗帘",
             "x": -5, "y": -25, "w": 155, "h": 175,
             "layoutMode": "NONE",
             "visible": avatar_decor,
             "children": [
                 {"type": "RECTANGLE", "name": "图片_装饰红窗帘",
                  "x": 0, "y": 0, "w": 155, "h": 175}
             ]}
        ]
    }


def make_front_decor(front_decor: bool):
    """子 ccb 装饰物前 (2 variant 有/空) — wrapper visible 切换"""
    return {
        "type": "FRAME", "name": "组_装饰前",
        "x": 285, "y": 55, "w": 75, "h": 75,
        "layoutMode": "NONE",
        "visible": front_decor,
        "children": [
            {"type": "RECTANGLE", "name": "图片_装饰前",
             "x": 0, "y": 0, "w": 75, "h": 75}
        ]
    }


def make_name_group(name: str, subtitle: str):
    """组_名字 (玩家名 + 副标 + 小盾牌) — 单实例结构, 不抽 ccb"""
    children = [
        {"type": "TEXT", "name": "文本_玩家名",
         "x": 0, "y": 0, "h": 70, "content": name,
         "font_size": 52, "font_weight": 700,
         "textAlignHorizontal": "LEFT", "textAlignVertical": "CENTER"}
    ]
    # 副标 wrapper 始终存在, 通过 visible 切显隐 (规则 11.5: children 结构一致)
    children.append({
        "type": "FRAME", "name": "组_副标",
        "x": 0, "y": 75, "w": 280, "h": 50,
        "layoutMode": "NONE",
        "visible": bool(subtitle),
        "children": [
            {"type": "TEXT", "name": "文本_副标",
             "x": 0, "y": 0, "h": 45, "content": subtitle if subtitle else "",
             "font_size": 34, "font_weight": 500,
             "textAlignHorizontal": "LEFT", "textAlignVertical": "CENTER"},
            {"type": "RECTANGLE", "name": "图标_盾牌",
             "x": 210, "y": 5, "w": 38, "h": 38}
        ]
    })
    return {
        "type": "FRAME", "name": "组_名字",
        "x": 380, "y": 30, "w": 290, "h": 130,
        "layoutMode": "NONE",
        "children": children
    }


def make_item(item: str, item_x: str):
    """子 ccb 道具 (2 variant 常态/空) — wrapper visible 切, children 100% 一致"""
    show = bool(item)
    return {
        "type": "FRAME", "name": "组_道具",
        "x": 680, "y": 50, "w": 160, "h": 90,
        "layoutMode": "NONE",
        "visible": show,
        "children": [
            {"type": "RECTANGLE", "name": "图片_道具",
             "x": 0, "y": 0, "w": 90, "h": 90},
            {"type": "TEXT", "name": "文本_x数量",
             "x": 95, "y": 25, "h": 50, "content": item_x if item_x else "",
             "font_size": 38, "font_weight": 700,
             "textAlignHorizontal": "LEFT", "textAlignVertical": "CENTER"}
        ]
    }


def make_count(count: str):
    """子 ccb 收集物数量 (1 variant icon+底板+文本) — 横排徽章左图右文"""
    return {
        "type": "FRAME", "name": "组_收集物数量",
        "x": 855, "y": 55, "w": 215, "h": 100,
        "layoutMode": "NONE",
        "children": [
            {"type": "RECTANGLE", "name": "底板_数量胶囊",
             "x": 30, "y": 20, "w": 185, "h": 70, "corner_radius": 35},
            {"type": "RECTANGLE", "name": "图标_舵轮",
             "x": 0, "y": 0, "w": 105, "h": 105},
            {"type": "TEXT", "name": "文本_数量",
             "x": 100, "y": 35, "h": 50, "content": count,
             "font_size": 40, "font_weight": 700,
             "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"}
        ]
    }


def make_list_row(row):
    """列表项_行 (父 ccb, 2 variant 常态/当前用户) — 扁平 FRAME, children 100% 一致"""
    # corner_radius 微差表达 variant 视觉差异 (07d 方法 C); is_current 影响底板视觉签名
    base_radius = 25 if not row["is_current"] else 26
    return {
        "type": "FRAME", "name": "组_列表项行",
        "w": 1080, "h": 190,
        "layoutMode": "NONE",
        "children": [
            {"type": "RECTANGLE", "name": "底板_列表项行",
             "x": 30, "y": 5, "w": 1020, "h": 180, "corner_radius": base_radius},
            make_rank(row["rank"], row["is_current"]),
            make_avatar(row["avatar_decor"]),
            make_front_decor(row["front_decor"]),
            make_name_group(row["name"], row["subtitle"]),
            make_item(row["item"], row["item_x"]),
            make_count(row["count"])
        ]
    }


def make_box(box):
    """子 ccb 宝箱 (3 variant 金/银/铜) — children 100% 一致, 装饰子节点 visible 切换"""
    return {
        "type": "FRAME", "name": "组_宝箱",
        "w": 170, "h": 180,
        "layoutMode": "NONE",
        "children": [
            {"type": "RECTANGLE", "name": "图片_宝箱_铜",
             "x": 0, "y": 0, "w": 170, "h": 180,
             "visible": box["show_bronze"]},
            {"type": "RECTANGLE", "name": "图片_宝箱_银",
             "x": 0, "y": 0, "w": 170, "h": 180,
             "visible": box["show_silver"]},
            {"type": "RECTANGLE", "name": "图片_宝箱_金",
             "x": 0, "y": 0, "w": 170, "h": 180,
             "visible": box["show_gold"]}
        ]
    }


def make_box_button(box, x):
    """按钮_宝箱_N 外层 FRAME (做法 B 包装) — 内含 组_宝箱 扁平 FRAME"""
    return {
        "type": "FRAME", "name": "按钮_宝箱_" + str(box["index"]),
        "x": x, "y": 20, "w": 170, "h": 180,
        "layoutMode": "NONE",
        "children": [
            make_box(box)
        ]
    }


def make_state(state, x):
    """子 ccb 状态 (3 variant 已完成/未完成/可领取) — children 100% 一致, 子节点 visible 切换"""
    return {
        "type": "FRAME", "name": "组_状态",
        "x": x, "y": 230, "w": 215, "h": 85,
        "layoutMode": "NONE",
        "children": [
            # variant: 已完成 (绿色对勾, 无底)
            {"type": "RECTANGLE", "name": "图标_对勾",
             "x": 65, "y": 0, "w": 85, "h": 85,
             "visible": state["show_done"]},
            # variant: 未完成 (文本+底板)
            {"type": "RECTANGLE", "name": "底板_未完成数字",
             "x": 0, "y": 10, "w": 215, "h": 75, "corner_radius": 12,
             "visible": state["show_pending"]},
            {"type": "TEXT", "name": "文本_未完成数字",
             "x": 0, "y": 22, "w": 215, "h": 50, "content": state["number"],
             "font_size": 42, "font_weight": 700,
             "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
             "visible": state["show_pending"]},
            # variant: 可领取 (按钮_claim 内层) — 视频未触发, S7 阶段 children 完整, visible:false
            {"type": "FRAME", "name": "按钮_claim",
             "x": 0, "y": 10, "w": 215, "h": 75,
             "layoutMode": "NONE",
             "visible": state["show_claim"],
             "children": [
                 {"type": "RECTANGLE", "name": "底板_claim",
                  "x": 0, "y": 0, "w": 215, "h": 75, "corner_radius": 12},
                 {"type": "TEXT", "name": "文本_claim",
                  "x": 0, "y": 12, "w": 215, "h": 50, "content": "CLAIM",
                  "font_size": 40, "font_weight": 700,
                  "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"}
             ]}
        ]
    }


# ===== 顶部装饰区 =====
top_decoration = {
    "type": "FRAME", "name": "组_顶部装饰",
    "x": 0, "y": 0, "w": 1080, "h": 805,
    "layoutMode": "NONE",
    "constraints": {"horizontal": "CENTER", "vertical": "TOP"},
    "children": [
        {"type": "RECTANGLE", "name": "底板_顶部黄色波浪",
         "x": 0, "y": 0, "w": 1080, "h": 340, "corner_radius": 0},
        {"type": "TEXT", "name": "文本_标题",
         "x": 135, "y": 95, "w": 810, "h": 130, "content": "Team Treasure",
         "font_size": 90, "font_weight": 800,
         "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"},
        {"type": "RECTANGLE", "name": "图片_海盗插画",
         "x": 0, "y": 260, "w": 1080, "h": 440},
        {"type": "RECTANGLE", "name": "图片_金币堆",
         "x": 50, "y": 645, "w": 280, "h": 145},
        {"type": "FRAME", "name": "组_倒计时",
         "x": 370, "y": 690, "w": 325, "h": 110,
         "layoutMode": "NONE",
         "children": [
             {"type": "RECTANGLE", "name": "底板_倒计时",
              "x": 0, "y": 0, "w": 325, "h": 110, "corner_radius": 55},
             {"type": "RECTANGLE", "name": "图标_钟表",
              "x": 20, "y": 5, "w": 100, "h": 100},
             {"type": "TEXT", "name": "文本_倒计时",
              "x": 130, "y": 25, "h": 70, "content": "2d 1h",
              "font_size": 56, "font_weight": 800,
              "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"}
         ]},
        {"type": "FRAME", "name": "按钮_信息",
         "x": 25, "y": 225, "w": 80, "h": 80,
         "layoutMode": "NONE",
         "children": [
             {"type": "RECTANGLE", "name": "底板_按钮信息",
              "x": 0, "y": 0, "w": 80, "h": 80, "corner_radius": 40},
             {"type": "TEXT", "name": "文本_按钮信息",
              "x": 0, "y": 15, "w": 80, "h": 50, "content": "i",
              "font_size": 50, "font_weight": 800,
              "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"}
         ]},
        {"type": "FRAME", "name": "按钮_关闭",
         "x": 960, "y": 100, "w": 95, "h": 95,
         "layoutMode": "NONE",
         "children": [
             {"type": "RECTANGLE", "name": "底板_按钮关闭",
              "x": 0, "y": 0, "w": 95, "h": 95, "corner_radius": 47},
             {"type": "TEXT", "name": "文本_按钮关闭",
              "x": 0, "y": 18, "w": 95, "h": 60, "content": "×",
              "font_size": 60, "font_weight": 800,
              "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"}
         ]}
    ]
}

# ===== Choisss 玩家行 =====
choisss_row = {
    "type": "FRAME", "name": "组_Choisss行",
    "x": 30, "y": 805, "w": 1020, "h": 185,
    "layoutMode": "NONE",
    "constraints": {"horizontal": "CENTER", "vertical": "TOP"},
    "children": [
        {"type": "RECTANGLE", "name": "底板_Choisss行",
         "x": 0, "y": 25, "w": 1020, "h": 160, "corner_radius": 30},
        {"type": "FRAME", "name": "角标_红三角",
         "x": 30, "y": 0, "w": 140, "h": 175,
         "layoutMode": "NONE",
         "children": [
             {"type": "RECTANGLE", "name": "图片_红三角",
              "x": 0, "y": 0, "w": 140, "h": 175}
         ]},
        {"type": "TEXT", "name": "文本_玩家名Choisss",
         "x": 200, "y": 50, "h": 90, "content": "Choisss",
         "font_size": 64, "font_weight": 800,
         "textAlignHorizontal": "LEFT", "textAlignVertical": "CENTER"},
        {"type": "FRAME", "name": "组_玩家分",
         "x": 700, "y": 30, "w": 350, "h": 140,
         "layoutMode": "NONE",
         "children": [
             {"type": "RECTANGLE", "name": "图标_玩家舵轮",
              "x": 0, "y": 10, "w": 115, "h": 120},
             {"type": "RECTANGLE", "name": "底板_玩家进度胶囊",
              "x": 105, "y": 35, "w": 245, "h": 70, "corner_radius": 35},
             {"type": "TEXT", "name": "文本_玩家进度",
              "x": 105, "y": 50, "w": 245, "h": 45, "content": "1906/5000",
              "font_size": 42, "font_weight": 700,
              "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"}
         ]}
    ]
}

# ===== 团队进度组团 (父 ccb) =====
# 父 ccb 整体不可点 (Q1c), 子级按钮_宝箱_N 单独可点
team_progress = {
    "type": "FRAME", "name": "组_团队进度",
    "x": 0, "y": 990, "w": 1080, "h": 321,
    "layoutMode": "NONE",
    "constraints": {"horizontal": "CENTER", "vertical": "TOP"},
    "children": [
        {"type": "RECTANGLE", "name": "底板_团队进度区",
         "x": 0, "y": 0, "w": 1080, "h": 321},
        {"type": "RECTANGLE", "name": "图标_起点舵轮",
         "x": 25, "y": 50, "w": 155, "h": 165},
        # 进度条三层 (skill 07c 铁律: 三层 XXX 一致, 内部不带"进度", 进度条内缩中心对齐)
        {"type": "FRAME", "name": "组_进度_团队",
         "x": 180, "y": 90, "w": 810, "h": 75,
         "layoutMode": "NONE",
         "children": [
             {"type": "RECTANGLE", "name": "底板_团队",
              "x": 0, "y": 0, "w": 810, "h": 75, "corner_radius": 37},
             {"type": "RECTANGLE", "name": "进度条_团队",
              "x": 10, "y": 10, "w": 790, "h": 55, "corner_radius": 27}
         ]},
        # 3 个 按钮_宝箱_N (做法 B, 内含 组_宝箱 扁平 FRAME)
        make_box_button(BOXES[0], x=210),
        make_box_button(BOXES[1], x=470),
        make_box_button(BOXES[2], x=800),
        # 3 个 组_状态 (3 variant: 已完成/未完成/可领取)
        make_state(STATES[0], x=85),
        make_state(STATES[1], x=355),
        make_state(STATES[2], x=685)
    ]
}

# ===== 列表滚动区 =====
# 滚动区: clip_content + overflow VERTICAL, 子容器 layoutSizingVertical: HUG
list_container = {
    "type": "FRAME", "name": "容器_排行榜滚动区",
    "x": 0, "y": 1311, "w": 1080, "h": 1089,
    "layoutMode": "VERTICAL",
    "primaryAxisSizingMode": "FIXED",
    "counterAxisSizingMode": "FIXED",
    "clip_content": True,
    "overflow": "VERTICAL",
    "constraints": {"horizontal": "CENTER", "vertical": "SCALE"},
    "children": [
        {"type": "FRAME", "name": "组_排行榜滚动内容",
         "layoutMode": "VERTICAL",
         "primaryAxisSizingMode": "AUTO",
         "counterAxisSizingMode": "FIXED",
         "layoutSizingHorizontal": "FIXED",
         "layoutSizingVertical": "HUG",
         "itemSpacing": 12,
         "w": 1080,
         "children": [make_list_row(r) for r in ROWS]}
    ]
}

# ===== 顶层 scene.json =====
scene = {
    "screens": [
        {
            "name": "界面_团队宝藏",
            "type": "FRAME",
            "w": 1080, "h": 2400,
            "layers": [
                top_decoration,
                choisss_row,
                team_progress,
                list_container
            ],
            "flow": []  # S5: 无屏幕跳转
        }
    ],
    "components": []  # S7 阶段空, S11 抽取后填充
}

# 写出
with open("scene.json", "w", encoding="utf-8") as f:
    json.dump(scene, f, ensure_ascii=False, indent=2)

# 统计
def count_nodes(node, count={"total":0,"frame":0,"rect":0,"text":0}):
    if isinstance(node, dict):
        t = node.get("type")
        if t == "FRAME":
            count["frame"] += 1
            count["total"] += 1
        elif t == "RECTANGLE":
            count["rect"] += 1
            count["total"] += 1
        elif t == "TEXT":
            count["text"] += 1
            count["total"] += 1
        for v in node.values():
            count_nodes(v, count)
    elif isinstance(node, list):
        for v in node:
            count_nodes(v, count)
    return count

c = count_nodes(scene)
print(f"scene.json 写出完成: {c}")
print(f"  屏幕数: {len(scene['screens'])}")
print(f"  顶层 layers: {len(scene['screens'][0]['layers'])}")
print(f"  列表行: {len(ROWS)}")
print(f"  宝箱按钮: {len(BOXES)}")
print(f"  状态: {len(STATES)}")
