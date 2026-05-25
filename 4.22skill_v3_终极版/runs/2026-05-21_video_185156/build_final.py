#!/usr/bin/env python3
"""S11 主路径: 从扁平 scene.json 构造 v20.6 schema final_scene.json"""
import json, copy

# 通用 helper
def rect(name, x, y, w, h, cr=0, vis=True, elem='static', extra=None):
    r = {"type": "RECTANGLE", "name": name, "x": x, "y": y, "w": w, "h": h,
         "element_class": elem}
    if cr: r["corner_radius"] = cr
    if not vis: r["visible"] = False
    if extra: r.update(extra)
    return r

def text(name, x, y, w, h, content="", fs=32, fw="Bold", ah="CENTER", av="CENTER", vis=True, elem='dynamic'):
    t = {"type": "TEXT", "name": name, "x": x, "y": y, "w": w, "h": h,
         "content": content, "font_size": fs, "font_weight": fw,
         "textAlignHorizontal": ah, "textAlignVertical": av,
         "element_class": elem}
    if not vis: t["visible"] = False
    return t

def inst(name, comp, variant, x, y, w, h, ov=None, vis=True, extra=None):
    i = {"type": "INSTANCE", "name": name, "component_name": comp, "variant": variant,
         "x": x, "y": y, "w": w, "h": h}
    if ov: i["overrides"] = ov
    if not vis: i["visible"] = False
    if extra: i.update(extra)
    return i

# ============================================================
# components[]
# ============================================================
components = []

# 1. 宝箱 (3 variants: 金/银/铜)
components.append({
    "name": "宝箱", "w": 146, "h": 150, "variant_property": "宝箱色",
    "variants": [
        {"name": "金", "is_default": True, "layers": [
            rect("图片_宝箱", 0, 0, 146, 150, cr=20, elem='dynamic')]},
        {"name": "银", "layers": [
            rect("图片_宝箱", 0, 0, 146, 150, cr=21, elem='dynamic')]},
        {"name": "铜", "layers": [
            rect("图片_宝箱", 0, 0, 146, 150, cr=22, elem='dynamic')]},
    ]
})

# 2. 状态 (3 variants: 已完成 / 未完成 / 可领取)
def state_layers(visible_set):
    return [
        rect("底板_状态", 0, 8, 130, 56, cr=28, vis=("底板" in visible_set)),
        text("文本_状态_阈值", 0, 18, 130, 36, "", fs=32, vis=("阈值" in visible_set)),
        rect("图标_状态_对勾", 38, 5, 55, 60, cr=28, vis=("对勾" in visible_set), elem='static'),
        text("文本_状态_claim", 0, 18, 130, 36, "claim", fs=28, vis=("claim" in visible_set)),
    ]

components.append({
    "name": "状态", "w": 130, "h": 71, "variant_property": "状态",
    "variants": [
        {"name": "已完成", "is_default": True, "layers": state_layers({"对勾"})},
        {"name": "未完成", "layers": state_layers({"底板","阈值"})},
        {"name": "可领取", "layers": state_layers({"底板","claim"})},
    ]
})

# 3. 组_节点 (1 variant; 内部含 2 个子 INSTANCE)
components.append({
    "name": "组_节点", "w": 180, "h": 240, "variant_property": "默认",
    "variants": [{
        "name": "默认", "is_default": True, "layers": [
            inst("组_宝箱", "宝箱", "金", 17, 0, 146, 150),
            inst("组_状态", "状态", "已完成", 25, 169, 130, 71),
        ]
    }]
})

# 4. 排名 (4 variants: 金/银/铜/普通)
def rank_layers(cr, base_vis):
    return [
        rect("底板_排名", 0, 0, 119, 122, cr=cr, vis=base_vis),
        text("文本_排名", 0, 0, 119, 122, "1", fs=56),
    ]

components.append({
    "name": "排名", "w": 119, "h": 122, "variant_property": "排名",
    "variants": [
        {"name": "金", "is_default": True, "layers": rank_layers(15, True)},
        {"name": "银", "layers": rank_layers(16, True)},
        {"name": "铜", "layers": rank_layers(17, True)},
        {"name": "普通", "layers": rank_layers(0, False)},
    ]
})

