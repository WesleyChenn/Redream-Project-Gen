// Elsa UI 生成器 v20.6
// [v20.6]: Component 表达从命名标记切换到 schema 字段
//          - scene.json 顶层加 components 数组(每个 Component + 多 Variant + 完整 layers)
//          - 主场景里用 type:"INSTANCE" 节点引用 Component(component_name + variant 字段)
//          - ▶生成 时调 figma.combineAsVariants() 创建 Figma 真 Component Set
//          - INSTANCE 节点用 createInstance() + setProperties() 创建,改一处所有同步
//          - 画布右侧自动创建 📦_组件库 Frame 摆放所有 Component Set
//          - 删除老 _CCB_ 命名机制(v20.4 / v20.5 / v20.5.1 均废弃)
//          - 删除 📦导出 CCB / 🖼️ 渲染组件库 标签页(已不需要,▶生成 直接产出真 Component)
// [v20.5.1]: (废弃) _CCB_ 三段命名 <Component>_<序号>_CCB_<状态>
// [v20.5]:   (废弃) _CCB_ 后缀位命名 <真实命名>_CCB_<Variant>
// [v20.4]:   (废弃) CCB_ 前缀命名,导出器扫命名生成 components 数组
// [v20.2]: 进度条颜色改为浅蓝(0.55, 0.78, 0.95),与底板灰色拉开强对比,彻底解决撞色
// [v20.1]: 进度条上色修复 — 底板_xxx进度走底板分级(中深灰),进度条_xxx走亮灰,解决撞色
// 合并自 v19 + [v20]: 按钮识别规则重构 — "按钮_xxx" FRAME = 触控层（REDNodeButton）
//   · 按钮内层底板:父是"按钮_xxx" FRAME 的 "底板_xxx" RECT → 最浅灰
//   · 外层容器底板:父非按钮的 "底板_xxx" RECT → 中深灰
//   · 不再依赖 "形状" 后缀;装饰附件(角标/徽章/底标)作为按钮 FRAME 的 children
//   · 兼容老命名:切图_底板_xxx(最老)/ 底板_xxx FRAME(v19 临时方案)
// FIX①: FRAME无fill=透明  FIX②: overrides文字防溢出  FIX③: overrides精确匹配
// FIX④: font_size深度分级  FIX⑤: AL内节点坐标  FIX⑥: TEXT w+h=固定尺寸
// FIX⑦: screen.w/h 兼容读取  FIX⑧: FLEX_END/非法 alignItems 自动映射
// 新增: COMPONENT_SET构建 / Prototype OVERLAY+CLOSE / 自检系统 / rotation / overflow

figma.showUI(__html__, { width: 460, height: 620 });

// ── 色板 ──
// 规则：
//   FRAME 永远透明
//   RECTANGLE 按命名语义分层灰度
//   底板_xxx RECT 按父容器是否为按钮判断所属类型，分配不同灰度
var G = {
  bg:       { r:0.91, g:0.91, b:0.91 },  // 背景_ (最浅，屏幕背景)
  mask:     { r:0.20, g:0.20, b:0.20 },  // 遮罩_ (最深，蒙层)
  shadow:   { r:0.45, g:0.45, b:0.45 },  // 阴影
  img:      { r:0.76, g:0.76, b:0.76 },  // 图片_ / 图标_ / 插图_ / 特效_
  progress: { r:0.55, g:0.78, b:0.95 },  // 进度条填充 (浅蓝色,与底板灰色形成强对比)
  txt:      { r:0.12, g:0.12, b:0.12 },  // TEXT节点
  warn:     { r:1.00, g:0.85, b:0.85 },  // 占位警告
  rect:     { r:0.70, g:0.70, b:0.70 },  // 其余RECTANGLE默认

  // 底板_xxx RECT 按上下文语义分层
  shape_popup:  { r:0.52, g:0.52, b:0.52 },  // 弹窗/浮层底板 → 最深
  shape_card:   { r:0.63, g:0.63, b:0.63 },  // Toggle/卡片底板 → 中灰
  shape_switch: { r:0.72, g:0.72, b:0.72 },  // 开关底板 → 较浅
  shape_btn:    { r:0.82, g:0.82, b:0.82 },  // 按钮内层底板 → 最浅
  shape_container: { r:0.56, g:0.56, b:0.56 }  // 外层容器底板 → 中深灰
};

// ── 颜色分配 ──
// parentName: 直接父容器的 name，由 buildNode 传入
// FIX⑨: FRAME 永远返回 null（透明）
// [v20] 按钮识别规则重构：
//   · 按钮触控层：name 以 "按钮_" 开头的 FRAME
//   · 按钮内层底板：name 以 "底板_" 开头的 RECT，且父是 "按钮_xxx" FRAME → 最浅灰（按钮语义可选分级）
//   · 外层容器底板：name 以 "底板_" 开头的 RECT，且父非按钮 → 中深灰
//   · 老命名兼容：切图_底板_xxx（任意 type）和 底板_xxx 形状（旧方案A 的"形状"后缀）仍能识别
//   · 装饰附件（角标/徽章/底标）作为按钮 FRAME 的 children，无需特殊上色规则
function getColor(layer, depth, parentName) {
  var type = (layer.type || '').toUpperCase();
  var name = (layer.name || '').toLowerCase();
  var fill = (layer.fill || '').toLowerCase();
  var pname = (parentName || '').toLowerCase();

  // ── FRAME：永远透明，不上色 ──
  if (type === 'FRAME') return null;

  // ── TEXT：固定深色 ──
  if (type === 'TEXT') return G.txt;

  // ── hex 直读（仅对 RECTANGLE 生效）──
  if (fill && fill !== 'transparent' && fill !== '#00000000' && fill.startsWith('#')) {
    var hex = fill.replace('#', '');
    if (hex.length === 6) return {
      r: parseInt(hex.slice(0,2),16)/255,
      g: parseInt(hex.slice(2,4),16)/255,
      b: parseInt(hex.slice(4,6),16)/255
    };
  }
  if (fill === 'transparent' || fill === '#00000000' || fill === 'none') return null;

  // ── RECTANGLE 语义分层 ──

  // 遮罩：最深
  if (name.indexOf('遮罩') >= 0 || name.indexOf('mask') >= 0) return G.mask;

  // 阴影
  if (name.indexOf('阴影') >= 0 || name.indexOf('shadow') >= 0) return G.shadow;

  // 背景：最浅
  if (name.indexOf('背景') >= 0) return G.bg;

  // 图片/图标占位
  if (name.indexOf('图片') >= 0 || name.indexOf('图标') >= 0 ||
      name.indexOf('插图') >= 0 || name.indexOf('特效') >= 0) return G.img;

  // [v20.1] 进度条系列上色 (优先级须高于通用"含进度"匹配)
  //   · 底板_xxx进度 (RECT, 底板) → 走底板分级（外层容器底板 中深灰）
  //   · 进度条_xxx (RECT, 填充) → 进度填充色,亮一点
  //   注意: 必须先判断 进度条_ 前缀,再判断 底板_ 前缀,最后才是通用 "进度" 关键字匹配
  if (name.indexOf('进度条_') === 0) return G.progress;

  // [v20] 底板_xxx RECT：按父容器是否为按钮来分层
  //   · 父 name 以 "按钮_" 开头 → 按钮内层底板，最浅灰（可按语义分级）
  //   · 父 name 不以 "按钮_" 开头 → 外层容器底板，中深灰
  //   · [v20.5] CCB_ 改为后缀位命名(<真实命名>_CCB_<Variant>),CCB_ 不再出现在父名首位,
  //              灰度判断回归单条件,无需 CCB_ 特判。设计师用真实前缀(按钮_/网格行_)控制灰度。
  //   · [v20.5.1] CCB 命名进一步升级为三段(<Component>_<序号>_CCB_<Variant>),
  //              父名形如"任务行_1_CCB_已完成"、"宝箱按钮_1_CCB_常态",这些 CCB FRAME 本身
  //              就是按钮型复用单元,内部底板应走"按钮内层"浅灰。所以加一条:父名含 _CCB_ 也算按钮父。
  //   · 兼容老命名：
  //     - 以 "底板_" 开头并以 "形状" 结尾的 RECT（v19 方案A）
  //     - 父以 "切图_底板_" 开头的任意子节点（v18 及更早）
  //     这两种情况都按父容器语义后缀分级
  if (name.indexOf('底板') === 0) {
    var isButtonParent = pname.indexOf('按钮_') === 0;
    var isLegacyShape = name.indexOf('形状') >= 0;                // v19 兼容
    var isLegacyQietu = pname.indexOf('切图_底板_') >= 0;          // v18 兼容

    if (isButtonParent || isLegacyShape || isLegacyQietu) {
      // 按钮内层（含老命名场景）→ 按语义后缀分级灰度
      var semantic = pname
        .replace('按钮_', '')
        .replace('切图_底板_', '').replace('切图_底板', '')
        .replace('底板_', '');
      // 弹窗/浮层按钮 → 最深
      if (semantic.indexOf('弹窗') >= 0 || semantic.indexOf('浮层') >= 0 ||
          pname.indexOf('弹窗') >= 0 || pname.indexOf('浮层') >= 0) return G.shape_popup;
      // Toggle/卡片按钮 → 中灰
      if (semantic.indexOf('toggle') >= 0 || semantic.indexOf('卡片') >= 0) return G.shape_card;
      // 开关按钮 → 较浅
      if (semantic.indexOf('开关') >= 0) return G.shape_switch;
      // 其余按钮（首页/关卡/Action 等）→ 最浅
      return G.shape_btn;
    }

    // 父不是按钮 → 外层容器底板，中深灰
    return G.shape_container;
  }

  // 通用"含进度"匹配（兜底,FRAME 容器或老命名 进度_xxx 用）
  if (name.indexOf('进度') >= 0) return G.progress;

  // 其余 RECTANGLE 默认灰
  return G.rect;
}

// ── 字体 ──
var _fontCache = {};
async function loadFont(weight) {
  var style = (weight === 'Bold') ? 'Bold' : 'Regular';
  if (_fontCache[style]) return _fontCache[style];
  var families = ['Inter', 'Roboto', 'Arial'];
  for (var i = 0; i < families.length; i++) {
    try {
      await figma.loadFontAsync({ family: families[i], style: style });
      _fontCache[style] = { family: families[i], style: style };
      return _fontCache[style];
    } catch(e) {}
  }
  var fallback = { family: 'Arial', style: 'Regular' };
  await figma.loadFontAsync(fallback);
  _fontCache[style] = fallback;
  return fallback;
}

