"""S7 — 生成扁平 scene.json (Royal Pass 列表行 ccb)
按 SKILL.md 铁律 + S7a/S7e/S7c/S7d 执行.
"""
import json
from copy import deepcopy

# === 尺寸常量 (1080×2400) ===
W_SCREEN, H_SCREEN = 1080, 2400

# 列表项
W_ITEM, H_ITEM = 1080, 362

# 气泡 (左右共用 ccb)
W_BUBBLE, H_BUBBLE = 363, 205

# 中央节点 ccb
W_NODE, H_NODE = 110, 120

# 气泡内: 底板铺满
# 气泡内: 奖励物 居中靠上
W_REWARD_BOX, H_REWARD_BOX = 180, 140
X_REWARD_BOX = (W_BUBBLE - W_REWARD_BOX) // 2  # 居中
Y_REWARD_BOX = 25  # 偏上

# 气泡内: 角标在右下
W_BADGE, H_BADGE = 80, 80
X_BADGE = W_BUBBLE - W_BADGE - 10  # 右下, 10px 间距 (LEFT/TOP + 正坐标)
Y_BADGE = H_BUBBLE - H_BADGE - 10

# === 视觉差异微差常量 (07d #3 方法 C) ===
CR_BUBBLE_NORMAL = 100  # 底板气泡 常态 (胶囊形)
CR_BUBBLE_LOCKED = 101  # 底板气泡 待解锁
CR_NODE_DONE = 10  # 中央节点 底板 已完成
CR_NODE_UNDONE = 11  # 中央节点 底板 未完成


# === ccb 组件构造 ===

def make_组_底板气泡(variant: str):
    """底板气泡 2V: 常态 / 待解锁 — corner_radius 微差.
    单 RECT 抽 Component 必须包装 FRAME (07d #2 最小单元 FRAME 包装铁律).
    """
    cr = CR_BUBBLE_NORMAL if variant == "常态" else CR_BUBBLE_LOCKED
    return {
        "type": "FRAME", "name": "组_底板气泡",
        "x": 0, "y": 0, "w": W_BUBBLE, "h": H_BUBBLE,
        "layoutMode": "NONE",
        "children": [
            {
                "type": "RECTANGLE", "name": "底板_气泡",
                "x": 0, "y": 0, "w": W_BUBBLE, "h": H_BUBBLE,
                "corner_radius": cr
            }
        ]
    }


def make_组_奖励物(variant: str, num_text: str = ""):
    """奖励物 4V: 金/银/铜/道具 — 子节点 visible 切换 (方法 A, 07d #3).
    children 跨所有实例 name 100% 一致 (规则 11.5), visible 不同表达 4 Variant.
    道具 Variant 内部含 dynamic TEXT (异构, 07d #2.5).
    """
    is_gold = variant == "金宝箱"
    is_silver = variant == "银宝箱"
    is_copper = variant == "铜宝箱"
    is_item = variant == "道具"
    return {
        "type": "FRAME", "name": "组_奖励物",
        "x": X_REWARD_BOX, "y": Y_REWARD_BOX, "w": W_REWARD_BOX, "h": H_REWARD_BOX,
        "layoutMode": "NONE",
        "children": [
            {
                "type": "RECTANGLE", "name": "图片_奖励物_金",
                "x": 0, "y": 0, "w": W_REWARD_BOX, "h": H_REWARD_BOX,
                "visible": is_gold
            },
            {
                "type": "RECTANGLE", "name": "图片_奖励物_银",
                "x": 0, "y": 0, "w": W_REWARD_BOX, "h": H_REWARD_BOX,
                "visible": is_silver
            },
            {
                "type": "RECTANGLE", "name": "图片_奖励物_铜",
                "x": 0, "y": 0, "w": W_REWARD_BOX, "h": H_REWARD_BOX,
                "visible": is_copper
            },
            {
                "type": "RECTANGLE", "name": "图片_奖励物_道具",
                "x": 0, "y": 0, "w": W_REWARD_BOX, "h": H_REWARD_BOX,
                "visible": is_item
            },
            {
                "type": "TEXT", "name": "文本_数量",
                "content": num_text if is_item else "",
                "x": 0, "y": H_REWARD_BOX - 40, "h": 35,
                "font_size": 32, "font_weight": 700,
                "textAlignHorizontal": "CENTER", "textAlignVertical": "BOTTOM",
                "visible": is_item
            }
        ]
    }


