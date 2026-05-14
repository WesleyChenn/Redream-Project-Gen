# scene.json schema + 节点结构 + 坐标

> 引擎 SKILL 拆分文档(v20.7.x+,2026-05-11) · 索引见 SKILL.md

---

## 三、scene.json 数据结构（v20.6 schema）

### 顶层结构

```json
{
  "meta": { "design_size": { "w": 1080, "h": 2400 } },
  "components": [...],   // 子 CCB 定义列表
  "screens": [...],      // 主场景列表
  "flow": [...]          // V1 不消费，保留兼容
}
```

### Component Set（components 数组项）

```json
{
  "name": "排行榜行",
  "w": 997, "h": 203,
  "property_name": "状态",
  "variants": [
    {
      "name": "常态",
      "is_default": true,
      "layers": [...]       // 完整节点列表
    },
    { "name": "带徽章", "layers": [...] },
    { "name": "带道具", "layers": [...] }
  ]
}
```

### INSTANCE 节点（screens.layers 内引用 Component）

```json
{
  "type": "INSTANCE",
  "name": "列表项_排名6",        // → reboltName / displayName
  "component_name": "排行榜行",   // → redFile 路径解析
  "variant": "当前用户",          // V1 不消费，等行为树接入
  "x": 50, "y": 800,
  "w": 200, "h": 200,
  "constraints": { "horizontal": "LEFT", "vertical": "TOP" },
  "visible": true
}
```

### component_ref 节点（老体系组件库引用）

```json
{
  "component_ref": "椭圆按钮_活动",
  "name": "活动_花朵",
  "x": 854, "y": 395, "w": 198, "h": 175,
  "constraints": {...}
}
```

V1 处理：**生成空 CCNode 占位**（位置和尺寸正确，内部空白）。原因：scene.json 没有 children 字段，Figma 组件库不规范暂不展开。

---

## 四、节点结构规范（v16+）

### 主场景标准结构

```
CCLayer
└── 总组 (CCNode 100%×100%, 固定 displayName="总组")
    ├── 组_背景层 (CCNode 100%×100%)        ← scene_kids[0]
    │   ├── 全屏防点击穿透层 (REDNodeButton 100%×100%)
    │   └── 背景_XXX (CCSprite 100%×100%, 仅界面_有)
    ├── 遮罩_背景 (CCLayerColor 100%×100% opacity=178 黑, 仅浮层_有)
    ├── 中间内容（弹窗/卡片等）
    ├── 组_顶部合并 (多个 TOP 节点合并后) 或 单独 TOP 节点
    └── 组_底部合并 (多个 BOTTOM 节点合并后) 或 单独 BOTTOM 节点
```

### 子 CCB 标准结构（Component → 子 CCB）

```
CCNode（根，控件原始尺寸，displayName = 组件名如"排行榜行"）
└── 内部节点（按 default_variant.layers 生成）
```

v20.7.x 起根节点改为 **CCNode**（原为 CCLayer），且不再多包一层"内层 CCNode"。原因：
- 子 CCB 作为被引用的组件，被嵌入主场景时不应出现 CCLayer 嵌套（CCLayer 只在场景根）
- CCNode 更轻量（没有 touch 处理），子 CCB 不需要独立处理触控
- 单层根节点结构清爽，displayName 直接是组件名

子 CCB 跟主场景的差异：

| 项 | 主场景 | 子 CCB |
|---|---|---|
| 根节点 | CCLayer | **CCNode**（v20.7.x） |
| 总组包装 | 有 | 无 |
| 组_背景层 / 防穿透层 | 有 | 无 |
| 遮罩 | 仅浮层 | 无 |
| resolutions | 5 种 | 1 种（控件自身尺寸）|
| sequences | 1 条占位 | N 条（Variant 数量） |
| currentResolution | 0 | 0 |

### 关键约定

- **总组**：所有 .red 文件 CCLayer 下第一层固定叫"总组"
- **屏幕名**：通过 .red 文件名表达（如 `界面_主菜单.red`），不写在节点 displayName
- **组_背景层**：所有屏幕（界面_/浮层_）必须有
- **背景节点提升**：顶层全屏背景（名以"背景_"开头 + 接近屏幕尺寸）自动提取到背景层作为 CCSprite

---

## 五、坐标规则

### 全宽节点判断

- `horizontal == 'SCALE'` → 全宽
- `horizontal == 'LEFT'` 且 `right < 10`（容差）→ 全宽

### 全宽节点参数

宽 = `100% u=2`，高 = `固定 px u=0`

| vertical | pos x | pos y | anchor |
|---|---|---|---|
| TOP | `50% u=2` | `100% u=2` | `(0.5, 1.0)` |
| BOTTOM | `50% u=2` | `0% u=2` | `(0.5, 0.0)` |
| CENTER | `50% u=2` | `50% u=2` | `(0.5, 0.5)` |

### 固定宽节点参数

按 left/right 对比关系：

| Figma 状况 | 对齐 | pos x | anchor x |
|---|---|---|---|
| left ≈ right | 居中 | `50% u=2` | `0.5` |
| left < right | 靠左 | `0% u=2` | `0.0` |
| left > right | 靠右 | `100% u=2` | `1.0` |

### 子节点处理（V1 当前限制）

- 父全宽 → 子 x 用百分比 u=2，子 y 用绝对像素 u=0
- 父固定 → 子 x/y 都用绝对像素 u=0
- **当前不读子节点的 constraints 字段**（V2 任务）

### 单位约定（铁律）

position 5 元数组：`[x, y, z, unitX, unitY]`

- `unit=0` → 绝对像素
- `unit=2` → 百分比
- `unit=3` → **仅用于 contentSize 高度**（"剩余空间"），position 永远不能用 u=3

---

## 六、默认值规约（v20.7.x+，2026-05-14）

### 主屏 resolutions 4 套预设

主屏 .red 文件 `resolutions` 数组固定 4 条，顺序敏感，`currentResolution=0`：

| index | name | width × height | 用途 |
|---|---|---|---|
| 0 | 设计分辨率 | 1080 × 2400 | 设计基准（默认进入） |
| 1 | 正常分辨率 | 1080 × 2080 | 正常屏 |
| 2 | 偏宽分辨率 | 1560 × 2080 | 偏宽屏（宽方向变大） |
| 3 | 偏高分辨率 | 1080 × 2800 | 偏高屏 |

子 CCB（Component）文件保留单条 = 控件自身 cw×ch（见上面"四、节点结构规范"对比表）。

---

