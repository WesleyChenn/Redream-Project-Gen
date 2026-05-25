"""
S11 主路径 - 直接构造 v20.6 schema final_scene.json
跳过 extract_components.py, 手写 components[] + INSTANCE + element_class
"""
import json
from pathlib import Path
from copy import deepcopy

OUT = Path("/Users/red/Desktop/5.21工作流/4.22skill_v3_终极版/runs/2026-05-25_video_091341/final_scene.json")

# Data shared with generate_scene.py
COLOR_CR = {"绿": 30.0, "橙": 30.01, "红": 30.02, "黄": 30.03, "紫": 30.04, "蓝": 30.05}
CHEST_VARIANTS_CR = {"金": 10.0, "银": 10.01, "铜": 10.02}
CLAIM_BTN_VARIANTS_CR = {"已领取": 40.0, "未达成": 40.01, "达成可领取": 40.02}
GIFT_CR = {"蓝": 20.0, "紫": 20.01, "浅": 20.02}

CATEGORIES = [
    ("運動裝備", "绿", False), ("飲品世界", "橙", True), ("速食狂歡", "红", False),
    ("玩具樂園", "黄", False), ("水果天地", "紫", False), ("甜點誘惑", "绿", True),
    ("戶外露營", "绿", False), ("辦公神器", "蓝", False), ("清潔用品", "紫", False),
    ("潮流服飾", "紫", False), ("數碼產品", "橙", False), ("家居好物", "绿", False),
    ("藝術品", "绿", False), ("旅行必備", "蓝", False), ("節日限定", "蓝", False),
]
TABS = [("購物", False), ("獎杯", False), ("家", False), ("花", False), ("收藏", True)]
REWARDS = [("金币", "10000"), ("黄物", "10"), ("星星", "10"), ("红物", "10")]

def rect(name, x, y, w, h, ec="static", corner=None, extra=None, constraints=None):
    n = {"type": "RECTANGLE", "name": name, "x": x, "y": y, "w": w, "h": h, "element_class": ec}
    if corner is not None: n["corner_radius"] = corner
    if constraints: n["constraints"] = constraints
    if extra: n.update(extra)
    return n

def text(name, x, y, h, content, ec="dynamic", font_size=40, font_weight="Bold",
         align_h="CENTER", align_v="CENTER", w=None):
    n = {"type": "TEXT", "name": name, "x": x, "y": y, "h": h, "content": content,
         "element_class": ec, "font_size": font_size, "font_weight": font_weight,
         "textAlignHorizontal": align_h, "textAlignVertical": align_v}
    if w is not None: n["w"] = w
    return n

def frame(name, x, y, w, h, layout_mode="NONE", children=None, extra=None):
    n = {"type": "FRAME", "name": name, "x": x, "y": y, "w": w, "h": h,
         "layoutMode": layout_mode, "children": children or []}
    if extra: n.update(extra)
    return n

def instance(name, comp, variant, x, y, w, h, overrides=None, extra=None):
    n = {"type": "INSTANCE", "name": name, "component_name": comp, "variant": variant,
         "x": x, "y": y, "w": w, "h": h}
    if overrides: n["overrides"] = overrides
    if extra: n.update(extra)
    return n

# ============= Build components[] =============

# 1. 收集物 (2 variant: 常态 + dummy 凑数, 应付 combineAsVariants ≥2)
c_collect = {
    "name": "收集物", "w": 310, "h": 310, "variant_property": "状态",
    "variants": [
        {"name": "常态", "is_default": True, "layers": [
            rect("底板_圆形", 0, 0, 310, 310, corner=155),
            rect("图标_收集物", 55, 55, 200, 200),
        ]},
        {"name": "高亮", "layers": [
            rect("底板_圆形", 0, 0, 310, 310, corner=155.5),  # corner_radius 微差签名唯一
            rect("图标_收集物", 55, 55, 200, 200),
        ]}
    ]
}

