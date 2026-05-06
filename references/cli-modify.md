# Redream CLI Write Surface

Source of truth for this file:

- current binary: `build/bin/Redream/Redream.app/Contents/MacOS/Redream`
- current source: `Classes/CLI/CCliModify.cpp`, `CCliReboltModify.cpp`
- verified against recent CLI commits on `feature/f108_redream_cli` on 2026-03-30

Use this file for scene, project, timeline, and `.rebolt` mutation flows.

## 关键格式速查

### parent 节点路径规则

parent 参数必须使用 root 节点的 **displayName**，不是固定的 "root"：

| 场景根节点类型 | root displayName | --parent 参数 |
|-------------|-----------------|-------------|
| CCLayer（弹窗/浮层/界面） | "CCLayer" | `--parent CCLayer` |
| CCNode（子CCB/其他） | "CCNode" | `--parent CCNode` |

子节点路径示例：`CCLayer/子节点名/孙节点名`

### displayFrame (SpriteFrame) 属性值格式

| 场景 | 格式 | 示例 |
|------|------|------|
| plist 中的图片 | "plistFile.plist,frameName.png" | "ui_atlas.plist,btn_start.png" |
| 独立图片文件 | ",filename.png" | ",background.png" |
| 清除图片 | "," | "," |

### 常用属性值格式

| 属性 | 类型代码 | 值格式 | 示例 |
|------|---------|--------|------|
| position / Position | 3 | x,y,xUnit,yUnit,corner | "540,1040,0,0,0" |
| contentSize / Size | — | w,h,wUnit,hUnit | "1080,2080,0,0" |
| scale / ScaleLock | 4 | scaleX,scaleY,locked | "1,1,1" |
| opacity / Byte | 5 | 0-255 | "255" |
| visible / Check | 1 | true/false | "true" |
| rotation / Degrees | 2 | degrees | "45" |
| color / Color3 | — | r,g,b | "255,255,255" |

### rebolt-modify 路径注意

`rebolt-modify` 命令的 `--rebolt` 参数支持两种形式：

- 绝对路径
- 配合 `--project` 使用的 project-relative 路径，例如 `ccb/Foo.rebolt`

## Must Not

- Do not edit `.red` or `.rebolt` by hand if the current CLI already covers the change.
- Do not assume any top-level scene field is writable through `modify scene`; it only supports a controlled whitelist.
- Do not assume `modify batch` supports every single action. Its whitelist is smaller than the single-command surface.
- Do not rely on actions that are only visible in source but missing from `--help` or `actions` unless this skill explicitly marks them as verified.
- Do not skip validation after `.rebolt` writes. Use `rebolt validate` for project-wide checks, or `rebolt-modify validate` for a single target file.
- Do not write `.rebolt` selectors from guesswork. Read the paired `.red` first and bind only to live node/timeline IDs that the scene actually exposes.
- Do not guess sprite block fields from memory. `BTSpriteImageAction` uses `TitleInput` for a standalone image path; `BTSpritePlistAction` uses `pathInput` + `frameNameInput` for atlas swaps.

## Shared Safety

Common write options:

- `--dry-run`: preview without writing files
- `--backup`: write `<file>.bak` before mutating
- `--force`: bypass specific safety checks
- `--json`: structured result payloads

## `modify`

Most write actions require `--project <path>` or `-p`.

Exceptions:

- `modify actions`
- `modify list-node-types`
- `modify node-type-info`
- `modify property-info`

Important surface note:

- `modify actions --json` is still the best machine-readable source for the current public action surface.
- `modify --help` and `modify actions` now both expose the advanced keyframe actions plus node-type introspection helpers.

### Public actions

