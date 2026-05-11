# Figma 插件 v20.7 集成

> 引擎 SKILL 拆分文档(v20.7.x+,2026-05-11) · 索引见 SKILL.md

---

## 十一、Figma 插件 v20.7 集成

### 4 个 Tab

```
▶ 生成        — JSON 输入 → Figma 画布渲染（含 Component Set 自动构建）
⬇ 组件库      — 扫描"组件库"页面 Component → 输出 JSON 模板
📄 导出JSON   — 选中 Frame → 导出 wireframe JSON
🚀 生成 .red  — 选中屏幕 → POST localhost:5001 → 生成 .red 文件
```

### 🚀 Tab 工作流

1. 在 Figma 选中一个或多个 `界面_xxx` / `浮层_xxx` Frame
2. 切到 🚀 Tab
3. 检测 Python 服务连通性（绿点）
4. 设置/确认输出路径（默认 `~/Desktop/red_output`）
5. 点🚀按钮
6. 插件 `buildSceneForRed()`：过滤选中、反查 Component Set、组装 v20.6 schema
7. POST `/api/generate_red`
8. UI 显示生成的文件列表，点击在 Finder 中打开

### manifest.json 关键字段

```json
"networkAccess": {
  "allowedDomains": ["none"],
  "devAllowedDomains": ["http://localhost:5001/"],
  "reasoning": "本插件通过本地 Python 服务..."
}
```

注意：

- URL 末尾必须带 `/`
- 不能用 IP（`127.0.0.1` 不行）
- 必须加 `reasoning` 字段
- `devAllowedDomains` 仅在开发模式加载的插件能用

### code.js 新增函数

- `cleanComponentName(rawName)` — 去掉 `=Variant` 后缀
- `getInstanceVariant(inst)` — 取 INSTANCE 当前选中的 Variant 名
- `getInstanceMainComponent(inst)` — 取 INSTANCE 引用的 Component Set
- `nodeToJsonForRed(node, registry, keepInvisible)` — 节点 → JSON（v20.7.x 加 keepInvisible 参数）
- `componentSetToJsonForRed(compSet, registry)` — Component Set → JSON
- `extractConstraints(node)` — 提取约束（容错）
- `figmaFillsToHex(fills)` — **v20.7.x 新增**：把 Figma 节点的 fills 数组转成 `#RRGGBB` 字符串
- `buildSceneForRed()` — 主入口

### code.js v20.7.x 修复（三处关键 bug）

之前 buildSceneForRed() 导出 component variants 时丢数据，导致引擎拿到的 scene.json 缺关键字段：

#### Bug 1：隐藏节点跳过

```js
// 之前（有问题）：
function nodeToJsonForRed(node, registry) {
  if (!node.visible) return null; // 隐藏节点直接跳过
  ...
}

// v20.7.x 修复：
function nodeToJsonForRed(node, registry, keepInvisible) {
  if (!keepInvisible && !node.visible) return null; // 屏幕扫描下仍跳过
  // component variants 扫描下保留隐藏节点（写 visible:false）
}
```

`componentSetToJsonForRed` 调用时传 `keepInvisible=true`：

```js
layers = variantComp.children
  .map(function(c) { return nodeToJsonForRed(c, registry, true); })
  .filter(Boolean);
```

效果：每个 variant 的 visible=false 节点被保留，引擎能识别 variant 间的 visible 差异。

#### Bug 2：fill 字段不输出

```js
// v20.7.x 新增工具函数
function figmaFillsToHex(fills) {
  if (!Array.isArray(fills) || fills.length === 0) return null;
  for (var i = 0; i < fills.length; i++) {
    var f = fills[i];
    if (f.visible === false) continue;
    if (f.type === 'SOLID' && f.color) {
      var r = Math.round(f.color.r * 255);
      var g = Math.round(f.color.g * 255);
      var b = Math.round(f.color.b * 255);
      function h2(n) { var s = n.toString(16); return s.length < 2 ? '0' + s : s; }
      return '#' + h2(r) + h2(g) + h2(b);
    }
  }
  return null;
}
```

RECTANGLE / TEXT / FRAME 三处分支末尾各加：

```js
var hex = figmaFillsToHex(node.fills);
if (hex) o.fill = hex;
if (node.visible === false) o.visible = false;
```

效果：variant 之间的颜色差异（例如"当前用户"底板 fill=#88c870）能传给引擎。

#### Bug 3：component w/h 用合并尺寸

```js
// 之前（有问题）：
return {
  name: compName,
  w: Math.round(compSet.width),    // ← compSet 整体宽 = N 个 variant 横向并排合并宽度（5520）
  h: Math.round(compSet.height),
  ...
};

// v20.7.x 修复：
var sampleVariant = compSet;
if (compSet.type === 'COMPONENT_SET' && compSet.children.length > 0) {
  sampleVariant = compSet.children[0];
}
return {
  name: compName,
  w: Math.round(sampleVariant.width),    // 用单 variant 的宽度（1080）
  h: Math.round(sampleVariant.height),
  ...
};
```

效果：列表项_排名 component 的 w/h 是单个 variant 尺寸（1080×177），不再是 5 个并排合并的 5520×177。

---

