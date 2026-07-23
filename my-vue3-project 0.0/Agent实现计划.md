# 鲤工助手 · Agent 实现计划

> **本文档仅为方案与计划，当前不要求改业务代码。**  
> 范围：**只做两件事**——① 对话驱动跳转（查分/选课/课表等）；② 基于本地课表回答「今天有什么课」等。  
> **不做 GUI 自动化**（AutoGLM、模拟点击教务等一律排除）。  
> 依据：桌面稿《一、整体架构思路.md》+ 仓库现状（`pages/agent`、`00.my-agent`、课表/WebVPN）。

---

## 0. 结论（先读这段）

后端已是 LangGraph ReAct（`create_react_agent`），升级不靠换框架，靠三件事：

1. **结构化动作协议** `actions[]`（机器指令与用户可见文案分离）  
2. **手机端执行器**（`switchTab` / `openCampusWeb`）  
3. **本地课表进对话上下文**（数据在 `uni.storage`，不造教务爬虫）

| 要做 | 不做 |
| --- | --- |
| 阶段一：能跳转的 Agent | GUI / 模拟点击 / ADB 操控 |
| 阶段二：能查今日课的 Agent | 独立查分页、教务成绩开放 API、系统 URL Scheme（非必须） |

---

## 1. 现状与纠偏

### 1.1 已有能力

| 能力 | 位置 |
| --- | --- |
| 真机对话 | `agent.vue` → `POST /chat`（`message` + `thread_id`） |
| ReAct + 知识库 | `00.my-agent`：MiniMax + `search_knowledge_base` |
| 本地课表 | `local_course_data`、`semester_start`、`time_mode` |
| 校园深链 | 首页已有查分/选课等 URL + `openCampusWeb` |
| 课表页 | Tab：`pages/timetable`（须 `switchTab`） |

### 1.2 缺口

- 工具只有知识库 → 不会「办事」  
- 响应只有 `{ answer }` → 前端无法可靠执行跳转  
- 请求无设备上下文 → 后端不知道课表  
- 系统提示偏「知识库唯一」 → 抑制动作工具  

### 1.3 相对桌面稿的纠偏

| 桌面稿 | 本项目正确做法 |
| --- | --- |
| `/pages/grade` 等 DeepLink 页 | 查分等走 **WebVPN 深链** + `open_campus_web` |
| 后端调教务 API 查课表 | 用手机 **`local_course_data`**（请求内附带摘要） |
| GUI 自动化 | **明确不做** |

---

## 2. 目标架构（仅两阶段）

```
手机 agent.vue
  │  请求：message + thread_id + device_context（阶段二起带课表摘要）
  ▼
00.my-agent（LangGraph）
  │  工具：知识库 + 打开校园服务 / 跳转课表
  ▼
响应：{ thread_id, answer, actions[] }
  ▼
手机执行 actions（switchTab / openCampusWeb）并展示 answer
```

**原则：** 后端决策，前端执行；课表数据默认不出手机（只传摘要给模型用）。

---

## 3. 统一协议（两阶段共用）

### 3.1 响应

```json
{
  "thread_id": "app-xxx",
  "answer": "好的，正在打开查分～",
  "actions": [
    {
      "type": "open_campus_web",
      "title": "查分",
      "url": "https://….webvpn.scut.edu.cn/…"
    }
  ]
}
```

| type | 用途 |
| --- | --- |
| `switch_tab` | 打开课表等 Tab（`path`） |
| `navigate_to` | 非 Tab 普通页（如导入页，按需） |
| `open_campus_web` | 查分/选课/教务等，复用 `openCampusWeb` |
| `open_webview` | 普通外链（按需） |

- 用户文案 → `answer`  
- 机器指令 → `actions`  
- **禁止**把 `NAVIGATE:` 当作唯一正式协议（最多作临时兼容）

### 3.2 请求（阶段二启用课表字段）

```json
{
  "message": "今天有什么课？",
  "thread_id": "app-xxx",
  "device_context": {
    "has_timetable": true,
    "semester_start": "2026-02-23",
    "time_mode": "university",
    "today": "2026-07-20",
    "weekday": 1,
    "today_courses": [
      { "name": "高等数学", "section": "1-2", "room": "B2-101" }
    ]
  }
}
```

无课表时：`has_timetable: false`，`today_courses: []`。

### 3.3 服务目录（Service Catalog）

与首页功能入口对齐的一份表（建议 `service_catalog`：key → title/url/route）：

| key 示例 | 行为 |
| --- | --- |
| `grade` | `open_campus_web` 查分 URL |
| `course_select` | 自主选课 URL |
| `jw_home` | 教务系统 |
| `gpa` | GPA 页 |
| `webvpn` | WebVPN 门户 |
| `timetable` | `switch_tab` → `/pages/timetable/timetable` |

动作 **只允许目录内目标**，防止乱跳。

---

## 4. 阶段一：能跳转的 Agent

### 4.1 目标效果

| 用户说 | 期望 |
| --- | --- |
| 我要查分 | 走 WebVPN 打开查分 |
| 打开课表 / 我的课表 | `switchTab` 到课表 |
| 自主选课 | 打开选课深链 |
| 华工某政策是什么 | 仍走知识库文字答，不乱跳 |

