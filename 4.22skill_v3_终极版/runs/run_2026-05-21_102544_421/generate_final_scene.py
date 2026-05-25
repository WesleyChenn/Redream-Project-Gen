"""
生成 RoyalPass final_scene.json (v20.6 schema, S11 主路径手写)
"""
import json
from copy import deepcopy

# ---------- 尺寸常量 (1080x2400 base) ----------
SCREEN_W, SCREEN_H = 1080, 2400

# 固定区
HUD_BG_H = 570       # 顶部装饰场景背景
BANNER_Y, BANNER_H = 570, 150
PROG_Y, PROG_H = 720, 180
LIST_Y, LIST_H = 900, 1500

# 列表行
ROW_H = 368
BUBBLE_W, BUBBLE_H = 400, 294
NODE_W, NODE_H = 170, 368

# 气泡内部
BADGE_W, BADGE_H = 80, 80
REWARD_W, REWARD_H = 260, 200

# 进度节点内部
BAR_BG_W = 14
BAR_BG_H = 368
DIAMOND_W, DIAMOND_H = 60, 60

# ---------- 公共字段 ----------
def constraints(h, v):
    return {"horizontal": h, "vertical": v}

# ---------- Component: 底板_气泡 ----------
def comp_底板_气泡():
    def variant(name, cr, is_default=False):
        v = {"name": name, "layers": [{
            "type": "RECTANGLE", "name": "底板_气泡",
            "x": 0, "y": 0, "w": BUBBLE_W, "h": BUBBLE_H,
            "corner_radius": cr,
            "element_class": "static",
            "constraints": constraints("SCALE", "SCALE")
        }]}
        if is_default:
            v["is_default"] = True
        return v
    return {
        "name": "底板_气泡",
        "w": BUBBLE_W, "h": BUBBLE_H,
        "variant_property": "状态",
        "variants": [
            variant("常态", 30, is_default=True),
            variant("待解锁", 31)
        ]
    }

# ---------- Component: 奖励物_关卡 (4 variants, 道具异构) ----------
def comp_奖励物():
    def 宝箱(name, cr, is_default=False):
        # corner_radius 微差让视觉签名唯一 (S7d 方法 C)
        v = {"name": name, "layers": [{
            "type": "RECTANGLE", "name": "图片_奖励",
            "x": 0, "y": 0, "w": REWARD_W, "h": REWARD_H,
            "corner_radius": cr,
            "element_class": "dynamic",
            "constraints": constraints("SCALE", "SCALE")
        }]}
        if is_default:
            v["is_default"] = True
        return v
    return {
        "name": "奖励物_关卡",
        "w": REWARD_W, "h": REWARD_H,
        "variant_property": "类型",
        "variants": [
            宝箱("金宝箱", 0, is_default=True),
            宝箱("银宝箱", 1),
            宝箱("铜宝箱", 2),
            {
                "name": "道具",
                "layers": [{
                    "type": "FRAME", "name": "组_奖励单元",
                    "x": 0, "y": 0, "w": REWARD_W, "h": REWARD_H,
                    "layoutMode": "NONE",
                    "constraints": constraints("SCALE", "SCALE"),
                    "children": [
                        {"type": "RECTANGLE", "name": "图片_奖励",
                         "x": 0, "y": 0, "w": REWARD_W, "h": 140,
                         "element_class": "dynamic",
                         "constraints": constraints("SCALE", "TOP")},
                        {"type": "TEXT", "name": "文本_数量",
                         "x": 0, "y": 150, "h": 50,
                         "content": "x1",
                         "element_class": "dynamic",
                         "font_size": 36, "font_weight": "Bold",
                         "textAlignHorizontal": "CENTER",
                         "textAlignVertical": "CENTER",
                         "constraints": constraints("SCALE", "BOTTOM")}
                    ]
                }]
            }
        ]
    }

