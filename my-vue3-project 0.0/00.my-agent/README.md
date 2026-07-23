# 华工校园智能体后端（SCUT Campus Agent）

面向「鲤工助手」App 的**本地** Agent 服务：知识库问答 + 对话驱动跳转 + 本地课表/签到上下文。

> **本项目不提供公共在线服务器。**  
> 调用大模型需要你自己的 API Key，费用由你自己承担。有兴趣体验的同学请按本文在自己电脑上配置并启动。

---

## 功能概览

- 校园知识库检索（Chroma + 本地 BGE 向量模型）
- LangGraph ReAct Agent（MiniMax 等 OpenAI 兼容接口）
- 返回 `actions[]`，配合鲤工助手 App 打开课表 / 查分 / WebVPN 等
- 可选本地网页对话看板（`frontend/`）

---

## 环境要求

| 项 | 说明 |
| --- | --- |
| 系统 | Windows 10/11（脚本为 `.bat`；其他系统可手动等价命令） |
| Python | 建议 3.10+ |
| 大模型 Key | MiniMax 或其他 OpenAI 兼容接口密钥（自行申请） |
| 向量模型 | `BAAI/bge-large-zh-v1.5`（需本机已有 HuggingFace 缓存，或先联网下载一次） |
| 真机联调 | Android 手机 + USB 数据线 + `adb`（Android SDK platform-tools） |

---

## 1. 获取代码

```bash
git clone https://github.com/tuoxingwanli/SCUT-Helper-Agent.git
cd SCUT-Helper-Agent
```

（若仓库地址不同，以你 clone 时的 URL 为准。）

---

## 2. 配置 API Key（必做）

1. 复制示例环境文件：

```bat
copy .env.example .env
```

2. 用记事本打开 `.env`，填写你自己的密钥，例如：

```env
OPENAI_API_KEY=sk-你的真实密钥
OPENAI_BASE_URL=https://api.minimax.chat/v1
```

3. **不要**把 `.env` 发给别人，也不要提交到 Git（仓库已用 `.gitignore` 忽略）。

