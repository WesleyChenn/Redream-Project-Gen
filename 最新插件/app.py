"""
RED Tool — Redream 工具箱（CLI 驱动版）
运行: python app.py
浏览器打开: http://localhost:5001

流程:
  Figma JSON → Python 生成中间 .red → CLI build-scene 规范化 → CLI inspect check 校验

v20.7 新增:
  - /api/generate_red：接收 v20.6 schema（含 components + INSTANCE）生成 .red
  - /api/ping：连通性检测
  - CORS 头：允许 Figma 插件跨域访问
"""
from flask import Flask, render_template, request, jsonify
import plistlib, json, os, random, subprocess, tempfile, shutil
from pathlib import Path

app = Flask(__name__)
app.config['JSON_ENSURE_ASCII'] = False

# ═══════════════════════════════════════════════════
#  CORS（让 Figma 插件能跨域访问）
# ═══════════════════════════════════════════════════
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/api/<path:any>', methods=['OPTIONS'])
def cors_preflight(any):
    return '', 204


# ═══════════════════════════════════════════════════
#  配置
# ═══════════════════════════════════════════════════
DEFAULT_OUTPUT   = os.path.expanduser('~/Desktop/red_output')
PROJECT_NAME     = 'red_project'
REDREAM_CLI      = '/Applications/Redream.app/Contents/MacOS/Redream'

# ═══════════════════════════════════════════════════
#  ID 生成（用于中间 .red 文件）
# ═══════════════════════════════════════════════════
_used_ids: set = set()

def reset_ids():
    global _used_ids
    _used_ids = set()

def new_id() -> int:
    while True:
        i = random.randint(100_000_000, 999_999_999)
        if i not in _used_ids:
            _used_ids.add(i)
            return i

# ═══════════════════════════════════════════════════
#  属性构建
# ═══════════════════════════════════════════════════
def p_pos(x, y, ux=0, uy=0):
    return {'name':'position',    'type':'Position', 'value':[float(x),float(y),0,ux,uy]}
def p_size(w, h, uw=0, uh=0):
    return {'name':'contentSize', 'type':'Size',     'value':[float(w),float(h),uw,uh,False,False]}
def p_anchor(ax, ay):
    return {'name':'anchorPoint', 'type':'Point',    'value':[float(ax),float(ay)]}
def p_ignoreAP(v=False):
    return {'name':'ignoreAnchorPointForPosition','type':'Check','value':v}
def p_opacity(v=255):
    return {'name':'opacity','type':'Byte','value':v}
def p_color(r=255,g=255,b=255):
    return {'name':'color','type':'Color3','value':[r,g,b]}
def p_sprite():
    return {'name':'displayFrame','type':'SpriteFrame','value':['','']}
def p_cccontrol():
    return {'name':'ccControl','type':'BlockCCControl','value':['',1,32]}
def p_preferedsize(w, h, uw=0, uh=0):
    return {'name':'preferedSize','type':'Size','value':[float(w),float(h),uw,uh,False,False]}
def p_visible(v=True):
    return {'name':'visible','type':'Check','value':v}

# ═══════════════════════════════════════════════════
#  节点工厂
# ═══════════════════════════════════════════════════
def make_node(base, name, props, children=None, custom=''):
    return {
        'animatedProperties': {},
        'baseClass': base,
        'children': children or [],
        'customClass': custom,
        'customProperties': [],
        'displayName': name,
        'expand': False,
        'hidden': False,
        'locked': False,
        'memberVarAssignmentName': '',
        'memberVarAssignmentType': 0,
        'nodeColorTag': 0,
        'properties': props,
        'seqExpanded': False,
        'uniqueNodeId': new_id(),
    }

# ═══════════════════════════════════════════════════
#  节点构建（和之前一致的规则）
# ═══════════════════════════════════════════════════
def make_ccnode(name, px, py, ux, uy, w, h, uw, uh, ax, ay, children=None):
    return make_node('CCNode', name, [
        p_pos(px, py, ux, uy),
        p_size(w, h, uw, uh),
        p_anchor(ax, ay),
        p_ignoreAP(), p_opacity(), p_color(),
    ], children)

def make_ccsprite(name, px, py, ux, uy, w, h):
    return make_node('CCSprite', name, [
        p_pos(px, py, ux, uy),
        p_size(w, h),
        p_anchor(0.5, 0.5),
        p_ignoreAP(), p_opacity(), p_color(), p_sprite(),
    ])

# CCProgressTimer 方向映射表
# Figma direction → (barType, midpoint[x,y], barChangeRate[x,y])
PROGRESS_DIRECTION_MAP = {
    'horizontal_lr': (0, [0.0, 0.5], [1.0, 0.0]),   # 水平左→右（默认）
    'horizontal_rl': (0, [1.0, 0.5], [1.0, 0.0]),   # 水平右→左
    'vertical_bt':   (0, [0.5, 0.0], [0.0, 1.0]),   # 垂直下→上
    'vertical_tb':   (0, [0.5, 1.0], [0.0, 1.0]),   # 垂直上→下
}