| Action | Usage | Notes |
| --- | --- | --- |
| `actions` | `modify actions [--action-name <name>] [--json]` | Query current binary action surface. |
| `list-node-types` | `modify list-node-types [--all] [--json]` | Default output is the GUI-visible node list. Add `--all` to expose abstract/internal definitions and raw metadata. No project required. |
| `node-type-info` | `modify node-type-info --type <NodeClass> [--property <name>] [--details] [--json]` | Returns a compact merged property summary plus node-level GUI metadata. Add `--details` for the full property contract. No project required. |
| `property-info` | `modify property-info --type <NodeClass> --property <name> [--json]` | Returns one resolved property schema with the full GUI-aligned contract. No project required. |
| `project` | `modify project --project <proj.redproj> [--resolution WxH] [--publish-dir dir] [--add-resource-path path] [--remove-resource-path path] [--add-language lang] [--remove-language lang] [--flatten-paths true\|false] [--ccb-only true\|false] [--property global_msg.foo --value bar] [--remove --property global_var.score]` | Project settings plus Rebolt project globals. |
| `scene` | `modify scene --project <proj.redproj> --scene <file.red> --property currentSequenceId [--value 0 \| --remove]` | Scene shell field mutation only. |
| `set-property` | `modify set-property --project <proj.redproj> --scene <file.red> --node <root>/foo --property Position --value 100,200,0,0,0 [--timeline <id\|name> --time <float>]` | Node property or node metadata mutation with GUI-aligned semantics. Add timeline context when the write must follow GUI keyframe semantics. GUI-disabled properties require `--force`. |
| `batch` | `modify batch --project <proj.redproj> --config ops.json` | Per-scene atomic batch mutate with a reduced action whitelist. `set-property` and `keyframe` reuse the same GUI safety rules as the single-command surface. |
| `add-node` | `modify add-node --project <proj.redproj> --scene <file.red> --parent <root> --type CCNode --name Foo` | Create a GUI-valid child node with parent/child compatibility checks. |
| `delete-node` | `modify delete-node --project <proj.redproj> --scene <file.red> --node <root>/foo` | Deletes a node. |
| `duplicate-node` | `modify duplicate-node --project <proj.redproj> --scene <file.red> --node <root>/foo [--count 2]` | Deep-copy node plus children/keyframes. |
| `move-node` | `modify move-node --project <proj.redproj> --scene <file.red> --node <root>/foo [--direction down \| --parent <root>]` | Reorder or reparent a node with the same GUI parent/child compatibility checks used by `add-node`. |
| `rename-node` | `modify rename-node --project <proj.redproj> --scene <file.red> --node <root>/foo --name Bar` | Rename display name. |
| `timeline` | `modify timeline --project <proj.redproj> --scene <file.red> --timeline 0 [--name Name] [--length 2] [--fps 30] [--scale 128] [--position 0] [--offset 0] [--start-play 0] [--end-play 2] [--play-speed 1] [--chain <id\|name\|-1>] [--auto-play true]` | Timeline metadata mutation, including playback flags. `--chain` accepts a sequence ID, timeline name, or `-1`. |
| `timeline-channel` | `modify timeline-channel --project <proj.redproj> --scene <file.red> --timeline 0 --channel wise --time 0.0 [--add\|--remove] [--value '["bank.bnk","Evt",true,[],100]'] [--easing 1] [--easing-opt '[0.5]'] [--new-time 0.5]` | Channel keyframe mutation for callback/sound/wise/shake/shake2. |
| `add-timeline` | `modify add-timeline --project <proj.redproj> --scene <file.red> [--name Intro] [--length 2] [--fps 30] [--scale 128] [--position 0] [--offset 0] [--start-play 0] [--end-play 2] [--play-speed 1] [--chain <id\|name\|-1>] [--auto-play true]` | Creates a new timeline. `--chain` accepts a sequence ID, timeline name, or `-1`. |
| `delete-timeline` | `modify delete-timeline --project <proj.redproj> --scene <file.red> --timeline Intro [--force]` | Deletes a timeline and its keyed data. `--force` is required for last/chained targets. |
| `duplicate-timeline` | `modify duplicate-timeline --project <proj.redproj> --scene <file.red> --timeline Intro [--name Outro]` | Duplicates a timeline plus all node tracks. Omitting `--name` uses `<source> copy` with uniqueness suffixing. |
| `keyframe` | `modify keyframe --project <proj.redproj> --scene <file.red> --timeline 0 --node <root>/foo --property Position --time 0 [--add\|--remove] [--value 0,0\|[...]] [--easing 1] [--easing-opt '[0.5]'] [--new-time 0.5]` | Property keyframe add/update/remove. GUI-disabled or non-animatable properties require `--force`. |
| `align-keyframes` | `modify align-keyframes --project <proj.redproj> --scene <file.red> --node <root>/foo --timeline 0 --property Position --time 1.0` | Shifts a track so its first key lands at `--time`. |
| `stretch-keyframes` | `modify stretch-keyframes --project <proj.redproj> --scene <file.red> --node <root>/foo --timeline 0 --property Position --factor 2.0` | Multiplies spacing from the first keyframe. |
| `reverse-keyframes` | `modify reverse-keyframes --project <proj.redproj> --scene <file.red> --node <root>/foo --timeline 0 --property Position` | Reverses track timing order. |
| `create-frames` | `modify create-frames --project <proj.redproj> --scene <file.red> --node <root>/foo --timeline 0 --frames a.png,b.png [--plist atlas.plist] [--interval 0.1] [--start-time 0]` | Creates sprite-frame animation keys. |
| `duplicate-file` | `modify duplicate-file --project <proj.redproj> --scene <file.red> [--name Copy]` | Duplicates `.red` and companion `.rebolt`, then refreshes copied `reboltId` values. |
| `new-scene` | `modify new-scene --project <proj.redproj> --scene ccb/Foo.red [--type CCNode] [--resolution WxH] [--minimal] [--enable-rebolt] [--no-default-timeline] [--no-rebolt-file]` | Creates a new scene shell with optional default timeline and companion `.rebolt` stub. |
| `new-project` | `modify new-project --project <dest.redproj> [--resolution WxH]` | Creates a new project file and `ccb/` directory. |
| `set-rebolt-public` | `modify set-rebolt-public --project <proj.redproj> --scene <file.red> --value true [--rebolt-id <id>]` | Mutates `rebolt.redInfos[*].isPublic` on direct current-scene `REDFile` nodes by default; use `--rebolt-id` to target one entry. |
| `build-scene` | `modify build-scene --project <proj.redproj> --scene <file.red> --config scene.json [--resolution WxH] [--preserve-rebolt-ids]` | Builds a scene from JSON or clones another `.red`, optionally keeping source `reboltId` values. |

