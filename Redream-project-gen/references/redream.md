# Redream `.red` File Format Reference

Complete reference for reading `.red` Apple plist XML scene layout files used by the Redream UI framework for Cocos2d-x.

**Source files:** `.red` — typically in a `ccb/` or `res/ccb/` directory.
**Compiled output:** `.redream` (Protobuf binary) — do NOT read directly; it is a compiled artifact.
**Compiled animation:** `.redanim` (Protobuf binary) — compiled from `.anim` animation files. Found in `ccbi/` directories alongside `.redream` files. Do NOT read directly; use the source `.anim` files instead. The `.redanim`-to-`.anim` relationship mirrors `.redream`-to-`.red`.
**Loader source:** `Libraries/redream/*.cpp` — authoritative reference for all property types and node behavior.

> See also: `references/cocosbase.md` for coordinate system, unit types, and anchor point fundamentals.

---

## Quick Lookup

**"I see a property with `type` string X"** → §2.3 (alphabetical table of all 59 types)
**"I see a node with `baseClass` Y"** → §2.4 (Tier-1 detail, Tier-2 table)
**"I see a keyframe / `animatedProperties`"** → §2.5 (keyframe structure + property type codes)
**"I see a `sequences` entry field"** → §2.6 (runtime fields) + §2.6 Editor-only fields note
**"I see the root `rebolt` key"** → §2.1 (root-level fields table, including `redInfos` structure)

Most common specific lookups:

| Token seen in file | What it is | Go to |
|---|---|---|
| `Position` type, value `[x, y, xUnit, yUnit, corner]` | Node position | §2.3 + **cocosbase §1.1-1.2** |
| `Size` type, value `[w, h, wUnit, hUnit, lockAspect, ignoreContentSize]` | Node size | §2.3 + **cocosbase §1.1** |
| `SpriteFrame` type, value `[plistPath, frameName]` | Sprite atlas frame | §2.3 |
| `Blendmode` type, value `[srcFactor, dstFactor]` or `[1]` | GL blend mode (`[1]`=normal) | §2.3 |
| `Check` type | Boolean (true/false) | §2.3 |
| `Byte` type | Integer 0–255 (opacity) | §2.3 |
| `Color3` type, value `[r, g, b]` | RGB color | §2.3 |
| `ScaleLock` type, value `[scaleX, scaleY, locked]` | Scale | §2.3 |
| `Degrees` type | Float, clockwise positive | §2.3 |
| `Text` type | String label content | §2.3 |
| `REDFile` property type | Sub-scene path string | §2.3 |
| `Animation` property type | Sequence ID integer (-2=none) | §2.3 |
| `reboltId` (12-char string on any node) | Unique ID for Rebolt references | §2.2 |
| `animatedProperties` dict | Keyframe animations keyed by sequenceId | §2.5 |
| `pathValues` in a position keyframe | Bezier tangent control points (7 floats) | §2.5 |
| `easing.type` / `easing.opt` in a keyframe | Easing curve | §2.5 + **cocosbase §1.6** |
| `sequences` array | Animation timelines | §2.6 |
| `rebolt` root key / `redInfos` | Sub-red binding metadata | §2.1 |
| `REDFile` node (`baseClass`) | Embeds a child `.red` scene | §2.4 |
| `CCSprite` node | Single sprite frame | §2.4 |
| `CCScale9Sprite` node | Nine-patch sprite | §2.4 |
| `CCRedLabel` node | Dual-layer bitmap label | §2.4 |
| `REDNodeButton` node | Tappable button | §2.4 |
| `RParticleSystem` node | Particle system | §2.4 |

---

## §2.1 Root-Level Fields

Every `.red` file is an Apple plist XML with these root keys:

