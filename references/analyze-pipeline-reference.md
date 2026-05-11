---
name: analyze-pipeline-reference
description: >
  Redream-project-gen 管线第 1 阶段参考资料：游戏录屏/截图 → Figma 低保真原型的 9 步分析方法论。
  被 guides/1-analyze-game.md 引用，提供骨架分析、组件库匹配、Figma MCP 绘制等完整技术栈。
---

# 游戏分析管线 参考资料（源自 elsa-analyzer-line，v1 2026-04-02）

将截图/录屏 → 直接在 Figma 中绘制低保真交互原型，遵循 Elsa 设计规范 + 低保真复刻规范 + 底板分离导出规范。

**与 elsa-analyzer 的区别：** 通过 Figma MCP `use_figma` 工具直接在 Figma 中创建节点，不再生成中间 JSON 文件。

---

# 一、核心原则（执行前必读，贯穿全流程）

## 1.1 两类节点的根本区分

**所有 Figma 节点只分两类，规则完全不同：**

| 类型 | 定义 | 底板分离要求 | 内部结构要求 |
|---|---|---|---|
| **component_ref 节点** | 元素属于组件库（可识别为库中某个组件） | **不适用** | **不管**，库内部结构由库自己负责 |
| **手搓节点** | 元素不属于任何组件库，需要从零构建 | **强制适用** | 必须遵守底板分离四层原则 |

**这是整个 skill 最重要的判断分支。识别到组件库元素时，立刻走 component_ref 路径，不再检查库内部结构。**

---

## 1.2 底板分离原则（仅适用于手搓节点）

凡**手搓**截图上的圆角/直角实心底板 + 其上排版内容（按钮、标签、横向信息卡/通知卡/礼物条、列表行、弹窗顶条等），**必须**在 Figma 中体现为物理分层：

| 层级 | 作用 | Figma 实现 |
|---|---|---|
| 大包装 `FRAME` | `layoutMode: NONE`，规定整体 `w/h`；**fills 为空 `[]`** | `figma.createFrame()`, `frame.fills = []` |
| `切图_底板_*` `FRAME` | `NONE`，与包装等大，`x:0, y:0`；**fills 为空 `[]`** | 同上 |
| `底板_形状` `RECTANGLE` | 放在切图 Frame 内部，承载实际颜色和圆角 | `figma.createRectangle()`, 设 `fills` 和 `cornerRadius` |
| 内容层 | 与 `切图_底板_*` **同级**。简单按钮为单层 TEXT；卡片/横条为 FRAME 内容区（HORIZONTAL/VERTICAL，**fills 为空**） | Auto Layout Frame |

---

## 1.3 零幻觉原则

绝不允许视觉创造、脑补或逻辑推断。唯一任务是对用户提供的图片进行高精度结构剥离与 1:1 物理复刻。**图里没有的元素，绝对不能在 Figma 中创建。**

---

## 1.4 全局尺寸规则

- 输出尺寸固定 **1080×2400**，无论素材实际分辨率
- 读取素材实际宽高 → `scale_x = 1080 / W`，`scale_y = 2400 / H`
- **所有坐标和尺寸必须从截图量测后乘以对应 scale，取整，不得估算，不得直接写量测像素值**
- 暗背景忽略：深色遮罩/弹窗底层统一替换为 `#E8E8E8`

---

## 1.5 比例还原原则

低保真稿和高保真图的每个元素，位置、比例、大小必须高度一致。

- 允许误差：±5%，超过说明量测有误，需重新计算
- 禁止为了避免重叠而压缩元素尺寸
- 禁止估算（"大概是 200px"）
- 如果各区域尺寸加总超过 2400，说明量测有误，重新量测

---

# 二、工作流（强制六步，不得跳步）

```
Step 0    → 全帧扫描（录屏专用）
Step 0.3  → 滚动菜单识别（录屏专用）
Step 0.5a → Python 辅助量测（客观基准）
Step 0.5  → 骨架分析（所有输入必须）
Step 1    → 组件库匹配与尺寸计算
Step 2    → 在 Figma 中绘制节点
Step 2.5  → 绘制后验证循环（像素级校验）
Step 3    → 自检输出
```

---

## Step 0 · 全帧扫描【录屏专用，强制】

若输入为 .mp4/.mov/.avi 等录屏：

1. 提取所有帧（2fps 捕捉触摸点）：
   - 优先：`ffmpeg -i input.mp4 -vf "fps=2" /tmp/frames/frame_%03d.png`
   - 回退（ffmpeg 不可用时）：使用 Python OpenCV：
     ```python
     import cv2, os
     os.makedirs('/tmp/frames', exist_ok=True)
     cap = cv2.VideoCapture('input.mp4')
     fps = cap.get(cv2.CAP_PROP_FPS)
     interval = int(fps / 2)  # 每秒取2帧
     idx, saved = 0, 0
     while cap.read()[0]:
         if idx % interval == 0:
             cv2.imwrite(f'/tmp/frames/frame_{saved:03d}.png', cap.read()[1])
             saved += 1
         idx += 1
     cap.release()
     ```
