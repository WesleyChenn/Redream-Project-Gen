# Redream CLI Read Surface

Source of truth for this file:

- current binary: `build/bin/Redream/Redream.app/Contents/MacOS/Redream`
- current source: `Classes/CLI/CCliInspect.cpp`, `CCliRebolt.cpp`, `CCliReboltModify.cpp`
- verified against the current CLI binary and recent help/action parity updates through 2026-04-09

Use this file for read-only inspection flows. For write operations, use `references/cli-modify.md`.

## Read First

- Prefer `Redream inspect actions --json`, `Redream rebolt-modify actions --json`, and `Redream ... --help` over memory.
- Prefer `--scene <file.red>` syntax in prompts and examples.
- Use `rebolt validate` for project-wide `.rebolt` structural + paired-`.red` reference/selector validation, and `rebolt-modify validate` for single-file structural + paired-`.red` selector / `reboltName` validation.
- Treat `inspect` as project/scene/resource inspection only. For a single `.rebolt` file, route to `rebolt-modify read`; top-level `rebolt` stays project-level only.
- Do not require `--rebolt` for `rebolt-modify list-blocks` or `rebolt-modify block-info`.
- Do not rely on hidden or source-only actions that are not exposed by `--help` or `actions`.

## `inspect`

Requires `--project <path>` or `-p`.

Scope note:

- `inspect` does not provide a public `inspect rebolt --rebolt <file>` action
- if you need one `.rebolt` file's functions, trees, or block subtree, use `rebolt-modify read`

Global options:

- `--json`: machine-readable output. For `inspect scene`, JSON mode always includes property payloads even without `--properties`.
- `--action-name <name>`: query one action from `inspect actions`.

### Public actions

| Action | Usage | Notes |
| --- | --- | --- |
| `actions` | `inspect actions [--action-name <name>] [--json]` | Lists current inspect surface from the binary. |
| `project` | `inspect project --project <path> [--json]` | Returns project settings, publish config, resource paths, languages, and current project globals. |
| `files` | `inspect files --project <path> [--type red\|rebolt\|resource] [--json]` | `--type` filters `.red`, `.rebolt`, or general resources. |
| `scene` | `inspect scene --scene <file.red> --project <path> [--properties] [--summary] [--json]` | Preferred form is `--scene`. Source still supports compatibility positional syntax for this action. JSON includes scene shell fields plus `nodeGraph`. |
| `node` | `inspect node --scene <file.red> --node <path> --project <path> [--json]` | Reads one node by slash path such as `root/panel/button`. |
| `timelines` | `inspect timelines --scene <file.red> --project <path> [--json]` | Preferred form is `--scene`. Source still supports compatibility positional syntax here. Returns per-timeline metadata plus channel summaries. |
| `timeline` | `inspect timeline --scene <file.red> --timeline <id\|name> --project <path> [--json]` | Shows one timeline's metadata, channel payload, and animated nodes. |
| `resources` | `inspect resources --project <path> [--unused] [--json]` | `--unused` filters to unreferenced resources. |
| `check` | `inspect check --project <path> [--skip-parse] [--json]` | Full project integrity pass. `--skip-parse` skips `.red` parse-derived checks. |
| `duplicates` | `inspect duplicates --project <path> [--json]` | Finds duplicate `memberVarAssignmentName` values per scene. |
| `references` | `inspect references --project <path> --resource <path> [--json]` | Finds resource references across scenes and keyframes. Does not inspect `.rebolt` internals. |

### `inspect scene` output shape

JSON mode includes scene shell fields plus `nodeGraph`:

- `centeredOrigin`
- `fileVersion`
- `fileType`
- `currentResolution`
- `currentSequenceId`
- `stageBorder`
- `referenceImgNode`
- `resolutions`
- `rebolt`
- `nodeGraph`

Text mode prints the same shell fields first, then the node tree.

### `inspect check` coverage

Current source validates:

- `.red` parse validity and presence of `nodeGraph`
- `.rebolt` structural + semantic issues through the `rebolt_validate` section, including selector uniqueness/type errors and invalid `RedFileList` bindings that can be diagnosed from the paired `.red`
- keyframes missing required `type` or `name`
- property value storage types for GUI-sensitive property kinds
- missing asset references through verifier database
- duplicate `reboltId` detection as a warning section

This is stricter than the older skill docs. It now catches common CLI write mistakes that would later break GUI loading.

Legacy compatibility notes for `inspect check` and publish-time verifier:

- verifier now tolerates legacy `rebolt.redInfos[*]` entries that were accidentally serialized as JSON strings instead of plist dictionaries
- when a historical `.red` keeps an old `rebolt.redInfos` key but the live node tree already regenerated that node's `reboltId`, verifier now tries a safe alias-based fallback
- that fallback only activates when the old `redInfos` alias maps uniquely to one current node in the same scene, so ambiguous alias collisions still surface as real issues
- `RedFileList` keys that resolve to a normal `CCNode` or any non-`REDFile` target are reported as invalid `REDFile` node bindings during `inspect check` / `rebolt validate`, not treated as a generic missing-reference case

