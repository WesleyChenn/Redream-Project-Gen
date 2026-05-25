# Lesson · 视觉缩窄识别 = AutoLayout 决策 (一体化, 不该分开做)

**适用阶段**: S3 (识别布局) ↔ S7 (生成骨架)
**配套**: SKILL.md 铁律 15 / 03_S3 §"layoutMode 合约 → S7" / 07e §"复用类 component 内部布局"
**新增**: 2026-05-21

---

## 一句话总结

S3 的"视觉缩窄识别 layoutMode" 跟 S7 的"写 AL 字段" 是**同一件事的两个表达**: 缩窄识别到的"单向排列结构"= AL 的天然对象。**禁止在 S7 阶段重新独立判断**, 让 S3 的判定直接传导到 S7 写字段。

---

## 核心概念

### 视觉缩窄识别 (S3 / 06a)
S3 递归缩窄找重复结构, 每个组团判 layoutMode:
- 子节点 **Y 中心对齐 + X 各异** → HORIZONTAL
- 子节点 **X 中心对齐 + Y 各异** → VERTICAL
- 叠加 / 无明确排列关系 → NONE

### AutoLayout 决策 (S7)
S7 按 layoutMode 写字段:
- HORIZONTAL → 横排, AL 接管 x 位置
- VERTICAL → 竖排, AL 接管 y 位置
- NONE → 子节点绝对定位 (x/y 手算)

### 两者是同一件事
**视觉上单向排列** ⟺ **AL 接管位置的最佳场景**:
- HORIZONTAL 的"横排"就是 HORIZONTAL AL 要做的
- VERTICAL 的"竖排"就是 VERTICAL AL 要做的
- 没必要在 S7 阶段重新判断 "要不要用 AL", S3 已经判完了

---

## 失败模式 (S3 识别对, 但 S7 退化)

### 实证 1: TT 列表项 收集物数量出底板 20px

```
源视频: 列表项是横排 (排名 / 头像 / 名字 / 道具 / 收集物数量 横向排列)
S3 标: layoutMode = HORIZONTAL ✓
S7 退化: 列表项 component 用了 NONE + 手算 x/y
        子元素 收集物数量 x=855 + w=215 = 1070 > 底板 1050
       → 出底板 20px ❌
```

### 实证 2: JO 列表项 角标出 75px

```
源视频: 列表项横排 (底板 / 内容 / 金币堆 / 角标)
S3 标: layoutMode = HORIZONTAL ✓
S7 退化: 列表项 component 用了 NONE + 手算 x/y
        子元素 角标 x=905 + w=60 = 965 > 列表项 890
       → 出 75px ❌
```

### 通用模式

```
S3 判 [HORIZONTAL/VERTICAL] → ✓ 视觉缩窄正确
                ↓
       S7 写 component 时
                ↓
   ❌ "我自己再判一次, 用 NONE + 手算 x/y 吧"
                ↓
       手算坐标必然算超界 / 不对齐
```

---

## 正确做法 (一体化决策)

### S3 的输出 = S7 的合约

```
S3 表 B (AL 容器对齐意图) 已确定:
  容器名         | layoutMode  | 对齐意图          | itemSpacing | paddings | 弹性缝隙
  列表项          | HORIZONTAL  | MIN + 右靠      | 15          | 20/20     | 1 处
  组_名字         | VERTICAL    | CENTER          | 6           | -         | 无

S7 写时:
  列表项 component {
    layoutMode: "HORIZONTAL",       ← 来自 S3
    primaryAxisSizingMode: "FIXED",
    counterAxisSizingMode: "FIXED",
    primaryAxisAlignItems: "MIN",   ← 来自表 B
    counterAxisAlignItems: "CENTER",
    itemSpacing: 15,                ← 来自表 B
    paddingLeft: 20,                ← 来自表 B
    paddingRight: 20,
    children: [
      INSTANCE 排名,
      INSTANCE 头像,
      FRAME 组_名字,                 ← 内部用 VERTICAL AL, 同样来自 S3
      INSTANCE 弹性缝隙,
      INSTANCE 道具,
      INSTANCE 收集物数量
    ]
  }
```

**关键**: S7 不需要再判断"列表项内部要不要用 AL", S3 已经判好了 HORIZONTAL, 照写。

---

## 跨层级一致 (适用所有层级)

S3 的判定不区分层级, S7 也不该区分:

| 层级 | 例子 | S3 判 layoutMode | S7 写法 |
|---|---|---|---|
| 屏幕级外侧大组团 | 顶部 HUD | HORIZONTAL | HORIZONTAL AL |
| 屏幕级外侧大组团 | 容器_排行榜滚动区 | VERTICAL | VERTICAL AL |
| Component 内部 | 列表项 | HORIZONTAL | HORIZONTAL AL |
| Component 内部 | 进度面板 | NONE (节点叠加在进度条上) | NONE + 绝对坐标 (合理) |
| Component 嵌套子组 | 组_名字 (名字+副标) | VERTICAL | VERTICAL AL |
| Component 嵌套子组 | 组_名字行 (装饰+名字) | HORIZONTAL | HORIZONTAL AL |

→ **同一套规则贯穿**, S7 只是 S3 的"忠实执行者"。

---

## 防退步 (S7 阶段的自检)

S7 写每个 FRAME / component 时, 主动问自己:
1. "S3 给这个组团判的 layoutMode 是啥?"
2. "我写的 layoutMode 字段跟 S3 判定**是否一致**?"
3. 如果 S3 判 HORIZONTAL/VERTICAL → **必须写完整 AL 字段**, 不能写 NONE
4. 如果 S7 我觉得 "用 NONE + 手算 x/y 更简单" → **错觉**, 必出框, 立刻改回 AL

---

## 反例与例外

### 合理的 NONE (不需要 AL)
- 进度面板: 进度条 + 节点 (节点叠加在进度条上, 不是横排关系)
- 浮层: 装饰图 + 标题 + 按钮 (各自绝对定位)
- Component 的底板 RECT: ABSOLUTE 脱离布局流 (但本身不是组团)

→ S3 这些场景判 NONE, S7 也写 NONE, 一致。

### 错误的 NONE (该 AL 但退化)
- 列表项 横排 5 子单元 → S3 判 HORIZONTAL → S7 退化成 NONE = **错** ❌
- 组_名字 竖排 2 行 (玩家名 / 副标) → S3 判 VERTICAL → S7 退化成 NONE = **错** ❌

---

## 总结

| 维度 | 拆分决策 (老) | 一体化决策 (新) |
|---|---|---|
| S3 角色 | 给出 layout 建议 | 给出 layout **合约** |
| S7 角色 | 重新判一次, 决定 NONE/AL | **执行 S3 合约**, 写完整 AL 字段 |
| 退化风险 | 高 (Claude 在 S7 倾向偷懒用 NONE) | 低 (S7 没有重新判的机会) |
| 实证 bug | TT 出 20px / JO 出 75px | 修了 |
| 认知负担 | S3 + S7 各判一次 | S3 判一次, S7 执行 |
| 跨层级一致 | 不保证 | 保证 |

**记住**: 视觉缩窄识别的"单向排列结构" = AutoLayout 的天然对象。**这两件事一体化决策。**
