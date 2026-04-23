# Cocos2d-x Fundamentals

Core concepts needed to interpret `.red` scene layout files and `.rebolt` behavior trees in the Redream UI framework.

**Engine:** Cocos2d-x 3.x, C++17
**Loader source:** `Libraries/redream/*.cpp` — authoritative reference for all property types and node behavior.

---

## Quick Lookup

| If you encounter… | Go to |
|---|---|
| Position value `[x, y, xUnit, yUnit, corner]` — decode units | §1.1 PositionUnit table |
| Size value `[w, h, wUnit, hUnit, ...]` — decode units | §1.1 SizeUnit table |
| Position 5th element (corner integer 0–3) | §1.2 Reference Corner |
| `anchorPoint` value (two floats 0.0–1.0) | §1.3 Anchor Point |
| `easing.type` integer in a keyframe | §1.6 easing.type table |
| `easing.opt` value (array or single float) | §1.6 easing.opt note |
| `curvePreset` string in a BT action | §1.8 Rebolt Action Easing Curves |
| `CCSprite` / `CCScale9Sprite` / `CCRedLabel` concept | §1.4 Sprite and Atlas / §1.5 CCRedLabel |
| `ignoreAnchorPointForPosition` behavior | §1.3 Anchor Point |

---

## §1.1 Coordinate System

- **Origin:** bottom-left corner `(0, 0)`. Y-axis points **upward**.
- **`position` unit types** — `PositionUnit` (3 values only; confirmed from `CCNodeLoader.cpp → getAbsolutePosition`):

| Integer | Name | Meaning |
|---------|------|---------|
| `0` | POINTS | Absolute design points × `resolutionScale` |
| `1` | UIPOINTS | Absolute points × `resolutionScale` × `mainScale` |
| `2` | NORMALIZED | `value / 100 × containerDimension` (percentage) |

- **`contentSize` / `preferedSize` / `dimensions` unit types** — `SizeUnit` (5 values; confirmed from `CCNodeLoader.cpp → getAbsoluteSize`):

| Integer | Name | Meaning |
|---------|------|---------|
| `0` | POINTS | `value × resolutionScale` |
| `1` | UIPOINTS | `value × resolutionScale × mainScale` |
| `2` | NORMALIZED | `value / 100 × containerDimension` |
| `3` | INSETPOINTS | `containerDimension − value × resolutionScale` |
| `4` | INSETUIPOINTS | `containerDimension − value × resolutionScale × mainScale` |

**Important:** `INSETPOINTS`/`INSETUIPOINTS` only exist in `SizeUnit`, NOT in `PositionUnit`.

## §1.2 Reference Corner (Position 5th element)

Which corner of the parent the position is measured from (confirmed from `CCNodeLoader.cpp`):

| Value | Corner | Transform |
|-------|--------|-----------|
| `0` | BOTTOMLEFT | No transform (default Cocos2d-x origin) |
| `1` | TOPLEFT | `y = containerHeight − y` |
| `2` | TOPRIGHT | `x = containerWidth − x`, `y = containerHeight − y` |
| `3` | BOTTOMRIGHT | `x = containerWidth − x` |

## §1.3 Anchor Point

Normalized `(x, y)` in 0.0–1.0 defining the registration and pivot point.

| Value | Meaning |
|-------|---------|
| `(0.5, 0.5)` | Center — most common for game objects |
| `(0.0, 0.0)` | Bottom-left (default for CCScale9Sprite, set by loader) |
| `(0.5, 0.0)` | Bottom-center |
| `(0.5, 1.0)` | Top-center |

`ignoreAnchorPointForPosition: true` (CCLayer default) means anchor does not shift the node's position, but still acts as scale/rotation pivot.

## §1.4 Sprite and Atlas

- **CCSprite:** renders one frame. Property `displayFrame` (SpriteFrame type) = `[plistPath, frameName]`.
- **Plist Atlas:** multiple frames packed into one `.webp` texture + `.plist` descriptor. Reduces draw calls.
- **CCScale9Sprite:** nine-patch resizable sprite. `preferedSize` = rendered size; `insetTop/Bottom/Left/Right` = non-stretching border widths in pixels. Default anchor `(0, 0)`. Source: `CCScale9SpriteLoader.cpp`.

## §1.5 CCRedLabel

`CCRedLabel` is a Redream extension node — a custom dual-layer bitmap font label. Renders two overlapping font layers: front (text) and back (outline/shadow). Used instead of `CCLabelBMFont`/`CCLabelTTF` for pre-styled bitmap text with built-in outline rendering.

## §1.6 Timeline Animation System

Animations are **Sequences** with keyframe tracks per property. Easing types (`easing.type` integer):

| Value | Behavior |
|-------|---------|
| `0` | Linear |
| `1` | Ease In |
| `4` | Ease Bounce In |
| `6` | Ease Sine In |
| `11` | Ease Exponential In |
| `12` | Ease Exponential Out |
| `16` | Ease Bounce Out |
| `35` | Custom Cubic Bézier — `opt: [x1, y1, x2, y2]` |