| Key | Type | Notes |
|-----|------|-------|
| `fileType` | string | Always `"Redream"` |
| `fileVersion` | integer | Always `1` |
| `centeredOrigin` | bool | Editor display setting; runtime irrelevant |
| `currentResolution` | integer | Last selected resolution in editor |
| `currentSequenceId` | integer | Last viewed sequence in editor |
| `stageBorder` | integer | Always `0`; runtime irrelevant |
| `guides` | array | Editor guide lines (see §2.7); may be empty |
| `rebolt` | dict | `{isRebolted: bool, redInfos: dict}` — Rebolt binding metadata. `isRebolted: true` means this scene has a linked `.rebolt` file. `redInfos` is a dict keyed by `reboltId` of each `REDFile` node; each value: `{alias: string, enableEditAlias: bool, isPublic: bool}`. `alias` = human-readable reference name; `isPublic: true` = external `.rebolt` files can reference this sub-red by alias. |
| `resolutions` | array | Screen resolution targets (see §2.8) |
| `referenceImgNode` | dict | Editor-only background reference image; always `hidden: true`; runtime irrelevant |
| `sequences` | array | Animation timelines (see §2.6) |
| `nodeGraph` | dict | Root scene node; typically `baseClass: CCLayer` for scene `.red` files. Exception: `.anim` path animation files and some effect `.red` files use `CCNode` as root. |

---

## §2.2 Node Common Fields

Every node dict (in `nodeGraph` and recursively in `children`) contains:

| Field | Type | Meaning |
|-------|------|---------|
| `baseClass` | string | Cocos2d-x class name |
| `displayName` | string | Editor display name |
| `reboltId` | string (12 chars) | Unique node ID for Rebolt references (e.g., `"ahiITqBTmq6J"`) |
| `reboltName` | string | Name used in Rebolt's `baseSelect.DisplayName` |
| `customClass` | string | C++ subclass override; empty = use baseClass |
| `memberVarAssignmentName` | string | C++ member variable name; empty = none |
| `memberVarAssignmentType` | integer | `0`=none, `1`=Node*, `2`=Sprite*, `3`=Layer* |
| `uniqueNodeId` | integer | Internal ID; not used in Rebolt |
| `hidden` | bool | Editor visibility; **not** the runtime `visible` property |
| `locked` | bool | Editor lock; runtime irrelevant |
| `expand` | bool | Editor expand; runtime irrelevant |
| `seqExpanded` | bool | Editor expand; runtime irrelevant |
| `nodeColorTag` | integer | Editor color tag; runtime irrelevant |
| `properties` | array | Static property list `[{name, type, value}]` |
| `animatedProperties` | dict | Keyframe data keyed by sequenceId string (see §2.5) |
| `children` | array | Child nodes; later entries render on top |
| `customProperties` | array | Custom extension properties; usually empty |

---

## §2.3 Property Type System

Each `properties` entry: `{name: string, type: string, value: any}`

**Complete property type system — all 59 active types from `REDNodeProperty.hpp` enum** (3 deprecated excluded). Less commonly seen types are marked *(rare)*.

