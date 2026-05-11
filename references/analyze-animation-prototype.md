# 动画提取与原型连线规范

> 本文档记录 Elsa 从视频/PRD 中提取交互动画、生成 Figma 原型连线的完整规范。
> 所有规则来源于真实实现问题的事后总结。
>
> **⚠️ 适配说明：** 第二节"原型连线 JSON 格式"和第四节"序列帧动画 JSON 格式"为 JSON+插件流程格式，仅作参考。
> 直接绘制时的 Prototype 连线请使用 SKILL.md 2.8 节的 `reactions` API 写法。
> 第一节（动画参数提取）和第三节（规则 K/L/N）的设计原则仍然有效。

---

## 一、从录屏提取动画参数

### 1.1 动画时长提取

**方法：** 录屏通常为 60fps，1 帧 ≈ 16.7ms

```python
# 定位动画起始帧和结束帧
# 用亮度差分法找到"开始变化"和"停止变化"的帧号
import numpy as np
from PIL import Image

def get_lum(path):
    arr = np.array(Image.open(path).convert('L')).astype(float)
    return arr

def estimate_duration_ms(start_frame_no, end_frame_no, fps=60):
    return round((end_frame_no - start_frame_no) / fps * 1000)
```

常见动画时长参考（手机休闲游戏）：
| 类型 | 典型时长 |
|---|---|
| 按钮点击反馈 | 80–120ms |
| 弹窗淡入/缩放弹出 | 300–400ms |
| 页面跳转 | 200–300ms |
| 卡片翻转 | 300–500ms |
| 粒子/特效（不在 Figma 范畴） | 600ms+ |

### 1.2 缓动曲线识别

| 视觉特征 | 缓动类型 | Figma 对应 |
|---|---|---|
| 开始快、结束慢 | Ease Out | EASE_OUT |
| 开始慢、结束快 | Ease In | EASE_IN |
| 两端慢、中间快 | Ease In Out | EASE_IN_AND_OUT |
| 匀速 | Linear | LINEAR |
| 弹性回弹 | Spring | SPRING（Stiffness/Damping 需手动调） |

### 1.3 哪些动画属于 Figma 范畴 / 哪些不属于

| 属于（Figma 原型可表达） | 不属于（标注给开发） |
|---|---|
| 页面跳转（Overlay/Navigate To） | 粒子特效 |
| 元素淡入淡出（Opacity 过渡） | Spine 动画 |
| 弹窗弹出/收起（Scale 过渡） | 物理模拟 |
| 状态切换（Toggle/选中状态） | 复杂 3D 变换 |
| 序列帧动画（COMPONENT_SET 循环） | 着色器/后处理效果 |

---

## 二、原型连线 JSON 格式

### 2.1 顶层 prototype 字段结构

每个 screen 对象可包含 `prototype` 字段：

```json
{
  "id": "screen_main",
  "layers": [...],
  "prototype": {
    "flows": [
      {
        "trigger_node_id": "按钮_开始游戏",
        "action": "NAVIGATE",
        "destination": "screen_gameplay",
        "transition": {
          "type": "SMART_ANIMATE",
          "easing": "EASE_OUT",
          "duration_ms": 300
        }
      }
    ]
  }
}
```

### 2.2 支持的 Action 类型

| action | 说明 | 参数 |
|---|---|---|
| `NAVIGATE` | 跳转到另一个 screen | `destination`: screen id |
| `OVERLAY` | 叠加显示（弹窗） | `destination`: screen id |
| `CLOSE_OVERLAY` | 关闭当前浮层 | — |
| `BACK` | 返回上一页 | — |
| `CHANGE_TO` | 切换组件变体（COMPONENT_SET 内） | `variant_name`: 变体名 |

### 2.3 支持的 Trigger 类型

| trigger | Figma API 字段 | 说明 |
|---|---|---|
| 点击 | `ON_CLICK` | 普通交互 |
| 悬停 | `ON_HOVER` | PC 端 |
| 按住 | `ON_PRESS` | 长按 |
| 延时自动触发 | `AFTER_TIMEOUT` | 序列帧/自动跳转 |

---

## 三、关键规则（K / L / N）

### 规则 K：COMPONENT_SET 自动循环触发器字段名

**场景：** 时钟指针、加载动画、序列帧等自动循环的 COMPONENT_SET。

| 字段 | ❌ 错误 | ✅ 正确 |
|---|---|---|
| trigger type | `"AFTER_DELAY"` | `"AFTER_TIMEOUT"` |
| 延时字段 | `delay: 500` | `timeout: 0.5`（单位**秒**） |

**Elsa JSON 内部约定（与 Figma API 解耦）：**
- Elsa 输出 JSON 时写 `"delay_ms": 500`（毫秒），插件负责 `÷1000` 换算为秒
- 若直接写 Figma prototype interactions 格式，必须用秒（`timeout: 0.5`）

---

### 规则 L：AFTER_TIMEOUT.timeout 单位是**秒**，不是毫秒

```
❌ timeout: 1000  →  等待 1000 秒 = 277 小时
✅ timeout: 1.0   →  等待 1 秒
✅ timeout: 0.5   →  等待 500ms
```

