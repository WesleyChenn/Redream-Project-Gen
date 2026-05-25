#!/usr/bin/env python3
"""S11 主路径 — 直接构造 v20.6 schema final_scene.json
铁律:
- components[] 只含最小单元 Component (8 个), 不含父 ccb 团队进度组团 / 列表行
  → 用户预声明列表项是父 ccb, 这里抽; 团队进度组团是父 ccb (1 实例) 用户预声明抽
  → 实际按"复用 ≥3 必抽" 规则: 团队进度组团 1 实例 → 不抽 (扁平 FRAME); 列表项 ≥13 实例 → 抽 ccb
- 每个 component 必有 w/h/variant_property/variants
- 每个 INSTANCE w/h == 引用 component 顶层 w/h
- 每个 RECTANGLE/TEXT layer 有 element_class (static/dynamic)
- components[] 拓扑顺序: 子 component 在前
- variant 名禁含下划线
"""
import json

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


def rect(name, x, y, w, h, **kw):
    n = {"type":"RECTANGLE", "name":name, "x":x, "y":y, "w":w, "h":h, "element_class":"static"}
    n.update(kw)
    return n


def text(name, x, y, w, h, content, font_size=40, **kw):
    n = {"type":"TEXT","name":name,"x":x,"y":y,"w":w,"h":h,"content":content,
         "font_size":font_size,"font_weight":700,
         "textAlignHorizontal":"CENTER","textAlignVertical":"CENTER",
         "element_class":"dynamic"}
    n.update(kw)
    return n


def frame(name, x, y, w, h, children, **kw):
    n = {"type":"FRAME","name":name,"x":x,"y":y,"w":w,"h":h,"layoutMode":"NONE","children":children}
    n.update(kw)
    return n


def instance(name, component_name, variant, x, y, w, h, overrides=None):
    n = {"type":"INSTANCE","name":name,"component_name":component_name,"variant":variant,
         "x":x,"y":y,"w":w,"h":h}
    if overrides:
        n["overrides"] = overrides
    return n


# ===== Component 定义 (8 个最小单元) =====
# 拓扑顺序: 子 component 在前

COMPONENTS = []

# ----- 组_排名号 (4 Variants 金/银/铜/普通) -----
def make_rank_variant(tier, is_default=False):
    show_bg = tier != "普通"
    layers = [
        rect("底盘_排名", 0, 0, 80, 100, corner_radius=18, visible=show_bg),
        text("文本_排名", 0, 30, 80, 60, content="1" if tier=="金" else ("2" if tier=="银" else ("3" if tier=="铜" else "4")),
             font_size=60)
    ]
    v = {"name":tier, "layers":layers}
    if is_default: v["is_default"] = True
    return v

COMPONENTS.append({
    "name":"组_排名号","w":80,"h":120,"variant_property":"排名档位",
    "variants":[make_rank_variant("金", True), make_rank_variant("银"), make_rank_variant("铜"), make_rank_variant("普通")]
})

# ----- 组_头像 (2 Variants 带装饰/无装饰) -----
def make_avatar_variant(decor, is_default=False):
    layers = [
        rect("图片_头像", 0, 0, 145, 145, corner_radius=15, element_class="dynamic"),
        {"type":"FRAME","name":"装饰_红窗帘","x":-5,"y":-25,"w":155,"h":175,"layoutMode":"NONE",
         "visible": decor,
         "children":[rect("图片_装饰红窗帘", 0, 0, 155, 175)]}
    ]
    v = {"name":"带装饰" if decor else "无装饰","layers":layers}
    if is_default: v["is_default"] = True
    return v

COMPONENTS.append({
    "name":"组_头像","w":145,"h":145,"variant_property":"框装饰",
    "variants":[make_avatar_variant(True, True), make_avatar_variant(False)]
})

# ----- 组_装饰前 (2 Variants 有/空) -----
COMPONENTS.append({
    "name":"组_装饰前","w":75,"h":75,"variant_property":"显示状态",
    "variants":[
        {"name":"有","is_default":True,"layers":[rect("图片_装饰前", 0, 0, 75, 75, element_class="dynamic")]},
        {"name":"空","layers":[]}
    ]
})

