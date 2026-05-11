# Redream Development Workflow

Use this file for end-to-end Redream/Rebolt work on existing projects or new project creation.

## Goal

Produce Redream assets and Rebolt logic that are:

- CLI-verifiable
- naming-consistent
- structurally standard
- safe to hand off to code integration later

## Phase 1: Clarify The Task Type

Classify the work before touching files.

Common task types:

- inspect existing project
- modify existing scene or rebolt logic
- create new project or new scene
- convert from Figma engineering document
- standardize an existing asset set

If the task type is unclear, do not jump into mutation commands.

## Phase 2: Confirm The Contract

Before editing, confirm the minimum contract:

- project path
- target `.redproj`
- target `.red` or `.rebolt` file
- exact node path, timeline name, function name, or resource path
- whether the operation should be CLI-first or direct-source fallback

If any of these are missing, inspect first.

Use:

- `references/cli-inspect.md`

## Phase 3: Inspect First

Default rule: inspect before modify.

Typical inspection order:

1. list project files
2. inspect scene tree
3. inspect node details
4. inspect timelines
5. inspect the `.rebolt` file if behavior logic is involved, using `rebolt-modify read` rather than a non-existent `inspect rebolt` action

Use:

- `references/cli-inspect.md`
- `references/redream.md`
- `references/rebolt.md`

## Phase 4: Choose The Editing Path

### Path A: CLI-first

Use CLI when:

- the target node/path is known
- the mutation is supported by `modify` or `rebolt-modify`
- a dry-run or validation path exists

### Path B: Direct format fallback

Use source-file fallback only when:

- CLI cannot express the operation
- CLI is unavailable
- the task requires understanding or repairing low-level structure

If using fallback, the file format references become mandatory.

## Phase 5: Apply Standards

Before creating or renaming anything, load the smallest relevant standards file.

Typical mappings:

- project layout, naming, engineering: `project-standards.md`
- Rebolt conventions: `rebolt-standards.md`
- asset/UI/sound rules: `asset-standards.md`
- font/multilang: `i18n-standards.md`
- shared project patterns: `project-patterns.md` (in `guides/`)

Do not create new content first and “standardize later”.

## Phase 6: Modify

When mutating:

1. prefer CLI
2. use exact names from inspection
3. keep naming and folder placement consistent with standards
4. if adding Rebolt logic, keep function and notify patterns aligned with project standards

Use:

- `references/cli-modify.md`

## Phase 7: Validate

Every mutation should be followed by validation.

Minimum validation options:

- `inspect scene`
- `inspect node`
- `inspect check`
- `rebolt validate`
- `rebolt-modify validate`

For Figma conversion, validate both structure and logic scaffolding phase by phase instead of only at the end.

If the task changed CLI code or the public CLI contract:

- update the matching `--help` text in the same change
- update the matching `actions --json` metadata in the same change
- update the corresponding markdown references in `references/`
- verify help, machine-readable action output, and markdown docs are still aligned before handoff

## Phase 8: Handoff Readiness

Before considering the asset work complete, check:

- paths and names are standard
- required nodes expose correct `reboltName` / `reboltId` contracts
- timelines and functions follow conventions
- scenes pass integrity checks
- downstream code can refer to exact asset names without guessing
- if CLI surface changed, public help and markdown references were updated in the same batch

## Special Path: Figma To Redream

For Figma conversion:

1. use `workflow-config.md` to constrain the intake questions
2. use `figma-to-redream.md` for execution order
3. pull in standards only for the current phase
4. validate at each phase boundary

Do not compress the whole process into one mutation pass.

## What This Workflow Prevents

- editing the wrong file because the path was assumed
- mutating nodes before confirming actual display names
- non-standard naming and scene layout drift
- Rebolt logic that cannot be matched by downstream code
- direct file edits that are never CLI-verified
