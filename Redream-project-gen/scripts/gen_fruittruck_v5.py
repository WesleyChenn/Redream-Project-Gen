#!/usr/bin/env python3
"""
FruitTruck CCB 工程结构图 v5
严格对照参考图：
  上半 — 白底，Header + 时间线4列表格 + 节点列表
  下半 — 深底，Rebolt三栏（自定义函数 | 程序变量 | 通知工程师）
"""
import sys, subprocess

FAM = "system-ui,-apple-system,PingFang SC,Noto Sans CJK SC,sans-serif"

# ══════════════════════════════════════════════
# 颜色
# ══════════════════════════════════════════════
# 上半（浅色区）
L_BG   = "#FFFFFF"     # 卡片浅色区底
L_BDR  = "#E2E2EC"     # 卡片描边
L_ROW  = "#F4F4F8"     # 时间线/节点行底色
L_ROW2 = "#EEEEF4"     # 行交替底色
L_TXT  = "#111122"     # 主文字（深）
L_GRY  = "#8888AA"     # 次要文字（灰）
L_DOT_TL = "#4499FF"   # 时间线 section 蓝点
L_DOT_ND = "#333344"   # 节点 section 深点
L_HDR_BG = "#F0F0F8"   # 标题区底色

# 下半（深色区）
D_BG   = "#181820"     # 深色区底
D_ROW  = "#252535"     # item 行底
D_TXT  = "#E8E8F0"     # 深区主文字
D_GRY  = "#7070A0"     # 深区次要文字
D_SEP  = "#28283A"     # 三栏间分隔线

# Rebolt 标题色
C_FN  = "#FF4455"   # 自定义函数 红
C_VAR = "#FF8800"   # 程序变量 橙
C_NTF = "#FFD700"   # 通知工程师 金黄

# 函数 badge
B_PROG = ("#2A3E6A", "#7A9AEE")  # "程序"  (bg, tc)
B_LOC  = ("#323244", "#9090B8")  # "本地"

# 变量 badge
B_VAR  = ("#3A2A00", "#DDAA44")  # 枚举/整型 等

# 连线
LINE_S = "#6666AA"   # stub（实线）
LINE_D = "#CC6600"   # dyn（虚线）

# 循环 tag  (在表格循环列中)
TAG_LOOP = "#22AA55"  # 绿
TAG_SMPL = "#AA3322"  # 暗红

# ══════════════════════════════════════════════
# 布局常量
# ══════════════════════════════════════════════
CARD_W   = 580          # 卡片宽
CARD_RX  = 18           # 圆角半径
LPAD     = 20           # 浅色区内边距
DPAD     = 16           # 深色区内边距

HDR_H    = 86           # Header 区高度
SEC_H    = 32           # Section 标题行高（时间线/节点）
TL_CH    = 28           # 时间线列标题行高
TL_RH    = 46           # 时间线数据行高
ND_RH    = 40           # 节点行高
SEC_GAP  = 12           # Section 间距
DARK_PT  = 16           # 深区顶部 padding
DARK_PB  = 16           # 深区底部 padding
RBT_CH   = 30           # Rebolt 列标题高
RBT_RH   = 38           # Rebolt 行高

COL_GAP  = 100          # 列间距
ROW_GAP  = 40           # 同列卡片间距
CPAX     = 60           # 画布左右边距
CPAY     = 72           # 画布顶部边距

# 时间线4列宽度比
TL_C1    = 0.32         # 时间线名
TL_C2    = 0.40         # 说明
TL_C3    = 0.14         # 音频
TL_C4    = 0.14         # 循环

# Rebolt 三栏宽
def _rbt_col_w():
    return (CARD_W - 2*DPAD - 2) // 3   # 2px 用于两条分隔线

# ══════════════════════════════════════════════
# SVG 工具
# ══════════════════════════════════════════════
def esc(s): return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def R(x,y,w,h,fill,rx=0,stroke=None,sw=1,opacity=None):
    op = f' opacity="{opacity}"' if opacity else ""
    s  = f'stroke="{stroke}" stroke-width="{sw}"' if stroke else 'stroke="none"'
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" {s}{op}/>'

def Ci(cx,cy,r,fill,stroke=None,sw=1.5):
    s = f'stroke="{stroke}" stroke-width="{sw}"' if stroke else 'stroke="none"'
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" {s}/>'