| Type string | Value format | Typical property names | Notes |
|-------------|-------------|----------------------|-------|
| `Animation` | integer (`-2`=none, `0`/`1`/`2`…=sequenceId) | `animation` on REDFile nodes | |
| `BakeAnimation` | `{name: string, time: float, loop: bool}` | `bakeAnimation` on RedBakeNode | *(rare)* |
| `BakeDataFile` | string path | `bakeDataFile` on RedBakeNode | *(rare)* |
| `Blendmode` | `[srcFactor, dstFactor]` GL blend enum ints | `blendFunc` | `[1]` = normal blend |
| `Block` | `{selectorName: string, targetType: int}` | `block` on CCMenuItem | *(rare)* |
| `BlockCCControl` | dict (touch control config) | `ccControl` on REDNodeButton | |
| `Byte` | integer 0–255 | `opacity`, `frontOpacity`, `backOpacity` | |
| `Callbacks` | `{selector: string, target: int}` | Legacy CCMenu callbacks | *(rare)* |
| `Check` | `true`/`false` | `visible`, `enabled`, `enableWrap`, `ignoreAnchorPointForPosition`, `cascadeOpacityEnabled`, `cascadeColorEnabled`… | |
| `Color3` | `[r, g, b]` integers 0–255 | `color`, `frontColor`, `backColor` | |
| `Color4` | `[r, g, b, a]` integers 0–255 | Color with alpha | *(rare)* |
| `Color4FVar` | `[[r,g,b,a], [r,g,b,a]]` float 0–1 color + variance | Old particle color variance | *(rare)* |
| `Degrees` | float (degrees, positive = clockwise) | `rotation`, `rotationX`, `rotationY` | |
| `EmissionData` | dict (burst timing config) | `EmissionModuleBurst` on RParticleSystem | |
| `Flip` | `[flipX: bool, flipY: bool]` | `flip` on CCSprite, CCScale9Sprite | Single property, NOT two separate Check properties (source: `CCSpriteLoader.cpp`) |
| `Float` | float | `insetLeft/Right/Top/Bottom`, `touchMoveCancelDistance`… | |
| `FloatScale` | float (scaled by resolutionScale at runtime) | Editor-scaled float fields | *(rare)* |
| `FloatVar` | `[value: float, variance: float]` | Old particle float + variance pairs | *(rare)* |
| `FloatXY` | `[x: float, y: float]` floats | `skew` → `[skewX, skewY]` in degrees | |
| `FloatXYZ` | `[x, y, z]` floats | 3D vectors in RParticleSystem shape params | |
| `FntFile` | string path to `.fnt` file | `frontBMFntFile`, `backBMFntFile` on CCRedLabel; `fntFile` on CCLabelBMFont | |
| `FontI18n` | `{style: string}` i18n font style key | `frontFontI18n`, `backFontI18n` on CCRedLabel | |
| `FontOptConfig` | `{font, size, color, stroke}` dict | `fontOptConfig` on CCLabelBMFont | *(rare)* |
| `FontTTF` | string (TTF file path or system font name) | `fontName` on CCLabelTTF | If file path exists, loaded as TTF; otherwise used as system font name |
| `FrameSet` | array of frame path strings | Multi-frame sprite sets | *(rare)* |
| `Integer` | integer | Various RParticleSystem params, `tag` | |
| `IntegerLabeled` | integer (enum with editor-displayed labels) | `horizontalAlignment` (0=left,1=center,2=right), `verticalAlignment` (0=top,1=center,2=bottom), `type` on CCProgressTimer, `direction` on CCScrollView | |
| `LabelConfig` | array of label config dicts | `labelConfig` on CCLabelPlus | *(rare)* |
| `Localization` | `{isLocalization: bool, key: string}` | `localization` on CCLabelBMFont/TTF | Superseded by LocalizationV2 |
| `LocalizationV2` | `{isLocalization: bool, lanFile: string, lanKey: string}` | `localizationV2` on CCRedLabel | |
| `MaterialBall` | `{path: string, params: {paramName: float}}` | `materialBall` on CCSprite | *(rare)* |
| `MaterialFile` | string path to material file | Custom shader material | |
| `MinMaxCurveData` | dict (animation curve with mode/key arrays) | `EmissionModuleRate`, size/rotation curves on RParticleSystem | |
| `MinMaxGradientData` | dict (gradient with color keys) | Color gradient on RParticleSystem | |
| `PbVertsFile` | string path to protobuf polygon file | `pbVertsFile` on TiledPolygonSprite | *(rare)* |
| `Percent` | integer 0–100 | `percent` on UISlider | *(rare)* |
| `Point` | `[x, y]` floats 0.0–1.0 | `anchorPoint`, `midpoint`, `barChangeRate` | |
| `PointLock` | `[x, y]` floats (aspect-locked in editor) | Editor-only locked point | *(rare)* |
| `PolygonFile` | string path | Polygon clipping data file | *(rare)* |
| `PolygonVerts` | array of `[x, y]` vertex arrays | `polygonVerts` on REDPolygonClippingNode2 | |
| `Position` | `[x, y, xUnit, yUnit, corner]` — units 0–2 only | `position` | → **cocosbase §1.1-1.2** for unit and corner decoding |
| `REDFile` | string path to sub `.red` file | `redFile` on REDFile nodes (e.g., `"ui/G010Item.red"`) | |
| `RedreamTimelineEvent` | dict (timeline trigger config) | `redreamTimelineEvent` on RParticleSystem | |
| `ReferenceSpriteFrame` | `["", ""]` | Editor-only reference background image | **Editor-only** — not a real runtime property type |
| `ScaleLock` | `[scaleX, scaleY, locked]` | `scale` | |
| `SeparatorCheck` | bool (with UI separator in editor) | Particle module enable flags | |
| `Size` | `[w, h, wUnit, hUnit, lockAspect, ignoreContentSize]` — units 0–4 | `contentSize`, `preferedSize`, `dimensions` | → **cocosbase §1.1** for SizeUnit decoding (includes INSETPOINTS/INSETUIPOINTS) |
| `SkelFrame` | dict (spine animation frame config) | `frame` on SkeletonAnimation | |
| `Skin` | string skin name | `skin` on SkeletonAnimation | |
| `SpineAtlas` | string path to `.atlas` file | `atlasFile` on SkeletonAnimation | |
| `SpineSkel` | string path to `.skel`/`.json` | `dataFile` on SkeletonAnimation | |
| `SpriteFrame` | `[plistPath, frameName]` strings | `displayFrame`, `spriteFrame` | |
| `SpriteFrameI18n` | `{langCode: [plist, frame], …}` per-language frame map | `spriteFrameI18n` on CCSpriteI18n | *(rare)* |
| `String` | plain string value | Generic string fields | Rarely distinct from Text in practice |
| `TableViewREDFile` | array of sub-red file paths | `tableviewRedFile` on CCTableView | *(rare)* |
| `Text` | string | `string` on CCRedLabel, CCLabelBMFont, CCLabelTTF | |
| `ToggleGroup` | integer direction: `0`=off, `1`=right/up, `-1`=left/down | `copyFlipXDir`, `copyFlipYDir` on CCSprite/CCScale9Sprite | See §2.4 CCSprite for runtime behavior |
| `VideoConfig` | `{filename: string, keepLW: bool, loop: bool}` | `videoConfig` on CCVideoPlayer | *(rare)* |
| `Wise` | dict — `{bnkFile, eventName, autoStop, params}` | `wiseOnTouchUpInside`, `wiseOnTouchDown` on REDNodeButton | |