def parse_progress_direction(name):
    """
    从节点名末尾解析 direction（v20.4 规范）：
    - 末尾 _rl → horizontal_rl
    - 末尾 _tb → vertical_tb
    - 末尾 _bt → vertical_bt
    - 其他（包括无后缀、含 _cw/_ccw 等不识别的）→ horizontal_lr（默认）
    """
    if name.endswith('_rl'): return 'horizontal_rl'
    if name.endswith('_tb'): return 'vertical_tb'
    if name.endswith('_bt'): return 'vertical_bt'
    return 'horizontal_lr'

def make_progresstimer(name, px, py, ux, uy, w, h):
    """
    CCProgressTimer 节点：进度条（动态填充部分）

    direction 从节点名末尾解析（_rl/_tb/_bt 或默认 horizontal_lr）
    percentage 固定默认 100（视觉满，运行时由代码控制）
    """
    direction = parse_progress_direction(name)
    bar_type, midpoint, change_rate = PROGRESS_DIRECTION_MAP[direction]

    return make_node('CCProgressTimer', name, [
        p_pos(px, py, ux, uy),
        p_size(w, h),
        p_anchor(0.5, 0.5),
        p_ignoreAP(), p_opacity(), p_color(), p_sprite(),
        {'name':'percentage',      'type':'Float',          'value': 100.0},
        {'name':'barType',         'type':'IntegerLabeled', 'value': bar_type},
        {'name':'midpoint',        'type':'Point',          'value': midpoint},
        {'name':'barChangeRate',   'type':'Point',          'value': change_rate},
        {'name':'reverseDirection','type':'Check',          'value': False},
    ])

def make_ccbutton(name, px, py, ux, uy, w, h, children=None):
    return make_node('REDNodeButton', name, [
        p_pos(px, py, ux, uy),
        p_size(w, h),
        p_anchor(0.5, 0.5),
        p_opacity(), p_color(), p_cccontrol(),
        p_preferedsize(w, h),
    ], children)

def make_cclabel(name, px, py, ux, uy, text=''):
    return make_node('CCRedLabel', name, [
        p_visible(True),
        p_pos(px, py, ux, uy),
        p_anchor(0.5, 0.5),
        p_opacity(),
        p_color(31,31,31), p_color(31,31,31),
        {'name':'string',               'type':'Text',          'value':text},
        {'name':'frontBMFntFile',        'type':'FntFile',       'value':''},
        {'name':'backBMFntFile',         'type':'FntFile',       'value':''},
        {'name':'horizontalAlignment',   'type':'IntegerLabeled','value':1},
        {'name':'verticalAlignment',     'type':'IntegerLabeled','value':1},
        {'name':'dimensions',            'type':'Size',          'value':[0.0,0.0,0,0,False,False]},
        {'name':'enableWrap',            'type':'Check',         'value':False},
    ])

def make_mask():
    return make_node('CCLayerColor', '遮罩_背景', [
        p_pos(50.0, 50.0, 2, 2),
        p_size(100.0, 100.0, 2, 2),
        p_anchor(0.5, 0.5),
        p_ignoreAP(), p_opacity(178), p_color(0, 0, 0),
    ])

def make_scene_root(name, children):
    return make_node('CCNode', name, [
        p_pos(50.0, 50.0, 2, 2),
        p_size(100.0, 100.0, 2, 2),
        p_anchor(0.5, 0.5),
        p_ignoreAP(), p_opacity(), p_color(),
    ], children)

# ═══════════════════════════════════════════════════
#  识别辅助
# ═══════════════════════════════════════════════════
def is_skip(name):
    if name == '弹性缝隙': return True
    if name.startswith('内容区_'): return True
    if name.startswith('底板_') and name.endswith('形状'): return True
    return False

def is_btn_layer(name, node_type=''):
    """
    触控层识别（兼容 v18/v19/v20 三套命名）：
    - v20（新）：按钮_XXX (FRAME) 是触控层
    - v19：底板_XXX (FRAME，非"形状"后缀) 是触控层
    - v18（旧）：切图_底板_XXX 是触控层
    """
    # v18 老命名
    if name.startswith('切图_底板_'):
        return True
    # v20 新命名：按钮_XXX FRAME
    if name.startswith('按钮_') and node_type.upper() == 'FRAME':
        return True
    # v19 过渡命名：底板_XXX FRAME（非"形状"后缀）
    if (name.startswith('底板_') and not name.endswith('形状')
            and node_type.upper() == 'FRAME'):
        return True
    return False

def btn_layer_name(container_name):
    """v20 下容器本身就是按钮_XXX，无需改名"""
    if container_name.startswith('按钮_'):
        return container_name
    # 老命名兼容
    return container_name.replace('组_按钮_','按钮_').replace('按钮_','按钮_')