def T(x,y,s,sz=14,fill=L_TXT,anchor="start",weight="normal",dy_=0,max_w=0):
    """max_w>0 时用 textLength 限宽截断"""
    d = f' dy="{dy_}"' if dy_ else ""
    if max_w > 0:
        char_w = sz * (1.05 if any(ord(c)>127 for c in s) else 0.6)
        max_chars = max(4, int(max_w / char_w))
        if len(s) > max_chars:
            s = s[:max_chars-1] + "…"
    return (f'<text x="{x}" y="{y}" font-size="{sz}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" '
            f'font-family="{FAM}"{d}>{esc(s)}</text>')

def Hline(x1,y,x2,clr):
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{clr}" stroke-width="1"/>'
def Vline(x,y1,y2,clr):
    return f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{clr}" stroke-width="1"/>'

def Bezier(x1,y1,x2,y2,clr,dash="",sw=2):
    mx=(x1+x2)//2
    d=f"M {x1} {y1} C {mx} {y1},{mx} {y2},{x2} {y2}"
    da=f'stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{clr}" stroke-width="{sw}" {da}/>'

def RoutedLine(x1,y1,x2,y2,via_y,clr,dash="",sw=2):
    """L形路由连线：从源点上行到 via_y 水平通道，再下行到目标。
    用于跨多列的连线，避免穿越中间卡片。"""
    r = 10  # 圆角半径
    if y1 > via_y:
        # 上行部分有圆角
        d = (f"M {x1} {y1} "
             f"L {x1} {via_y+r} "
             f"Q {x1} {via_y} {x1+r} {via_y} "
             f"L {x2-r} {via_y} "
             f"Q {x2} {via_y} {x2} {via_y+r} "
             f"L {x2} {y2}")
    else:
        d = f"M {x1} {y1} L {x1} {via_y} L {x2} {via_y} L {x2} {y2}"
    da = f'stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{clr}" stroke-width="{sw}" {da} stroke-linejoin="round"/>'

def pill_w(label, sz=11):
    return int(sum(sz*1.05 if ord(c)>127 else sz*0.6 for c in label) + 18)