## Node Type Discovery

Use these before `add-node` or `set-property` when you need the actual schema instead of guessing from memory.

### `modify list-node-types`

Use this to discover valid `--type` values for `add-node`.

Default behavior:

- returns the same GUI-visible node set that the editor creation surface uses
- filters `isAbstract=true`
- sorts by `ordering`, then by class name

Add `--all` when you need the raw registry, including abstract/internal node types.

JSON output includes:

- `name`
- `definitionPath`
- `inheritsFrom`
- `declaredPropertyCount`
- `displayName`
- `description`
- `ordering`
- `editorClassName`
- `canBeRoot`
- `canHaveChildren`
- `isChildrenFix`
- `isAbstract`
- `requireParentClass`
- `requireChildClass`
- `spriteFrameDropClass`
- `spriteFrameDropProperty`

### `modify node-type-info`

Use this to inspect one node class.

Default output stays compact on purpose:

- node-level GUI metadata such as `displayName`, `description`, `ordering`, `editorClassName`, `canBeRoot`, `canHaveChildren`, `isChildrenFix`, `isAbstract`, `requireParentClass`, `requireChildClass`, `spriteFrameDropClass`, and `spriteFrameDropProperty`
- merged property list after resolving the full `inheritsFrom` chain
- `resolvedType` after CLI alias normalization
- `valueFormat` hints for common CLI-editable types
- `animatable` flag when defined by the node schema
- `readOnly`
- `hiddenInEditor`

Add `--details` when you also need:

- `description`
- `dontSetInEditor`
- `config`
- `affectsProperties`
- `affects`
- `defaultSerialization` and `defaultValue`
- `constraints` such as `minimum`, `maximum`, `singleStep`, and `decimals`
- `options` for enum-like and toggle-backed properties such as `IntegerLabeled`, `ToggleGroup`, and boolean `Check`

Helpful patterns:

- `modify node-type-info --type CCSprite --json`
- `modify node-type-info --type CCSprite --property displayFrame --json`
- `modify node-type-info --type CCLabelTTF --property fontSize --json`
- `modify node-type-info --type CCLabelTTF --property horizontalAlignment --details --json`

### `modify property-info`

Use this when you already know the node class and property name and want a single detailed machine-readable contract object instead of scanning the full property list.

JSON output includes:

- `nodeType`
- `definitionPath`
- `inheritsFrom`
- `property`

The nested `property` object is the full property contract and includes:

- `type`
- `resolvedType`
- `readOnly`
- `hiddenInEditor`
- `description`
- `dontSetInEditor`
- `config`
- `affectsProperties`
- `affects`
- `defaultSerialization`
- `defaultValue`
- `valueFormat`
- `constraints`
- `animatable`
- `options`

Helpful patterns:

- `modify property-info --type CCSprite --property copyFlipXDir --json`
- `modify property-info --type CCLabelTTF --property horizontalAlignment --json`

## Project And Scene Shell Mutation

### `modify project`

Supports:

- `--resolution <WxH>`
- `--publish-dir <dir>`
- `--add-resource-path <path>`
- `--remove-resource-path <path>`
- `--add-language <lang>`
- `--remove-language <lang>`
- `--flatten-paths <true|false>`
- `--ccb-only <true|false>`
- `--property global_msg.<key> --value <text>`
- `--property global_var.<key> --value <text>`
- `--remove --property global_msg.<key>` or `global_var.<key>`

Use this when the target is project metadata or project-level Rebolt globals, not node-level scene content.

### `modify scene`

`modify scene` edits scene shell data, not node properties.

Notes:

- use `--value` for normal writes
- use `--remove` to delete a shell field or nested shell entry instead of writing a value
- when loading or rewriting a scene, CLI now normalizes legacy `rebolt.redInfos[*]` entries that were accidentally serialized as JSON strings back into plist dictionaries before writing the `.red`
- when that legacy metadata still points at stale node `reboltId` keys, scene normalization now remaps those `redInfos` entries onto the current live node IDs when the saved alias matches exactly one node
- direct writes to `rebolt.redInfos.<legacyId>.<field>` now follow the same canonicalization path, so a stale historical key still lands on the live node entry instead of silently recreating the orphaned old key

Supported property paths:

