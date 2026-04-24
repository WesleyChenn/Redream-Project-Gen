# S6 · 自检清单【强制，有 ❌ 必须修正后才能交付】

> 每次生成 JSON 后必须逐项执行，不能只做格式浅检查。

---

## 【第一层：骨架完整性】

```
✅/❌ 【仅录屏】S1 全帧扫描完成（含触摸点识别与翻页类型判断）
✅/❌ 【仅录屏】S2 滚动菜单识别完成（已区分固定区/滚动区/viewport）
✅/❌ S3 骨架表格已输出（含组件库匹配标注）
✅/❌ 骨架无重叠，所有大区 h 加总 = 2400（算术闭环）
✅/❌ 贴底区域从下往上计算 y，未从上往下叠加估算
✅/❌ 所有 h/w 已量测后 × scale（非估算值）
```

## 【第二层：尺寸精度】

```
✅/❌ 所有 w/h/x/y 从截图量测后 × scale，非直接写量测值
✅/❌ 同组控件尺寸一致；对称布局两个按钮 w 相同
✅/❌ 允许误差 ±5%，超出说明量测有误
✅/❌ screens 尺寸用 "w"/"h"（非 width/height）
✅/❌ 录屏帧：H 已排除播放器 UI
✅/❌ 异构列表：每种行类型已分别量测 h
```

## 【第三层：组件合规性】

```
✅/❌ 开始前已加载组件库 JSON，S3 逐一比对后才标注匹配结论
✅/❌ 识别到库组件 → component_ref，未退化为手搓
✅/❌ component_ref 使用前已在 S3 确认组件内部 constraints 为 SCALE/SCALE（可缩放）
✅/❌ 组件内部 constraints 非 SCALE 时，已改为手搓或要求用户先更新组件库
✅/❌ component_ref 输出 w/h = 截图量测 × scale（不使用组件库原始尺寸）
✅/❌ 导航栏 item 数量已通过像素扫描逐个确认，未用「屏幕宽÷估算宽」推断
✅/❌ 骨架表中已备注导航每项名称（项1=xxx, 项2=xxx...），与 JSON 中 导航_项N 一一对应
✅/❌ 导航按钮：导航_项N 命名 + overrides 写入实际文字
✅/❌ 导航双态：当前页用 _选中，其他用 _未选中，未使用旧组件
✅/❌ component_ref 是独立 key
✅/❌ component_ref 未写 layoutSizingHorizontal/Vertical
✅/❌ overrides 字段名与组件内文字节点名 100% 匹配
✅/❌ RECTANGLE 仅用于无组件的纯图片/装饰色块
✅/❌ 角标均已找到父本，与父本在同一 NONE 容器内，未平铺在 AL 容器中
✅/❌ 叠加结构父容器 h/w = 主体组件 h/w（不含附加元素高度）
```

## 【第四层：底板分离与按钮内容居中】

```
✅/❌ 手搓按钮底板结构：大包装 FRAME + 底板_xxx FRAME + 底板_xxx形状 RECTANGLE + 内容区_ FRAME AL
✅/❌ 外层容器底板（卡片/弹窗）：容器 FRAME + 底板_xxx RECTANGLE（不含"形状"，独立使用）
✅/❌ 节点类型区分无误：FRAME 底板_xxx（按钮外壳透明）/ RECTANGLE 底板_xxx形状（按钮内层分级灰）/ RECTANGLE 底板_xxx（外层容器中深灰）
✅/❌ 按钮内层 RECTANGLE 必须含"形状"后缀，外层容器 RECTANGLE 必须不含"形状"
✅/❌ 所有手搓按钮内部均有 内容区_ FRAME（layoutMode: HORIZONTAL/VERTICAL，CENTER/CENTER）
✅/❌ 内容区_ FRAME 的 w/h 与底板完全一致（constraints: SCALE/SCALE）
✅/❌ 按钮内子元素（文字、图标等）均放在 内容区_ 内，不写估算 x/y
✅/❌ 无"一层底"（FRAME 同时有 fill 和 children）
✅/❌ layoutPositioning: ABSOLUTE 仅在 AL 容器内
```

## 【第五层：布局与约束】

```
✅/❌ 所有 FRAME 设置了 layoutMode
✅/❌ primaryAxisSizingMode / counterAxisSizingMode 只用 FIXED / AUTO
✅/❌ 所有 AL FRAME 有 primaryAxisAlignItems
✅/❌ constraints 只在屏幕顶层直接子节点 和 NONE 父容器子节点
✅/❌ VERTICAL 容器内底板 layoutPositioning: ABSOLUTE
✅/❌ VERTICAL 容器内子 FRAME 有 layoutSizingHorizontal: FILL
✅/❌ 弹性缝隙 / SPACE_BETWEEN 使用正确
✅/❌ 无 SPACE_AROUND；无 STRETCH
✅/❌ children 从底到顶排序
```

## 【第六层：Prototype 连线】

```
✅/❌ 导航_页面切换：N×(N-1) 条 slide 连线（全量，每个屏幕的每个非激活Tab都已连线）
✅/❌ 只写视频中实际出现的屏幕，未出现的屏幕不写连线
✅/❌ 导航_状态切换：未生成任何 flow
✅/❌ from_node 名称与 JSON 节点 name 100% 一致
✅/❌ flow 的 from/to 屏幕名在 screens 中存在
✅/❌ 全屏跳转 dissolve，浮层 overlay，浮层关闭 CLOSE
✅/❌ 屏幕类型正确：全屏替换用 界面_，弹窗覆盖用 浮层_
✅/❌ 同一屏幕内无重名节点
✅/❌ 零幻觉：未生成不存在的屏幕或连线
```

## 【第七层：Overflow 滚动】

```
✅/❌ 父容器：overflow + clipsContent: true + primaryAxisSizingMode: FIXED
✅/❌ 子容器：primaryAxisSizingMode: AUTO，是父容器直接 child
✅/❌ 子容器 h > 父容器 h
✅/❌ 子容器 w 已显式指定
✅/❌ 滚动未写进 flow
```

## 【第八层：命名合规】

```
✅/❌ 所有 name 前缀在枚举白名单内
✅/❌ 无非白名单前缀（顶部_/底部_/主体_/区域_/面板_/切图_ 等）
✅/❌ 无残留 切图_底板_ 前缀（方案A: 简化为 底板_）
✅/❌ 浮层_ 屏幕 layers[0] = 遮罩_浮层背景 RECTANGLE 1080×2400
✅/❌ 界面_ 屏幕有全屏背景时 layers[0] = 背景_xxx RECTANGLE 1080×2400
✅/❌ 背景/遮罩未被放进中间弹性区容器内部
✅/❌ 导航按钮统一 导航_项N
✅/❌ TEXT 无多余 w
✅/❌ 无 stroke 属性
✅/❌ 手搓节点 fill 全部省略（无 hex、无 transparent）
✅/❌ component_ref 节点未被错误添加 fill 字段
```

---

⛔ 全部 ✅ 后交付 JSON。有任何 ❌ 必须修正后重新自检，直到全部通过。
