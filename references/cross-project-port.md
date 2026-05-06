# 跨项目移植活动模块 — 经验总结

基于将 ArrowsGameDev 的 JigsawPlay（拼图式闯关收集）模块移植到 EmptyDemo2（找茬游戏）的实战经验。

## 移植清单

跨项目移植一个完整的游戏活动模块，需要处理以下层面：

| 层面 | 内容 | 常见陷阱 |
|------|------|----------|
| **C++ 库** | 独立库（如 `code_JigsawPlay/`）直接复制 | 库内无项目特有依赖，可直接编译 |
| **C++ 集成层** | Controller/DelegateImpl（如 `JigsawGame/`） | 引用源项目特有类（需重写适配） |
| **Redream 资源** | .red/.rebolt + publish 产物 .redream + Rebolt_BT XML | 见下方详细陷阱 |
| **图片/字体/音效** | plist 图集、fnt 字体、spine 动画、音效 | 运行时找不到→crash |
| **配置文件** | JSON 配置（如 `JigsawConfig_默认.json`） | 路径和命名约定 |
| **资源打包** | `资源拷贝配置.csv` + ResourcePacker | 目录覆盖问题 |
| **A/B 分组** | `FindObject.redabproj` + `RedABTest.hpp/.cpp` | 分组函数声明+实现+配置三处同步 |
| **主页集成** | HomeScene 分流 + CtlMainView 通知处理 | 节点绑定、坐标系、初始化时序 |

## Rebolt_BT ID 冲突

### 问题
两个项目的 `.rebolt` 文件中 `randomID`（tree ID）可能重名。publish 后生成的 `Rebolt_BT/*.xml` 文件以 `randomID.xml` 命名，资源打包时后加载的会覆盖先加载的同名文件。

### 解决方案
移植前用脚本重新生成所有 `randomID`，避免与目标项目冲突：

```python
# 只重新生成主 TreeList 的 randomID，不要动 RedFileList
# RedFileList 存储的是子场景的快照，其 ID 必须和子场景实际的 tree ID 匹配
def regen_main_tree_ids(rebolt_data, existing_ids):
    # 遍历 TreeList，替换冲突的 randomID
    # 同步更新 CustomFunc 中的 tree 引用
    # 同步更新 funcHeadID 引用
    # 不要碰 RedFileList 内部的 randomID！
```

### 关键规则
- **RedFileList 中的 randomID 不能改** — 它们是子场景的快照，改了会导致子场景 BT 找不到
- 改完 rebolt 后必须重新 `publish` 生成新的 BT XML
- publish 前清理 `_ccbi/` 目录避免残留旧文件

## 资源打包覆盖问题

### 问题
`资源拷贝配置.csv` 中多个资源模块都有 `_ccbi` 目录（含 `Rebolt_BT/` 子目录），打包器按顺序处理，后处理的会覆盖先处理的同名子目录。

### 解决方案
1. 确保 Rebolt_BT 文件无 ID 冲突（见上）
2. 配置中使用 `是否保留子目录结构=-`（扁平化），所有 BT XML 和 .redream 文件都扁平化到 `bin/` 根目录
3. 运行时 Redream 引擎会同时搜索 `<filename>.xml` 和 `Rebolt_BT/<filename>.xml`

### publish 输出目录
- `redproj` 中 `publishDirectory` 字段控制输出目录（如 `ccbi` 或 `_ccbi`）
- 资源拷贝配置中的源路径必须和 publish 输出目录一致
- 用 CLI 修改：`modify project --publish-dir _ccbi`

## Scale9Sprite Crash

### 问题
加载 .redream 场景时，Scale9Sprite 引用的 plist 图集未预加载，`setSpriteFrame(nullptr)` 导致 crash。

### 解决方案
在加载场景前手动预加载 plist：

```cpp
SpriteFrameCache::getInstance()->addSpriteFramesWithFile("Arrows_主页.plist");
auto* layer = RUReboltLayer::createReboltLayer("WorldJig_主页界面.redream");
```

## Rebolt 变量缺失 Crash

### 问题
源项目的 rebolt 引用了目标项目没有的 `P-` 变量（如 `P-是否继续`），运行到 `getCoderString` 时 assert 失败。

### 解决方案
- 方案 A：在 C++ 中提前设置变量 `setCoderDataVar("P-是否继续", "No")`
- 方案 B：用 CLI 给 rebolt 添加变量 `rebolt-modify add-var --var-name "P-是否继续"`

