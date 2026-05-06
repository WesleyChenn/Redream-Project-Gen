# 场景创建完整检查清单

从零创建一个完整 .red 场景的标准步骤。每一步都有可直接复制的 CLI 命令。

## CLI 变量

```bash
CLI="Redream/build/bin/Redream/Redream.app/Contents/MacOS/Redream"
# 或 /Applications/Redream.app/Contents/MacOS/Redream
PROJ="path/to/project.redproj"
```

## Step 1: 创建场景文件

```bash
$CLI modify new-scene --scene ccb/XX_界面_名称.red -p $PROJ --enable-rebolt --no-default-timeline
```

生成 .red + .rebolt 两个文件，并直接开启 rebolt；默认不创建 `Default Timeline`。

## Step 2: 修复根节点类型和分辨率

`new-scene` 默认创建 CCNode 根节点，并先继承项目 `designSize` 作为初始分辨率。Figma 流程仍需要修复为目标根节点类型和分辨率集合：

**根节点类型判断规则**：
- 文件名含 `弹窗`、`浮层`、`全屏反馈`、`界面` → CCLayer
- 其他 → CCNode（保持默认）

**修复方法**：使用 Python 脚本一次性替换 baseClass + displayName + resolutions。见 `figma-to-redream.md` Phase 3.3。

修复后：
- CCLayer 场景的 root displayName = "CCLayer"
- CCNode 场景的 root displayName = "CCNode"

## Step 3: 添加节点

**支持 `root` 作为通用 parent 别名**（自动匹配 CCLayer 或 CCNode）：

```bash
# 推荐：使用 root 作为 parent（兼容 CCLayer 和 CCNode 场景）
$CLI modify add-node --scene ccb/XX.red --parent root --type CCSprite --name "背景" -p $PROJ

# 也可以使用具体的 displayName
$CLI modify add-node --scene ccb/XX.red --parent CCLayer --type CCSprite --name "背景" -p $PROJ
```

### 新增：--properties 内联属性（推荐）

一条命令同时创建节点 + 设置属性：

```bash
# 创建带图片和位置的 CCSprite（1 条命令代替 3 条）
$CLI modify add-node --scene ccb/XX.red --parent root --type CCSprite --name "背景" \
  --properties '{"displayFrame":",bg.png","position":"540,1040,0,0,0"}' -p $PROJ

# 创建 REDFile + 设置子场景路径
$CLI modify add-node --scene ccb/XX.red --parent root --type REDFile --name "子场景" \
  --properties '{"redFile":"XX_子ccb.red","position":"400,1750,0,0,0"}' -p $PROJ

# 创建程序绑定节点
$CLI modify add-node --scene ccb/XX.red --parent root --type CCNode --name "定位点" \
  --properties '{"reboltName":"定位点"}' -p $PROJ
```

### 传统方式（仍然支持）

```bash
$CLI modify add-node --scene ccb/XX.red --parent root --type CCSprite --name "背景" -p $PROJ
$CLI modify set-property --scene ccb/XX.red --node "root/背景" --property displayFrame --value ",bg.png" -p $PROJ
$CLI modify set-property --scene ccb/XX.red --node "root/背景" --property position --value "540,1040,0,0,0" -p $PROJ
```

### Batch 模式（最高效，推荐用于多节点场景）

```bash
$CLI modify batch --config scene_ops.json -p $PROJ
```

scene_ops.json 支持 add-node 内联 properties：
```json
[
  {"action":"add-node","scene":"ccb/XX.red","parent":"root","type":"CCSprite","name":"背景",
   "properties":{"displayFrame":",bg.png","position":"540,1040,0,0,0"}},
  {"action":"add-node","scene":"ccb/XX.red","parent":"root","type":"REDFile","name":"子场景",
   "properties":{"redFile":"XX_子ccb.red"}},
  {"action":"keyframe","scene":"ccb/XX.red","timeline":2,"node":"root/背景","property":"Byte","time":0,"value":"0"},
  {"action":"keyframe","scene":"ccb/XX.red","timeline":2,"node":"root/背景","property":"Byte","time":0.5,"value":"255"}
]
```

