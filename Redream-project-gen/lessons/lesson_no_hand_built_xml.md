---
name: 禁止手拼 XML 字符串生成 .red
date: 2026-04-20
status: ✅ 已落地（硬规则）
source: Mengmeng plistlib 实战
---

# Lesson: 手拼 XML 字符串会造成"双 dict"崩溃

## 事件

早期尝试用 Python 字符串拼接的方式生成 `.red` 文件（.red 是 Apple plist XML 格式），出现**双 `<dict>` 嵌套错误**，Redream 打开崩溃。

## 根因

- .red 是严格的 XML plist 格式，手工拼接极易出现：
  - 多余的 `<dict>` 包裹
  - `<key>` 与 `<value>` 对不齐
  - `<array>` 内元素类型混乱
- Apple plistlib 模块会自动处理所有这些细节，不会出错

## 规则

**生成 .red 文件一律用 `plistlib.dump()`，不手拼 XML。**

```python
import plistlib

red = {
    'centeredOrigin': True,
    # ... Python dict 结构
}

with open('output.red', 'wb') as f:
    plistlib.dump(red, f)
```

## 禁止做法

```python
# ❌ 禁止
xml = '<?xml version="1.0"?>\n<plist>\n<dict>\n<key>...</key>...'
with open('output.red', 'w') as f:
    f.write(xml)
```

## CLI 下的处理

使用 CLI `modify` 系列命令时，引擎内部用 C++ 代码序列化 .red，不涉及此问题。

## 关联

- `references/figma-to-red-plistlib.md`
- `references/redream.md` — .red 文件格式定义