// ── 组件库（v12：查已有库）──
var compMap = {};
function loadLib() {
  compMap = {};
  var page = null;
  for (var i = 0; i < figma.root.children.length; i++) {
    if (figma.root.children[i].name === '组件库') { page = figma.root.children[i]; break; }
  }
  if (!page) return 0;
  function scan(node) {
    if (node.type === 'COMPONENT' && !compMap[node.name]) compMap[node.name] = node;
    if ('children' in node) { for (var j = 0; j < node.children.length; j++) scan(node.children[j]); }
  }
  scan(page);
  return Object.keys(compMap).length;
}

// ── 注册表 ──
var nodeReg = {}, frameReg = {};
var missingCompCount = 0;
var __absConstraintTotal = 0, __absConstraintSkipped = 0, __absPositioningTotal = 0;

function reg(screen, name, node) {
  var k = screen + '::' + name;
  if (!nodeReg[k]) nodeReg[k] = node;
}

// ── 自检系统（v9）──
var issueList = [];
var VALID_PREFIXES = [
  '界面_', '弹窗_', '浮层_', '屏幕_',
  '面板_', '按钮_', '标签_', '列表区域_', '列表容器_', '列表项_', '滑块_', '列表_',
  '底板Frame_', '内容_', '内容区_', '道具_', '组_', '输入框_', '搜索框_', '下拉框_', '复选框_', '单选框_', '分页器_',
  '底板_', '文字_', '文本_', '图片_', '图标_', '开关_', '进度条_', '背景图_', '遮罩_',
  '特效_', '插图_', '效果图_', '按钮基底_', '按钮内容_', '按钮角标_', '序列_',
  '切图_', '背景_', '全屏遮罩', '容器_', '导航_', '网格行_', '网格项_', '角标_',
  '徽章_', '进度_', 'Tab_', 'Toggle_', '请求_', '消息项_', '活动_', '底标_', '弹性缝隙'
];
function checkNameOk(name) {
  for (var i = 0; i < VALID_PREFIXES.length; i++) {
    if (name.indexOf(VALID_PREFIXES[i]) === 0) return true;
  }
  return false;
}
function checkLayer(layer, sw, sh, isTopLevel) {
  var name = layer.name || '(无名)';
  var type = (layer.type || '').toUpperCase();
  if (type === 'COMPONENT_SET') {
    if (!Array.isArray(layer.variants) || layer.variants.length < 2)
      issueList.push('COMPONENT_SET 需要 ≥2 个 variants: ' + name);
    var variants = layer.variants || [];
    for (var v = 0; v < variants.length; v++) {
      var vc = variants[v].children || [];
      for (var j = 0; j < vc.length; j++) checkLayer(vc[j], sw, sh, false);
    }
    return;
  }
  var x = layer.x||0, y = layer.y||0, w = layer.w||0, h = layer.h||0;
  if (isTopLevel && (x<0 || y<0 || (x+w)>sw || (y+h)>sh)) issueList.push('越界: ' + name);
  if (w<=0 || h<=0) issueList.push('无效尺寸: ' + name);
  if (!checkNameOk(name)) issueList.push('命名不规范: ' + name);
  if (Array.isArray(layer.children))
    for (var j = 0; j < layer.children.length; j++) checkLayer(layer.children[j], sw, sh, false);
}

// ── ComponentSet 容器（v9：新建组件集）──
var compHolder = null, compCount = 0, compCreated = 0, compHolderNextY = 40;
function getCompHolder() {
  if (!compHolder) {
    compHolder = figma.createFrame();
    compHolder.name = '◆ 组件库 (自动生成)';
    compHolder.x = -3200; compHolder.y = 0;
    compHolder.resize(400, 200);
    compHolder.layoutMode = 'VERTICAL';
    compHolder.primaryAxisSizingMode = 'AUTO';
    compHolder.counterAxisSizingMode = 'AUTO';
    compHolder.itemSpacing = 60;
    compHolder.paddingTop = 40;
    compHolder.paddingBottom = 40;
    compHolder.paddingLeft = 40;
    compHolder.paddingRight = 40;
    compHolder.fills = [{ type:'SOLID', color:{ r:0.94, g:0.94, b:0.94 } }];
    compHolder.clipsContent = false;
    figma.currentPage.appendChild(compHolder);
    compHolderNextY = 40;
  }
  return compHolder;
}

// ── overrides（FIX②③ + v20.7+ 嵌套 override）──
// v20.7+: 支持嵌套 override
//   flat: { "文本_玩家名": "gen" }                    → 找 TEXT 设 content
//   嵌套: { "排名圆": { "圆形容器_图标_文本": "3" } }   → 找子 INSTANCE,递归 applyOverrides
async function applyOverrides(inst, overrides) {
  if (!overrides || !Object.keys(overrides).length) return;
  for (var key in overrides) {
    var val = overrides[key];
    if (val === null || val === undefined) continue;

    // 嵌套 override: val 是对象 → 在子节点找同名 INSTANCE,递归
    if (typeof val === 'object' && !Array.isArray(val)) {
      var subInst = null;
      try {
        subInst = inst.findOne(function(n) {
          return (n.type === 'INSTANCE' || n.type === 'FRAME') && n.name === key;
        });
      } catch(e) {}
      if (subInst) {
        await applyOverrides(subInst, val);
      } else {
        log('⚠ 嵌套 override 未找到子 INSTANCE: ' + key + '（' + inst.name + '）');
      }
      continue;
    }

    // 平铺 override: val 是字符串 → 找 TEXT 设 content
    if (val === '') continue;
    var texts;
    try {
      texts = inst.findAll(function(n){ return n.type === 'TEXT'; });
    } catch(e) { continue; }
    var target = null;
    for (var i = 0; i < texts.length; i++) { if (texts[i].name === key) { target = texts[i]; break; } }
    if (!target) { for (var j = 0; j < texts.length; j++) { if (texts[j].name.indexOf(key) >= 0) { target = texts[j]; break; } } }
    if (!target) { log('⚠ overrides 未匹配: ' + key + '（' + inst.name + '）'); continue; }
    try {
      await figma.loadFontAsync(target.fontName);
      var origAutoResize = target.textAutoResize, origFontSize = target.fontSize, origWidth = target.width;
      target.textAutoResize = 'WIDTH_AND_HEIGHT';
      target.characters = String(val);
      if (target.width > origWidth * 1.05) {
        var ratio = origWidth / target.width;
        var newSize = Math.max(20, Math.floor(origFontSize * ratio));
        target.fontSize = newSize;
        log('⚠ 文字缩小: ' + key + ' ' + origFontSize + '→' + newSize + 'px');
      }
      try { target.textAutoResize = origAutoResize; } catch(e) {}
    } catch(e) { log('❌ overrides 写入失败: ' + key + ' — ' + e); }
  }
}

// ── component_ref 构建（v12）──
async function buildRef(layer, parent, screen) {
  var comp = compMap[layer.component_ref];
  if (!comp) {
    log('❌ 未找到组件: ' + layer.component_ref);
    missingCompCount++;
    var ph = figma.createRectangle();
    ph.name = '⚠ ' + layer.component_ref;
    ph.resize(layer.w||200, layer.h||80);
    ph.x = layer.x||0; ph.y = layer.y||0;
    ph.fills = [{ type:'SOLID', color:G.warn }];
    parent.appendChild(ph); reg(screen, ph.name, ph);
    return ph;
  }
  var inst = comp.createInstance();
  inst.name = layer.name || layer.component_ref;
  inst.x = layer.x||0; inst.y = layer.y||0;
  if (layer.w && layer.h) { try { inst.resize(layer.w, layer.h); } catch(e) {} }
  await applyOverrides(inst, layer.overrides);
  parent.appendChild(inst); reg(screen, inst.name, inst);
  if (layer.layoutPositioning === 'ABSOLUTE') {
    __absPositioningTotal++;
    try { inst.layoutPositioning = 'ABSOLUTE'; } catch(e) {}
    inst.x = layer.x||0; inst.y = layer.y||0;
  }
  if (layer.layoutSizingHorizontal) { try { inst.layoutSizingHorizontal = layer.layoutSizingHorizontal; } catch(e) {} }
  if (layer.layoutSizingVertical)   { try { inst.layoutSizingVertical   = layer.layoutSizingVertical;   } catch(e) {} }
  if (layer.constraints && layer.layoutPositioning === 'ABSOLUTE') { __absConstraintTotal++; __absConstraintSkipped++; }
  if (layer.constraints && layer.layoutPositioning !== 'ABSOLUTE') {
    try { inst.constraints = { horizontal: layer.constraints.horizontal||'MIN', vertical: layer.constraints.vertical||'MIN' }; } catch(e) {}
  }
  if (layer.visible === false) inst.visible = false;
  return inst;
}

// ── FIX⑤: 父容器是否 Auto Layout ──
function parentIsAutoLayout(p) {
  return p && (p.layoutMode === 'HORIZONTAL' || p.layoutMode === 'VERTICAL');
}

// ── ComponentSet 构建（v9）──
async function buildComponentSet(layer, parent, screenName) {
  var variants = layer.variants || [];
  if (variants.length < 2) {
    issueList.push('COMPONENT_SET 变体不足，降级 FRAME: ' + layer.name);
    var fb = Object.assign({}, layer, { type:'FRAME', children:(variants[0]||{}).children||[] });
    return await buildNode(fb, parent, 0, screenName);
  }
  var w = layer.w||100, h = layer.h||100, name = layer.name||'Component';
  var holder = getCompHolder(), components = [];
  for (var i = 0; i < variants.length; i++) {
    var comp = figma.createComponent();
    comp.name = 'State=' + (variants[i].state || i);
    comp.resize(w, h);
    comp.x = i * (w + 30); comp.y = 0;
    comp.fills = []; comp.clipsContent = false;
    holder.appendChild(comp);
    var vc = variants[i].children || [];
    for (var j = 0; j < vc.length; j++) await buildNode(vc[j], comp, 1, '__comp__');
    components.push(comp);
  }
  compCount++;
  var compSet;
  try { compSet = figma.combineAsVariants(components, holder); compSet.name = name; }
  catch(e) { issueList.push('combineAsVariants 失败: ' + name); return null; }
  var isLoop = (layer.animation_trigger === 'AFTER_DELAY'), delayMs = layer.delay_ms||500;
  for (var i = 0; i < components.length; i++) {
    var next = (i+1) % components.length;
    try {
      await components[i].setReactionsAsync([{
        trigger: isLoop ? { type:'AFTER_TIMEOUT', timeout:delayMs/1000 } : { type:'ON_CLICK' },
        actions: [{ type:'NODE', destinationId:components[next].id, navigation:'CHANGE_TO',
          transition:{ type:'SMART_ANIMATE', easing:{type:'EASE_IN_AND_OUT'}, duration:isLoop?0.3:0.15 } }]
      }]);
    } catch(e) { issueList.push('CHANGE_TO 失败: ' + name + '[' + i + ']'); }
  }
  var defIdx = 0;
  for (var i = 0; i < variants.length; i++) { if (variants[i].default) { defIdx = i; break; } }
  var instance;
  try { instance = components[defIdx].createInstance(); }
  catch(e) { issueList.push('createInstance 失败: ' + name); return null; }
  instance.name = name; instance.x = layer.x||0; instance.y = layer.y||0;
  parent.appendChild(instance); reg(screenName, name, instance);
  compCreated++;
  return instance;
}