**Elsa JSON 双字段约定：**
```json
"animation_trigger": "AFTER_DELAY",
"delay_ms": 500
```
插件读取 `delay_ms`，传给 Figma API 时 `÷1000 → timeout: 0.5`。

---

### 规则 N：旋转型动画（如时钟指针）必须用 `relativeTransform` 矩阵

#### 背景
时钟指针旋转动画在 Figma 中需要精确地绕**父 Frame 圆心**旋转。

#### 已废弃方案（禁止）
1. ~~宽高互换模拟旋转~~ → 变形不是旋转，尺寸语义错误
2. ~~包装 FRAME + rotation 字段~~ → 子节点坐标系随 FRAME 旋转，位置全错

#### 正确方案：`relativeTransform` 矩阵

每个方向状态直接计算旋转矩阵，注入到节点的 `relativeTransform` 字段。

**矩阵含义：**
```
relativeTransform = [[a, b, tx],
                     [c, d, ty]]
其中：
  a=cos θ, b=-sin θ
  c=sin θ, d=cos θ
  tx, ty = 旋转后的左上角绝对坐标（需从圆心反算）
```

**标准时钟案例（父 Frame cx=cy=34.5，针 w=7, h=30，针底对齐圆心）：**

| 方向 | θ | relativeTransform |
|---|---|---|
| 12点 | 0° | `[[1,0,31],[0,1,4.5]]` |
| 3点  | 90° | `[[0,-1,64.5],[1,0,31]]` |
| 6点  | 180° | `[[-1,0,38],[0,-1,64.5]]` |
| 9点  | 270° | `[[0,1,4.5],[-1,0,38]]` |

**通用公式（任意圆心 cx/cy，针尺寸 pw/ph）：**

```python
import math

def needle_transform(cx, cy, pw, ph, angle_deg):
    """计算时针在任意角度的 relativeTransform。
    angle_deg: 顺时针角度，0=12点
    cx, cy: 父Frame圆心坐标
    pw, ph: 针的宽高（12点朝上时 pw<ph）
    """
    θ = math.radians(angle_deg)
    cos_t, sin_t = math.cos(θ), math.sin(θ)

    # 12点时针中心相对圆心的偏移（针竖放，中心在 x=cx, y=cy-ph/2）
    ox = 0
    oy = -(ph / 2)  # 针中心在圆心正上方

    # 旋转后的针中心位置
    new_cx = cx + ox * cos_t - oy * sin_t
    new_cy = cy + ox * sin_t + oy * cos_t

    # 左上角 = 旋转后针中心 - 旋转后的半宽/半高
    # 但因针是旋转的，直接计算左上角的绝对坐标：
    # 旋转后宽方向变成 (cos_t, sin_t)，高方向变成 (-sin_t, cos_t)
    tx = new_cx - pw/2 * cos_t + ph/2 * sin_t
    ty = new_cy - pw/2 * sin_t - ph/2 * cos_t

    return [[round(cos_t,6), round(-sin_t,6), round(tx,3)],
            [round(sin_t,6), round( cos_t,6), round(ty,3)]]
```

---

## 四、序列帧动画 JSON 格式

### 4.1 COMPONENT_SET 结构（用于自动循环动画）

```json
{
  "name": "序列_时钟指针",
  "type": "COMPONENT_SET",
  "element_class": "state_driven",
  "x": 0, "y": 0, "w": 69, "h": 69,
  "auto_play": true,
  "loop": true,
  "animation_type": "sequence",
  "delay_ms": 1000,
  "variants": [
    {
      "name": "State=12点",
      "default": true,
      "transition_to": "State=3点",
      "layers": [
        {
          "name": "组_时钟指针",
          "type": "FRAME",
          "w": 7, "h": 30,
          "relativeTransform": [[1,0,31],[0,1,4.5]],
          "fill": "#FFFFFF"
        }
      ]
    },
    {
      "name": "State=3点",
      "transition_to": "State=6点",
      "layers": [...]
    }
  ]
}
```

### 4.2 自检清单（动画/原型专项）

```
【Elsa 动画自检报告】
✅/❌ 所有 COMPONENT_SET 变体有 transition_to（循环链闭合）
✅/❌ delay_ms 字段为毫秒整数（不是秒）
✅/❌ 时钟类旋转全部用 relativeTransform，无 w/h 互换
✅/❌ 页面跳转连线 destination 指向存在的 screen id
✅/❌ Overlay 弹窗有对应的 CLOSE_OVERLAY 出口连线
✅/❌ 自动播放序列帧有 auto_play: true, loop: true
```

---

## 五、常见动画模式速查

| 场景 | Figma 方案 | 参数示例 |
|---|---|---|
| 按钮点击反馈 | Scale 0.95→1，EASE_OUT | duration=80ms |
| 弹窗弹出 | Overlay + Scale 0.8→1，EASE_OUT | duration=300ms |
| 弹窗关闭 | Close Overlay + Scale 1→0.8，EASE_IN | duration=200ms |
| 页面滑入 | Navigate + 水平 Move In，EASE_OUT | duration=250ms |
| Loading 循环 | COMPONENT_SET AFTER_TIMEOUT | delay_ms=200 |
| 时钟/指针旋转 | COMPONENT_SET + relativeTransform | delay_ms=1000 |
| 倒计时数字 | data_driven（标注给开发，不在 Figma 范畴） | — |
