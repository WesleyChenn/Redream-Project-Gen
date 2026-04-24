---
name: CLI 帮助文档不等于真实支持（--json 陷阱）
date: 2026-04-24
status: ✅ 已落地
source: RED Tool CLI 迁移（Redream CLI 1.3.4）
---

# Lesson: CLI 帮助文档和真实支持可能不一致

## 事件

Redream CLI 1.3.4 的 `--help` 列出了 `--json` 选项，但实际用的时候报 `Unknown option 'json'`。

## 根因

帮助文档里写的选项不一定都实现了 / 还没实现 / 被移除但忘了删帮助。

## 规则

1. 帮助文档只是**参考**，实测为准
2. 去掉 `--json` 用文本输出也能解析
3. 遇到"帮助里有但报错"的选项，先怀疑是不是没真的支持

## 排查方法

- 先用最简单的命令形式跑一遍（不带任何可选参数）
- 报错后逐个加参数，定位到哪个参数不支持
- 查 `actions` 或 `actions --json` 输出（如果有的话），和 `--help` 对比

## 关联

- `references/test-results-rebolt-commands.md` — 实测过的 CLI 验证清单
- `references/cli-inspect.md` / `references/cli-modify.md`
