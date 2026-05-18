# 按钮 + 进度条命名规范

> 引擎 SKILL 拆分文档(v20.7.x+,2026-05-11) · 索引见 SKILL.md

---

## 零、SPRITE_NAME_PREFIXES (v20.7.x+ 2026-05-15 修订)

`red_tool/app.py` 里 `SPRITE_NAME_PREFIXES` 决定**哪些图层会走 sprite 分支 + 自动取图**:

```python
SPRITE_NAME_PREFIXES = ('图片_', '图标_', '背景_', '插图_', '特效_', '底板_', '进度条_')
```

命中前缀 → `build_child` / `build_top_layer` 走 CCSprite/CCProgressTimer 分支 → `lookup_image()` 查 `_IMAGE_INDEX` → displayFrame 自动填路径。

不命中(如 `文本_/组_/按钮_/容器_/`) → 跳过 sprite 处理。

### 真图集分类规则 (classify_sprite_kind)

- `背景_xxx` → 进 `<scene>_背景大图.{plist,webp}`
- 其他 sprite 前缀 → 进 `<scene>_图片资源.{plist,webp}`(包括 `底板_xxx`, `进度条_xxx`)
- "游戏内元件"类外围活动场景暂不实现

### Figma 插件 SPRITE_NAME_PREFIXES_JS

`code.js` 里也有一份相同列表,用于 `exportAllSprites` 决定要 export 哪些图层。**两边必须同步**(改了一边必须改另一边)。

---

## 六、按钮命名规则（v20）

| 命名 | type | 引擎角色 |
|---|---|---|
| `按钮_XXX` | FRAME | 触控层 REDNodeButton |
| `底板_XXX`（父非按钮）| RECT | 外层容器 CCSprite |
| `底板_XXX`（父是按钮）| RECT | 内层装饰 CCSprite |

### 兼容老命名

- v19: `底板_XXX` FRAME = 触控层
- v18: `切图_底板_XXX` = 触控层

### REDNodeButton 7 个属性

`position / contentSize / anchorPoint / opacity / color / ccControl(['',1,32]) / preferedSize`

- `ccControl` 值：`''` 选择器空 / `1` 启用 / `32` Up inside
- `preferedSize` 单位必须和 `contentSize` 一致（否则渲染成小方块）

### auto_btn 机制

`组_按钮_/按钮_` 无触控层子节点时，自动补 REDNodeButton 触控层并把内容移入其 children

### 按钮容器识别

看 baseClass=='REDNodeButton' 子节点，**不看名字**

---

## 七、进度条规范（v20.4）

### 三层结构

```
组_进度_XXX (CCNode 容器, 普通处理)
├── 底板_XXX (CCSprite, 永远显示完整底板)
└── 进度条_XXX (CCProgressTimer, 默认 100% 满)
```

### 识别条件

- type == 'RECTANGLE'
- name 以 `进度条_` 开头
- 同时满足才生成 CCProgressTimer，否则按普通节点处理

### Direction 命名后缀

| 节点名末尾 | direction |
|---|---|
| 无后缀（默认）| horizontal_lr（水平左→右）|
| `_rl` | horizontal_rl |
| `_tb` | vertical_tb |
| `_bt` | vertical_bt |
| `_cw` / `_ccw` | 不识别，按默认（环形不实现）|

### Direction → CCProgressTimer 属性映射

| direction | barType | midpoint | barChangeRate |
|---|---|---|---|
| horizontal_lr | 0 | [0, 0.5] | [1, 0] |
| horizontal_rl | 0 | [1, 0.5] | [1, 0] |
| vertical_bt | 0 | [0.5, 0] | [0, 1] |
| vertical_tb | 0 | [0.5, 1] | [0, 1] |

### 其他规则

- **percentage 默认 100**（视觉满，运行时控制）
- **不读 JSON 字段**：percentage/direction 都通过命名编码
- **节点 displayName 保留原名**（含后缀）
- **children 提升**（防御性）：进度条 RECT 通常无子节点，但若有则提升到父级

---