def auto_btn(name, w, h, kids, ux=0, uy=0):
    """
    如果是按钮容器但没有触控层子节点，自动补一个，
    并把其他内容作为其子节点（这样点击缩放时内容跟随）
    """
    is_btn = name.startswith('按钮_') or name.startswith('组_按钮_')
    if is_btn:
        # 检查是否已有 REDNodeButton 子节点
        has = any(c.get('baseClass') == 'REDNodeButton' for c in kids)
        if not has:
            # 把所有现有内容移到新触控层里面
            other_kids = list(kids)
            kids.clear()
            bd = btn_layer_name(name)
            px = w / 2 if ux == 0 else 50.0
            py = h / 2 if uy == 0 else 50.0
            kids.append(make_ccbutton(bd, px, py, ux, uy, w, h, other_kids))

# ═══════════════════════════════════════════════════
#  子节点构建
# ═══════════════════════════════════════════════════
def build_children(children, parent_w, parent_h, parent_is_fullwidth,
                   offset_x=0.0, offset_y=0.0):
    result = []
    for ch in children or []:
        b = build_child(ch, parent_w, parent_h, parent_is_fullwidth,
                        offset_x, offset_y)
        if b is None: continue
        if isinstance(b, list): result.extend(b)
        else: result.append(b)
    return result

def build_child(n, parent_w, parent_h, parent_is_fullwidth,
                offset_x=0.0, offset_y=0.0):
    name = n.get('name','')
    t    = n.get('type','')
    w    = float(n.get('w',0))
    h    = float(n.get('h',0))
    fx   = float(n.get('x',0)) + offset_x
    fy   = float(n.get('y',0)) + offset_y

    # 跳过：提升子节点
    if is_skip(name):
        return build_children(n.get('children',[]), parent_w, parent_h,
                              parent_is_fullwidth, fx, fy)

    # 遮罩由 generate_red 单独处理
    if name == '遮罩_背景' or name == '底板_遮罩':
        return None

    # 坐标
    cx = fx + w / 2.0
    cy = parent_h - fy - h / 2.0
    if parent_is_fullwidth:
        px = cx / parent_w * 100.0
        py = cy
        ux, uy = 2, 0
    else:
        px = cx
        py = cy
        ux, uy = 0, 0

    # v20.7: INSTANCE 类型 → V1 占位（空 CCNode，contentSize 保留）
    # component_ref 类型 → 同样占位（旧体系不展开）
    if t == 'INSTANCE' or n.get('component_ref'):
        return make_ccnode(name, px, py, ux, uy, w, h, 0, 0, 0.5, 0.5, [])

    # 文本
    if t == 'TEXT' or name.startswith(('文本_','文字_')):
        return make_cclabel(name, px, py, ux, uy, text=n.get('content',''))

    # REDNodeButton（兼容新老命名）
    if is_btn_layer(name, t):
        kids = build_children(n.get('children',[]), w, h, False)
        return make_ccbutton(name, px, py, ux, uy, w, h, kids)

    # CCProgressTimer：进度条节点（v20.4 规范）
    # 识别条件：type=='RECTANGLE' 且 name 以 '进度条_' 开头
    # direction 从节点名末尾解析（_rl/_tb/_bt 或默认 horizontal_lr）
    # percentage 固定默认 100（运行时由代码控制）
    # children 提升到父级（防御性，CCProgressTimer 通常是叶子节点）
    if name.startswith('进度条_') and t == 'RECTANGLE':
        progress_node = make_progresstimer(name, px, py, ux, uy, w, h)
        if n.get('children'):
            siblings = build_children(n.get('children',[]),
                                       parent_w, parent_h, parent_is_fullwidth,
                                       offset_x=fx, offset_y=fy)
            return [progress_node] + siblings
        return progress_node

    # CCSprite
    sprite_pfx = ('图片_','图标_','背景_','插图_','特效_')
    is_rect_底板 = (name.startswith('底板_') and t == 'RECTANGLE'
                    and not name.endswith('形状'))
    if (name.startswith(sprite_pfx) or is_rect_底板
            or (t=='RECTANGLE' and not name.startswith(('切图_底板_','底板_')))):
        return make_ccsprite(name, px, py, ux, uy, w, h)

    # CCNode 容器
    all_kids = build_children(n.get('children',[]), w, h, False)

    # 按钮容器识别：有 REDNodeButton 子节点 = 按钮容器
    btn_node = next((c for c in all_kids
                     if c.get('baseClass') == 'REDNodeButton'), None)
    is_btn_container = (btn_node is not None
                        or name.startswith('按钮_')
                        or name.startswith('组_按钮_'))

    if is_btn_container:
        other_kids = [c for c in all_kids
                      if c.get('baseClass') != 'REDNodeButton']
        if btn_node is None:
            bd = btn_layer_name(name)
            btn_node = make_ccbutton(bd, w/2, h/2, 0, 0, w, h, other_kids)
            return make_ccnode(name, px, py, ux, uy, w, h, 0, 0, 0.5, 0.5, [btn_node])
        else:
            btn_node['children'].extend(other_kids)
            return make_ccnode(name, px, py, ux, uy, w, h, 0, 0, 0.5, 0.5, [btn_node])

    return make_ccnode(name, px, py, ux, uy, w, h, 0, 0, 0.5, 0.5, all_kids)