# 5. 头像 (2 variants: 带装饰/不带装饰)
def avatar_layers(huan_vis):
    return [
        rect("图片_头像", 8, 8, 130, 130, cr=65, elem='dynamic'),
        rect("图标_花环", 0, 0, 146, 146, cr=73, vis=huan_vis, elem='static'),
    ]

components.append({
    "name": "头像", "w": 146, "h": 146, "variant_property": "装饰",
    "variants": [
        {"name": "带装饰", "is_default": True, "layers": avatar_layers(True)},
        {"name": "不带装饰", "layers": avatar_layers(False)},
    ]
})

# 6. 组_名字前装饰 (2 variants: 有/空)
components.append({
    "name": "组_名字前装饰", "w": 40, "h": 40, "variant_property": "状态",
    "variants": [
        {"name": "有", "is_default": True, "layers": [
            rect("图标_装饰", 0, 0, 40, 40, cr=20, elem='static')]},
        {"name": "空", "layers": []},
    ]
})

# 7. 组_名字后道具 (1 variant)
components.append({
    "name": "组_名字后道具", "w": 200, "h": 36, "variant_property": "状态",
    "variants": [{
        "name": "常态", "is_default": True, "layers": [
            rect("图标_道具", 0, 0, 36, 36, elem='static'),
            text("文本_道具", 42, 0, 158, 36, "Knight", fs=28, ah="LEFT"),
        ]
    }]
})

# 8. 组_收集物数量 (1 variant)
components.append({
    "name": "组_收集物数量", "w": 200, "h": 84, "variant_property": "状态",
    "variants": [{
        "name": "常态", "is_default": True, "layers": [
            rect("底板_徽章", 25, 12, 175, 60, cr=30),
            rect("图标_徽章", 0, 0, 70, 84, elem='dynamic'),
            text("文本_徽章_数字", 75, 18, 115, 48, "529", fs=36),
        ]
    }]
})

# 9. 列表项 (2 variants: 常态/当前用户)
def list_layers(row_cr):
    return [
        # 底板 ABSOLUTE 脱离 AL 流
        {"type": "RECTANGLE", "name": "底板_行", "x": 0, "y": 0, "w": 1044, "h": 188,
         "corner_radius": row_cr, "layoutPositioning": "ABSOLUTE", "element_class": "static"},
        inst("组_排名", "排名", "金", 25, 33, 119, 122),
        inst("组_头像", "头像", "带装饰", 160, 21, 146, 146),
        {
            "type": "FRAME", "name": "组_名字",
            "x": 322, "y": 29, "w": 410, "h": 130,
            "layoutMode": "VERTICAL",
            "primaryAxisSizingMode": "FIXED",
            "counterAxisSizingMode": "FIXED",
            "primaryAxisAlignItems": "CENTER",
            "counterAxisAlignItems": "MIN",
            "itemSpacing": 6,
            "children": [
                {
                    "type": "FRAME", "name": "组_名字行",
                    "layoutMode": "HORIZONTAL",
                    "primaryAxisSizingMode": "AUTO",
                    "counterAxisSizingMode": "AUTO",
                    "primaryAxisAlignItems": "MIN",
                    "counterAxisAlignItems": "CENTER",
                    "itemSpacing": 8,
                    "layoutSizingHorizontal": "HUG",
                    "layoutSizingVertical": "HUG",
                    "children": [
                        inst("组_名字前装饰", "组_名字前装饰", "有", 0, 0, 40, 40),
                        text("文本_玩家名", 48, 0, 200, 50, "Name", fs=44, ah="LEFT"),
                    ]
                },
                inst("组_名字后道具", "组_名字后道具", "常态", 0, 56, 200, 36),
            ]
        },
        {"type": "FRAME", "name": "弹性缝隙", "x": 748, "y": 0, "w": 0, "h": 0,
         "layoutMode": "NONE", "layoutSizingHorizontal": "FILL"},
        inst("组_收集物数量", "组_收集物数量", "常态", 819, 52, 200, 84),
    ]

