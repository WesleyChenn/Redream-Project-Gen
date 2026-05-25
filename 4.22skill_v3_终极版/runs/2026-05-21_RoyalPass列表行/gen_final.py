"""S11 主路径 — Claude 直接产 v20.6 schema final_scene.json.
抽 4 个最小单元 Component, 大组团 (列表项) + 中间组团 (气泡) 扁平 FRAME 含 INSTANCE.
"""
import json

# === 尺寸常量 (跟 gen_scene.py 一致) ===
W_SCREEN, H_SCREEN = 1080, 2400
W_ITEM, H_ITEM = 1080, 362
W_BUBBLE, H_BUBBLE = 363, 205
W_NODE, H_NODE = 110, 120
W_REWARD_BOX, H_REWARD_BOX = 180, 140
X_REWARD_BOX = (W_BUBBLE - W_REWARD_BOX) // 2
Y_REWARD_BOX = 25
W_BADGE, H_BADGE = 80, 80
X_BADGE = W_BUBBLE - W_BADGE - 10
Y_BADGE = H_BUBBLE - H_BADGE - 10

CR_BUBBLE_NORMAL = 100
CR_BUBBLE_LOCKED = 101
CR_NODE_DONE = 10
CR_NODE_UNDONE = 11


# === 4 个最小单元 Component 的 Variant.layers 模板 ===

def variant_底板气泡(name, cr, is_default=False):
    """组_底板气泡 Variant: 单 RECT, corner_radius 微差."""
    return {
        "name": name, "is_default": is_default,
        "layers": [{
            "type": "RECTANGLE", "name": "底板_气泡",
            "x": 0, "y": 0, "w": W_BUBBLE, "h": H_BUBBLE,
            "corner_radius": cr,
            "element_class": "static",
            "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}
        }]
    }


def variant_奖励物(name, is_default=False, item=False):
    """组_奖励物 Variant: 单 icon (金/银/铜) 或 异构 含数量 TEXT (道具).
    Variant 内部异构 (07d #2.5).
    """
    layers = [{
        "type": "RECTANGLE", "name": "图片_奖励物",
        "x": 0, "y": 0, "w": W_REWARD_BOX, "h": H_REWARD_BOX,
        "element_class": "dynamic",
        "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}
    }]
    if item:
        layers.append({
            "type": "TEXT", "name": "文本_数量",
            "content": "x1",  # 占位, INSTANCE.overrides 覆盖实际值
            "x": 0, "y": H_REWARD_BOX - 40, "w": W_REWARD_BOX, "h": 35,
            "font_size": 32, "font_weight": 700,
            "textAlignHorizontal": "CENTER", "textAlignVertical": "BOTTOM",
            "element_class": "dynamic",
            "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}
        })
    return {"name": name, "is_default": is_default, "layers": layers}


def variant_角标(name, icon_name=None, is_default=False, empty=False):
    """角标_状态 Variant: 底板 + 1 个图标. "空" Variant layers=[]."""
    if empty:
        return {"name": name, "is_default": is_default, "layers": []}
    layers = [{
        "type": "RECTANGLE", "name": "底板_圆角标",
        "x": 0, "y": 0, "w": W_BADGE, "h": H_BADGE,
        "corner_radius": 40,
        "element_class": "static",
        "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}
    }]
    if icon_name:
        layers.append({
            "type": "RECTANGLE", "name": icon_name,
            "x": 15, "y": 15, "w": W_BADGE - 30, "h": H_BADGE - 30,
            "element_class": "static",
            "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}
        })
    return {"name": name, "is_default": is_default, "layers": layers}


def variant_节点(name, cr, is_default=False):
    """组_节点 Variant: 底板菱形 + 数字 TEXT."""
    return {
        "name": name, "is_default": is_default,
        "layers": [
            {
                "type": "RECTANGLE", "name": "底板_菱形",
                "x": 0, "y": 0, "w": W_NODE, "h": H_NODE,
                "corner_radius": cr,
                "element_class": "static",
                "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}
            },
            {
                "type": "TEXT", "name": "文本_关卡号",
                "content": "20",  # 占位
                "x": 0, "y": (H_NODE - 50) // 2, "w": W_NODE, "h": 50,
                "font_size": 44, "font_weight": 700,
                "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
                "element_class": "dynamic",
                "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}
            }
        ]
    }