## Rebolt 函数缺失 Crash

### 问题
目标项目 C++ 代码调用 `runBehaviacWhitFunName("默认动画")`，但源项目的 rebolt 中没有这个函数。

### 解决方案
用 CLI 批量添加空函数：

```bash
for func in "默认动画" "检查网络弱提示" "下载中"; do
    Redream rebolt-modify add-func --rebolt <file>.rebolt --func-name "$func"
done
```

## 节点绑定与坐标系

### 问题
JigsawPlay 的渲染依赖正确的父节点设置：
- `jigsawNode` — 棋盘渲染的父节点，需要有正确的 `contentSize`
- `showNode` — 展示区/相册弹窗的父节点
- `jigsawShowNode` — 奖杯合成动画的父节点，**必须是全屏节点**（百分比布局依赖父节点尺寸）
- `activeNode` — 活动入口按钮的父节点
- `effectNode` — 特效层

### 关键教训

1. **棋盘节点必须有 contentSize** — `contentSize=(0,0)` 会导致 `tilemapCenter=(0,0)`，棋盘渲染在左下角
2. **奖杯动画需要全屏父节点** — `拼图式闯关_拼图棋盘.red` 是 CCLayer（百分比全屏 100%x100%），如果父节点 contentSize 不是全屏，百分比定位会偏移
3. **区分 showNode 和 jigsawShowNode** — GameDirector 用 `getShowNode()` 给展示区/相册，用 `getJigsawShowNode()` 给 Jigsaw 的 `_showNode`（奖杯动画的父节点）。搞混会导致动画位置错误
4. **收集动画用世界坐标** — `P-色块嵌入坐标x/y` 是通过 `convertToWorldSpace` 计算的，`_cellLayer` 的父节点必须和世界坐标系对齐

### 推荐做法
在目标项目的主页 .red 中新建专用定位节点（用 CLI），和源项目的布局对齐：

```bash
# 拼图棋盘定位点（居中，有尺寸）
modify add-node --type CCNode --name "拼图节点" --rebolt-name "拼图节点"
set-property --property position --value "50,50,0,2,2"
set-property --property contentSize --value "777.6,898.56,0,0"
set-property --property anchorPoint --value "0.5,0.5"

# 拼图弹窗层（全屏，给奖杯动画用）
modify add-node --type CCNode --name "拼图弹窗层" --rebolt-name "拼图弹窗层"
set-property --property position --value "50,50,0,2,2"
set-property --property contentSize --value "100,100,2,2"
set-property --property anchorPoint --value "0.5,0.5"
```

## 初始化时序

### 问题
Redream 场景的节点绑定通知（`绑定XX节点`）和 C++ 延迟初始化的时序必须匹配。

### 关键规则
1. `显示主界面` rebolt 函数中的绑定通知在 `scheduleOnce` 延迟回调**之前**发送
2. `入场完成` 通知可能不触发（代码注释已说明）
3. 初始化逻辑放在 `scheduleOnce` 延迟回调中，此时所有绑定通知已完成
4. 从游戏场景返回主页时，需要清理单例状态（`resetJigsawSystem`），否则悬空指针 crash

## C++ 集成层适配

### 问题
源项目的 Controller/DelegateImpl 引用了大量源项目特有类。

### 解决方案
- `DelegateImpl` 通常很干净（纯 getter/setter），直接复制后删除不存在的 include
- `Controller` 需要重写，保留核心 `GameDirector` 调用，移除源项目的 UI/业务依赖
- 在析构函数中清理 `GameDirector` 防止 scene 切换后悬空指针

## 资源搜索路径

### 问题
新模块的资源文件（.redream/.plist/.fnt 等）在运行时找不到。

### 解决方案
在 `AppDelegate.cpp` 中添加搜索路径：

```cpp
FileUtils::getInstance()->addSearchPath("Resources/res_arrows_trophy", true);
```

## Publish 工作流

每次修改 .red 或 .rebolt 后必须执行完整流程：

```bash
# 1. 清理旧的导出
rm -rf res_xxx/_ccbi

# 2. 重新导出
Redream publish -p res_xxx/xxx.redproj --force

# 3. 重新打包资源
cmake --build . --target ResourcePacker

# 4. 编译
cmake --build . --target MyGame
```

跳过任何一步都可能导致运行时使用旧的 BT/redream 文件。
