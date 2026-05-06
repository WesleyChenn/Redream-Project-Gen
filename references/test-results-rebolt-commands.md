# Redream CLI Baseline And Update Notes

Date: 2026-03-31

Validation baseline:

- binary: `/Users/jer/workspace/ai_dev_trial/Redream/build/bin/Redream/Redream.app/Contents/MacOS/Redream`
- source repo: `/Users/jer/workspace/ai_dev_trial/Redream`
- branch context used for audit: `feature/f108_redream_cli`

This file replaces the older "sample output" style note with a current CLI surface audit. Use it as the validation anchor for the skill when command memory and older docs disagree.

## Recent CLI Update Record Checked

Most recent relevant CLI commits inspected:

- `0715e2bd` `开发：继续完善 CLI`
- `ce236ca1` `优化：继续开发 CLI`
- `d61b5607` `开发：继续完善 CLI`
- `cd2b966f` `开发：继续补充 CLI`
- `cac5ead8` `优化：继续完善CLI功能`

These commits align with the current binary and explain why older skill docs were stale.

## Current Public Surface

### `inspect`

Current `inspect actions --json` exposes:

- `actions`
- `project`
- `files`
- `scene`
- `node`
- `timelines`
- `timeline`
- `resources`
- `check`
- `duplicates`
- `references`

Confirmed changes vs older docs:

- `inspect` now has `actions`
- `inspect scene` and `inspect timelines` prefer `--scene <file.red>`
- source still accepts compatibility positional scene paths for `scene` and `timelines`
- JSON mode for `inspect scene` always includes property payloads
- `inspect check` now includes stricter keyframe-field and property-value-type validation

### `modify`

Current `modify actions --json` exposes:

- `actions`
- `project`
- `scene`
- `set-property`
- `batch`
- `timeline`
- `timeline-channel`
- `keyframe`
- `add-node`
- `delete-node`
- `rename-node`
- `move-node`
- `duplicate-node`
- `add-timeline`
- `delete-timeline`
- `duplicate-timeline`
- `duplicate-file`
- `new-scene`
- `new-project`
- `set-rebolt-public`
- `build-scene`

Confirmed changes vs older docs:

- `modify` now has `actions`
- `modify` now has `scene`
- `modify` now has `timeline-channel`
- `modify` now has `build-scene`
- `modify project` can mutate `global_msg.<key>` and `global_var.<key>`
- `modify timeline` now supports `--scale`, `--position`, `--offset`, `--start-play`, `--end-play`, `--play-speed`
- `modify timeline` / `modify add-timeline` now accept sequence ID, timeline name, or `-1` in `--chain`
- `modify new-scene` now supports `--enable-rebolt`
- `modify new-scene` now supports `--no-default-timeline`
- `modify new-scene` now supports `--no-rebolt-file`
- `modify build-scene` now supports `--preserve-rebolt-ids`
- `modify set-rebolt-public` supports `--rebolt-id`

Current option additions confirmed in source and help:

- `--enable-rebolt`
- `--no-default-timeline`
- `--no-rebolt-file`
- `--preserve-rebolt-ids`
- `--channel`
- `--scale`
- `--position`
- `--offset`
- `--start-play`
- `--end-play`
- `--play-speed`
- `--rebolt-id`

### `rebolt`

Current public actions:

- `list`
- `export`
- `validate`

Validation semantics were corrected during the audit:

- `rebolt validate` now performs project-wide structural validation and can also surface paired-scene reference issues that are recoverable from companion `.red` metadata
- it loads each file through `BTTreeOperations::loadReboltFile`
- it reports `parse_failed` when a file cannot be parsed
- it reports `validation_failed` when `BTTreeOperations::validateTree` returns issues
- it should now be treated as the project-scope counterpart to `rebolt-modify validate`

### `rebolt-modify`

Current `rebolt-modify actions --json` exposes:

- `read`
- `set-section`
- `set-entry`
- `remove-entry`
- `validate`
- `add-block`
- `set-prop`
- `set-var`
- `add-var`
- `remove-var`
- `undo`
- `remove-block`
- `copy-block`
- `move-block`
- `add-func`
- `remove-func`
- `rename-func`
- `diff`
- `export-tree`
- `import-tree`
- `add-tree`
- `list-blocks`
- `block-info`
- `search`
- `batch`
- `actions`

