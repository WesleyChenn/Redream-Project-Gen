"""
S7 - Generate scene.json (flat, no INSTANCE, no components[])
Per skill v3 ultimate: child name 100% identical across instances, visible:false for hidden,
corner_radius micro-diff for variant signing, NONE outer + AL inner for ccb.
"""
import json
from pathlib import Path

OUT = Path("/Users/red/Desktop/5.21工作流/4.22skill_v3_终极版/runs/2026-05-25_video_091341/scene.json")

# ========= Collect category list (15 categories from frames 005/022/035) =========
# Each: (中文名, 底板色 group → corner_radius 微差区分 6 variant)
# color_cr: 绿=30, 橙=30.01, 红=30.02, 黄=30.03, 紫=30.04, 蓝=30.05
COLOR_CR = {"绿": 30.0, "橙": 30.01, "红": 30.02, "黄": 30.03, "紫": 30.04, "蓝": 30.05}

CATEGORIES = [
    # (中文名, 底板色, has NEW)
    ("運動裝備", "绿", False),
    ("飲品世界", "橙", True),
    ("速食狂歡", "红", False),
    ("玩具樂園", "黄", False),    # frame_005 second row "玩具卡车" - 名字 video 未读出, 占位
    ("水果天地", "紫", False),    # frame_005 second row "葡萄" - 名字 video 未读出, 占位
    ("甜點誘惑", "绿", True),     # frame_005 second row "甜甜圈" NEW
    ("戶外露營", "绿", False),
    ("辦公神器", "蓝", False),
    ("清潔用品", "紫", False),
    ("潮流服飾", "紫", False),
    ("數碼產品", "橙", False),
    ("家居好物", "绿", False),
    ("藝術品", "绿", False),
    ("旅行必備", "蓝", False),
    ("節日限定", "蓝", False),
]

# ========= Bottom tab 5 buttons (10 variants: 5 tab × 2 state) =========
# Video shows only "收藏" (#5) selected, others unselected.
# tab data: (label, icon_name placeholder, is_selected_in_video)
TABS = [
    ("購物", "购物袋", False),   # #1
    ("獎杯", "奖杯", False),     # #2
    ("家", "房子", False),        # #3
    ("花", "花朵", False),         # #4
    ("收藏", "花型选中", True),    # #5 selected in video
]

# ========= Reward panel 4 items (1 variant, icon dynamic placeholder) =========
REWARDS = [
    ("金币", "10000"),
    ("黄物", "10"),
    ("星星", "10"),
    ("红物", "10"),
]

# ========= Helper builders =========

def mk_rect(name, x, y, w, h, corner=None, extra=None):
    n = {"type": "RECTANGLE", "name": name, "x": x, "y": y, "w": w, "h": h}
    if corner is not None:
        n["corner_radius"] = corner
    if extra:
        n.update(extra)
    return n

def mk_frame(name, x, y, w, h, layout_mode="NONE", children=None, extra=None):
    n = {"type": "FRAME", "name": name, "x": x, "y": y, "w": w, "h": h,
         "layoutMode": layout_mode, "children": children or []}
    if extra:
        n.update(extra)
    return n

def mk_text(name, x, y, h, content, font_size=40, font_weight="Bold",
            align_h="CENTER", align_v="CENTER", w=None):
    n = {"type": "TEXT", "name": name, "x": x, "y": y, "h": h,
         "content": content, "font_size": font_size, "font_weight": font_weight,
         "textAlignHorizontal": align_h, "textAlignVertical": align_v}
    if w is not None:
        n["w"] = w
    return n

# ========= 列表项_收集类别 (大 ccb, 15 instances) =========
# Internal: NONE outer + 3 子 ccb wrappers (V AL between them via outer V AL on 列表项)
# But per 铁律 18, 底板 not in AL. 列表项 itself has 3 子 wrappers竖排 → 列表项外层用 VERTICAL AL,
# 3 wrapper 各自 NONE 内层. NEW 角标 ABSOLUTE 在 列表项 内 (但 列表项 内是 VERTICAL AL).
# Per 07e §1.3 角标在 AL 容器内必 layoutPositioning: ABSOLUTE.
# Solution: 列表项外层 NONE + 内容 wrapper (3 子 wrappers VERTICAL AL) + NEW 角标 children[-1] ABSOLUTE.
#
# Wait - that means children[0] is... there's no 底板 for 列表项 itself (用户清单 ③④⑤ inside, but 列表项 itself has no separate 底板). Looking at video again: 列表项 has no border/底板 of its own, just transparent wrapper containing 3 children. So 列表项 外层 = transparent wrapper.