2. **逐帧查看全部帧，不得跳过**，记录每帧界面状态
3. **识别触摸点**（半透明白色小圆点）→ 确认点击位置对应的 UI 元素 → 写入 flow
4. 汇总唯一屏幕清单（帧差分 >40% 屏幕 → 独立屏幕；遮罩弹窗不算独立屏幕）
5. 播报："共 N 帧，识别到 M 个独立屏幕：[列表]，识别到 K 条交互连线：[列表]"
6. 确认清单后才进入 Step 0.3

**禁止：** 看前几帧就开始绘制；跳帧。

### 0.1 翻页类型识别（帧扫描时同步判断）

扫描每一次画面切换时，同步判断切换类型，记录到连线清单中：

| 识别特征 | 切换类型 | 后续动画 |
|---|---|---|
| 过渡帧中**两个屏幕同时可见**，内容区横向位移，导航栏不动 | Tab 导航切换 | `slide 300ms` |
| 触摸点在**内容区按钮**，切换后界面结构完全不同 | 全屏页面跳转 | `dissolve 300ms` |
| 切换后**原屏幕内容仍可见**（变暗），新内容浮在上方 | 弹窗/浮层打开 | `dissolve 300ms` |
| 触摸点在浮层上的关闭按钮，回到原屏幕 | 浮层关闭 | 省略 animation |
| 触摸点不清晰，但底部 Nav 高亮 Tab 发生变化 | 推断为 Tab 切换 | `slide 300ms` |

---

## Step 0.3 · 滚动菜单识别【录屏专用，强制】

当视频中出现列表/网格上下滚动时，必须先完成"滚动容器识别"，再进入骨架分析。

### 0.3.1 识别滚动区（谁在动，谁不动）

逐帧比对同一屏幕连续帧，先标注三类区域：

1. **固定区（不动）**：顶部标题/HUD、底部导航、全局浮层按钮等。
2. **滚动区（在动）**：列表卡片区、三列菜单网格区、排行榜条目区等。
3. **遮挡/裁切边界（Viewport）**：滚动内容可见窗口的上/下边界。

### 0.3.2 识别滚动方向与滚动单元

根据连续帧中元素位移方向判定：
- 纵向位移为主 → `scrollDirection = VERTICAL`
- 横向位移为主 → `scrollDirection = HORIZONTAL`

### 0.3.3 锚点帧与可见范围记录

每个滚动区至少记录三组锚点：anchor_start / anchor_mid / anchor_end

---

## Step 0.5a · Python 辅助量测【强制，骨架分析前必须执行】

在骨架分析之前，用 Python 图像处理提供客观的量测基准。**禁止跳过此步直接目测。**

### 0.5a.1 水平边界检测（找大区域分割线）

```python
from PIL import Image, ImageDraw
import numpy as np

def detect_horizontal_boundaries(image_path):
    """检测截图中的水平分割线，找出大区域边界的 y 坐标"""
    img = np.array(Image.open(image_path).convert('L')).astype(float)
    h, w = img.shape

    # 计算相邻行的亮度差
    row_mean = np.mean(img, axis=1)
    row_diff = np.abs(np.diff(row_mean))

    # 差异大于阈值的行 = 区域边界候选
    threshold = np.percentile(row_diff, 95)
    boundary_rows = np.where(row_diff > threshold)[0]

    # 聚类相邻的边界行（合并 5px 内的）
    if len(boundary_rows) == 0:
        return [], h, w
    clusters = []
    current = [boundary_rows[0]]
    for i in range(1, len(boundary_rows)):
        if boundary_rows[i] - boundary_rows[i-1] <= 5:
            current.append(boundary_rows[i])
        else:
            clusters.append(int(np.mean(current)))
            current = [boundary_rows[i]]
    clusters.append(int(np.mean(current)))

    return clusters, h, w

boundaries, src_h, src_w = detect_horizontal_boundaries('/tmp/frames/frame_001.png')
scale_x = 1080 / src_w
scale_y = 2400 / src_h
scaled_boundaries = [int(b * scale_y) for b in boundaries]
print(f"原图 {src_w}x{src_h}, scale_x={scale_x:.4f}, scale_y={scale_y:.4f}")
print(f"大区域边界 y (缩放后): {scaled_boundaries}")
```

### 0.5a.2 局部裁切分析（找内部元素 BBox）

对每个大区域单独裁切后做边缘检测，获取内部元素的 bounding box：

```python
from scipy import ndimage

def analyze_region_elements(image_path, y_start, y_end):
    """裁切区域并检测内部元素边界"""
    img = np.array(Image.open(image_path))
    region = img[y_start:y_end, :, :]
    gray = np.mean(region, axis=2)

    # Sobel 边缘检测
    edges = np.hypot(ndimage.sobel(gray, axis=0), ndimage.sobel(gray, axis=1))
    binary = (edges > np.percentile(edges, 90)).astype(np.uint8)

    # 连通域分析
    labeled, num = ndimage.label(binary)
    bboxes = ndimage.find_objects(labeled)

    results = []
    for bbox in bboxes:
        if bbox is None: continue
        y_slice, x_slice = bbox
        bw, bh = x_slice.stop - x_slice.start, y_slice.stop - y_slice.start
        if bw > 20 and bh > 20:  # 过滤噪声
            results.append({
                'x': x_slice.start, 'y': y_start + y_slice.start,
                'w': bw, 'h': bh
            })
    return results
```