- `centeredOrigin`
- `fileVersion`
- `fileType`
- `currentResolution`
- `currentSequenceId`
- `stageBorder`
- `referenceImgNode`
- `referenceImgNode.*`
- `resolutions`
- `rebolt`
- `rebolt.isRebolted`
- `rebolt.redInfos`
- `rebolt.redInfos.<reboltId>.<field>`

Special handling for `rebolt.redInfos.<reboltId>.<field>`:

- `alias` is written as string
- `isPublic` and `enableEditAlias` are written as booleans

If you need to change node data, use `set-property`, `add-node`, or other node actions instead.

## Node Mutation

### `modify set-property`

Supports both normal node properties and node metadata:

- normal property names such as `Position`, `Visible`, `contentSize`
- metadata fields: `memberVarAssignmentName`, `memberVarAssignmentType`, `customClass`, `reboltId`, `reboltName`

Important behavior:

- property writes use type injection from the node type definition when the property is missing from the stored property array
- `memberVarAssignmentType` is validated as `0|1|2`
- changing `reboltId` or `reboltName` also synchronizes `rebolt.redInfos`
- `readOnly` properties are rejected by default, matching GUI editor behavior
- GUI-disabled properties such as root `position`, `scale`, `rotation`, `tag`, `visible`, and `skew` are rejected by default; use `--force` only for repair flows
- `--timeline` and `--time` must be provided together
- without timeline context, CLI performs static property writes only
- if the target node already has timeline-sensitive state for that property, the command fails and tells you to add both `--timeline` and `--time`
- with timeline context, CLI reuses GUI property-edit semantics instead of a separate CLI-only ruleset
- GUI-style dependent-property refreshes also apply to static writes; for example, toggling `scale9SpriteEnable` can recreate missing `contentSize` and `preferedSize` from existing size data or the current `displayFrame`

Examples of timed GUI-aligned behavior now covered by `set-property`:

- `ScaleLock`
- `Position` coordinate-mode conversions, including keyframe updates
- `PolygonVerts` synchronized point-count updates across keyframes
- `LocalizationV2` writing through the `string` track when a text keyframe exists at the selected time
- `labelConfig` cleanup/reindex side effects
- `affectsProperties` and related dependent-property refreshes
- `visible` special setter behavior
- editor value conversions such as `preferedSize`, `LocalizationV2`, and `fntFile`

### `modify add-node`

Supported modifiers:

- `--index <n>`
- `--rebolt-name <name>`
- `--minimal`
- `--no-rebolt-id`

Important behavior:

- start with `modify list-node-types --json` if you are unsure whether a node class exists
- use `modify node-type-info --type <NodeClass> --json` to inspect default properties before constructing `--properties`
- default mode builds default properties from the node type definition
- `--minimal` creates an empty property list and is safer for clone or replay workflows
- unless `--no-rebolt-id` is set, a fresh `reboltId` is generated and registered into the scene's `rebolt.redInfos` when the scene has a rebolt section
- abstract or non-creatable node types are rejected
- parent/child compatibility is validated with the same GUI metadata (`canHaveChildren`, `requireChildClass`, `requireParentClass`) used by the editor

### Other node actions

- `delete-node`: refuses unsafe deletes unless `--force`, and removes the deleted subtree's `rebolt.redInfos` entries so alias/reboltId state stays in sync
- `duplicate-node`: duplicates subtree and keyed data, clears copied `memberVarAssignmentName`, and can create multiple copies with `--count`
- `move-node`: supports both sibling reorder by `--direction` and reparent-by-`--parent`, and reuses the same GUI parent/child compatibility checks as `add-node`
- `rename-node`: changes display name only

## Batch Mutation

`modify batch` currently supports this reduced whitelist:

- `scene`
- `set-property`
- `add-node`
- `rename-node`
- `delete-node`
- `add-timeline`
- `delete-timeline`
- `keyframe`
- `timeline-channel`

Behavior:

- operations are grouped by scene
- execution order is preserved inside each scene
- scene-level atomicity: one failed op rolls back the whole scene batch
- batch `delete-timeline` is idempotent when the timeline is missing
- batch `set-property` and `keyframe` reuse the same GUI safety checks as the single commands; pass top-level `--force` only when intentionally overriding them for repair flows

Minimal example:

```json
[
  {
    "action": "scene",
    "scene": "ccb/Foo.red",
    "property": "currentSequenceId",
    "value": 0
  },
  {
    "action": "set-property",
    "scene": "ccb/Foo.red",
    "node": "<root>/panel/title",
    "property": "customClass",
    "value": "RedreamLoader"
  },
  {
    "action": "timeline-channel",
    "scene": "ccb/Foo.red",
    "timeline": 0,
    "channel": "wise",
    "time": 0.0,
    "add": true,
    "value": ["bank.bnk", "Play_Click", true, [], 100]
  }
]
```

## Timeline Mutation

### `modify timeline`