LIST_ITEM_W = 310
LIST_ITEM_H = 460  # 圆按钮 310 + 文本卡 60 + 进度条 50 + spacing ~ 40

def build_list_item(idx, name_cn, color_key, has_new):
    """Build a single 列表项_收集类别 FRAME (扁平, completely independent children)."""
    cr_text_card = COLOR_CR[color_key]

    # 圆形按钮 wrapper (子 ccb 收集物) - NONE 内层
    circle = mk_frame("组_收集物", 0, 0, 310, 310, "NONE", children=[
        mk_rect("底板_圆形", 0, 0, 310, 310, corner=155),
        mk_rect("图标_收集物", 55, 55, 200, 200),  # 占位 - 程序换图
    ])

    # NEW 角标 (子 ccb 角标_New) - 在 列表项 内, 视觉溢出圆按钮右上
    # 即使 列表项 外层 NONE, 角标依然作为 列表项 children, visible 切换
    new_badge = mk_frame("角标_New", 220, 0, 110, 80, "NONE", children=[
        mk_rect("底板_丝带", 0, 0, 110, 80, corner=15),
        mk_text("文本_New", 0, 15, 50, "New", font_size=38, w=110),
    ], extra={"visible": has_new})

    # 文本卡 wrapper (子 ccb 文本卡_类别) - 底板颜色 variant 用 corner_radius 微差区分
    text_card = mk_frame("组_文本卡_类别", 0, 350, 310, 60, "NONE", children=[
        mk_rect("底板_文本卡", 0, 0, 310, 60, corner=cr_text_card),
        mk_text("文本_类别", 0, 5, 50, name_cn, font_size=38, w=310),
    ])

    # 进度条 wrapper (子 ccb 进度条_收集) - 100% 满模板, 引擎按 percentage 切
    progress = mk_frame("组_进度_收集", 0, 420, 310, 50, "NONE", children=[
        mk_rect("底板_收集", 0, 0, 310, 50, corner=25),
        mk_rect("进度条_收集", 10, 7, 290, 36, corner=18),
        mk_text("文本_收集_进度", 0, 5, 40, "0/9", font_size=32, w=310),
    ])

    # 列表项 外层 - NONE (因有 NEW 角标需要 ABSOLUTE 在 NONE 内自然定位)
    return mk_frame(f"列表项_收集类别", 0, 0, LIST_ITEM_W, LIST_ITEM_H + 30, "NONE", children=[
        circle,        # children[0]
        text_card,     # children[1]
        progress,      # children[2]
        new_badge,     # children[3] - 顶层 z, 视觉溢出圆按钮右上
    ])


# ========= tab_按钮 (大 ccb, 5 instances × 10 variants total) =========
# Each tab: [底板_tab, 凸出_选中(visible 切换), icon_tab, 文本_tab]
TAB_W = 195
TAB_H = 220

def build_tab_button(idx, label, icon_name, is_selected):
    """Build a single tab_按钮 FRAME."""
    # 底板_tab - 主体卡片 (常显, RECT 圆角矩形)
    bg = mk_rect("底板_tab", 0, 60, TAB_W, 160, corner=25)
    # 凸出_选中 - 装饰卡片 (visible 切换, 不用黄色 - 占位 RECT, 高保真时调色)
    # 凸出于 底板_tab 上方 (y=0~80 区域, visible:true 才显示)
    bump = mk_rect("凸出_选中", 10, 0, TAB_W - 20, 200, corner=30, extra={"visible": is_selected})
    # icon_tab - 占位 (每个 tab 不同 icon, 程序换图; 5 种 icon 名靠 wrapper_signature 区分)
    icon = mk_rect("图标_tab", 47, 75, 100, 100)
    # 文本_tab - dynamic 文本 (tab 名)
    text = mk_text("文本_tab", 0, 180, 40, label, font_size=30, w=TAB_W)

    # tab_按钮 - 是按钮 FRAME, 但点击不跨屏 (5.2 状态切换 Tab, 不写 flow)
    return mk_frame("按钮_tab", 0, 0, TAB_W, TAB_H, "NONE", children=[
        bg,    # children[0] - 底板
        bump,  # children[1] - 凸出装饰 (visible 切换)
        icon,  # children[2] - icon
        text,  # children[3] - 文本
    ])