### 0.5a.3 标注图验证

将检测结果叠加到原图上，供 AI 视觉核对：

```python
def overlay_annotations(image_path, boundaries, element_bboxes, output_path):
    """在截图上叠加检测结果，生成标注图"""
    img = Image.open(image_path).copy()
    draw = ImageDraw.Draw(img)

    # 画水平分割线（红色）
    for y in boundaries:
        draw.line([(0, y), (img.width, y)], fill='red', width=2)
        draw.text((5, y + 2), f'y={y}', fill='red')

    # 画元素边框（绿色）
    for i, box in enumerate(element_bboxes):
        x, y, w, h = box['x'], box['y'], box['w'], box['h']
        draw.rectangle([(x, y), (x + w, y + h)], outline='lime', width=2)
        draw.text((x, y - 12), f'{i}: {w}x{h}', fill='lime')

    img.save(output_path)
    return output_path
```

### 0.5a.4 执行流程

1. 对每个独立屏幕的代表帧执行 `detect_horizontal_boundaries()`
2. 对每个大区域执行 `analyze_region_elements()`
3. 执行 `overlay_annotations()` 生成标注图 `/tmp/annotated_屏幕名.png`
4. **阅读标注图**，验证 Python 检测结果是否与视觉判断一致
5. 一致 → 使用 Python 值填写骨架表
6. 不一致 → 以 Python 值为基准，AI 微调（**偏差不得超过 ±2%**）
7. 骨架表中每个数值标注来源：`P`（Python）、`A`（AI 判断）、`P+A`（Python+AI 微调）

**禁止：** 跳过 Python 量测直接目测写坐标；AI 调整幅度超过 Python 值的 ±2%（除非有明确理由并记录）。

---

## Step 0.5 · 骨架分析【强制，绘制前必须完成】

在绘制任何 Figma 节点之前，必须先完成骨架分析并输出骨架表格。

### 执行流程（四步强制）

**第一步：测算原子控件边界点（Bounding Box）**
以 Step 0.5a 的 Python 检测结果为基准，确认每个可见元素的边界坐标 `[x, y, w, h]`。

**第二步：基于坐标的物理分组与嵌套（找关系）**
- **包含判定：** 若文字/图标边界完全落在某个色块边界内部，则色块为底板，建立大包装 Frame。
- **对齐判定（计分法）：** 不再用简单的"中心点对齐"规则，改用以下计分法：

| 特征 | HORIZONTAL 得分 | VERTICAL 得分 |
|---|---|---|
| Y 中心点方差 < 元素平均高 × 15% | +3 | — |
| X 排列单调递增 | +2 | — |
| X 间距变异系数 < 0.3 | +1 | — |
| X 中心点方差 < 元素平均宽 × 15% | — | +3 |
| Y 排列单调递增 | — | +2 |
| Y 间距变异系数 < 0.3 | — | +1 |

  - 得分 ≥ 4 且高于另一方 → 采用该 layoutMode
  - 两方得分均 < 4 → NONE（自由布局）
  - 推断为 HORIZONTAL/VERTICAL 时，同时计算 **itemSpacing = 子元素间距中位数**

- **散落画布豁免（地图例外）：** 自由地图区域绝对禁止强行用 HORIZONTAL/VERTICAL 收编。

**第三步：以"组"为单位的宏观定位与锁高**
- 将屏幕切分为顶区（y=0起）、底区（y=2400往上）和中间内容区。

**第四步：标注组件库匹配 + 输出坐标系骨架树**

### 区域类型识别表

| 区域类型 | 特征 | 布局方式 | constraints (API值) |
|---|---|---|---|
| 顶部状态栏 | 贴顶，全宽 | HORIZONTAL, w=1080, 固定高 | SCALE + MIN（贴顶） |
| 底部导航栏 | 贴底，全宽 | HORIZONTAL, w=1080, 固定高 | SCALE + MAX（贴底） |
| 内容滚动区 | 中间大面积 | VERTICAL, w=1080, 弹性高 | SCALE + MIN |
| 地图内容区 | 自由布局 | NONE, w=1080, 固定高 | SCALE + MIN |
| 弹窗主体 | 居中浮层 | NONE, 固定宽高 | CENTER + CENTER |

### 骨架表格输出格式（强制带序号 + 量测审计）