# ----- 组_道具 (2 Variants 常态/空, 用户Q3) -----
COMPONENTS.append({
    "name":"组_道具","w":160,"h":90,"variant_property":"显示状态",
    "variants":[
        {"name":"常态","is_default":True,"layers":[
            rect("图片_道具", 0, 0, 90, 90, element_class="dynamic"),
            text("文本_x数量", 95, 25, 60, 50, content="x2", font_size=38,
                 textAlignHorizontal="LEFT")
        ]},
        {"name":"空","layers":[]}
    ]
})

# ----- 组_收集物数量 (1 Variant 常态) -----
COMPONENTS.append({
    "name":"组_收集物数量","w":215,"h":100,"variant_property":"状态",
    "variants":[
        {"name":"常态","is_default":True,"layers":[
            rect("底板_数量胶囊", 30, 20, 185, 70, corner_radius=35),
            rect("图标_舵轮", 0, 0, 105, 105),
            text("文本_数量", 100, 35, 115, 50, content="000", font_size=40)
        ]}
    ]
})

# ----- 组_宝箱 (3 Variants 金/银/铜) -----
def make_box_variant(tier, is_default=False):
    show_bronze = tier == "铜"
    show_silver = tier == "银"
    show_gold = tier == "金"
    layers = [
        rect("图片_宝箱_铜", 0, 0, 170, 180, visible=show_bronze, element_class="dynamic"),
        rect("图片_宝箱_银", 0, 0, 170, 180, visible=show_silver, element_class="dynamic"),
        rect("图片_宝箱_金", 0, 0, 170, 180, visible=show_gold,   element_class="dynamic"),
    ]
    v = {"name":tier,"layers":layers}
    if is_default: v["is_default"] = True
    return v

COMPONENTS.append({
    "name":"组_宝箱","w":170,"h":180,"variant_property":"档位",
    "variants":[make_box_variant("铜", True), make_box_variant("银"), make_box_variant("金")]
})

# ----- 组_状态 (3 Variants 已完成/未完成/可领取) -----
# Variant 内部异构: 可领取内含 按钮_claim FRAME
COMPONENTS.append({
    "name":"组_状态","w":215,"h":85,"variant_property":"领取状态",
    "variants":[
        {"name":"已完成","is_default":True,"layers":[
            rect("图标_对勾", 65, 0, 85, 85)
        ]},
        {"name":"未完成","layers":[
            rect("底板_未完成数字", 0, 10, 215, 75, corner_radius=12),
            text("文本_未完成数字", 0, 22, 215, 50, content="3000", font_size=42)
        ]},
        {"name":"可领取","layers":[
            {"type":"FRAME","name":"按钮_claim","x":0,"y":10,"w":215,"h":75,"layoutMode":"NONE",
             "children":[
                 rect("底板_claim", 0, 0, 215, 75, corner_radius=12),
                 text("文本_claim", 0, 12, 215, 50, content="CLAIM", font_size=40)
             ]}
        ]}
    ]
})

# ----- 组_列表项行 (2 Variants 常态/当前用户, 父 ccb 含 5 子 ccb INSTANCE) -----
def make_list_row_variant(is_current, is_default=False):
    radius = 25 if not is_current else 26
    layers = [
        rect("底板_列表项行", 30, 5, 1020, 180, corner_radius=radius),
        instance("组_排名号", "组_排名号", "普通", 25, 35, 80, 120),
        instance("组_头像", "组_头像", "带装饰", 120, 25, 145, 145),
        instance("组_装饰前", "组_装饰前", "空", 285, 55, 75, 75),
        # 组_名字 是单实例结构, 内嵌在 layers (规则 11.5: 每个 component 内部 layers 结构一致)
        {"type":"FRAME","name":"组_名字","x":380,"y":30,"w":290,"h":130,"layoutMode":"NONE",
         "children":[
             text("文本_玩家名", 0, 0, 280, 70, content="Name", font_size=52, textAlignHorizontal="LEFT"),
             {"type":"FRAME","name":"组_副标","x":0,"y":75,"w":280,"h":50,"layoutMode":"NONE",
              "visible":True,
              "children":[
                  text("文本_副标", 0, 0, 200, 45, content="Knight", font_size=34, textAlignHorizontal="LEFT"),
                  rect("图标_盾牌", 210, 5, 38, 38)
              ]}
         ]},
        instance("组_道具", "组_道具", "空", 680, 50, 160, 90),
        instance("组_收集物数量", "组_收集物数量", "常态", 855, 55, 215, 100)
    ]
    v = {"name":"常态" if not is_current else "当前用户","layers":layers}
    if is_default: v["is_default"] = True
    return v

