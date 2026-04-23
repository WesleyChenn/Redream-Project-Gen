#!/usr/bin/env python3
"""
figma_auto_export.py — Figma → Redream 自动化出图 + 建节点树

功能：
1. 解析 Figma 节点树 JSON，按命名规范分类
2. 坐标转换（Figma 左上角原点 → Redream 百分比定位 [x%, y%, 0, 2, 2]）
3. 生成 Redream CLI 命令（add-node / set-property / batch）
4. 生成图片导出计划

用法（由 Claude 调用）：
    # 分析模式：分析 Figma 节点并生成计划
    python3 figma_auto_export.py analyze --input nodes.json --parent-size 1080x2400

    # 生成模式：生成 Redream CLI 命令
    python3 figma_auto_export.py generate --input nodes.json \\
        --scene ccb/FP_弹窗_开启通知.red \\
        --project /path/to/project.redproj \\
        --project-prefix FP --module-name 开启通知 \\
        --parent-size 1080x2400

    # 图片导出模式：生成图片导出 URL 列表
    python3 figma_auto_export.py export-images --input nodes.json \\
        --file-key QGnttK1FTJfNi6CpwBEGTa \\
        --project-prefix FP --module-name 开启通知
"""

import argparse
import json
import sys
import os
import re
import subprocess
import shutil
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from typing import Optional


# ============================================================
# 命名规范 → Redream 节点类型映射
# ============================================================

# 前缀 → (Redream 节点类型, 是否需要导出图片, 描述)
PREFIX_MAP = {
    "按钮_":     ("REDNodeButton", False, "可点击按钮"),
    "底板_":     ("CCScale9Sprite", True, "底板/九宫格"),
    "文字_":     ("CCRedLabel", False, "文本标签"),
    "图片_":     ("CCSprite", True, "插图/装饰图"),
    "图标_":     ("CCSprite", True, "功能图标"),
    "插图_":     ("CCSprite", True, "场景/人物插图"),
    "面板_":     ("CCNode", False, "容器/区域"),
    "遮罩_":     ("CCLayerColor", False, "半透明遮罩"),
    "弹窗_":     ("CCNode", False, "弹窗容器"),
    "按钮基底_": ("CCSprite", True, "按钮底座贴图"),
    "按钮内容_": ("CCSprite", True, "按钮内容图标"),
    "按钮角标_": ("CCSprite", True, "按钮角标"),
    "底板组_":   ("CCNode", False, "底板合组容器"),
    "底板Frame_": ("CCSprite", True, "底板Frame整图导出"),
    "内容_":     ("CCNode", False, "内容居中容器"),
    "进度条_":   ("CCProgressTimer", True, "进度条"),
    "背景图_":   ("CCSprite", True, "全屏背景图"),
    "特效_":     ("CCSprite", True, "视觉特效"),
    "效果图_":   ("CCSprite", True, "效果覆盖图"),
    "标签_":     ("CCSprite", True, "角标/徽章"),
    "序列_":     ("CCSprite", True, "帧动画序列"),
    "列表_":     ("CCNode", False, "列表容器"),
    "列表项_":   ("CCNode", False, "列表单元格"),
    "道具_":     ("CCNode", False, "道具展示组"),
    "开关_":     ("CCNode", False, "Toggle 控件"),
    "滑块_":     ("CCNode", False, "Slider 控件"),
    "界面_":     ("CCNode", False, "主功能界面"),
    "浮层_":     ("CCNode", False, "浮层/气泡"),
}

# 弹窗/界面/浮层等关键词 → 根节点为 CCLayer
CCLAYER_KEYWORDS = ["弹窗", "浮层", "全屏反馈", "界面"]


# ============================================================
# 场景类型检测与标准骨架定义
# ============================================================

def detect_scene_type(root_name: str, scene_name: str = "") -> Optional[str]:
    """
    检测场景类型，返回 "弹窗" | "界面" | "浮层" | None

    优先匹配更具体的关键词。
    """
    combined = root_name + " " + scene_name
    # 按优先级排序：弹窗 > 浮层 > 全屏反馈 > 界面
    for scene_type in ["弹窗", "浮层", "全屏反馈", "界面"]:
        if scene_type in combined:
            return scene_type
    return None


def _is_mask_node(node: 'FigmaNode') -> bool:
    """判断是否是遮罩节点（全屏遮罩/半透明遮罩）"""
    name = node.name
    # 匹配 "遮罩_xxx" 或 "全屏遮罩" 或 "xxx遮罩"
    return name.startswith("遮罩_") or "遮罩" in name


def find_popup_inner_frame(root_node: 'FigmaNode') -> Optional['FigmaNode']:
    """
    从弹窗根节点找到内部弹窗容器。

    弹窗 Figma 结构通常为：
        弹窗_xxx (root, 1080x2400)
        ├─ 全屏遮罩 (RECTANGLE) ← 跳过
        └─ 弹窗_xxx (内部容器, 更小尺寸) ← 返回这个

    优先返回有子节点的非遮罩容器。
    """
    candidates = []
    for child in root_node.children:
        if _is_mask_node(child):
            continue
        candidates.append(child)

    if not candidates:
        return None

    # 优先选择有子节点的容器（实际弹窗内容）
    with_children = [c for c in candidates if c.children]
    if with_children:
        return max(with_children, key=lambda n: n.width * n.height)

    return max(candidates, key=lambda n: n.width * n.height)


def find_mask_node(root_node: 'FigmaNode') -> Optional['FigmaNode']:
    """找到弹窗的遮罩节点，用于提取遮罩透明度"""
    for child in root_node.children:
        if _is_mask_node(child):
            return child
    return None


def classify_popup_child(node: 'FigmaNode') -> str:
    """
    分类弹窗内容节点到对应骨架槽位。

    返回槽位名称：
      "弹窗底板" — 底板组或主底板
      "标题栏"   — 标题文本、标题底板、关闭按钮
      "内容区域" — 面板类容器
      "按钮组"   — 操作按钮（非关闭）
      "弹窗总组" — 默认，直接放入弹窗总组
    """
    name = node.name

    # 底板组（含弹窗底板结构）→ 弹窗底板
    if name.startswith("底板组_"):
        return "弹窗底板"

    # 底板Frame（整图导出的弹窗底板）→ 弹窗底板
    if name.startswith("底板Frame_") and "弹窗" in name:
        return "弹窗底板"

    # 主底板（弹窗底板，非阴影）→ 弹窗底板
    # 注意：底板组的子节点不会到这里，因为它们是底板组的 children
    if name.startswith("底板_") and "弹窗" in name and "底板" in name and "阴影" not in name:
        return "弹窗底板"

    # 标题相关 → 标题栏
    if name.startswith("文字_") and ("标题" in name or "弹窗标题" in name):
        return "标题栏"
    if name.startswith("底板_") and "标题" in name:
        return "标题栏"

    # 关闭按钮 → 标题栏
    if name.startswith("按钮_") and "关闭" in name:
        return "标题栏"

    # 面板 → 内容区域
    if name.startswith("面板_"):
        return "内容区域"

    # 操作按钮（非关闭）→ 按钮组
    if name.startswith("按钮_") and "关闭" not in name:
        return "按钮组"

    # 其他 → 弹窗总组
    return "弹窗总组"


# 弹窗标准骨架节点定义
# 每项：(parent_path, node_type, node_name, properties_dict)
# properties_dict 的 key=属性名, value=CLI 格式值
#
# position 格式：[x, y, posType, xRef, yRef]  posType: 始终为 0; xRef/yRef: 0=绝对, 2=百分比
# contentSize 格式：[w, h, wUnit, hUnit]  unit: 0=绝对点值, 2=百分比
POPUP_SKELETON = [
    # CCLayer 根节点（锚点 0,0，不勾选忽略锚点）
    ("CCLayer", None, None, {
        "contentSize": "100,100,2,2",
        "anchorPoint": "0,0",
        "ignoreAnchorPointForPosition": "false",
    }),
    # 总组：50%/50% 居中，100%/100% 全屏，初始隐藏
    ("CCLayer", "CCNode", "总组", {
        "position": "50,50,0,2,2",
        "contentSize": "100,100,2,2",
        "anchorPoint": "0.5,0.5",
        "visible": "false",
    }),
    # 全屏防穿透按钮
    ("CCLayer/总组", "REDNodeButton", "全屏防穿透按钮", {
        "position": "50,50,0,2,2",
        "contentSize": "100,100,2,2",
        "preferedSize": "100,100,2,2",
        "anchorPoint": "0.5,0.5",
        "opacity": "0",
        "zoomOnTouchDown": "false",
        "swallowTouches": "true",
    }),
    # 黑色遮罩（居中定位，ignoreAnchor=false，opacity 由 Figma 遮罩节点提取）
    ("CCLayer/总组", "CCLayerColor", "黑色遮罩", {
        "position": "50,50,0,2,2",
        "contentSize": "100,100,2,2",
        "ignoreAnchorPointForPosition": "false",
        "color": "0,0,0",
        "opacity": "204",  # 占位，会被实际值覆盖
    }),
    # 安全区域（RedSafeAreaLayer 内部自动处理位置，保持默认值不动）
    ("CCLayer/总组", "RedSafeAreaLayer", "安全区域", {}),
    # 弹窗总组（位置和尺寸由 Figma 内部弹窗容器决定）
    ("CCLayer/总组/安全区域", "CCNode", "弹窗总组", {
        "position": "50,50,0,2,2",
        "anchorPoint": "0.5,0.5",
    }),
]

# 弹窗总组内的标准容器节点
POPUP_CONTENT_CONTAINERS = [
    # (parent_path_suffix, node_type, node_name)
    # 只在有对应内容时才创建
    ("标题栏", "CCNode", "标题栏"),
    ("内容区域", "CCNode", "内容区域"),
    ("按钮组", "CCNode", "按钮组"),
]

# 界面标准骨架
INTERFACE_SKELETON = [
    # 背景组
    ("CCLayer", "CCNode", "背景组", {}),
    ("CCLayer/背景组", "REDNodeButton", "全屏点击屏蔽", {
        "position": "50,50,2,2,0",
        "contentSize": "100,100,2,2",
        "preferedSize": "100,100,2,2",
    }),
    # 安全区域
    ("CCLayer", "RedSafeAreaLayer", "安全区域", {}),
    # 总组
    ("CCLayer/安全区域", "CCNode", "总组", {
        "position": "50,50,2,2,0",
        "contentSize": "100,100,2,2",
    }),
    # 定位点
    ("CCLayer", "CCNode", "banner定位点", {}),
    ("CCLayer", "CCNode", "弹窗层定位点", {}),
]

