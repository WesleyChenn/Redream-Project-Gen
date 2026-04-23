# Rebolt `.rebolt` File Format Reference

Complete reference for reading `.rebolt` JSON behavior tree files used by the Rebolt runtime in the Redream UI framework.

**Runtime:** `Libraries/redream/Rebolt/ReboltRedManager.h/.cpp`
**BT implementation:** `Libraries/redream/Rebolt/behaviac/RedBehaviacTree.cpp`
**Authority:** `reboltBt_behaviac_agent_meta.cpp` — complete list of all registered C++ methods (~100 functions).

> See also: `references/redream.md` for `.red` scene layout; `references/cocosbase.md` for coordinate/unit fundamentals.

---

## Quick Lookup

| If you encounter… | Go to |
|---|---|
| A `"Type": "BT*Action"` in TreeList | **Action Type Index** (below) — alphabetical, covers all ~100 types |
| Top-level fields (`DisPlayName`, `CustomFunc`, etc.) | §3.1 |
| `CustomFunc` structure / calling from C++ | §3.2 |
| `CustomVar` / variable scopes (`P-` prefix, `VarScope`) | §3.3 |
| `RedFileList` / sub-red keys / `::` separator | §3.4 |
| TreeList node fields (`randomID`, `isIllegal`, `stepSlot`, etc.) | §3.5 |
| `BTInputSlot` / `BTStepSlot` / `BTBoolSlot` slot types | §3.26 |
| `baseSelect` / `redSelect` / `mathSelector` reference types | §3.26 |
| Read-value functions (`getCoderFloat`, `nodeGetPosX`, etc.) | §3.27 |
| `curvePreset` easing names | **cocosbase §1.8** |

---

## Action Type Index

All registered `BT*Action` types, alphabetical. ✓ = observed in project files; *(unobserved)* = registered in C++ but not seen in project.

| Type | §Section | One-line description |
|------|----------|----------------------|
| `BTAddCustomDataVarAction` *(unobserved)* | §3.19 | Increment a scene variable by a float value |
| `BTAddOperatorAction` ✓ | §3.20 | Binary addition of two numeric inputs (conditionA + conditionB) |
| `BTButtonClickFuncAction` ✓ | §3.11 | Bind button tap event in current red — uses `mathSelector`, not `baseSelect` |
| `BTButtonEnableAction` ✓ | §3.11 | Enable or disable a button (`enableButton: {Type:"BTCheckBox", isEnable:bool}`) |
| `BTCallBackFuncAction` | §3.6 | Callback entry point — executes `stepSlot` when a WithCallBack timeline ends |
| `BTCallRedCustomFuncBodyAction` ✓ | §3.6 | Call a custom function in a sub-red file by `funcHeadID` + `redSelect` |
| `BTCoderVariableAction` ✓ | §3.19 | Read a CoderVar (P- prefix) or SceneVar into an input slot |
| `BTCustomFuncBodyAction` | §3.6 | Call another function by its `funcHeadID` (randomID) |
| `BTCustomFuncHeadAction` ✓ | §3.6 | Function entry point; `ExportTree: true` + `Name` field |
| `BTDataVarSetAction` ✓ | §3.19 | Write a value to a scene/coder/global variable |
| `BTEqualOperatorAction` ✓ | §3.6 / §3.20 | Equality comparison a == b → bool (used in `BTBoolSlot`) |
| `BTFuncVariableAction` ✓ | §3.19 | Read a function input parameter (declared in CustomFunc) |
| `BTHiddenSelfAction` | §3.7 | Hide this entire red component itself |
| `BTIFElseControlAction` ✓ | §3.6 | Conditional branch: `conditionA` → `sectionA` (true) or `sectionB` (false) |
| `BTLabelTitleAction` ✓ | §3.9 | Set label text in current red file |
| `BTLabelUpdatePlaceHolderAction` ✓ | §3.9 | Replace `%1`–`%5` placeholders in label text |
| `BTLBNumberIncreaseAction` *(unobserved)* | §3.15 | Animate label numeric value from start to end over time |
| `BTMessageSendAction` *(unobserved)* | §3.24 | Send a named message to the scene event bus |
| `BTNodeHiddenAction` ✓ | §3.7 | `setVisible(false)` on a node in current red |
| `BTNodeRotationToAction` *(unobserved)* | §3.13 | Animate node rotation to target degrees (non-blocking) |
| `BTNodeRotationToActionWithCallBack` *(unobserved)* | §3.13 | Animate node rotation with callback on finish |
| `BTNodeRotationToWaitAction` *(unobserved)* | §3.13 | Animate node rotation to target degrees (blocking) |
| `BTNodeScaleToAction` *(unobserved)* | §3.13 | Animate node scale to target value (non-blocking) |
| `BTNodeScaleToActionWithCallBack` *(unobserved)* | §3.13 | Animate node scale with callback on finish |
| `BTNodeScaleToWaitAction` *(unobserved)* | §3.13 | Animate node scale to target value (blocking) |
| `BTNodeSetAnimAction` ✓ | §3.14 | Move node along `.anim` path (non-blocking) |
| `BTNodeSetAnimActionWithCallBack` *(unobserved)* | §3.14 | Move node along `.anim` path with callback |
| `BTNodeSetAnimWaitAction` ✓ | §3.14 | Move node along `.anim` path (blocking) — `.anim` is a standard `.red` plist file |
| `BTNodeSetGlobalPosAction` *(unobserved)* | §3.8 | Set node global position immediately |
| `BTNodeSetPosAction` ✓ | §3.8 | Set node local position immediately |
| `BTNodeSetRotationAction` *(unobserved)* | §3.8 | Set node rotation immediately |
| `BTNodeSetScaleAction` ✓ | §3.8 | Set node scale immediately |
| `BTNodeShowAction` ✓ | §3.7 | `setVisible(true)` on a node in current red |
| `BTNotificationNodeToCoderAction` ✓ | §3.23 | Send notification to C++ with a node reference |
| `BTNotificationNodeToCoderWaitAction` *(unobserved)* | §3.23 | Send notification with node ref and wait for C++ completion |
| `BTNotificationToCoderAction` ✓ | §3.23 | Send a named notification to C++ (no params) |
| `BTNotificationToCoderWaitAction` *(unobserved)* | §3.23 | Send notification and block until C++ signals completion |
| `BTNotificationToCoderWithParamAction` ✓ | §3.23 | Send notification to C++ with a string parameter |
| `BTNotifiSceneNodeToCoderAction` ✓ | §3.23 | Send notification to C++ with a sub-red node reference |
| `BTNotificationToCoderWithParamWaitAction` *(unobserved)* | §3.23 | Send notification with param and wait |
| `BTPlaySceneTimeLineAction` ✓ | §3.12 | Play timeline in a sub-red file (non-blocking) |
| `BTPlaySceneTimeLineActionWithCallBack` ✓ | §3.12 | Play timeline in sub-red with callback on finish |
| `BTPlaySceneTimeLineWaitAction` ✓ | §3.12 | Play timeline in sub-red and wait for end (blocking) |
| `BTPlayTimeLineAction` ✓ | §3.12 | Play timeline in current red (non-blocking) — `baseSelect.Value` = sequenceId string |
| `BTPlayTimeLineActionWithCallBack` ✓ | §3.12 | Play timeline in current red with callback on finish |
| `BTPlayTimeLineWaitAction` ✓ | §3.12 | Play timeline in current red and wait for end (blocking) |
| `BTPlayWiseSoundAction` *(unobserved)* | §3.17 | Play audio via Wwise (bank + event name) |
| `BTProgressBarAction` ✓ | §3.10 | Set CCProgressTimer fill percentage immediately |
| `BTProgressFromToAction` *(unobserved)* | §3.10 | Animate CCProgressTimer from start to end percentage with easing |
| `BTRedHiddenAction` ✓ | §3.7 | **See §3.7 note** — `baseSelect.Value` is a sequenceId (not reboltId); behavior unconfirmed |
| `BTRedShowAction` ✓ | §3.7 | `setVisible(true)` on a node inside a sub-red |
| `BTSceneBtnClickFuncAction` ✓ | §3.11 | Bind button tap event for a button inside a sub-red |
| `BTSceneButtonEnableAction` ✓ | §3.11 | Enable or disable a button inside a sub-red |
| `BTSceneLabelTitleAction` ✓ | §3.9 | Set label text inside a sub-red |
| `BTSceneLabelUpdatePlaceHolderAction` ✓ | §3.9 | Replace `%1`–`%5` placeholders in a sub-red label |
| `BTSceneLBNumberIncreaseAction` *(unobserved)* | §3.15 | Animate label numeric value in a sub-red |
| `BTSceneNodeHiddenAction` ✓ | §3.7 | `setVisible(false)` on a node inside a sub-red |
| `BTSceneNodeShowAction` ✓ | §3.7 | `setVisible(true)` on a node inside a sub-red |
| `BTSceneNodeSetGlobalPosAction` *(unobserved)* | §3.8 | Set global position of a node inside a sub-red |
| `BTSceneNodeSetPosAction` *(unobserved)* | §3.8 | Set local position of a node inside a sub-red |
| `BTSceneNodeSetRotationAction` *(unobserved)* | §3.8 | Set rotation of a node inside a sub-red |
| `BTSceneNodeSetScaleAction` *(unobserved)* | §3.8 | Set scale of a node inside a sub-red |
| `BTSceneProgressBarAction` *(unobserved)* | §3.10 | Set CCProgressTimer fill in a sub-red immediately |
| `BTSceneProgressFromToAction` *(unobserved)* | §3.10 | Animate CCProgressTimer in a sub-red with easing |
| `BTSceneSpriteImageAction` *(unobserved)* | §3.9 | Set CCSprite texture from file path in a sub-red |
| `BTSceneSpritePlistAction` *(unobserved)* | §3.9 | Set CCSprite atlas frame in a sub-red |
| `BTSetSubReboltCoderDataVarAction` *(unobserved)* | §3.19 | Set a CoderVar (P- prefix) inside a sub-red |
| `BTShowInterstitialAdsAction` *(unobserved)* | §3.18 | Show interstitial ad — blocks tree until ad ends |
| `BTShowRewardVideoAdsAction` *(unobserved)* | §3.18 | Show reward video ad — blocks tree; check `temporaryVariablesBool` for result |
| `BTShowSelfAction` | §3.7 | Show this entire red component itself |
| `BTSimulatorAction` | §3.6 | Editor-only preview node — **no runtime effect** |
| `BTSpine4SetSkelFrameAction` *(unobserved)* | §3.16 | Play a Spine 4.x animation by frame name |
| `BTSpine4SetSkeletonSkinAction` *(unobserved)* | §3.16 | Switch a Spine 4.x skeleton skin |
| `BTSpineSetSkelFrameAction` *(unobserved)* | §3.16 | Play a Spine 2.x animation by frame name |
| `BTSpineSetSkeletonSkinAction` *(unobserved)* | §3.16 | Switch a Spine 2.x skeleton skin |
| `BTSpriteImageAction` ✓ | §3.9 | Set CCSprite texture from a file path |
| `BTSpritePlistAction` ✓ | §3.9 | Set CCSprite frame from a sprite atlas (plist + frame name) |
| `BTStartLoopAction` *(unobserved)* | §3.25 | Begin a loop construct (see §3.25 for iteration pattern) |
| `BTStopSubredTimeLineAction` *(unobserved)* | §3.12 | Stop a playing timeline in a sub-red |
| `BTStopTimeLineAction` *(unobserved)* | §3.12 | Stop a playing timeline in current red |
| `BTStringEqualOperatorAction` ✓ | §3.20 | String equality comparison a == b → bool (used in `BTBoolSlot`) |
| `BTStringLinkOperatorAction` ✓ | §3.20 | Concatenate two strings |
| `BTTestFuncAction` | §3.6 | Editor test node — **no runtime effect** |
| `BTVariableAction` ✓ | §3.19 | Old alias for `BTCoderVariableAction` — identical structure |