# ═══════════════════════════════════════════════════
#  顶层节点分类
# ═══════════════════════════════════════════════════
def classify_top_layers(layers, sw, sh):
    result = []
    for n in layers:
        w  = float(n.get('w',0))
        h  = float(n.get('h',0))
        x  = float(n.get('x',0))
        y  = float(n.get('y',0))
        cons = n.get('constraints') or {}
        hc   = cons.get('horizontal','').upper()
        vc   = cons.get('vertical','').upper()
        is_fullwidth = hc == 'SCALE' or (hc == 'LEFT' and sw - (x + w) < 10)
        result.append({
            'node': n, 'w': w, 'h': h, 'x': x, 'y': y,
            'left': x, 'right': sw - (x + w),
            'top': y, 'bottom': sh - (y + h),
            'hc': hc, 'vc': vc, 'is_fullwidth': is_fullwidth,
        })
    return result

def build_top_layer(info, sw, sh):
    n    = info['node']
    name = n.get('name','')
    t    = n.get('node_type','') or n.get('type','')
    w    = info['w']
    h    = info['h']
    hc   = info['hc']
    vc   = info['vc']

    if name == '遮罩_背景':
        return None

    # v20: 顶层节点如果本身是触控层（按钮_XXX FRAME），生成 REDNodeButton
    is_self_btn = is_btn_layer(name, t)

    # 全宽节点
    if info['is_fullwidth']:
        if vc == 'TOP':
            px, ux = 50.0, 2
            py, uy, ay = 100.0, 2, 1.0
        elif vc == 'BOTTOM':
            px, ux = 50.0, 2
            py, uy, ay = 0.0, 2, 0.0
        else:
            px, ux = 50.0, 2
            py, uy, ay = 50.0, 2, 0.5

        kids = build_children(n.get('children',[]), w, h, True)
        if is_self_btn:
            # 顶层本身就是按钮，直接生成 REDNodeButton，不再 auto_btn
            return make_node('REDNodeButton', name, [
                p_pos(px, py, ux, uy),
                p_size(100.0, h, 2, 0),
                p_anchor(0.5, ay),
                p_opacity(), p_color(), p_cccontrol(),
                p_preferedsize(w, h),
            ], kids)
        auto_btn(name, w, h, kids, 2, 0)
        return make_ccnode(name, px, py, ux, uy,
                           100.0, h, 2, 0, 0.5, ay, kids)

    # 固定宽节点：看左右边距对称性
    diff = info['left'] - info['right']
    if abs(diff) < 10:
        px, ux, ax = 50.0, 2, 0.5
    elif info['left'] < info['right']:
        px = info['left'] / sw * 100.0
        ux, ax = 2, 0.0
    else:
        px = info['right'] / sw * 100.0
        ux, ax = 2, 1.0

    if vc == 'CENTER':
        py, uy, ay = 50.0, 2, 0.5
    elif vc == 'TOP':
        py, uy, ay = 100.0, 2, 1.0
    elif vc == 'BOTTOM':
        py, uy, ay = 0.0, 2, 0.0
    else:
        cy = sh - info['y'] - h / 2.0
        py = cy / sh * 100.0
        uy, ay = 2, 0.5

    kids = build_children(n.get('children',[]), w, h, False)
    if is_self_btn:
        return make_ccbutton(name, px, py, ux, uy, w, h, kids)
    auto_btn(name, w, h, kids)
    return make_ccnode(name, px, py, ux, uy, w, h, 0, 0, ax, ay, kids)

# ═══════════════════════════════════════════════════
#  多节点合并
# ═══════════════════════════════════════════════════
def merge_edge_nodes(infos, sw, sh, stick):
    if len(infos) == 1:
        return build_top_layer(infos[0], sw, sh)

    infos_sorted = sorted(infos,
        key=lambda r: r['top'] if stick == 'TOP' else r['bottom'])
    total_h = sum(r['h'] for r in infos_sorted)

    kids = []
    cursor = 0.0
    for r in infos_sorted:
        n = r['node']
        w = r['w']
        h = r['h']
        if stick == 'TOP':
            cy = total_h - cursor - h / 2.0
        else:
            cy = cursor + h / 2.0
        cursor += h

        node_kids = build_children(n.get('children',[]), w, h, True)
        auto_btn(n.get('name',''), w, h, node_kids, 2, 0)
        kids.append(make_ccnode(
            n.get('name',''), 50.0, cy, 2, 0,
            100.0, h, 2, 0, 0.5, 0.5, node_kids
        ))

    wrap_name = '组_顶部合并' if stick == 'TOP' else '组_底部合并'
    if stick == 'TOP':
        px, py, ux, uy, ax, ay = 50.0, 100.0, 2, 2, 0.5, 1.0
    else:
        px, py, ux, uy, ax, ay = 50.0, 0.0, 2, 2, 0.5, 0.0

    return make_ccnode(wrap_name, px, py, ux, uy,
                       100.0, total_h, 2, 0, ax, ay, kids)