# 浮层标准骨架
OVERLAY_SKELETON = [
    # 背景组
    ("CCLayer", "CCNode", "背景组", {}),
    ("CCLayer/背景组", "REDNodeButton", "全屏点击层", {
        "position": "50,50,2,2,0",
        "contentSize": "100,100,2,2",
        "preferedSize": "100,100,2,2",
    }),
    # 总组
    ("CCLayer", "CCNode", "总组", {
        "position": "50,50,2,2,0",
        "contentSize": "100,100,2,2",
    }),
    # 底部按钮组
    ("CCLayer", "CCNode", "底部按钮组", {}),
]


@dataclass
class FigmaNode:
    """解析后的 Figma 节点"""
    id: str
    name: str
    node_type: str  # Figma 类型: FRAME, RECTANGLE, TEXT, GROUP, etc.
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    # 样式
    fill_color: Optional[str] = None  # hex
    fill_r: int = 255
    fill_g: int = 255
    fill_b: int = 255
    opacity: float = 1.0
    visible: bool = True
    corner_radius: float = 0.0
    # 文本属性
    text_content: Optional[str] = None
    font_size: Optional[float] = None
    font_weight: Optional[str] = None
    text_color: Optional[str] = None
    # 约束
    h_constraint: str = "LEFT"  # LEFT, CENTER, RIGHT, SCALE
    v_constraint: str = "TOP"   # TOP, CENTER, BOTTOM, SCALE
    # 图片填充
    has_image_fill: bool = False
    image_ref: Optional[str] = None
    # 分析结果
    prefix: str = ""
    semantic_name: str = ""
    redream_type: str = "CCNode"
    needs_export: bool = False
    # 层级
    parent_id: Optional[str] = None
    children: list = field(default_factory=list)
    depth: int = 0


@dataclass
class RedreamCommand:
    """一条 Redream CLI 命令"""
    cmd_type: str  # add-node, set-property, batch
    args: dict = field(default_factory=dict)
    description: str = ""


# ============================================================
# 1. Figma 节点解析
# ============================================================

def parse_figma_node(node_data: dict, parent_id: str = None, depth: int = 0,
                     parent_abs_x: float = 0, parent_abs_y: float = 0) -> FigmaNode:
    """递归解析 Figma REST API 返回的节点数据

    Figma API 只返回 absoluteBoundingBox（绝对页面坐标），
    需要减去父节点绝对坐标得到相对于父级的位置。
    """
    n = FigmaNode(
        id=node_data.get("id", ""),
        name=node_data.get("name", ""),
        node_type=node_data.get("type", ""),
        parent_id=parent_id,
        depth=depth,
    )

    # 位置和尺寸（绝对坐标）
    bbox = node_data.get("absoluteBoundingBox") or node_data.get("absoluteRenderBounds")
    abs_x, abs_y = 0.0, 0.0
    if bbox:
        abs_x = bbox.get("x", 0)
        abs_y = bbox.get("y", 0)
        n.width = bbox.get("width", 0)
        n.height = bbox.get("height", 0)

    # 转为相对于父级的坐标
    n.x = abs_x - parent_abs_x
    n.y = abs_y - parent_abs_y

    # 尺寸（从 size 字段获取，更准确）
    size = node_data.get("size")
    if size:
        n.width = size.get("x", n.width)
        n.height = size.get("y", n.height)

    # 可见性
    n.visible = node_data.get("visible", True)

    # 透明度
    n.opacity = node_data.get("opacity", 1.0)

    # 圆角
    n.corner_radius = node_data.get("cornerRadius", 0)

    # 填充颜色
    fills = node_data.get("fills", [])
    for fill in fills:
        if fill.get("visible", True) is False:
            continue
        if fill.get("type") == "SOLID":
            color = fill.get("color", {})
            n.fill_r = int(color.get("r", 1) * 255)
            n.fill_g = int(color.get("g", 1) * 255)
            n.fill_b = int(color.get("b", 1) * 255)
            n.fill_color = f"#{n.fill_r:02x}{n.fill_g:02x}{n.fill_b:02x}"
            if "opacity" in fill:
                n.opacity *= fill["opacity"]
        elif fill.get("type") == "IMAGE":
            n.has_image_fill = True
            n.image_ref = fill.get("imageRef")

    # 文本属性
    if n.node_type == "TEXT":
        n.text_content = node_data.get("characters", "")
        style = node_data.get("style", {})
        n.font_size = style.get("fontSize")
        n.font_weight = style.get("fontWeight")
        text_fills = node_data.get("fills", [])
        for f in text_fills:
            if f.get("type") == "SOLID" and f.get("visible", True):
                c = f.get("color", {})
                r, g, b = int(c.get("r", 1)*255), int(c.get("g", 1)*255), int(c.get("b", 1)*255)
                n.text_color = f"#{r:02x}{g:02x}{b:02x}"

    # 约束
    constraints = node_data.get("constraints", {})
    n.h_constraint = constraints.get("horizontal", "LEFT")
    n.v_constraint = constraints.get("vertical", "TOP")

    # 递归处理子节点（传入当前节点绝对坐标作为子节点的父坐标参考）
    children_data = node_data.get("children", [])
    for child_data in children_data:
        child = parse_figma_node(child_data, parent_id=n.id, depth=depth + 1,
                                 parent_abs_x=abs_x, parent_abs_y=abs_y)
        n.children.append(child)

    return n


def parse_figma_metadata_xml(xml_text: str) -> dict:
    """解析 MCP get_metadata 返回的 XML 格式元数据，提取节点 ID 和名称"""
    nodes = {}
    # 简单正则提取 <node> 标签的属性
    pattern = r'<(\w+)\s+([^>]+)/?>'
    for match in re.finditer(pattern, xml_text):
        tag = match.group(1)
        attrs_str = match.group(2)
        attrs = {}
        for attr_match in re.finditer(r'(\w+)="([^"]*)"', attrs_str):
            attrs[attr_match.group(1)] = attr_match.group(2)
        if "id" in attrs and "name" in attrs:
            nodes[attrs["id"]] = {
                "id": attrs["id"],
                "name": attrs["name"],
                "type": tag,
                "x": float(attrs.get("x", 0)),
                "y": float(attrs.get("y", 0)),
                "width": float(attrs.get("width", 0)),
                "height": float(attrs.get("height", 0)),
            }
    return nodes


# ============================================================
# 2. 节点分类（按命名规范）
# ============================================================

def classify_node(node: FigmaNode) -> FigmaNode:
    """根据命名前缀分类节点，确定 Redream 类型和是否需要导出"""
    name = node.name

    # 匹配前缀
    matched = False
    for prefix, (redream_type, needs_export, _desc) in PREFIX_MAP.items():
        if name.startswith(prefix):
            node.prefix = prefix.rstrip("_")
            node.semantic_name = name[len(prefix):]
            node.redream_type = redream_type
            node.needs_export = needs_export
            matched = True
            break

    if not matched:
        # 无前缀的节点：
        # - TEXT 类型 → CCRedLabel
        # - 有图片填充 → CCSprite
        # - 其他 → CCNode
        if node.node_type == "TEXT":
            node.redream_type = "CCRedLabel"
            node.needs_export = False
        elif node.has_image_fill:
            node.redream_type = "CCSprite"
            node.needs_export = True
        else:
            node.redream_type = "CCNode"
            node.needs_export = False
        node.prefix = ""
        node.semantic_name = name

    # 特殊判断：底板可能是普通 Sprite 而非九宫格
    # 如果尺寸较小且无圆角，用 CCSprite
    if node.redream_type == "CCScale9Sprite":
        if node.corner_radius == 0 and node.width < 100 and node.height < 100:
            node.redream_type = "CCSprite"

    # 按钮节点：检查子节点结构
    if node.redream_type == "REDNodeButton":
        # REDNodeButton 本身是容器，内部子节点需要分别处理
        pass

    # 如果节点本身需要导出图片且有子节点（FRAME 类型），
    # 以 Frame 为单位导出整张图，不递归处理子节点
    if node.needs_export and node.children:
        node.children = []  # 清空子节点，整个 Frame 作为一张图导出
        return node

    # 递归分类子节点
    for child in node.children:
        classify_node(child)

    return node


def collect_export_nodes(node: FigmaNode, result: list = None) -> list:
    """收集所有需要导出图片的节点"""
    if result is None:
        result = []

    if node.needs_export and node not in result:
        result.append(node)

    # 对于按钮，导出子节点中的图片元素
    if node.redream_type == "REDNodeButton":
        for child in node.children:
            if child.has_image_fill or child.needs_export:
                if child not in result:
                    result.append(child)
            collect_export_nodes(child, result)
    else:
        for child in node.children:
            collect_export_nodes(child, result)

    return result


def collect_all_nodes(node: FigmaNode, result: list = None) -> list:
    """平铺收集所有节点"""
    if result is None:
        result = []
    result.append(node)
    for child in node.children:
        collect_all_nodes(child, result)
    return result


# ============================================================
# 3. 坐标转换
# ============================================================