```
【骨架分析】界面_主地图
原图尺寸: 576×1280, scale_x=1.875, scale_y=1.875

序号 | 区域名称        | 原图y | 原图h | ×sy   | 输出y | 输出h | layoutMode | 来源
-----|----------------|-------|-------|-------|-------|-------|------------|-----
1    | 面板_顶部HUD    | 0     | 93    | ×1.875| 0     | 174   | HORIZONTAL | P
2    | 面板_地图内容   | 93    | 1017  | ×1.875| 174   | 1907  | NONE       | P+A
3    | 面板_底部导航   | 1110  | 85    | ×1.875| 2241  | 159   | HORIZONTAL | P
                                                        合计:   2400  ✅

来源: P=Python检测, A=AI判断, P+A=Python初值+AI微调(幅度≤±2%)
```

### 骨架 y 坐标计算顺序（强制）

```
① 贴顶区域：从 y=0 往下叠加
② 贴底区域：从 y=2400 往上叠加
③ 中间内容区：h = 贴底起始y - 贴顶结束y
```

**禁止：** 从上往下一路叠加估算 y，导致底部区域和导航栏重叠。

### 约束传播检查（强制 5 项，全部通过才能进入 Step 1）

```
规则 P-1 相邻区域 y 连续:
  R[i].y + R[i].h == R[i+1].y
  → 违反则重新量测相关区域

规则 P-2 大区域 h 加总 = 2400:
  sum(R[i].h) == 2400
  → 违反则找出最大偏差区域重新量测

规则 P-3 子元素不溢出父元素:
  child.x >= 0 且 child.x + child.w <= parent.w
  child.y >= 0 且 child.y + child.h <= parent.h
  → 违反则缩小子元素或检查量测

规则 P-4 对称性检查:
  若两个元素关于屏幕中轴对称:
  abs((x1 + w1/2) + (x2 + w2/2) - 1080) < 1080 × 0.02
  → 违反则微调 x 使对称

规则 P-5 同类元素等尺寸:
  同类控件的 w/h 方差 < 5%
  → 违反则取中位数统一尺寸
```

### 骨架验证汇总（强制输出）

```
【骨架验证】界面_主地图
P-1 相邻 y 连续: 0+174=174 ✅ | 174+1907=2081 ✅ (注:贴底区从2400算)
P-2 h 加总=2400: 174+1907+159=2240 ❌ → 重新量测中间区域
P-3 子元素不溢出: 全部通过 ✅
P-4 对称性: N/A
P-5 同类等尺寸: N/A
```

---

## Step 1 · 组件库匹配与尺寸计算

### 1.1 识别规则（按顺序判断）

**看整体形状：**
- 椭圆头像区 + 底部时间条 → `椭圆按钮_活动`
- 正圆 + 单图标 → `圆形按钮_xxx`
- 圆角方形 + 消息气泡 → `方形按钮_消息_激活/禁用`
- 横向圆角矩形 + 文字 → 进入下一步

**看内部结构（条状组件）：**
- 只有文字 → `矩形按钮_纯文本`
- 胶囊条 + 进度数字（短）→ `进度条_短`
- 宽胶囊条 + 进度数字 → `进度条_宽`
- 圆角矩形 + 时间（无时钟图标）→ `底标_时间`
- 圆角矩形 + 时间（有时钟图标）→ `底标_倒计时`

**看叠加附件（ABSOLUTE）：**
- 右上角小圆形 + ! → `角标_感叹号`
- 右上角矩形 + ×2 → `角标_倍数`
- 圆形 + icon 占位 → `圆形容器_图标`
- 好友头像框 → `头像_朋友`

### 1.2 可拉伸组件（5个）

| 组件名 | 原始尺寸 | 文字节点 |
|---|---|---|
| `矩形按钮_纯文本` | 265×127 | `文本_主` |
| `底标_时间` | 173×71 | `文本_时间` |
| `底标_倒计时` | 134×33 | `文本_时间` |
| `进度条_短` | 170×34 | `进度条_文本` |
| `进度条_宽` | 413×61 | `文本_进度` |

**尺寸规则：** `w = 截图测量宽 × scale_x`，`h = 截图测量高 × scale_y`，直接写入。

### 1.3 不可拉伸组件（18个）

| 组件名 | 原始尺寸 |
|---|---|
| `圆形按钮_关闭` / `退出` / `设置` / `信息` / `播放_激活` / `播放_禁用` / `加_激活` / `加_禁用` | 185×185 |
| `方形按钮_消息_激活` / `消息_禁用` | 165×158 |
| `角标_感叹号` | 49×51 |
| `角标_倍数` | 69×84 |
| `圆形容器_图标` | 75×75 |
| `椭圆按钮_活动` | 251×291 |
| `活动按钮_进度标签` | 110×56 |
| `头像_朋友` | 107×114 |
| `图标_金币` | 66×66 |
| `图标_锁` | 76×76 |

**尺寸规则：** 等比缩放 `缩放比 = 截图测量高 × scale_y ÷ 原始h`，`实际w = 原始w × 缩放比`。

```
缩放后 ≥ 原始尺寸 → 直接写缩放后的 w/h
缩放后 < 原始尺寸 → 写原始尺寸（Figma 不允许实例缩小到比主组件更小）
```

### 1.4 component_ref 在 Figma 中的实现

在直接绘制模式下，组件库引用通过 Figma Plugin API 实现：