# ═══════════════════════════════════════════════════
#  主生成函数（返回 .red dict）
# ═══════════════════════════════════════════════════
def generate_red(screen):
    reset_ids()
    sw   = float(screen.get('w',1080))
    sh   = float(screen.get('h',2400))
    name = screen.get('name','未命名')

    layers    = screen.get('layers',[])
    has_mask  = any(l.get('name') == '遮罩_背景' for l in layers)
    is_overlay= name.startswith('浮层_')

    # 提取背景节点（界面_ 屏幕的全屏背景图，需要单独放进 组_背景层）
    bg_layer = next((l for l in layers
                     if l.get('name','').startswith('背景_')
                     and float(l.get('w',0)) >= sw - 5
                     and float(l.get('h',0)) >= sh - 5), None)

    classified = classify_top_layers(
        [l for l in layers
         if l.get('name') != '遮罩_背景'
         and l is not bg_layer], sw, sh
    )
    top_infos    = [r for r in classified if r['vc'] == 'TOP']
    bottom_infos = [r for r in classified if r['vc'] == 'BOTTOM']
    other_infos  = [r for r in classified if r['vc'] not in ('TOP','BOTTOM')]

    scene_kids = []

    # 所有屏幕（界面_/浮层_）都加「组_背景层」作为 scene_root 第一个子节点
    # 内含「全屏防点击穿透层」+「背景_XXX」（如有）
    bg_kids = [
        # 全屏防点击穿透层（REDNodeButton 100%×100%）
        make_node('REDNodeButton', '全屏防点击穿透层', [
            p_pos(50.0, 50.0, 2, 2),
            p_size(100.0, 100.0, 2, 2),
            p_anchor(0.5, 0.5),
            p_opacity(), p_color(), p_cccontrol(),
            p_preferedsize(100.0, 100.0, 2, 2),
        ]),
    ]
    # 如果有全屏背景图，作为 CCSprite 加入背景层
    if bg_layer is not None:
        bg_name = bg_layer.get('name','背景_未命名')
        bg_kids.append(make_node('CCSprite', bg_name, [
            p_pos(50.0, 50.0, 2, 2),
            p_size(100.0, 100.0, 2, 2),
            p_anchor(0.5, 0.5),
            p_ignoreAP(), p_opacity(), p_color(), p_sprite(),
        ]))
    scene_kids.append(make_ccnode(
        '组_背景层', 50.0, 50.0, 2, 2, 100.0, 100.0, 2, 2, 0.5, 0.5, bg_kids
    ))

    if has_mask:
        scene_kids.append(make_mask())

    for info in other_infos:
        b = build_top_layer(info, sw, sh)
        if b is None: continue
        if isinstance(b, list): scene_kids.extend(b)
        else: scene_kids.append(b)

    if top_infos:
        b = merge_edge_nodes(top_infos, sw, sh, 'TOP')
        if b: scene_kids.append(b)
    if bottom_infos:
        b = merge_edge_nodes(bottom_infos, sw, sh, 'BOTTOM')
        if b: scene_kids.append(b)

    # 总组：CCLayer 下第一个固定叫"总组"的容器节点
    # 屏幕名（界面_主菜单）通过 .red 文件名表达，不再作为 scene_root displayName
    sr = make_scene_root('总组', scene_kids)

    cclayer = {
        'animatedProperties': {},
        'baseClass': 'CCLayer',
        'children': [sr],
        'customClass': 'CoreLayer',
        'customProperties': [],
        'displayName': 'CCLayer',
        'expand': True,
        'hidden': False, 'locked': False,
        'memberVarAssignmentName': '',
        'memberVarAssignmentType': 0,
        'nodeColorTag': 0,
        'properties': [
            {'name':'position',    'type':'Position','value':[0.0,0.0,0,0,0]},
            {'name':'contentSize', 'type':'Size',    'value':[100.0,100.0,2,2,False,False]},
        ],
        'seqExpanded': False,
        'uniqueNodeId': new_id(),
    }

    return {
        'centeredOrigin':    True,
        'currentResolution': 0,
        'currentSequenceId': 0,
        'fileType':          'Redream',
        'fileVersion':       1,
        'guides':            [],
        'nodeGraph':         cclayer,
        'rebolt':            {'isRebolted':False,'redInfos':{}},
        'resolutions': [
            {'additionalScale':2.0,'centeredOrigin':False,'height':2400,
             'mainScale':2.0,'name':'1080x2400','resourceScale':2.0,'scale':2.0,'width':1080},
        ],
        'sequences': [{
            'autoPlay': False,
            'callbackChannel': {'keyframes':[],'name':'','type':0},
            'chainedSequenceId': -1,
            'length': 10.0,
            'name': 'Default Timeline',
            'offset': 0.0, 'position': 0.0,
            'resolution': 30.0, 'scale': 128.0,
            'sequenceId': 0,
            'shake2Channel': {'keyframes':[],'name':'','type':0},
            'shakeChannel':  {'keyframes':[],'name':'','type':0},
            'soundChannel':  {'keyframes':[],'name':'','type':0},
            'timelineEndPlay': 10.0, 'timelineStartPlay': 0.0,
            'wiseChannel':   {'keyframes':[],'name':'','type':0},
        }],
        'stageBorder': 0,
    }