Supported timeline metadata writes:

- `--name`
- `--length`
- `--fps`
- `--scale`
- `--position`
- `--offset`
- `--start-play`
- `--end-play`
- `--play-speed`
- `--chain`
- `--auto-play`

Current validation rules:

- `--length`, `--fps`, `--scale` must be positive
- `--start-play` and `--end-play` must be non-negative
- `--start-play` cannot exceed `--end-play`
- `--play-speed` must be between `0.1` and `5.0`
- `--chain` accepts `-1`, an existing `sequenceId`, or an existing timeline `name`
- enabling `--auto-play true` clears `autoPlay` on all sibling timelines

### `modify add-timeline`

Supported options mirror timeline metadata creation:

- `--name`
- `--length`
- `--fps`
- `--scale`
- `--position`
- `--offset`
- `--start-play`
- `--end-play`
- `--play-speed`
- `--chain`
- `--auto-play`

Defaults:

- name: `Untitled Timeline` with automatic suffixing for uniqueness
- length: `10.0`
- fps: `30`
- scale: `128`
- position: `0`
- offset: `0`
- start play: `0`
- end play: timeline length
- play speed: `1.0`
- chain: `-1`, an existing `sequenceId`, or an existing timeline `name`
- autoPlay: `false`

### `modify delete-timeline`

Behavior:

- requires `--timeline <id|name>`
- deletes timeline metadata plus all keyed node data for that sequence
- refuses to delete the last remaining timeline unless `--force` is set
- refuses to delete a timeline that other timelines chain to unless `--force` is set
- when deletion succeeds, clears any remaining `chainedSequenceId` references that still pointed at the removed sequence

### `modify duplicate-timeline`

Behavior:

- requires `--timeline <id|name>`
- `--name` is optional; default copy name is `<source> copy`
- auto-suffixes the final timeline name when the requested name already exists
- duplicates the source timeline metadata and all node animated-property tracks into a fresh `sequenceId`

### `modify timeline-channel`

Supported channels:

- `callback`
- `sound`
- `wise`
- `shake`
- `shake2`

Supported operations:

- `--add`
- `--remove`
- modify in place with `--value`, `--easing`, `--easing-opt`, `--new-time`

Notes:

- `--easing-opt` accepts the same scalar, comma-vector, JSON array, or JSON object forms used by `modify keyframe`
- use `--new-time` to move an existing channel keyframe without rebuilding the payload

CSV value forms:

- `callback`: `callbackName,intArg`
- `sound`: `file,pitch,pan,gain`
- `wise`: `bank,event[,postMode[,volume]]`
- `shake`: `intA,intB`
- `shake2`: raw string

JSON array input is also accepted for channel payloads. This is the safer choice for `wise` and future-proof tooling.

### `modify create-frames`

Supported options:

- `--frames <frame1,frame2,...>`
- `--plist <file>`
- `--interval <seconds>`
- `--start-time <float>`

Important behavior:

- `--plist` is optional when frames refer to standalone images; use `'Use regular file'` semantics when matching GUI exports
- default `--interval` is `1 / timeline_fps`
- default `--start-time` is `0`

### Property keyframe actions

`modify keyframe` stores GUI-safe keyframes:

- GUI-disabled properties (for example root `position`) are rejected by default
- `--add` requires the property to be animatable in GUI metadata; use `--force` only for repair flows
- `--add` creates a new keyframe and rejects duplicate times
- `--remove` deletes the keyframe at the selected time
- plain modify mode updates an existing keyframe at `--time`
- default easing is linear (`1`) unless explicitly changed
- `--value` accepts raw scalars, comma-separated vectors, or JSON array/object payloads when the target property uses structured keyframe data
- `--easing-opt` accepts the same scalar, comma-vector, JSON array, or JSON object forms used by timeline-channel updates
- `--new-time` moves an existing keyframe without rebuilding the whole track
- each keyframe includes `type`
- each keyframe includes `name`

When `set-property` changes `Position` on a timeline-sensitive node, pass `--timeline` and `--time`: the CLI rewrites the stored value, every keyframe value, and any valid 7-slot `pathValues` payload using the GUI coordinate-mode conversion rules.

This matters because older CLI output could create keyframes that later crashed or confused the GUI.

Track-level helpers:

- `align-keyframes` requires an existing track and shifts the whole track so the first keyframe lands at `--time`
- `stretch-keyframes` requires at least 2 keyframes and scales spacing from the first keyframe
- `reverse-keyframes` requires at least 2 keyframes and reverses timing order across the track

## File-Level Scene Actions

### `modify new-project`

Creates a full `.redproj` file with the fields the GUI expects and creates the `ccb/` directory.

Behavior:

- `--resolution <WxH>` is optional; default design resolution is `750x1334`
- creates parent directories as needed
- refuses to overwrite an existing project file

### `modify new-scene`

Supported options:

- `--type <rootType>`
- `--resolution <WxH>`
- `--enable-rebolt`
- `--no-default-timeline`
- `--minimal`
- `--no-rebolt-id`
- `--no-rebolt-file`

Important behavior:

- default resolution comes from project `designSize`
- scene shell is initialized with `currentSequenceId = 0`
- a `rebolt` section is always created in the `.red`
- for new Figma/generated `.red` scenes, prefer `--enable-rebolt --no-default-timeline` so the file starts GUI-ready without extra rebolt/default-timeline repair steps
- `--minimal` gives the root node an empty property list instead of default root properties
- `--no-default-timeline` skips creating the default timeline/sequence entry
- if a legacy scene already contains `Default Timeline`, deleting it may still require a one-time `currentSequenceId` repair in the serialized `.red`
- unless `--no-rebolt-file` is set, a companion legacy-schema `.rebolt` stub is created when missing
- if a legacy scene was created without `--enable-rebolt`, you can still repair it with `modify scene --property rebolt.isRebolted --value true`
- unless `--no-rebolt-id` is set, the root node is assigned a new `reboltId` and registered in `rebolt.redInfos`

### `modify duplicate-file`

Duplicates `.red` plus companion `.rebolt` when present, and regenerates `reboltId` values in the duplicate to avoid collisions.

Important behavior:

- `--name` is optional; when omitted the CLI auto-generates `<source>-1`, `<source>-2`, ... using the GUI-style naming pattern
- refuses to overwrite an existing destination file
- copies the companion `.rebolt` only when the source scene has one
- refreshes both scene node `reboltId` values and Rebolt block `randomID` values in the duplicate
- rewrites copied Rebolt references so they point at the duplicated scene node IDs instead of the source IDs

### `modify build-scene`

Verified behavior:

- target scene path must not already exist
- `--config <source.red>` clones an existing scene, keeps timelines/keyframes, and regenerates `reboltId` values unless `--preserve-rebolt-ids` is set
- `--config <scene.json>` builds a new scene from JSON matching `inspect scene --properties --json`
- `--resolution <WxH>` is only used in JSON build mode; default is `960x640`
- JSON mode writes a default resolution and one default timeline unless the source mode already supplies them

## `modify set-rebolt-public`

Purpose:

- mutates `rebolt.redInfos[*].isPublic`
- by default only touches direct current-scene `REDFile` nodes; use `--rebolt-id` to target one entry

Important behavior:

- creates the scene's `rebolt` section if missing
- creates the companion `.rebolt` file if missing
- lists available IDs when a requested `--rebolt-id` is not found
- repairs legacy/stringified `rebolt.redInfos[*]` entries before mutating them, so follow-up `inspect check` runs see the normalized dictionary form
- the same normalization step also carries forward legacy alias/public metadata when a node ID was regenerated but the old `redInfos` key can still be mapped back to one live node by alias
- when `--rebolt-id` names that stale historical key, the command now resolves it onto the canonical live node entry before writing, instead of rejecting the request

## `rebolt-modify` Write Actions

These actions mutate a single `.rebolt` file directly.

Routing rule:

- if the task is read-only, use `rebolt-modify read`
- `rebolt-modify` is the public single-file `.rebolt` read surface even though the command name says "modify"
- do not use project-level `rebolt` commands to inspect one file's functions or block tree
- do not invent `inspect rebolt --rebolt <file>`; that surface is not public

Fast read examples before a write:

With `--project`, prefer project-relative `.rebolt` paths.

```bash
Redream rebolt-modify read --rebolt ccb/Foo.rebolt --section CustomFunc --project <path.redproj> --json
Redream rebolt-modify read --rebolt ccb/Foo.rebolt --block-id <randomID> --project <path.redproj> --json
```

### Paired `.red` contract

Before any `.rebolt` write:

- read the paired `.red` first
- confirm the target node or timeline still exists
- confirm the target node still has a non-empty `reboltName`
- keep `reboltName` unique within the paired `.red`; ambiguous aliases fail validation instead of falling back to `DisplayName` or first-match lookup
- do not invent selector IDs or reuse stale historical IDs unless the current scene still resolves them
- for node selectors, keep `Value` as the live `reboltId` and `DisplayName` as the live `reboltName`; do not leave `DisplayName` as a raw ID
- if the paired `.red` still has empty `reboltName` or blank `rebolt.redInfos[*].alias`, repair the scene metadata first and only then write the `.rebolt`

Current CLI-enforced selector rules:

- button callbacks / button enable blocks must target `CCControlButton` or `REDNodeButton`
- label title / placeholder / number-increase blocks must target `CCLabelTTF`, `CCLabelBMFont`, `CCRedLabel`, or `CCLabelPlus`
- sprite image / plist blocks must target `CCSprite`, `CCScale9Sprite`, or `SpritePlus`
- progress blocks must target `CCProgressTimer`