components.append({
    "name": "列表项", "w": 1044, "h": 188, "variant_property": "状态",
    "variants": [
        {"name": "常态", "is_default": True, "layers": list_layers(25)},
        {"name": "当前用户", "layers": list_layers(26)},
    ]
})

# ============================================================
# screens[].layers
# ============================================================
screen_layers = [
    rect("背景_TeamTreasure场景", 0, 0, 1080, 2400, elem='static',
         extra={"constraints": {"horizontal": "CENTER", "vertical": "CENTER"}}),
    {
        "type": "FRAME", "name": "组_标题栏",
        "x": 0, "y": 0, "w": 1080, "h": 340,
        "layoutMode": "NONE",
        "constraints": {"horizontal": "CENTER", "vertical": "TOP"},
        "children": [
            rect("底板_TeamTreasure_banner", 120, 84, 840, 170, cr=20),
            text("文本_TeamTreasure_标题", 120, 110, 840, 110, "Team Treasure", fs=72, elem='static'),
            rect("图标_步骤1", 46, 262, 73, 75, elem='static'),
            {
                "type": "FRAME", "name": "按钮_关闭",
                "x": 945, "y": 50, "w": 110, "h": 110,
                "layoutMode": "NONE",
                "children": [
                    rect("底板_按钮_关闭", 0, 0, 110, 110, cr=55),
                    text("文本_按钮_关闭", 0, 0, 110, 110, "X", fs=56, elem='static'),
                ]
            }
        ]
    },
    {
        "type": "FRAME", "name": "容器_插画区",
        "x": 0, "y": 340, "w": 1080, "h": 640,
        "layoutMode": "NONE",
        "constraints": {"horizontal": "CENTER", "vertical": "CENTER"},
        "children": [
            rect("图片_海盗船长场景", 0, 0, 1080, 640, elem='dynamic'),
            {
                "type": "FRAME", "name": "徽章_时间",
                "x": 27, "y": 91, "w": 220, "h": 80,
                "layoutMode": "NONE",
                "children": [
                    rect("底板_徽章", 25, 5, 195, 70, cr=35),
                    rect("图标_徽章", 0, 0, 80, 80, elem='static'),
                    text("文本_徽章_数字", 90, 18, 130, 44, "2d 1h", fs=32),
                ]
            }
        ]
    },
    {
        "type": "FRAME", "name": "容器_进度面板",
        "x": 27, "y": 980, "w": 1025, "h": 468,
        "layoutMode": "NONE",
        "constraints": {"horizontal": "CENTER", "vertical": "TOP"},
        "children": [
            rect("底板_进度面板", 0, 32, 1025, 412, cr=30),
            {
                "type": "FRAME", "name": "组_玩家名行",
                "x": 19, "y": 32, "w": 990, "h": 130,
                "layoutMode": "HORIZONTAL",
                "primaryAxisSizingMode": "FIXED",
                "counterAxisSizingMode": "FIXED",
                "primaryAxisAlignItems": "MIN",
                "counterAxisAlignItems": "CENTER",
                "itemSpacing": 16,
                "paddingLeft": 0, "paddingRight": 20,
                "children": [
                    rect("图标_玩家旗", 0, 0, 128, 130, elem='static'),
                    text("文本_玩家名", 0, 0, 0, 64, "Choisss", fs=56, ah="LEFT"),
                    {"type": "FRAME", "name": "弹性缝隙", "x": 0, "y": 0, "w": 0, "h": 0,
                     "layoutMode": "NONE", "layoutSizingHorizontal": "FILL"},
                    text("文本_进度数", 0, 0, 0, 64, "1906 / 5000", fs=48, ah="RIGHT"),
                ]
            },
            {
                "type": "FRAME", "name": "组_进度_TeamTreasure",
                "x": 35, "y": 207, "w": 955, "h": 60,
                "layoutMode": "NONE",
                "children": [
                    rect("底板_TeamTreasure", 0, 0, 955, 60, cr=30),
                    rect("进度条_TeamTreasure", 10, 10, 935, 40, cr=20),
                ]
            },
            inst("组_节点_1", "组_节点", "默认", 73, 145, 180, 240,
                 ov={"组_宝箱": "金", "组_状态": "已完成"}),
            inst("组_节点_2", "组_节点", "默认", 456, 145, 180, 240,
                 ov={"组_宝箱": "银", "组_状态": "未完成", "文本_状态_阈值": "3000"}),
            inst("组_节点_3", "组_节点", "默认", 833, 145, 180, 240,
                 ov={"组_宝箱": "铜", "组_状态": "未完成", "文本_状态_阈值": "5000"}),
        ]
    },
    {
        "type": "FRAME", "name": "容器_排行榜滚动区",
        "x": 18, "y": 1448, "w": 1044, "h": 952,
        "layoutMode": "VERTICAL",
        "primaryAxisSizingMode": "FIXED",
        "counterAxisSizingMode": "FIXED",
        "clip_content": True, "overflow": "VERTICAL",
        "constraints": {"horizontal": "CENTER", "vertical": "SCALE"},
        "children": [
            {
                "type": "FRAME", "name": "组_滚动内容",
                "x": 0, "y": 0, "w": 1044, "h": 0,
                "layoutMode": "VERTICAL",
                "primaryAxisSizingMode": "AUTO",
                "counterAxisSizingMode": "FIXED",
                "layoutSizingHorizontal": "FIXED",
                "layoutSizingVertical": "HUG",
                "itemSpacing": 8,
                "children": [
                    inst("列表项_1", "列表项", "常态", 0, 0, 1044, 188, ov={
                        "组_排名": "金", "文本_排名": "1", "组_头像": "带装饰",
                        "组_名字前装饰": "有", "文本_玩家名": "medi___",
                        "组_名字后道具": "常态", "文本_道具": "",
                        "文本_徽章_数字": "529"
                    }),
                    inst("列表项_2", "列表项", "常态", 0, 0, 1044, 188, ov={
                        "组_排名": "银", "文本_排名": "2", "组_头像": "不带装饰",
                        "组_名字前装饰": "空", "文本_玩家名": "Onon",
                        "文本_徽章_数字": "419"
                    }, extra={}),
                    inst("列表项_3", "列表项", "常态", 0, 0, 1044, 188, ov={
                        "组_排名": "铜", "文本_排名": "3", "组_头像": "不带装饰",
                        "组_名字前装饰": "空", "文本_玩家名": "Choy",
                        "文本_徽章_数字": "244"
                    }),
                    inst("列表项_4", "列表项", "常态", 0, 0, 1044, 188, ov={
                        "组_排名": "普通", "文本_排名": "4", "组_头像": "不带装饰",
                        "组_名字前装饰": "空", "文本_玩家名": "Inle",
                        "组_名字后道具": "常态", "文本_道具": "Knight",
                        "文本_徽章_数字": "129"
                    }),
                    inst("列表项_5", "列表项", "当前用户", 0, 0, 1044, 188, ov={
                        "组_排名": "普通", "文本_排名": "6", "组_头像": "不带装饰",
                        "组_名字前装饰": "空", "文本_玩家名": "mmmmm",
                        "组_名字后道具": "常态", "文本_道具": "Knight",
                        "文本_徽章_数字": "109"
                    }),
                    inst("列表项_6", "列表项", "常态", 0, 0, 1044, 188, ov={
                        "组_排名": "普通", "文本_排名": "8", "组_头像": "不带装饰",
                        "组_名字前装饰": "空", "文本_玩家名": "Arthur",
                        "文本_徽章_数字": "65"
                    }),
                ]
            }
        ]
    }
]

final = {
    "screens": [{
        "name": "界面_TeamTreasure", "type": "FRAME",
        "w": 1080, "h": 2400, "layers": screen_layers, "flow": []
    }],
    "components": components,
}

with open("final_scene.json", "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

print(f"final_scene.json 已生成")
print(f"  components: {len(components)}")
for c in components:
    print(f"    - {c['name']:20s} {c['w']:4d}x{c['h']:4d} variants={len(c['variants'])} ({[v['name'] for v in c['variants']]})")
print(f"  screen layers: {len(screen_layers)}")