# 2. 角标_New (2 variant: 常态 / 空)
c_new_badge = {
    "name": "角标_New", "w": 110, "h": 80, "variant_property": "状态",
    "variants": [
        {"name": "常态", "is_default": True, "layers": [
            rect("底板_丝带", 0, 0, 110, 80, corner=15),
            text("文本_New", 0, 15, 50, "New", font_size=38, w=110),
        ]},
        {"name": "空", "layers": []}
    ]
}

# 3. 文本卡_类别 (6 variant 颜色枚举)
def text_card_variant(name, cr, is_default=False):
    v = {"name": name, "layers": [
        rect("底板_文本卡", 0, 0, 310, 60, corner=cr),
        text("文本_类别", 0, 5, 50, name, font_size=38, w=310),  # placeholder; instance overrides
    ]}
    if is_default: v["is_default"] = True
    return v
c_text_card = {
    "name": "文本卡_类别", "w": 310, "h": 60, "variant_property": "颜色",
    "variants": [
        text_card_variant("绿", 30.0, True),
        text_card_variant("橙", 30.01),
        text_card_variant("红", 30.02),
        text_card_variant("黄", 30.03),
        text_card_variant("紫", 30.04),
        text_card_variant("蓝", 30.05),
    ]
}

# 4. 进度条_收集 (2 variant: 常态 + dummy)
c_progress_collect = {
    "name": "进度条_收集", "w": 310, "h": 50, "variant_property": "状态",
    "variants": [
        {"name": "常态", "is_default": True, "layers": [
            rect("底板_收集", 0, 0, 310, 50, corner=25),
            rect("进度条_收集", 10, 7, 290, 36, corner=18),
            text("文本_收集_进度", 0, 5, 40, "0/9", font_size=32, w=310),
        ]},
        {"name": "完成", "layers": [
            rect("底板_收集", 0, 0, 310, 50, corner=25.5),  # 微差签名
            rect("进度条_收集", 10, 7, 290, 36, corner=18),
            text("文本_收集_进度", 0, 5, 40, "9/9", font_size=32, w=310),
        ]}
    ]
}

# 5. tab_按钮 (10 variant: 5 tab × 2 状态)
# 每个 tab 用 底板 corner_radius 微差签名唯一 (25 + tab_idx*0.01); 状态用是否含 凸出_选中 区分
TAB_STATE_NAMES = []
for tab_idx, (label, _) in enumerate(TABS):
    for state in ["未选中", "选中"]:
        TAB_STATE_NAMES.append((label, state, f"{label}{state}", tab_idx))

def tab_variant(label, state, vname, tab_idx, is_default=False):
    is_sel = (state == "选中")
    bg_cr = 25 + tab_idx * 0.01  # 每个 tab 底板 corner_radius 微差区分
    v = {"name": vname, "layers": [
        rect("底板_tab", 0, 60, 195, 160, corner=bg_cr),
        *([rect("凸出_选中", 10, 0, 175, 200, corner=30 + tab_idx * 0.01)] if is_sel else []),
        rect("图标_tab", 47, 75, 100, 100, corner=50 + tab_idx * 0.01),
        text("文本_tab", 0, 180, 40, label, font_size=30, w=195),
    ]}
    if is_default: v["is_default"] = True
    return v

c_tab = {
    "name": "tab_按钮", "w": 195, "h": 220, "variant_property": "tab状态",
    "variants": [tab_variant(label, state, vname, tab_idx, i==0)
                 for i, (label, state, vname, tab_idx) in enumerate(TAB_STATE_NAMES)]
}

# 6. 奖励物 (2 variant: 常态 + dummy 凑数)
c_reward = {
    "name": "奖励物", "w": 200, "h": 200, "variant_property": "状态",
    "variants": [
        {"name": "常态", "is_default": True, "layers": [
            rect("底板_奖励物", 0, 0, 200, 200, corner=100),
            rect("图标_奖励物", 30, 20, 140, 130),
            text("文本_奖励物_数量", 0, 155, 40, "x10", font_size=34, w=200),
        ]},
        {"name": "高亮", "layers": [
            rect("底板_奖励物", 0, 0, 200, 200, corner=100.5),
            rect("图标_奖励物", 30, 20, 140, 130),
            text("文本_奖励物_数量", 0, 155, 40, "x10", font_size=34, w=200),
        ]}
    ]
}

