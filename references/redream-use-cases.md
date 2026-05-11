# Redream Use Cases

Use this file for recurring Redream/Rebolt task shapes.

## Use Case 1: Inspect An Existing Scene

Scenario:

- user knows the scene file but not the exact node path or timeline name

Recommended path:

1. inspect scene tree
2. inspect properties if needed
3. inspect specific node only after the path is confirmed

Must not:

- guess node paths from class names
- assume a `root/...` path format

## Use Case 2: Modify A Known Node Property

Scenario:

- user knows the scene and node path
- property update is simple

Recommended path:

1. confirm node path with inspect
2. use CLI modify command
3. re-inspect or run project check

Must not:

- edit XML by hand first if CLI already supports the change

## Use Case 3: Add Or Reorder Scene Nodes

Scenario:

- user wants a new node, duplicate, move, rename, or reparent operation

Recommended path:

1. inspect parent path and sibling order
2. use `modify add-node`, `duplicate-node`, `move-node`, or `rename-node`
3. verify final tree

Must not:

- guess display-name paths
- reorder without inspecting current structure

## Use Case 4: Add Or Repair Rebolt Logic

Scenario:

- user needs function, variable, block, or property changes in `.rebolt`

Recommended path:

1. inspect file or tree structure
2. confirm tree name, slot path, and variable/function names
3. use `rebolt-modify`
4. validate after mutation

Must not:

- add notify names that are inconsistent with project standards
- create logic blocks before confirming the required function structure

## Use Case 5: Figma Engineering Document To Redream

Scenario:

- user provides a Figma engineering document and wants a Redream project or scenes

Recommended path:

1. use `workflow-config.md` for intake gating
2. use `figma-to-redream.md` phase by phase
3. create scenes leaf-first
4. configure timelines and rebolt after structure exists
5. validate every phase

Must not:

- invent file names or node names
- skip the project configuration confirmation
- write `.red` / `.rebolt` directly when CLI is available

## Use Case 6: Standardize A Messy Existing Project

Scenario:

- files exist but naming, folders, timelines, or Rebolt conventions drifted

Recommended path:

1. inspect current structure
2. compare against standards
3. fix naming and structure in a controlled sequence
4. revalidate after each batch

Use:

- `project-standards.md`
- `project-patterns.md` (in `guides/`)

## Use Case 7: Prepare Assets For Downstream Code Integration

Scenario:

- code will later bind to Redream/Rebolt assets

Recommended path:

1. make sure node names and notify names are stable
2. make sure `reboltName` is set only where required
3. keep function names and coder vars consistent
4. validate that CLI inspection gives an unambiguous contract

Must not:

- leave notify names implicit or tied to temporary labels
- rely on visual placement instead of explicit node identity