COMPONENTS = [
    {
        "name": "组_底板气泡",
        "w": W_BUBBLE, "h": H_BUBBLE,
        "variant_property": "状态",
        "variants": [
            variant_底板气泡("常态", CR_BUBBLE_NORMAL, is_default=True),
            variant_底板气泡("待解锁", CR_BUBBLE_LOCKED),
        ]
    },
    {
        "name": "组_奖励物",
        "w": W_REWARD_BOX, "h": H_REWARD_BOX,
        "variant_property": "类型",
        "variants": [
            variant_奖励物("金宝箱", is_default=False),
            variant_奖励物("银宝箱"),
            variant_奖励物("铜宝箱"),
            variant_奖励物("道具", is_default=True, item=True),
        ]
    },
    {
        "name": "角标_状态",
        "w": W_BADGE, "h": H_BADGE,
        "variant_property": "状态",
        "variants": [
            variant_角标("锁", icon_name="图标_锁", is_default=True),
            variant_角标("对勾", icon_name="图标_对勾"),
            variant_角标("可领取", icon_name="图标_可领取"),
            variant_角标("空", empty=True),
        ]
    },
    {
        "name": "组_节点",
        "w": W_NODE, "h": H_NODE,
        "variant_property": "状态",
        "variants": [
            variant_节点("已完成", CR_NODE_DONE, is_default=True),
            variant_节点("未完成", CR_NODE_UNDONE),
        ]
    },
]


# === 主屏 INSTANCE 构造 ===

def inst_底板气泡(variant):
    return {
        "type": "INSTANCE", "name": "组_底板气泡",
        "component_name": "组_底板气泡", "variant": variant,
        "x": 0, "y": 0, "w": W_BUBBLE, "h": H_BUBBLE,
        "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}
    }


def inst_奖励物(variant, num_text=""):
    inst = {
        "type": "INSTANCE", "name": "组_奖励物",
        "component_name": "组_奖励物", "variant": variant,
        "x": X_REWARD_BOX, "y": Y_REWARD_BOX, "w": W_REWARD_BOX, "h": H_REWARD_BOX,
        "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}
    }
    if variant == "道具" and num_text:
        inst["overrides"] = {"文本_数量": num_text}
    return inst


def inst_角标(variant):
    return {
        "type": "INSTANCE", "name": "角标_状态",
        "component_name": "角标_状态", "variant": variant,
        "x": X_BADGE, "y": Y_BADGE, "w": W_BADGE, "h": H_BADGE,
        "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}
    }


def inst_节点(variant, 关卡号):
    return {
        "type": "INSTANCE", "name": "组_节点",
        "component_name": "组_节点", "variant": variant,
        "w": W_NODE, "h": H_NODE,
        "overrides": {"文本_关卡号": str(关卡号)}
    }


def make_气泡(name, 底板_variant, 奖励物_variant, 奖励物_num, 角标_variant):
    """气泡 = 扁平 FRAME (中间组团), 内含 3 个 INSTANCE."""
    return {
        "type": "FRAME", "name": name,
        "w": W_BUBBLE, "h": H_BUBBLE,
        "layoutMode": "NONE",
        "children": [
            inst_底板气泡(底板_variant),
            inst_奖励物(奖励物_variant, 奖励物_num),
            inst_角标(角标_variant)
        ]
    }


def make_列表项(行号, 左_底板, 左_奖励, 左_数量, 左_角标, 节点_state,
                 右_底板, 右_奖励, 右_数量, 右_角标):
    """列表项 = 扁平 FRAME (大组团), HORIZONTAL AL."""
    return {
        "type": "FRAME", "name": "列表项_关卡奖励",
        "w": W_ITEM, "h": H_ITEM,
        "layoutMode": "HORIZONTAL",
        "primaryAxisSizingMode": "FIXED",
        "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "SPACE_BETWEEN",
        "counterAxisAlignItems": "CENTER",
        "paddingLeft": 70, "paddingRight": 70,
        "paddingTop": 0, "paddingBottom": 0,
        "children": [
            make_气泡("气泡_左", 左_底板, 左_奖励, 左_数量, 左_角标),
            inst_节点(节点_state, 行号),
            make_气泡("气泡_右", 右_底板, 右_奖励, 右_数量, 右_角标),
        ]
    }