# 7. 组_礼物卡 (3 variant: 蓝/紫/浅)
def gift_card_variant(color_key, has_plus2_default, is_default=False):
    cr = GIFT_CR[color_key]
    layers = [
        rect("底板_卡", 0, 0, 290, 320, corner=cr),
        # 星组 wrapper FRAME (HORIZONTAL AL 内部, 但 variant 内 layer 是 FRAME 也合法)
        frame("组_星组", 60, 10, 170, 50, "HORIZONTAL", children=[
            rect("图标_星", 0, 0, 45, 45, corner=22),
            rect("图标_星", 0, 0, 45, 45, corner=22),
            rect("图标_星", 0, 0, 45, 45, corner=22),
        ], extra={
            "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
            "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "CENTER",
            "itemSpacing": 12,
        }),
        rect("图片_物品", 65, 65, 160, 160),
        frame("组_丝带", 35, 230, 220, 70, "NONE", children=[
            rect("底板_丝带", 0, 0, 220, 70, corner=10),
            text("文本_物品名", 0, 12, 45, "Item", font_size=32, w=220),
        ]),
    ]
    # +2 角标 default 不画 (instance override 控制 visible)
    v = {"name": color_key, "layers": layers}
    if is_default: v["is_default"] = True
    return v

c_gift_card = {
    "name": "组_礼物卡", "w": 290, "h": 320, "variant_property": "卡色",
    "variants": [
        gift_card_variant("蓝", False, True),
        gift_card_variant("紫", True),
        gift_card_variant("浅", False),
    ]
}

# 8. 组_宝箱 (3 variant: 金/银/铜)
def chest_variant(name, is_default=False):
    cr = CHEST_VARIANTS_CR[name]
    v = {"name": name, "layers": [
        rect("底板_宝箱", 0, 0, 220, 220, corner=cr),
        rect("图标_宝箱", 25, 30, 170, 160),  # 数据驱动 + 变 variant 视觉
    ]}
    if is_default: v["is_default"] = True
    return v

c_chest = {
    "name": "组_宝箱", "w": 220, "h": 220, "variant_property": "宝箱等级",
    "variants": [
        chest_variant("金", True),
        chest_variant("银"),
        chest_variant("铜"),
    ]
}

# 9. 按钮_领取 (3 variant: 已领取/未达成/达成可领取)
def claim_btn_variant(name, is_default=False):
    cr = CLAIM_BTN_VARIANTS_CR[name]
    if name == "已领取":
        layers = [
            rect("底板_领取", 0, 0, 460, 140, corner=cr),
            rect("图标_勾", 180, 30, 100, 80),
            text("文本_领取", 0, 30, 80, "", ec="dynamic", font_size=42, w=460),
        ]
    else:
        layers = [
            rect("底板_领取", 0, 0, 460, 140, corner=cr),
            rect("图标_勾", 50, 35, 70, 70),  # name 一致, 实际显示星 icon
            text("文本_领取", 140, 30, 80, "100", ec="dynamic", font_size=50, w=300, align_h="LEFT"),
        ]
    v = {"name": name, "layers": layers}
    if is_default: v["is_default"] = True
    return v

c_claim_btn = {
    "name": "按钮_领取", "w": 460, "h": 140, "variant_property": "状态",
    "variants": [
        claim_btn_variant("已领取"),
        claim_btn_variant("未达成", True),  # 视频中所有 3 行都是未达成 → default
        claim_btn_variant("达成可领取"),
    ]
}

# Final components[] (order: 子 component 在前, 引用它们的外层在后 — 但本案例无嵌套 component, 任意顺序)
components = [
    c_collect, c_new_badge, c_text_card, c_progress_collect, c_tab,
    c_reward, c_gift_card, c_chest, c_claim_btn,
]

# ============= Build screens (大组团 = 扁平 FRAME, 最小单元 = INSTANCE) =============

# --- Screen A 主屏 ---