def convert_position(
    figma_x: float, figma_y: float,
    node_width: float, node_height: float,
    anchor_x: float = 0.5, anchor_y: float = 0.5,
    parent_width: float = 0, parent_height: float = 0,
    h_constraint: str = "LEFT", v_constraint: str = "TOP",
    use_percent: bool = False
) -> dict:
    """
    Figma 坐标 → Redream Position 值

    标准格式：[x%, y%, 0, 2, 2]（百分比相对父级）
    - posType: 始终为 0
    - xRef/yRef: 2=百分比（相对父级）

    转换公式（Figma 左上角原点 → Redream 左下角原点）：
        x% = (figma_x + node_width * anchorX) / parent_width * 100
        y% = (figma_y + node_height * (1 - anchorY)) / parent_height * 100

    注意：Figma Y 轴向下，Redream Y 轴向上（左下角原点），
    但使用百分比时 y% 从底部计算，所以需要翻转：
        y% = (1 - (figma_y + node_height * (1 - anchorY)) / parent_height) * 100

    返回：
        {
            "value": [x_pct, y_pct, 0, 2, 2],
            "position_str": "x_pct,y_pct,0,2,2"  # CLI 格式
        }
    """
    result = {}

    if parent_width > 0 and parent_height > 0:
        # 百分比定位（相对于父容器，标准格式）
        x_pct = (figma_x + node_width * anchor_x) / parent_width * 100
        # Y 轴翻转：Figma 从上到下，Redream 从下到上
        y_pct = (1 - (figma_y + node_height * (1 - anchor_y)) / parent_height) * 100

        result["value"] = [round(x_pct, 1), round(y_pct, 1), 0, 2, 2]
        result["position_str"] = f"{round(x_pct, 1)},{round(y_pct, 1)},0,2,2"
    else:
        # 回退：父级尺寸未知时使用绝对坐标
        x_val = figma_x + node_width * anchor_x
        y_val = figma_y + node_height * (1 - anchor_y)
        result["value"] = [round(x_val, 1), round(y_val, 1), 0, 0, 0]
        result["position_str"] = f"{round(x_val, 1)},{round(y_val, 1)},0,0,0"

    return result


def convert_size(width: float, height: float, w_unit: int = 0, h_unit: int = 0) -> dict:
    """
    生成 Redream contentSize 值

    返回 CLI 格式字符串
    """
    return {
        "value": [round(width, 1), round(height, 1), w_unit, h_unit],
        "size_str": f"{round(width, 1)},{round(height, 1)},{w_unit},{h_unit}"
    }


def convert_color(r: int, g: int, b: int) -> str:
    """生成 CLI Color3 格式"""
    return f"{r},{g},{b}"


def convert_opacity(opacity: float) -> int:
    """Figma opacity (0-1) → Redream Byte (0-255)"""
    return max(0, min(255, int(opacity * 255)))


# ============================================================
# 4. CLI 命令生成
# ============================================================

def generate_image_name(node: FigmaNode, project_prefix: str, module_name: str) -> str:
    """
    按命名规范生成图片文件名

    格式：[项目前缀]_[模块名]_[类型前缀]_[语义描述].png
    """
    prefix = node.prefix if node.prefix else "图片"
    # 底板Frame_ 前缀导出时命名为 底板_（去掉 Frame）
    prefix = prefix.replace("Frame", "")
    semantic = node.semantic_name if node.semantic_name else node.name

    # 清理名称中的特殊字符
    semantic = re.sub(r'[/\\:*?"<>|]', '_', semantic)

    return f"{project_prefix}_{module_name}_{prefix}_{semantic}.png"


def generate_image_ref(node: FigmaNode, project_prefix: str, module_name: str, atlas_name: str = None) -> str:
    """
    生成 spriteFrame/displayFrame 引用值

    格式：{plist名}.plist,{帧名}.png
    plist名 = 图集文件夹名（即 {项目前缀}_{模块名}）
    帧名 = 图片文件名（与 image/ 下的 png 文件名一致）
    """
    plist_name = atlas_name or f"{project_prefix}_{module_name}"
    frame_name = generate_image_name(node, project_prefix, module_name)
    return f"{plist_name}.plist,{frame_name}"


def build_node_path(node: FigmaNode, nodes_map: dict, root_type: str = "CCNode") -> str:
    """
    构建节点在 Redream 场景中的路径

    格式：CCNode/面板_xxx/子节点名
    """
    path_parts = []
    current = node
    while current:
        path_parts.insert(0, current.name)
        if current.parent_id and current.parent_id in nodes_map:
            current = nodes_map[current.parent_id]
        else:
            break

    # 根节点
    if path_parts:
        path_parts[0] = root_type

    return "/".join(path_parts)


def generate_add_node_cmd(
    scene: str, parent_path: str, node_type: str, name: str,
    project: str, redream_bin: str
) -> str:
    """生成 add-node CLI 命令"""
    return (
        f'{redream_bin} modify add-node '
        f'--scene {scene} '
        f'--parent "{parent_path}" '
        f'--type {node_type} '
        f'--name "{name}" '
        f'-p {project}'
    )


def generate_set_property_cmd(
    scene: str, node_path: str, prop_name: str, value: str,
    project: str, redream_bin: str
) -> str:
    """生成 set-property CLI 命令"""
    return (
        f'{redream_bin} modify set-property '
        f'--scene {scene} '
        f'--node "{node_path}" '
        f'--property {prop_name} '
        f'--value "{value}" '
        f'-p {project}'
    )


def generate_commands_for_node(
    node: FigmaNode,
    parent_path: str,
    scene: str,
    project: str,
    redream_bin: str,
    project_prefix: str,
    module_name: str,
    parent_width: float,
    parent_height: float,
    plist_path: str = "",
    atlas_name: str = "",
) -> list:
    """
    为一个节点生成所有需要的 CLI 命令

    返回命令字符串列表
    """
    commands = []
    node_name = node.name
    node_type = node.redream_type
    node_path = f"{parent_path}/{node_name}"

    # 1. 添加节点
    commands.append({
        "cmd": generate_add_node_cmd(scene, parent_path, node_type, node_name, project, redream_bin),
        "desc": f"添加 {node_type} 节点: {node_name}"
    })

    # 2. 设置位置
    pos = convert_position(
        node.x, node.y,
        node.width, node.height,
        anchor_x=0.5, anchor_y=0.5,
        parent_width=parent_width,
        parent_height=parent_height,
        h_constraint=node.h_constraint,
        v_constraint=node.v_constraint
    )
    commands.append({
        "cmd": generate_set_property_cmd(scene, node_path, "position", pos["position_str"], project, redream_bin),
        "desc": f"设置位置: {pos['position_str']}"
    })

    # 2.5. 设置锚点（标准默认 0.5,0.5，所有内容节点统一设置）
    if node_type in ("CCScale9Sprite", "CCNode", "CCSprite", "CCRedLabel", "REDNodeButton"):
        commands.append({
            "cmd": generate_set_property_cmd(scene, node_path, "anchorPoint", "0.5,0.5", project, redream_bin),
            "desc": f"设置锚点: 0.5,0.5"
        })

    # 3. 设置尺寸
    size = convert_size(node.width, node.height)
    if node_type in ("CCNode", "CCLayerColor", "REDNodeButton", "CCLayer"):
        commands.append({
            "cmd": generate_set_property_cmd(scene, node_path, "contentSize", size["size_str"], project, redream_bin),
            "desc": f"设置尺寸: {size['size_str']}"
        })
    elif node_type == "CCScale9Sprite":
        commands.append({
            "cmd": generate_set_property_cmd(scene, node_path, "preferedSize", size["size_str"], project, redream_bin),
            "desc": f"设置九宫格尺寸: {size['size_str']}"
        })

    # 4. 设置图片引用（如果有）
    if node.needs_export and node_type in ("CCSprite", "CCScale9Sprite", "CCProgressTimer"):
        if plist_path:
            # 手动指定 plist 路径
            img_name = generate_image_name(node, project_prefix, module_name)
            frame_value = f"{plist_path},{img_name}"
        else:
            # 自动生成引用：plist名.plist,帧名.png
            frame_value = generate_image_ref(node, project_prefix, module_name, atlas_name)

        prop_name = "displayFrame" if node_type != "CCScale9Sprite" else "spriteFrame"
        commands.append({
            "cmd": generate_set_property_cmd(scene, node_path, prop_name, frame_value, project, redream_bin),
            "desc": f"设置图片: {frame_value}"
        })

    # 5. 设置颜色（CCLayerColor / CCRedLabel）
    if node_type == "CCLayerColor" and node.fill_color:
        commands.append({
            "cmd": generate_set_property_cmd(scene, node_path, "color", convert_color(node.fill_r, node.fill_g, node.fill_b), project, redream_bin),
            "desc": f"设置颜色: {node.fill_color}"
        })

    # 6. 设置透明度
    if node.opacity < 1.0:
        opacity_val = convert_opacity(node.opacity)
        commands.append({
            "cmd": generate_set_property_cmd(scene, node_path, "opacity", str(opacity_val), project, redream_bin),
            "desc": f"设置透明度: {opacity_val}"
        })

    # 7. 设置可见性
    if not node.visible:
        commands.append({
            "cmd": generate_set_property_cmd(scene, node_path, "visible", "false", project, redream_bin),
            "desc": "设置不可见"
        })

    # 8. 文本属性
    if node_type == "CCRedLabel" and node.text_content:
        commands.append({
            "cmd": generate_set_property_cmd(scene, node_path, "string", node.text_content, project, redream_bin),
            "desc": f"设置文本: {node.text_content}"
        })
        if node.text_color:
            r, g, b = int(node.text_color[1:3], 16), int(node.text_color[3:5], 16), int(node.text_color[5:7], 16)
            commands.append({
                "cmd": generate_set_property_cmd(scene, node_path, "frontColor", convert_color(r, g, b), project, redream_bin),
                "desc": f"设置文本颜色: {node.text_color}"
            })

    # 9. 按钮特殊属性
    if node_type == "REDNodeButton":
        commands.append({
            "cmd": generate_set_property_cmd(scene, node_path, "preferedSize", size["size_str"], project, redream_bin),
            "desc": f"设置按钮尺寸: {size['size_str']}"
        })

    return commands


def generate_skeleton_commands(
    skeleton_def: list,
    scene: str,
    project: str,
    redream_bin: str,
    overrides: dict = None,
) -> list:
    """
    根据骨架定义生成标准骨架节点的 CLI 命令。

    skeleton_def: [(parent_path, node_type, node_name, properties), ...]
    overrides: {node_name: {prop: value}} 用于覆盖默认属性（如遮罩透明度）
    """
    if overrides is None:
        overrides = {}

    commands = []
    for parent_path, node_type, node_name, props in skeleton_def:
        # 特殊项：node_type=None 表示设置已有根节点的属性（不添加新节点）
        if node_type is None and node_name is None:
            node_path = parent_path
            display_name = parent_path
        else:
            node_path = f"{parent_path}/{node_name}"
            display_name = node_name

            # 添加节点
            commands.append({
                "cmd": generate_add_node_cmd(scene, parent_path, node_type, node_name, project, redream_bin),
                "desc": f"[骨架] 添加 {node_type}: {node_name}"
            })

        # 合并属性（overrides 优先）
        merged_props = dict(props)
        if node_name and node_name in overrides:
            merged_props.update(overrides[node_name])

        # 设置属性
        for prop_name, prop_value in merged_props.items():
            commands.append({
                "cmd": generate_set_property_cmd(scene, node_path, prop_name, prop_value, project, redream_bin),
                "desc": f"[骨架] {display_name}.{prop_name} = {prop_value}"
            })

    return commands