Confirmed changes vs older docs:

- `set-section`, `set-entry`, and `remove-entry` are now public actions
- `--value-file` is supported for `set-section` and `set-entry`
- `read` now supports `--section`, `--entry`, and `--block-id`
- `add-tree` and `batch` are public in both `--help` and `actions --json`
- `list-blocks` no longer needs `--rebolt`
- `block-info` no longer needs `--rebolt`
- `import-tree` reads the input path from `--value <inputFile>`
- `inspect --help` now explicitly routes single-file `.rebolt` reads to `rebolt-modify read`
- `inspect actions --action-name actions` now mirrors the same single-file `.rebolt` routing note
- `rebolt --help` now explicitly says it is project-level `list/export/validate`, not the single-file read surface
- `rebolt-modify --help` now advertises `read` as the single-file read-only inspection entry point
- `rebolt-modify actions --action-name read` now mirrors the same single-file inspection wording
- `rebolt-modify --help` now also matches runtime behavior for `--rebolt`: absolute paths work, and project-relative paths work when paired with `--project`
- public docs should describe `rebolt validate` / `rebolt-modify validate` as paired-`.red` aware validation surfaces, not structure-only checks

Schema-parity updates confirmed in the current binary/tests:

- `block-info` and `add-block` now expose/use richer headless `defaultJson` templates for GUI-only block families such as node animation, transform, message, button helpers, ads/control helpers, timeline/skeleton helpers, list-variable helpers, and function-head/simulator helpers
- `set-prop` repairs legacy broken BTInputSlot / selector wrappers from block metadata, rejects unknown nested paths without a schema template, and normalizes selector/string-like values back to strings
- `rebolt-modify validate` and `rebolt validate` now catch missing required structured properties for known block schemas, while still allowing legacy slot-embedded expression blocks and `CallBackInfo` reference wrappers that do not serialize full block bodies; current headless defaults for `BTNodeSetAnimAction` / `BTNodeSetAnimWaitAction` / `BTNodeSetAnimActionWithCallBack` include `rotateCheck`
- `rebolt-modify add-block` / `set-prop` now validate selector writes against the paired `.red` scene before saving, including node-exists and supported-node-class checks for button / label / sprite / progress helpers
- `rebolt-modify validate` now hard-fails empty `reboltName`, ambiguous `reboltName` aliases, missing selector targets, and selector/node-type mismatches against the paired `.red`; blank helper selectors remain allowed until the caller fills them
- `inspect check` / `rebolt validate` now report `RedFileList` keys that point to a normal `CCNode` or other non-`REDFile` target as invalid `REDFile` node bindings; empty strings or empty `::` path segments remain legacy bad-data examples that surface through the same reference-integrity path

## Verified Divergences And Hidden Surface

These are the important inconsistencies that the skill must model explicitly.

### `modify --help` and `modify actions --json` are currently aligned

Observed:

- `modify --help` now lists `build-scene`
- `modify actions --json` also exposes `build-scene`
- usage strings for the current binary match the broadened modify surface

Rule:

- treat `modify actions --json` as the primary machine-readable source
- use `modify --help` as a cross-check, not as a blocker for `build-scene`

### `rebolt-modify add-tree` and `batch` are now public

Observed:

- dispatcher routes `add-tree`
- `rebolt-modify --help` lists `add-tree` and `batch`
- `rebolt-modify actions --json` also lists `add-tree` and `batch`

Rule:

- treat both commands as public for the current binary
- they are no longer hidden/internal surfaces

### Old absolute/relative `rebolt export --tree` note was stale

Current source matches against both:

- relative resource path
- absolute filesystem path

So the older statement "relative path only" should no longer be treated as current truth.

## Command Precedence For The Skill

When CLI memory conflicts with docs, resolve in this order:

1. current binary `... actions --json`
2. current binary `... --help`
3. current source under `Classes/CLI/`
4. this validation note
5. any older examples or archived test output

## Blocking Guidance For Future Skill Use

- Do not claim a command exists only because an older skill file mentioned it.
- Do not claim a command is stable if it is present only in source and absent from public help/action output.
- Do not keep using the older "add-tree is hidden" guidance; it is stale for the current binary.
- Do not describe `rebolt validate` as a non-structural or non-empty-only check.
- Do not document `inspect scene <file.red>` as positional-only; `--scene` is the preferred contract now.