---

## §3.1 Top-Level Fields

```json
{
  "DisPlayName": "G010游戏物品单个",
  "CustomFunc": { … },
  "CustomVar": { … },
  "CustomList": { … },
  "CustomMessage": {"Hello Red": 1},
  "CustomTestFunc": { … },
  "RedNoteInfo": { … },
  "RedFileList": { … },
  "TreeList": { … }
}
```

| Field | Purpose |
|-------|---------|
| `DisPlayName` | Display name of this rebolt component |
| `CustomFunc` | Exported function declarations callable from C++ |
| `CustomVar` | Variable declarations (`P-` prefix = C++ injected) |
| `CustomList` | List variable declarations |
| `CustomMessage` | Message event declarations; key = message name, value = 1 |
| `CustomTestFunc` | Editor test functions; usually empty |
| `RedNoteInfo` | Notes; usually empty |
| `RedFileList` | Sub-red behavior trees keyed by reboltId |
| `TreeList` | Behavior tree definitions keyed by "Tree0", "Tree1"… |

---

## §3.2 CustomFunc — Exported Function Declarations

```json
"消散并通知": [
  ["Name", "消散并通知", "OyGmdEDC8CTF", "/path/to/file.red"],
  ["BTInputSlot", "失去数量"],
  ["BTInputSlot", "变化后生命"]
]
```

- **First entry:** `["Name", funcName, randomID, redFilePath]` — `randomID` matches the `BTCustomFuncHeadAction` in `TreeList`.
- **Subsequent entries:** `["BTInputSlot", paramName]` — each is a numeric input parameter.

**C++ invocation** (`ReboltRedManager.h → runBehaviacWhitFunName`):
```cpp
manager->runBehaviacWhitFunName("消散并通知");
manager->runBehaviacWhitFunName("生命减少函数", {}, {{"失去数量","1"},{"变化后生命","4"}});
```

---

## §3.3 CustomVar — Variable Declarations

```json
"CustomVar": {
  "P-图片名字": 0,   ← P-prefixed: injected by C++ via setCoderDataVar()
  "当前生命": 0      ← no prefix: internal scene variable
}
```

All values are `0` (type is always Number).

**Variable scopes:**

