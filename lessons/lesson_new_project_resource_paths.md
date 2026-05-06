---
name: new-project 默认只加 ccb，必须手动加 Resources
date: 2026-04-24
status: ✅ 已落地
source: RED Tool CLI 迁移
---

# Lesson: new-project 默认资源路径只有 ccb

## 事件

用 `Redream modify new-project` 创建项目，把 .red 文件放在 `Resources/` 目录下。Redream 打开项目时**看不到**这些场景。

## 根因

`new-project` 默认生成的 `.redproj` 只配置 `resourcePaths: ["ccb"]`，不包含 `Resources`。

## 规则

创建项目后**立即**调用：

```bash
Redream modify --project xxx.redproj --add-resource-path Resources project
```

把 `Resources` 目录加入资源扫描路径。

## 推荐的两步工作流

```bash
# 1. 创建项目
Redream modify new-project --project xxx.redproj --resolution 1080x2400

# 2. 加 Resources 资源路径
Redream modify --project xxx.redproj --add-resource-path Resources project
```

## 教训

CLI 的默认值不一定符合实际使用场景，**要主动测试打开效果**，不要假设默认值合理。

## 关联

- `references/cli-modify.md` — `new-project` / `add-resource-path` 完整格式
- `references/figma-to-red-cli-driven.md` — RED Tool v15 已内置这一步