# ---------- Component: 角标_状态 (4 variants) ----------
def comp_角标():
    return {
        "name": "角标_状态",
        "w": BADGE_W, "h": BADGE_H,
        "variant_property": "状态",
        "variants": [
            {
                "name": "锁", "is_default": True,
                "layers": [
                    {"type": "RECTANGLE", "name": "底板_角标",
                     "x": 0, "y": 0, "w": BADGE_W, "h": BADGE_H,
                     "corner_radius": 40,
                     "element_class": "static",
                     "constraints": constraints("SCALE", "SCALE")},
                    {"type": "RECTANGLE", "name": "图标_锁",
                     "x": 20, "y": 20, "w": 40, "h": 40,
                     "element_class": "static",
                     "constraints": constraints("SCALE", "SCALE")}
                ]
            },
            {
                "name": "对勾",
                "layers": [
                    {"type": "RECTANGLE", "name": "底板_角标",
                     "x": 0, "y": 0, "w": BADGE_W, "h": BADGE_H,
                     "corner_radius": 40,
                     "element_class": "static",
                     "constraints": constraints("SCALE", "SCALE")},
                    {"type": "RECTANGLE", "name": "图标_对勾",
                     "x": 18, "y": 22, "w": 44, "h": 36,
                     "element_class": "static",
                     "constraints": constraints("SCALE", "SCALE")}
                ]
            },
            {
                "name": "空",
                "layers": []
            },
            {
                "name": "可领取",
                "layers": [{
                    "type": "FRAME", "name": "组_可领取",
                    "x": 0, "y": 0, "w": BADGE_W, "h": BADGE_H,
                    "layoutMode": "NONE",
                    "constraints": constraints("SCALE", "SCALE"),
                    "children": [
                        {"type": "RECTANGLE", "name": "底板_可领取",
                         "x": 0, "y": 0, "w": BADGE_W, "h": BADGE_H,
                         "corner_radius": 16,
                         "element_class": "static",
                         "constraints": constraints("SCALE", "SCALE")},
                        {"type": "TEXT", "name": "文本_claim",
                         "x": 0, "y": 20, "w": BADGE_W, "h": 40,
                         "content": "CLAIM",
                         "element_class": "static",
                         "font_size": 22, "font_weight": "Bold",
                         "textAlignHorizontal": "CENTER",
                         "textAlignVertical": "CENTER",
                         "constraints": constraints("SCALE", "CENTER")}
                    ]
                }]
            }
        ]
    }

# ---------- Component: 组_进度节点 (2 variants 已完成/未完成) ----------
def comp_进度节点():
    bar_bg_x = (NODE_W - BAR_BG_W) // 2
    bar_fill_w = BAR_BG_W - 4
    bar_fill_x = (NODE_W - bar_fill_w) // 2
    dm_x = (NODE_W - DIAMOND_W) // 2
    dm_y = (NODE_H - DIAMOND_H) // 2

    def layers(progress_visible):
        return [
            {"type": "RECTANGLE", "name": "底板_短",
             "x": bar_bg_x, "y": 0, "w": BAR_BG_W, "h": BAR_BG_H,
             "corner_radius": 7,
             "element_class": "static",
             "constraints": constraints("CENTER", "SCALE")},
            {"type": "RECTANGLE", "name": "进度条_短",
             "x": bar_fill_x, "y": 2, "w": bar_fill_w, "h": BAR_BG_H - 4,
             "corner_radius": 5,
             "element_class": "static",
             "visible": progress_visible,
             "constraints": constraints("CENTER", "SCALE")},
            {"type": "RECTANGLE", "name": "底板_菱形",
             "x": dm_x, "y": dm_y, "w": DIAMOND_W, "h": DIAMOND_H,
             "corner_radius": 8,
             "element_class": "static",
             "constraints": constraints("CENTER", "CENTER")},
            {"type": "TEXT", "name": "文本_关卡号",
             "x": dm_x, "y": dm_y + 12, "w": DIAMOND_W, "h": 36,
             "content": "20",
             "element_class": "dynamic",
             "font_size": 30, "font_weight": "Bold",
             "textAlignHorizontal": "CENTER",
             "textAlignVertical": "CENTER",
             "constraints": constraints("CENTER", "CENTER")}
        ]

    return {
        "name": "组_进度节点",
        "w": NODE_W, "h": NODE_H,
        "variant_property": "状态",
        "variants": [
            {"name": "未完成", "is_default": True, "layers": layers(False)},
            {"name": "已完成", "layers": layers(True)}
        ]
    }