// ── 节点构建 ──
async function buildNode(layer, parent, depth, screen) {
  var type = (layer.type||'RECTANGLE').toUpperCase();
  var name = layer.name || type;
  var isAbsolute = layer.layoutPositioning === 'ABSOLUTE';
  var cst = layer.constraints || {};
  var H_MAP = { LEFT:'MIN', RIGHT:'MAX', CENTER:'CENTER', SCALE:'STRETCH', LEFT_RIGHT:'STRETCH' };
  var V_MAP = { TOP:'MIN', BOTTOM:'MAX', CENTER:'CENTER', SCALE:'STRETCH', TOP_BOTTOM:'STRETCH' };

  // [v20.6] INSTANCE 节点(引用 Component Set 的 Instance)
  if (type === 'INSTANCE' && layer.component_name) {
    var compName = layer.component_name;
    var variantName = layer.variant;
    var entry = v20_6_componentRegistry[compName];
    if (!entry) {
      issueList.push('INSTANCE "' + name + '" 引用的 component_name "' + compName + '" 在 components 数组里不存在');
      return null;
    }
    if (variantName && !entry.variantMap[variantName]) {
      issueList.push('INSTANCE "' + name + '" 引用的 variant "' + variantName + '" 在 Component "' + compName + '" 里不存在');
      // 不退出,降级为 default
      variantName = null;
    }
    var inst;
    try {
      inst = entry.defaultVariantNode.createInstance();
    } catch (e) {
      issueList.push('createInstance 失败: ' + name + ' (' + e.message + ')');
      return null;
    }
    inst.name = name;
    inst.x = layer.x || 0;
    inst.y = layer.y || 0;
    if (layer.w) inst.resize(layer.w, layer.h || inst.height);
    // 设 variant
    if (variantName && variantName !== getV20_6_DefaultVariantName(compName)) {
      setV20_6_InstanceVariant(inst, compName, variantName);
    }
    // 应用 constraints
    if (cst.horizontal || cst.vertical) {
      try {
        inst.constraints = {
          horizontal: H_MAP[cst.horizontal] || 'MIN',
          vertical: V_MAP[cst.vertical] || 'MIN'
        };
      } catch (e) {}
    }
    parent.appendChild(inst);
    reg(screen, name, inst);
    if (layer.visible === false) inst.visible = false;
    // [v20.7+] 应用 INSTANCE 节点上的 overrides(支持嵌套)
    // 这一步之前漏掉,导致同 Variant 多实例渲染时 TEXT.content 全部用模板数据,
    // 列表里所有行都显示同一个名字/分数。
    if (layer.overrides) {
      await applyOverrides(inst, layer.overrides);
    }
    return inst;
  }

  // COMPONENT_SET 路由（优先）
  if (type === 'COMPONENT_SET') return await buildComponentSet(layer, parent, screen);
  // component_ref 路由
  if (layer.component_ref) return buildRef(layer, parent, screen);

  // CENTER+CENTER 自动居中（v9）
  var x = layer.x||0, y = layer.y||0, w = layer.w||100, h = layer.h||100;
  if (cst.horizontal === 'CENTER' && cst.vertical === 'CENTER' &&
      parent && parent.width > 0 && parent.height > 0) {
    x = (parent.width  - w) / 2;
    y = (parent.height - h) / 2;
  }

  // ══ FRAME ══
  if (type === 'FRAME') {
    var fr = figma.createFrame();
    fr.name = name; fr.resize(w, h);
    if (isAbsolute || !parentIsAutoLayout(parent)) { fr.x = x; fr.y = y; }
    // FIX⑨: FRAME 永远透明
    fr.fills = [];
    if (layer.corner_radius) fr.cornerRadius = layer.corner_radius;
    fr.clipsContent = !!layer.clip_content;
    if (layer.rotation !== undefined) fr.rotation = layer.rotation;
    if (layer.overflow && layer.overflow !== 'NONE') {
      try { fr.overflowDirection = layer.overflow; } catch(e) {}
    }
    if (cst.horizontal || cst.vertical) {
      try { fr.constraints = { horizontal: H_MAP[cst.horizontal]||'MIN', vertical: V_MAP[cst.vertical]||'MIN' }; } catch(e) {}
    }
    var lm = layer.layoutMode;
    if (lm === 'HORIZONTAL' || lm === 'VERTICAL') {
      fr.layoutMode = lm;
      if (layer.primaryAxisSizingMode)  fr.primaryAxisSizingMode  = layer.primaryAxisSizingMode;
      if (layer.counterAxisSizingMode)  fr.counterAxisSizingMode  = layer.counterAxisSizingMode;
      var COUNTER_AXIS_MAP = { 'FLEX_END':'MAX', 'FLEX_START':'MIN', 'STRETCH':'MIN' };
      var PRIMARY_AXIS_MAP = { 'FLEX_END':'MAX', 'FLEX_START':'MIN', 'STRETCH':'MIN', 'SPACE_AROUND':'SPACE_BETWEEN' };
      if (layer.primaryAxisAlignItems) {
        var pa = PRIMARY_AXIS_MAP[layer.primaryAxisAlignItems] || layer.primaryAxisAlignItems;
        try { fr.primaryAxisAlignItems = pa; } catch(e) {}
      }
      if (layer.counterAxisAlignItems) {
        var ca = COUNTER_AXIS_MAP[layer.counterAxisAlignItems] || layer.counterAxisAlignItems;
        try { fr.counterAxisAlignItems = ca; } catch(e) {}
      }
      if (layer.paddingLeft   != null)  fr.paddingLeft   = layer.paddingLeft;
      if (layer.paddingRight  != null)  fr.paddingRight  = layer.paddingRight;
      if (layer.paddingTop    != null)  fr.paddingTop    = layer.paddingTop;
      if (layer.paddingBottom != null)  fr.paddingBottom = layer.paddingBottom;
      if (layer.itemSpacing   != null)  fr.itemSpacing   = layer.itemSpacing;
    } else {
      fr.layoutMode = 'NONE';
    }
    parent.appendChild(fr); reg(screen, name, fr);
    if (isAbsolute) {
      __absPositioningTotal++;
      try { fr.layoutPositioning = 'ABSOLUTE'; } catch(e) {}
      fr.x = x; fr.y = y;
    }
    if (layer.layoutSizingHorizontal) { try { fr.layoutSizingHorizontal = layer.layoutSizingHorizontal; } catch(e) {} }
    if (layer.layoutSizingVertical)   { try { fr.layoutSizingVertical   = layer.layoutSizingVertical;   } catch(e) {} }
    if (Array.isArray(layer.children))
      for (var i = 0; i < layer.children.length; i++) await buildNode(layer.children[i], fr, depth+1, screen);
    if (layer.visible === false) fr.visible = false;
    return fr;
  }

  // ══ TEXT ══
  if (type === 'TEXT') {
    var defSize = depth===0 ? 48 : depth===1 ? 40 : depth===2 ? 36 : 32; // FIX④
    var font = await loadFont(layer.font_weight);
    var tn = figma.createText();
    tn.name = name; tn.fontName = font;
    tn.fontSize = layer.font_size || defSize;
    // FIX⑥: w+h 同时指定 → NONE 固定尺寸
    if (layer.w && layer.w > 0 && layer.h && layer.h > 0) {
      tn.textAutoResize = 'NONE';
      tn.resize(layer.w, layer.h);
      tn.characters = layer.content || name;
    } else if (layer.w && layer.w > 0) {
      tn.textAutoResize = 'HEIGHT';
      tn.resize(layer.w, 100);
      tn.characters = layer.content || name;
    } else {
      tn.textAutoResize = 'WIDTH_AND_HEIGHT';
      tn.characters = layer.content || name;
    }
    var ha = layer.textAlignHorizontal ||
      ((cst.horizontal === 'CENTER' || cst.horizontal === 'SCALE' || cst.horizontal === 'LEFT_RIGHT') ? 'CENTER' : 'LEFT');
    tn.textAlignHorizontal = ha;
    if (layer.textAlignVertical) tn.textAlignVertical = layer.textAlignVertical;
    var tc = getColor(layer, depth, parent && parent.name);
    if (tc) tn.fills = [{ type:'SOLID', color:tc }];
    if (isAbsolute || !parentIsAutoLayout(parent)) { tn.x = x; tn.y = y; } // FIX⑤
    if (cst.horizontal || cst.vertical) {
      try { tn.constraints = { horizontal: H_MAP[cst.horizontal]||'MIN', vertical: V_MAP[cst.vertical]||'MIN' }; } catch(e) {}
    }
    parent.appendChild(tn); reg(screen, name, tn);
    if (isAbsolute) {
      __absPositioningTotal++;
      try { tn.layoutPositioning = 'ABSOLUTE'; } catch(e) {}
      tn.x = x; tn.y = y;
    }
    if (layer.layoutSizingHorizontal) { try { tn.layoutSizingHorizontal = layer.layoutSizingHorizontal; } catch(e) {} }
    if (layer.layoutSizingVertical)   { try { tn.layoutSizingVertical   = layer.layoutSizingVertical;   } catch(e) {} }
    if (layer.visible === false) tn.visible = false;
    return tn;
  }

  // ══ RECTANGLE（默认）══
  var rc = figma.createRectangle();
  rc.name = name; rc.resize(w, h);
  if (isAbsolute || !parentIsAutoLayout(parent)) { rc.x = x; rc.y = y; } // FIX⑤
  var col = getColor(layer, depth, parent && parent.name);
  rc.fills = col ? [{ type:'SOLID', color:col }] : [];
  if (layer.corner_radius) rc.cornerRadius = layer.corner_radius;
  if (layer.rotation !== undefined) rc.rotation = layer.rotation;
  if (layer.relativeTransform) { try { rc.relativeTransform = layer.relativeTransform; } catch(e) {} }
  if (name.toLowerCase().indexOf('遮罩') >= 0 || name.toLowerCase().indexOf('mask') >= 0) {
    rc.opacity = layer.opacity !== undefined ? layer.opacity : 0.7;
  }
  if (cst.horizontal || cst.vertical) {
    try { rc.constraints = { horizontal: H_MAP[cst.horizontal]||'MIN', vertical: V_MAP[cst.vertical]||'MIN' }; } catch(e) {}
  }
  parent.appendChild(rc); reg(screen, name, rc);
  if (isAbsolute) {
    __absPositioningTotal++;
    try { rc.layoutPositioning = 'ABSOLUTE'; } catch(e) {}
    rc.x = x; rc.y = y;
  }
  if (layer.layoutSizingHorizontal) { try { rc.layoutSizingHorizontal = layer.layoutSizingHorizontal; } catch(e) {} }
  if (layer.layoutSizingVertical)   { try { rc.layoutSizingVertical   = layer.layoutSizingVertical;   } catch(e) {} }
  if (layer.visible === false) rc.visible = false;
  return rc;
}