**Deprecated types** (in enum but marked for removal; do not use): `TargetLanguages`, `FontStroke`, `VideoFile`.

---

## §2.4 All Node Types (baseClass)

### Tier-1 — Commonly Used

#### `CCLayer`
Root container. Always the root of `nodeGraph`. `ignoreAnchorPointForPosition: true` by default.
Properties: `contentSize` (Size), `position` (Position), `ignoreAnchorPointForPosition` (Check)

#### `CCLayerColor`
Layer with solid color fill.
Properties (adds to CCLayer): `color` (Color3), `opacity` (Byte), `blendFunc` (Blendmode)

#### `CCBlockTouchLayer`
Invisible layer that captures and blocks all touch events. Used to prevent touches from reaching nodes below.
Properties: `contentSize` (Size), `position` (Position), `color` (Color3), `opacity` (Byte), `visible` (Check)

#### `CCNode`
Generic container node.
Properties: `position` (Position), `anchorPoint` (Point), `contentSize` (Size), `scale` (ScaleLock), `rotation` (Degrees), `rotationX` (Degrees), `rotationY` (Degrees), `skew` (FloatXY), `tag` (Integer), `opacity` (Byte), `color` (Color3), `visible` (Check), `ignoreAnchorPointForPosition` (Check), `cascadeOpacityEnabled` (Check), `cascadeColorEnabled` (Check)