# ---------- Component: 组_气泡 (1 variant + 引用 3 孙 ccb) ----------
def comp_气泡():
    # 气泡内布局: 底板 0,0 满填; 奖励物 居中偏上; 角标 右下溢出夹断 (LEFT/TOP + 正坐标)
    reward_x = (BUBBLE_W - REWARD_W) // 2  # 70
    reward_y = 30
    badge_x = BUBBLE_W - BADGE_W - 10      # 右内 10px
    badge_y = BUBBLE_H - BADGE_H + 20      # 底部溢出 20px
    # 但按 7e §1.3: 不允许负坐标, 也不超外层 → 调整
    # 简化: 角标内置不溢出, 坐标都正
    badge_y = BUBBLE_H - BADGE_H - 10      # 右下内 10px
    layers_常态 = [
        {"type": "INSTANCE", "name": "底板_气泡",
         "component_name": "底板_气泡", "variant": "常态",
         "x": 0, "y": 0, "w": BUBBLE_W, "h": BUBBLE_H,
         "constraints": constraints("SCALE", "SCALE")},
        {"type": "INSTANCE", "name": "奖励物_关卡",
         "component_name": "奖励物_关卡", "variant": "金宝箱",
         "x": reward_x, "y": reward_y, "w": REWARD_W, "h": REWARD_H,
         "constraints": constraints("CENTER", "TOP")},
        {"type": "INSTANCE", "name": "角标_状态",
         "component_name": "角标_状态", "variant": "锁",
         "x": badge_x, "y": badge_y, "w": BADGE_W, "h": BADGE_H,
         "constraints": constraints("LEFT", "TOP")}
    ]
    # dummy 第 2 Variant: corner_radius 微差让视觉签名唯一 (S11 第 4 层)
    layers_dummy = deepcopy(layers_常态)
    layers_dummy[0]["variant"] = "待解锁"  # 底板 INSTANCE 选不同 variant 制造视觉签名差异
    return {
        "name": "组_气泡",
        "w": BUBBLE_W, "h": BUBBLE_H,
        "variant_property": "状态",
        "variants": [
            {"name": "常态", "is_default": True, "layers": layers_常态},
            {"name": "变体2", "layers": layers_dummy}
        ]
    }

# ---------- Component: 列表项_关卡奖励行 (1 variant + 引用 3 子 ccb) ----------
def comp_列表项():
    # 行内布局: 左气泡 / 进度节点 / 右气泡 横排, 居中等距
    # 用 NONE + 计算 x 位置 (主路径手写 v20.6, 不写 AL 字段在 component variant 里)
    left_x = 50
    right_x = SCREEN_W - 50 - BUBBLE_W       # = 1080-50-400 = 630
    node_x = (SCREEN_W - NODE_W) // 2        # = (1080-170)/2 = 455
    bubble_y = (ROW_H - BUBBLE_H) // 2       # = (368-294)/2 = 37
    node_y = 0
    layers_常态 = [
        {"type": "INSTANCE", "name": "组_气泡_左",
         "component_name": "组_气泡", "variant": "常态",
         "x": left_x, "y": bubble_y, "w": BUBBLE_W, "h": BUBBLE_H,
         "constraints": constraints("LEFT", "CENTER")},
        {"type": "INSTANCE", "name": "组_进度节点",
         "component_name": "组_进度节点", "variant": "未完成",
         "x": node_x, "y": node_y, "w": NODE_W, "h": NODE_H,
         "constraints": constraints("CENTER", "TOP")},
        {"type": "INSTANCE", "name": "组_气泡_右",
         "component_name": "组_气泡", "variant": "常态",
         "x": right_x, "y": bubble_y, "w": BUBBLE_W, "h": BUBBLE_H,
         "constraints": constraints("RIGHT", "CENTER")}
    ]
    # dummy 第 2 Variant: 进度节点选不同 variant 制造视觉签名差异
    layers_dummy = deepcopy(layers_常态)
    layers_dummy[1]["variant"] = "已完成"
    return {
        "name": "列表项_关卡奖励行",
        "w": SCREEN_W, "h": ROW_H,
        "variant_property": "状态",
        "variants": [
            {"name": "常态", "is_default": True, "layers": layers_常态},
            {"name": "变体2", "layers": layers_dummy}
        ]
    }