# ========= 奖励物 (4 instances, 1 variant) =========
def build_reward_item(idx, label, count):
    return mk_frame("组_奖励物", 0, 0, 200, 200, "NONE", children=[
        mk_rect("底板_奖励物", 0, 0, 200, 200, corner=100),
        mk_rect("图标_奖励物", 30, 20, 140, 130),  # 占位
        mk_text("文本_奖励物_数量", 0, 155, 40, f"x{count}", font_size=34, w=200),
    ])


# ========= 礼物卡 (3 instances, 3 variants: 蓝/紫/浅) =========
GIFT_CARD_W = 290
GIFT_CARD_H = 320

def build_gift_card(idx, name_label, stars_count, color_key, has_plus2):
    # 底板色 corner_radius 微差: 蓝=20, 紫=20.01, 浅=20.02
    card_cr = {"蓝": 20.0, "紫": 20.01, "浅": 20.02}[color_key]

    # 顶部 3 颗黄星组 (HORIZONTAL AL, 但简化为 NONE 内绝对定位 — 都是装饰)
    stars = mk_frame("组_星组", 60, 10, 170, 50, "HORIZONTAL", children=[
        mk_rect("图标_星", 0, 0, 45, 45, corner=22),
        mk_rect("图标_星", 0, 0, 45, 45, corner=22),
        mk_rect("图标_星", 0, 0, 45, 45, corner=22),
    ], extra={
        "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "CENTER",
        "itemSpacing": 12,
    })
    # icon 物品 (占位)
    icon = mk_rect("图片_物品", 65, 65, 160, 160)
    # 丝带挂名称
    ribbon = mk_frame("组_丝带", 35, 230, 220, 70, "NONE", children=[
        mk_rect("底板_丝带", 0, 0, 220, 70, corner=10),
        mk_text("文本_物品名", 0, 12, 45, name_label, font_size=32, w=220),
    ])
    # +2 角标 (visible 切换, 仅 Handle 卡)
    plus_badge = mk_frame("角标_+2", 235, 5, 55, 55, "NONE", children=[
        mk_rect("底板_+2", 0, 0, 55, 55, corner=27),
        mk_text("文本_+2", 0, 5, 40, "+2", font_size=30, w=55),
    ], extra={"visible": has_plus2})

    return mk_frame("组_礼物卡", 0, 0, GIFT_CARD_W, GIFT_CARD_H, "NONE", children=[
        mk_rect("底板_卡", 0, 0, GIFT_CARD_W, GIFT_CARD_H, corner=card_cr),  # children[0]
        stars,        # children[1]
        icon,         # children[2]
        ribbon,       # children[3]
        plus_badge,   # children[4] - 顶层 z, visible 切换
    ])


# ========= 列表行_宝箱 (3 instances, 大 ccb 0 多态) + 子 ccb =========
# 宝箱: 3 variant 金/银/铜 (corner_radius 微差: 金=10, 银=10.01, 铜=10.02)
# 按钮_领取: 3 variant 已领取/未达成/达成可领取 (corner_radius: 40/40.01/40.02)
# 视频里 3 行全是 未达成 (variant 未达成)

# 但用户清单告知 variant 数量, 视频里只 1 态 — S7 仍按每实例完整 children 写, variant 体现在 corner_radius 微差
# 跨 3 个实例的"实际状态" 是: 宝箱=金/银/铜 (按视频次序 蓝→绿→紫, 视觉签名映射到金/银/铜); 按钮_领取=未达成/未达成/未达成 (视频全灰)
# 即 3 个列表行 各有一个 宝箱 INSTANCE (variant 金/银/铜) + 一个 按钮_领取 INSTANCE (variant 未达成)

CHEST_VARIANTS_CR = {"金": 10.0, "银": 10.01, "铜": 10.02}
CLAIM_BTN_VARIANTS_CR = {"已领取": 40.0, "未达成": 40.01, "达成可领取": 40.02}

def build_chest(variant_key):
    """子 ccb 宝箱, 3 variant 金/银/铜 - corner_radius 微差区分"""
    cr = CHEST_VARIANTS_CR[variant_key]
    return mk_frame("组_宝箱", 0, 0, 220, 220, "NONE", children=[
        mk_rect("底板_宝箱", 0, 0, 220, 220, corner=cr),
        mk_rect("图标_宝箱", 25, 30, 170, 160),  # 占位 - 程序换图 + variant 视觉差异
    ])