COMPONENTS.append({
    "name":"组_列表项行","w":1080,"h":190,"variant_property":"行状态",
    "variants":[make_list_row_variant(False, True), make_list_row_variant(True)]
})


# ===== 主屏 layers =====

# 顶部装饰区 (扁平 FRAME, 单实例)
top_decoration = {
    "type":"FRAME","name":"组_顶部装饰",
    "x":0,"y":0,"w":1080,"h":805,"layoutMode":"NONE",
    "constraints":{"horizontal":"CENTER","vertical":"TOP"},
    "children":[
        rect("底板_顶部黄色波浪", 0, 0, 1080, 340, corner_radius=0),
        text("文本_标题", 135, 95, 810, 130, content="Team Treasure", font_size=90),
        rect("图片_海盗插画", 0, 260, 1080, 440, element_class="static"),
        rect("图片_金币堆", 50, 645, 280, 145, element_class="static"),
        frame("组_倒计时", 370, 690, 325, 110, [
            rect("底板_倒计时", 0, 0, 325, 110, corner_radius=55),
            rect("图标_钟表", 20, 5, 100, 100),
            text("文本_倒计时", 130, 25, 195, 70, content="2d 1h", font_size=56)
        ]),
        frame("按钮_信息", 25, 225, 80, 80, [
            rect("底板_按钮信息", 0, 0, 80, 80, corner_radius=40),
            text("文本_按钮信息", 0, 15, 80, 50, content="i", font_size=50)
        ]),
        frame("按钮_关闭", 960, 100, 95, 95, [
            rect("底板_按钮关闭", 0, 0, 95, 95, corner_radius=47),
            text("文本_按钮关闭", 0, 18, 95, 60, content="×", font_size=60)
        ])
    ]
}

# Choisss 玩家行 (扁平 FRAME, 单实例)
choisss_row = {
    "type":"FRAME","name":"组_Choisss行",
    "x":30,"y":805,"w":1020,"h":185,"layoutMode":"NONE",
    "constraints":{"horizontal":"CENTER","vertical":"TOP"},
    "children":[
        rect("底板_Choisss行", 0, 25, 1020, 160, corner_radius=30),
        frame("角标_红三角", 30, 0, 140, 175, [
            rect("图片_红三角", 0, 0, 140, 175)
        ]),
        text("文本_玩家名Choisss", 200, 50, 480, 90, content="Choisss", font_size=64, textAlignHorizontal="LEFT"),
        frame("组_玩家分", 700, 30, 350, 140, [
            rect("图标_玩家舵轮", 0, 10, 115, 120),
            rect("底板_玩家进度胶囊", 105, 35, 245, 70, corner_radius=35),
            text("文本_玩家进度", 105, 50, 245, 45, content="1906/5000", font_size=42)
        ])
    ]
}