### 4.2 后端要做

1. 新增动作类工具（如 `open_campus_service(service_key)`）  
2. 落地 Service Catalog，与首页链接一致  
3. 改 system prompt：明确「打开/跳转/去查」必须调动作工具；禁止假装已打开  
4. `app.py`：响应增加 `actions[]`（从 tool 结果规范化）  
5. 知识库工具保留，负责百科/说明类问题  

### 4.3 前端要做

1. 新增 `agentActions.js`：执行 `actions[]`  
2. `agent.vue`：收到响应后先/后展示 `answer`，再执行动作  
3. Tab 只用 `switchTab`  

### 4.4 验收

- [ ] 查分 / 选课 / 教务 / 课表 四类说法各测通  
- [ ] 纯知识问答不误触发跳转  
- [ ] 非法 key 不执行并友好说明  

### 4.5 本阶段不做

- 不读课表、不传 `device_context` 课表字段（可先留空结构）  
- 不做 GUI、不做成绩爬取  

---

## 5. 阶段二：能查今日课的 Agent

### 5.1 目标效果

| 用户说 | 期望 |
| --- | --- |
| 今天有什么课（已导入） | 根据本地课表列出节次/课程/教室 |
| 今天有什么课（未导入） | 说明未导入，并可 `switch_tab` 去课表 |
| 下一节在哪 / 明天上午有没有课 | 基于同一套本地数据与周次计算 |

### 5.2 推荐做法：上下文注入（简单稳妥）

1. App 发消息前读取 storage，用与课表页**同一套**周次/节次逻辑算「今日摘要」  
2. 写入 `device_context.today_courses` 等字段  
3. 后端依据上下文直接回答；无课表则引导导入并附带跳转课表的 `actions`  
4. **不**新建教务 API，**不**把完整课表默认同步云端  

> 说明：更「正统」的客户端工具环（Agent 下令 → App 查表 → 再回传）可作后续增强，**本计划阶段二不强制**，以免拖慢交付。

### 5.3 后端要做

1. `ChatRequest` 接收 `device_context`  
2. Prompt：有课表摘要则据此答；无则引导导入 + 可发 `switch_tab`  
3. 回答今日课时优先用上下文，避免瞎编课程  

### 5.4 前端要做

1. `agentContext.js`：组装 `device_context`  
2. 复用/抽取 `timetableParse` 相关纯函数，与课表页逻辑一致  
3. `agent.vue` 每次请求带上上下文  

### 5.5 验收

- [ ] 已导入：今日课问答正确（对照课表页）  
- [ ] 未导入：提示清晰且能跳到课表  
- [ ] 开学日未设：不硬算瞎答，提示去课表设置  

### 5.6 本阶段不做

- GUI、教务爬虫、云端存课表、成绩查询 API  

---

## 6. 计划改动清单（实施时用，现在不动手）

### 后端 `00.my-agent`

| 项 | 阶段 |
| --- | --- |
| `tools/app_actions.py` + Catalog | 一 |
| `agent.py` 注册工具 + 改 prompt | 一 |
| `app.py` 返回 `actions` | 一 |
| 接收并使用 `device_context` | 二 |

### 前端

| 项 | 阶段 |
| --- | --- |
| `utils/agentActions.js` + `agent.vue` 执行动作 | 一 |
| `utils/serviceCatalog.js`（与后端对齐） | 一 |
| `utils/agentContext.js` + 请求带课表摘要 | 二 |

### 文档（做完功能后再改）

- `项目架构说明.md`、`00.my-agent/00.项目结构与功能分析.md` 同步协议与工具  

---

## 7. 风险（针对这两阶段）

| 风险 | 对策 |
| --- | --- |
| 该跳不跳 / 乱跳 | Prompt + Catalog 白名单 |
| 协议写进用户可见正文 | 正式只用 `actions` |
| 今日课与课表页不一致 | 共用同一套解析与开学日 |
| 知识库规则过严拒答办事 | Prompt 分流：办事走动作/上下文，百科走知识库 |

---

## 8. 实施顺序（仅计划勾选）

**阶段一**（已落地代码，需真机联调验收）

1. [x] 定稿 Action Schema + Service Catalog（对齐首页链接）
2. [x] 后端动作工具 + prompt + `/chat` 返回 `actions`
3. [x] 前端执行器接入 `agent.vue`
4. [ ] 阶段一验收用例通过（真机：查分 / 选课 / 教务 / 课表 + 纯知识不误跳）

**阶段二**（已落地代码，需真机联调验收）

5. [x] 前端组装 `device_context`（今日课摘要 + 签到）
6. [x] 后端消费上下文并改 prompt
7. [ ] 阶段二验收用例通过
8. [ ] 更新架构说明文档

---

## 9. 范围声明（避免返工）

本计划 **包含**：阶段一跳转 + 阶段二本地课表问答。  

本计划 **不包含**：GUI 自动化、系统级手机操控、教务自动登录填表、成绩开放 API、为 Agent 重做课表 UI、默认同步课表到云端。

---

*若日后只加「产品化」（确认弹窗、SSE、日志），另开小节即可，不纳入当前必做范围。*







# 最初的计划建议