// ── Prototype 连线（v9 完整版：支持 OVERLAY / CLOSE）──
async function applyPrototypeFlow(flowItems) {
  var linked = 0, failed = [];
  for (var i = 0; i < flowItems.length; i++) {
    var item = flowItems[i];
    var fromScreen = item.from || item.from_screen || '';  // FIX: 兼容 from_screen 字段名
    var src  = nodeReg[fromScreen + '::' + item.from_node];
    var dest = frameReg[item.to];
    var isTargetOverlay = (item.to || '').indexOf('浮层_') === 0;
    var isSourceOverlay = fromScreen.indexOf('浮层_') === 0;
    if (!src)  { failed.push('源节点未找到: ' + item.from_node); continue; }
    if (!dest && !isSourceOverlay) { failed.push('目标未找到: ' + item.to); continue; }  // FIX: CLOSE flow 允许 to=""
    var dur = 0.3;
    var m = (item.animation||'').match(/(\d+)ms/);
    if (m) dur = parseInt(m[1]) / 1000;
    var ttype = (item.animation||'').indexOf('slide') >= 0 ? 'SMART_ANIMATE' : 'DISSOLVE';
    try {
      var action;
      if (isSourceOverlay) {
        action = { type:'CLOSE' };
      } else {
        var nav = isTargetOverlay ? 'OVERLAY' : 'NAVIGATE';
        action = { type:'NODE', destinationId:dest.id, navigation:nav,
          transition:{ type:ttype, easing:{type:'EASE_OUT'}, duration:dur }, preserveScrollPosition:false };
        if (nav === 'OVERLAY') {
          try { dest.overlayPosition = 'CENTER'; } catch(ex) {}
          try { dest.overlayBackground = { type:'NONE' }; } catch(ex) {}
        }
      }
      await src.setReactionsAsync([{ actions:[action], trigger:{ type:item.trigger||'ON_CLICK' } }]);
      linked++;
    } catch(e) { failed.push(item.from_node + '→' + item.to + ': ' + e); }
  }
  return { linked, failed };
}

