# 工程创建工作流配置

## 询问分类

创建工程过程中可能出现的询问，按阶段分类：

### Phase 0：项目配置

| ID | 询问类型 | 说明 | 默认值 |
|---|---|---|---|
| `P0_RESOLUTION` | 设计分辨率 | 如 750x1334、1334x750 | 无（必须确认） |
| `P0_PROJECT_DIR` | 项目目录路径 | 工程存放位置 | 无（必须确认） |
| `P0_PROJECT_NAME` | 项目名 / .redproj 文件名 | 项目文件命名 | 从目录名推断 |
| `P0_RESOURCE_DIR` | 资源目录名 | .red 文件存放子目录 | `ccb/` |

### Phase 1：Figma 解析

| ID | 询问类型 | 说明 | 默认值 |
|---|---|---|---|
| `P1_PARSE_RESULT` | Figma 解析结果确认 | 解析出的文件列表、类型 | 自动解析不询问 |
| `P1_FILENAME` | 文件名推断确认 | 从卡片标题推断文件名 | 卡片标题文字为准，自动推断不询问 |

### Phase 2：计划确认

| ID | 询问类型 | 说明 | 默认值 |
|---|---|---|---|
| `P2_PLAN_CONFIRM` | 创建计划确认 | 展示文件列表和配置，等待确认 | 无（必须确认） |

### Phase 3：场景创建

| ID | 询问类型 | 说明 | 默认值 |
|---|---|---|---|
| `P3_ROOT_TYPE` | 根节点类型确认 | CCNode 还是 CCLayer | 按文件名关键词自动判断（弹窗/浮层/全屏反馈/界面→CCLayer，其他→CCNode） |
| `P3_RESOLUTION_FIX` | 场景分辨率修复确认 | new-scene 后修复分辨率 | 自动执行 |

### Phase 4：节点层级

| ID | 询问类型 | 说明 | 默认值 |
|---|---|---|---|
| `P4_NODE_HIERARCHY` | 节点层级结构确认 | 子节点置入、程序创建节点 | 按 Figma 卡片内容自动创建不询问 |
| `P4_REDFILE_LINK` | REDFile 链接确认 | 子场景文件关联 | 自动设置不询问 |

### Phase 5：时间线

| ID | 询问类型 | 说明 | 默认值 |
|---|---|---|---|
| `P5_TIMELINE_CONFIG` | 时间线配置确认 | 时间线名称、循环、音频 | 按 Figma 卡片内容自动配置不询问 |
| `P5_DEFAULT_TIMELINE_DELETE` | 默认时间线策略确认 | 新建场景时使用 `--no-default-timeline`；只有旧场景才删除 Default Timeline | 自动跳过创建，不询问 |
| `P5_SEQUENCE_ID_FIX` | currentSequenceId 修复确认 | 仅在旧场景删除 Default Timeline 后修复 ID | 仅按需自动修复，不询问 |

### Phase 6：Rebolt 逻辑

| ID | 询问类型 | 说明 | 默认值 |
|---|---|---|---|
| `P6_FUNC_TIMELINE_MAP` | 函数→时间线映射确认 | 推断的函数与时间线对应关系 | 自动推断不询问 |
| `P6_FUNC_LIST` | 自定义函数列表确认 | rebolt 函数配置 | 按 Figma 卡片内容自动添加不询问 |
| `P6_VAR_LIST` | 程序变量列表确认 | rebolt 变量配置 | 按 Figma 卡片内容自动添加不询问 |
| `P6_NOTIFICATION_LIST` | 通知工程师列表确认 | 节点绑定和事件通知 | 按 Figma 卡片内容自动添加不询问 |
| `P6_REBOLT_PUBLIC` | isPublic 设置确认 | 含子场景的 red 设为 public | 自动设置不询问 |

### Phase 7：验证

| ID | 询问类型 | 说明 | 默认值 |
|---|---|---|---|
| `P7_INSPECT_CHECK` | 验证结果确认 | inspect check 结果展示 | 自动验证，只在失败时报告 |

### 环境问题

| ID | 询问类型 | 说明 | 默认值 |
|---|---|---|---|
| `ENV_CLI_UNAVAILABLE` | CLI 不可用处理 | CLI 报错时选择回退方案还是等用户修复 | 回退到源文件创建 |
| `ENV_QUARANTINE` | macOS 隔离属性移除 | xattr -cr 移除隔离 | 自动执行 |
| `ENV_PERMISSION` | 文件权限问题 | chmod 修复权限 | 自动执行 |

---

## 白名单

白名单中的询问类型将自动使用默认值执行，不中断流程。

**当前白名单（全部非必须确认项）：**

- `P0_RESOURCE_DIR` — 默认使用 `ccb/`
- `P0_PROJECT_NAME` — 从项目目录名推断
- `P1_PARSE_RESULT` — 自动解析 Figma 内容不询问
- `P1_FILENAME` — 卡片标题文字为准，自动推断文件名
- `P3_ROOT_TYPE` — 按文件名关键词自动判断（弹窗/浮层/全屏反馈/界面→CCLayer，其他→CCNode）
- `P3_RESOLUTION_FIX` — new-scene 后自动用 python 修复分辨率
- `P4_NODE_HIERARCHY` — 按 Figma 卡片内容自动创建节点
- `P4_REDFILE_LINK` — 自动设置 REDFile 链接
- `P5_TIMELINE_CONFIG` — 按 Figma 卡片内容自动配置时间线
- `P5_DEFAULT_TIMELINE_DELETE` — 新场景自动使用 `--no-default-timeline`，旧场景才删除 Default Timeline
- `P5_SEQUENCE_ID_FIX` — 仅在旧场景删除 Default Timeline 后自动修复 currentSequenceId
- `P6_FUNC_TIMELINE_MAP` — 自动推断函数→时间线映射
- `P6_FUNC_LIST` — 按 Figma 卡片内容自动添加函数
- `P6_VAR_LIST` — 按 Figma 卡片内容自动添加变量
- `P6_NOTIFICATION_LIST` — 按 Figma 卡片内容自动添加通知
- `P6_REBOLT_PUBLIC` — 含子场景时自动设置 isPublic
- `P7_INSPECT_CHECK` — 自动验证，只在失败时报告
- `ENV_QUARANTINE` — 自动执行 `xattr -cr`
- `ENV_PERMISSION` — 自动修复权限
- `ENV_CLI_UNAVAILABLE` — 自动回退到源文件创建

**始终需要确认（不可加入白名单）：**

- `P0_RESOLUTION` — 分辨率直接影响工程配置，必须明确
- `P0_PROJECT_DIR` — 路径错误不可逆，必须确认
- `P2_PLAN_CONFIRM` — 创建计划需要用户审核

---

## 使用规则

1. 执行工程创建时，先检查本文件的白名单
2. 白名单中的项直接使用默认值，不调用 AskUserQuestion
3. 不在白名单中的项正常询问
4. 用户可随时要求将某个询问类型加入或移出白名单
5. **核心原则：整个创建流程最多只中断 3 次**（分辨率、项目目录、创建计划），其他全部自动执行