def Pill(x,y,label,bg,tc="#fff",sz=11,h=20):
    w = pill_w(label,sz)
    return (R(x,y,w,h,bg,rx=10)
            + T(x+w//2, y+14, label, sz=sz, fill=tc, anchor="middle", weight="600"))

# Level badge (L1/L2/…)
def LevelBadge(x, y, level):
    sz = 46
    return (R(x,y,sz,sz,"#222233",rx=10)
            + T(x+sz//2, y+sz//2+7, f"L{level}", sz=16,
                fill="#FFFFFF", anchor="middle", weight="700"))

# ══════════════════════════════════════════════
# 高度计算
# ══════════════════════════════════════════════
def calc_light_h(cd):
    tls = cd.get("timelines", [])
    nds = cd.get("nodes", [])
    h = LPAD + HDR_H + LPAD
    if tls:
        h += SEC_H + TL_CH + len(tls)*TL_RH + SEC_GAP
    if nds:
        h += SEC_H + len(nds)*ND_RH + SEC_GAP
    h += LPAD
    return h

def calc_dark_h(cd):
    rbt = cd.get("rebolt", {})
    if not rbt: return 0
    fns = rbt.get("funcs", [])
    vs  = rbt.get("vars", [])
    nts = rbt.get("notifs", [])
    max_rows = max(len(fns), len(vs), len(nts), 0)
    return DARK_PT + RBT_CH + max_rows * RBT_RH + DARK_PB

def calc_h(cd):
    return calc_light_h(cd) + calc_dark_h(cd)

# ══════════════════════════════════════════════
# 卡片渲染
# ══════════════════════════════════════════════
def build_card(cd):
    cx, cy = cd["x"], cd["y"]
    name   = cd["name"]
    level  = cd.get("level", 2)
    desc   = cd.get("desc", "")
    tls    = cd.get("timelines", [])
    nds    = cd.get("nodes", [])
    rbt    = cd.get("rebolt", {})
    fns    = rbt.get("funcs", [])
    vs     = rbt.get("vars", [])
    nts    = rbt.get("notifs", [])

    lh  = calc_light_h(cd)
    dh  = calc_dark_h(cd)
    tot = lh + dh
    dots = {}
    p = []

    # ── 外框 ──────────────────────────────────────────────────────────────
    # 浅色外框（完整卡片）
    p.append(R(cx, cy, CARD_W, tot, L_BG, rx=CARD_RX, stroke=L_BDR, sw=1))
    # 深色区覆盖下半（尖上、圆下）
    if dh > 0:
        p.append(R(cx, cy+lh, CARD_W, dh, D_BG, rx=0))
        # 底部圆角覆盖
        p.append(R(cx, cy+lh+dh-CARD_RX, CARD_W, CARD_RX, D_BG, rx=0))
        p.append(R(cx, cy+tot-CARD_RX*2, CARD_W, CARD_RX*2, D_BG, rx=CARD_RX))

    # ── Header（浅色区） ──────────────────────────────────────────────────
    dy = cy + LPAD
    # 标题背景条
    p.append(R(cx, cy, CARD_W, HDR_H+LPAD, L_HDR_BG, rx=CARD_RX))
    p.append(R(cx, cy+HDR_H+LPAD-10, CARD_W, 10, L_HDR_BG, rx=0))
    # Level badge
    p.append(LevelBadge(cx+LPAD, dy, level))
    # 标题 + 说明
    tx = cx + LPAD + 46 + 14
    p.append(T(tx, dy+24, name, sz=20, fill=L_TXT, weight="700"))
    if desc:
        p.append(T(tx, dy+46, desc, sz=12, fill=L_GRY))

    dy = cy + LPAD + HDR_H + LPAD

    # ── 时间线 Section ────────────────────────────────────────────────────
    if tls:
        # Section header
        p.append(Ci(cx+LPAD+5, dy+SEC_H//2, 6, L_DOT_TL))
        p.append(T(cx+LPAD+18, dy+SEC_H//2+5, "时间线", sz=13, fill=L_GRY, weight="600"))
        dy += SEC_H

        # 列标题行
        c1x = cx+LPAD
        c2x = c1x + int(CARD_W*TL_C1)
        c3x = c2x + int(CARD_W*TL_C2)
        c4x = c3x + int(CARD_W*TL_C3)
        inner_w = CARD_W - LPAD*2

        p.append(R(cx+LPAD, dy, inner_w, TL_CH, L_ROW2, rx=6))
        p.append(T(c1x+10, dy+TL_CH//2+5, "时间线",  sz=12, fill=L_GRY))
        p.append(T(c2x+8,  dy+TL_CH//2+5, "说明",    sz=12, fill=L_GRY))
        p.append(T(c3x+8,  dy+TL_CH//2+5, "音频",    sz=12, fill=L_GRY))
        p.append(T(c4x+8,  dy+TL_CH//2+5, "循环",    sz=12, fill=L_GRY))
        dy += TL_CH

        # 时间线行
        for i, row in enumerate(tls):
            clip_n = row[0]
            desc_t = row[1] if len(row)>1 else ""
            audio  = row[2] if len(row)>2 else "/"
            loop   = row[3] if len(row)>3 else "/"
            bg = L_ROW if i%2==0 else L_ROW2
            p.append(R(cx+LPAD, dy, inner_w, TL_RH, bg, rx=0))
            # 底部分隔线
            p.append(Hline(cx+LPAD, dy+TL_RH-1, cx+LPAD+inner_w, L_BDR))
            # 文字
            p.append(T(c1x+10, dy+TL_RH//2+5, clip_n, sz=13, fill=L_TXT, weight="600"))
            p.append(T(c2x+8,  dy+TL_RH//2+5, desc_t, sz=12, fill=L_GRY))
            # 音频
            if audio == "有":
                p.append(T(c3x+8, dy+TL_RH//2+5, "有", sz=12, fill="#44AA66", weight="600"))
            else:
                p.append(T(c3x+8, dy+TL_RH//2+5, "/", sz=12, fill=L_GRY))
            # 循环
            if loop == "自循环":
                pw = pill_w("自循环", 11)
                p.append(Pill(c4x+4, dy+TL_RH//2-10, "自循环", TAG_LOOP, "#fff", sz=11, h=20))
            else:
                p.append(T(c4x+8, dy+TL_RH//2+5, "/", sz=12, fill=L_GRY))
            dy += TL_RH
        dy += SEC_GAP

    # ── 节点 Section ─────────────────────────────────────────────────────
    if nds:
        p.append(Ci(cx+LPAD+5, dy+SEC_H//2, 6, L_DOT_ND))
        p.append(T(cx+LPAD+18, dy+SEC_H//2+5, "节点", sz=13, fill=L_GRY, weight="600"))
        dy += SEC_H

        inner_w = CARD_W - LPAD*2
        for i, item in enumerate(nds):
            lbl  = item["label"]
            ik   = item["icon"]
            rdot = item.get("rdot")
            bg   = L_ROW if i%2==0 else L_ROW2
            p.append(R(cx+LPAD, dy, inner_w, ND_RH, bg, rx=0))
            p.append(Hline(cx+LPAD, dy+ND_RH-1, cx+LPAD+inner_w, L_BDR))
            # 右侧类型 badge（先算宽，再限制文字不超出）
            type_map = {"S":"图片","Lb":"文本","Sp":"动画","N":"定位点","La":"定位区","Ly":"定位层","Pos":"坐标点"}
            type_lbl = type_map.get(ik,"")
            type_col = {"S":"#3366CC","Lb":"#CC6600","Sp":"#AA00AA","N":"#444455","La":"#667788","Ly":"#556677"}.get(ik,"#444466")
            badge_w = pill_w(type_lbl,10) if type_lbl else 0
            txt_max = CARD_W - 2*LPAD - 10 - badge_w - (8 if badge_w else 0)
            p.append(T(cx+LPAD+10, dy+ND_RH//2+5, lbl, sz=13, fill=L_TXT, max_w=txt_max))
            if type_lbl:
                p.append(Pill(cx+CARD_W-LPAD-badge_w, dy+ND_RH//2-10,
                              type_lbl, type_col+"44", type_col, sz=10, h=20))
            # 连接点
            if rdot:
                rdx, rdy = cx+CARD_W, dy+ND_RH//2
                p.append(Ci(rdx, rdy, 5, "none", stroke=LINE_S, sw=2))
                dots[rdot] = (rdx, rdy)
            dy += ND_RH
        dy += SEC_GAP

    # ── Rebolt 区（深色） ─────────────────────────────────────────────────
    if rbt:
        dy = cy + lh + DARK_PT
        cw = _rbt_col_w()

        # 三列 x 坐标
        c1x = cx + DPAD
        c2x = c1x + cw + 1
        c3x = c2x + cw + 1

        # 竖向分隔线
        p.append(Vline(c2x-1, cy+lh+DARK_PT//2, cy+lh+dh-DARK_PB//2, D_SEP))
        p.append(Vline(c3x-1, cy+lh+DARK_PT//2, cy+lh+dh-DARK_PB//2, D_SEP))

        # 列标题
        def col_hdr(x, dot_c, label):
            p.append(Ci(x+7, dy+RBT_CH//2, 6, dot_c))
            p.append(T(x+18, dy+RBT_CH//2+5, label, sz=13, fill=dot_c, weight="600"))

        col_hdr(c1x, C_FN,  "自定义函数")
        col_hdr(c2x, C_VAR, "程序变量")
        col_hdr(c3x, C_NTF, "通知工程师")
        ry = dy + RBT_CH

        max_rows = max(len(fns), len(vs), len(nts))
        for i in range(max_rows):
            row_y = ry + i*RBT_RH

            # 自定义函数
            if i < len(fns):
                fn_name, fn_badge = fns[i]
                p.append(R(c1x, row_y+3, cw-4, RBT_RH-6, D_ROW, rx=6))
                if fn_badge:
                    bg_, tc_ = B_PROG if fn_badge=="程序" else B_LOC
                    bw = pill_w(fn_badge, 10)
                    p.append(Pill(c1x+cw-4-bw, row_y+RBT_RH//2-9, fn_badge, bg_, tc_, sz=10, h=18))
                    p.append(T(c1x+8, row_y+RBT_RH//2+5, fn_name, sz=12, fill=D_TXT, max_w=cw-bw-24))
                else:
                    p.append(T(c1x+8, row_y+RBT_RH//2+5, fn_name, sz=12, fill=D_TXT, max_w=cw-16))

            # 程序变量
            if i < len(vs):
                var_name, var_badge = vs[i]
                p.append(R(c2x, row_y+3, cw-4, RBT_RH-6, D_ROW, rx=6))
                if var_badge:
                    bw = pill_w(var_badge, 10)
                    p.append(Pill(c2x+cw-4-bw, row_y+RBT_RH//2-9, var_badge,
                                  B_VAR[0], B_VAR[1], sz=10, h=18))
                    p.append(T(c2x+8, row_y+RBT_RH//2+5, var_name, sz=12, fill=D_TXT, max_w=cw-bw-24))
                else:
                    p.append(T(c2x+8, row_y+RBT_RH//2+5, var_name, sz=12, fill=D_TXT, max_w=cw-16))

            # 通知工程师
            if i < len(nts):
                nt = nts[i]
                p.append(R(c3x, row_y+3, cw-4, RBT_RH-6, D_ROW, rx=6))
                p.append(T(c3x+8, row_y+RBT_RH//2+5, nt, sz=12, fill=D_TXT, max_w=cw-16))

    return "".join(p), tot, dots


# ══════════════════════════════════════════════
# FruitTruck CCB 数据
# ══════════════════════════════════════════════

import subprocess

CARDS = {

"main": {
    "level":1, "name":"游戏主界面",
    "desc":"游戏核心界面，管理所有子模块生命周期与游戏流程",
    "timelines":[
        ("常态", "游戏界面正常运行时", "/", "/"),
    ],
    "nodes":[
        {"icon":"S",  "label":"图片_背景"},
        {"icon":"La", "label":"游戏板区定位区",   "rdot":"r_board"},
        {"icon":"La", "label":"HUD区定位区",      "rdot":"r_hud"},
        {"icon":"La", "label":"公路区定位区",     "rdot":"r_road"},
        {"icon":"La", "label":"等待槽定位区",     "rdot":"r_slot"},
        {"icon":"La", "label":"颜色桶定位区",     "rdot":"r_barrel"},
        {"icon":"La", "label":"道具栏定位区",     "rdot":"r_boost"},
        {"icon":"La", "label":"广告Banner定位区", "rdot":"r_banner"},
        {"icon":"Ly", "label":"全屏反馈定位层"},
    ],
    "rebolt":{
        "funcs":[("初始化","程序"),("加载关卡","程序"),("消除结果回调","程序"),("通关回调","程序")],
        "vars": [("当前关卡","整型"),("累计分数","整型")],
        "notifs":["关卡开始","关卡通过","游戏结束"],
    }
},

"board": {
    "level":2, "name":"游戏板区",
    "desc":"水果消除棋盘，动态生成格子单元并处理消除逻辑",
    "timelines":[
        ("常态", "棋盘正常显示", "/", "/"),
    ],
    "nodes":[
        {"icon":"S",  "label":"图片_板框背景"},
        {"icon":"S",  "label":"图片_棋盘底纹"},
        {"icon":"La", "label":"格子生成区",    "rdot":"r_fruit"},
    ],
    "rebolt":{
        "funcs":[("初始化棋盘","程序"),("格子点击响应","程序"),("消除判定","程序")],
        "notifs":["消除完成","无解状态"],
    }
},

"hud": {
    "level":2, "name":"HUD区",
    "desc":"顶部状态栏，显示关卡进度与分数",
    "timelines":[
        ("常态", "HUD正常显示", "/", "/"),
    ],
    "nodes":[
        {"icon":"S",  "label":"图片_关卡底板"},
        {"icon":"Lb", "label":"文本_关卡"},
        {"icon":"Lb", "label":"文本_分数"},
        {"icon":"N",  "label":"按钮_重玩"},
        {"icon":"N",  "label":"按钮_暂停"},
    ],
},

"road": {
    "level":2, "name":"公路区",
    "desc":"卡车行驶公路，负责生成与调度卡车队列",
    "timelines":[
        ("常态",        "道路正常显示",     "/", "/"),
        ("动画_卡车进场", "卡车进场前置动作", "/", "/"),
    ],
    "nodes":[
        {"icon":"S",  "label":"图片_公路背景"},
        {"icon":"S",  "label":"图片_草地"},
        {"icon":"La", "label":"卡车队列节点", "rdot":"r_bus"},
        {"icon":"N",  "label":"路牌定位点",   "rdot":"r_sign"},
    ],
    "rebolt":{
        "funcs":[("生成卡车","程序"),("派发卡车","程序")],
        "notifs":["卡车满载出发"],
    }
},

"slot": {
    "level":2, "name":"等待槽",
    "desc":"水果中转等待区，共5个，暂存待分配水果",
    "timelines":[
        ("常态_空",  "槽位为空",       "/", "/"),
        ("动画_填入", "水果进入等待槽", "/", "/"),
        ("动画_送出", "水果送往目标",   "/", "/"),
    ],
    "nodes":[
        {"icon":"S", "label":"图片_槽底"},
        {"icon":"S", "label":"图片_水果"},
    ],
},

"barrel": {
    "level":2, "name":"颜色桶",
    "desc":"按颜色分类的目标容器，5列×3行共15个",
    "timelines":[
        ("常态_空",  "空桶初始状态", "/",  "/"),
        ("常态_满",  "桶满载完成态", "/",  "/"),
        ("动画_填满", "水果落入动效", "有", "/"),
        ("动画_出场", "满桶飞出消除", "有", "/"),
    ],
    "nodes":[
        {"icon":"S",  "label":"图片_桶身"},
        {"icon":"S",  "label":"图片_桶盖"},
        {"icon":"Lb", "label":"文本_数量"},
        {"icon":"La", "label":"水果容纳区"},
    ],
    "rebolt":{
        "funcs":[("装入水果","程序"),("清空桶","程序")],
        "vars": [("桶颜色","枚举"),("已装入数","整型")],
        "notifs":["满桶触发消除"],
    }
},

"boost": {
    "level":2, "name":"按钮_道具",
    "desc":"底部道具栏，包含4种道具按钮及引导逻辑",
    "timelines":[
        ("常态",    "道具可用状态",   "/",  "/"),
        ("动画_点击", "点击触觉反馈",   "有", "/"),
        ("动画_引导", "引导玩家使用闪烁", "/",  "自循环"),
    ],
    "nodes":[
        {"icon":"S",  "label":"图片_道具图标"},
        {"icon":"Lb", "label":"文本_数量"},
        {"icon":"N",  "label":"点击响应区"},
    ],
    "rebolt":{
        "funcs":[("激活道具","程序"),("扣除使用次数","程序")],
        "vars": [("道具类型","枚举"),("剩余数量","整型")],
        "notifs":["道具激活"],
    }
},

"banner": {
    "level":2, "name":"广告Banner",
    "desc":"底部广告横幅，展示可玩广告及下载引导",
    "timelines":[
        ("常态", "广告横幅展示", "/", "/"),
    ],
    "nodes":[
        {"icon":"S",  "label":"图片_banner横幅"},
        {"icon":"S",  "label":"图片_按钮"},
        {"icon":"La", "label":"广告点击响应区"},
    ],
},

"fruit": {
    "level":3, "name":"水果单元",
    "desc":"棋盘中单个水果格子，含5色变体与消除动画",
    "timelines":[
        ("常态_默认", "等待点击触发",   "/",  "/"),
        ("动画_消除", "消除飞出动效",   "有", "/"),
        ("动画_落下", "水果从上方落入", "/",  "/"),
    ],
    "nodes":[
        {"icon":"S",   "label":"图片_水果"},
        {"icon":"Pos", "label":"引导定位点",   "rdot":"r_guide"},
        {"icon":"La",  "label":"特效定位区"},
    ],
},

"bus": {
    "level":3, "name":"卡车_大巴",
    "desc":"承载水果的大巴卡车，含3个座位槽",
    "timelines":[
        ("常态",    "卡车停靠等待",   "/",  "/"),
        ("动画_进场", "从画面左侧驶入", "/",  "/"),
        ("动画_出场", "满载后向右驶离", "有", "/"),
        ("动画_等待", "等待时车身晃动", "/",  "自循环"),
    ],
    "nodes":[
        {"icon":"S",  "label":"图片_车身"},
        {"icon":"Sp", "label":"动画_冒烟特效"},
        {"icon":"N",  "label":"座位槽_1"},
        {"icon":"N",  "label":"座位槽_2"},
        {"icon":"N",  "label":"座位槽_3"},
    ],
    "rebolt":{
        "funcs":[("水果入座","程序"),("满载触发","程序")],
        "vars": [("座位数","整型")],
    }
},

"truck": {
    "level":3, "name":"卡车_货车",
    "desc":"运输水果的货车，左侧进场右侧出场",
    "timelines":[
        ("常态",    "货车停靠等待",   "/",  "/"),
        ("动画_进场", "从画面左侧驶入", "/",  "/"),
        ("动画_出场", "满载后向右驶离", "有", "/"),
    ],
    "nodes":[
        {"icon":"S",  "label":"图片_车身"},
        {"icon":"La", "label":"装载区"},
    ],
},

"sign": {
    "level":3, "name":"路牌",
    "desc":"公路路牌，显示剩余关卡数量",
    "timelines":[
        ("常态",    "路牌立起显示",   "/", "/"),
        ("动画_摆动", "风吹摆动效果", "/", "自循环"),
    ],
    "nodes":[
        {"icon":"S",  "label":"图片_路牌"},
        {"icon":"Lb", "label":"文本_剩余关卡数"},
    ],
},

"guide": {
    "level":4, "name":"点击引导",
    "desc":"手指点击引导动画，引导玩家首次操作",
    "timelines":[
        ("动画_点击引导", "手指点击循环动画", "/", "自循环"),
    ],
    "nodes":[
        {"icon":"S", "label":"图片_引导小手"},
    ],
},

}

# ══════════════════════════════════════════════
# 布局：树形 Y 对齐（卡片让路给连线）
# ══════════════════════════════════════════════
# 规则：
#   · L3 卡片在 Col2 顺序堆叠（基准）
#   · L2 有子节点的：垂直居中对齐到其子节点组的 Y 范围中心
#   · L2 叶节点：自然填充剩余空间
#   · main：垂直居中对齐到所有 L2 的 Y 范围中心
# 效果：所有 Bezier 连线近乎水平，自然散开，无需绕行

def tree_layout():
    COL0_X = CPAX
    COL1_X = CPAX + CARD_W + COL_GAP
    COL2_X = CPAX + 2 * (CARD_W + COL_GAP)

    # ──────────────────────────────────────────────────────────────────
    # 4 列布局：
    #   Col 0 (COL0_X): main（根节点）
    #   Col 1 (COL1_X): board / hud / road（有子节点的 L2）
    #   Col 2 (COL2_X): fruit / bus / truck / sign / guide（L3）
    #   Col 3 (COL3_X): slot / barrel / boost / banner（叶节点 L2）
    #
    # 连线策略：
    #   main → Col1 (相邻, 曲线)
    #   main → Col3 (相邻右侧, 曲线——比 main→Col1 稍长但仍清晰)
    #   Col1 → Col2 (相邻, 曲线)
    # ──────────────────────────────────────────────────────────────────
    COL3_X = CPAX + 3 * (CARD_W + COL_GAP)

    # ── Step 1: L3 在 Col2 堆叠（基准柱）────────────────────────────
    col2_order = ["fruit", "bus", "truck", "sign", "guide"]
    y = CPAY
    for key in col2_order:
        CARDS[key]["x"] = COL2_X
        CARDS[key]["y"] = y
        y += calc_h(CARDS[key]) + ROW_GAP

    def group_span(keys):
        tops    = [CARDS[k]["y"] for k in keys]
        bottoms = [CARDS[k]["y"] + calc_h(CARDS[k]) for k in keys]
        return min(tops), max(bottoms)

    # ── Step 2: Col1 有子节点的 L2——Y 对齐到子节点组中心 ─────────────
    for parent, children in [("board", ["fruit"]),
                              ("road",  ["bus", "truck", "sign"])]:
        span_top, span_bot = group_span(children)
        center = (span_top + span_bot) / 2
        ph = calc_h(CARDS[parent])
        CARDS[parent]["x"] = COL1_X
        CARDS[parent]["y"] = max(CPAY, int(center - ph / 2))

    # ── Step 3: hud——紧接在 road 之后（避免空间争抢问题）──────────────
    # hud 是叶节点，不需要 Y 对齐到任何 Col2 卡片，放 road 下面最简洁
    road_bot  = CARDS["road"]["y"] + calc_h(CARDS["road"])
    CARDS["hud"]["x"] = COL1_X
    CARDS["hud"]["y"] = road_bot + ROW_GAP

    # ── Step 4: Col3 叶节点——与 Col2 的 L3 对齐（避免 Col3 和 Col2 高差太大）
    # 叶节点从 Col2 顶部开始，均匀分布
    col2_top, col2_bot = group_span(col2_order)
    col2_h    = col2_bot - col2_top
    leaves    = ["slot", "barrel", "boost", "banner"]
    leaves_total = sum(calc_h(CARDS[k]) for k in leaves) + (len(leaves)-1)*ROW_GAP
    # 居中对齐到 Col2 的纵向中心
    col2_center = (col2_top + col2_bot) / 2
    after_y = max(CPAY, int(col2_center - leaves_total / 2))
    for key in leaves:
        CARDS[key]["x"] = COL3_X
        CARDS[key]["y"] = after_y
        after_y += calc_h(CARDS[key]) + ROW_GAP

    # ── Step 5: main——居中对齐到 Col1 + Col3 所有子节点 ──────────────
    all_children = ["board", "hud", "road", "slot", "barrel", "boost", "banner"]
    ch_top, ch_bot = group_span(all_children)
    main_h = calc_h(CARDS["main"])
    CARDS["main"]["x"] = COL0_X
    CARDS["main"]["y"] = max(CPAY, int((ch_top + ch_bot) / 2 - main_h / 2))

    # Canvas
    all_keys = list(CARDS.keys())
    max_x = max(CARDS[k]["x"] + CARD_W for k in all_keys)
    max_y = max(CARDS[k]["y"] + calc_h(CARDS[k]) for k in all_keys)
    return max_x + CPAX, max_y + 80

W, H = tree_layout()

CONNS = [
    # ── main → Col1（左侧 L2，短曲线）────────────────────────────────
    {"t":"stub","f":"r_board",  "to":"board"},
    {"t":"stub","f":"r_hud",    "to":"hud"},
    {"t":"stub","f":"r_road",   "to":"road"},
    # ── main → Col3（右侧叶节点，曲线向右，不经过 Col1/Col2）─────────
    {"t":"stub","f":"r_slot",   "to":"slot"},
    {"t":"stub","f":"r_barrel", "to":"barrel"},
    {"t":"stub","f":"r_boost",  "to":"boost"},
    {"t":"stub","f":"r_banner", "to":"banner"},
    # ── Col1 → Col2（L2 对齐子节点，连线近水平）─────────────────────
    {"t":"dyn", "f":"r_fruit",  "to":"fruit"},
    {"t":"dyn", "f":"r_bus",    "to":"bus"},
    {"t":"dyn", "f":"r_bus",    "to":"truck"},
    {"t":"stub","f":"r_sign",   "to":"sign"},
    {"t":"dyn", "f":"r_guide",  "to":"guide"},
]

# ══════════════════════════════════════════════
# 渲染
# ══════════════════════════════════════════════
svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    f'<rect width="{W}" height="{H}" fill="#0F0F14"/>',
]

all_dots = {}
card_svgs = []
for key, cd in CARDS.items():
    s, h, dots = build_card(cd)
    card_svgs.append(s)
    all_dots.update(dots)

# 连线（先渲染，在卡片下方）
svg.append('<g id="conn">')
for conn in CONNS:
    did  = conn["f"]
    tkey = conn["to"]
    ct   = conn["t"]
    if did not in all_dots or tkey not in CARDS: continue
    x1, y1 = all_dots[did]
    x2 = CARDS[tkey]["x"]
    y2 = CARDS[tkey]["y"] + calc_h(CARDS[tkey]) // 2   # 连到目标卡片中部
    clr  = LINE_S if ct=="stub" else LINE_D
    dash = "" if ct=="stub" else "8,5"
    svg.append(Bezier(x1, y1, x2, y2, clr, dash, 2))
    svg.append(Ci(x2, y2, 5, clr))
svg.append('</g>')

svg.append('<g id="cards">' + "".join(card_svgs) + '</g>')

# 图例
leg_y = H - 36; lx = CPAX
leg = []
items=[("●",L_DOT_TL,"图片/Sprite"),("●",C_FN,"自定义函数"),("●",C_VAR,"程序变量"),("●",C_NTF,"通知工程师")]
for sym,clr,lbl in items:
    leg.append(Ci(lx+6,leg_y+10,6,clr))
    leg.append(T(lx+16,leg_y+15,lbl,sz=12,fill="#9090B0"))
    lx+=max(len(lbl)*14+24, 120)
leg.append(Bezier(lx,leg_y+10,lx+32,leg_y+10,LINE_S,"",2))
leg.append(T(lx+36,leg_y+15,"stub 嵌套",sz=12,fill="#9090B0"))
lx+=140
leg.append(Bezier(lx,leg_y+10,lx+32,leg_y+10,LINE_D,"8,5",2))
leg.append(T(lx+36,leg_y+15,"dynamicInstantiate",sz=12,fill="#9090B0"))
svg.append('<g id="legend">'+"".join(leg)+'</g>')
svg.append(f'<text x="{W-24}" y="{H-18}" font-size="12" fill="#505070" '
           f'text-anchor="end" font-family="{FAM}">Ada · FruitTruck CCB 结构图 v5</text>')
svg.append('</svg>')

SVG_PATH = '/tmp/FruitTruck_v5.svg'
PNG_PATH = '/tmp/FruitTruck_v5.png'
with open(SVG_PATH,'w',encoding='utf-8') as f:
    f.write("\n".join(svg))
print(f"Canvas: {W}×{H}")

r = subprocess.run(
    ['python3','-c',
     f'import cairosvg; cairosvg.svg2png(url="{SVG_PATH}",write_to="{PNG_PATH}",scale=2)'],
    capture_output=True)
if r.returncode != 0:
    subprocess.run(['rsvg-convert','-w',str(W*2),'-h',str(H*2),'-o',PNG_PATH,SVG_PATH])
    print(r.stderr.decode()[:200])
print(f'✅ {PNG_PATH}')