# ═══════════════════════════════════════════════════
#  CLI 调用封装
# ═══════════════════════════════════════════════════
def run_cli(args, cwd=None):
    """统一调用 Redream CLI，返回 (success, stdout, stderr)"""
    if not os.path.exists(REDREAM_CLI):
        return False, '', f'Redream CLI 不存在: {REDREAM_CLI}'
    try:
        result = subprocess.run(
            [REDREAM_CLI] + args,
            cwd=cwd, capture_output=True, text=True, timeout=60
        )
        return (result.returncode == 0,
                result.stdout.strip(),
                result.stderr.strip())
    except subprocess.TimeoutExpired:
        return False, '', 'CLI 调用超时（60秒）'
    except Exception as e:
        return False, '', f'CLI 调用异常: {e}'

def ensure_project(output_dir):
    """确保项目存在，不存在则创建并配置 resourcePaths"""
    os.makedirs(output_dir, exist_ok=True)
    proj_path = os.path.join(output_dir, f'{PROJECT_NAME}.redproj')

    if os.path.exists(proj_path):
        return True, proj_path, '项目已存在'

    # 1. 创建项目
    ok, out, err = run_cli([
        'modify', 'new-project',
        '--project', proj_path,
        '--resolution', '1080x2400',
    ])
    if not ok:
        return False, proj_path, f'创建项目失败: {err or out}'

    # 2. 把 Resources 目录加入资源路径（CLI 默认只加 ccb）
    ok2, out2, err2 = run_cli([
        'modify',
        '--project', proj_path,
        '--add-resource-path', 'Resources',
        'project',
    ])
    if not ok2:
        # 不致命，但警告用户
        return True, proj_path, f'{out}（警告：Resources 未加入资源路径：{err2 or out2}）'

    return True, proj_path, f'{out}; Resources 已加入资源路径'

def build_scene_via_cli(proj_path, scene_name, intermediate_red):
    """调用 build-scene 把中间 .red 转换为规范 .red"""
    scene_rel = f'Resources/{scene_name}.red'
    ok, out, err = run_cli([
        'modify', 'build-scene',
        '--project', proj_path,
        '--scene', scene_rel,
        '--config', intermediate_red,
    ])
    return ok, out, err

def inspect_check_via_cli(proj_path):
    """校验整个项目"""
    ok, out, err = run_cli([
        'inspect', 'check',
        '--project', proj_path,
    ])
    return ok, out, err

# ═══════════════════════════════════════════════════
#  其他工具
# ═══════════════════════════════════════════════════
def clean_for_json(v):
    if isinstance(v, dict):  return {k: clean_for_json(vv) for k,vv in v.items()}
    if isinstance(v, list):  return [clean_for_json(i) for i in v]
    if isinstance(v, bytes): return v.hex()
    return v

# ═══════════════════════════════════════════════════
#  Flask 路由
# ═══════════════════════════════════════════════════
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config')
def api_config():
    return jsonify({
        'output_dir': DEFAULT_OUTPUT,
        'project_name': PROJECT_NAME,
        'cli_path': REDREAM_CLI,
        'cli_exists': os.path.exists(REDREAM_CLI),
    })

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.get_json()
    logs = []
    try:
        raw     = data.get('json_text','')
        parsed  = json.loads(raw) if isinstance(raw,str) else raw
        screens = parsed.get('screens',[parsed]) if 'screens' in parsed else [parsed]
        out_dir = data.get('output_dir', DEFAULT_OUTPUT)

        # 1. 确保项目存在
        ok, proj_path, msg = ensure_project(out_dir)
        if not ok:
            return jsonify({'ok':False, 'error': msg, 'logs': logs})
        logs.append(f'📁 项目: {proj_path} ({msg})')

        results = []
        # 2. 逐个屏幕生成
        for screen in screens:
            sname = screen.get('name','未命名')
            logs.append(f'')
            logs.append(f'━━━ {sname} ━━━')

            # 2.1 Python 生成中间 .red
            try:
                red_dict = generate_red(screen)
            except Exception as e:
                logs.append(f'  ❌ 生成失败: {e}')
                results.append({'name':sname, 'ok':False, 'error':str(e)})
                continue

            # 2.2 写入临时文件
            with tempfile.NamedTemporaryFile(suffix='.red', delete=False,
                                              prefix='redtool_') as tf:
                tmp_path = tf.name
            with open(tmp_path, 'wb') as f:
                plistlib.dump(red_dict, f)
            logs.append(f'  📝 中间文件: {tmp_path}')

            # 2.3 CLI build-scene 规范化
            ok, out, err = build_scene_via_cli(proj_path, sname, tmp_path)
            if not ok:
                logs.append(f'  ❌ build-scene 失败: {err or out}')
                results.append({'name':sname, 'ok':False, 'error':err or out})
                os.unlink(tmp_path)
                continue
            logs.append(f'  ✅ {out}')

            # 清理临时文件
            os.unlink(tmp_path)

            final_path = os.path.join(out_dir, 'Resources', f'{sname}.red')
            size = os.path.getsize(final_path) if os.path.exists(final_path) else 0
            results.append({
                'name': sname,
                'ok': True,
                'path': final_path,
                'size': size,
                'cli_output': out,
            })

        # 3. 整体校验
        logs.append('')
        logs.append('━━━ 项目校验 ━━━')
        ok, out, err = inspect_check_via_cli(proj_path)
        if ok:
            logs.append(f'  ✅ {out}')
        else:
            logs.append(f'  ⚠️ 校验有问题:')
            logs.append(f'  {err or out}')

        return jsonify({
            'ok': True,
            'project': proj_path,
            'results': results,
            'logs': logs,
        })
    except Exception as e:
        import traceback
        return jsonify({'ok':False, 'error':str(e),
                        'trace':traceback.format_exc(),
                        'logs': logs})