def generate_popup_commands(
    root_node: FigmaNode,
    scene: str,
    project: str,
    redream_bin: str,
    project_prefix: str,
    module_name: str,
    plist_path: str = "",
    atlas_name: str = "",
) -> list:
    """
    生成弹窗场景的完整命令：标准骨架 + Figma 内容映射。

    弹窗标准结构：
      CCLayer
      ├─ 总组 (CCNode, visible=false, 50%/50%, 100%/100%)
      │   ├─ 全屏防穿透按钮 (REDNodeButton)
      │   ├─ 黑色遮罩 (CCLayerColor, opacity=170~204)
      │   └─ 安全区域 (RedSafeAreaLayer)
      │       └─ 弹窗总组 (CCNode)
      │           ├─ [底板组/弹窗底板]  ← Figma 底板组映射
      │           ├─ 标题栏 (CCNode)    ← Figma 标题/关闭按钮映射
      │           ├─ 内容区域 (CCNode)  ← Figma 面板映射
      │           └─ 按钮组 (CCNode)    ← Figma 操作按钮映射
      └─ 浮层定位层 (CCNode)
    """
    all_commands = []

    # --- 1. 从 Figma 提取信息 ---
    mask_node = find_mask_node(root_node)
    inner_frame = find_popup_inner_frame(root_node)

    if inner_frame is None:
        # 没有找到内部弹窗容器，回退到平铺模式
        return _generate_flat_commands(
            root_node, scene, project, redream_bin,
            project_prefix, module_name, plist_path, atlas_name
        )

    # 提取遮罩透明度
    mask_opacity = "204"  # 默认 80%
    if mask_node and mask_node.opacity < 1.0:
        mask_opacity = str(convert_opacity(mask_node.opacity))

    # --- 2. 生成标准骨架 ---
    skeleton_overrides = {
        "黑色遮罩": {"opacity": mask_opacity},
    }
    all_commands.extend(
        generate_skeleton_commands(POPUP_SKELETON, scene, project, redream_bin, skeleton_overrides)
    )

    # --- 3. 设置弹窗总组的位置和尺寸（来自 Figma 内部容器） ---
    popup_root_path = "CCLayer/总组/安全区域/弹窗总组"

    # 弹窗总组居中于安全区域（百分比定位，标准格式 [x%, y%, 0, 2, 2]）
    inner_center_x = (inner_frame.x + inner_frame.width * 0.5) / root_node.width * 100
    # Y 轴翻转：Figma 从上到下，Redream 从下到上
    inner_center_y = (1 - (inner_frame.y + inner_frame.height * 0.5) / root_node.height) * 100
    popup_pos = f"{round(inner_center_x, 1)},{round(inner_center_y, 1)},0,2,2"
    popup_size = convert_size(inner_frame.width, inner_frame.height)

    all_commands.append({
        "cmd": generate_set_property_cmd(scene, popup_root_path, "position", popup_pos, project, redream_bin),
        "desc": f"[骨架] 弹窗总组.position = {popup_pos}"
    })
    all_commands.append({
        "cmd": generate_set_property_cmd(scene, popup_root_path, "contentSize", popup_size["size_str"], project, redream_bin),
        "desc": f"[骨架] 弹窗总组.contentSize = {popup_size['size_str']}"
    })

    # --- 4. 分类 Figma 内容节点到骨架槽位 ---
    slots = {
        "弹窗底板": [],
        "标题栏": [],
        "内容区域": [],
        "按钮组": [],
        "弹窗总组": [],
    }

    for child in inner_frame.children:
        slot = classify_popup_child(child)
        slots[slot].append(child)

    # --- 5. 按 Figma 顺序（back-to-front）添加节点到弹窗总组 ---
    # Figma JSON children 顺序 = back-to-front（第一个=最底层）
    # Redream children 顺序也是 first=back, last=front
    # 所以直接按 Figma 顺序：弹窗底板（最底层）→ 标题栏 → 内容区域 → 按钮组（最顶层）

    # 5a. 先添加弹窗底板（最底层背景）
    for slot_name in ["弹窗底板", "弹窗总组"]:
        for node in slots[slot_name]:
            _generate_content_recursive(
                node=node,
                parent_path=popup_root_path,
                parent_width=inner_frame.width,
                parent_height=inner_frame.height,
                scene=scene, project=project, redream_bin=redream_bin,
                project_prefix=project_prefix, module_name=module_name,
                plist_path=plist_path,
                commands=all_commands,
                atlas_name=atlas_name,
            )

    # 5b. 创建容器节点并填充内容（按 Figma 的 back-to-front 顺序）
    # 标题栏（底层）→ 内容区域 → 按钮组（顶层）
    for slot_name in ["标题栏", "内容区域", "按钮组"]:
        if not slots[slot_name]:
            continue

        container_path = f"{popup_root_path}/{slot_name}"

        # 创建容器节点
        all_commands.append({
            "cmd": generate_add_node_cmd(scene, popup_root_path, "CCNode", slot_name, project, redream_bin),
            "desc": f"[骨架] 添加容器: {slot_name}"
        })
        # 容器默认锚点 0.5,0.5
        all_commands.append({
            "cmd": generate_set_property_cmd(scene, container_path, "anchorPoint", "0.5,0.5", project, redream_bin),
            "desc": f"[骨架] {slot_name}.anchorPoint = 0.5,0.5"
        })

        # 计算容器包围盒
        bbox = _compute_bounding_box(slots[slot_name])
        if bbox:
            cx_pct = (bbox["x"] + bbox["width"] / 2) / inner_frame.width * 100
            cy_pct = (1 - (bbox["y"] + bbox["height"] / 2) / inner_frame.height) * 100
            cpos = f"{round(cx_pct, 1)},{round(cy_pct, 1)},0,2,2"
            csize = convert_size(bbox["width"], bbox["height"])
            all_commands.append({
                "cmd": generate_set_property_cmd(scene, container_path, "position", cpos, project, redream_bin),
                "desc": f"[骨架] {slot_name}.position = {cpos}"
            })
            all_commands.append({
                "cmd": generate_set_property_cmd(scene, container_path, "contentSize", csize["size_str"], project, redream_bin),
                "desc": f"[骨架] {slot_name}.contentSize = {csize['size_str']}"
            })
        else:
            bbox = {"x": 0, "y": 0, "width": inner_frame.width, "height": inner_frame.height}

        # 填充容器内容
        for node in slots[slot_name]:
            adjusted_node = _clone_node_with_offset(node, -bbox["x"], -bbox["y"])
            _generate_content_recursive(
                node=adjusted_node,
                parent_path=container_path,
                parent_width=bbox["width"],
                parent_height=bbox["height"],
                scene=scene, project=project, redream_bin=redream_bin,
                project_prefix=project_prefix, module_name=module_name,
                plist_path=plist_path,
                commands=all_commands,
                atlas_name=atlas_name,
            )

    return all_commands


def generate_interface_commands(
    root_node: FigmaNode,
    scene: str,
    project: str,
    redream_bin: str,
    project_prefix: str,
    module_name: str,
    plist_path: str = "",
    atlas_name: str = "",
) -> list:
    """生成界面场景的完整命令：标准骨架 + Figma 内容映射"""
    all_commands = []

    # 生成界面骨架
    all_commands.extend(
        generate_skeleton_commands(INTERFACE_SKELETON, scene, project, redream_bin)
    )

    # 内容放入总组
    content_root = "CCLayer/安全区域/总组"

    # 跳过背景类节点（由骨架处理），其他内容放入总组
    for child in root_node.children:
        if child.name.startswith("背景图_") or child.name.startswith("遮罩_"):
            # 背景图 → 放入背景组
            _generate_content_recursive(
                node=child,
                parent_path="CCLayer/背景组",
                parent_width=root_node.width,
                parent_height=root_node.height,
                scene=scene, project=project, redream_bin=redream_bin,
                project_prefix=project_prefix, module_name=module_name,
                plist_path=plist_path,
                commands=all_commands,
                atlas_name=atlas_name,
            )
        else:
            _generate_content_recursive(
                node=child,
                parent_path=content_root,
                parent_width=root_node.width,
                parent_height=root_node.height,
                scene=scene, project=project, redream_bin=redream_bin,
                project_prefix=project_prefix, module_name=module_name,
                plist_path=plist_path,
                commands=all_commands,
                atlas_name=atlas_name,
            )

    return all_commands


def _compute_bounding_box(nodes: list) -> Optional[dict]:
    """计算一组节点的包围盒"""
    if not nodes:
        return None
    min_x = min(n.x for n in nodes)
    min_y = min(n.y for n in nodes)
    max_x = max(n.x + n.width for n in nodes)
    max_y = max(n.y + n.height for n in nodes)
    return {
        "x": min_x,
        "y": min_y,
        "width": max_x - min_x,
        "height": max_y - min_y,
    }


def _clone_node_with_offset(node: FigmaNode, dx: float, dy: float) -> FigmaNode:
    """创建节点的浅拷贝，偏移坐标"""
    import copy
    cloned = copy.copy(node)
    cloned.x = node.x + dx
    cloned.y = node.y + dy
    # children 保持原引用（不需要深拷贝，递归时直接用原 children）
    return cloned


def _generate_content_recursive(
    node: FigmaNode,
    parent_path: str,
    parent_width: float,
    parent_height: float,
    scene: str,
    project: str,
    redream_bin: str,
    project_prefix: str,
    module_name: str,
    plist_path: str,
    commands: list,
    atlas_name: str = "",
):
    """递归生成内容节点的命令（BFS 展开一个子树）"""
    queue = [(node, parent_path, parent_width, parent_height)]

    while queue:
        n, pp, pw, ph = queue.pop(0)

        cmds = generate_commands_for_node(
            node=n, parent_path=pp, scene=scene, project=project,
            redream_bin=redream_bin, project_prefix=project_prefix,
            module_name=module_name, parent_width=pw, parent_height=ph,
            plist_path=plist_path, atlas_name=atlas_name,
        )
        commands.extend(cmds)

        node_path = f"{pp}/{n.name}"
        # Figma 图层顺序与 Redream 渲染顺序相反：反转子节点
        for child in n.children:
            queue.append((child, node_path, n.width, n.height))