#### `CCSprite`
Renders a single sprite frame.
Properties (adds to CCNode): `displayFrame` (SpriteFrame), `flip` (Flip — `[flipX:bool, flipY:bool]`; **single** property, NOT two Check properties), `blendFunc` (Blendmode), `copyFlipXDir` (ToggleGroup), `copyFlipYDir` (ToggleGroup), `useMaterial` (Check), `materialBall` (MaterialBall)

**`copyFlipXDir` / `copyFlipYDir` runtime behavior** (confirmed from `CCSprite.cpp → _updatePoly4CopyFliped`):

| Value | Effect on width (X) or height (Y) |
|-------|------------------------------------|
| `0` | Disabled — normal single-tile rendering, content size unchanged |
| `1` | **Copy right / up** — content size doubled in that axis. First tile = original sprite; second tile = mirrored copy. |
| `-1` | **Copy left / down** — content size doubled in that axis. First tile = mirrored copy; second tile = original sprite. |

Only `1` is observed in this project. `copyFlipXDir=1` is used on button backgrounds and progress bar tracks — the intended visual effect is a symmetric, centered texture that doesn't require a full-width source asset.

**Godot migration:** There is no direct equivalent. Recreate at runtime by combining the original image with a horizontally-flipped copy into an `ImageTexture` with doubled width. Example:
```gdscript
var img := tex.get_image()
var flipped := img.duplicate(); flipped.flip_x()
var combined := Image.create(img.get_width() * 2, img.get_height(), ...)
combined.blit_rect(img, ...)
combined.blit_rect(flipped, ..., Vector2i(img.get_width(), 0))
```

Source: `CCSpriteLoader.cpp`, `CCSprite.cpp`

#### `CCScale9Sprite`
Nine-patch resizable sprite. Default anchor `(0, 0)` (set by loader).
Properties: `spriteFrame` (SpriteFrame), `preferedSize` (Size), `insetLeft/Top/Right/Bottom` (Float), `blendFunc` (Blendmode), `copyFlipXDir/Y` (ToggleGroup), `previewInset` (Check — editor only), `useMaterial` (Check)

`copyFlipXDir/Y` behaves identically to CCSprite (see above) but also correctly mirrors the nine-patch insets for each tile — e.g. `copyFlipXDir=1` with `insetLeft=20, insetRight=20` produces a symmetric nine-patch where both halves have consistent cap widths.

Source: `CCScale9SpriteLoader.cpp`

#### `CCRedLabel`
Custom dual-layer bitmap font label (Redream extension).
Properties:
- `string` (Text), `frontBMFntFile` (FntFile), `frontColor` (Color3), `frontOpacity` (Byte), `frontFontI18n` (FontI18n)
- `backBMFntFile` (FntFile), `backColor` (Color3), `backOpacity` (Byte), `backFontI18n` (FontI18n)
- `horizontalAlignment` (IntegerLabeled: 0=left, 1=center, 2=right)
- `verticalAlignment` (IntegerLabeled: 0=top, 1=center, 2=bottom)
- `dimensions` (Size), `enableWrap` (Check), `blendFunc` (Blendmode)
- `localizationV2` (LocalizationV2)
- Plus standard: `position`, `anchorPoint`, `scale`, `rotation`, `opacity`, `color`, `visible`

#### `CCProgressTimer`
Progress bar sprite.
Properties: `displayFrame` (SpriteFrame), `type` (IntegerLabeled: `0`=vertical, `1`=horizontal), `midpoint` (Point), `barChangeRate` (Point), `percentage` (Float — initial fill 0.0–100.0), plus standard node properties

#### `REDFile`
Embeds another `.red` file as a child scene component.
Properties:
- `redFile` (REDFile) — relative path to the sub-red file; e.g., `"ui/G010Item.red"`
- `animation` (Animation) — sequence to activate on load; `-2` = default/none
- Standard transforms: `position`, `scale`, `rotation`, `opacity`, `color`, `visible`