# 团队进度组团 (父 ccb, 单实例 → 扁平 FRAME 不抽)
# 内含 3 按钮_宝箱_N (做法 B, 内含 组_宝箱 INSTANCE) + 3 组_状态 INSTANCE
team_progress = {
    "type":"FRAME","name":"组_团队进度",
    "x":0,"y":990,"w":1080,"h":321,"layoutMode":"NONE",
    "constraints":{"horizontal":"CENTER","vertical":"TOP"},
    "children":[
        rect("底板_团队进度区", 0, 0, 1080, 321),
        rect("图标_起点舵轮", 25, 50, 155, 165),
        frame("组_进度_团队", 180, 90, 810, 75, [
            rect("底板_团队", 0, 0, 810, 75, corner_radius=37),
            rect("进度条_团队", 10, 10, 790, 55, corner_radius=27)
        ]),
        # 3 按钮_宝箱_N (做法 B 包装), 内含 组_宝箱 INSTANCE
        frame("按钮_宝箱_1", 210, 20, 170, 180, [
            instance("组_宝箱", "组_宝箱", "铜", 0, 0, 170, 180)
        ]),
        frame("按钮_宝箱_2", 470, 20, 170, 180, [
            instance("组_宝箱", "组_宝箱", "银", 0, 0, 170, 180)
        ]),
        frame("按钮_宝箱_3", 800, 20, 170, 180, [
            instance("组_宝箱", "组_宝箱", "金", 0, 0, 170, 180)
        ]),
        # 3 组_状态 INSTANCE
        instance("组_状态", "组_状态", "已完成", 85, 230, 215, 85),
        instance("组_状态", "组_状态", "未完成", 355, 230, 215, 85,
                 overrides={"文本_未完成数字":"3000"}),
        instance("组_状态", "组_状态", "未完成", 685, 230, 215, 85,
                 overrides={"文本_未完成数字":"5000"})
    ]
}

# 列表滚动区 — 13 列表项 INSTANCE
list_rows_instances = []
for i, row in enumerate(ROWS):
    rank_tier = "金" if row["rank"]==1 else ("银" if row["rank"]==2 else ("铜" if row["rank"]==3 else "普通"))
    overrides = {
        "组_排名号": rank_tier,
        "组_头像": "带装饰" if row["avatar_decor"] else "无装饰",
        "组_装饰前": "有" if row["front_decor"] else "空",
        "组_道具": "常态" if row["item"] else "空",
        "文本_玩家名": row["name"],
        "文本_数量": row["count"],
        "文本_排名": str(row["rank"]),
    }
    if row["subtitle"]:
        overrides["文本_副标"] = row["subtitle"]
    if row["item"]:
        overrides["文本_x数量"] = row["item_x"]
    list_rows_instances.append(
        instance("组_列表项行", "组_列表项行",
                 "当前用户" if row["is_current"] else "常态",
                 0, i*200, 1080, 190,
                 overrides=overrides)
    )

list_container = {
    "type":"FRAME","name":"容器_排行榜滚动区",
    "x":0,"y":1311,"w":1080,"h":1089,
    "layoutMode":"VERTICAL",
    "primaryAxisSizingMode":"FIXED","counterAxisSizingMode":"FIXED",
    "clip_content":True,"overflow":"VERTICAL",
    "constraints":{"horizontal":"CENTER","vertical":"SCALE"},
    "children":[
        {"type":"FRAME","name":"组_排行榜滚动内容",
         "layoutMode":"VERTICAL","primaryAxisSizingMode":"AUTO","counterAxisSizingMode":"FIXED",
         "layoutSizingHorizontal":"FIXED","layoutSizingVertical":"HUG",
         "itemSpacing":12,"w":1080,
         "children": list_rows_instances}
    ]
}


# ===== 顶层 final_scene.json =====
final_scene = {
    "schema_version":"v20.6",
    "screens":[{
        "name":"界面_团队宝藏",
        "type":"FRAME","w":1080,"h":2400,
        "layers":[top_decoration, choisss_row, team_progress, list_container],
        "flow":[]
    }],
    "components": COMPONENTS
}

with open("final_scene.json","w",encoding="utf-8") as f:
    json.dump(final_scene, f, ensure_ascii=False, indent=2)

print(f"final_scene.json 写出完成")
print(f"  Components 数: {len(COMPONENTS)}")
for c in COMPONENTS:
    print(f"    {c['name']}: {len(c['variants'])} Variants ({', '.join(v['name'] for v in c['variants'])})")
print(f"  列表项 INSTANCE: {len(list_rows_instances)}")