ROWS = [
    ("20", "常态", "道具", "x1",  "对勾",  "已完成", "常态",   "道具",   "x2", "锁"),
    ("21", "常态", "铜宝箱", "",  "对勾",  "已完成", "常态",   "道具",   "x1", "锁"),
    ("25", "常态", "道具", "x1",  "空",    "已完成", "常态",   "银宝箱", "",   "锁"),
    ("23", "常态", "道具", "x1",  "空",    "已完成", "待解锁", "道具",   "x1", "锁"),
    ("40", "常态", "铜宝箱", "",  "空",    "未完成", "常态",   "金宝箱", "",   "可领取"),
]


# === 顶部装饰区 / HUD / 主进度条 (保持扁平, 加 element_class) ===

def make_顶部装饰区():
    return {
        "type": "FRAME", "name": "组_顶部装饰",
        "x": 0, "y": 0, "w": 1080, "h": 410,
        "layoutMode": "NONE",
        "constraints": {"horizontal": "CENTER", "vertical": "TOP"},
        "children": [
            {
                "type": "RECTANGLE", "name": "背景_顶部装饰",
                "x": 0, "y": 0, "w": 1080, "h": 410,
                "element_class": "static",
                "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}
            },
            {
                "type": "RECTANGLE", "name": "图片_装饰_宝箱堆",
                "x": 0, "y": 30, "w": 1080, "h": 220,
                "element_class": "static",
                "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}
            },
            {
                "type": "RECTANGLE", "name": "图片_装饰_金宝箱中央",
                "x": 380, "y": 100, "w": 320, "h": 280,
                "element_class": "static",
                "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}
            }
        ]
    }