The `reboltId` of a REDFile node becomes the key in `.rebolt`'s `RedFileList`.

#### `REDNodeButton`
Tappable button built on CCControl.
Properties: `preferedSize` (Size), `enabled` (Check), `touchMoveCancel` (Check), `touchMoveCancelDistance` (Float), `swallowTouches` (Check), `zoomOnTouchDown` (Check), `ccControl` (BlockCCControl), `wiseOnTouchUpInside` (Wise), plus standard node properties

#### `RedSafeAreaLayer`
Adjusts children to stay within device safe area (notch/home-bar).
Properties: `position`, `opacity`, `color`, `ignoreAnchorPointForPosition` (Check)

#### `REDPolygonClippingNode2`
Clips children to a polygon shape.
Properties: `polygonVerts` (PolygonVerts), `Inverted` (Check), `debugVerts` (Check), `contentSize` (Size), `position`, `opacity`, `color`

#### `MatteNode` / `MatteRenderNode`
Matte/mask pair for masking effects. `MatteNode` is the mask source; `MatteRenderNode` is the render target.

#### `RParticleSystem`
Particle effect system (50+ properties). Key fields:
- `displayFrame` (SpriteFrame), `position`, `scale`, `visible`, `blendFunc`, `contentSize`
- `redreamTimelineEvent` (RedreamTimelineEvent)
- Module enable flags (SeparatorCheck): `EmissionModuleBurstEnabled`, `SizeModuleEnabled`, `RotationModuleEnabled`…
- `EmissionModuleRate` (MinMaxCurveData), `EmissionModuleBurst` (EmissionData)
- `LengthInSec` (Float), `LoopingModeLooping` (Check), `MaxNumParticles` (Integer)

Source: `RParticleSystemLoader.cpp`

#### `SkeletonAnimation` / `SkeletonAnimation4`
Spine 2D/4.x skeletal animation.
Properties: `dataFile` (SpineSkel), `atlasFile` (SpineAtlas), `skin` (Skin), `frame` (SkelFrame), standard transforms

---

### Tier-2 — Engine-Available