### Timeline inspection notes

`inspect timelines` summarizes the five supported timeline channels:

- `callback`
- `sound`
- `wise`
- `shake`
- `shake2`

Each summary reports whether the channel exists and how many keyframes it contains.

## `rebolt`

Requires `--project <path>`.

This surface is project-level only. Use it for `list`, `export`, and `validate` across project resources, not for detailed inspection of one `.rebolt` file.

### Public actions

| Action | Usage | Notes |
| --- | --- | --- |
| `list` | `rebolt list --project <path> [--json]` | Lists all `.rebolt` files under project resource paths. JSON includes `absolutePath`. |
| `export` | `rebolt export --project <path> --output <dir> [--tree <path>] [--json]` | Copies raw `.rebolt` file bytes to the output directory. No format conversion is performed. `--tree` may match relative or absolute path. |
| `validate` | `rebolt validate --project <path> [--json]` | Project-wide structural validation. Loads each `.rebolt`, reports parse failures, then runs `BTTreeOperations::validateTree` on each file. Current project-wide checks also surface paired-scene issues that can be resolved from companion `.red` metadata, such as invalid `RedFileList` bindings and related reference integrity problems. |

## Read-oriented `rebolt-modify`

These actions operate on a single `.rebolt` file directly. `--project` is optional and only used when some actions want project context.

Use this surface for single-file `.rebolt` inspection. There is no public `inspect rebolt --rebolt <file>` action in the current CLI, and top-level `rebolt` remains the project-level route for `list`, `export`, and `validate`.

### Public actions

| Action | Usage | Notes |
| --- | --- | --- |
| `read` | `rebolt-modify read --rebolt <file> [--section <name>] [--entry <key>] [--tree <name>] [--block-id <id>] [--json]` | Reads the whole file, one top-level section, one entry, one tree, or one block subtree. `--rebolt` may be absolute, or project-relative when paired with `--project`. |
| `validate` | `rebolt-modify validate --rebolt <file> [--json]` | Single-file structural + paired-`.red` validation. Besides tree/schema checks, current CLI validation also enforces paired-scene selector target and `reboltName` rules. `--rebolt` may be absolute, or project-relative when paired with `--project`. |
| `list-blocks` | `rebolt-modify list-blocks [--category <name>] [--json]` | Lists available block classes by category. Does not require `--rebolt`. |
| `block-info` | `rebolt-modify block-info --type <class> [--json]` | Returns category, simulator-only flag, property list, and default JSON template. Use this as the source of truth for field names such as `BTSpriteImageAction.TitleInput` vs `BTSpritePlistAction.pathInput` + `frameNameInput`. Does not require `--rebolt`. |
| `search` | `rebolt-modify search --rebolt <file> --keyword <text> [--red <file>] [--json]` | Searches block types, selectors, function names, messages, and optionally resolved node names from a paired `.red` file. `--rebolt` may be absolute, or project-relative when paired with `--project`. |
| `actions` | `rebolt-modify actions [--action-name <name>] [--json]` | Lists current public rebolt-modify actions. |

### `rebolt-modify read` section support

Supported top-level sections:

- `DisPlayName`
- `TreeList`
- `CustomVar`
- `CustomList`
- `CustomMessage`
- `CustomFunc`
- `CustomTestFunc`
- `RedFileList`
- `RedNoteInfo`

`--entry` is only valid when the chosen section is an object. It is not valid for scalar sections such as `DisPlayName`.

### Common routing examples

List functions from one `.rebolt` file:

```bash
Redream rebolt-modify read --rebolt ccb/Foo.rebolt --section CustomFunc --project <path.redproj> --json
```

Read one function/block subtree after you know its `randomID`:

```bash
Redream rebolt-modify read --rebolt ccb/Foo.rebolt --block-id <randomID> --project <path.redproj> --json
```

Do not use this non-existent route:

```bash
Redream inspect rebolt --rebolt ccb/Foo.rebolt --project <path.redproj>
```

## Practical Guidance

- Use `inspect scene --json` before any write operation so later code generation or mutation steps work from exact field names and types.
- Use `inspect timelines` before touching timeline metadata or channel keyframes.
- Use `rebolt-modify block-info` before `add-block` so the generated properties match the registered block schema.
- For sprite swaps, inspect `block-info` instead of guessing: standalone image blocks use `TitleInput`; plist swaps use `pathInput` plus `frameNameInput`.
- Use `rebolt validate` after project-wide `.rebolt` changes, or `rebolt-modify validate` when you only need to validate one target file.