```javascript
// 在目标 page 中查找组件库中的组件
const componentSet = figma.root.findOne(n => n.type === 'COMPONENT_SET' && n.name === '矩形按钮_纯文本');
// 或者查找单个 Component
const component = figma.root.findOne(n => n.type === 'COMPONENT' && n.name === '圆形按钮_设置');

if (component) {
  const instance = component.createInstance();
  instance.resize(w, h);
  instance.x = x;
  instance.y = y;
  // 设置文字 overrides
  const textNode = instance.findOne(n => n.type === 'TEXT' && n.name === '文本_主');
  if (textNode) {
    await figma.loadFontAsync(textNode.fontName);
    textNode.characters = '按钮文字';
  }
}
```

**兜底原则：** 无法找到组件时，走手搓路径。宁可手搓，不可错误引用。

### 1.5 尺寸计算表（每次绘制前必须列出，含完整计算过程）

**禁止直接写最终值。** 每个元素必须展示：原图量测 → ×scale → 取整 → 边界验证。

```
【尺寸计算表】界面_主页

元素名称         | 类型     | 原图x | 原图y | 原图w | 原图h | ×sx    | ×sy    | 输出x | 输出y | 输出w | 输出h | 边界检查           | 来源
-----------------|----------|-------|-------|-------|-------|--------|--------|-------|-------|-------|-------|--------------------|-----
面板_顶部HUD     | 手搓     | 0     | 0     | 576   | 93    | ×1.875 | ×1.875 | 0     | 0     | 1080  | 174   | 0+1080≤1080✅ 0+174≤2400✅ | P
按钮_设置        | 不可拉伸 | 510   | 15    | 55    | 55    | ×1.875 | ×1.875 | 956   | 28    | 103   | 103   | 103<185→写185×185  | P+A
矩形按钮_开始    | 可拉伸   | 125   | 960   | 326   | 80    | ×1.875 | ×1.875 | 234   | 1800  | 611   | 150   | 234+611=845≤1080✅ | P

不可拉伸组件尺寸计算:
  按钮_设置: 缩放比 = 103/185 = 0.557, 缩放后 103×103 < 原始 185×185 → 写原始尺寸
```

---

## Step 2 · 在 Figma 中绘制节点

### 2.1 绘制入口

通过 `use_figma` MCP 工具执行 Figma Plugin API 代码，在指定 page 中创建所有节点。

**绘制顺序：**
1. 先创建所有屏幕的根 Frame（1080×2400）
2. 按屏幕逐个绘制内部节点（自底向顶：底板在前，内容在后）
3. 最后设置 Prototype 交互连线

### 2.2 Figma 节点创建代码模板

#### 创建屏幕根 Frame

```javascript
// 切换到目标 page
const targetPage = figma.root.children.find(p => p.id === 'PAGE_ID');
await figma.setCurrentPageAsync(targetPage);

// 创建屏幕 Frame
const screen = figma.createFrame();
screen.name = '界面_主页';
screen.resize(1080, 2400);
screen.x = 0; // 多屏幕时横向排列，间距 200
screen.y = 0;
screen.fills = [{ type: 'SOLID', color: { r: 0.91, g: 0.91, b: 0.91 } }]; // #E8E8E8
screen.clipsContent = true;
```

#### 创建手搓 FRAME 节点

```javascript
const frame = figma.createFrame();
frame.name = '面板_顶部HUD';
frame.resize(1080, 178);
frame.x = 0;
frame.y = 0;
frame.fills = []; // FRAME 禁止 fill
frame.clipsContent = false;

// Auto Layout 设置
frame.layoutMode = 'HORIZONTAL';
frame.primaryAxisSizingMode = 'FIXED';
frame.counterAxisSizingMode = 'FIXED';
frame.primaryAxisAlignItems = 'MIN';
frame.counterAxisAlignItems = 'CENTER';
frame.paddingLeft = 16;
frame.paddingRight = 16;
frame.itemSpacing = 12;

// Constraints（仅在 NONE 父容器或屏幕顶层时设置）
frame.constraints = { horizontal: 'SCALE', vertical: 'MIN' }; // MIN=贴顶, MAX=贴底, CENTER=居中

// 添加到父节点
parentFrame.appendChild(frame);
```

#### 创建 RECTANGLE 节点

```javascript
const rect = figma.createRectangle();
rect.name = '底板_形状';
rect.resize(1008, 120);
rect.x = 0;
rect.y = 0;
rect.cornerRadius = 20;
// 颜色设置 - hex 转 RGB (0~1)
rect.fills = [{ type: 'SOLID', color: { r: 0x88/255, g: 0x88/255, b: 0x88/255 } }]; // #888888
parentFrame.appendChild(rect);
```

#### 创建 TEXT 节点

```javascript
const text = figma.createText();
text.name = '文字_标题';
await figma.loadFontAsync({ family: 'Inter', style: 'Regular' });
text.characters = '标题文字';
text.fontSize = 32;
text.fills = [{ type: 'SOLID', color: { r: 0.1, g: 0.1, b: 0.1 } }]; // #1A1A1A
// 居中文字
text.textAlignHorizontal = 'CENTER';
text.textAlignVertical = 'CENTER';
// 不手动设置宽度，让 TEXT 自适应（除非有固定宽度约束）
parentFrame.appendChild(text);
```

