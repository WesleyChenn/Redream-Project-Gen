# Lesson: 结构图 conn.fromNode 必须 0-indexed 且写完必须目视校验

**日期:** 2026-04-14
**状态:** ✅ 已修复（phase2 文档已改正；generator 已对齐）

## 事件

六格烧烤结构图渲染后，用户反馈：
1. 完成反馈特效（feedback_effect）卡片没有任何入线
2. container→element 的 6 条连线中，槽位_0 对应的那条"看不到"

## 根因（一个共同 bug）

HTML 模板 renderer 生成节点端口 ID 的方式（`templates/*_structure.html:1483`）：
```js
d.nodes.forEach((nd, ni) => {
  h += `... <div class="nd-port" id="pa-${d.id}-${ni}"></div>`;
});
```
`ni` 是 `forEach` 的 0-indexed 下标。drawConns 查这个 id：
```js
document.getElementById(`pa-${c.fromCard}-${c.fromNode}`)
```

**但 `phases/phase2-structure-diagram.md` 旧文档写**：
> fromNode 是 1-indexed 节点序号

两者相差 1。按旧文档写 `fromNode: 4` 意图指向 main 的第 4 个节点（特效层），renderer 会去找 `pa-main-4` —— main 只有 4 个节点 (ni=0..3)，查不到 element → `getElementById` 返回 `null` → drawConns 的 `if(!oEl||!iEl) return;` 静默跳过 → 整条线**既不画也不报错**。

六格烧烤里两处全被这个 bug 命中：
- `main.fromNode=4 → feedback_effect`：pa-main-4 不存在 → 线消失
- `container.fromNode=7 → element`：pa-container-7 不存在 → 6 条少 1；同时 fromNode=2~6 全部偏移一位，视觉上"槽位_0"无外出连线

## 规则

### 规则 A（硬性）：fromNode 严格 0-indexed

`conn.fromNode` 必须 ∈ `[0, len(cards[parent].nodes) - 1]`，与 HTML `forEach((_, ni)=>{})` 的 ni 一致。

### 规则 B（硬性）：写完必须目视 + 脚本双重校验

静默失败是这个 bug 的恶性特征，自检断言如果没有和 renderer 的 getElementById 口径对齐，也会漏报。必须：

1. **脚本校验**（phase2 Step 8 已更新）：
   ```python
   assert 0 <= conn['fromNode'] < len(fc['nodes'])
   ```
2. **目视校验**：浏览器打开 HTML，每张卡片数一下输入/输出连线数，对照 JSON 的 `conns` 列表长度，**缺一条都不行**。
3. **Console 校验**（更严谨）：在浏览器 DevTools Console 跑：
   ```js
   S.conns.forEach(c => {
     const ok = document.getElementById(`pa-${c.fromCard}-${c.fromNode}`);
     if (!ok) console.error('broken conn:', c);
   });
   ```

**Why**：`drawConns` 对找不到 port 的 conn 静默 `return`，不抛错不报警，只能靠目视/主动查询发现。修文档（phase2）的 assert 是第一道防线，但模板 renderer 的行为才是最终事实。

## How to apply

- 新建结构图前 read 一遍 `phases/phase2-structure-diagram.md` 的 Step 3（已更新为 0-indexed）
- 写 conns 前列一张映射表（`main.nodes[0]=..., [1]=...`），对着填 fromNode
- 生成 HTML 后，**必须**运行 Step 8 自检 + 浏览器目视双重校验
- 模板/renderer 与文档出现不一致时，**以 renderer 为准**，反向更正文档

## 关联

- `phases/phase2-structure-diagram.md` 第 72 行已改为 0-indexed，Step 8 断言已改为 `0 <= ... < len`
- `templates/BeadsOut_structure.html` / `FruitTruck_structure.html` 的 conns 本身就是 0-indexed（事实上的权威来源），与 renderer 一致