## Step 4: displayFrame（图片）属性值格式

```
SpriteFrame 属性值格式：
- plist 中的图片: "plistFile.plist,frameName.png"
- 独立图片文件: ",filename.png"（逗号开头，plist 部分留空）
- 空/无图片: ","
```

图片文件必须在 .redproj 配置的 resourcePaths 目录下。

## Step 5: 添加时间线

```bash
# 添加自定义时间线
$CLI modify add-timeline --scene ccb/XX.red --name "动画_入场" --length 1.0 --fps 30 -p $PROJ

# 自循环时，--chain 可直接写时间线名字
$CLI modify add-timeline --scene ccb/XX.red --name "常态_选中状态" --length 1.0 --fps 30 \
  --chain "常态_选中状态" --auto-play true -p $PROJ
```

使用 `--no-default-timeline` 创建的新场景，不需要删除默认时间线，也不需要修 `currentSequenceId`。

仅修复旧场景或旧 CLI 产物时，才执行：

```bash
# 删除默认时间线（旧流程 new-scene 自动创建的）
$CLI modify delete-timeline --scene ccb/XX.red --timeline "Default Timeline" -p $PROJ

# 修复 currentSequenceId（删除 id=0 后必须修复）
sed -i '' '/<key>currentSequenceId<\/key>/{n;s/<integer>0<\/integer>/<integer>1<\/integer>/;}' ccb/XX.red
```

## Step 6: 添加关键帧

```bash
$CLI modify keyframe --scene ccb/XX.red --timeline 2 --node "CCLayer/背景" --property Byte --time 0 --value "0" -p $PROJ
$CLI modify keyframe --scene ccb/XX.red --timeline 2 --node "CCLayer/背景" --property Byte --time 0.5 --value "255" -p $PROJ
```

常用属性和值格式：
| 属性 | 类型 | 值格式 | 示例 |
|------|------|--------|------|
| Position | 位置 | x,y,xUnit,yUnit,corner | "540,1040,0,0,0" |
| ScaleLock | 缩放 | scaleX,scaleY,locked | "1,1,1" |
| Byte | 透明度 | 0-255 | "255" |
| Check | 可见性 | true/false | "true" |
| Degrees | 旋转 | 角度 | "45" |

## Step 7: 配置 Rebolt

**现在支持相对路径！**（也支持绝对路径）

### Rebolt Batch 模式（推荐，最高效）

```bash
$CLI rebolt-modify batch --rebolt ccb/XX.rebolt --config rebolt_ops.json -p $PROJ
```

rebolt_ops.json — 使用 `LAST` 引用上一个 block 的 ID 来链接：
```json
[
  {"tree":"Tree2","path":"stepSlot","type":"BTPlayTimeLineWaitAction",
   "props":{"baseSelect":{"Value":"2","DisplayName":"动画_入场","Type":"Action"}}},
  {"tree":"Tree2","path":"LAST/stepSlot","type":"BTNotificationToCoderAction",
   "props":{"conditionA":"入场动画播完"}}
]
```

### 传统方式（逐条命令）

```bash
# 查看树结构
$CLI rebolt-modify read --rebolt ccb/XX.rebolt --section CustomFunc --json -p $PROJ

# 添加 block（返回 randomID）
$CLI rebolt-modify add-block --rebolt ccb/XX.rebolt --tree Tree0 --path stepSlot --type BTPlayTimeLineWaitAction -p $PROJ

# 设置 block 属性
$CLI rebolt-modify set-prop --rebolt ccb/XX.rebolt --block-id <ID> --prop baseSelect --value '{"Value":"2","DisplayName":"动画_入场","Type":"Action"}' -p $PROJ
```

## Step 8: 验证

```bash
$CLI inspect check -p $PROJ --json
$CLI rebolt validate -p $PROJ --json
```