#### 创建底板分离结构（手搓按钮示例）

```javascript
// 大包装 FRAME
const wrapper = figma.createFrame();
wrapper.name = '卡片_通知_示例';
wrapper.resize(1008, 120);
wrapper.layoutMode = 'NONE';
wrapper.fills = [];
wrapper.clipsContent = false;

// 切图底板 FRAME
const bgFrame = figma.createFrame();
bgFrame.name = '切图_底板_卡片';
bgFrame.resize(1008, 120);
bgFrame.x = 0; bgFrame.y = 0;
bgFrame.layoutMode = 'NONE';
bgFrame.fills = [];
wrapper.appendChild(bgFrame);

// 底板形状 RECTANGLE
const bgRect = figma.createRectangle();
bgRect.name = '底板_形状';
bgRect.resize(1008, 120);
bgRect.x = 0; bgRect.y = 0;
bgRect.cornerRadius = 20;
bgRect.fills = [{ type: 'SOLID', color: { r: 0x88/255, g: 0x88/255, b: 0x88/255 } }];
bgFrame.appendChild(bgRect);

// 内容区 FRAME（与切图底板同级）
const contentFrame = figma.createFrame();
contentFrame.name = '内容区_卡片';
contentFrame.resize(1008, 120);
contentFrame.x = 0; contentFrame.y = 0;
contentFrame.layoutMode = 'HORIZONTAL';
contentFrame.primaryAxisSizingMode = 'FIXED';
contentFrame.counterAxisSizingMode = 'FIXED';
contentFrame.primaryAxisAlignItems = 'MIN';
contentFrame.counterAxisAlignItems = 'CENTER';
contentFrame.paddingLeft = 16;
contentFrame.paddingRight = 16;
contentFrame.itemSpacing = 16;
contentFrame.fills = [];
wrapper.appendChild(contentFrame);
```

### 2.3 颜色工具函数

在每次 `use_figma` 调用中包含此工具函数：

```javascript
function hexToRgb(hex) {
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;
  return { r, g, b };
}

function solidFill(hex) {
  return [{ type: 'SOLID', color: hexToRgb(hex) }];
}
```

### 2.4 constraints 规则

**三种场景，规则完全不同：**

| 场景 | constraints | Figma API |
|---|---|---|
| 屏幕顶层区域 | **必须写** | `node.constraints = { horizontal: 'SCALE', vertical: 'MIN' }` |
| `NONE` 父容器的子节点 | **必须写** | 同上 |
| `HORIZONTAL` / `VERTICAL` 父容器的子节点 | **不写** | 不设置 constraints |

**常用对照表（Figma API 枚举值）：**

| 元素类型 | horizontal | vertical | 语义 |
|---|---|---|---|
| 全屏背景/遮罩 | SCALE | SCALE | 随屏幕拉伸 |
| 弹窗 Frame | CENTER | CENTER | 居中 |
| 标题栏/顶部面板 | SCALE | MIN | 贴顶 |
| 屏底面板/导航栏 | SCALE | MAX | 贴底 |

> **API 枚举对照：** `MIN`=贴顶/贴左，`MAX`=贴底/贴右，`CENTER`=居中，`SCALE`=拉伸。Figma Plugin API **不接受** `TOP`/`BOTTOM`/`LEFT`/`RIGHT`。

### 2.5 布局规范（Auto Layout）

#### 合法属性值速查

| 属性 | 合法值 | 非法值 |
|---|---|---|
| `primaryAxisAlignItems` | MIN / MAX / CENTER / SPACE_BETWEEN | ~~SPACE_AROUND~~ |
| `counterAxisAlignItems` | MIN / MAX / CENTER / BASELINE | ~~STRETCH~~ |
| `layoutSizingHorizontal` | FIXED / HUG / FILL | |
| `layoutSizingVertical` | FIXED / HUG / FILL | |
| `layoutMode` | HORIZONTAL / VERTICAL / NONE | |
| `primaryAxisSizingMode` | FIXED / AUTO | ~~HUG~~ ~~FILL~~ |
| `counterAxisSizingMode` | FIXED / AUTO | ~~HUG~~ ~~FILL~~ |

#### 弹性缝隙（推送按钮到末端）

```javascript
const spacer = figma.createFrame();
spacer.name = '弹性缝隙';
spacer.fills = [];
spacer.layoutMode = 'NONE';
spacer.resize(1, 1); // 最小尺寸，FILL 会自动撑开
parentFrame.appendChild(spacer); // 必须先 appendChild 到 AL 父容器
spacer.layoutSizingHorizontal = 'FILL'; // 然后才能设 layoutSizing
```

### 2.6 命名规范

参见 `references/naming.md`。核心前缀：