| baseClass | Key unique properties | Notes |
|-----------|-----------------------|-------|
| `CCLabelBMFont` | `fntFile` (FntFile), `string` (Text), `horizontalAlignment`/`verticalAlignment` (IntegerLabeled), `dimensions` (Size), `enableWrap` (Check), `lineSpace` (Float), `localizationV2` | Standard bitmap font label |
| `CCLabelTTF` | `fontName` (FontTTF), `fontSize` (FloatScale), `string` (Text), `horizontalAlignment`/`verticalAlignment`, `dimensions`, `enableWrap`, `localizationV2` | System/TTF font label |
| `CCLabelPlus` | `labelConfig` (LabelConfig) | Multi-segment rich text label |
| `CCScrollView` | `contentSize` → `setViewSize()`, `direction` (IntegerLabeled: 1=H, 2=V, 3=both), `bounces` (Check), `clipsToBounds` (Check), `container` (REDFile) | Scrollable container |
| `CCTableView` | `tableviewRedFile` (TableViewREDFile), `direction`, `vordering` | Table/list view |
| `CCVideoPlayer` | `videoConfig` (VideoConfig — `{filename, keepLW, loop}`) | Video playback |
| `CCMenuItemImage` | `normalSpriteFrame`, `selectedSpriteFrame`, `disabledSpriteFrame` (SpriteFrame) | Menu item with states |
| `CCControlButton` | `preferedSize`, `zoomOnTouchDown`, `title\|1/2/3` (Text), `titleColor\|1/2/3`, `backgroundSpriteFrame\|1/2/3`, `localization` | Older-style button. `REDNodeButton` is modern replacement |
| `CCLayerGradient` | `startColor`/`endColor` (Color3), `startOpacity`/`endOpacity` (Byte), `vector` (Point) | Color gradient layer |
| `CCParticleSystemQuad` | `texture`, `emitterMode`, `duration`, `totalParticles`, legacy particle params | Older particle system; `RParticleSystem` is modern replacement |
| `ZMLParticleSystem` | Similar to CCParticleSystemQuad | Extended legacy particle system |
| `ZGFrameActionSprite` | `frameNamePrefix` (String), `frameIndex` (Integer) | Frame-sequence animation |
| `UICheckBox` | `isSelected` (Check), `backgrounds` (SpriteFrame array), `frontCross` (SpriteFrame) | Checkbox widget |
| `UISlider` | `percent` (Percent), `bar` (SpriteFrame), `ball` (SpriteFrame) | Slider widget |
| `UIEditBox` | `placeHolder` (Text), `text` (Text), `inputMode`, `password`, `fontName`, `fontSize`, `fontColor`, `maxLength` | Text input field |
| `CCSpriteI18n` | `spriteFrameI18n` (SpriteFrameI18n — per-language frame map) | Locale-swapping sprite |
| `TiledPolygonSprite` | `pbVertsFile` (PbVertsFile) | Tiled texture along polygon path |
| `RedBakeNode` | `bakeDataFile` (BakeDataFile), `bakeAnimation` (BakeAnimation), `texture` | Baked render node |
| `CCMenu` | Container for CCMenuItem nodes | Legacy menu container |
| `REDPolygonClippingNode` | Same as `REDPolygonClippingNode2` | v1 variant, superseded |
| `CCSpritePlus` | Same as `CCScale9Sprite` | Alias |

---

## §2.5 Animated Properties

`animatedProperties` on any node — dict keyed by **sequenceId as string**:

```json
{
  "3": {
    "scale": {
      "name": "scale",
      "type": 4,
      "keyframes": [
        {
          "time": 0.0,
          "value": [1.0, 1.0],
          "name": "scale",
          "type": 4,
          "easing": {"type": 35, "opt": [0.384, -0.217, 1.0, -0.116]},
          "pathValues": []
        },
        {
          "time": 0.233,
          "value": [0.0, 0.0],
          "name": "scale",
          "type": 4,
          "easing": {"type": 1}
        }
      ]
    }
  }
}
```

**Property type integer codes in keyframes:**

| `type` | Property |
|--------|----------|
| `1` | Check (visible) |
| `2` | Degrees (rotation) |
| `3` | Position |
| `4` | ScaleLock (scale) |
| `5` | Byte (opacity) |
| `14` | SkelFrame (SkeletonAnimation frame) |
| `15` | Animation |
| `18` | Wise audio event (wiseChannel) |
| `19` | RedreamTimelineEvent (RParticleSystem timeline trigger) |

**Common animated property names:** `animation`, `frame`, `opacity`, `position`, `redreamTimelineEvent`, `rotation`, `scale`, `visible`

**`pathValues` field in position keyframes** — A 7-element float array that may appear alongside `value` in position-type keyframes (keyframe `type: 3`). Observed structure:
```
[posX, posY, tangentX, tangentY, elem4, elem5, elem6]
```
- Elements 0–1: duplicate the keyframe's `value` position coordinates
- Elements 2–3: bezier tangent control point coordinates (observed behavior — not confirmed from C++ source)
- Elements 4–6: zero in most `.red` scene files, but **non-zero in `.anim` path animation files** (e.g., `[1.0, 1.0, 2.0]`). Exact purpose unknown; possibly related to path interpolation weights or secondary control points.

When `pathValues` is an empty array `[]`, only the `value` coordinates are used. The `pathValues` field appears in both `.red` scene files and `.anim` path animation files.

---

## §2.6 Sequences Array

Each entry in the root `sequences` array:

| Field | Type | Meaning |
|-------|------|---------|
| `sequenceId` | integer | Unique ID within file; used as string key in `animatedProperties` and in `.rebolt` timeline actions |
| `name` | string | Display name; e.g., `"默认状态"`, `"完成状态"`, `"消散"` |
| `length` | real | Duration in seconds |
| `autoPlay` | bool | Play automatically on scene load |
| `chainedSequenceId` | integer | Next sequence to play after this ends; `-1` = none |
| `resolution` | real | Keyframe resolution in FPS; typically `30.0` |
| `callbackChannel` | dict | Code execution events |
| `shakeChannel` | dict | Screen shake events |
| `soundChannel` | dict | Audio events |
| `wiseChannel` | dict | Wwise audio events |

**Wwise channel keyframe `value` format:** `[bankName: string, eventName: string, autoStop: bool, parameters: array]`
Example: `["SeekAndFind.bnk", "seek_popup_fail", true, []]`

**Editor-only sequence fields** — These fields appear in every sequence entry alongside the runtime fields above. They have **no runtime effect** and can be ignored during migration:

| Field | Type | Meaning |
|-------|------|---------|
| `offset` | real | Timeline viewport scroll offset saved by editor |
| `position` | real | Playhead position saved by editor |
| `scale` | real | Timeline zoom level saved by editor (e.g., `128.0`) |
| `timelineStartPlay` | real | Editor playback start marker |
| `timelineEndPlay` | real | Editor playback end marker |
| `shake2Channel` | dict | Secondary shake channel (same structure as `shakeChannel`); observed empty in all project files; purpose unknown |

---

## §2.7 Guides (Root Level)

Editor layout guides — runtime irrelevant:
```json
{"orientation": 0, "position": -0.5, "type": 0}
```
`orientation`: 0 = vertical line, 1 = horizontal line

---

## §2.8 Resolutions (Root Level)

Defines screen size targets for editor preview. Runtime loads from actual device.

```json
{
  "name": "1080x2080",
  "width": 1080, "height": 2080,
  "scale": 2.0, "mainScale": 2.0,
  "additionalScale": 2.0, "resourceScale": 2.0,
  "centeredOrigin": false
}
```

`mainScale` is the device scale factor used in UIPOINTS unit calculations.

---

## Quick Reference: .red ↔ .rebolt Relationship

```
Example.red                       Example.rebolt
─────────────────────             ──────────────────────────
nodeGraph:                        CustomFunc:
  CCNode "物品整个"                 "消散": [["Name","消散","8AN6TjS5ZHof",…]]
    reboltId: "wpLIsiaEpAxH"
    CCSprite "物品"               TreeList:
      reboltId: "ahiITqBTmq6J"     Tree10 (randomID "8AN6TjS5ZHof"):
                                     BTCustomFuncHeadAction "消散"
sequences:                             → BTPlayTimeLineAction
  {sequenceId:3, name:"消散",               baseSelect.Value = "3" ──┐
   length:0.233}  ◄───────────────────────────────────────────────────┘

  REDFile node                     RedFileList:
    reboltId: "IDFVujQFWo9f"  ──►   "IDFVujQFWo9f": { TreeList:{…} }
    redFile: "ui/SubScene.red"
```

---

## Known Gaps

- **`pathValues` bezier tangent semantics**: Elements 2–3 of the 7-float `pathValues` array in position keyframes are observed to look like bezier control point offsets, but their exact interpretation (relative vs absolute, coordinate space) is not confirmed from `CCNodeLoader.cpp`. Elements 4–6 are non-zero in `.anim` files (e.g., `[1.0, 1.0, 2.0]`) — purpose unknown. Treat with caution when reconstructing path animations.
- **`shake2Channel` purpose**: Structure is identical to `shakeChannel` but observed empty in all project files. No documentation found for how it differs from the primary `shakeChannel`.

All other content in this file is confirmed complete against `Libraries/redream/*.cpp` and all 191 observed project `.red` / 3 `.anim` source files.