def _generate_flat_commands(
    root_node: FigmaNode,
    scene: str,
    project: str,
    redream_bin: str,
    project_prefix: str,
    module_name: str,
    plist_path: str = "",
    atlas_name: str = "",
) -> list:
    """平铺模式：直接镜像 Figma 结构（无骨架），用于无法识别类型的场景"""
    root_type = "CCNode"
    for kw in CCLAYER_KEYWORDS:
        if kw in root_node.name or kw in scene:
            root_type = "CCLayer"
            break

    all_commands = []
    queue = [(root_node, root_type, root_node.width, root_node.height)]

    while queue:
        node, parent_path, pw, ph = queue.pop(0)

        if node == root_node:
            # Figma 图层顺序与 Redream 渲染顺序相反：反转子节点
            for child in node.children:
                queue.append((child, root_type, node.width, node.height))
            continue

        cmds = generate_commands_for_node(
            node=node, parent_path=parent_path, scene=scene,
            project=project, redream_bin=redream_bin,
            project_prefix=project_prefix, module_name=module_name,
            parent_width=pw, parent_height=ph, plist_path=plist_path,
            atlas_name=atlas_name,
        )
        all_commands.extend(cmds)

        node_path = f"{parent_path}/{node.name}"
        # Figma 图层顺序与 Redream 渲染顺序相反：反转子节点
        for child in node.children:
            queue.append((child, node_path, node.width, node.height))

    return all_commands


def generate_all_commands(
    root_node: FigmaNode,
    scene: str,
    project: str,
    redream_bin: str,
    project_prefix: str,
    module_name: str,
    design_width: float,
    design_height: float,
    plist_path: str = "",
    atlas_name: str = "",
) -> list:
    """
    为整个节点树生成所有 CLI 命令。

    自动检测场景类型：
      - 弹窗 → 生成弹窗标准骨架 + 内容映射
      - 界面 → 生成界面标准骨架 + 内容映射
      - 浮层 → 生成浮层标准骨架 + 内容映射
      - 其他 → 平铺模式（直接镜像 Figma 结构）
    """
    scene_type = detect_scene_type(root_node.name, scene)

    if scene_type == "弹窗":
        return generate_popup_commands(
            root_node, scene, project, redream_bin,
            project_prefix, module_name, plist_path, atlas_name
        )
    elif scene_type == "界面":
        return generate_interface_commands(
            root_node, scene, project, redream_bin,
            project_prefix, module_name, plist_path, atlas_name
        )
    elif scene_type == "浮层":
        # 浮层骨架 + 内容放入总组
        all_commands = generate_skeleton_commands(
            OVERLAY_SKELETON, scene, project, redream_bin
        )
        content_root = "CCLayer/总组"
        for child in root_node.children:
            if child.name.startswith("背景图_") or child.name.startswith("遮罩_"):
                _generate_content_recursive(
                    child, "CCLayer/背景组",
                    root_node.width, root_node.height,
                    scene, project, redream_bin,
                    project_prefix, module_name, plist_path, all_commands,
                    atlas_name
                )
            else:
                _generate_content_recursive(
                    child, content_root,
                    root_node.width, root_node.height,
                    scene, project, redream_bin,
                    project_prefix, module_name, plist_path, all_commands,
                    atlas_name
                )
        return all_commands
    else:
        return _generate_flat_commands(
            root_node, scene, project, redream_bin,
            project_prefix, module_name, plist_path, atlas_name
        )


# ============================================================
# 5. 图片导出计划
# ============================================================

def generate_export_plan(
    root_node: FigmaNode,
    file_key: str,
    project_prefix: str,
    module_name: str,
    scale: int = 1,
    image_format: str = "png"
) -> dict:
    """
    生成图片导出计划

    返回：
        {
            "api_url": "Figma REST API 图片导出 URL",
            "node_ids": ["id1", "id2", ...],
            "files": [{"node_id": "...", "figma_name": "...", "export_name": "..."}, ...]
        }
    """
    export_nodes = collect_export_nodes(root_node)

    if not export_nodes:
        return {"api_url": "", "node_ids": [], "files": []}

    node_ids = [n.id for n in export_nodes]
    ids_param = ",".join(node_ids)

    api_url = (
        f"https://api.figma.com/v1/images/{file_key}"
        f"?ids={ids_param}&scale={scale}&format={image_format}"
    )

    files = []
    for n in export_nodes:
        export_name = generate_image_name(n, project_prefix, module_name)
        files.append({
            "node_id": n.id,
            "figma_name": n.name,
            "export_name": export_name,
            "width": n.width,
            "height": n.height,
        })

    return {
        "api_url": api_url,
        "node_ids": node_ids,
        "scale": scale,
        "format": image_format,
        "files": files,
    }


# ============================================================
# 5b. 图片下载
# ============================================================

def find_or_create_atlas_dir(project_dir: str, project_prefix: str, module_name: str, atlas_name: str = None) -> str:
    """
    在工程 image/ 目录下查找或创建图集文件夹。

    返回图集文件夹名。
    """
    image_dir = os.path.join(project_dir, "image")
    if atlas_name:
        target = atlas_name
    else:
        target = f"{project_prefix}_{module_name}"

    target_path = os.path.join(image_dir, target)
    if not os.path.exists(target_path):
        os.makedirs(target_path, exist_ok=True)

    return target


def download_images(
    export_plan: dict,
    project_dir: str,
    atlas_dir_name: str,
    figma_token: str,
) -> dict:
    """
    调用 Figma REST API 获取图片 URL 并下载到工程目录。

    export_plan: generate_export_plan() 的返回值
    project_dir: 工程根目录
    atlas_dir_name: 图集文件夹名（image/ 下的子目录）
    figma_token: Figma API token

    返回下载结果摘要。
    """
    if not export_plan.get("node_ids"):
        return {"downloaded": 0, "errors": [], "message": "没有需要导出的图片"}

    # 1. 调用 Figma API 获取图片 URL
    api_url = export_plan["api_url"]
    req = urllib.request.Request(api_url, headers={"X-Figma-Token": figma_token})

    try:
        with urllib.request.urlopen(req) as resp:
            api_result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"downloaded": 0, "errors": [f"Figma API 错误: {e.code} {e.reason}"], "message": "API 请求失败"}

    image_urls = api_result.get("images", {})
    if not image_urls:
        return {"downloaded": 0, "errors": ["Figma API 未返回图片 URL"], "message": "无图片 URL"}

    # 2. 下载图片到 image/{atlas_dir_name}/
    target_dir = os.path.join(project_dir, "image", atlas_dir_name)
    os.makedirs(target_dir, exist_ok=True)

    downloaded = 0
    errors = []
    files = []

    for file_info in export_plan["files"]:
        node_id = file_info["node_id"]
        export_name = file_info["export_name"]
        img_url = image_urls.get(node_id)

        if not img_url:
            errors.append(f"节点 {node_id} ({file_info['figma_name']}) 无图片 URL")
            continue

        target_path = os.path.join(target_dir, export_name)
        try:
            urllib.request.urlretrieve(img_url, target_path)
            downloaded += 1
            files.append({"name": export_name, "path": target_path})
        except Exception as e:
            errors.append(f"下载失败 {export_name}: {e}")

    return {
        "downloaded": downloaded,
        "total": len(export_plan["files"]),
        "errors": errors,
        "target_dir": target_dir,
        "atlas_name": atlas_dir_name,
        "files": files,
        "message": f"已下载 {downloaded}/{len(export_plan['files'])} 张图片到 image/{atlas_dir_name}/",
    }


# ============================================================
# 5c. TexturePacker 打图
# ============================================================

