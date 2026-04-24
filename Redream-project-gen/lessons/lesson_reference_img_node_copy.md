---
name: referenceImgNode 必须从已知可用参考文件复制
date: 2026-04-20
status: ✅ 已落地
source: Mengmeng plistlib 实战
---

# Lesson: referenceImgNode 不能手工构造

## 事件

尝试手工构造 `.red` 顶层的 `referenceImgNode` 字段，Redream 打开时报错或显示异常。

## 根因

`referenceImgNode` 字段结构复杂（包含多层 dict + 平台特定字段），手工构造极易漏字段或格式错误。

## 规则（plistlib 流程）

**从已验证可用的 .red 文件里直接复制 `referenceImgNode` 字段：**

```python
import plistlib

REF_PATH = '~/Desktop/red_output/界面_主菜单/Resources/界面_主菜单.red'

with open(REF_PATH, 'rb') as f:
    ref = plistlib.load(f)

red = {
    # ... 其他字段
    'referenceImgNode': ref['referenceImgNode'],   # ← 直接复制
}
```

## 参考文件

| 文件 | 用途 |
|------|------|
| `~/Desktop/red_output/界面_主菜单/Resources/界面_主菜单.red` | referenceImgNode 参考来源（首个成功生成的文件） |

## CLI 下的处理

使用 CLI `modify new-scene` 时，引擎自动写入合法 `referenceImgNode`，不用手动管。

## 关联

- `references/figma-to-red-plistlib.md`