```
界面_  弹窗_  浮层_                              ← 顶层 Frame
面板_  按钮_  标签_  列表区域_  列表容器_  列表项_  ← 内部容器
底板_  文字_  图标_  图片_  遮罩_                 ← 视觉节点
组_  道具_  内容_  内容区_  底板Frame_  切图_      ← 组织/导出容器
```

### 2.7 灰度色板

| 色值 | 用途 | 层级 |
|---|---|---|
| `#E8E8E8` | 页面背景、暗背景替换 | 第 0 层 |
| `#C8C8C8` | 大区域底板（顶部栏、底部导航） | 第 1 层 |
| `#A8A8A8` | 卡片、列表项底板 | 第 2 层 |
| `#888888` | 按钮底色、控件底板 | 第 3 层 |
| `#606060` | 强调按钮、激活状态 | 第 4 层 |
| `#444444` | 深色强调 | 第 5 层 |
| `#BEBEBE` | 图片/插图 RECTANGLE 占位 | 专用 |

**文字色：**
- 浅底板（≤ `#A8A8A8`）上 → `#1A1A1A`
- 深底板（≥ `#888888`）上 → `#FFFFFF`
- 次要说明文字 → `#444444`

### 2.8 Prototype 交互连线

在所有屏幕绘制完成后，通过 Figma Plugin API 设置 Prototype 连线：

```javascript
// 页面跳转（dissolve）
const sourceNode = screen1.findOne(n => n.name === '按钮_开始');
const targetScreen = figma.root.findOne(n => n.name === '界面_游戏');

if (sourceNode && targetScreen) {
  sourceNode.reactions = [{
    trigger: { type: 'ON_CLICK' },
    actions: [{
      type: 'NODE',
      destinationId: targetScreen.id,
      navigation: 'NAVIGATE',
      transition: {
        type: 'DISSOLVE',
        duration: 0.3,
        easing: { type: 'EASE_IN_AND_OUT' }
      }
    }]
  }];
}

// Tab 切换（slide / smart animate）
sourceNode.reactions = [{
  trigger: { type: 'ON_CLICK' },
  actions: [{
    type: 'NODE',
    destinationId: targetScreen.id,
    navigation: 'NAVIGATE',
    transition: {
      type: 'SMART_ANIMATE',
      duration: 0.3,
      easing: { type: 'EASE_IN_AND_OUT' }
    }
  }]
}];

// 弹窗打开（overlay）
sourceNode.reactions = [{
  trigger: { type: 'ON_CLICK' },
  actions: [{
    type: 'NODE',
    destinationId: overlayScreen.id,
    navigation: 'OVERLAY',
    transition: {
      type: 'DISSOLVE',
      duration: 0.3,
      easing: { type: 'EASE_IN_AND_OUT' }
    }
  }]
}];

// 弹窗关闭
closeButton.reactions = [{
  trigger: { type: 'ON_CLICK' },
  actions: [{
    type: 'BACK'
  }]
}];
```

### 2.9 滚动容器

```javascript
// 外层视口
const viewport = figma.createFrame();
viewport.name = '列表区域_奖励';
viewport.resize(848, 1200);
viewport.layoutMode = 'VERTICAL';
viewport.primaryAxisSizingMode = 'FIXED';
viewport.counterAxisSizingMode = 'FIXED';
viewport.clipsContent = true;
viewport.overflowDirection = 'VERTICAL'; // 启用垂直滚动
viewport.fills = [];

// 内层内容容器（高度超出视口）
const content = figma.createFrame();
content.name = '列表容器_奖励';
content.resize(848, 1800); // 高度 > 视口高度
content.layoutMode = 'VERTICAL';
content.primaryAxisSizingMode = 'AUTO';
content.counterAxisSizingMode = 'FIXED';
content.itemSpacing = 8;
content.fills = [];
viewport.appendChild(content);
```

---

## Step 2.5 · 绘制验证循环【强制，最多 3 轮】

在所有屏幕绘制完成后、进入 Step 3 之前，执行像素级验证。

### 2.5.1 截取绘制结果

使用 `get_screenshot` MCP 工具截取每个屏幕 Frame 的截图。

### 2.5.2 差分分析

用 Python 对比原图（resize 到 1080×2400）与 Figma 截图：