@app.route('/api/files')
def api_files():
    base = request.args.get('dir', DEFAULT_OUTPUT)
    files = []
    try:
        if os.path.exists(base):
            for root, dirs, fnames in os.walk(base):
                dirs.sort()
                for fn in sorted(fnames):
                    if fn.endswith('.red'):
                        full = os.path.join(root, fn)
                        files.append({
                            'name': fn[:-4],
                            'path': full,
                            'rel':  os.path.relpath(full, base),
                            'size': os.path.getsize(full),
                        })
        return jsonify({'ok':True,'files':files,'base':base})
    except Exception as e:
        return jsonify({'ok':False,'error':str(e)})

@app.route('/api/load')
def api_load():
    path = request.args.get('path','')
    if not os.path.exists(path):
        return jsonify({'ok':False,'error':'文件不存在: '+path})
    try:
        with open(path,'rb') as f: data = plistlib.load(f)
        return jsonify({'ok':True,'data':clean_for_json(data),'path':path})
    except Exception as e:
        return jsonify({'ok':False,'error':str(e)})

@app.route('/api/save', methods=['POST'])
def api_save():
    payload = request.get_json()
    path = payload.get('path','')
    data = payload.get('data')
    if not path or data is None:
        return jsonify({'ok':False,'error':'缺少 path 或 data'})
    try:
        with open(path,'wb') as f: plistlib.dump(data,f)
        return jsonify({'ok':True,'size':os.path.getsize(path)})
    except Exception as e:
        import traceback
        return jsonify({'ok':False,'error':str(e),'trace':traceback.format_exc()})

@app.route('/api/open_finder', methods=['GET', 'POST'])
def api_open_finder():
    if request.method == 'POST':
        data = request.get_json() or {}
        path = data.get('path', DEFAULT_OUTPUT)
    else:
        path = request.args.get('path', DEFAULT_OUTPUT)
    path = os.path.expanduser(path)
    try:
        if os.path.isfile(path):
            # 在 Finder 中显示并选中文件
            subprocess.Popen(['open', '-R', path])
        elif os.path.isdir(path):
            subprocess.Popen(['open', path])
        else:
            # 不存在：打开父目录
            parent = os.path.dirname(path) or DEFAULT_OUTPUT
            os.makedirs(parent, exist_ok=True)
            subprocess.Popen(['open', parent])
        return jsonify({'ok':True})
    except Exception as e:
        return jsonify({'ok':False,'error':str(e)})


# ═══════════════════════════════════════════════════
#  🚀 v20.7 新增：连通性检测 + 生成 .red
# ═══════════════════════════════════════════════════
@app.route('/api/ping', methods=['GET'])
def api_ping():
    """让 Figma 插件检测 Python 服务是否在线"""
    return jsonify({
        'ok': True,
        'service': 'RED Tool',
        'version': 'v20.7',
        'cli_ready': os.path.exists(REDREAM_CLI),
    })