# ---------- 主屏 7 行数据 (#20-#26, 视频实测) ----------
# 每行: (左气泡 [底板v, 奖励v, 角标v, 数量文本, 关卡号], 右气泡 [...])
ROWS = [
    # (关卡号, 左[底板, 奖励, 角标, 数量], 右[底板, 奖励, 角标, 数量])
    ("20", ("常态", "铜宝箱", "对勾", None),       ("待解锁", "金宝箱", "锁", "x2")),
    ("21", ("常态", "道具",   "空",   "∞30m"),    ("待解锁", "道具",   "锁", "x2")),
    ("22", ("常态", "道具",   "对勾", "x1"),       ("待解锁", "金宝箱", "锁", "x2")),
    ("23", ("常态", "道具",   "对勾", "x1"),       ("待解锁", "银宝箱", "锁", "30m")),
    ("24", ("常态", "道具",   "对勾", "x1"),       ("待解锁", "道具",   "锁", "x3")),
    ("25", ("常态", "铜宝箱", "对勾", None),       ("待解锁", "银宝箱", "锁", None)),
    ("26", ("常态", "道具",   "对勾", "x1"),       ("待解锁", "金宝箱", "锁", "x3")),
]

def 行_INSTANCE(idx, level, left, right):
    """生成 列表项_关卡奖励行 的 INSTANCE 节点, 含 overrides

    overrides 用 path 表达深嵌套覆盖. 这里用 dict 指明每个子 INSTANCE 应选哪个 variant
    """
    overrides = {
        "组_气泡_左": "常态",   # 气泡本体只 1 variant
        "组_气泡_右": "常态",
        "组_进度节点": "未完成"  # 视频里全是未完成
    }
    # 更深层的 variant override 用 path key
    deep = {
        "组_气泡_左/底板_气泡": left[0],
        "组_气泡_左/奖励物_关卡": left[1],
        "组_气泡_左/角标_状态": left[2],
        "组_气泡_右/底板_气泡": right[0],
        "组_气泡_右/奖励物_关卡": right[1],
        "组_气泡_右/角标_状态": right[2],
        "组_进度节点/文本_关卡号": level,
    }
    if left[3]:
        deep["组_气泡_左/奖励物_关卡/文本_数量"] = left[3]
    if right[3]:
        deep["组_气泡_右/奖励物_关卡/文本_数量"] = right[3]
    overrides.update(deep)
    return {
        "type": "INSTANCE",
        "name": f"列表项_关卡奖励行_{level}",
        "component_name": "列表项_关卡奖励行",
        "variant": "常态",
        "x": 0, "y": idx * ROW_H,
        "w": SCREEN_W, "h": ROW_H,
        "constraints": constraints("CENTER", "TOP"),
        "overrides": overrides
    }