```python
from PIL import Image
import numpy as np
from scipy import ndimage

def compare_layouts(original_path, figma_screenshot_path):
    """比较原图与 Figma 绘制结果的结构差异"""
    original = np.array(Image.open(original_path).resize((1080, 2400)).convert('L')).astype(float)
    figma = np.array(Image.open(figma_screenshot_path).convert('L')).astype(float)

    # 对两张图做边缘检测
    orig_edges = np.hypot(ndimage.sobel(original, axis=0), ndimage.sobel(original, axis=1))
    fig_edges = np.hypot(ndimage.sobel(figma, axis=0), ndimage.sobel(figma, axis=1))

    orig_binary = (orig_edges > np.percentile(orig_edges, 85)).astype(np.uint8)
    fig_binary = (fig_edges > np.percentile(fig_edges, 85)).astype(np.uint8)

    # 按 120px 纵向带统计
    band_h = 120
    deviations = []
    for band_start in range(0, 2400, band_h):
        band_end = min(band_start + band_h, 2400)
        orig_band = orig_binary[band_start:band_end, :]
        fig_band = fig_binary[band_start:band_end, :]

        orig_density = orig_band.sum()
        fig_density = fig_band.sum()
        density_ratio = fig_density / max(orig_density, 1)

        # 边缘重心水平偏移
        h_offset = 0
        orig_cols = np.where(orig_band > 0)
        fig_cols = np.where(fig_band > 0)
        if len(orig_cols[1]) > 0 and len(fig_cols[1]) > 0:
            h_offset = abs(orig_cols[1].mean() - fig_cols[1].mean())

        deviations.append({
            'y_range': f'{band_start}-{band_end}',
            'density_ratio': round(density_ratio, 2),
            'h_offset_px': round(h_offset, 1),
            'pass': 0.4 < density_ratio < 2.5 and h_offset < 40
        })

    pass_count = sum(1 for d in deviations if d['pass'])
    pass_rate = pass_count / len(deviations)
    problem_zones = [d['y_range'] for d in deviations if not d['pass']]

    return deviations, pass_rate, problem_zones
```

### 2.5.3 验证报告格式

```
【验证报告】界面_主页 — 第 1 轮

区域         | 密度比  | 水平偏移 | 状态
0-120        |   1.05  |   3.2px  | ✅ 通过
120-240      |   0.42  |  45.1px  | ❌ 需修正
240-360      |   0.98  |   5.0px  | ✅ 通过
...
通过率: 85% (17/20)
问题区域: ['120-240', '960-1080']
```

### 2.5.4 修正流程

1. 通过率 ≥ 90% → 验证通过，进入 Step 3
2. 通过率 < 90% → 对每个问题区域：
   a. 裁切原图中该 y 范围的区域
   b. 重新分析该区域内元素的坐标和结构
   c. 用 `use_figma` 修正对应节点的 x/y/w/h（仅修正问题区域，不动已通过区域）
3. 修正后重新截图验证（回到 2.5.1）
4. **最多 3 轮修正。** 3 轮后仍未通过 → 在自检报告中标注未通过区域和偏差值，继续执行 Step 3

---

## Step 3 · 自检（绘制完成后逐项核对）

### 【第一层：骨架完整性】
- Step 0 全帧扫描完成（含触摸点识别与翻页类型判断）
- Step 0.3 滚动菜单识别完成
- Step 0.5 骨架表格已输出
- 骨架无重叠：所有相邻区域 (y+h) ≤ 下方区域 y
- 贴底区域从下往上计算 y
- 所有大区 h 加总 = 2400

### 【第二层：尺寸精度】
- 所有 w/h/x/y 从截图量测后 × scale
- 同组控件尺寸一致

### 【第三层：组件合规性】
- 识别到库组件 → 用 createInstance()，未退化为手搓
- 可拉伸组件：截图量测 × scale 直接 resize
- 不可拉伸组件：缩放后≥原始写缩放值；缩放后<原始写原始尺寸

### 【第四层：手搓节点底板分离】
- 凡手搓的实心底板块：包装 NONE + 切图_Frame + 底板_形状 RECTANGLE + 内容区
- FRAME 的 fills 全部为 `[]`
- 底板_形状 RECTANGLE 才设 fills 和 cornerRadius

### 【第五层：Auto Layout 合规性】
- 所有 FRAME 设置了 layoutMode
- primaryAxisSizingMode / counterAxisSizingMode 只用 FIXED / AUTO
- HORIZONTAL 容器 counterAxisAlignItems: CENTER
- AL 子节点不写 constraints；NONE 子节点写 constraints

### 【第六层：视觉质感】
- 无 stroke
- 相邻嵌套层级灰度明显跳跃（差值 ≥ 30）
- children 添加顺序自底向顶
- 居中文字设 textAlignHorizontal: CENTER + textAlignVertical: CENTER
- 零幻觉：Figma 中无截图未出现的元素

### 【第七层：Prototype 连线】
- 所有触摸点已识别并设置 reactions
- Tab 切换用 SMART_ANIMATE，页面跳转用 DISSOLVE
- 弹窗用 OVERLAY + DISSOLVE，关闭用 BACK

### 【第八层：Overflow 滚动】
- 滚动视口 clipsContent = true
- 滚动视口 overflowDirection 已设置
- 内容容器高度 > 视口高度
- 内容容器是视口的直接 child

### 【第九层：量测精度与参考对比】
- Step 0.5a Python 辅助量测已执行，标注图已生成并核对
- 骨架表每个值标注来源（P / A / P+A），Python 值占比 ≥ 60%
- AI 调整幅度未超过 Python 基准的 ±2%
- 约束传播 5 项检查全部通过（P-1 ~ P-5）
- Step 1 尺寸计算表包含完整计算链（原图量测 → ×scale → 取整）
- Step 2.5 验证循环通过率 ≥ 90%（或已完成最多 3 轮修正）
- 最终 Figma 截图与原图的边缘密度偏差 < 10%