def make_角标_状态(variant: str):
    """角标 4V: 锁/对勾/空/可领取.
    "空" = wrapper visible:false (方法 B). 内容 = 子节点 visible 切换 (方法 A).
    children 跨所有实例 name 100% 一致 (规则 11.5).
    constraints LEFT/TOP + 正坐标 (07e §1.3 角标硬夹断), 但这里在 NONE 父容器内 不需要 constraints
    (07e §1.2: 完整控件单元内部 layer 一律不写 constraints).
    """
    is_visible = variant != "空"
    is_lock = variant == "锁"
    is_check = variant == "对勾"
    is_claim = variant == "可领取"
    return {
        "type": "FRAME", "name": "角标_状态",
        "x": X_BADGE, "y": Y_BADGE, "w": W_BADGE, "h": H_BADGE,
        "layoutMode": "NONE",
        "visible": is_visible,
        "children": [
            {
                "type": "RECTANGLE", "name": "底板_圆角标",
                "x": 0, "y": 0, "w": W_BADGE, "h": H_BADGE,
                "corner_radius": 40
            },
            {
                "type": "RECTANGLE", "name": "图标_锁",
                "x": 15, "y": 15, "w": W_BADGE - 30, "h": H_BADGE - 30,
                "visible": is_lock
            },
            {
                "type": "RECTANGLE", "name": "图标_对勾",
                "x": 15, "y": 15, "w": W_BADGE - 30, "h": H_BADGE - 30,
                "visible": is_check
            },
            {
                "type": "RECTANGLE", "name": "图标_可领取",
                "x": 15, "y": 15, "w": W_BADGE - 30, "h": H_BADGE - 30,
                "visible": is_claim
            }
        ]
    }


def make_气泡(name: str, 底板_variant: str, 奖励物_variant: str, 奖励物_num: str, 角标_variant: str):
    """气泡 ccb (1V 单态): NONE 叠加 底板 + 奖励物 + 角标."""
    return {
        "type": "FRAME", "name": name,
        "w": W_BUBBLE, "h": H_BUBBLE,
        "layoutMode": "NONE",
        "children": [
            make_组_底板气泡(底板_variant),
            make_组_奖励物(奖励物_variant, 奖励物_num),
            make_角标_状态(角标_variant)
        ]
    }


def make_中央节点(节点_variant: str, 关卡号: str):
    """中央节点 ccb 2V: 已完成 / 未完成 — corner_radius 微差.
    内部: 组_底板菱形 (单 RECT 包装) + 文本_关卡号.
    """
    cr = CR_NODE_DONE if 节点_variant == "已完成" else CR_NODE_UNDONE
    return {
        "type": "FRAME", "name": "组_节点",
        "w": W_NODE, "h": H_NODE,
        "layoutMode": "NONE",
        "children": [
            {
                "type": "FRAME", "name": "组_底板菱形",
                "x": 0, "y": 0, "w": W_NODE, "h": H_NODE,
                "layoutMode": "NONE",
                "children": [
                    {
                        "type": "RECTANGLE", "name": "底板_菱形",
                        "x": 0, "y": 0, "w": W_NODE, "h": H_NODE,
                        "corner_radius": cr
                    }
                ]
            },
            {
                "type": "TEXT", "name": "文本_关卡号",
                "content": 关卡号,
                "x": 0, "y": (H_NODE - 50) // 2, "h": 50,
                "font_size": 44, "font_weight": 700,
                "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"
            }
        ]
    }


def make_列表项(行号: str, 左_底板, 左_奖励, 左_数量, 左_角标, 节点_state, 右_底板, 右_奖励, 右_数量, 右_角标):
    """列表项 (大ccb 1V): HORIZONTAL AL — 左气泡 / 中央节点 / 右气泡.
    paddings + SPACE_BETWEEN 自动分布 (1080 - 363 - 110 - 363 = 244, 分成 padding + 2 itemSpacing).
    """
    return {
        "type": "FRAME", "name": "列表项_关卡奖励",
        "w": W_ITEM, "h": H_ITEM,
        "layoutMode": "HORIZONTAL",
        "primaryAxisSizingMode": "FIXED",
        "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "SPACE_BETWEEN",
        "counterAxisAlignItems": "CENTER",
        "paddingLeft": 70,
        "paddingRight": 70,
        "paddingTop": 0,
        "paddingBottom": 0,
        "children": [
            make_气泡("气泡_左", 左_底板, 左_奖励, 左_数量, 左_角标),
            make_中央节点(节点_state, 行号),
            make_气泡("气泡_右", 右_底板, 右_奖励, 右_数量, 右_角标),
        ]
    }


# === 5 行样本 (覆盖所有 Variant 组合) ===
# 字段: (行号, 左_底板, 左_奖励, 左_数量, 左_角标, 节点_state, 右_底板, 右_奖励, 右_数量, 右_角标)
ROWS = [
    ("20", "常态", "道具", "x1",      "对勾",   "已完成", "常态",    "道具",    "x2", "锁"),
    ("21", "常态", "铜宝箱", "",      "对勾",   "已完成", "常态",    "道具",    "x1", "锁"),
    ("25", "常态", "道具", "x1",      "空",     "已完成", "常态",    "银宝箱",  "",   "锁"),
    ("23", "常态", "道具", "x1",      "空",     "已完成", "待解锁",  "道具",    "x1", "锁"),
    ("40", "常态", "铜宝箱", "",      "空",     "未完成", "常态",    "金宝箱",  "",   "可领取"),
]

# === 屏幕级 wrapper (顶部装饰/HUD/主进度条 简化) ===