# 内置最小 .tps 模板（从 GoodsMerge 标准配置提取）
MINIMAL_TPS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<data version="1.0">
    <struct type="Settings">
        <key>fileFormatVersion</key>
        <int>6</int>
        <key>texturePackerVersion</key>
        <string>7.0.1</string>
        <key>autoSDSettings</key>
        <array>
            <struct type="AutoSDSettings">
                <key>scale</key>
                <double>1</double>
                <key>extension</key>
                <string></string>
                <key>spriteFilter</key>
                <string></string>
                <key>acceptFractionalValues</key>
                <false/>
                <key>maxTextureSize</key>
                <QSize>
                    <key>width</key>
                    <int>-1</int>
                    <key>height</key>
                    <int>-1</int>
                </QSize>
            </struct>
        </array>
        <key>allowRotation</key>
        <false/>
        <key>shapeDebug</key>
        <false/>
        <key>dpi</key>
        <uint>72</uint>
        <key>dataFormat</key>
        <string>cocos2d</string>
        <key>textureFileName</key>
        <filename>__TEXTURE_FILENAME__</filename>
        <key>flipPVR</key>
        <false/>
        <key>pvrQualityLevel</key>
        <uint>3</uint>
        <key>astcQualityLevel</key>
        <uint>2</uint>
        <key>basisUniversalQualityLevel</key>
        <uint>2</uint>
        <key>etc1QualityLevel</key>
        <uint>70</uint>
        <key>etc2QualityLevel</key>
        <uint>70</uint>
        <key>dxtInformations</key>
        <struct type="DxtsettingsDTO">
            <key>compressionMode</key>
            <enum type="SettingsBase::DxtCompressionMode">DXT_PERCEPTUAL</enum>
        </struct>
        <key>jxlLossyQuality</key>
        <uint>75</uint>
        <key>jxlEffort</key>
        <uint>7</uint>
        <key>webpQualityLevel</key>
        <uint>80</uint>
        <key>textureSubPath</key>
        <string></string>
        <key>textureFormat</key>
        <enum type="SettingsBase::TextureFormat">webp</enum>
        <key>borderPadding</key>
        <uint>0</uint>
        <key>maxTextureSize</key>
        <QSize>
            <key>width</key>
            <int>4096</int>
            <key>height</key>
            <int>4096</int>
        </QSize>
        <key>fixedTextureSize</key>
        <QSize>
            <key>width</key>
            <int>-1</int>
            <key>height</key>
            <int>-1</int>
        </QSize>
        <key>algorithmSettings</key>
        <struct type="AlgorithmSettings">
            <key>algorithm</key>
            <enum type="AlgorithmSettings::AlgorithmId">MaxRects</enum>
            <key>freeSizeMode</key>
            <enum type="AlgorithmSettings::AlgorithmFreeSizeMode">Best</enum>
            <key>sizeConstraints</key>
            <enum type="AlgorithmSettings::SizeConstraints">POT</enum>
            <key>orderPriority</key>
            <enum type="AlgorithmSettings::OrderPriority">Area</enum>
            <key>order</key>
            <enum type="AlgorithmSettings::Order">Descending</enum>
        </struct>
        <key>dataFileNames</key>
        <map type="GFileNameMap">
            <key>data</key>
            <struct type="DataFile">
                <key>name</key>
                <filename>__DATA_FILENAME__</filename>
            </struct>
        </map>
        <key>multiPackMode</key>
        <enum type="SettingsBase::MultiPackMode">MultiPackOff</enum>
        <key>forceIdenticalLayout</key>
        <false/>
        <key>outputFormat</key>
        <enum type="SettingsBase::OutputFormat">RGBA8888</enum>
        <key>alphaHandling</key>
        <enum type="SettingsBase::AlphaHandling">ClearTransparentPixels</enum>
        <key>contentProtection</key>
        <struct type="ContentProtection">
            <key>key</key>
            <string></string>
        </struct>
        <key>autoAliasEnabled</key>
        <true/>
        <key>trimSpriteNames</key>
        <false/>
        <key>prependSmartFolderName</key>
        <false/>
        <key>autodetectAnimations</key>
        <true/>
        <key>globalSpriteSettings</key>
        <struct type="SpriteSettings">
            <key>scale</key>
            <double>1</double>
            <key>scaleMode</key>
            <enum type="ScaledObject::ScaleMode">Smooth</enum>
            <key>extrude</key>
            <uint>1</uint>
            <key>trimThreshold</key>
            <uint>1</uint>
            <key>trimMargin</key>
            <uint>1</uint>
            <key>trimMode</key>
            <enum type="SpriteSettings::TrimMode">Trim</enum>
            <key>tracerTolerance</key>
            <int>200</int>
            <key>heuristicMask</key>
            <false/>
            <key>defaultPivotPoint</key>
            <point_f>0.5,0.5</point_f>
            <key>writePivotPoints</key>
            <false/>
        </struct>
        <key>fileList</key>
        <array>
            <filename>__FILE_LIST__</filename>
        </array>
        <key>ignoreFileList</key>
        <array/>
        <key>replaceList</key>
        <array/>
        <key>ignoredWarnings</key>
        <array/>
        <key>commonDivisorX</key>
        <uint>1</uint>
        <key>commonDivisorY</key>
        <uint>1</uint>
        <key>packNormalMaps</key>
        <false/>
        <key>autodetectNormalMaps</key>
        <true/>
        <key>normalMapFilter</key>
        <string></string>
        <key>normalMapSuffix</key>
        <string></string>
        <key>normalMapSheetFileName</key>
        <filename></filename>
        <key>exporterProperties</key>
        <map type="ExporterProperties"/>
    </struct>