def build_claim_button(variant_key, number):
    """子 ccb 按钮_领取, 3 variant 已领取/未达成/达成可领取"""
    cr = CLAIM_BTN_VARIANTS_CR[variant_key]
    if variant_key == "已领取":
        # 对勾 icon, 无数字
        return mk_frame("按钮_领取", 0, 0, 460, 140, "NONE", children=[
            mk_rect("底板_领取", 0, 0, 460, 140, corner=cr),
            mk_rect("图标_勾", 180, 30, 100, 80),  # 对勾 icon
            mk_text("文本_领取", 0, 30, 80, "", font_size=42, w=460),  # 空 content
        ])
    elif variant_key == "未达成":
        # 灰胶囊 + ⭐ icon + 数字
        return mk_frame("按钮_领取", 0, 0, 460, 140, "NONE", children=[
            mk_rect("底板_领取", 0, 0, 460, 140, corner=cr),
            mk_rect("图标_勾", 50, 35, 70, 70),  # 实际是星 icon (但 children name 100% 一致, 这里复用 name)
            mk_text("文本_领取", 140, 30, 80, str(number), font_size=50, w=300, align_h="LEFT"),
        ])
    else:  # 达成可领取
        return mk_frame("按钮_领取", 0, 0, 460, 140, "NONE", children=[
            mk_rect("底板_领取", 0, 0, 460, 140, corner=cr),
            mk_rect("图标_勾", 50, 35, 70, 70),
            mk_text("文本_领取", 140, 30, 80, str(number), font_size=50, w=300, align_h="LEFT"),
        ])

def build_chest_row(idx, chest_variant, claim_variant, number):
    """大 ccb 列表行_宝箱 - NONE 外层 + 内容 wrapper H AL"""
    # 底板_行 (children[0], 米色)
    bg = mk_rect("底板_行", 0, 0, 960, 280, corner=30)
    # 内容 wrapper (HORIZONTAL AL)
    content = mk_frame("组_内容", 30, 30, 900, 220, "HORIZONTAL", children=[
        build_chest(chest_variant),
        mk_rect("图标_箭头", 0, 0, 80, 60),  # 箭头装饰
        build_claim_button(claim_variant, number),
    ], extra={
        "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "CENTER",
        "itemSpacing": 30,
    })
    return mk_frame("列表项_宝箱", 0, 0, 960, 280, "NONE", children=[
        bg,       # children[0]
        content,  # children[1]
    ])


# ============= MAIN ASSEMBLY =============

# ===== Screen A 界面_主屏 =====
main_layers = []

# 1. 顶部插画+标题区 (y=0, h=488, NONE)
top_section = mk_frame("组_顶部插画区", 0, 0, 1080, 488, "NONE", children=[
    mk_rect("图片_顶部插画", 0, 0, 1080, 488),  # 整块插画占位
    mk_frame("按钮_信息", 13, 16, 80, 80, "NONE", children=[
        mk_rect("底板_信息", 0, 0, 80, 80, corner=40),
        mk_text("文本_信息", 0, 15, 50, "!", font_size=44, w=80),
    ]),
    mk_frame("按钮_宝箱", 870, 30, 130, 145, "NONE", children=[
        mk_rect("底板_宝箱_入口", 0, 0, 130, 130, corner=65),
        mk_rect("图标_宝箱_入口", 20, 15, 90, 100),  # 占位
    ]),
    # 收藏 banner (粉红椭圆)
    mk_frame("组_收藏banner", 248, 380, 540, 108, "NONE", children=[
        mk_rect("底板_收藏banner", 0, 0, 540, 108, corner=54),
        mk_text("文本_收藏标题", 0, 25, 65, "收藏!", font_size=64, w=540),
    ]),
], extra={"constraints": {"horizontal": "CENTER", "vertical": "TOP"}})
main_layers.append(top_section)