If the write would produce a selector that does not exist in the paired `.red`, or that points at the wrong node class, the write now fails before saving.

### Public actions

| Action | Usage | Notes |
| --- | --- | --- |
| `set-section` | `rebolt-modify set-section --rebolt <file> --section <name> (--value <value> \| --value-file <file>) [--dry-run] [--backup]` | Replaces one top-level section value. |
| `set-entry` | `rebolt-modify set-entry --rebolt <file> --section <name> --entry <key> (--value <value> \| --value-file <file>) [--dry-run] [--backup]` | Replaces or inserts one entry inside an object section. |
| `remove-entry` | `rebolt-modify remove-entry --rebolt <file> --section <name> --entry <key> [--dry-run] [--backup]` | Removes one entry from an object section. |
| `validate` | `rebolt-modify validate --rebolt <file> [--json]` | Single-file structural + paired-`.red` validation. Besides schema checks, it now hard-fails empty `reboltName`, missing selector targets, and selector/node-type mismatches for non-empty selectors. Current headless defaults for `BTNodeSetAnimAction` / `BTNodeSetAnimWaitAction` / `BTNodeSetAnimActionWithCallBack` include `rotateCheck`; do not omit it when writing new blocks. Headless helper defaults may still leave selectors blank until the caller fills them. |
| `add-block` | `rebolt-modify add-block --rebolt <file> --tree <name> --path <slot-path> --type <class> [--props '{...}'] [--dry-run] [--backup]` | Adds a block using registered defaults plus optional property overrides. Partial `--props` objects merge into BTInputSlot/selector wrappers instead of replacing them wholesale. Headless defaults now cover more GUI-only block families such as node anim / transform / message / button helpers, ads / control helpers, timeline / skeleton helpers, list-variable helpers, and function-head / simulator helpers. Use `block-info` first when the field contract matters; for example `BTSpriteImageAction` uses `TitleInput`, while `BTSpritePlistAction` uses `pathInput` + `frameNameInput`. If `--props` contains node selectors, write the live `reboltId` into `Value`; the save rejects missing/mismatched targets and keeps `DisplayName` human-readable. |
| `set-prop` | `rebolt-modify set-prop --rebolt <file> --block-id <id> --prop <path> --value <val> [--dry-run] [--backup]` | Mutates a property on one block by `randomID`. Single-part writes preserve BTInputSlot / selector wrappers instead of flattening them to raw scalars, and legacy broken wrappers are auto-repaired from block metadata before the new value is applied. Unknown nested paths now fail fast instead of silently creating half-shaped objects. Selector writes validate against the paired `.red` scene before saving; for node selectors, pass the live `reboltId` and the save path auto-syncs `DisplayName` from the matching `reboltId` and current `reboltName`. |
| `set-var` | `rebolt-modify set-var --rebolt <file> --var-name <name> --value <num> [--dry-run] [--backup]` | Mutates an existing `CustomVar` entry. |
| `add-var` | `rebolt-modify add-var --rebolt <file> --var-name <name> [--value <num>] [--dry-run] [--backup]` | Adds a `CustomVar` entry. |
| `remove-var` | `rebolt-modify remove-var --rebolt <file> --var-name <name> [--force] [--dry-run] [--backup]` | Removes a `CustomVar` entry. |
| `undo` | `rebolt-modify undo --rebolt <file>` | Restores from `.bak`. |
| `remove-block` | `rebolt-modify remove-block --rebolt <file> --block-id <id> [--dry-run] [--backup]` | Removes one block subtree and reconnects the chain. Empty tails are serialized as `null`, not `{}`. |
| `copy-block` | `rebolt-modify copy-block --rebolt <file> --block-id <id> --tree <name> --path <slot-path> [--target-rebolt <file>] [--dry-run] [--backup]` | Copies a subtree, optionally cross-file. |
| `move-block` | `rebolt-modify move-block --rebolt <file> --block-id <id> --tree <name> --path <slot-path> [--dry-run] [--backup]` | Moves a block to another slot path. Detached `stepSlot.ContainerValue` stays `null` when there is no child chain. |
| `add-func` | `rebolt-modify add-func --rebolt <file> --func-name <name> [--dry-run] [--backup]` | Adds a custom function and its head tree entry. |
| `remove-func` | `rebolt-modify remove-func --rebolt <file> --func-name <name> [--force] [--dry-run] [--backup]` | Removes a custom function and its tree. |
| `rename-func` | `rebolt-modify rename-func --rebolt <file> --func-name <old> --value <new> [--dry-run] [--backup]` | Renames function key plus all tree references. |
| `diff` | `rebolt-modify diff --rebolt <fileA> --rebolt2 <fileB> [--json]` | Structural comparison between two files. |
| `export-tree` | `rebolt-modify export-tree --rebolt <file> --tree <name> [--output <file>]` | Exports one tree as indented JSON. |
| `import-tree` | `rebolt-modify import-tree --rebolt <file> --value <inputFile> [--tree <name>] [--dry-run] [--backup]` | Imports a JSON tree, regenerates all `randomID`s, and inserts it into `TreeList`. |