</data>"""


def generate_tps_file(
    project_dir: str,
    atlas_name: str,
    template_tps_path: str = None,
) -> str:
    """
    生成 .tps 文件（若不存在）。

    优先从工程 tps/ 下复制已有 tps 作为模板，替换路径。
    若无模板则使用内置最小模板。

    返回生成的 tps 文件路径。
    """
    tps_dir = os.path.join(project_dir, "tps")
    os.makedirs(tps_dir, exist_ok=True)
    tps_path = os.path.join(tps_dir, f"{atlas_name}.tps")

    # 如果已存在，直接返回
    if os.path.exists(tps_path):
        return tps_path

    # 路径替换值（相对于 tps/ 目录）
    texture_filename = f"../_img_plist/{atlas_name}.webp"
    data_filename = f"../_img_plist/{atlas_name}.plist"
    file_list = f"../image/{atlas_name}"

    if template_tps_path and os.path.exists(template_tps_path):
        # 从模板复制
        with open(template_tps_path, 'r') as f:
            content = f.read()

        # 替换 textureFileName
        content = re.sub(
            r'(<key>textureFileName</key>\s*<filename>)[^<]*(</filename>)',
            rf'\g<1>{texture_filename}\2',
            content
        )
        # 替换 dataFileNames/data/name
        content = re.sub(
            r'(<key>name</key>\s*<filename>)[^<]*(</filename>)',
            rf'\g<1>{data_filename}\2',
            content
        )
        # 替换 fileList（两种结构都支持）
        # 结构 A: <key>fileList</key><array><filename>path</filename>
        content = re.sub(
            r'(<key>fileList</key>\s*<array>\s*<filename>)[^<]*(</filename>)',
            rf'\g<1>{file_list}\2',
            content
        )
        # 结构 B: fileLists/map/files/array 中的 ../image/xxx 路径
        content = re.sub(
            r'(<filename>)\.\./image/[^<]*(</filename>)',
            rf'\g<1>{file_list}\2',
            content
        )
        # 将 dataFormat 从 cocos2d-x 改为 cocos2d
        content = re.sub(
            r'(<key>dataFormat</key>\s*<string>)cocos2d-x(</string>)',
            r'\g<1>cocos2d\2',
            content
        )
        # 确保 maxTextureSize 为 4096
        content = re.sub(
            r'(<key>maxTextureSize</key>\s*<QSize>\s*<key>width</key>\s*<int>)\d+(</int>)',
            r'\g<1>4096\2',
            content
        )
        content = re.sub(
            r'(<key>maxTextureSize</key>\s*<QSize>\s*<key>width</key>\s*<int>\d+</int>\s*<key>height</key>\s*<int>)\d+(</int>)',
            r'\g<1>4096\2',
            content
        )
    else:
        # 尝试从工程 tps/ 找一个已有模板
        existing_tps = None
        if os.path.exists(tps_dir):
            for f in os.listdir(tps_dir):
                if f.endswith(".tps") and f != f"{atlas_name}.tps":
                    existing_tps = os.path.join(tps_dir, f)
                    break

        if existing_tps:
            return generate_tps_file(project_dir, atlas_name, existing_tps)

        # 使用内置模板
        content = MINIMAL_TPS_TEMPLATE
        content = content.replace("__TEXTURE_FILENAME__", texture_filename)
        content = content.replace("__DATA_FILENAME__", data_filename)
        content = content.replace("__FILE_LIST__", file_list)

    with open(tps_path, 'w') as f:
        f.write(content)

    return tps_path


def run_texture_packer(
    tps_path: str,
    tp_bin: str = "/Applications/TexturePacker.app/Contents/MacOS/TexturePacker",
) -> dict:
    """
    调用 TexturePacker CLI 打图。

    返回执行结果。
    """
    if not os.path.exists(tp_bin):
        return {"success": False, "error": f"TexturePacker 未找到: {tp_bin}"}

    if not os.path.exists(tps_path):
        return {"success": False, "error": f"tps 文件不存在: {tps_path}"}

    try:
        result = subprocess.run(
            [tp_bin, tps_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return {
                "success": True,
                "message": f"TexturePacker 打图成功: {tps_path}",
                "stdout": result.stdout,
            }
        else:
            return {
                "success": False,
                "error": f"TexturePacker 返回码 {result.returncode}",
                "stderr": result.stderr,
                "stdout": result.stdout,
            }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "TexturePacker 执行超时(60s)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# 6. 分析报告
# ============================================================

def generate_analysis_report(root_node: FigmaNode, project_prefix: str, module_name: str) -> dict:
    """
    生成完整分析报告

    返回节点分析结果、导出计划、命令统计
    """
    all_nodes = collect_all_nodes(root_node)
    export_nodes = collect_export_nodes(root_node)

    # 按类型统计
    type_stats = {}
    for n in all_nodes:
        t = n.redream_type
        type_stats[t] = type_stats.get(t, 0) + 1

    # 节点树结构（缩进文本）
    tree_lines = []
    def build_tree_text(node, indent=0):
        prefix = "  " * indent
        export_mark = " 📷" if node.needs_export else ""
        type_mark = f"[{node.redream_type}]"
        size_mark = f"({node.width}x{node.height})"
        tree_lines.append(f"{prefix}├─ {node.name} {type_mark} {size_mark}{export_mark}")
        for child in node.children:
            build_tree_text(child, indent + 1)

    build_tree_text(root_node)

    # 导出文件列表
    export_files = []
    for n in export_nodes:
        export_files.append({
            "node_id": n.id,
            "figma_name": n.name,
            "export_name": generate_image_name(n, project_prefix, module_name),
            "size": f"{n.width}x{n.height}",
        })

    # 根节点类型判断
    root_type = "CCNode"
    for kw in CCLAYER_KEYWORDS:
        if kw in root_node.name:
            root_type = "CCLayer"
            break

    # 场景类型和骨架映射
    scene_type = detect_scene_type(root_node.name)
    skeleton_info = None

    if scene_type == "弹窗":
        inner_frame = find_popup_inner_frame(root_node)
        mask_node = find_mask_node(root_node)
        if inner_frame:
            # 分类内容节点
            slot_mapping = {}
            for child in inner_frame.children:
                slot = classify_popup_child(child)
                if slot not in slot_mapping:
                    slot_mapping[slot] = []
                slot_mapping[slot].append(child.name)

            skeleton_info = {
                "scene_type": scene_type,
                "skeleton": "弹窗标准骨架",
                "inner_frame": inner_frame.name,
                "inner_frame_size": f"{inner_frame.width}x{inner_frame.height}",
                "mask_opacity": convert_opacity(mask_node.opacity) if mask_node else 204,
                "slot_mapping": slot_mapping,
                "skeleton_tree": (
                    "CCLayer\n"
                    "├─ 总组 (CCNode, visible=false, 50%/50%, 100%/100%)\n"
                    "│   ├─ 全屏防穿透按钮 (REDNodeButton)\n"
                    f"│   ├─ 黑色遮罩 (CCLayerColor, opacity={convert_opacity(mask_node.opacity) if mask_node else 204})\n"
                    "│   └─ 安全区域 (RedSafeAreaLayer)\n"
                    "│       └─ 弹窗总组 (CCNode)\n"
                    + "".join(
                        f"│           ├─ [{slot}]: {', '.join(names)}\n"
                        for slot, names in slot_mapping.items()
                    )
                    + "└─ 浮层定位层 (CCNode)"
                ),
            }
    elif scene_type:
        skeleton_info = {
            "scene_type": scene_type,
            "skeleton": f"{scene_type}标准骨架",
        }

    return {
        "root_name": root_node.name,
        "root_type": root_type,
        "scene_type": scene_type,
        "total_nodes": len(all_nodes),
        "export_count": len(export_nodes),
        "type_stats": type_stats,
        "tree_text": "\n".join(tree_lines),
        "export_files": export_files,
        "design_size": {
            "width": root_node.width,
            "height": root_node.height,
        },
        "skeleton_info": skeleton_info,
    }


# ============================================================
# 7. 批量配置生成
# ============================================================

def generate_batch_config(
    root_node: FigmaNode,
    scene: str,
    project_prefix: str,
    module_name: str,
    plist_path: str = "",
    atlas_name: str = "",
) -> list:
    """
    生成 batch --config 所需的 JSON 配置

    格式：[{scene, node, property, value}, ...]
    """
    root_type = "CCNode"
    for kw in CCLAYER_KEYWORDS:
        if kw in root_node.name or kw in scene:
            root_type = "CCLayer"
            break

    batch_items = []

    def process_node(node, parent_path, pw, ph):
        if node == root_node:
            # Figma 图层顺序与 Redream 渲染顺序相反：反转子节点
            for child in node.children:
                process_node(child, root_type, node.width, node.height)
            return

        node_path = f"{parent_path}/{node.name}"

        # 位置
        pos = convert_position(
            node.x, node.y, node.width, node.height,
            anchor_x=0.5, anchor_y=0.5,
            parent_width=pw, parent_height=ph,
            h_constraint=node.h_constraint,
            v_constraint=node.v_constraint
        )
        batch_items.append({
            "scene": scene,
            "node": node_path,
            "property": "position",
            "value": pos["position_str"]
        })

        # 锚点（标准默认 0.5,0.5，所有内容节点统一设置）
        if node.redream_type in ("CCScale9Sprite", "CCNode", "CCSprite", "CCRedLabel", "REDNodeButton"):
            batch_items.append({
                "scene": scene,
                "node": node_path,
                "property": "anchorPoint",
                "value": "0.5,0.5"
            })

        # 尺寸
        size = convert_size(node.width, node.height)
        if node.redream_type in ("CCNode", "CCLayerColor", "REDNodeButton", "CCLayer"):
            batch_items.append({
                "scene": scene,
                "node": node_path,
                "property": "contentSize",
                "value": size["size_str"]
            })
        elif node.redream_type == "CCScale9Sprite":
            batch_items.append({
                "scene": scene,
                "node": node_path,
                "property": "preferedSize",
                "value": size["size_str"]
            })

        # 图片引用
        if node.needs_export and node.redream_type in ("CCSprite", "CCScale9Sprite", "CCProgressTimer"):
            if plist_path:
                img_name = generate_image_name(node, project_prefix, module_name)
                frame_value = f"{plist_path},{img_name}"
            else:
                frame_value = generate_image_ref(node, project_prefix, module_name, atlas_name)
            prop_name = "displayFrame" if node.redream_type != "CCScale9Sprite" else "spriteFrame"
            batch_items.append({
                "scene": scene,
                "node": node_path,
                "property": prop_name,
                "value": frame_value
            })

        # 颜色
        if node.redream_type == "CCLayerColor" and node.fill_color:
            batch_items.append({
                "scene": scene,
                "node": node_path,
                "property": "color",
                "value": convert_color(node.fill_r, node.fill_g, node.fill_b)
            })

        # 透明度
        if node.opacity < 1.0:
            batch_items.append({
                "scene": scene,
                "node": node_path,
                "property": "opacity",
                "value": str(convert_opacity(node.opacity))
            })

        # 可见性
        if not node.visible:
            batch_items.append({
                "scene": scene,
                "node": node_path,
                "property": "visible",
                "value": "false"
            })

        # 文本
        if node.redream_type == "CCRedLabel" and node.text_content:
            batch_items.append({
                "scene": scene,
                "node": node_path,
                "property": "string",
                "value": node.text_content
            })

        # 递归子节点（Figma 图层顺序与 Redream 渲染顺序相反）
        for child in node.children:
            process_node(child, node_path, node.width, node.height)

    process_node(root_node, "", root_node.width, root_node.height)
    return batch_items


# ============================================================
# 8. 新建场景辅助
# ============================================================

CCLAYER_RESOLUTIONS = """<array>
                <dict>
                    <key>centeredOrigin</key>
                    <false/>
                    <key>height</key>
                    <integer>2400</integer>
                    <key>mainScale</key>
                    <real>2</real>
                    <key>name</key>
                    <string>设计分辨率 1080x2400</string>
                    <key>resourceScale</key>
                    <real>2</real>
                    <key>scale</key>
                    <real>2</real>
                    <key>width</key>
                    <integer>1080</integer>
                </dict>
                <dict>
                    <key>centeredOrigin</key>
                    <false/>
                    <key>height</key>
                    <integer>2080</integer>
                    <key>mainScale</key>
                    <real>2</real>
                    <key>name</key>
                    <string>正常分辨率 1080x2080</string>
                    <key>resourceScale</key>
                    <real>2</real>
                    <key>scale</key>
                    <real>2</real>
                    <key>width</key>
                    <integer>1080</integer>
                </dict>
                <dict>
                    <key>centeredOrigin</key>
                    <false/>
                    <key>height</key>
                    <integer>2080</integer>
                    <key>mainScale</key>
                    <real>2</real>
                    <key>name</key>
                    <string>偏宽分辨率 2100x2080</string>
                    <key>resourceScale</key>
                    <real>2</real>
                    <key>scale</key>
                    <real>2</real>
                    <key>width</key>
                    <integer>2100</integer>
                </dict>
                <dict>
                    <key>centeredOrigin</key>
                    <false/>
                    <key>height</key>
                    <integer>2800</integer>
                    <key>mainScale</key>
                    <real>2</real>
                    <key>name</key>
                    <string>偏高分辨率 1080x2800</string>
                    <key>resourceScale</key>
                    <real>2</real>
                    <key>scale</key>
                    <real>2</real>
                    <key>width</key>
                    <integer>1080</integer>
                </dict>
            </array>"""

CCNODE_RESOLUTION = """<array>
                <dict>
                    <key>centeredOrigin</key>
                    <false/>
                    <key>height</key>
                    <integer>0</integer>
                    <key>mainScale</key>
                    <real>2</real>
                    <key>name</key>
                    <string>Node分辨率</string>
                    <key>resourceScale</key>
                    <real>2</real>
                    <key>scale</key>
                    <real>2</real>
                    <key>width</key>
                    <integer>0</integer>
                </dict>
            </array>"""


def fix_scene_after_creation(red_file: str, is_cclayer: bool) -> str:
    """
    生成修复 new-scene 后的 Python 代码

    修复内容：根节点类型 + 分辨率
    """
    return f'''
import re

red_file = "{red_file}"
is_cclayer = {is_cclayer}

with open(red_file, 'r') as f:
    content = f.read()

if is_cclayer:
    content = content.replace(
        '<key>baseClass</key>\\n            <string>CCNode</string>',
        '<key>baseClass</key>\\n            <string>CCLayer</string>', 1)
    content = content.replace(
        '<key>displayName</key>\\n            <string>CCNode</string>',
        '<key>displayName</key>\\n            <string>CCLayer</string>', 1)

new_res = """{CCLAYER_RESOLUTIONS if is_cclayer else CCNODE_RESOLUTION}"""

content = re.sub(
    r'<key>resolutions</key>\\s*<array>.*?</array>',
    '<key>resolutions</key>\\n            ' + new_res,
    content, flags=re.DOTALL)

with open(red_file, 'w') as f:
    f.write(content)

print(f"Fixed: {{red_file}} (root={{'CCLayer' if is_cclayer else 'CCNode'}})")
'''


# ============================================================
# 8.5 plistlib 后处理：补全 CLI 无法设置的属性
# ============================================================

def postprocess_red_file(red_file: str):
    """
    用 plistlib 直接修改 .red 文件，补全 CLI 无法设置的属性。

    规则：
    1. 所有节点 ignoreAnchorPointForPosition = false（不勾选忽略锚点）
    2. CCLayer 根节点 anchorPoint = [0, 0]
    3. 其他所有节点 anchorPoint = [0.5, 0.5]（默认居中锚点）
    """
    import plistlib as _plistlib

    with open(red_file, "rb") as f:
        data = _plistlib.load(f)

    if "nodeGraph" not in data:
        return

    fixed = []

    def _fix_node(node, is_root=False):
        props = node.get("properties", [])
        name = node.get("displayName", node.get("baseClass", ""))
        base_class = node.get("baseClass", "")

        # RedSafeAreaLayer 内部自动处理位置，跳过不修改
        if base_class == "RedSafeAreaLayer":
            for child in node.get("children", []):
                _fix_node(child, is_root=False)
            return

        # --- 规则 1: ignoreAnchorPointForPosition = false ---
        found_ignore = False
        for p in props:
            if p.get("name") == "ignoreAnchorPointForPosition":
                if p.get("value") is not False:
                    p["value"] = False
                    fixed.append(f"{name}: ignoreAnchorPointForPosition -> false")
                found_ignore = True
                break
        if not found_ignore:
            props.append({"name": "ignoreAnchorPointForPosition", "type": "Check", "value": False})
            fixed.append(f"{name}: +ignoreAnchorPointForPosition=false")

        # --- 规则 2/3: anchorPoint ---
        target_anchor = [0, 0] if is_root else [0.5, 0.5]
        found_anchor = False
        for p in props:
            if p.get("name") == "anchorPoint":
                if p.get("value") != target_anchor:
                    p["value"] = target_anchor
                    fixed.append(f"{name}: anchorPoint -> {target_anchor}")
                found_anchor = True
                break
        if not found_anchor:
            props.append({"name": "anchorPoint", "type": "Point", "value": target_anchor})
            fixed.append(f"{name}: +anchorPoint={target_anchor}")

        node["properties"] = props

        for child in node.get("children", []):
            _fix_node(child, is_root=False)

    _fix_node(data["nodeGraph"], is_root=True)

    with open(red_file, "wb") as f:
        _plistlib.dump(data, f)

    return fixed


# ============================================================
# 9. 完整工作流脚本生成
# ============================================================

def generate_workflow_script(
    root_node: FigmaNode,
    scene: str,
    project: str,
    redream_bin: str,
    project_prefix: str,
    module_name: str,
    image_dir: str = "image/",
    atlas_name: str = "",
) -> str:
    """
    生成完整的 Shell 工作流脚本

    包含：创建场景 → 修复根节点 → 添加节点 → 设置属性
    """
    # 判断根节点类型
    is_cclayer = any(kw in root_node.name or kw in scene for kw in CCLAYER_KEYWORDS)
    root_type = "CCLayer" if is_cclayer else "CCNode"

    lines = [
        "#!/bin/bash",
        f"# Figma → Redream 自动化脚本",
        f"# 源节点: {root_node.name}",
        f"# 场景: {scene}",
        f"# 生成时间: $(date)",
        "",
        f'REDREAM="{redream_bin}"',
        f'PROJECT="{project}"',
        f'SCENE="{scene}"',
        "",
        "set -e  # 遇错即停",
        "",
        "# === Step 1: 创建场景 ===",
        f'$REDREAM modify new-scene --scene $SCENE -p $PROJECT',
        "",
        "# === Step 2: 修复根节点类型和分辨率 ===",
        "# (由 Python 脚本处理，见 fix_scene.py)",
        "",
        "# === Step 3: 添加节点并设置属性 ===",
    ]

    # 生成所有命令
    commands = generate_all_commands(
        root_node, scene, project, redream_bin,
        project_prefix, module_name,
        root_node.width, root_node.height,
        atlas_name=atlas_name,
    )

    for cmd_info in commands:
        lines.append(f"# {cmd_info['desc']}")
        lines.append(cmd_info["cmd"])
        lines.append("")

    # postprocess: 用 plistlib 补全 CLI 无法设置的属性
    script_path = os.path.abspath(__file__)
    lines.extend([
        "# === Step 3.5: plistlib 后处理（补全锚点、ignoreAnchor） ===",
        f'python3 -c "import sys; sys.path.insert(0, \\"{os.path.dirname(script_path)}\\"); '
        f'from figma_auto_export import postprocess_red_file; '
        f'fixes = postprocess_red_file(\\"{scene}\\"); '
        f'print(f\\"后处理修复 {{len(fixes)}} 处\\")"',
        "",
        "# === Step 4: 验证 ===",
        f'$REDREAM inspect scene $SCENE --properties -p $PROJECT',
        "",
        'echo "完成！"',
    ])

    return "\n".join(lines)


# ============================================================
# CLI 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Figma → Redream 自动化出图 + 建节点树工具"
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # --- analyze ---
    p_analyze = subparsers.add_parser("analyze", help="分析 Figma 节点并生成报告")
    p_analyze.add_argument("--input", required=True, help="Figma 节点 JSON 文件路径（或 - 表示 stdin）")
    p_analyze.add_argument("--project-prefix", default="FP", help="项目前缀")
    p_analyze.add_argument("--module-name", default="模块", help="模块名称")

    # --- generate ---
    p_generate = subparsers.add_parser("generate", help="生成 Redream CLI 命令")
    p_generate.add_argument("--input", required=True, help="Figma 节点 JSON 文件路径")
    p_generate.add_argument("--scene", required=True, help="目标 .red 场景路径")
    p_generate.add_argument("--project", required=True, help=".redproj 项目路径")
    p_generate.add_argument("--redream-bin", default="/Applications/Redream.app/Contents/MacOS/Redream", help="Redream 二进制路径")
    p_generate.add_argument("--project-prefix", default="FP", help="项目前缀")
    p_generate.add_argument("--module-name", default="模块", help="模块名称")
    p_generate.add_argument("--plist-path", default="", help="图集 plist 路径（手动指定，优先于自动生成）")
    p_generate.add_argument("--atlas-name", default="", help="图集名称（默认为 {项目前缀}_{模块名}）")
    p_generate.add_argument("--format", choices=["shell", "batch", "commands"], default="commands", help="输出格式")

    # --- export-images ---
    p_export = subparsers.add_parser("export-images", help="生成图片导出计划")
    p_export.add_argument("--input", required=True, help="Figma 节点 JSON 文件路径")
    p_export.add_argument("--file-key", required=True, help="Figma 文件 key")
    p_export.add_argument("--project-prefix", default="FP", help="项目前缀")
    p_export.add_argument("--module-name", default="模块", help="模块名称")
    p_export.add_argument("--scale", type=int, default=1, help="导出倍率")

    # --- download-images ---
    p_download = subparsers.add_parser("download-images", help="下载 Figma 图片到工程 image/ 目录")
    p_download.add_argument("--input", required=True, help="Figma 节点 JSON 文件路径")
    p_download.add_argument("--file-key", required=True, help="Figma 文件 key")
    p_download.add_argument("--project-dir", required=True, help="工程根目录路径")
    p_download.add_argument("--project-prefix", default="FP", help="项目前缀")
    p_download.add_argument("--module-name", default="模块", help="模块名称")
    p_download.add_argument("--atlas-name", default="", help="图集文件夹名（默认为 {项目前缀}_{模块名}）")
    p_download.add_argument("--figma-token", default="", help="Figma API token（或设置 FIGMA_TOKEN 环境变量）")
    p_download.add_argument("--scale", type=int, default=1, help="导出倍率")

    # --- pack-images ---
    p_pack = subparsers.add_parser("pack-images", help="生成 tps + 调用 TexturePacker 打图")
    p_pack.add_argument("--project-dir", required=True, help="工程根目录路径")
    p_pack.add_argument("--atlas-name", required=True, help="图集名称")
    p_pack.add_argument("--template-tps", default="", help="模板 tps 文件路径（可选）")
    p_pack.add_argument("--tp-bin", default="/Applications/TexturePacker.app/Contents/MacOS/TexturePacker", help="TexturePacker CLI 路径")

    # --- fix-scene ---
    p_fix = subparsers.add_parser("fix-scene", help="修复 new-scene 创建的场景（根节点+分辨率）")
    p_fix.add_argument("--red-file", required=True, help=".red 文件路径")
    p_fix.add_argument("--scene-name", required=True, help="场景名称（用于判断根节点类型）")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # 读取输入
    if args.command in ("analyze", "generate", "export-images", "download-images"):
        input_path = args.input
        if input_path == "-":
            data = json.load(sys.stdin)
        else:
            with open(input_path, 'r') as f:
                data = json.load(f)

        # 解析节点树
        # 支持两种输入格式：
        # 1. Figma REST API /v1/files/:key/nodes 的 document 字段
        # 2. 直接的节点对象
        if "document" in data:
            node_data = data["document"]
        elif "nodes" in data:
            # /v1/files/:key/nodes 返回格式
            first_key = list(data["nodes"].keys())[0]
            node_data = data["nodes"][first_key]["document"]
        else:
            node_data = data

        root = parse_figma_node(node_data)
        classify_node(root)

    if args.command == "analyze":
        report = generate_analysis_report(root, args.project_prefix, args.module_name)
        print(json.dumps(report, ensure_ascii=False, indent=2))

    elif args.command == "generate":
        atlas = args.atlas_name or f"{args.project_prefix}_{args.module_name}"
        if args.format == "shell":
            script = generate_workflow_script(
                root, args.scene, args.project, args.redream_bin,
                args.project_prefix, args.module_name,
                atlas_name=atlas
            )
            print(script)
        elif args.format == "batch":
            batch = generate_batch_config(
                root, args.scene, args.project_prefix, args.module_name,
                args.plist_path, atlas
            )
            print(json.dumps(batch, ensure_ascii=False, indent=2))
        else:  # commands
            commands = generate_all_commands(
                root, args.scene, args.project, args.redream_bin,
                args.project_prefix, args.module_name,
                root.width, root.height,
                args.plist_path, atlas
            )
            for cmd_info in commands:
                print(f"# {cmd_info['desc']}")
                print(cmd_info["cmd"])
                print()

    elif args.command == "export-images":
        plan = generate_export_plan(
            root, args.file_key, args.project_prefix, args.module_name, args.scale
        )
        print(json.dumps(plan, ensure_ascii=False, indent=2))

    elif args.command == "download-images":
        # 获取 Figma token
        figma_token = args.figma_token or os.environ.get("FIGMA_TOKEN", "")
        if not figma_token:
            print(json.dumps({"error": "需要 Figma API token，通过 --figma-token 或 FIGMA_TOKEN 环境变量提供"}, ensure_ascii=False))
            sys.exit(1)

        # 生成导出计划
        plan = generate_export_plan(
            root, args.file_key, args.project_prefix, args.module_name, args.scale
        )

        # 确定图集文件夹
        atlas_name = args.atlas_name or f"{args.project_prefix}_{args.module_name}"
        atlas_dir = find_or_create_atlas_dir(args.project_dir, args.project_prefix, args.module_name, atlas_name)

        # 下载图片
        result = download_images(plan, args.project_dir, atlas_dir, figma_token)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "pack-images":
        # 生成 tps 文件
        template = args.template_tps if args.template_tps else None
        tps_path = generate_tps_file(args.project_dir, args.atlas_name, template)
        print(json.dumps({"tps_path": tps_path, "message": f"tps 文件: {tps_path}"}, ensure_ascii=False))

        # 确保 _img_plist 目录存在
        plist_dir = os.path.join(args.project_dir, "_img_plist")
        os.makedirs(plist_dir, exist_ok=True)

        # 调用 TexturePacker
        tp_result = run_texture_packer(tps_path, args.tp_bin)
        print(json.dumps(tp_result, ensure_ascii=False, indent=2))

    elif args.command == "fix-scene":
        is_cclayer = any(kw in args.scene_name for kw in CCLAYER_KEYWORDS)
        fix_code = fix_scene_after_creation(args.red_file, is_cclayer)

        # 直接执行修复
        exec(fix_code)


if __name__ == "__main__":
    main()