// ── 组件库导出（v12）──
function nodeToJson(node) {
  if (!node) return null;
  if (node.type === 'TEXT') return {
    type:'TEXT', name:node.name,
    x:Math.round(node.x), y:Math.round(node.y),
    w:Math.round(node.width), h:Math.round(node.height),
    fill:'←截图读取', element_class:'static',
    constraints:{ horizontal:'LEFT', vertical:'TOP' },
    content:node.characters||'',
    font_size:Math.round(node.fontSize)||32,
    font_weight:(node.fontName&&node.fontName.style==='Bold')?'Bold':'Regular'
  };
  if (['RECTANGLE','ELLIPSE','VECTOR','STAR','POLYGON','LINE'].indexOf(node.type) >= 0) {
    var cr = (node.cornerRadius && typeof node.cornerRadius === 'number') ? Math.round(node.cornerRadius) : 0;
    if (node.type === 'ELLIPSE') cr = Math.round(Math.min(node.width, node.height)/2);
    var o = { type:'RECTANGLE', name:node.name, x:Math.round(node.x), y:Math.round(node.y),
      w:Math.round(node.width), h:Math.round(node.height), fill:'←截图读取', element_class:'static',
      constraints:{ horizontal:'LEFT', vertical:'TOP' } };
    if (cr > 0) o.corner_radius = cr;
    return o;
  }
  if (['FRAME','COMPONENT','INSTANCE','GROUP','COMPONENT_SET'].indexOf(node.type) >= 0) {
    var cr2 = (node.cornerRadius && typeof node.cornerRadius === 'number') ? Math.round(node.cornerRadius) : 0;
    var o2 = { type:'FRAME', name:node.name, x:Math.round(node.x), y:Math.round(node.y),
      w:Math.round(node.width), h:Math.round(node.height), fill:'transparent', element_class:'static',
      constraints:{ horizontal:'LEFT', vertical:'TOP' } };
    if (cr2 > 0) o2.corner_radius = cr2;
    if ('children' in node && node.children.length > 0)
      o2.children = node.children.map(function(c){ return nodeToJson(c); }).filter(Boolean);
    return o2;
  }
  return null;
}
function exportLib() {
  var page = null;
  for (var i = 0; i < figma.root.children.length; i++) {
    if (figma.root.children[i].name === '组件库') { page = figma.root.children[i]; break; }
  }
  if (!page) return { error:'未找到「组件库」页面' };
  var result = {};
  function scan(node) {
    if ((node.type === 'COMPONENT' || node.type === 'COMPONENT_SET') && !result[node.name])
      result[node.name] = nodeToJson(node);
    if ('children' in node) { for (var i = 0; i < node.children.length; i++) scan(node.children[i]); }
  }
  scan(page);
  return result;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 🚀 生成 .red：scene.json 构造逻辑
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// 清洗 Component Set 名（去掉 "=Variant" 后缀，Figma 自动加的）
function cleanComponentName(rawName) {
  if (!rawName) return rawName;
  var idx = rawName.indexOf('=');
  return idx >= 0 ? rawName.substring(0, idx) : rawName;
}

// 取 INSTANCE 节点当前选中的 Variant 名
function getInstanceVariant(inst) {
  try {
    var props = inst.componentProperties;
    if (!props) return '常态';
    // 找 VARIANT 类型的属性，取它的 value
    for (var key in props) {
      var p = props[key];
      if (p && p.type === 'VARIANT') return p.value || '常态';
    }
    return '常态';
  } catch(e) {
    return '常态';
  }
}

// 取 INSTANCE 节点引用的 Component Set
function getInstanceMainComponent(inst) {
  try {
    var main = inst.mainComponent;
    if (!main) return null;
    // 如果 main 在 ComponentSet 里（即有 Variants），取 ComponentSet
    if (main.parent && main.parent.type === 'COMPONENT_SET') return main.parent;
    return main;
  } catch(e) {
    return null;
  }
}

// 节点 → JSON（含 INSTANCE 识别）
// v20.7.x: 把 Figma 节点的 fills 转成 #RRGGBB 字符串
// 取第一个 SOLID 类型的可见填充。其他类型（GRADIENT/IMAGE）暂不处理，返回 null。
function figmaFillsToHex(fills) {
  if (!Array.isArray(fills) || fills.length === 0) return null;
  for (var i = 0; i < fills.length; i++) {
    var f = fills[i];
    if (!f) continue;
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


// v20.7.x: keepInvisible=true 用于 component variants 内部扫描
// 让 visible=false 的节点也保留下来（写 visible:false 字段），Python 端用来识别 variant 间差异。
// 屏幕扫描时仍保持 keepInvisible=false（隐藏的辅助节点跳过）。
function nodeToJsonForRed(node, registry, keepInvisible) {
  if (!node) return null;
  if (!keepInvisible && !node.visible) return null; // 屏幕扫描：隐藏节点跳过
  // component variants 扫描下保留隐藏节点，写 visible:false（见各分支）

  // INSTANCE：输出引用，并把 Component Set 加进 registry
  if (node.type === 'INSTANCE') {
    var compSet = getInstanceMainComponent(node);
    var rawName = compSet ? compSet.name : (node.mainComponent ? node.mainComponent.name : 'unknown');
    var compName = cleanComponentName(rawName);
    var variant = getInstanceVariant(node);
    if (compSet && !registry[compName]) {
      registry[compName] = compSet;
    }
    var oI = {
      type: 'INSTANCE',
      name: node.name,
      component_name: compName,
      variant: variant,
      x: Math.round(node.x), y: Math.round(node.y),
      w: Math.round(node.width), h: Math.round(node.height),
      visible: node.visible !== false,
      constraints: extractConstraints(node)
    };
    return oI;
  }

  // TEXT
  if (node.type === 'TEXT') {
    var oT = {
      type: 'TEXT', name: node.name,
      x: Math.round(node.x), y: Math.round(node.y),
      w: Math.round(node.width), h: Math.round(node.height),
      content: node.characters || '',
      font_size: Math.round(node.fontSize) || 32,
      font_weight: (node.fontName && node.fontName.style === 'Bold') ? 'Bold' : 'Regular',
      constraints: extractConstraints(node)
    };
    if (node.visible === false) oT.visible = false;
    var hexT = figmaFillsToHex(node.fills);
    if (hexT) oT.fill = hexT;
    return oT;
  }

  // RECT 类
  if (['RECTANGLE','ELLIPSE','VECTOR','STAR','POLYGON','LINE'].indexOf(node.type) >= 0) {
    var cr = (node.cornerRadius && typeof node.cornerRadius === 'number') ? Math.round(node.cornerRadius) : 0;
    if (node.type === 'ELLIPSE') cr = Math.round(Math.min(node.width, node.height)/2);
    var o = {
      type: 'RECTANGLE', name: node.name,
      x: Math.round(node.x), y: Math.round(node.y),
      w: Math.round(node.width), h: Math.round(node.height),
      constraints: extractConstraints(node)
    };
    if (cr > 0) o.corner_radius = cr;
    if (node.visible === false) o.visible = false;
    var hexR = figmaFillsToHex(node.fills);
    if (hexR) o.fill = hexR;
    return o;
  }

  // FRAME / GROUP / COMPONENT / COMPONENT_SET（容器）
  if (['FRAME','GROUP','COMPONENT','COMPONENT_SET'].indexOf(node.type) >= 0) {
    var cr2 = (node.cornerRadius && typeof node.cornerRadius === 'number') ? Math.round(node.cornerRadius) : 0;
    var o2 = {
      type: 'FRAME', name: node.name,
      x: Math.round(node.x), y: Math.round(node.y),
      w: Math.round(node.width), h: Math.round(node.height),
      constraints: extractConstraints(node)
    };
    if (cr2 > 0) o2.corner_radius = cr2;
    if (node.visible === false) o2.visible = false;
    var hexF = figmaFillsToHex(node.fills);
    if (hexF) o2.fill = hexF;
    // AL 属性
    if (node.layoutMode && node.layoutMode !== 'NONE') {
      o2.layoutMode = node.layoutMode;
      if (node.primaryAxisAlignItems) o2.primaryAxisAlignItems = node.primaryAxisAlignItems;
      if (node.counterAxisAlignItems) o2.counterAxisAlignItems = node.counterAxisAlignItems;
      if (typeof node.itemSpacing === 'number') o2.itemSpacing = node.itemSpacing;
      if (typeof node.paddingLeft === 'number') o2.paddingLeft = node.paddingLeft;
      if (typeof node.paddingRight === 'number') o2.paddingRight = node.paddingRight;
      if (typeof node.paddingTop === 'number') o2.paddingTop = node.paddingTop;
      if (typeof node.paddingBottom === 'number') o2.paddingBottom = node.paddingBottom;
    }
    if ('children' in node && node.children.length > 0) {
      o2.children = node.children
        .map(function(c) { return nodeToJsonForRed(c, registry, keepInvisible); })
        .filter(Boolean);
    }
    return o2;
  }

  return null;
}

// 提取节点的 constraints（容错）
function extractConstraints(node) {
  try {
    var c = node.constraints;
    if (!c) return { horizontal: 'LEFT', vertical: 'TOP' };
    return { horizontal: c.horizontal || 'LEFT', vertical: c.vertical || 'TOP' };
  } catch(e) {
    return { horizontal: 'LEFT', vertical: 'TOP' };
  }
}

// Component Set → JSON（v20.6 schema：name + variants 数组）
function componentSetToJsonForRed(compSet, registry) {
  var compName = cleanComponentName(compSet.name);

  // 取 Variant Property 名
  var propertyName = '状态';
  try {
    if (compSet.componentPropertyDefinitions) {
      for (var key in compSet.componentPropertyDefinitions) {
        var def = compSet.componentPropertyDefinitions[key];
        if (def && def.type === 'VARIANT') {
          propertyName = key;
          break;
        }
      }
    }
  } catch(e) {}

  // 遍历 ComponentSet 的 children（每个是一个 Variant Component）
  // v20.7.x: nodeToJsonForRed 第三参数 keepInvisible=true，让 visible=false 的节点
  // 也保留下来（写 visible:false），Python 端从中识别 variant 间的差异并生成 keyframe。
  var variants = [];
  var sampleVariant = compSet;  // 单 variant 默认值
  if (compSet.type === 'COMPONENT_SET') {
    if (compSet.children.length > 0) sampleVariant = compSet.children[0];
    for (var i = 0; i < compSet.children.length; i++) {
      var variantComp = compSet.children[i];
      // Variant 名：从命名 "状态=常态" 里取
      var vName = '常态';
      var vIdx = variantComp.name.indexOf('=');
      if (vIdx >= 0) {
        vName = variantComp.name.substring(vIdx + 1);
      } else {
        vName = variantComp.name;
      }
      // Variant 内部 layers（keepInvisible=true）
      var layers = [];
      if ('children' in variantComp) {
        layers = variantComp.children
          .map(function(c) { return nodeToJsonForRed(c, registry, true); })
          .filter(Boolean);
      }
      variants.push({
        name: vName,
        is_default: (i === 0),  // 第一个 Variant 标为默认
        layers: layers
      });
    }
  } else {
    // 单 Component（无 Variants）
    var layers0 = [];
    if ('children' in compSet) {
      layers0 = compSet.children
        .map(function(c) { return nodeToJsonForRed(c, registry, true); })
        .filter(Boolean);
    }
    variants.push({
      name: '常态',
      is_default: true,
      layers: layers0
    });
  }

  // v20.7.x: w/h 用单个 variant 的尺寸，不是 ComponentSet frame 整体的尺寸
  // （ComponentSet 整体宽 = N 个 variant 横向并排，会得到 5520 这种错误的合并宽度）

  // [v20.7+] 标记是否是组件库引用(parent 为"组件库" page)
  // 组件库引用的 INSTANCE 必然按 S0 规则缩放(80×80 vs 库 25×25),
  // 不应该参与"INSTANCE vs Component 本体"尺寸一致性检查。
  var isLibrary = false;
  try {
    var node = compSet;
    while (node && node.type !== 'PAGE') node = node.parent;
    if (node && node.name === '组件库') isLibrary = true;
  } catch(e) {}

  var result = {
    name: compName,
    w: Math.round(sampleVariant.width),
    h: Math.round(sampleVariant.height),
    property_name: propertyName,
    variants: variants
  };
  if (isLibrary) result._is_library = true;
  return result;
}

// [v20.7+] 生成 .red 前的清理: 递归删除 Variant.layers 内 visible=false 节点
//   - 对应 S0 用户决策: "某根时间线里隐藏的图层直接删掉" — 这里"时间线"特指
//     Component Set 内的 Variant 时间线
//   - 屏幕级 layers 的 visible=false 必须保留(Tab 切换/状态切换 都依赖它,
//     例如 同屏 Tab 时,被隐藏的那个 Tab 容器不能被删,否则切回来什么都没有了)
function stripInvisibleNodes(scene) {
  var stats = { variant: 0 };

  function recurseAndStrip(layers) {
    if (!Array.isArray(layers)) return layers;
    var out = [];
    for (var i = 0; i < layers.length; i++) {
      var n = layers[i];
      if (n && n.visible === false) {
        continue;  // 节点不可见,在 Variant 内删掉(连同 children)
      }
      if (n) {
        if (Array.isArray(n.children)) n.children = recurseAndStrip(n.children);
        if (Array.isArray(n.layers))   n.layers   = recurseAndStrip(n.layers);
      }
      out.push(n);
    }
    return out;
  }

  // ❌ 屏幕 layers 不剥离 (保留 visible=false 给 Tab/状态切换用)

  // ✅ 仅 Component variants 内部 layers 剥离
  (scene.components || []).forEach(function(c) {
    (c.variants || []).forEach(function(v) {
      var before = JSON.stringify(v.layers || []).length;
      v.layers = recurseAndStrip(v.layers || []);
      var after = JSON.stringify(v.layers || []).length;
      if (after < before) stats.variant++;
    });
  });

  return stats;
}

// [v20.7+] INSTANCE 尺寸同步检查
// 对应 S0 文档 "INSTANCE 尺寸同步铁律":
//   设计师在屏幕里直接拖 INSTANCE 改尺寸 → Figma 不会自动同步到 Component Set 本体
//   生成 .red 时父 CCNode 用 INSTANCE 尺寸,子 CCB 用 Component 尺寸 → 视觉错位
// 本函数扫描 scene 输出,发现尺寸不一致时报警,但不自动修复(必须从 Figma 端 Push)
function checkInstanceSizeConsistency(scene) {
  var compSize = {};
  // [v20.7+] 组件库引用按 S0 规则故意缩放,跳过尺寸一致性检查(否则误报)
  (scene.components || []).forEach(function(c) {
    if (c._is_library) return;
    compSize[c.name] = { w: c.w, h: c.h };
  });

  var byComp = {};   // component_name → [{name, w, h}, ...]
  function walk(n) {
    if (!n) return;
    if (n.type === 'INSTANCE') {
      var cn = n.component_name || '';
      if (!byComp[cn]) byComp[cn] = [];
      byComp[cn].push({ name: n.name, w: n.w, h: n.h });
    }
    var kids = n.children || n.layers || [];
    for (var i = 0; i < kids.length; i++) walk(kids[i]);
  }
  (scene.screens || []).forEach(function(s) {
    (s.layers || []).forEach(walk);
  });

  var issues = [];
  for (var cn in byComp) {
    var insts = byComp[cn];
    var seen = {}, sizes = [];
    insts.forEach(function(i) {
      var k = i.w + 'x' + i.h;
      if (!seen[k]) { seen[k] = true; sizes.push({ w: i.w, h: i.h }); }
    });
    if (sizes.length > 1) {
      issues.push({
        kind: 'inconsistent_instance_sizes',
        component: cn,
        instances: insts,
        sizes: sizes
      });
    }
    var cs = compSize[cn];
    if (cs) {
      insts.forEach(function(i) {
        if (i.w !== cs.w || i.h !== cs.h) {
          issues.push({
            kind: 'instance_vs_component_mismatch',
            component: cn,
            instance_name: i.name,
            instance_size: { w: i.w, h: i.h },
            component_size: cs
          });
        }
      });
    }
  }
  return issues;
}

function logSizeIssues(issues) {
  if (!issues || !issues.length) return;
  log('⚠️  INSTANCE 尺寸同步检查发现 ' + issues.length + ' 条问题:');
  issues.forEach(function(it) {
    if (it.kind === 'inconsistent_instance_sizes') {
      log('  ❌ Component "' + it.component + '" 的 INSTANCE 尺寸不一致:');
      it.instances.forEach(function(i) {
        log('       - ' + i.name + ': ' + i.w + '×' + i.h);
      });
    } else if (it.kind === 'instance_vs_component_mismatch') {
      log('  ❌ ' + it.component + ' / ' + it.instance_name +
          ': INSTANCE ' + it.instance_size.w + '×' + it.instance_size.h +
          ' ≠ Component 本体 ' + it.component_size.w + '×' + it.component_size.h);
    }
  });
  log('  📌 修复: 选中目标尺寸 INSTANCE → 右键 Push changes to main component (⌥⌘Y)');
  log('       所有同 component 的 INSTANCE 自动同步,Component 本体也更新');
  log('  ⛔ 不修复直接生成 .red → 父子尺寸不匹配,渲染视觉错位');
}

// 主入口：把当前选中的屏幕打包成 scene.json（v20.6 schema）
function buildSceneForRed() {
  var selection = figma.currentPage.selection;

  // 过滤出 界面_/浮层_ 屏幕
  var screens = selection.filter(function(node) {
    return node.type === 'FRAME' &&
      (node.name.indexOf('界面_') === 0 || node.name.indexOf('浮层_') === 0);
  });

  if (screens.length === 0) {
    return {
      error: '请先选中一个或多个 界面_/浮层_ Frame（已忽略 ' +
        selection.length + ' 个非屏幕节点）'
    };
  }

  var ignoredCount = selection.length - screens.length;

  // 反查所有 Component Set
  var registry = {};

  // 序列化每个屏幕
  var screensOut = screens.map(function(screen) {
    var layers = [];
    if ('children' in screen) {
      layers = screen.children
        .map(function(c) { return nodeToJsonForRed(c, registry); })
        .filter(Boolean);
    }
    return {
      id: 'screen_' + screen.name.replace(/^(界面_|浮层_)/, ''),
      name: screen.name,
      w: Math.round(screen.width),
      h: Math.round(screen.height),
      layers: layers
    };
  });

  // 把 registry 里的 Component Set 序列化（注意：内部 INSTANCE 也会注册新的 Component，要循环直到稳定）
  var componentsOut = [];
  var processed = {};
  var pending = Object.keys(registry);
  while (pending.length > 0) {
    var name = pending.shift();
    if (processed[name]) continue;
    processed[name] = true;
    var compSet = registry[name];
    componentsOut.push(componentSetToJsonForRed(compSet, registry));
    // 检查 registry 里有没有新加进来的
    for (var k in registry) {
      if (!processed[k] && pending.indexOf(k) < 0) pending.push(k);
    }
  }

  var sceneOut = {
    meta: {
      design_size: {
        w: screensOut[0] ? screensOut[0].w : 1080,
        h: screensOut[0] ? screensOut[0].h : 2400
      }
    },
    components: componentsOut,
    screens: screensOut,
    flow: [],
    _ignored_count: ignoredCount
  };

  // [v20.7+] INSTANCE 尺寸同步检查 — 把警告附在 scene 上,UI 层根据这个决定是否阻止生成
  var sizeIssues = checkInstanceSizeConsistency(sceneOut);
  if (sizeIssues.length > 0) {
    sceneOut._size_warnings = sizeIssues;
  }

  // [v20.7+] 生成 .red 前的最后一道清理: 把所有 visible=false 节点硬删
  // 引擎不需要看到隐藏层(Figma 时间线里 visible=false 的元素 → 进 .red 时直接删除)
  var stripStats = stripInvisibleNodes(sceneOut);
  log('🧹 已清理 invisible 节点: ' + stripStats.screen + ' 个屏幕受影响, ' +
      stripStats.variant + ' 个 Variant 受影响');

  return sceneOut;
}

// ── Log ──
function log(msg) { figma.ui.postMessage({ type:'log', msg:msg }); }

// ── 主流程 ──
// ── [v20.6] Component Set 构建器 ──
// 全局注册表:Component 名 → 元数据
var v20_6_componentRegistry = {};
var v20_6_componentIssues = [];

// 全局 Component 库 Holder Frame(画布右侧的 📦_组件库 - 只放 Variant 平铺定义)
var v20_6_libHolder = null;
// [v20.7+] 全局可切换预览 Holder Frame(画布右侧的 🎮_可切换预览 - 每 Component 一个 INSTANCE)
var v20_6_previewHolder = null;

function getV20_6_LibHolder(rightOfX) {
  if (v20_6_libHolder) return v20_6_libHolder;
  v20_6_libHolder = figma.createFrame();
  v20_6_libHolder.name = '📦_组件库';
  v20_6_libHolder.fills = [{ type:'SOLID', color: { r:0.95, g:0.95, b:0.95 } }];
  v20_6_libHolder.cornerRadius = 24;
  v20_6_libHolder.clipsContent = false;
  // 用 Auto Layout 让 Component Set 横向排列
  v20_6_libHolder.layoutMode = 'HORIZONTAL';
  v20_6_libHolder.primaryAxisSizingMode = 'AUTO';
  v20_6_libHolder.counterAxisSizingMode = 'AUTO';
  v20_6_libHolder.itemSpacing = 80;
  v20_6_libHolder.paddingLeft = 60;
  v20_6_libHolder.paddingRight = 60;
  v20_6_libHolder.paddingTop = 80;
  v20_6_libHolder.paddingBottom = 80;
  v20_6_libHolder.x = rightOfX;
  v20_6_libHolder.y = 0;
  figma.currentPage.appendChild(v20_6_libHolder);
  return v20_6_libHolder;
}

// [v20.7+] 可切换预览 Holder: 每个 Component 一个 INSTANCE,设计师可在右侧 "状态" 下拉切换
function getV20_6_PreviewHolder(rightOfX) {
  if (v20_6_previewHolder) return v20_6_previewHolder;
  v20_6_previewHolder = figma.createFrame();
  v20_6_previewHolder.name = '🎮_可切换预览';
  v20_6_previewHolder.fills = [{ type:'SOLID', color: { r:0.92, g:0.96, b:0.92 } }];
  v20_6_previewHolder.cornerRadius = 24;
  v20_6_previewHolder.clipsContent = false;
  v20_6_previewHolder.layoutMode = 'HORIZONTAL';
  v20_6_previewHolder.primaryAxisSizingMode = 'AUTO';
  v20_6_previewHolder.counterAxisSizingMode = 'AUTO';
  v20_6_previewHolder.itemSpacing = 80;
  v20_6_previewHolder.paddingLeft = 60;
  v20_6_previewHolder.paddingRight = 60;
  v20_6_previewHolder.paddingTop = 80;
  v20_6_previewHolder.paddingBottom = 80;
  // 放在 📦_组件库 下方,留 80px 间距
  v20_6_previewHolder.x = rightOfX;
  v20_6_previewHolder.y = (v20_6_libHolder ? v20_6_libHolder.y + v20_6_libHolder.height + 80 : 0);
  figma.currentPage.appendChild(v20_6_previewHolder);
  return v20_6_previewHolder;
}

// 根据 components 数组创建 Figma 真 Component Set
async function buildV20_6_ComponentSets(componentsArr) {
  // 先创建一个临时 Holder(放在画布远处),稍后整个 Component Set 会被挪到 lib holder
  for (var ci = 0; ci < componentsArr.length; ci++) {
    var compDef = componentsArr[ci];
    var name = compDef.name;
    var w = compDef.w || 200, h = compDef.h || 200;
    var propName = compDef.property_name || '状态';
    var variants = compDef.variants || [];

    if (!name) { v20_6_componentIssues.push('Component 缺少 name'); continue; }
    if (variants.length === 0) { v20_6_componentIssues.push('Component "' + name + '" 没有 variants'); continue; }

    // 校验 is_default 个数
    var defaultCount = 0;
    for (var i = 0; i < variants.length; i++) if (variants[i].is_default) defaultCount++;
    if (defaultCount !== 1) {
      v20_6_componentIssues.push('Component "' + name + '" 的 is_default 数量 = ' + defaultCount + ',应为 1');
    }

    // 为每个 Variant 创建一个临时 Component(脱离任何容器,远离画布)
    var componentNodes = [];
    var variantMap = {};
    var defaultIdx = 0;
    for (var vi = 0; vi < variants.length; vi++) {
      var vDef = variants[vi];
      var vName = vDef.name || ('Variant_' + vi);

      var comp = figma.createComponent();
      // [v20.6] Figma 命名约定: combineAsVariants 用 <ComponentName>/<VariantValue> 斜杠语法
      // Figma 会自动把 / 后面的部分作为 Variant 取值,Property 名默认是"Property 1",创建后改名
      comp.name = name + '/' + vName;
      comp.resize(w, h);
      comp.x = -100000 + ci * 5000 + vi * (w + 30);  // 远离主画布,稍后会被挪到 lib holder
      comp.y = -100000;
      comp.fills = [];
      comp.clipsContent = false;
      figma.currentPage.appendChild(comp);

      // 构建 Variant 内部 layers
      var vLayers = vDef.layers || [];
      for (var li = 0; li < vLayers.length; li++) {
        await buildNode(vLayers[li], comp, 1, '__comp__' + name);
      }

      componentNodes.push(comp);
      variantMap[vName] = comp;
      if (vDef.is_default) defaultIdx = vi;
    }

    // combineAsVariants 合并
    var compSet = null;
    try {
      compSet = figma.combineAsVariants(componentNodes, figma.currentPage);
      compSet.name = name;
    } catch (e) {
      v20_6_componentIssues.push('combineAsVariants 失败: ' + name + ' (' + e.message + ')');
      continue;
    }

    // [v20.6] 把默认的 "Property 1" 改名为 propName(如"状态")
    try {
      var propDefs = compSet.componentPropertyDefinitions;
      var oldPropNames = Object.keys(propDefs);
      // 默认应该只有一个 Property(因为我们 Component name 只用了一个 /)
      // 找出默认那个 VARIANT property 改名为 propName
      for (var oi = 0; oi < oldPropNames.length; oi++) {
        var oldName = oldPropNames[oi];
        if (propDefs[oldName].type === 'VARIANT' && oldName !== propName) {
          // editComponentProperty 改名
          compSet.editComponentProperty(oldName, { name: propName });
          break;
        }
      }
    } catch (e) {
      v20_6_componentIssues.push('Property 改名失败: ' + name + ' (' + e.message + '),Component Set 已建好但 Property 名仍是 "Property 1"');
    }

    // 注册
    v20_6_componentRegistry[name] = {
      componentSet: compSet,
      defaultVariantNode: componentNodes[defaultIdx],
      variantMap: variantMap,
      propertyName: propName
    };
    compCount++;
  }
}

// 把所有 Component Set 挪到画布右侧的 lib holder + preview holder 两个独立面板
// [v20.7+]
//   📦_组件库:        所有 Component Set Variant 平铺 (定义视图,不可切换)
//   🎮_可切换预览:    每 Component 一个 INSTANCE (设计师可右侧切换状态测视觉)
function moveV20_6_ComponentSetsToLibHolder(rightOfX) {
  var libHolder = getV20_6_LibHolder(rightOfX);
  // 先把所有 Component Set 放到 libHolder (这样下方 previewHolder 计算 y 才对)
  for (var name in v20_6_componentRegistry) {
    var entry = v20_6_componentRegistry[name];
    libHolder.appendChild(entry.componentSet);
  }
  // 再创建并填充 previewHolder (此时 libHolder.height 已稳定)
  var previewHolder = getV20_6_PreviewHolder(rightOfX);
  for (var name2 in v20_6_componentRegistry) {
    var entry2 = v20_6_componentRegistry[name2];
    try {
      var preview = entry2.defaultVariantNode.createInstance();
      preview.name = '预览_' + name2;
      previewHolder.appendChild(preview);
    } catch (e) {
      v20_6_componentIssues.push('预览 INSTANCE 创建失败: ' + name2 + ' (' + e.message + ')');
    }
  }
}

// 给 INSTANCE 节点设置 Variant Property
function setV20_6_InstanceVariant(instance, componentName, variantName) {
  var entry = v20_6_componentRegistry[componentName];
  if (!entry) return false;
  if (!entry.variantMap[variantName]) return false;
  try {
    // 动态读 Component Set 当前的 Property 名,以防改名失败
    var compSet = entry.componentSet;
    var propDefs = compSet.componentPropertyDefinitions;
    var actualPropName = entry.propertyName;
    // 如果 entry.propertyName 不在 propDefs 里,说明改名失败,fallback 找第一个 VARIANT property
    if (!propDefs[actualPropName]) {
      for (var pn in propDefs) {
        if (propDefs[pn].type === 'VARIANT') {
          actualPropName = pn;
          break;
        }
      }
    }
    var props = {};
    props[actualPropName] = variantName;
    instance.setProperties(props);
    return true;
  } catch (e) {
    return false;
  }
}

// 取 default Variant 名(用于跳过设置 setProperties)
function getV20_6_DefaultVariantName(componentName) {
  var entry = v20_6_componentRegistry[componentName];
  if (!entry) return null;
  for (var vname in entry.variantMap) {
    if (entry.variantMap[vname] === entry.defaultVariantNode) return vname;
  }
  return null;
}

async function generate(data) {
  nodeReg = {}; frameReg = {};
  missingCompCount = 0; issueList = [];
  compHolder = null; compCount = 0; compCreated = 0; compHolderNextY = 40;
  __absConstraintTotal = 0; __absConstraintSkipped = 0; __absPositioningTotal = 0;

  // [v20.6] Component Set 注册表: name → { componentSet, defaultVariantNode, variantMap: {variantName: componentNode} }
  v20_6_componentRegistry = {};
  v20_6_componentIssues = [];
  v20_6_libHolder = null;

  var libCount = loadLib();
  if (libCount > 0) log('✅ 组件库：' + libCount + ' 个组件');
  else log('⚠ 未找到「组件库」页面，component_ref 将使用占位矩形');

  var screens = data.screens || [], flow = data.flow || [];
  var componentsArr = data.components || [];
  var offsetX = 0, allFrames = [];

  // ── [v20.6] 阶段 A: 读 components 数组,创建 Figma 真 Component Set ──
  if (componentsArr.length > 0) {
    figma.ui.postMessage({ type:'progress', message:'构建 ' + componentsArr.length + ' 个 Component Set...' });
    await buildV20_6_ComponentSets(componentsArr);
  }

  // ── 阶段 B: 创建主场景 + 处理 INSTANCE 节点 ──
  for (var s = 0; s < screens.length; s++) {
    var screen = screens[s];
    var sw = screen.w || screen.width || 1080, sh = screen.h || screen.height || 2400;
    var sname = screen.name||('屏幕_' + (s+1));

    // 自检
    figma.ui.postMessage({ type:'progress', message:'校验: ' + sname });
    var layers = screen.layers || [];
    for (var c = 0; c < layers.length; c++) checkLayer(layers[c], sw, sh, true);

    figma.ui.postMessage({ type:'progress', message:'生成: ' + sname });
    var sf = figma.createFrame();
    sf.name = sname; sf.resize(sw, sh);
    sf.x = offsetX; sf.y = 0;
    // 浮层_ 透明背景
    var isOverlay = sname.indexOf('浮层_') === 0;
    sf.fills = isOverlay ? [] : [{ type:'SOLID', color:G.bg }];
    sf.clipsContent = true;
    figma.currentPage.appendChild(sf);
    frameReg[sname] = sf; reg(sname, sname, sf);

    for (var i = 0; i < layers.length; i++) await buildNode(layers[i], sf, 0, sname);
    allFrames.push(sf);
    offsetX += sw + 160;
  }

  figma.ui.postMessage({ type:'progress', message:'建立 Prototype 连线...' });
  var proto = { linked:0, failed:[] };
  if (flow.length > 0) proto = await applyPrototypeFlow(flow);

  // [v20.6] 把所有 Component Set 挪到画布右侧的 📦_组件库 Frame 里
  if (Object.keys(v20_6_componentRegistry).length > 0) {
    moveV20_6_ComponentSetsToLibHolder(offsetX + 200);
  }

  // 视野要包含主场景 + 组件库
  var viewportFrames = allFrames.slice();
  if (v20_6_libHolder) viewportFrames.push(v20_6_libHolder);
  if (v20_6_previewHolder) viewportFrames.push(v20_6_previewHolder);
  if (viewportFrames.length > 0) figma.viewport.scrollAndZoomIntoView(viewportFrames);

  var totalIssues = issueList.length + proto.failed.length + missingCompCount + v20_6_componentIssues.length;
  var reportLines = [
    '【生成报告】共 ' + screens.length + ' 个屏幕',
    issueList.length === 0 ? '✅ 结构校验全部通过' : ('⚠ 结构问题 ' + issueList.length + ' 项:')
  ];
  for (var k = 0; k < issueList.length; k++) reportLines.push('  • ' + issueList[k]);

  // [v20.6] Component 报告
  if (componentsArr.length > 0 || v20_6_componentIssues.length > 0) {
    reportLines.push('');
    reportLines.push('【Component Set (v20.6)】');
    if (v20_6_componentIssues.length === 0) {
      reportLines.push('✅ ' + Object.keys(v20_6_componentRegistry).length + ' 个 Component Set 创建成功');
      for (var cn in v20_6_componentRegistry) {
        var en = v20_6_componentRegistry[cn];
        var vCount = Object.keys(en.variantMap).length;
        reportLines.push('  • ' + cn + ' (' + vCount + ' Variant, Property=' + en.propertyName + ')');
      }
    } else {
      reportLines.push('⚠ Component 问题 ' + v20_6_componentIssues.length + ' 项:');
      for (var i = 0; i < v20_6_componentIssues.length; i++) reportLines.push('  • ' + v20_6_componentIssues[i]);
    }
  }

  reportLines.push('');
  reportLines.push('【Prototype】✅ 连线 ' + proto.linked + ' 条  ◆ ComponentSet ' + compCreated + ' 个');
  if (proto.failed.length > 0) { reportLines.push('❌ 连线失败:'); for (var f = 0; f < proto.failed.length; f++) reportLines.push('  • ' + proto.failed[f]); }
  if (missingCompCount > 0) reportLines.push('❌ 缺失组件: ' + missingCompCount + ' 个（见黄色占位）');
  reportLines.push('[v20.6] ABS-POS=' + __absPositioningTotal);

  figma.ui.postMessage({ type:'done', count:screens.length, issueCount:totalIssues, report:reportLines.join('\n') });
}

// ── 导出辅助：全局状态（仅导出期间使用）──
var _exportFlow = [];       // 收集所有 flow 条目
var _exportIdMap = {};      // figma node id → node name（全页面）
var _exportCurScreen = '';  // 当前正在导出的顶层 Frame 名称

// 扫描整个当前页面，建立 id → name 映射
function buildIdMap() {
  _exportIdMap = {};
  function scan(node) {
    _exportIdMap[node.id] = node.name;
    if ('children' in node) {
      for (var i = 0; i < node.children.length; i++) scan(node.children[i]);
    }
  }
  for (var i = 0; i < figma.currentPage.children.length; i++) {
    scan(figma.currentPage.children[i]);
  }
}

// ── 导出当前页面 JSON（Figma → wireframe JSON）v20: 新增 reactions + flow ──
// [v20.7+] 用选中 INSTANCE 同步全部 — 替代被新版 Figma 删掉的 "Push to main"
//   1. 当前 selection 必须是 exactly 1 个 INSTANCE
//   2. 取它的 mainComponent (在 Component Set 里就是某个 Variant)
//   3. 把 main 自身 resize 到选中 INSTANCE 的 w/h
//   4. 扫当前 page 所有引用同 mainComponent 的 INSTANCE,全部 resize
//   5. 报告结果
function syncInstanceSizeToMain() {
  var sel = figma.currentPage.selection;
  if (sel.length !== 1) {
    return { ok: false, error: '请只选中 1 个 INSTANCE 节点（当前选中 ' + sel.length + ' 个）' };
  }
  var node = sel[0];
  if (node.type !== 'INSTANCE') {
    return { ok: false, error: '请选中 INSTANCE 节点（当前是 ' + node.type + '）' };
  }
  var main = node.mainComponent;
  if (!main) {
    return { ok: false, error: '此 INSTANCE 找不到 mainComponent（可能引用了已删除组件）' };
  }
  var targetW = Math.round(node.width);
  var targetH = Math.round(node.height);

  // 1. resize main 本身
  try {
    main.resize(targetW, targetH);
  } catch (e) {
    return { ok: false, error: '改 main 尺寸失败: ' + e.message };
  }

  // 2. 扫当前 page 所有同 mainComponent 的 INSTANCE
  var siblingsResized = 0;
  function scan(n) {
    if (n.type === 'INSTANCE' && n.mainComponent && n.mainComponent.id === main.id) {
      if (Math.round(n.width) !== targetW || Math.round(n.height) !== targetH) {
        try {
          n.resize(targetW, targetH);
          siblingsResized++;
        } catch (e) {
          // 单个 resize 失败继续往下,最后报告
        }
      }
    }
    if ('children' in n) {
      for (var i = 0; i < n.children.length; i++) scan(n.children[i]);
    }
  }
  for (var i = 0; i < figma.currentPage.children.length; i++) {
    scan(figma.currentPage.children[i]);
  }

  return {
    ok: true,
    component_name: main.name,
    target_size: { w: targetW, h: targetH },
    siblings_resized: siblingsResized,
    main_resized: true
  };
}

// [v20.7+] 解析 Variant 名为属性对: "状态=常态, 尺寸=499" → { props: {状态:'常态', 尺寸:'499'}, keys: ['状态','尺寸'] }
function parseVariantName(name) {
  var obj = {};
  var keys = [];
  var parts = String(name || '').split(',');
  for (var i = 0; i < parts.length; i++) {
    var p = parts[i].trim();
    if (!p) continue;
    var eq = p.indexOf('=');
    if (eq < 0) continue;
    var k = p.substring(0, eq).trim();
    var v = p.substring(eq + 1).trim();
    if (!(k in obj)) keys.push(k);
    obj[k] = v;
  }
  return { props: obj, keys: keys };
}

function serializeVariantName(parsed) {
  var parts = [];
  for (var i = 0; i < parsed.keys.length; i++) {
    var k = parsed.keys[i];
    parts.push(k + '=' + parsed.props[k]);
  }
  return parts.join(', ');
}

// [v20.7+] 把所选 INSTANCE 按尺寸拆为多个 Variant
//   1. 选 ≥2 个 INSTANCE,必须全引用同一 Component Set
//   2. 按 (w, h) 分组
//   3. 实例数最多的尺寸保留 anchor Variant(并 resize 到该尺寸)
//   4. 其余每个尺寸 clone anchor → resize → append 到 Component Set
//   5. 给 Component Set 加 "尺寸" 属性维度（Variant 名追加 尺寸=h 后缀）
//   6. swapComponent 把每个 INSTANCE 重新指向匹配尺寸的 Variant
function splitInstancesByVariantSize() {
  var sel = figma.currentPage.selection;
  if (sel.length < 2) {
    return { ok: false, error: '请选中 ≥2 个尺寸不同的 INSTANCE（当前 ' + sel.length + ' 个）' };
  }
  for (var i = 0; i < sel.length; i++) {
    if (sel[i].type !== 'INSTANCE') {
      return { ok: false, error: '所有选中节点必须是 INSTANCE（"' + sel[i].name + '" 是 ' + sel[i].type + '）' };
    }
  }

  // 所有 INSTANCE 必须引用同一 Component Set
  var componentSet = null;
  for (var j = 0; j < sel.length; j++) {
    var main = sel[j].mainComponent;
    if (!main) {
      return { ok: false, error: 'INSTANCE "' + sel[j].name + '" 找不到 mainComponent' };
    }
    var setOrComp = (main.parent && main.parent.type === 'COMPONENT_SET') ? main.parent : main;
    if (componentSet === null) {
      componentSet = setOrComp;
    } else if (componentSet.id !== setOrComp.id) {
      return { ok: false, error: '所选 INSTANCE 引用了不同的 Component / Component Set,请只选同一个组件的实例' };
    }
  }
  if (componentSet.type !== 'COMPONENT_SET') {
    return { ok: false, error: '该组件不在 Component Set 里(只有单个 COMPONENT)。请先在 Figma 把它转成 Variants(右键 → Combine as variants),再回来拆分' };
  }

  // 按 (w, h) 分组
  var sizeMap = {};   // "WxH" → { w, h, instances: [] }
  var sizeOrder = []; // 保持插入顺序
  for (var k = 0; k < sel.length; k++) {
    var inst = sel[k];
    var w = Math.round(inst.width);
    var h = Math.round(inst.height);
    var key = w + 'x' + h;
    if (!sizeMap[key]) {
      sizeMap[key] = { w: w, h: h, instances: [] };
      sizeOrder.push(key);
    }
    sizeMap[key].instances.push(inst);
  }
  if (sizeOrder.length < 2) {
    return { ok: false, error: '所选 INSTANCE 尺寸都一样（' + sizeOrder[0] + '),无需拆分' };
  }

  // 按"实例数降序"排,实例最多的尺寸保留为 anchor Variant
  sizeOrder.sort(function(a, b) {
    return sizeMap[b].instances.length - sizeMap[a].instances.length;
  });

  var anchorVariant = sel[0].mainComponent;
  var keepKey = sizeOrder[0];
  var keep = sizeMap[keepKey];

  // 1. anchor Variant + 同尺寸 INSTANCE 都 resize 到 keep
  try {
    anchorVariant.resize(keep.w, keep.h);
  } catch (e) {
    return { ok: false, error: '改 anchor Variant 尺寸失败: ' + e.message };
  }
  keep.instances.forEach(function(inst) {
    try { inst.resize(keep.w, keep.h); } catch (e) {}
  });

  // 2. 给整个 Component Set 加 "尺寸" 属性维度(如果还没有)
  // 现有所有 Variant 的名字补 ", 尺寸=<自身高度>"
  var anchorParsed = parseVariantName(anchorVariant.name);
  if (!('尺寸' in anchorParsed.props)) {
    var setVariants = componentSet.children;
    for (var v = 0; v < setVariants.length; v++) {
      var vNode = setVariants[v];
      var p = parseVariantName(vNode.name);
      if (!('尺寸' in p.props)) {
        var sizeVal = (vNode.id === anchorVariant.id)
          ? String(keep.h)
          : String(Math.round(vNode.height));
        p.props['尺寸'] = sizeVal;
        p.keys.push('尺寸');
        // 单 Variant 无属性场景 fallback
        if (p.keys.length === 1 && p.keys[0] === '尺寸') {
          // OK,只有 尺寸 一个属性
        }
        vNode.name = serializeVariantName(p);
      }
    }
    anchorParsed = parseVariantName(anchorVariant.name);
  } else {
    anchorParsed.props['尺寸'] = String(keep.h);
    anchorVariant.name = serializeVariantName(anchorParsed);
    anchorParsed = parseVariantName(anchorVariant.name);
  }

  // 3. 其余每个尺寸 clone anchor → resize → append → swap INSTANCE
  var newVariantsCreated = [];
  for (var s = 1; s < sizeOrder.length; s++) {
    var sk = sizeOrder[s];
    var grp = sizeMap[sk];

    var newV;
    try {
      newV = anchorVariant.clone();
    } catch (e) {
      return { ok: false, error: 'clone anchor Variant 失败: ' + e.message };
    }

    // 新 Variant 名: 沿用 anchor 其他属性,改 尺寸=<新高>
    var newParsed = parseVariantName(anchorVariant.name);
    newParsed.props['尺寸'] = String(grp.h);
    newV.name = serializeVariantName(newParsed);

    componentSet.appendChild(newV);

    try { newV.resize(grp.w, grp.h); } catch (e) {}

    // 重指向所有同尺寸 INSTANCE
    grp.instances.forEach(function(inst) {
      try {
        inst.swapComponent(newV);
        inst.resize(grp.w, grp.h);
      } catch (e) {}
    });

    newVariantsCreated.push({ name: newV.name, w: grp.w, h: grp.h, instances: grp.instances.length });
  }

  return {
    ok: true,
    component_set: componentSet.name,
    anchor_variant: anchorVariant.name,
    keep_size: { w: keep.w, h: keep.h, instances: keep.instances.length },
    variants_created: newVariantsCreated,
    total_instances: sel.length,
    total_sizes: sizeOrder.length
  };
}

// ── 消息处理 ──
figma.ui.onmessage = function(msg) {
  if (msg.type === 'generate') {
    generate(msg.data).catch(function(e) {
      figma.ui.postMessage({ type:'error', message:String(e) });
    });
  }

  // [v20.7+] 用选中 INSTANCE 同步全部尺寸
  if (msg.type === 'sync_instance_size') {
    var result = syncInstanceSizeToMain();
    if (result.ok) {
      figma.notify('✅ 已同步: ' + result.component_name + ' → ' +
                   result.target_size.w + '×' + result.target_size.h +
                   '（main + ' + result.siblings_resized + ' 个 INSTANCE）',
                   { timeout: 5000 });
    } else {
      figma.notify('❌ ' + result.error, { timeout: 5000, error: true });
    }
    figma.ui.postMessage({ type: 'sync_instance_size_done', result: result });
  }

  // [v20.7+] 按尺寸拆为多 Variant
  if (msg.type === 'split_instance_by_size') {
    var splitResult = splitInstancesByVariantSize();
    if (splitResult.ok) {
      figma.notify('✅ 已拆分: ' + splitResult.component_set + ' → ' +
                   splitResult.total_sizes + ' 个 Variant(' +
                   splitResult.total_instances + ' 个 INSTANCE 已重指向)',
                   { timeout: 5000 });
    } else {
      figma.notify('❌ ' + splitResult.error, { timeout: 5000, error: true });
    }
    figma.ui.postMessage({ type: 'split_instance_by_size_done', result: splitResult });
  }

  if (msg.type === 'export_lib') {
    figma.ui.postMessage({ type:'export_done', data:exportLib() });
  }

  // 📄 导出 JSON：直接复用 buildSceneForRed 的逻辑
  if (msg.type === 'export_json') {
    var result = buildSceneForRed();
    if (result.error) {
      figma.ui.postMessage({ type: 'export_json_done', error: result.error });
    } else {
      // 即使有尺寸警告也允许导出 JSON（仅 .red 生成才阻止），但要打到日志面板
      if (result._size_warnings && result._size_warnings.length) {
        logSizeIssues(result._size_warnings);
        figma.notify('⚠️ INSTANCE 尺寸不一致 ' + result._size_warnings.length +
                     ' 条 — 详情看日志,生成 .red 前需修复', { timeout: 6000 });
      }
      figma.ui.postMessage({ type: 'export_json_done', data: result, screenCount: result.screens.length });
    }
  }

  // 🚀 生成 .red：构造 scene.json，传回 ui.html 由 ui.html 调 Python
  if (msg.type === 'gen_red') {
    var scene = buildSceneForRed();
    if (scene.error) {
      figma.ui.postMessage({ type: 'gen_red_error', message: scene.error });
    } else if (scene._size_warnings && scene._size_warnings.length && !msg.force) {
      // [v20.7+] INSTANCE 尺寸不一致 — 阻止生成 .red,因为父子尺寸会错位
      logSizeIssues(scene._size_warnings);
      figma.notify('⛔ 阻止生成 .red: INSTANCE 尺寸不一致 ' +
                   scene._size_warnings.length + ' 条', { timeout: 8000, error: true });
      figma.ui.postMessage({
        type: 'gen_red_size_blocked',
        warnings: scene._size_warnings,
        scene: scene,
        output_path: msg.output_path,
        message: 'INSTANCE 尺寸与 Component 本体不一致。\n' +
                 '修复方法: 选中 INSTANCE → ⌥⌘Y (Push to main component) → 重新导出。\n' +
                 '若确实需要按当前数据强制生成(可能渲染错位),再次点击生成会带 force 标志。'
      });
    } else {
      figma.ui.postMessage({
        type: 'gen_red_ready',
        scene: scene,
        output_path: msg.output_path
      });
    }
  }

  // 加载存储的输出路径
  if (msg.type === 'load_red_path') {
    figma.clientStorage.getAsync('red_output_path').then(function(val) {
      figma.ui.postMessage({
        type: 'red_path_loaded',
        path: val || '~/Desktop/red_output'
      });
    });
  }

  // 保存输出路径
  if (msg.type === 'save_red_path') {
    figma.clientStorage.setAsync('red_output_path', msg.path);
  }
};