### Supported top-level sections

- `DisPlayName`
- `TreeList`
- `CustomVar`
- `CustomList`
- `CustomMessage`
- `CustomFunc`
- `CustomTestFunc`
- `RedFileList`
- `RedNoteInfo`

Rules:

- `--value` and `--value-file` are mutually exclusive and exactly one is required for `set-section` and `set-entry`
- entry operations are not valid for `DisPlayName`
- section values parse as `null`, boolean, number, JSON object, JSON array, or fallback string
- `set-prop` uses the same scalar parsing order (`null` -> bool -> number -> JSON -> string); when `--prop` is a single structured field such as `conditionA`, `baseSelect`, `redSelect`, `mathSelector`, or `animSelect`, the CLI updates the nested value field instead of replacing the whole object
- if a legacy sample file already broke one of those fields down to a scalar, `set-prop` now reconstructs the GUI wrapper from block metadata before writing the new value
- dot-path writes such as `baseSelect.Value` still work when you need explicit nested control, and they also repair legacy scalar wrappers before updating nested fields
- if a nested path has no matching schema template, `set-prop` now returns an error instead of inventing a partial object like `{"Value": ...}`
- selector/string-like wrapper values are normalized back to strings, so `--value 1` on `baseSelect.Value` still serializes as `"1"` instead of an invalid numeric selector payload
- node selector wrappers should be kept human-readable: `baseSelect` / `redSelect` / `mathSelector` use the current node `reboltId` in `Value`, and the CLI save path now auto-syncs `DisplayName` from the paired `.red` node `reboltName`
- `add-block --props` and `rebolt-modify batch` use the same structured override semantics for BTInputSlot/selectors, so partial objects like `{"conditionA":{"StringValue":{"Value":"动画播完"}}}` preserve `Type` / `ContainerValue`
- use `rebolt-modify block-info --type <BlockClass>` when you need the exact headless `defaultJson` contract before scripting `add-block --props` or nested `set-prop`
- for sprite swaps, confirm the real resource contract before choosing the block type: standalone image path => `BTSpriteImageAction.TitleInput`; plist + frame => `BTSpritePlistAction.pathInput` + `frameNameInput`

## Public `rebolt-modify` Extras

Current binary/help/actions are in sync for these:

- `rebolt-modify add-tree`: public in `rebolt-modify --help` and `rebolt-modify actions`
- `rebolt-modify batch`: public in `rebolt-modify --help` and `rebolt-modify actions`

## Value Encoding For `set-property`

Common compound formats:

| Type | Format | Example |
| --- | --- | --- |
| `Position` | `x,y,anchorX,anchorY,anchorZ` | `100,200,0.5,0.5,0` |
| `Size` | `width,height,xMode,yMode[,xRelative,yRelative]` | `320,480,0,0,false,false` |
| `Point` | `x,y` | `0.5,0.5` |
| `Color3` | `r,g,b` | `255,128,0` |
| `Color4` | `r,g,b,a` | `255,128,0,255` |
| `ScaleLock` | `scaleX,scaleY,locked[,rotation]` | `1,1,1,0` |
| `FloatXY` | `x,y` | `1.0,1.0` |
| `FloatXYZ` | `x,y,z` | `1.0,2.0,3.0` |
| `FloatVar` | `value,variance` | `5.0,1.0` |
| `FloatScale` | `scale,type` | `1.0,0` |
| `SpriteFrame` | `plistFile,frameName` | `sprites.plist,icon.png` |
| `SkelFrame` | `animation,speed,loop` | `idle,1.0,true` |
| `Flip` | `flipX,flipY` | `0,1` |
| `Callbacks` | `target,type` | `myTarget,1` |
| `VideoConfig` | `file,keepLW,loop` | `video.mp4,true,true` |

Special formats:

| Type | Format | Example |
| --- | --- | --- |
| `Blendmode` | preset int or `src,dst` | `1` or `770,771` |
| `Color4FVar` | `rgba;rgba` float groups | `1,0.5,0,1;0.1,0.1,0.1,0` |
| `Wise` | `bank,event[,extra1,extra2]` | `sounds.bnk,Play_BGM` |

JSON string input is accepted for structured property types such as:

- `Localization`
- `LocalizationV2`
- `FontI18n`
- `SpriteFrameI18n`
- `FontOptConfig`
- `LabelConfig`
- `MinMaxCurveData`
- `MinMaxGradientData`
- `EmissionData`
- `PolygonVerts`
- `FrameSet`
- `BakeAnimation`

Aliases currently normalized by the CLI:

- `Percent`, `IntegerLabeled`, `ToggleGroup`, `Animation`, `RedreamTimelineEvent`, `StartStop` -> `Integer`
- `Skin` -> `String`