@app.route('/api/generate_red', methods=['POST'])
def api_generate_red():
    """接收 v20.6 schema（含 components + INSTANCE）生成 .red 文件
    
    Request body:
        {
            "output_path": "~/Desktop/red_output",
            "scene": {
                "meta": {...},
                "components": [...],  # 子 CCB 定义
                "screens": [...],     # 主屏幕
                "flow": [...]         # V1 不消费
            }
        }
    
    Response:
        {
            "ok": true/false,
            "output_dir": "/abs/path",
            "files": ["Resources/界面_xxx.red", ...],
            "log": "...",
            "error": "...",     # 仅失败时
            "stage": "..."      # 仅失败时
        }
    """
    log_lines = []
    try:
        body = request.get_json()
        if not body:
            return jsonify({'ok': False, 'stage': 'parse',
                            'error': '请求体为空或不是合法 JSON'})

        output_path = os.path.expanduser(
            body.get('output_path') or DEFAULT_OUTPUT)
        scene = body.get('scene') or {}

        screens = scene.get('screens') or []
        components = scene.get('components') or []

        if not screens:
            return jsonify({'ok': False, 'stage': 'validate',
                            'error': '未选中任何屏幕'})

        log_lines.append(f'📁 输出目录: {output_path}')
        log_lines.append(f'📊 输入: {len(screens)} 个屏幕, {len(components)} 个 Component')

        # 1. 确保项目存在
        ok, proj_path, msg = ensure_project(output_path)
        if not ok:
            return jsonify({'ok': False, 'stage': 'generate',
                            'error': f'项目初始化失败: {msg}',
                            'log': '\n'.join(log_lines)})
        log_lines.append(f'✅ 项目: {msg}')

        generated_files = []

        # 2. 子 CCB 生成（V1 占位实现：components 数组先标记为 TODO，不真生成）
        if components:
            log_lines.append('')
            log_lines.append(f'⚠️  components 数组检测到 {len(components)} 个 Component')
            log_lines.append('⚠️  V1 阶段子 CCB 生成功能开发中，将忽略 components 数组')
            log_lines.append('⚠️  主屏内 INSTANCE 节点将作为空 CCNode 占位生成')
            for c in components:
                log_lines.append(f'   - {c.get("name", "unknown")} (跳过)')

        # 3. 逐个屏幕生成
        for screen in screens:
            sname = screen.get('name', '未命名')
            log_lines.append('')
            log_lines.append(f'━━━ {sname} ━━━')

            # 3.1 Python 生成中间 .red
            try:
                red_dict = generate_red(screen)
            except Exception as e:
                log_lines.append(f'  ❌ 中间 .red 生成失败: {e}')
                return jsonify({'ok': False, 'stage': 'generate',
                                'error': f'{sname}: {str(e)}',
                                'log': '\n'.join(log_lines)})

            # 3.2 写入临时文件
            with tempfile.NamedTemporaryFile(suffix='.red', delete=False,
                                              prefix='redtool_v207_') as tf:
                tmp_path = tf.name
            with open(tmp_path, 'wb') as f:
                plistlib.dump(red_dict, f)
            log_lines.append(f'  📝 中间文件已生成')

            # 3.3 CLI build-scene 规范化
            ok, out, err = build_scene_via_cli(proj_path, sname, tmp_path)
            os.unlink(tmp_path)
            if not ok:
                log_lines.append(f'  ❌ build-scene 失败: {err or out}')
                return jsonify({'ok': False, 'stage': 'build_scene',
                                'error': f'{sname}: {err or out}',
                                'log': '\n'.join(log_lines)})
            log_lines.append(f'  ✅ build-scene OK')

            generated_files.append(f'Resources/{sname}.red')

        # 4. 整体校验
        log_lines.append('')
        log_lines.append('━━━ inspect check ━━━')
        ok, out, err = inspect_check_via_cli(proj_path)
        if ok:
            log_lines.append(f'  ✅ {out}')
        else:
            log_lines.append(f'  ⚠️  校验有问题: {err or out}')
            return jsonify({'ok': False, 'stage': 'inspect_check',
                            'error': err or out,
                            'log': '\n'.join(log_lines),
                            'files': generated_files,
                            'output_dir': output_path})

        return jsonify({
            'ok': True,
            'output_dir': output_path,
            'files': generated_files,
            'log': '\n'.join(log_lines),
        })

    except Exception as e:
        import traceback
        return jsonify({
            'ok': False,
            'stage': 'generate',
            'error': str(e),
            'trace': traceback.format_exc(),
            'log': '\n'.join(log_lines),
        })


# ═══════════════════════════════════════════════════
if __name__ == '__main__':
    print('='*60)
    print('  🔴 RED Tool v20.7 启动（CLI 驱动 + Figma 插件接口）')
    print(f'  浏览器打开: http://localhost:5001')
    print(f'  输出目录:   {DEFAULT_OUTPUT}')
    print(f'  项目名:     {PROJECT_NAME}.redproj')
    print(f'  Redream CLI: {REDREAM_CLI}')
    print(f'  CLI 就绪:   {"✅" if os.path.exists(REDREAM_CLI) else "❌ 未找到"}')
    print('-'*60)
    print('  Figma 插件接口:')
    print('    GET  /api/ping             连通性检测')
    print('    POST /api/generate_red     生成 .red（v20.6 schema）')
    print('    POST /api/open_finder      在 Finder 中打开路径')
    print('='*60)
    app.run(debug=False, port=5001, host='127.0.0.1')
