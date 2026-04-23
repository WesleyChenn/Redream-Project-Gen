---
name: redream-cli-reference
description: >
  DEPRECATED — 已拆分为三份权威文档，不要再从本文件查 CLI 命令。
---

# ⚠️ 已废弃（2026-04-21）

本文件原为 CLI 速查，已按官方 `ai_dev_skill` 审计结果拆分为三份权威来源：

| 目的 | 文件 |
|------|------|
| 只读查询命令 | [references/cli-inspect.md](cli-inspect.md) |
| 写入/修改命令 | [references/cli-modify.md](cli-modify.md) |
| 当前 CLI 表面审计（当记忆与旧文档冲突时的仲裁源） | [references/test-results-rebolt-commands.md](test-results-rebolt-commands.md) |

## CLI Binary

Primary（测试版/官方 alpha 构建，装完 `Redream-9.6.0.0-alpha.dmg` 后路径）：

```
/Applications/Redream.app/Contents/MacOS/Redream
```

Source build（仅源码开发者）：

```
build/bin/Redream/Redream.app/Contents/MacOS/Redream
```

遇到命令表面与旧记忆不一致时，按以下优先级解析：

1. `Redream ... actions --json`
2. `Redream ... --help`
3. `test-results-rebolt-commands.md`
4. 历史文档