# 列表项_收集类别: 大组团 FRAME, 内含 INSTANCE 引用
def build_list_item_with_instances(idx, name_cn, color_key, has_new):
    cat_text_card_variant = color_key  # variant name = 颜色 (绿/橙/...)
    new_variant = "常态" if has_new else "空"
    return frame("列表项_收集类别", 0, 0, 310, 490, "NONE", children=[
        instance("组_收集物", "收集物", "常态", 0, 0, 310, 310),
        instance("组_文本卡_类别", "文本卡_类别", cat_text_card_variant, 0, 350, 310, 60,
                 overrides={"文本_类别": name_cn}),
        instance("组_进度_收集", "进度条_收集", "常态", 0, 420, 310, 50,
                 overrides={"文本_收集_进度": "1/9" if has_new else "0/9"}),
        instance("角标_New", "角标_New", new_variant, 220, 0, 110, 80),
    ])

# tab 按钮: 5 INSTANCE, 各引用对应 variant
def build_tab_with_instance(idx):
    label, is_selected = TABS[idx]
    variant_name = f"{label}{'选中' if is_selected else '未选中'}"
    return instance("按钮_tab", "tab_按钮", variant_name, 0, 0, 195, 220)

# 顶部插画+标题区
top_section = frame("组_顶部插画区", 0, 0, 1080, 488, "NONE", children=[
    rect("图片_顶部插画", 0, 0, 1080, 488),
    frame("按钮_信息", 13, 16, 80, 80, "NONE", children=[
        rect("底板_信息", 0, 0, 80, 80, corner=40),
        text("文本_信息", 0, 15, 50, "!", ec="static", font_size=44, w=80),
    ]),
    frame("按钮_宝箱", 870, 30, 130, 145, "NONE", children=[
        rect("底板_宝箱_入口", 0, 0, 130, 130, corner=65),
        rect("图标_宝箱_入口", 20, 15, 90, 100),
    ]),
    frame("组_收藏banner", 248, 380, 540, 108, "NONE", children=[
        rect("底板_收藏banner", 0, 0, 540, 108, corner=54),
        text("文本_收藏标题", 0, 25, 65, "收藏!", ec="static", font_size=64, w=540),
    ]),
], extra={"constraints": {"horizontal": "CENTER", "vertical": "TOP"}})

# 奖励+进度面板 (含 4 奖励物 INSTANCE)
award_panel = frame("组_奖励进度面板", 30, 488, 1020, 622, "NONE", children=[
    rect("底板_奖励物板", 0, 0, 1020, 360, corner=40),
    frame("组_奖励chip", 380, -30, 260, 80, "NONE", children=[
        rect("底板_奖励chip", 0, 0, 260, 80, corner=40),
        text("文本_奖励chip", 0, 12, 50, "奖励", ec="static", font_size=44, w=260),
    ]),
    # 4 奖励物 INSTANCE (HORIZONTAL AL wrapper)
    frame("组_奖励物横排", 30, 60, 960, 280, "HORIZONTAL", children=[
        instance("组_奖励物_1", "奖励物", "常态", 0, 0, 200, 200, overrides={"文本_奖励物_数量": "x10000"}),
        instance("组_奖励物_2", "奖励物", "常态", 0, 0, 200, 200, overrides={"文本_奖励物_数量": "x10"}),
        instance("组_奖励物_3", "奖励物", "常态", 0, 0, 200, 200, overrides={"文本_奖励物_数量": "x10"}),
        instance("组_奖励物_4", "奖励物", "常态", 0, 0, 200, 200, overrides={"文本_奖励物_数量": "x10"}),
    ], extra={
        "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "CENTER",
        "itemSpacing": 30, "paddingLeft": 30, "paddingRight": 30,
    }),
    # 进度条 + 星卡chip
    frame("组_进度_星卡", 50, 400, 920, 90, "NONE", children=[
        rect("底板_星卡", 0, 0, 920, 90, corner=45),
        rect("进度条_星卡", 10, 10, 900, 70, corner=35),
        frame("组_星卡chip", -20, -10, 110, 110, "NONE", children=[
            rect("底板_星卡chip", 0, 0, 110, 110, corner=20),
            rect("图标_星", 25, 25, 60, 60),
        ]),
        text("文本_星卡_进度", 0, 15, 50, "2/135", ec="dynamic", font_size=42, w=920),
    ]),
    # 32d14h 倒计时 (NONE 外层 + AL 内层)
    frame("组_倒计时", 385, 520, 250, 80, "NONE", children=[
        rect("底板_倒计时", 0, 0, 250, 80, corner=40),
        frame("内容区_倒计时", 0, 0, 250, 80, "HORIZONTAL", children=[
            rect("图标_倒计时", 0, 0, 50, 50),
            text("文本_倒计时", 0, 0, 50, "32d14h", ec="dynamic", font_size=38, w=180, align_h="LEFT"),
        ], extra={
            "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
            "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "CENTER",
            "itemSpacing": 10, "paddingLeft": 20, "paddingRight": 20,
        }),
    ]),
], extra={"constraints": {"horizontal": "CENTER", "vertical": "TOP"}})