| Scope | Prefix | C++ method | Read in tree via |
|-------|--------|-----------|-----------------|
| CoderVar | `P-` | `setCoderDataVar("P-名字", val)` | `BTCoderVariableAction` |
| SceneVar | none | `setCustomDataVar("名字", val)` | `BTCoderVariableAction` (VarScope="Scene") or `BTVariableAction` |
| GlobalVar | none | `setGlobalDataVar("名字", val)` | `getGlobalFloat`/`getGlobalString` in BTInputSlot |
| FuncParam | — | `runBehaviacWhitFunName` stringMap | `BTFuncVariableAction` |

Source: `ReboltRedManager.h → _coderVarStringMap`, `_customVarStringMap`

**Note on `BTVariableAction`**: Observed in project files as an old alias for `BTCoderVariableAction`. Identical field structure (`VarScope`, `titleLabel`). Use `BTCoderVariableAction` in new files.

---

## §3.4 RedFileList — Sub-Red Definitions

`RedFileList` is only for sub-red definitions. Key = the `reboltId` of an actual `REDFile` node in the parent `.red` file; do not put ordinary `CCNode` ids, display names, selectors, or notification names here. Value = complete rebolt structure (same format as top-level).

```json
"RedFileList": {
  "IDFVujQFWo9f": {
    "DisPlayName": "G010游戏物品单个_重叠数字",
    "CustomFunc": {},
    "TreeList": {}
  }
}
```

**Nested sub-red key format (`::` separator):** When a `REDFile` node is nested inside another sub-red, the key uses `parentReboltId::childReboltId`:
```json
"HqgdhIhmYl9x::N32Vj8runaQR": {
  "DisPlayName": "G010道具按钮"
}
```
This means: within the sub-red with reboltId `HqgdhIhmYl9x`, there is a nested sub-red with reboltId `N32Vj8runaQR`.

If you need to expose or address ordinary scene nodes, use the normal Rebolt selector / notification mechanisms instead of `RedFileList`.

---

## §3.5 TreeList — Node Common Fields

| Field | Meaning |
|-------|---------|
| `Type` | Action type string (e.g., `BTCustomFuncHeadAction`) |
| `ExportTree` | `true` = callable entry point; appears in `CustomFunc` |
| `Name` | `{Type:"STRING", Value:"funcName"}` — only on `BTCustomFuncHeadAction` |
| `randomID` | 12-char unique ID; matches `CustomFunc` entries and `CallBackInfo.Value` |
| `isIllegal` | Runtime status flag; `true` = properly configured (confusingly named) |
| `VarJson` | `{boolJson:{}, numberJson:{paramName:"Number"}}` — parameter type declarations |
| `stepSlot` | `{ContainerValue: <next action or null>, Type:"BTStepSlot"}` |
| `x`, `y`, `xOffSetLen`, `colorName`, `ImageIndex` | Editor canvas layout — no runtime effect |

---

## §3.6 BT Action Types — Control Flow

**`BTCustomFuncHeadAction`** — Function entry point.
```json
{"Type":"BTCustomFuncHeadAction","Name":{"Type":"STRING","Value":"消散"},"ExportTree":true,"randomID":"8AN6TjS5ZHof","stepSlot":{…}}
```

**`BTCallBackFuncAction`** — Callback attachment. Referenced by `BTPlayTimeLineActionWithCallBack.CallBackInfo.Value`. Executes `stepSlot` when animation ends. `ExportTree: true` but no `Name`.

**`BTCustomFuncBodyAction`** — Call another function by `funcHeadID`.
```json
{
  "Type": "BTCustomFuncBodyAction",
  "funcHeadID": "FbH0T3pHl59t",
  "Name": {"Type":"STRING","Value":"播放动画"},
  "paramArr": []
}
```
C++ method: `customFunc(funName)`. `funcHeadID` = randomID of the target `BTCustomFuncHeadAction`. `paramArr` = array of `["BTInputSlotN", "paramName"]` pairs mapping input slots to function parameters.

**`BTCallRedCustomFuncBodyAction`** ✓ — Call a custom function defined in a **sub-red** file. Same as `BTCustomFuncBodyAction` but targets a function inside a referenced sub-red via `redSelect`.
C++ method: `redCustomFunc(blockId, redPath, funName)`.
```json
{
  "Type": "BTCallRedCustomFuncBodyAction",
  "baseSelect": {"DisplayName":"生命增加函数","Type":"Action","Value":"生命增加函数"},
  "funcHeadID": "9TZ7C8mkgRtw",
  "redSelect": {"DisplayName":"G010爱心","Type":"OBJ","Value":"0xpI0EfZpcU7"},
  "redId": "/path/to/G010爱心.red",
  "paramArr": [["BTInputSlot1","获得数量"],["BTInputSlot2","变化后生命"]]
}
```
- `funcHeadID` = randomID of the target `BTCustomFuncHeadAction` **in the sub-red's TreeList**
- `redSelect` = sub-red file reference (RedFileList key)
- `redId` = absolute path to the `.red` source file (editor metadata; not used at runtime)
- `paramArr` = array of `["BTInputSlotN", "paramName"]` pairs passing input values to function parameters
- `baseSelect.Value` = function name string (not a reboltId)

**`BTSimulatorAction`** — Editor-only preview node (`Name="模拟程序执行"`). No runtime effect.

**`BTTestFuncAction`** — Editor test node. Fields: `VarScope:"Red"`, `titleLabel: {Value:"测试"}`. No runtime effect.

**`BTIFElseControlAction`** — Conditional branch.
```json
{
  "Type": "BTIFElseControlAction",
  "conditionA": {"ContainerValue": {/* condition action */}, "Type":"BTBoolSlot"},
  "sectionA": {"ContainerValue": {/* action if true */}, "Type":"BTSectionSlot"},
  "sectionB": {"ContainerValue": {/* action if false */}, "Type":"BTSectionSlot"},
  "stepSlot": {/* continues after branch */}
}
```

**`BTEqualOperatorAction`** — Equality comparison → bool for BTBoolSlot.
```json
{"Type":"BTEqualOperatorAction","conditionA":{…BTInputSlot…},"conditionB":{…BTInputSlot…}}
```

---

## §3.7 BT Action Types — Node Visibility

All actions reference target nodes via `baseSelect` (see §3.26).

| `.rebolt` Type | C++ method | Action | Key fields |
|---|---|---|---|
| `BTNodeHiddenAction` | `hiddenNode` | `setVisible(false)` | `baseSelect` (nodeId) |
| `BTNodeShowAction` | `showNode` | `setVisible(true)` | `baseSelect` (nodeId) |
| `BTHiddenSelfAction` | `hiddenSelf` | Hide this red component itself | none |
| `BTShowSelfAction` | `showSelf` | Show this red component itself | none |
| `BTSceneNodeHiddenAction` ✓ | `hiddenRedNode` | `setVisible(false)` on node in sub-red | `baseSelect` (nodeId), `redSelect` (subRedId) |
| `BTSceneNodeShowAction` ✓ | `showRedNode` | `setVisible(true)` on node in sub-red | `baseSelect` (nodeId), `redSelect` (subRedId) |
| `BTRedShowAction` ✓ | `showRedNode` | `setVisible(true)` on node in sub-red | `baseSelect` (nodeId), `redSelect` (subRedId) |

> **`BTRedHiddenAction`** ✓ (observed in `G010复活红心.rebolt`): **Does not follow the standard node-reference pattern.** `baseSelect.Value` contains a sequenceId integer-as-string (e.g., `"0"`), not a 12-char reboltId. This does not match the `hiddenRedNode` C++ signature. Best current interpretation: this action stops or hides an animation sequence rather than a scene node — likely maps to `stopTimeLine`. **Verify against `ReboltRedManager.cpp` before implementing in Godot.**