# ---------- 主屏 ----------
def 主屏():
    layers = []

    # 0. 顶部装饰场景背景
    layers.append({
        "type": "RECTANGLE", "name": "图片_顶部场景",
        "x": 0, "y": 0, "w": SCREEN_W, "h": HUD_BG_H,
        "element_class": "static",
        "constraints": constraints("CENTER", "TOP")
    })

    # 1. 按钮_i (左上)
    layers.append({
        "type": "FRAME", "name": "按钮_i",
        "x": 44, "y": 132, "w": 92, "h": 92,
        "layoutMode": "NONE",
        "corner_radius": 46,
        "constraints": constraints("LEFT", "TOP"),
        "children": [
            {"type": "RECTANGLE", "name": "底板_i",
             "x": 0, "y": 0, "w": 92, "h": 92,
             "corner_radius": 46,
             "element_class": "static",
             "constraints": constraints("SCALE", "SCALE")},
            {"type": "TEXT", "name": "文本_i",
             "x": 0, "y": 0, "w": 92, "h": 92,
             "content": "i",
             "element_class": "static",
             "font_size": 56, "font_weight": "Bold",
             "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
             "constraints": constraints("SCALE", "SCALE")}
        ]
    })

    # 2. 按钮_X (右上)
    layers.append({
        "type": "FRAME", "name": "按钮_X",
        "x": 944, "y": 132, "w": 92, "h": 92,
        "layoutMode": "NONE",
        "corner_radius": 46,
        "constraints": constraints("RIGHT", "TOP"),
        "children": [
            {"type": "RECTANGLE", "name": "底板_X",
             "x": 0, "y": 0, "w": 92, "h": 92,
             "corner_radius": 46,
             "element_class": "static",
             "constraints": constraints("SCALE", "SCALE")},
            {"type": "TEXT", "name": "文本_X",
             "x": 0, "y": 0, "w": 92, "h": 92,
             "content": "X",
             "element_class": "static",
             "font_size": 56, "font_weight": "Bold",
             "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
             "constraints": constraints("SCALE", "SCALE")}
        ]
    })

    # 3. Banner_RoyalPass
    layers.append({
        "type": "FRAME", "name": "组_Banner",
        "x": 0, "y": BANNER_Y, "w": SCREEN_W, "h": BANNER_H,
        "layoutMode": "NONE",
        "constraints": constraints("CENTER", "TOP"),
        "children": [
            {"type": "RECTANGLE", "name": "底板_Banner",
             "x": 0, "y": 0, "w": SCREEN_W, "h": BANNER_H,
             "element_class": "static",
             "constraints": constraints("SCALE", "SCALE")},
            {"type": "TEXT", "name": "文本_RoyalPass",
             "x": 0, "y": 30, "w": SCREEN_W, "h": 60,
             "content": "Royal Pass",
             "element_class": "static",
             "font_size": 52, "font_weight": "Bold",
             "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
             "constraints": constraints("CENTER", "TOP")},
            {"type": "RECTANGLE", "name": "图标_沙漏",
             "x": 440, "y": 95, "w": 40, "h": 40,
             "element_class": "static",
             "constraints": constraints("CENTER", "BOTTOM")},
            {"type": "TEXT", "name": "文本_倒计时",
             "x": 490, "y": 95, "w": 200, "h": 40,
             "content": "23d 22h",
             "element_class": "dynamic",
             "font_size": 32, "textAlignHorizontal": "LEFT", "textAlignVertical": "CENTER",
             "constraints": constraints("CENTER", "BOTTOM")}
        ]
    })

    # 4. 进度条区_季票
    layers.append({
        "type": "FRAME", "name": "组_进度_季票区",
        "x": 0, "y": PROG_Y, "w": SCREEN_W, "h": PROG_H,
        "layoutMode": "NONE",
        "constraints": constraints("CENTER", "TOP"),
        "children": [
            # 左 icon 钥匙
            {"type": "RECTANGLE", "name": "图标_钥匙",
             "x": 40, "y": 50, "w": 80, "h": 80,
             "element_class": "static",
             "constraints": constraints("LEFT", "CENTER")},
            # 进度条三层
            {"type": "FRAME", "name": "组_进度_季票",
             "x": 120, "y": 70, "w": 540, "h": 60,
             "layoutMode": "NONE",
             "constraints": constraints("CENTER", "CENTER"),
             "children": [
                 {"type": "RECTANGLE", "name": "底板_季票",
                  "x": 0, "y": 0, "w": 540, "h": 60,
                  "corner_radius": 30,
                  "element_class": "static",
                  "constraints": constraints("SCALE", "SCALE")},
                 {"type": "RECTANGLE", "name": "进度条_季票",
                  "x": 10, "y": 10, "w": 520, "h": 40,
                  "corner_radius": 20,
                  "element_class": "static",
                  "constraints": constraints("SCALE", "SCALE")}
             ]},
            # 文本 39/40 居中覆盖
            {"type": "TEXT", "name": "文本_季票_进度",
             "x": 250, "y": 75, "w": 200, "h": 50,
             "content": "39/40",
             "element_class": "dynamic",
             "font_size": 34, "font_weight": "Bold",
             "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
             "constraints": constraints("CENTER", "CENTER")},
            # 右端节点 钻石+21
            {"type": "RECTANGLE", "name": "图标_钻石",
             "x": 660, "y": 50, "w": 80, "h": 80,
             "element_class": "static",
             "constraints": constraints("CENTER", "CENTER")},
            {"type": "TEXT", "name": "文本_钻石数",
             "x": 660, "y": 60, "w": 80, "h": 60,
             "content": "21",
             "element_class": "static",
             "font_size": 32, "font_weight": "Bold",
             "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
             "constraints": constraints("CENTER", "CENTER")},
            # Activate 按钮
            {"type": "FRAME", "name": "按钮_Activate",
             "x": 770, "y": 50, "w": 270, "h": 80,
             "layoutMode": "NONE",
             "corner_radius": 40,
             "constraints": constraints("RIGHT", "CENTER"),
             "children": [
                 {"type": "RECTANGLE", "name": "底板_Activate",
                  "x": 0, "y": 0, "w": 270, "h": 80,
                  "corner_radius": 40,
                  "element_class": "static",
                  "constraints": constraints("SCALE", "SCALE")},
                 {"type": "TEXT", "name": "文本_Activate",
                  "x": 0, "y": 0, "w": 270, "h": 80,
                  "content": "Activate",
                  "element_class": "static",
                  "font_size": 36, "font_weight": "Bold",
                  "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
                  "constraints": constraints("SCALE", "SCALE")}
             ]}
        ]
    })

    # 5. 滚动列表区
    list_children = []
    for i, (level, left, right) in enumerate(ROWS):
        list_children.append(行_INSTANCE(i, level, left, right))

    layers.append({
        "type": "FRAME", "name": "容器_关卡奖励滚动",
        "x": 0, "y": LIST_Y, "w": SCREEN_W, "h": LIST_H,
        "layoutMode": "VERTICAL",
        "primaryAxisSizingMode": "FIXED",
        "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "MIN",
        "counterAxisAlignItems": "CENTER",
        "clip_content": True,
        "overflow": "VERTICAL",
        "constraints": constraints("CENTER", "SCALE"),
        "children": [{
            "type": "FRAME", "name": "组_滚动内容",
            "layoutMode": "VERTICAL",
            "primaryAxisSizingMode": "AUTO",
            "counterAxisSizingMode": "FIXED",
            "primaryAxisAlignItems": "MIN",
            "counterAxisAlignItems": "CENTER",
            "layoutSizingHorizontal": "FIXED",
            "layoutSizingVertical": "HUG",
            "itemSpacing": 0,
            "x": 0, "y": 0, "w": SCREEN_W,
            "children": list_children
        }]
    })

    return {
        "name": "界面_RoyalPass",
        "type": "FRAME",
        "w": SCREEN_W, "h": SCREEN_H,
        "layers": layers,
        "flow": []
    }

# ---------- 组装 ----------
def main():
    components = [
        comp_底板_气泡(),       # 孙
        comp_奖励物(),          # 孙
        comp_角标(),            # 孙
        comp_进度节点(),        # 子 (无嵌套 INSTANCE)
        comp_气泡(),            # 子 (引用 3 孙)
        comp_列表项()           # 大 (引用 进度节点 + 气泡×2)
    ]
    data = {
        "screens": [主屏()],
        "components": components
    }
    with open("/Users/red/Desktop/5.21工作流/4.22skill_v3_只停S6/runs/run_2026-05-21_102544_421/final_scene.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ 生成完成: final_scene.json")
    print(f"   components: {len(components)} 个")
    for c in components:
        print(f"     • {c['name']}: {len(c['variants'])} Variant(s) — {[v['name'] for v in c['variants']]}")
    print(f"   主屏 layers: {len(data['screens'][0]['layers'])}")
    print(f"   列表行实例: {len(ROWS)}")

if __name__ == "__main__":
    main()