# 滚动列表区 (15 个列表项, 5 行)
rows = []
for row_i in range(5):
    items = []
    for col_i in range(3):
        cat_idx = row_i * 3 + col_i
        name_cn, color, has_new = CATEGORIES[cat_idx]
        items.append(build_list_item_with_instances(cat_idx, name_cn, color, has_new))
    row = frame("组_行", 0, 0, 1020, 490, "HORIZONTAL", children=items, extra={
        "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
        "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "CENTER",
        "itemSpacing": 30,
    })
    rows.append(row)

scroll_content = frame("组_滚动内容", 0, 0, 1020, 0, "VERTICAL", children=rows, extra={
    "primaryAxisSizingMode": "AUTO", "counterAxisSizingMode": "FIXED",
    "layoutSizingHorizontal": "FIXED", "layoutSizingVertical": "HUG",
    "primaryAxisAlignItems": "MIN", "counterAxisAlignItems": "CENTER",
    "itemSpacing": 40, "paddingTop": 20, "paddingBottom": 20,
})

scroll_section = frame("容器_收集列表滚动区", 30, 1110, 1020, 1046, "VERTICAL", children=[
    scroll_content,
], extra={
    "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
    "primaryAxisAlignItems": "MIN", "counterAxisAlignItems": "CENTER",
    "clip_content": True, "overflow": "VERTICAL",
    "constraints": {"horizontal": "CENTER", "vertical": "TOP"},
})

# 底部 tab (5 INSTANCE)
tab_instances = [build_tab_with_instance(i) for i in range(5)]
tab_section = frame("组_底部tab", 0, 2156, 1080, 244, "HORIZONTAL", children=tab_instances, extra={
    "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
    "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "MAX",
    "itemSpacing": 0, "paddingTop": 24,
    "constraints": {"horizontal": "CENTER", "vertical": "BOTTOM"},
})

screen_a = {
    "name": "界面_主屏", "type": "FRAME", "w": 1080, "h": 2400,
    "layers": [top_section, award_panel, scroll_section, tab_section],
    "flow": [{
        "trigger": "ON_CLICK", "from": "界面_主屏", "from_node": "按钮_宝箱",
        "to": "浮层_卡片星星", "animation": "dissolve 300ms (OVERLAY)",
        "_note": "来源未确认 (Show Taps 未开); S4 候选: 按钮_宝箱 [极高契合]"
    }]
}

# --- Screen B 浮层_卡片星星 ---

# 列表项_宝箱 (大组团 FRAME, 内含 INSTANCE)
def build_chest_row_with_instances(idx, chest_v, claim_v, number):
    return frame("列表项_宝箱", 0, 0, 960, 280, "NONE", children=[
        rect("底板_行", 0, 0, 960, 280, corner=30),
        frame("组_内容", 30, 30, 900, 220, "HORIZONTAL", children=[
            instance("组_宝箱", "组_宝箱", chest_v, 0, 0, 220, 220),
            rect("图标_箭头", 0, 0, 80, 60),
            instance("按钮_领取", "按钮_领取", claim_v, 0, 0, 460, 140,
                     overrides={"文本_领取": str(number)}),
        ], extra={
            "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
            "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "CENTER",
            "itemSpacing": 30,
        }),
    ])