def make_顶部HUD():
    return {
        "type": "FRAME", "name": "组_顶部HUD",
        "x": 0, "y": 410, "w": 1080, "h": 110,
        "layoutMode": "HORIZONTAL",
        "primaryAxisSizingMode": "FIXED",
        "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "SPACE_BETWEEN",
        "counterAxisAlignItems": "CENTER",
        "paddingLeft": 30, "paddingRight": 30,
        "constraints": {"horizontal": "CENTER", "vertical": "TOP"},
        "children": [
            {
                "type": "FRAME", "name": "按钮_信息",
                "w": 80, "h": 80,
                "layoutMode": "NONE",
                "children": [
                    {"type": "RECTANGLE", "name": "底板_按钮",
                     "x": 0, "y": 0, "w": 80, "h": 80, "corner_radius": 40,
                     "element_class": "static",
                     "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
                    {"type": "TEXT", "name": "文本_i",
                     "content": "i",
                     "x": 0, "y": 15, "w": 80, "h": 50,
                     "font_size": 44, "font_weight": 700,
                     "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
                     "element_class": "static",
                     "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}}
                ]
            },
            {
                "type": "FRAME", "name": "组_标题",
                "w": 600, "h": 110,
                "layoutMode": "VERTICAL",
                "primaryAxisSizingMode": "FIXED",
                "counterAxisSizingMode": "FIXED",
                "primaryAxisAlignItems": "CENTER",
                "counterAxisAlignItems": "CENTER",
                "itemSpacing": 4,
                "children": [
                    {"type": "TEXT", "name": "文本_标题",
                     "content": "Royal Pass",
                     "w": 600, "h": 50, "font_size": 44, "font_weight": 700,
                     "textAlignHorizontal": "CENTER",
                     "element_class": "static"},
                    {"type": "TEXT", "name": "文本_倒计时",
                     "content": "23d 22h",
                     "w": 600, "h": 36, "font_size": 28,
                     "textAlignHorizontal": "CENTER",
                     "element_class": "dynamic"}
                ]
            },
            {
                "type": "FRAME", "name": "按钮_关闭",
                "w": 80, "h": 80,
                "layoutMode": "NONE",
                "children": [
                    {"type": "RECTANGLE", "name": "底板_按钮",
                     "x": 0, "y": 0, "w": 80, "h": 80, "corner_radius": 40,
                     "element_class": "static",
                     "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
                    {"type": "TEXT", "name": "文本_X",
                     "content": "X",
                     "x": 0, "y": 15, "w": 80, "h": 50,
                     "font_size": 44, "font_weight": 700,
                     "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
                     "element_class": "static",
                     "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}}
                ]
            }
        ]
    }


def make_主进度条():
    return {
        "type": "FRAME", "name": "组_主进度条",
        "x": 0, "y": 520, "w": 1080, "h": 130,
        "layoutMode": "HORIZONTAL",
        "primaryAxisSizingMode": "FIXED",
        "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "CENTER",
        "counterAxisAlignItems": "CENTER",
        "itemSpacing": 12,
        "paddingLeft": 30, "paddingRight": 30,
        "constraints": {"horizontal": "CENTER", "vertical": "TOP"},
        "children": [
            {"type": "RECTANGLE", "name": "图片_钥匙",
             "w": 100, "h": 100,
             "element_class": "static"},
            {
                "type": "FRAME", "name": "组_进度面板_主",
                "w": 380, "h": 80,
                "layoutMode": "NONE",
                "children": [
                    {
                        "type": "FRAME", "name": "组_进度_主",
                        "x": 0, "y": 0, "w": 380, "h": 80,
                        "layoutMode": "NONE",
                        "children": [
                            {"type": "RECTANGLE", "name": "底板_主",
                             "x": 0, "y": 0, "w": 380, "h": 80, "corner_radius": 40,
                             "element_class": "static",
                             "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
                            {"type": "RECTANGLE", "name": "进度条_主",
                             "x": 10, "y": 10, "w": 360, "h": 60, "corner_radius": 30,
                             "element_class": "dynamic",
                             "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}}
                        ]
                    },
                    {"type": "TEXT", "name": "文本_进度",
                     "content": "39/40",
                     "x": 0, "y": 20, "w": 380, "h": 40,
                     "font_size": 36, "font_weight": 700,
                     "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
                     "element_class": "dynamic",
                     "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}}
                ]
            },
            # 主进度条上的 组_节点 INSTANCE
            inst_节点("已完成", "21"),
            {
                "type": "FRAME", "name": "按钮_Activate",
                "w": 280, "h": 100,
                "layoutMode": "NONE",
                "children": [
                    {"type": "RECTANGLE", "name": "底板_按钮",
                     "x": 0, "y": 0, "w": 280, "h": 100, "corner_radius": 25,
                     "element_class": "static",
                     "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}},
                    {"type": "TEXT", "name": "文本_按钮",
                     "content": "Activate",
                     "x": 0, "y": 30, "w": 280, "h": 40,
                     "font_size": 36, "font_weight": 700,
                     "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER",
                     "element_class": "static",
                     "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}}
                ]
            }
        ]
    }


def make_列表滚动区():
    rows = [make_列表项(*r) for r in ROWS]
    return {
        "type": "FRAME", "name": "容器_列表滚动区",
        "x": 0, "y": 650, "w": 1080, "h": 1750,
        "layoutMode": "VERTICAL",
        "primaryAxisSizingMode": "FIXED",
        "counterAxisSizingMode": "FIXED",
        "clip_content": True,
        "overflow": "VERTICAL",
        "constraints": {"horizontal": "CENTER", "vertical": "SCALE"},
        "children": [
            {
                "type": "FRAME", "name": "组_滚动内容",
                "w": 1080,
                "layoutMode": "VERTICAL",
                "primaryAxisSizingMode": "AUTO",
                "counterAxisSizingMode": "FIXED",
                "layoutSizingHorizontal": "FIXED",
                "layoutSizingVertical": "HUG",
                "primaryAxisAlignItems": "MIN",
                "counterAxisAlignItems": "CENTER",
                "itemSpacing": 12,
                "children": rows
            }
        ]
    }


# === 装配 final_scene.json ===
final = {
    "screens": [
        {
            "name": "界面_RoyalPass",
            "type": "FRAME",
            "w": W_SCREEN, "h": H_SCREEN,
            "layers": [
                make_顶部装饰区(),
                make_顶部HUD(),
                make_主进度条(),
                make_列表滚动区(),
            ],
            "flow": []
        }
    ],
    "components": COMPONENTS
}

out = "/Users/red/Desktop/5.21工作流/4.22skill_v3_视觉缩窄即AL/runs/2026-05-21_RoyalPass列表行/final_scene.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)
print(f"final_scene.json written: {out}")
print(f"size: {sum(1 for _ in open(out))} lines")
print(f"components: {len(final['components'])}")
for c in final['components']:
    vn = [v['name'] for v in c['variants']]
    print(f"  - {c['name']} ({c['w']}×{c['h']}) variant_property={c['variant_property']} variants={vn}")