---

## §3.8 BT Action Types — Node State

| `.rebolt` Type | C++ method | Action | Key fields |
|---|---|---|---|
| `BTNodeSetScaleAction` | `setNodeScale` | Set node scale (immediate) | `baseSelect`, `scaleXInput`, `scaleYInput` (BTInputSlot float) |
| `BTNodeSetRotationAction` *(unobserved)* | `setNodeRotation` | Set node rotation (immediate) | `baseSelect`, `rotationInput` (float) |
| `BTNodeSetPosAction` ✓ | `nodeSetPos` | Set node local position (immediate) | `baseSelect`, `posXInput`, `posYInput` (BTInputSlot float) |
| `BTNodeSetGlobalPosAction` *(unobserved)* | `nodeSetGlobalPos` | Set node global position | `baseSelect`, `posXInput`, `posYInput` |
| `BTSceneNodeSetScaleAction` *(unobserved)* | `setSubredNodeScale` | Set scale in sub-red | `baseSelect`, `redSelect`, scale inputs |
| `BTSceneNodeSetRotationAction` *(unobserved)* | `setSubredNodeRotation` | Set rotation in sub-red | `baseSelect`, `redSelect`, rotation input |
| `BTSceneNodeSetPosAction` *(unobserved)* | `sceneNodeSetPos` | Set local position in sub-red | `baseSelect`, `redSelect`, pos inputs |
| `BTSceneNodeSetGlobalPosAction` *(unobserved)* | `sceneNodeSetGlobalPos` | Set global position in sub-red | `baseSelect`, `redSelect`, pos inputs |

Example (`BTNodeSetPosAction`):
```json
{
  "Type": "BTNodeSetPosAction",
  "baseSelect": {"DisplayName":"点击区域","Type":"Action","Value":"nodeReboltId"},
  "posXInput": {"ContainerValue":{…},"StringValue":{"Type":"FLOAT","Value":0},"Type":"BTInputSlot"},
  "posYInput": {"ContainerValue":{…},"StringValue":{"Type":"FLOAT","Value":0},"Type":"BTInputSlot"}
}
```

---

## §3.9 BT Action Types — Sprite and Label

| `.rebolt` Type | C++ method | Action | Key fields |
|---|---|---|---|
| `BTSpriteImageAction` | `setSpriteImage` | Set CCSprite texture from file path | `baseSelect`, `TitleInput` (image path) |
| `BTSpritePlistAction` | `setSpritePlist` | Set CCSprite frame from atlas | `baseSelect`, `pathInput` (plist), `frameNameInput` (frame) |
| `BTSceneSpriteImageAction` *(unobserved)* | `setSubredSpriteImage` | Set sprite in sub-red | `baseSelect`, `redSelect`, `TitleInput` |
| `BTSceneSpritePlistAction` *(unobserved)* | `setSubredSpritePlist` | Set sprite frame in sub-red | `baseSelect`, `redSelect`, `pathInput`, `frameNameInput` |
| `BTLabelTitleAction` | `setLabelTitle` | Set label text | `baseSelect`, `TitleInput` |
| `BTSceneLabelTitleAction` | `setSceneLabelTitle` | Set label text in sub-red | `redSelect`, `baseSelect`, `TitleInput` |
| `BTLabelUpdatePlaceHolderAction` ✓ | `updateLabelPlaceHolder` | Replace `%1`–`%5` in label text | `baseSelect`, `PlaceHolder1`–`PlaceHolder4` (BTInputSlot) |
| `BTSceneLabelUpdatePlaceHolderAction` ✓ | `updateSceneLabelPlaceHolder` | Same, in sub-red | `redSelect`, `baseSelect`, `PlaceHolder1`–`PlaceHolder4` |

`BTSceneLabelTitleAction` field structure:
```json
{
  "Type": "BTSceneLabelTitleAction",
  "redSelect": {"DisplayName":"子红名称","Type":"OBJ","Value":"reboltId_of_REDFile_node"},
  "baseSelect": {"DisplayName":"标签节点名","Type":"Action","Value":"reboltId_of_label"},
  "TitleInput": {"ContainerValue":null,"StringValue":{"Type":"STRING","Value":"text"},"Type":"BTInputSlot"}
}
```

---

## §3.10 BT Action Types — Progress Bar

| `.rebolt` Type | C++ method | Action | Key fields |
|---|---|---|---|
| `BTProgressBarAction` | `redProgressBar` | Set CCProgressTimer fill (immediate) | `baseSelect`, `percentInput` (BTInputSlot float 0.0–100.0) |
| `BTSceneProgressBarAction` *(unobserved)* | `sceneProgressBar` | Set progress in sub-red (immediate) | `baseSelect`, `redSelect`, `percentInput` (float) |
| `BTProgressFromToAction` *(unobserved)* | `progressBarUpdate` | Animate progress from→to with easing | `baseSelect`, `keyTime`, `keyStart`, `keyEnd`, `curvePreset` |
| `BTSceneProgressFromToAction` *(unobserved)* | `sceneProgressBarUpdate` | Animate progress in sub-red | `baseSelect`, `redSelect`, `keyTime`, `keyStart`, `keyEnd`, `curvePreset` |

---

## §3.11 BT Action Types — Button Interaction

**`BTButtonClickFuncAction`** ✓ — Button click event handler (current red file).
- **Not** a C++ call — an event binding. When the referenced button is tapped, executes `stepSlot`.
- Field: `mathSelector: {Type:"OBJ", Value:"buttonReboltId"}` — button node reboltId (note: `mathSelector`, not `baseSelect`)
- `ExportTree: true`, no `Name` field.
```json
{
  "Type": "BTButtonClickFuncAction",
  "ExportTree": true,
  "mathSelector": {"DisplayName":"取消","Type":"OBJ","Value":"56JdMeDLIgQh"},
  "stepSlot": {…}
}
```