密钥可在 [MiniMax 开放平台](https://platform.minimaxi.com/) 自行申请；也可用其他兼容 OpenAI Chat Completions 的接口（需改 `OPENAI_BASE_URL`，并视情况改 `agent.py` 里的模型名）。

---

## 3. 安装依赖

在仓库根目录：

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

国内网络如遇 HuggingFace / pip 较慢，可自行配置镜像。

---

## 4. 构建知识库向量库（首次必做）

知识文档在 `data/documents/*.txt`。首次或文档有改动后：

```bat
venv\Scripts\activate
python build_vectordb.py
```

会生成目录 `vectordb/`（已在 `.gitignore`，不上传仓库）。

> 脚本默认 `local_files_only=True` 且 `HF_HUB_OFFLINE=1`。  
> 若本机还没有 `BAAI/bge-large-zh-v1.5` 缓存：先临时去掉离线限制、联网下载一次模型，再改回离线构建。

---

## 5. 启动后端

### 方式 A：一键脚本（推荐）

双击 `一键启动脚本.bat`。

会启动：

| 服务 | 地址 |
| --- | --- |
| Agent API | `http://127.0.0.1:8000`（脚本里 `--host 0.0.0.0`，局域网也可访问） |
| 网页前端 | `http://127.0.0.1:8080/frontend/index.html` |

接口文档：浏览器打开 `http://127.0.0.1:8000/docs`。

### 方式 B：手动

```bat
venv\Scripts\activate
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

关闭对应 CMD 窗口即可停止服务。

---

## 6. 与鲤工助手 App 真机联调

App 默认请求：`http://127.0.0.1:8000`。  
手机上的 `127.0.0.1` 是手机自己，所以必须用 **USB 调试 + adb reverse**，把手机的 8000 端口转到电脑后端。

### 6.1 手机打开开发者模式

1. 打开 **设置 → 关于手机**
2. 连续点击 **版本号** 约 7 次，直到提示已进入开发者模式
3. 返回设置，进入 **系统 → 开发者选项**（不同品牌路径略有差异）
4. 打开 **USB 调试**
5. （可选）打开 **USB 安装** / **通过 USB 验证应用** 等，按品牌需要开启

### 6.2 USB 连接电脑

1. 用数据线连接手机与电脑（仅「充电」有时不够，选 **文件传输 / MTP**）
2. 手机弹出「是否允许 USB 调试」→ 勾选始终允许 → **确定**
3. 电脑需已安装 `adb`（Android Studio / SDK platform-tools，并把目录加入 PATH）

验证：

```bat
adb devices
```

列表中应出现设备，状态为 `device`（若是 `unauthorized`，请在手机上点允许）。

### 6.3 设置端口转发（关键）

电脑后端已在 `:8000` 运行时，任选其一：

- 双击 `真机联调-adb-reverse.bat`
- 或手动执行：

```bat
adb reverse tcp:8000 tcp:8000
adb reverse --list
```

拔线重插后转发常会丢失，可再跑一次脚本，或运行 `真机联调-保持adb-reverse.bat` 自动维持。

### 6.4 在 App 里验证

1. 用 HBuilderX / 自定义基座等把「鲤工助手」跑到手机上  
2. 打开 **智能体** Tab，发一句「你好」  
3. 若仍失败：确认后端窗口无报错、`adb reverse --list` 含 `tcp:8000`、手机 USB 调试仍授权

> 仅开启「传输文件」而不开 **USB 调试**，`adb reverse` 无效，App 会连不上后端。

### 备选：局域网 IP（无需 reverse）

若手机与电脑同一 Wi‑Fi，可把 App 里 Agent 地址改为电脑局域网 IP（如 `http://192.168.x.x:8000`），且后端已 `--host 0.0.0.0`。默认发行版仍以 `127.0.0.1` + adb reverse 为准。

---

## 7. 主要 API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/chat` | Body: `{ "message", "thread_id?", "device_context?" }` → `{ thread_id, answer, actions }` |
| `POST` | `/chat/reset` | 清理指定 `thread_id` 的会话记忆 |
| `GET` | `/chat/stream` | SSE 流式（网页/App 当前以同步 `/chat` 为主） |

---

## 8. 目录说明

```
├── app.py                 # FastAPI 入口
├── agent.py               # LangGraph Agent / 系统提示
├── device_context.py      # 课表/签到上下文格式化
├── build_vectordb.py      # 构建向量库
├── tools/
│   ├── knowledge.py       # 知识库检索
│   └── app_actions.py     # 打开校园服务（返回 actions）
├── data/
│   ├── documents/         # 原始知识 txt
│   └── service_catalog.json
├── frontend/              # 可选网页对话
├── .env.example           # 环境变量模板（复制为 .env）
├── requirements.txt
└── 一键启动脚本.bat / 真机联调-*.bat
```

---

## 9. 费用与隐私说明

- 每次对话会调用你配置的大模型 API，**按服务商计费**，请自行控制用量。
- 本仓库不包含任何作者的真实 API Key；你本地的 `.env` 仅留在自己电脑。
- 课表、签到等由 App 按需上传 `device_context`，数据走你本机后端，不经过作者服务器。

---

## 10. 常见问题

**Q: 网页能聊，手机 App 不行？**  
A: 多半是没做 `adb reverse`，或 USB 调试未授权。见第 6 节。

**Q: 启动报向量模型 / HuggingFace 相关错误？**  
A: 本机缺少 `bge-large-zh-v1.5` 缓存，或未先跑 `build_vectordb.py`。

**Q: 改了 `data/documents` 没生效？**  
A: 删除旧 `vectordb` 后重新 `python build_vectordb.py`，并重启 uvicorn。

**Q: 为什么不直接部署成全员可用的云服务？**  
A: 云端托管会持续产生 API 费用，个人难以承担。开源本地版便于有兴趣的同学自备 Key 体验。

---

## 许可与相关

配合客户端：[鲤工助手 SCUT-Helper](https://github.com/tianma-afk/SCUT-Helper)（名称以实际仓库为准）。

有问题可通过 App 内反馈入口联系开发者。