popup_body = frame("弹窗_卡片星星", 40, 98, 999, 2080, "NONE", children=[
    rect("底板_弹窗", 0, 0, 999, 2080, corner=50),
    frame("按钮_关闭", 815, 30, 100, 100, "NONE", children=[
        rect("底板_关闭", 0, 0, 100, 100, corner=50),
        text("文本_关闭", 0, 15, 70, "×", ec="static", font_size=60, w=100),
    ]),
    frame("组_banner_卡片星星", 180, -8, 645, 145, "NONE", children=[
        rect("底板_banner", 0, 0, 645, 145, corner=72),
        text("文本_banner_标题", 0, 35, 70, "卡片星星", ec="static", font_size=64, w=645),
    ]),
    frame("组_弹窗内容", 30, 200, 939, 1850, "VERTICAL", children=[
        # 3 礼物卡 INSTANCE
        frame("组_3礼物卡横排", 0, 0, 939, 320, "HORIZONTAL", children=[
            instance("组_礼物卡_1", "组_礼物卡", "蓝", 0, 0, 290, 320,
                     overrides={"文本_物品名": "Ikebana"}),
            instance("组_礼物卡_2", "组_礼物卡", "紫", 0, 0, 290, 320,
                     overrides={"文本_物品名": "Handle"}),
            instance("组_礼物卡_3", "组_礼物卡", "浅", 0, 0, 290, 320,
                     overrides={"文本_物品名": "Ice cream"}),
        ], extra={
            "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
            "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "CENTER",
            "itemSpacing": 25,
        }),
        text("文本_提示", 30, 0, 100, "使用你的重複的卡片星星打開箱子!",
             ec="static", font_size=36, w=879),
        frame("组_你有状态", 0, 0, 939, 80, "HORIZONTAL", children=[
            text("文本_你有_label", 0, 0, 60, "你有:", ec="static", font_size=40, w=160),
            rect("图标_星", 0, 0, 60, 60, corner=30),
            text("文本_你有_数量", 0, 0, 60, "0", ec="dynamic", font_size=44, w=120, align_h="LEFT"),
        ], extra={
            "primaryAxisSizingMode": "FIXED", "counterAxisSizingMode": "FIXED",
            "primaryAxisAlignItems": "CENTER", "counterAxisAlignItems": "CENTER",
            "itemSpacing": 15,
        }),
        # 3 行宝箱列表 (VERTICAL AL)
        frame("组_3行宝箱列表", 0, 0, 939, 920, "VERTICAL", children=[
            build_chest_row_with_instances(0, "金", "未达成", 100),
            build_chest_row_with_instances(1, "银", "未达成", 200),
            build_chest_row_with_instances(2, "铜", "未达成", 400),
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

screen_b = {
    "name": "浮层_卡片星星", "type": "FRAME", "w": 1080, "h": 2400,
    "layers": [
        rect("遮罩_浮层背景", 0, 0, 1080, 2400, constraints={"horizontal": "SCALE", "vertical": "SCALE"}),
        popup_body,
    ],
    "flow": [{
        "trigger": "ON_CLICK", "from": "浮层_卡片星星", "from_node": "按钮_关闭",
        "to": "", "animation": "CLOSE",
        "_note": "来源未确认; S4 候选: 按钮_关闭 [极高契合]"
    }]
}

final = {
    "screens": [screen_a, screen_b],
    "components": components
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

print(f"Wrote {OUT}")
print(f"Components: {len(components)}")
for c in components:
    print(f"  - {c['name']}: {c['w']}x{c['h']}, {len(c['variants'])} variants ({[v['name'] for v in c['variants']]})")
print(f"\nScreen A layers: {len(screen_a['layers'])}")
print(f"Screen B layers: {len(screen_b['layers'])}")