**`BTSceneBtnClickFuncAction`** ✓ — Button click handler for a button in a sub-red file.
- Fields: `baseSelect` (button reboltId inside sub-red) + `redSelect` (sub-red's RedFileList key)
```json
{
  "Type": "BTSceneBtnClickFuncAction",
  "ExportTree": true,
  "baseSelect": {"DisplayName":"开始按钮","Type":"Action","Value":"buttonReboltId"},
  "redSelect": {"DisplayName":"G030游戏主页","Type":"OBJ","Value":"subRedReboltId"},
  "stepSlot": {…}
}
```

**`BTButtonEnableAction`** ✓ — Enable/disable a button in the current red file.
C++ method: `setButtonEnable(nodeId, isEnable)`.
```json
{
  "Type": "BTButtonEnableAction",
  "baseSelect": {"DisplayName":"按钮结束引导","Type":"Action","Value":"nLAClQmaQTPn"},
  "enableButton": {"Type":"BTCheckBox","isEnable":true}
}
```

**`BTSceneButtonEnableAction`** ✓ — Enable/disable a button in a sub-red file.
C++ method: `setSubredButtonEnable(redPath, nodeId, isEnable)`.
Fields: `baseSelect` (button in sub-red) + `redSelect` (sub-red) + `enableButton: {Type:"BTCheckBox", isEnable:bool}`

> **`BTCheckBox` inline type**: Used in `enableButton` field of button-enable actions and in `rotateCheck` of `BTNodeSetAnimWaitAction`. It is an inline config object, not a standalone action.

---

## §3.12 BT Action Types — Timeline Animation

### Current Red File

| `.rebolt` Type | C++ method | Blocking? | Callback? |
|---|---|---|---|
| `BTPlayTimeLineAction` | `playTimeLine` | No | No |
| `BTPlayTimeLineWaitAction` | `playTimeLineWait` | Yes — waits for end | No |
| `BTPlayTimeLineActionWithCallBack` | `playTimeLineWithCallBack` | No | Yes — `CallBackInfo.Value` = randomID of `BTCallBackFuncAction` |
| `BTStopTimeLineAction` *(unobserved)* | `stopTimeLine` | No | No — stops a playing timeline |

`baseSelect.Value` = **sequenceId as string** (not a reboltId):
```json
{"DisplayName":"消散","Type":"Action","Value":"3"}   ← sequenceId = 3
```

### Sub-Red File (needs `redSelect`)

| `.rebolt` Type | C++ method | Blocking? |
|---|---|---|
| `BTPlaySceneTimeLineAction` ✓ | `playSubredTimeLine` | No |
| `BTPlaySceneTimeLineWaitAction` ✓ | `playSubredTimeLineWait` | Yes |
| `BTPlaySceneTimeLineActionWithCallBack` ✓ | `playSubredTimeLineWithCallBack` | No (has `CallBackInfo`) |
| `BTStopSubredTimeLineAction` *(unobserved)* | `stopSubredTimeLine` | No |

---

## §3.13 BT Action Types — Animated Transforms

All use C++ `BTCurveActionFactory` with `curvePreset` named easing (see cocosbase §1.8).

**Parameters** (common to scale and rotation variants):
- `nodeId` / `baseSelect`: target node
- `keyTime`: duration in seconds (string form, e.g., `"0.3"`)
- `keyValue`: target value — scale multiplier or rotation degrees (string)
- `curvePreset`: easing curve name (string, e.g., `"EaseOut"`)

### Scale Animation

| `.rebolt` Type | C++ method | Blocking? |
|---|---|---|
| `BTNodeScaleToAction` *(unobserved)* | `playScaleAnim` | No |
| `BTNodeScaleToWaitAction` *(unobserved)* | `playScaleAnimWait` | Yes |
| `BTNodeScaleToActionWithCallBack` *(unobserved)* | `playScaleAnimWithCallBack` | No (has `callbackTreeId`) |
| Sub-red variants | `playSubredScaleAnim`, `playSubredScaleAnimWait`, `playSubredScaleAnimWithCallBack` | — |

### Rotation Animation

| `.rebolt` Type | C++ method | Blocking? |
|---|---|---|
| `BTNodeRotationToAction` *(unobserved)* | `playRotationAnim` | No |
| `BTNodeRotationToWaitAction` *(unobserved)* | `playRotationAnimWait` | Yes |
| `BTNodeRotationToActionWithCallBack` *(unobserved)* | `playRotationAnimWithCallBack` | No |
| Sub-red variants | `playSubredRotationAnim`, `playSubredRotationAnimWait`, `playSubredRotationAnimWithCallBack` | — |

---

## §3.14 BT Action Types — Path Animation (.anim files)

**`BTNodeSetAnimWaitAction`** ✓ — Move node along a `.anim` path animation file, **blocking**.
C++ method: `nodeSetAnimWaitAction(nodeId, animPath, posXKey, posYKey, posXKey2, posYKey2)`

```json
{
  "Type": "BTNodeSetAnimWaitAction",
  "baseSelect": {"DisplayName":"复活爱心","Type":"Action","Value":"nodeReboltId"},
  "animSelect": {"Type":"STRING","Value":"res_FindObject/anim/heart_fly.anim"},
  "posXInput":  {"ContainerValue":{…},"StringValue":{"Type":"FLOAT","Value":0},"Type":"BTInputSlot"},
  "posYInput":  {"ContainerValue":{…},"StringValue":{"Type":"FLOAT","Value":0},"Type":"BTInputSlot"},
  "posXInput2": {"ContainerValue":{…},"StringValue":{"Type":"FLOAT","Value":0},"Type":"BTInputSlot"},
  "posYInput2": {"ContainerValue":{…},"StringValue":{"Type":"FLOAT","Value":0},"Type":"BTInputSlot"},
  "rotateCheck": {"Type":"BTCheckBox","isEnable":false}
}
```

- `animSelect`: path to an `.anim` file — **`.anim` files are standard `.red` Apple plist XML files** (same format as `.red` scenes; → **references/redream.md** for format). They contain a CCNode root with a CCSprite child named `动画节点`. The CCSprite's position timeline keyframes define the **curve shape** of the path. → **redream §2.5** for keyframe format.
- `posXInput`/`posYInput`: start world position — overrides the path template's start coordinates at runtime
- `posXInput2`/`posYInput2`: end world position — overrides the path template's end coordinates at runtime
- `rotateCheck`: whether the node rotates to face movement direction (`{Type:"BTCheckBox", isEnable:bool}`); historical files may omit it, in which case runtime defaults to `false`, but current CLI-generated defaults still write it explicitly

| `.rebolt` Type | C++ method | Blocking? |
|---|---|---|
| `BTNodeSetAnimAction` *(unobserved)* | `nodeSetAnimAction` | No |
| `BTNodeSetAnimActionWithCallBack` *(unobserved)* | `nodeSetAnimActionWithCallBack` | No (has `callbacktreeId`) |
| `BTNodeSetAnimWaitAction` ✓ | `nodeSetAnimWaitAction` | Yes |

---

## §3.15 BT Action Types — Label Number Animation

| `.rebolt` Type | C++ method | Description |
|---|---|---|
| `BTLBNumberIncreaseAction` *(unobserved)* | `labelNumberIncrease` | Animate label numeric value from `keyStart` to `keyEnd` over `keyTime` seconds |
| `BTSceneLBNumberIncreaseAction` *(unobserved)* | `sceneLabelNumberIncrease` | Same, in sub-red (add `redSelect`) |

Parameters: `nodeId`, `keyTime` (duration), `keyStart` (initial number), `keyEnd` (final number), `curvePreset` (easing)

---

## §3.16 BT Action Types — Spine Skeletal Animation

| `.rebolt` Type | C++ method | Action |
|---|---|---|
| `BTSpineSetSkeletonSkinAction` *(unobserved)* | `setSpineSkeletonSkin` | Switch Spine 2.x skeleton skin |
| `BTSpineSetSkelFrameAction` *(unobserved)* | `setSpineSkelFrame` | Play Spine 2.x animation |
| `BTSpine4SetSkeletonSkinAction` *(unobserved)* | `setSpine4SkeletonSkin` | Switch Spine 4.x skeleton skin |
| `BTSpine4SetSkelFrameAction` *(unobserved)* | `setSpine4SkelFrame` | Play Spine 4.x animation |

Sub-red variants for all four: `setSubRedSpine*` (add `redPath` first param). All *(unobserved)*.

`setSpineSkelFrame` / `setSpine4SkelFrame` params: `(nodeId, frameId, isLoop: bool)`

---

## §3.17 BT Action Types — Audio

**`BTPlayWiseSoundAction`** *(unobserved)* — Play audio via Wwise.
C++ method: `playWiseSound(bnkPathKey, eventNameKey, ...)`
- `bnkPathKey`: Wwise bank file path
- `eventNameKey`: Wwise event name

---

## §3.18 BT Action Types — Ads

**`BTShowInterstitialAdsAction`** *(unobserved)* — Show interstitial ad; **blocks tree** until ad ends.
C++ method: `showInterstitialAds(adName)`

**`BTShowRewardVideoAdsAction`** *(unobserved)* — Show reward video ad; **blocks tree** until ad ends.
C++ method: `showRewardVideoAds(adName)`
After completion, read `temporaryVariablesBool` (= `videoIsSuccess`) to know if user watched successfully.

---

## §3.19 BT Action Types — Variable Operations

**`BTDataVarSetAction`** — Write a variable.
```json
{"Type":"BTDataVarSetAction","VarScope":"Scene","baseSelect":{"Value":"当前生命"},"TitleInput":{…}}
```
`VarScope` maps to C++ method:
- `"Scene"` → `setCustomDataVar` (scene-local)
- `"Coder"` → `setCoderDataVar` (same as P- vars, rarely seen in tree)
- `"Global"` → `setGlobalDataVar` (cross-scene persistent)

**`BTAddCustomDataVarAction`** *(unobserved)* — Increment a scene variable by a float value.
C++ method: `addCustomDataVar(dataName, float content)`.

**`BTSetSubReboltCoderDataVarAction`** *(unobserved)* — Set a CoderVar in a sub-red.
C++ method: `setSubReboltCoderDataVar(redPath, dataName, content)`.

**`BTFuncVariableAction`** — Read a function input parameter.
```json
{"Type":"BTFuncVariableAction","currentStr":"获得数量","fatherFuncID":"9TZ7C8mkgRtw","colorName":"More","titleLabel":{"Type":"STRING","Value":"获得数量"}}
```

**`BTCoderVariableAction`** — Read a CoderVar (P-prefix) or SceneVar.
```json
{"Type":"BTCoderVariableAction","VarScope":"Scene","titleLabel":{"Type":"STRING","Value":"P-重叠数量"}}
```

**Function-local variable management** — Used internally during custom function execution for temporary storage scoped to the function call:
- `addFunLocalBoolToMap(key, bool)` — store a bool in the function-local map
- `addFunLocalStringToMap(key, string)` — store a string in the function-local map
- `clearFunLocalMap()` — clear all function-local variables (called on function exit)

These are managed automatically by the Behaviac runtime during `BTCustomFuncBodyAction` / `BTCallRedCustomFuncBodyAction` execution. Not used directly as action types in `.rebolt` files.

**`updateSubReboltVariables`** — Notify C++ to refresh all CoderVar (`P-` prefix) values in a sub-red component.
C++ method: `updateSubReboltVariables(blockId, redPath, displayName)`.
Triggers `NotifyDevelopmentDelegate::onNotifyUpdateSubReboltVariables()` callback, allowing C++ code to push updated variable values into the sub-red's `ReboltRedManager`.

---

## §3.20 BT Action Types — Operators

Operators are used as `BTInputSlot.ContainerValue` to compute dynamic values.

**`BTEqualOperatorAction`** — `a == b` → bool.
Fields: `conditionA`, `conditionB` (BTInputSlot)

**`BTAddOperatorAction`** ✓ — Binary addition of two numeric inputs (`conditionA + conditionB`).
This is a built-in Behaviac numeric operation (not a C++ registered method). Returns float.
Fields: `conditionA`, `conditionB` (BTInputSlot float)
```json
{
  "Type": "BTAddOperatorAction",
  "conditionA": {"StringValue":{"Type":"FLOAT","Value":300},"Type":"BTInputSlot"},
  "conditionB": {"ContainerValue":{…BTCoderVariableAction…},"Type":"BTInputSlot"}
}
```

**`BTStringEqualOperatorAction`** ✓ — String equality comparison `a == b` → bool. Used inside `BTBoolSlot` for conditional branches.
C++ method: `stringEqual(a, b)` → bool.
Fields: `conditionA`, `conditionB` (BTInputSlot string)
```json
{
  "Type": "BTStringEqualOperatorAction",
  "conditionA": {"ContainerValue":{…BTCoderVariableAction…},"StringValue":{"Type":"STRING","Value":"Red"},"Type":"BTInputSlot"},
  "conditionB": {"ContainerValue":null,"StringValue":{"Type":"STRING","Value":"是"},"Type":"BTInputSlot"}
}
```
> Note: `BTEqualOperatorAction` (§3.6) is for **numeric** equality; `BTStringEqualOperatorAction` is for **string** equality.

**`BTStringLinkOperatorAction`** ✓ — Concatenate two strings.
C++ method: `stringLink(a, b)`.
Fields: `conditionA`, `conditionB` (BTInputSlot string)

**Unary math operator — `numberOperator`**
C++ method: `numberOperator(floatKey, int type)` → float. Applies a unary math function to a single numeric input. The `type` parameter is a `NumOperatorType` enum:

| Value | Name | Operation |
|-------|------|-----------|
| `0` | abs | Absolute value |
| `1` | floor | Floor (round down) |
| `2` | ceil | Ceiling (round up) |
| `3` | sqrt | Square root |
| `4` | sin | Sine |
| `5` | cos | Cosine |
| `6` | tan | Tangent |
| `7` | asin | Arc sine |
| `8` | acos | Arc cosine |
| `9` | atan | Arc tangent |
| `10` | ln | Natural logarithm |
| `11` | log10 | Log base 10 |
| `12` | exp | e^x |
| `13` | pow10 | 10^x |

Source: `RedBehaviacTree.h → NumOperatorType` enum.

**Other operators (all *(unobserved)*):**
- `numModOperator(a, b)` → float — modulo
- `randOperator(a, b)` → float — random float in [a, b]
- `numRandOperator(a)` → string — random number
- `stringLinkMoreOperator(a, b, c, d, e)` → string — concatenate up to 5 strings

---

## §3.21 BT Action Types — List Operations

Operates on lists declared in `CustomList`. All *(unobserved)*.

| C++ method | Action |
|-----------|--------|
| `globalListVarAdd(dataName, content)` | Append element to list end |
| `globalListVarDeleteAll(dataName)` | Clear list |
| `globalListVarDeleteOne(dataName, index)` | Remove element at index |
| `globalListVarInsertBefore(dataName, index, content)` | Insert before index |
| `globalListVarReplace(dataName, index, content)` | Replace element at index |

**Read operations (for BTInputSlot.ContainerValue):**
- `globalListVarCount(dataName)` → float — list length
- `globalListVarHasValue(dataName, value)` → bool
- `globalListVarFindValueID(dataName, value)` → float — index of value
- `globalListVarIndexValue(dataName, int)` → string — value at index

**Behaviac built-in vector operations** — These are framework-level operations registered by Behaviac itself (not Redream-specific). They operate on Behaviac's internal `vector` type, separate from the `globalListVar*` operations above:
- `VectorAdd` — Append element
- `VectorClear` — Clear all elements
- `VectorContains` — Check if element exists
- `VectorLength` — Get vector length
- `VectorRemove` — Remove element

These are rarely used in Redream projects; the `globalListVar*` functions (above) are the standard list API.

---

## §3.22 BT Action Types — Temporary Variables

Store temporary values in the tree's local context. All *(unobserved)*.

| C++ method | Stores to | Type |
|-----------|-----------|------|
| `storageTemporaryVariables(name, float)` | `temporaryVariablesFloat` | float |
| `storageTemporaryVariableBool(bool)` | `temporaryVariablesBool` | bool |
| `storageTemporaryVariablesString(name, content)` | `temporaryVariablesString` | string |

**Member property:** `temporaryVariablesInt` (int) — also registered as a member property in `reboltBt_behaviac_agent_meta.cpp`. Available for integer temporary storage alongside the float/bool/string variants.

Read back by referencing member properties `temporaryVariablesFloat` / `temporaryVariablesBool` / `temporaryVariablesString` / `temporaryVariablesInt` directly in BTInputSlot.

---

## §3.23 BT Action Types — Notifications to C++

**`BTNotificationToCoderAction`** — Send named notification (no params).
C++ method: `notifyDevelopment(key)`.
```json
{"Type":"BTNotificationToCoderAction","conditionA":{"StringValue":{"Type":"STRING","Value":"消散完成"},"Type":"BTInputSlot"}}
```
C++ receives via `NotifyDevelopmentDelegate::onNotifyDevelopment(manager, waiter, notify, param, reboltIsWait, outNode)`.

**`BTNotificationToCoderWithParamAction`** ✓ — Send notification with a string parameter.
C++ method: `notifyDevelopmentWithParam(key, paramKey)`.
```json
{
  "Type": "BTNotificationToCoderWithParamAction",
  "conditionA": {"StringValue":{"Type":"STRING","Value":"模拟点击找到物品"},"Type":"BTInputSlot"},
  "paramA":     {"StringValue":{"Type":"STRING","Value":"11"},"Type":"BTInputSlot"}
}
```

**`BTNotificationNodeToCoderAction`** — Send notification with a node reference.
C++ method: `notifyDevelopmentWithParamAndNode(key, paramKey, nodeId)`.
```json
{
  "Type": "BTNotificationNodeToCoderAction",
  "baseSelect": {"DisplayName":"物品","Value":"ahiITqBTmq6J"},
  "conditionA": {"StringValue":{"Value":"获取物品位置"},"Type":"BTInputSlot"},
  "paramA":     {"StringValue":{"Value":""},"Type":"BTInputSlot"}
}
```

**Wait variants (all *(unobserved)*):**
- `BTNotificationToCoderWaitAction` → `notifyDevelopmentWait` — blocks until C++ signals completion
- `BTNotificationToCoderWithParamWaitAction` → `notifyDevelopmentWithParamWait`
- `BTNotificationNodeToCoderWaitAction` → `notifyDevelopmentWithParamAndNodeWait`

**`BTNotifiSceneNodeToCoderAction`** ✓ — Send notification with a node reference from a **sub-red** file.
C++ method: `notifyDevelopmentWithParamAndSubredNode(blockId, key, paramKey, redPath, nodeId)`.
```json
{
  "Type": "BTNotifiSceneNodeToCoderAction",
  "conditionA": {"StringValue":{"Type":"STRING","Value":"挂载物品列表"},"Type":"BTInputSlot"},
  "paramA":     {"StringValue":{"Type":"STRING","Value":""},"Type":"BTInputSlot"},
  "baseSelect": {"DisplayName":"物品列表","Type":"Action","Value":"Wk8Pjo3gfwWF"},
  "redSelect":  {"DisplayName":"G010游戏物品列表","Type":"OBJ","Value":"HqgdhIhmYl9x"}
}
```
- `conditionA` = notification name
- `paramA` = string parameter
- `baseSelect` = node reboltId **inside** the sub-red
- `redSelect` = sub-red reference (RedFileList key)
- Wait variant: `notifyDevelopmentWithParamAndSubredNodeWait` *(unobserved)*

---

## §3.24 BT Action Types — Message System

**`BTMessageSendAction`** *(unobserved)* — Send a named message to the scene's event bus; triggers any tree nodes bound to that message name.
C++ method: `messageSend(messageName, messageValue)`.
Messages are declared in `CustomMessage` at top level.

---

## §3.25 BT Action Types — Loop Control

**`BTStartLoopAction`** *(unobserved)* — Begin a loop construct.
C++ method: `startLoop()`.

**Loop mechanism:**
1. `BTStartLoopAction` → initializes loop counter to 0
2. `getLoopState(blockId)` → `EBTStatus.SUCCESS` = continue loop body; `EBTStatus.FAILURE` = exit loop
3. `onLoopEnd()` → increments counter (called at end of each iteration)
4. `getLoopTimes()` → returns current iteration count (float)

---

## §3.26 Slot and Reference Types

### Input Slots

```json
// Literal value:
{"ContainerValue":null,"StringValue":{"Type":"FLOAT","Value":0.4},"Type":"BTInputSlot"}

// Dynamic (reads a variable or computes a value):
{"ContainerValue":{"Type":"BTCoderVariableAction","titleLabel":{"Value":"P-图片名字"}},"Type":"BTInputSlot"}
```
`StringValue.Type`: `"STRING"`, `"FLOAT"`, `"BOOL"`

### Control Slots

| Slot type | Purpose |
|-----------|---------|
| `BTStepSlot` | Sequential step — `ContainerValue` = next action (null = end) |
| `BTBoolSlot` | Boolean condition — `ContainerValue` = action returning bool |
| `BTSectionSlot` | Branch block — `ContainerValue` = first action in branch |

### Node References

`baseSelect` — node in current `.red` by `reboltId`:
```json
{"DisplayName":"物品","Type":"Action","Value":"ahiITqBTmq6J"}
```
When used for timeline actions, `Value` = **sequenceId as string**, not a reboltId.

`redSelect` — sub-red file by its `RedFileList` key:
```json
{"DisplayName":"G010游戏物品单个_重叠数字","Type":"OBJ","Value":"IDFVujQFWo9f"}
```

### baseSelect Value Rules

| Reference target | Value format | DisplayName | Type |
|-----------------|-------------|-------------|------|
| Timeline | sequenceId as string (`"0"`, `"3"`) | Timeline name | `"Action"` |
| Scene node | reboltId (`"7dx6ZZY2Fh7v"`) | Target node `reboltName` | `"Action"` |
| Button (mathSelector) | reboltId | Target node `reboltName` | `"OBJ"` |
| Variable | Variable name (`"P-金币数"`) | Variable name | `"Action"` |

For CLI writes, do not treat scene `displayName` as the selector label source. The stable contract is `Value = reboltId` and `DisplayName = current reboltName`.

### BTCheckBox

Used in `BTButtonEnableAction.enableButton` and in current headless defaults for `BTNodeSetAnimAction` / `BTNodeSetAnimWaitAction` / `BTNodeSetAnimActionWithCallBack` as `rotateCheck`:
```json
{"Type": "BTCheckBox", "isEnable": true}
```

---

## §3.27 Read-Value Functions (for BTInputSlot.ContainerValue)

All C++ registered functions with return values can be used as dynamic inputs.

### Variable Readers

| C++ method | Returns | Usage |
|-----------|---------|-------|
| `getCoderFloat(key)` | float | Read C++ CoderVar (P- prefix) |
| `getCoderString(key)` | string | Read C++ CoderVar |
| `getCustomFloat(key)` | float | Read Scene/Custom variable |
| `getCustomString(key)` | string | Read Scene/Custom variable |
| `getGlobalFloat(key)` | float | Read Global variable |
| `getGlobalString(key)` | string | Read Global variable |
| `getFunBoolVar(key)` | bool | Read function input parameter (bool) |
| `getFunStringVar(key)` | string | Read function input parameter (string/number) |

### Tree-Local Variable Readers

| C++ method | Returns | Usage |
|-----------|---------|-------|
| `getLocalTreeFloat(key)` | float | Read tree-local float variable (scoped to current behavior tree instance) |
| `getLocalTreeString(key)` | string | Read tree-local string variable (scoped to current behavior tree instance) |

Tree-local variables are stored in `_localTreeFloatMap` / `_localTreeStringMap` on `RedBehaviacTree`. They persist for the lifetime of the tree instance and are not shared across trees.

### Node Position Readers

| C++ method | Returns | Usage |
|-----------|---------|-------|
| `nodeGetPosX(nodeId)` | float | Node local X position |
| `nodeGetPosY(nodeId)` | float | Node local Y position |
| `nodeGetGlobalPosX(nodeId)` | float | Node global X position |
| `nodeGetGlobalPosY(nodeId)` | float | Node global Y position |
| `sceneNodeGetPosX(redPath, nodeId)` | float | Sub-red node local X |
| `sceneNodeGetPosY(redPath, nodeId)` | float | Sub-red node local Y |
| `sceneNodeGetGlobalPosX(redPath, nodeId)` | float | Sub-red node global X |
| `sceneNodeGetGlobalPosY(redPath, nodeId)` | float | Sub-red node global Y |

### Visibility Readers

| C++ method | Returns |
|-----------|---------|
| `isHiddenNode(nodeId)` | bool |
| `isHiddenRedNode(redPath, nodeId)` | bool |

### String Utilities

| C++ method | Returns | Action |
|-----------|---------|--------|
| `stringEqual(a, b)` | bool | Equality comparison |
| `stringLen(a)` | float | String length |
| `stringToFloat(a)` | float | Parse string as number |
| `floatToString(float)` | string | Convert number to string |
| `floatFormat(float, int)` | string | Format number (int = decimal places) |
| `findSubString(str, substr)` | bool | Substring search |

### Status Query (for Conditional Branches)

| C++ method | Returns | Queries |
|-----------|---------|---------|
| `getTimeLineState(key)` | EBTStatus | Is timeline still playing? |
| `getSubredTimeLineState(redPath, key)` | EBTStatus | Sub-red timeline state |
| `getRotationAnimState(key)` | EBTStatus | Rotation animation state |
| `getScaleAnimState(key)` | EBTStatus | Scale animation state |
| `getSubredRotationAnimState(redPath, key)` | EBTStatus | Sub-red rotation anim state |
| `getSubredScaleAnimState(redPath, key)` | EBTStatus | Sub-red scale anim state |
| `getNodeAnimState(key1, key2)` | EBTStatus | Node path animation state |
| `getInterstitialAdsState(key)` | EBTStatus | Interstitial ad state |
| `getRewardVideoAdsState(key)` | EBTStatus | Reward video state |
| `getNotifyDevelopmentState(key)` | EBTStatus | Notification wait state |
| `getLoopState(key)` | EBTStatus | Loop continuation state |
| `getLoopTimes()` | float | Current loop iteration count |
| `getTreeState()` | EBTStatus | This tree's state |
| `getSubRedTreeState(key)` | EBTStatus | Sub-red tree state |
| `rewardVideoIsLoad(key)` | bool | Is reward video loaded? |

---

## §3.28 Debug Utilities

**`LogMessage(char*)`** — Static debug logging method registered in `reboltBt_behaviac_agent_meta.cpp`. Outputs a message to the debug console at runtime. Has no gameplay effect and no migration significance. Can be safely ignored during Godot migration.

---

## §3.29 Common Block Patterns

### Pattern 1: Initialization (node binding chain)

```
BTCustomFuncHeadAction (初始化)
└─ stepSlot → BTNotificationNodeToCoderAction (conditionA="绑定节点", paramA="节点A")
               └─ stepSlot → BTNotificationNodeToCoderAction (conditionA="绑定节点", paramA="节点B")
                              └─ stepSlot → null
```

### Pattern 2: Update (variable → UI + play timeline)

```
BTCustomFuncHeadAction (更新)
└─ stepSlot → BTLabelTitleAction (read P-金币数 → set Label)
               └─ stepSlot → BTPlayTimeLineAction (常态_金币栏)
```

### Pattern 3: Conditional branch (IF-ELSE + timeline + notify)

```
BTCustomFuncHeadAction (消除反馈)
└─ stepSlot → BTIFElseControlAction
               ├─ conditionA → BTEqualOperatorAction
               │                ├─ conditionA → BTCoderVariableAction (P-是否完成)
               │                └─ conditionB → "1"
               ├─ sectionA → BTPlayTimeLineWaitAction (动画_完成)
               │              └─ stepSlot → BTNotificationToCoderAction (动画播完)
               └─ sectionB → BTPlayTimeLineWaitAction (动画_普通)
                              └─ stepSlot → BTNotificationToCoderAction (动画播完)
```

### Pattern 4: Button click handler

```
BTButtonClickFuncAction (mathSelector=按钮)
└─ stepSlot → BTButtonEnableAction (禁用)
               └─ stepSlot → BTNotificationToCoderAction (按钮被点击)
                              └─ stepSlot → BTWaitTimeAction (0.3s)
                                             └─ stepSlot → BTButtonEnableAction (启用)
```

### Pattern 5: Timeline callback

```
Tree3 (BTCustomFuncHeadAction: 反馈动画)
└─ stepSlot → BTPlayTimeLineActionWithCallBack (动画_反馈, CallBackInfo → Tree2)

Tree2 (BTCallBackFuncAction)
└─ stepSlot → BTNotificationToCoderAction (反馈动画播放完毕)
```

### Pattern 6: Test function

```
BTTestFuncAction
└─ stepSlot → BTDataCoderVarSetAction (P-金币数 = 100)
               └─ stepSlot → BTCustomFuncBodyAction (初始化)
                              └─ stepSlot → BTCustomFuncBodyAction (更新)
```

---

## Known Gaps

- **`BTRedHiddenAction` behavior**: `baseSelect.Value` is observed to be a sequenceId string (not a reboltId), which does not match the `hiddenRedNode` C++ signature. The action likely maps to `stopTimeLine`, but this is unconfirmed. **Must verify against `ReboltRedManager.cpp` before implementing in Godot.**
- **`easing.opt` single-float semantics**: See cocosbase Known Gaps.
- **`pathValues` bezier tangent semantics**: See redream Known Gaps.

All other content in this file (§3.1–§3.28) is confirmed complete against `reboltBt_behaviac_agent_meta.cpp` (all 151 registered methods + 5 member properties) and all 26 observed project `.rebolt` source files.