**`easing.opt` field** — Optional parameter accompanying `easing.type`:
- **Type `35`** (Custom Cubic Bézier): `opt` is a 4-element array `[x1, y1, x2, y2]` — cubic bezier control points in normalized time/value space.
- **Other types** (e.g., `4` Bounce In, `6` Sine In, `11` Exp In): `opt` can be a **single real number** — observed in `.anim` path files as a tension or amplitude modifier (e.g., `opt: 2.0`). Exact per-type semantics not confirmed from C++ source.
- **Absent**: When `easing.opt` is not present, the easing type uses its default curve with no modifier.

## §1.7 Node Tree and Rendering

- Children array order = render order; **last child renders on top**.
- Parent transforms (position, scale, rotation, opacity) cascade to all descendants.
- `visible: false` hides the entire subtree.
- `opacity` cascades multiplicatively (0–255 each level).

## §1.8 Rebolt Action Easing Curves

Actions using `curvePreset` parameter (e.g., `BTNodeScaleToAction`, `BTProgressFromToAction`) support these named easing types (from `BTCurveActionFactory.cpp`):

`EasingInstant`, `EasingLinear`, `EaseIn`, `EaseOut`, `EaseInOut`,
`EaseSineIn`, `EaseSineOut`, `EaseSineInOut`,
`EasingBounceIn`, `EasingBounceOut`, `EasingBounceInOut`,
`EasingElasticIn`, `EasingElasticOut`, `EasingElasticInOut`,
`EasingBackIn`, `EasingBackOut`, `EasingBackInOut`,
`EaseExponentialIn`, `EaseExponentialOut`, `EaseExponentialInOut`,
`EaseCircleActionIn`, `EaseCircleActionOut`, `EaseCircleActionInOut`,
`EaseQuadraticActionIn`, `EaseQuadraticActionOut`, `EaseQuadraticActionInOut`,
`EaseCubicActionIn`, `EaseCubicActionOut`, `EaseCubicActionInOut`,
`EaseQuarticActionIn`, `EaseQuarticActionOut`, `EaseQuarticActionInOut`,
`EaseQuinticActionIn`, `EaseQuinticActionOut`, `EaseQuinticActionInOut`

---

## §1.9 Sprite Atlas Plist Format

TexturePacker v3 export format used by all `.plist` files in `res_FindObject/plist/`.

**File structure:**
```
root dict
├── frames (dict)  — one entry per sprite, key = original filename (e.g. "加载_猫咪.png")
│   └── per-frame dict (see fields below)
└── metadata (dict)
    ├── format (integer)            — always 3 for this project
    ├── realTextureFileName (string) — atlas image filename (e.g. "loading.webp")
    └── size (string "{W,H}")       — total atlas image dimensions
```

**Per-frame fields:**

| Field | Format | Meaning |
|-------|--------|---------|
| `textureRect` | `{{x,y},{w,h}}` | Position in atlas + **logical (pre-rotation) dimensions** of the sprite |
| `textureRotated` | `true`/`false` | Whether the sprite was rotated 90° CW when packed into the atlas |
| `spriteSize` | `{w,h}` | Visible pixel size of the (possibly trimmed) sprite |
| `spriteSourceSize` | `{w,h}` | Original untrimmed source image size |
| `spriteOffset` | `{dx,dy}` | Pixel offset from center of source image to center of trimmed region |

**Critical: rotation affects how to interpret `textureRect` dimensions.**

When `textureRotated = false`:
- Atlas region: `(x, y)` to `(x + textureRect.w, y + textureRect.h)`
- Use directly as-is

When `textureRotated = true`:
- `textureRect.w` = sprite's original (logical) width
- `textureRect.h` = sprite's original (logical) height
- **Actual atlas region has swapped dimensions:** `width = textureRect.h`, `height = textureRect.w`
- To crop: `(x, y, x + textureRect.h, y + textureRect.w)`
- To restore upright orientation: rotate 90° counter-clockwise after cropping

**Example (confirmed from `loading.plist` + `plist_to_atlas.py`):**
```
加载_猫咪.png:
  spriteSize       = {433, 563}   ← original sprite is 433×563
  textureRect      = {{649,515},{433,563}}
  textureRotated   = true

  → actual atlas region: crop (649, 515) to (649+563, 515+433) = (649,515,1212,948)
  → rotate 90° CCW → 433×563 upright image  ✓
```

**Old-format plist variant** — some older plist files use different key names:

| Old key | Equivalent new key |
|---------|-------------------|
| `frame` | `textureRect` |
| `sourceSize` | `spriteSourceSize` |
| `rotated` | `textureRotated` |
| `offset` | `spriteOffset` |

(Old format omits `spriteSize`; derive from `frame` rect dimensions instead.)

---

## Known Gaps

- **`easing.opt` single-float semantics per type**: The meaning of a single-real `opt` value for specific non-type-35 easing types (e.g., exactly what `opt: 2.0` does for Bounce In) is not confirmed from C++ source (`BTCurveActionFactory.cpp`). It is observed but the parameter name and effect per type is unknown.

All other content in this file is confirmed complete against the project's source files (`Libraries/redream/*.cpp`) and all observed `.red` / `.anim` / `.plist` files.
