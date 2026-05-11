# Rebolt Block 速查表

## 常用 Block 类型

### 时间线播放

| Block | 用途 | 关键属性 |
|-------|------|---------|
| BTPlayTimeLineAction | 播放时间线（不等待） | baseSelect |
| BTPlayTimeLineWaitAction | 播放时间线（等待完成） | baseSelect |
| BTPlayTimeLineActionWithCallBack | 播放时间线（带回调） | baseSelect, CallBackInfo |

baseSelect 值格式（JSON 字符串）：
```json
{"Value":"<sequenceId>","DisplayName":"<时间线名>","Type":"Action"}
```
注意：Value 是 sequenceId 的**字符串形式**（如 "2"），不是时间线名称。

### 通知程序

| Block | 用途 | 关键属性 |
|-------|------|---------|
| BTNotificationToCoderAction | 发送事件通知 | conditionA = 通知名称 |
| BTNotificationToCoderWithParamAction | 发送带参数通知 | conditionA = 通知名, 额外参数 |
| BTNotificationNodeToCoderAction | 发送节点引用 | conditionA = displayName, `baseSelect.Value = reboltId`, `baseSelect.DisplayName = reboltName` |

### 条件控制

| Block | 用途 | 关键属性 |
|-------|------|---------|
| BTIFElseControlAction | 条件分支 | conditionA (BTBoolSlot), sectionA, sectionB |
| BTEqualOperatorAction | 相等比较 | conditionA (左值), conditionB (右值) |

### 变量操作

| Block | 用途 | 关键属性 |
|-------|------|---------|
| BTCoderVariableAction | 读取变量 | titleLabel = 变量名, VarScope = "Scene" |
| BTDataVarSetAction | 写入变量 | titleLabel = 变量名, value = 值 |
| BTFuncVariableAction | 读取函数参数 | titleLabel = 参数名 |

### 节点操作

| Block | 用途 | 关键属性 |
|-------|------|---------|
| BTNodeShowAction | 显示节点 | `baseSelect.Value = reboltId`, `baseSelect.DisplayName = reboltName` |
| BTNodeHiddenAction | 隐藏节点 | `baseSelect.Value = reboltId`, `baseSelect.DisplayName = reboltName` |
| BTButtonClickFuncAction | 按钮点击 | `mathSelector.Value = reboltId`, `mathSelector.DisplayName = reboltName` |
| BTButtonEnableAction | 按钮启用/禁用 | `baseSelect.Value = reboltId`, `baseSelect.DisplayName = reboltName`, `enabled` |
| BTSpriteImageAction | 设置单图 | baseSelect, TitleInput |
| BTSpritePlistAction | 设置图片集帧 | baseSelect, pathInput, frameNameInput |
| BTLabelTitleAction | 设置文本 | baseSelect, content |

节点 selector 的 CLI 规则：

- `Value` 一律写 live `reboltId`
- `DisplayName` 一律对应 live `reboltName`
- `BTButtonClickFuncAction` 用 `mathSelector`，其余大多数节点块用 `baseSelect`
- `rebolt-modify add-block` / `set-prop` 会按 paired `.red` 校验 selector，并自动同步 `DisplayName`

换图块选择规则：

- 运行时给的是单图路径 → `BTSpriteImageAction`，写 `TitleInput`
- 运行时给的是 plist + frame 名 → `BTSpritePlistAction`，写 `pathInput` + `frameNameInput`
- 不要把单图场景硬写成 plist 块

### Slot 类型

| Slot | 说明 | 用途 |
|------|------|------|
| stepSlot | 顺序执行 | 链接下一个 action |
| conditionA | 布尔条件 | IF 判断、比较左值 |
| conditionB | 比较右值 | 比较目标值 |
| sectionA | 真分支 | IF 为真时执行 |
| sectionB | 假分支 | IF 为假时执行 |

## 常见模式

### 模式 1：初始化 — 绑定节点
```
Tree0 (初始化):
  BTNotificationNodeToCoderAction (conditionA="节点名", baseSelect={Value=reboltId, DisplayName=reboltName})
  └─ stepSlot → BTNotificationNodeToCoderAction (下一个绑定)
     └─ stepSlot → ...
```

### 模式 2：播放时间线 + 通知
```
BTPlayTimeLineWaitAction (baseSelect={"Value":"2",...})
└─ stepSlot → BTNotificationToCoderAction (conditionA="动画播完")
```

### 模式 3：条件分支播放不同时间线
```
BTIFElseControlAction
├─ conditionA → BTEqualOperatorAction
│   ├─ conditionA → BTCoderVariableAction (titleLabel="P-变量名", VarScope="Scene")
│   └─ conditionB = "1"
├─ sectionA → BTPlayTimeLineWaitAction (timeline A)
│   └─ stepSlot → BTNotificationToCoderAction ("完成")
└─ sectionB → BTPlayTimeLineWaitAction (timeline B)
    └─ stepSlot → BTNotificationToCoderAction ("完成")
```

### 模式 4：按钮点击 → 禁用 → 通知 → 恢复
```
BTButtonClickFuncAction (mathSelector={Value=reboltId, DisplayName=reboltName})
└─ stepSlot → BTButtonEnableAction (enabled=false)
   └─ stepSlot → BTNotificationToCoderAction ("按钮被点击")
      └─ stepSlot → BTButtonEnableAction (enabled=true)
```

## Rebolt Batch 模式（推荐）

使用 `rebolt-modify batch` 一次性构建完整的行为树逻辑：

```bash
$CLI rebolt-modify batch --rebolt ccb/XX.rebolt --config rebolt_ops.json -p $PROJ
```

### JSON 配置格式

```json
[
  {"tree":"Tree0","path":"stepSlot","type":"BTNotificationNodeToCoderAction",
   "props":{"conditionA":"定位点名","baseSelect":{"Value":"<reboltId>","DisplayName":"<reboltName>"}}},
  {"tree":"Tree0","path":"LAST/stepSlot","type":"BTNotificationNodeToCoderAction",
   "props":{"conditionA":"另一个定位点","baseSelect":{"Value":"<nextReboltId>","DisplayName":"<nextReboltName>"}}}
]
```

### `LAST` 引用

`LAST` 自动替换为上一条操作创建的 block 的 randomID，用于链接 stepSlot：

```json
[
  {"tree":"Tree2","path":"stepSlot","type":"BTPlayTimeLineWaitAction",
   "props":{"baseSelect":{"Value":"2","DisplayName":"动画_入场","Type":"Action"}}},
  {"tree":"Tree2","path":"LAST/stepSlot","type":"BTNotificationToCoderAction",
   "props":{"conditionA":"入场动画播完"}}
]
```

### 条件分支示例

```json
[
  {"tree":"Tree3","path":"stepSlot","type":"BTIFElseControlAction"},
  {"tree":"Tree3","path":"LAST/conditionA","type":"BTEqualOperatorAction"},
  {"tree":"Tree3","path":"LAST/conditionA","type":"BTCoderVariableAction",
   "props":{"titleLabel":"P-变量名","VarScope":"Scene"}},
  {"tree":"Tree3","path":"LAST/sectionA","type":"BTPlayTimeLineWaitAction",
   "props":{"baseSelect":{"Value":"4","DisplayName":"时间线A","Type":"Action"}}}
]
```

注意：`LAST` 始终指向**前一条**操作创建的 block。条件分支中要注意 path 的嵌套层级。