# 2. 奖励+进度面板 (y=488, h=622, NONE outer)
award_panel = mk_frame("组_奖励进度面板", 30, 488, 1020, 622, "NONE", children=[
    # 橙色奖励物板 (NONE 外层 + 4 奖励物 HORIZONTAL AL 内层)
    mk_rect("底板_奖励物板", 0, 0, 1020, 360, corner=40),
    # 奖励 chip (顶部溢出)
    mk_frame("组_奖励chip", 380, -30, 260, 80, "NONE", children=[
        mk_rect("底板_奖励chip", 0, 0, 260, 80, corner=40),
        mk_text("文本_奖励chip", 0, 12, 50, "奖励", font_size=44, w=260),
    ]),
    # 4 奖励物横排 (HORIZONTAL AL)
    mk_frame("组_奖励物横排", 30, 60, 960, 280, "HORIZONTAL", children=[
        build_reward_item(0, *REWARDS[0]),
        build_reward_item(1, *REWARDS[1]),
        build_reward_item(2, *REWARDS[2]),
        build_reward_item(3, *REWARDS[3]),
    ], extra={
        "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "CENTER",
        "itemSpacing": 30, "paddingLeft": 30, "paddingRight": 30,
    }),
    # 进度条 + 32d14h (NONE 内底)
    mk_frame("组_进度_星卡", 50, 400, 920, 90, "NONE", children=[
        mk_rect("底板_星卡", 0, 0, 920, 90, corner=45),
        mk_rect("进度条_星卡", 10, 10, 900, 70, corner=35),
        # 星卡装饰 chip (左端溢出)
        mk_frame("组_星卡chip", -20, -10, 110, 110, "NONE", children=[
            mk_rect("底板_星卡chip", 0, 0, 110, 110, corner=20),
            mk_rect("图标_星", 25, 25, 60, 60),
        ]),
        mk_text("文本_星卡_进度", 0, 15, 50, "2/135", font_size=42, w=920),
    ]),
    # 32d14h 倒计时 (NONE 外层 + AL 内层 — 铁律 18, 底板永不进 AL)
    mk_frame("组_倒计时", 385, 520, 250, 80, "NONE", children=[
        mk_rect("底板_倒计时", 0, 0, 250, 80, corner=40),
        mk_frame("内容区_倒计时", 0, 0, 250, 80, "HORIZONTAL", children=[
            mk_rect("图标_倒计时", 0, 0, 50, 50),
            mk_text("文本_倒计时", 0, 0, 50, "32d14h", font_size=38, w=180, align_h="LEFT"),
        ], extra={
            "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
            "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "CENTER",
            "itemSpacing": 10, "paddingLeft": 20, "paddingRight": 20,
        }),
    ]),
], extra={"constraints": {"horizontal": "CENTER", "vertical": "TOP"}})
main_layers.append(award_panel)

# 3. 滚动收集列表区 (y=1110, h=1046, VERTICAL AL + clip_content)
# Inside: 5 行 (HORIZONTAL AL each, 3 列)
rows = []
for row_i in range(5):
    items = []
    for col_i in range(3):
        cat_idx = row_i * 3 + col_i
        name_cn, color, has_new = CATEGORIES[cat_idx]
        items.append(build_list_item(cat_idx, name_cn, color, has_new))
    row = mk_frame(f"组_行", 0, 0, 1020, LIST_ITEM_H + 30, "HORIZONTAL", children=items,
                   extra={
                       "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
                       "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "CENTER",
                       "itemSpacing": 30,
                   })
    rows.append(row)

scroll_content = mk_frame("组_滚动内容", 0, 0, 1020, 0, "VERTICAL", children=rows, extra={
    "primaryAxisSizingMode": "AUTO", "counterAxisSizingMode": "FIXED",
    "layoutSizingHorizontal": "FIXED", "layoutSizingVertical": "HUG",
    "primaryAxisAlignItems": "MIN", "counterAxisAlignItems": "CENTER",
    "itemSpacing": 40, "paddingTop": 20, "paddingBottom": 20,
})

scroll_section = mk_frame("容器_收集列表滚动区", 30, 1110, 1020, 1046, "VERTICAL", children=[
    scroll_content,
], extra={
    "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
    "primaryAxisAlignItems": "MIN", "counterAxisAlignItems": "CENTER",
    "clip_content": True, "overflow": "VERTICAL",
    "constraints": {"horizontal": "CENTER", "vertical": "TOP"},
})
main_layers.append(scroll_section)

# 4. 底部 tab 区 (y=2156, h=244, HORIZONTAL AL)
tabs = []
for i, (label, icon, sel) in enumerate(TABS):
    tabs.append(build_tab_button(i, label, icon, sel))

