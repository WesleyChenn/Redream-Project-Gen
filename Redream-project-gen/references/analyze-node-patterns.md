# 节点结构模板

> **⚠️ 适配说明：** 本文件中的模板为 JSON 格式（原 JSON+插件流程），仅作**设计结构参考**。
> 实际绘制时请使用 SKILL.md Step 2 中的 Figma Plugin API 代码模板。
> JSON 中的结构层级、命名、嵌套关系等设计原则仍然有效。

## 目录
1. 全屏遮罩
2. 普通按钮（扁平）
3. 3D 游戏按钮（立体感）
4. 文字型按钮（无底板）
5. 弹窗
6. Toggle 开关（COMPONENT_SET）

---

## 1. 全屏遮罩

```json
{
  "name": "全屏遮罩",
  "type": "RECTANGLE",
  "element_class": "static",
  "x": 0, "y": 0, "w": 1080, "h": 2400,
  "fill": "#000000",
  "opacity": 0.7
}
```

规则：fill 必须是 `#000000`，opacity 固定 `0.7`，禁止其他颜色。

---

## 2. 普通按钮（扁平，2 层）

```json
{
  "name": "按钮_继续",
  "type": "FRAME",
  "element_class": "interactive",
  "x": 240, "y": 1800, "w": 600, "h": 120,
  "children": [
    {
      "name": "底板_继续",
      "type": "RECTANGLE",
      "element_class": "static",
      "x": 0, "y": 0, "w": 600, "h": 120,
      "fill": "#55C040",
      "corner_radius": 60
    },
    {
      "name": "文字_继续",
      "type": "TEXT",
      "element_class": "static",
      "x": 150, "y": 35, "w": 300, "h": 50,
      "content": "Continue",
      "font_weight": "Bold",
      "fill": "#FFFFFF"
    }
  ]
}
```

---

## 3. 3D 游戏按钮（立体感，3 层）

截图中按钮有明显阴影/立体感时使用。

```json
{
  "name": "按钮_开始",
  "type": "FRAME",
  "element_class": "interactive",
  "x": 240, "y": 1800, "w": 600, "h": 130,
  "children": [
    {
      "name": "底板_开始_阴影",
      "type": "RECTANGLE",
      "element_class": "static",
      "x": 0, "y": 10, "w": 600, "h": 120,
      "fill": "#2E7D32",
      "corner_radius": 60
    },
    {
      "name": "底板_开始",
      "type": "RECTANGLE",
      "element_class": "static",
      "x": 0, "y": 0, "w": 600, "h": 120,
      "fill": "#55C040",
      "corner_radius": 60
    },
    {
      "name": "文字_开始",
      "type": "TEXT",
      "element_class": "static",
      "x": 150, "y": 35, "w": 300, "h": 50,
      "content": "Play",
      "font_weight": "Bold",
      "fill": "#FFFFFF"
    }
  ]
}
```

阴影层：比主按钮颜色深，y 偏移 8~12px，尺寸相同或略大。

---

## 4. 文字型按钮（无底板）

截图中只有文字可点击（如 QUIT / Skip）时使用。

```json
{
  "name": "按钮_退出",
  "type": "FRAME",
  "element_class": "interactive",
  "x": 400, "y": 200, "w": 200, "h": 60,
  "children": [
    {
      "name": "文字_退出",
      "type": "TEXT",
      "element_class": "static",
      "x": 0, "y": 0, "w": 200, "h": 60,
      "content": "QUIT",
      "font_weight": "Bold",
      "fill": "#FFFFFF"
    }
  ]
}
```

禁止强行加 RECTANGLE 底板。

---

## 5. 弹窗

```json
{
  "name": "弹窗_退出确认",
  "type": "FRAME",
  "element_class": "container",
  "x": 90, "y": 800, "w": 900, "h": 700,
  "children": [
    {
      "name": "底板_弹窗",
      "type": "RECTANGLE",
      "element_class": "static",
      "x": 0, "y": 0, "w": 900, "h": 700,
      "fill": "#2C2C2C",
      "corner_radius": 40
    },
    {
      "name": "文字_标题",
      "type": "TEXT",
      "element_class": "static",
      "x": 200, "y": 60, "w": 500, "h": 80,
      "content": "退出游戏？",
      "font_weight": "Bold",
      "fill": "#FFFFFF"
    },
    {
      "name": "面板_内容区",
      "type": "FRAME",
      "element_class": "container",
      "x": 60, "y": 180, "w": 780, "h": 300,
      "children": []
    },
    {
      "name": "按钮_确认退出",
      "type": "FRAME",
      "element_class": "interactive",
      "x": 100, "y": 560, "w": 320, "h": 100,
      "children": []
    },
    {
      "name": "按钮_取消",
      "type": "FRAME",
      "element_class": "interactive",
      "x": 480, "y": 560, "w": 320, "h": 100,
      "children": []
    }
  ]
}
```

规则：
- 标题 TEXT 直接作为弹窗子节点，**禁止**单独包 titlebar Frame（除非截图中有独立标题栏背景色块）
- 图片+说明文字归组在 `面板_内容区` 内，不作弹窗直接子节点

---

## 6. Toggle 开关（COMPONENT_SET）

凡截图中存在**可切换状态的开关**（Music/Sound/Vibration/Hints 等），必须使用 `COMPONENT_SET`。

```json
{
  "name": "开关_音乐",
  "type": "COMPONENT_SET",
  "element_class": "interactive",
  "x": 60, "y": 300, "w": 120, "h": 120,
  "variants": [
    {
      "state": "ON",
      "default": true,
      "children": [
        {
          "name": "底板_音乐",
          "type": "RECTANGLE",
          "element_class": "static",
          "x": 0, "y": 0, "w": 120, "h": 120,
          "fill": "#888888",
          "corner_radius": 60
        },
        {
          "name": "图标_音乐",
          "type": "RECTANGLE",
          "element_class": "static",
          "x": 25, "y": 25, "w": 70, "h": 70,
          "fill": "#AAAAAA"
        }
      ]
    },
    {
      "state": "OFF",
      "children": [
        {
          "name": "底板_音乐",
          "type": "RECTANGLE",
          "element_class": "static",
          "x": 0, "y": 0, "w": 120, "h": 120,
          "fill": "#BBBBBB",
          "corner_radius": 60
        },
        {
          "name": "图标_音乐",
          "type": "RECTANGLE",
          "element_class": "static",
          "x": 25, "y": 25, "w": 70, "h": 70,
          "fill": "#CCCCCC"
        },
        {
          "name": "图标_划线_音乐",
          "type": "RECTANGLE",
          "element_class": "static",
          "x": 5, "y": 55, "w": 110, "h": 10,
          "fill": "#444444",
          "rotation": -45
        }
      ]
    }
  ]
}
```

关键规则：
- `"type": "COMPONENT_SET"` — 必须，插件据此调用 combineAsVariants
- 至少 2 个 variants（ON + OFF）
- 第一个或标记 `"default": true` 的 variant 为初始状态
- ON：深灰底板；OFF：浅灰底板 + 划线矩形（rotation: -45）
- **圆形图标类 Toggle 不加 label 文字**
