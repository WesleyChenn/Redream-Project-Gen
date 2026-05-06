# Redream Must Not And Blocking Rules

Use this file whenever a Redream/Rebolt task is underspecified, risky, or likely to create broken assets.

## Must Not

### Inspection And Mutation

- Do not modify before inspecting the actual project structure.
- Do not guess node paths.
- Do not guess timeline names, function names, or tree names.
- Do not assume CLI path format from class names or editor hierarchy intuition.
- Do not skip post-change validation.

### CLI Usage

- Do not fall back to direct file editing if CLI already supports the operation.
- Do not run write commands against an uncertain project path.
- Do not mutate without confirming the target scene or rebolt file.
- Do not ignore dry-run or validation options when the task is high-risk.

### Naming And Standards

- Do not invent file names, node names, timeline names, or notify names during structured conversion work.
- Do not introduce naming that conflicts with `project-standards.md`.
- Do not create scene structure that conflicts with `project-standards.md` or `project-patterns.md`.
- Do not mix deprecated Rebolt patterns back into new work if `rebolt-standards.md` marks them obsolete.

### Rebolt

- Do not invent `通知工程师` names.
- Do not create function names or variable names without checking project conventions.
- Do not use global variables or deprecated block patterns when project standards say not to.
- Do not set unrelated binding fields if only `reboltName` is required.

### Figma Conversion

- Do not skip the project configuration confirmation.
- Do not invent names not present in the Figma engineering document.
- Do not write `.red` or `.rebolt` directly while CLI is available and sufficient.
- Do not compress all phases into one pass without intermediate checks.

## Blocking Conditions

Stop and inspect, or explicitly mark the output as partial, when any of the following is true.

### Project Contract Missing

- `.redproj` path unknown
- target scene or rebolt file unknown
- resource root unclear
- CLI binary unavailable and fallback path unconfirmed

### Scene Contract Missing

- actual node path unknown
- target parent path unknown
- timeline name or ID unknown
- whether a node already exists is unknown

### Rebolt Contract Missing

- target function or tree unknown
- variable names unknown
- slot path unknown
- notify naming convention unknown

### Figma Contract Missing

- project config unanswered
- Figma engineering structure incomplete
- required file naming source missing
- target scene decomposition unclear

## Allowed Partial Output When Blocked

If blocked, it is valid to provide:

- an inspection plan
- the exact information still needed
- a CLI command sequence for verification
- a naming/structure checklist
- a partial phase-by-phase conversion plan

It is not valid to silently invent missing contracts and continue mutating files.

## Red Flags

Treat these as strong stop signals:

- request says “just make it like the old project” with no exact files
- node path is inferred from screenshots only
- conversion work lacks agreed file naming source
- logic change requires a Rebolt function that cannot be identified
- direct XML/JSON edits are proposed only because inspection was skipped

## Enforcement Priority

When rules conflict, prefer:

1. verified project contract
2. CLI-supported mutation path
3. project standards and naming consistency
4. speed

Speed is never enough reason to violate the first three.