def make_顶部装饰区():
    """顶部装饰图区 — 简化为占位 RECT (本次聚焦列表行 ccb)."""
    return {
        "type": "FRAME", "name": "组_顶部装饰",
        "x": 0, "y": 0, "w": 1080, "h": 410,
        "layoutMode": "NONE",
        "constraints": {"horizontal": "CENTER", "vertical": "TOP"},
        "children": [
            {
                "type": "RECTANGLE", "name": "背景_顶部装饰",
                "x": 0, "y": 0, "w": 1080, "h": 410
            },
            {
                "type": "RECTANGLE", "name": "图片_装饰_宝箱堆",
                "x": 0, "y": 30, "w": 1080, "h": 220
            },
            {
                "type": "RECTANGLE", "name": "图片_装饰_金宝箱中央",
                "x": 380, "y": 100, "w": 320, "h": 280
            }
        ]
    }


def make_顶部HUD():
    """顶部 HUD: Royal Pass 标题 + 倒计时. HORIZONTAL AL."""
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
                    {
                        "type": "RECTANGLE", "name": "底板_按钮",
                        "x": 0, "y": 0, "w": 80, "h": 80, "corner_radius": 40
                    },
                    {
                        "type": "TEXT", "name": "文本_i",
                        "content": "i",
                        "x": 0, "y": 15, "h": 50,
                        "font_size": 44, "font_weight": 700,
                        "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"
                    }
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
                    {
                        "type": "TEXT", "name": "文本_标题",
                        "content": "Royal Pass",
                        "h": 50, "font_size": 44, "font_weight": 700,
                        "textAlignHorizontal": "CENTER"
                    },
                    {
                        "type": "TEXT", "name": "文本_倒计时",
                        "content": "23d 22h",
                        "h": 36, "font_size": 28,
                        "textAlignHorizontal": "CENTER"
                    }
                ]
            },
            {
                "type": "FRAME", "name": "按钮_关闭",
                "w": 80, "h": 80,
                "layoutMode": "NONE",
                "children": [
                    {
                        "type": "RECTANGLE", "name": "底板_按钮",
                        "x": 0, "y": 0, "w": 80, "h": 80, "corner_radius": 40
                    },
                    {
                        "type": "TEXT", "name": "文本_X",
                        "content": "X",
                        "x": 0, "y": 15, "h": 50,
                        "font_size": 44, "font_weight": 700,
                        "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"
                    }
                ]
            }
        ]
    }


def make_主进度条():
    """主进度条: 钥匙 + 39/40 + 21 + Activate. 简化结构."""
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
            {
                "type": "RECTANGLE", "name": "图片_钥匙",
                "w": 100, "h": 100
            },
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
                            {
                                "type": "RECTANGLE", "name": "底板_主",
                                "x": 0, "y": 0, "w": 380, "h": 80, "corner_radius": 40
                            },
                            {
                                "type": "RECTANGLE", "name": "进度条_主",
                                "x": 10, "y": 10, "w": 360, "h": 60, "corner_radius": 30
                            }
                        ]
                    },
                    {
                        "type": "TEXT", "name": "文本_进度",
                        "content": "39/40",
                        "x": 0, "y": 20, "w": 380, "h": 40,
                        "font_size": 36, "font_weight": 700,
                        "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"
                    }
                ]
            },
            {
                "type": "FRAME", "name": "组_节点",
                "w": 110, "h": 120,
                "layoutMode": "NONE",
                "children": [
                    {
                        "type": "FRAME", "name": "组_底板菱形",
                        "x": 0, "y": 0, "w": 110, "h": 120,
                        "layoutMode": "NONE",
                        "children": [
                            {
                                "type": "RECTANGLE", "name": "底板_菱形",
                                "x": 0, "y": 0, "w": 110, "h": 120, "corner_radius": 10
                            }
                        ]
                    },
                    {
                        "type": "TEXT", "name": "文本_关卡号",
                        "content": "21",
                        "x": 0, "y": 35, "h": 50,
                        "font_size": 44, "font_weight": 700,
                        "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"
                    }
                ]
            },
            {
                "type": "FRAME", "name": "按钮_Activate",
                "w": 280, "h": 100,
                "layoutMode": "NONE",
                "children": [
                    {
                        "type": "RECTANGLE", "name": "底板_按钮",
                        "x": 0, "y": 0, "w": 280, "h": 100, "corner_radius": 25
                    },
                    {
                        "type": "TEXT", "name": "文本_按钮",
                        "content": "Activate",
                        "x": 0, "y": 30, "w": 280, "h": 40,
                        "font_size": 36, "font_weight": 700,
                        "textAlignHorizontal": "CENTER", "textAlignVertical": "CENTER"
                    }
                ]
            }
        ]
    }


def make_列表滚动区():
    """列表滚动区: VERTICAL AL + clip_content + overflow."""
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


# === 装配 scene ===
scene = {
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
    "components": []
}

# === 保存 ===
out = "/Users/red/Desktop/5.21工作流/4.22skill_v3_视觉缩窄即AL/runs/2026-05-21_RoyalPass列表行/scene.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(scene, f, ensure_ascii=False, indent=2)
print(f"scene.json written: {out}")
print(f"size: {sum(1 for _ in open(out))} lines")