tab_section = mk_frame("组_底部tab", 0, 2156, 1080, 244, "HORIZONTAL", children=tabs, extra={
    "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
    "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "MAX",
    "itemSpacing": 0, "paddingTop": 24,
    "constraints": {"horizontal": "CENTER", "vertical": "BOTTOM"},
})
main_layers.append(tab_section)

screen_a = {
    "name": "界面_主屏",
    "type": "FRAME",
    "w": 1080, "h": 2400,
    "layers": main_layers,
    "flow": []  # S9 fills
}

# ===== Screen B 浮层_卡片星星 =====
popup_layers = []

# 0. 遮罩 (constraints SCALE/SCALE)
popup_layers.append(mk_rect("遮罩_浮层背景", 0, 0, 1080, 2400, extra={
    "constraints": {"horizontal": "SCALE", "vertical": "SCALE"}
}))

# 1. 弹窗主体 (CENTER/CENTER)
popup_body = mk_frame("弹窗_卡片星星", 40, 98, 999, 2080, "NONE", children=[
    # 弹窗底板 (children[0])
    mk_rect("底板_弹窗", 0, 0, 999, 2080, corner=50),
    # X 关闭按钮 (children[-2], 视觉溢出右上)
    mk_frame("按钮_关闭", 815, 30, 100, 100, "NONE", children=[
        mk_rect("底板_关闭", 0, 0, 100, 100, corner=50),
        mk_text("文本_关闭", 0, 15, 70, "×", font_size=60, w=100),
    ]),
    # banner_卡片星星 (chip 凸出顶部)
    mk_frame("组_banner_卡片星星", 180, -8, 645, 145, "NONE", children=[
        mk_rect("底板_banner", 0, 0, 645, 145, corner=72),
        mk_text("文本_banner_标题", 0, 35, 70, "卡片星星", font_size=64, w=645),
    ]),
    # 弹窗内容容器 (VERTICAL AL, 居中)
    mk_frame("组_弹窗内容", 30, 200, 939, 1850, "VERTICAL", children=[
        # 3 礼物卡 (HORIZONTAL AL)
        mk_frame("组_3礼物卡横排", 0, 0, 939, 320, "HORIZONTAL", children=[
            build_gift_card(0, "Ikebana", 3, "蓝", False),
            build_gift_card(1, "Handle", 2, "紫", True),
            build_gift_card(2, "Ice cream", 3, "浅", False),
        ], extra={
            "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
            "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "CENTER",
            "itemSpacing": 25,
        }),
        # 提示文字
        mk_text("文本_提示", 30, 0, 100, "使用你的重複的卡片星星打開箱子!", font_size=36, w=879),
        # 你有 状态
        mk_frame("组_你有状态", 0, 0, 939, 80, "HORIZONTAL", children=[
            mk_text("文本_你有_label", 0, 0, 60, "你有:", font_size=40, w=160),
            mk_rect("图标_星", 0, 0, 60, 60, corner=30),
            mk_text("文本_你有_数量", 0, 0, 60, "0", font_size=44, w=120, align_h="LEFT"),
        ], extra={
            "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
            "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "CENTER",
            "itemSpacing": 15,
        }),
        # 3 行宝箱列表 (VERTICAL AL)
        mk_frame("组_3行宝箱列表", 0, 0, 939, 920, "VERTICAL", children=[
            build_chest_row(0, "金", "未达成", 100),
            build_chest_row(1, "银", "未达成", 200),
            build_chest_row(2, "铜", "未达成", 400),
        ], extra={
            "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
            "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "CENTER",
            "itemSpacing": 30,
        }),
    ], extra={
        "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "MIN", "counterAxisAlignItems": "CENTER",
        "itemSpacing": 50,
    }),
], extra={"constraints": {"horizontal": "CENTER", "vertical": "CENTER"}})
popup_layers.append(popup_body)

screen_b = {
    "name": "浮层_卡片星星",
    "type": "FRAME",
    "w": 1080, "h": 2400,
    "layers": popup_layers,
    "flow": []
}

# ===== Final scene =====
scene = {
    "screens": [screen_a, screen_b],
    "components": []  # S11 will fill
}

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(scene, f, ensure_ascii=False, indent=2)
print(f"Wrote {OUT}")
print(f"Screen A layers: {len(main_layers)}")
print(f"Screen B layers: {len(popup_layers)}")
print(f"List items: {sum(len(r['children']) for r in rows)}")
print(f"Tab buttons: {len(tabs)}")
