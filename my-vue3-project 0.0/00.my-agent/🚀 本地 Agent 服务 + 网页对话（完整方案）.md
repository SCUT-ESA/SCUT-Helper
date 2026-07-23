# 🚀 本地 Agent 服务 + 网页对话（完整方案）

## 项目结构（最终）

text

```
my-agent/
├── .env                     # 环境变量（需自己创建）
├── requirements.txt         # 依赖列表
├── build_vectordb.py        # 构建知识库（运行一次）
├── agent.py                 # Agent 核心
├── app.py                   # FastAPI 服务（含 CORS）
├── start.sh / start.bat     # 一键启动脚本
├── tools/
│   ├── knowledge.py         # 知识库检索工具
│   └── analysis.py          # 代码执行工具（E2B）
├── data/
│   └── documents/           # 存放你的 .txt 知识文档（可自己添加）
│       └── campus.txt       # 示例文档
└── frontend/
    └── index.html           # 对话界面（双击打开）
```



------

## 第一步：环境准备

### 1. 安装 Python 3.10+（若未安装）

- 官网下载或使用 Anaconda。

### 2. 注册 API Key

- **OpenAI API Key**（或兼容接口，如 DeepSeek）
- **E2B API Key**（注册 [e2b.dev](https://e2b.dev/) 免费获取）

### 3. 克隆/创建项目

打开终端，执行：

bash

```
mkdir my-agent && cd my-agent
python -m venv venv
source venv/bin/activate          # Mac/Linux
# 或 venv\Scripts\activate       # Windows
```



------

## 第二步：安装依赖

创建 `requirements.txt`（固定版本，避免兼容性问题）：

txt

```
langgraph==0.0.20
langchain-openai==0.0.5
langchain-community==0.0.10
langchain-text-splitters==0.0.1
chromadb==0.5.0
fastapi==0.110.0
uvicorn==0.27.0
python-dotenv==1.0.0
e2b-code-interpreter==0.0.10
```



然后安装：

bash

```
pip install -r requirements.txt
```



------

## 第三步：配置环境变量

创建 `.env` 文件（与 `requirements.txt` 同级）：

env

```
OPENAI_API_KEY=sk-你的OpenAI密钥
E2B_API_KEY=e2b_你的E2B密钥
# 如果使用兼容接口，可加 OPENAI_BASE_URL=...
```



------

## 第四步：准备知识文档

在 `data/documents/` 下放入你的 `.txt` 或 `.md` 文件。
例如创建 `data/documents/campus.txt`，内容：

text

```
校园网缴费入口：http://netpay.university.edu.cn
账号为学号，初始密码是身份证后6位。
实验室离心机使用规范：必须先配平，转速不得超过5000rpm。
```



------

## 第五步：构建向量知识库

新建 `build_vectordb.py`：

python

```
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
load_dotenv()

loader = DirectoryLoader("data/documents/", glob="*.txt", loader_cls=TextLoader)
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="vectordb"
)
print(f"✅ 向量库构建完成，共 {len(chunks)} 个文档块。")
```



运行：

bash

```
python build_vectordb.py
```



------

## 第六步：创建工具

### 工具 1：知识库检索（`tools/knowledge.py`）

python

```
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.tools import tool

_vectorstore = Chroma(
    persist_directory="vectordb",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
)

@tool
def search_knowledge_base(query: str) -> str:
    """搜索内部知识库，包含校园服务、实验室规定等。"""
    docs = _vectorstore.similarity_search(query, k=3)
    if not docs:
        return "未找到相关信息。"
    parts = []
    for d in docs:
        src = d.metadata.get("source", "未知")
        parts.append(f"[来源：{src}]\n{d.page_content}")
    return "\n\n".join(parts)
```



### 工具 2：代码执行（`tools/analysis.py`，使用 E2B 新 API）

python

```
from e2b_code_interpreter import Sandbox
from langchain.tools import tool

@tool
def execute_python(code: str) -> str:
    """安全执行 Python 代码，用于数据分析、计算、画图。"""
    with Sandbox() as sandbox:
        execution = sandbox.run_code(code)
        if execution.error:
            return f"代码执行错误：{execution.error}"
        output = ""
        if execution.text:
            output += execution.text
        for result in execution.results:
            if result.is_main:
                output += str(result)
        return output if output else "代码执行成功，无输出。"
```



> 如果不想用 E2B，可替换为本地 Docker 方案（见附录）。

------

## 第七步：创建 Agent（`agent.py`）

python

```
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from tools.knowledge import search_knowledge_base
from tools.analysis import execute_python
from dotenv import load_dotenv
load_dotenv()

tools = [search_knowledge_base, execute_python]

# 支持自定义 base_url（如 DeepSeek）
model = ChatOpenAI(
    model="gpt-4o",  # 或 "deepseek-chat"
    temperature=0,
    # base_url="https://api.deepseek.com/v1"   # 如使用国产模型
)
memory = MemorySaver()

agent = create_react_agent(model, tools, checkpointer=memory)
```



------

## 第八步：创建 FastAPI 服务（`app.py`）

python

```
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agent import agent
import uuid
import json

app = FastAPI()

# 允许跨域（让本地 HTML 能访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    thread_id: str = None

@app.post("/chat")
def chat(req: ChatRequest):
    tid = req.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": tid}}
    result = agent.invoke({"messages": [("user", req.message)]}, config)
    # 取最后一条 AI 消息
    for msg in reversed(result["messages"]):
        if msg.type == "ai":
            answer = msg.content
            break
    else:
        answer = "未获取到回答"
    return {"thread_id": tid, "answer": answer}

@app.get("/chat/stream")
async def stream(message: str, thread_id: str = None):
    tid = thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": tid}}
    
    async def event_gen():
        async for event in agent.astream_events(
            {"messages": [("user", message)]}, config, version="v1"
        ):
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk:
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
        # 发送结束标记
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_gen(), media_type="text/event-stream")
```



------

## 第九步：启动后端服务

### 方式一：直接运行

bash

```
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```



### 方式二：一键启动脚本（可选）

**Mac/Linux** 创建 `start.sh`：

bash

```
#!/bin/bash
source venv/bin/activate
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```



**Windows** 创建 `start.bat`：

bat

```
call venv\Scripts\activate
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```



然后赋予执行权限（Mac/Linux: `chmod +x start.sh`），双击或终端运行。

------

## 第十步：打开前端对话界面

在项目根目录下创建 `frontend/index.html`（内容见下方）。
然后**直接在浏览器中双击打开** `index.html`，即可开始对话。

### `frontend/index.html`（完整代码）

```html
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>本地 Agent 智能助手</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .chat-box {
            width: 820px;
            max-width: 98vw;
            height: 90vh;
            background: white;
            border-radius: 28px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.12);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .header {
            padding: 18px 28px;
            background: #ffffff;
            border-bottom: 1px solid #e8eaed;
            font-weight: 600;
            font-size: 18px;
            color: #1f2a3a;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .header span {
            background: #eef2f6;
            padding: 4px 12px;
            border-radius: 30px;
            font-size: 13px;
            font-weight: 400;
            color: #3c4a5c;
        }
        .messages {
            flex: 1;
            padding: 24px 28px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 14px;
            background: #fafbfc;
        }
        .msg {
            max-width: 80%;
            padding: 12px 18px;
            border-radius: 20px;
            line-height: 1.6;
            word-break: break-word;
            white-space: pre-wrap;
            font-size: 15px;
            animation: fadeIn 0.3s ease;
        }
        .msg.user {
            align-self: flex-end;
            background: #0084ff;
            color: white;
            border-bottom-right-radius: 6px;
        }
        .msg.agent {
            align-self: flex-start;
            background: #e9edf2;
            color: #1e1e1e;
            border-bottom-left-radius: 6px;
        }
        .msg .typing {
            display: inline-block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #888;
            margin-right: 4px;
            animation: pulse 1.4s infinite;
        }
        .msg .typing:nth-child(2) { animation-delay: 0.2s; }
        .msg .typing:nth-child(3) { animation-delay: 0.4s; }
        @keyframes pulse {
            0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
            40% { opacity: 1; transform: scale(1.1); }
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .input-area {
            padding: 16px 28px 20px;
            border-top: 1px solid #e8eaed;
            background: white;
            display: flex;
            gap: 12px;
        }
        .input-area input {
            flex: 1;
            padding: 12px 18px;
            border: 1px solid #d0d5dd;
            border-radius: 40px;
            font-size: 15px;
            outline: none;
            transition: border 0.2s;
            background: #fafbfc;
        }
        .input-area input:focus {
            border-color: #0084ff;
            background: white;
        }
        .input-area button {
            padding: 12px 32px;
            background: #0084ff;
            color: white;
            border: none;
            border-radius: 40px;
            font-size: 15px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s, transform 0.1s;
        }
        .input-area button:hover { background: #0070e0; }
        .input-area button:active { transform: scale(0.96); }
        .input-area button:disabled {
            background: #b0b8c4;
            cursor: not-allowed;
        }
        .error-msg {
            color: #d32f2f;
            background: #ffebee;
            padding: 10px 16px;
            border-radius: 12px;
            align-self: center;
            max-width: 90%;
        }
    </style>
</head>
<body>
<div class="chat-box">
    <div class="header">
        🤖 本地 Agent
        <span>知识库 + 代码执行</span>
    </div>
    <div class="messages" id="messageContainer"></div>
    <div class="input-area">
        <input id="input" type="text" placeholder="输入你的问题..." autofocus />
        <button id="sendBtn">发送</button>
    </div>
</div>
<script>
    (function(){
        const container = document.getElementById('messageContainer');
        const input = document.getElementById('input');
        const sendBtn = document.getElementById('sendBtn');

        const BASE = 'http://127.0.0.1:8000';
        const THREAD_ID = 'web-' + Date.now();

        function addMessage(text, sender, isError = false) {
            const div = document.createElement('div');
            div.className = `msg ${sender}`;
            if (isError) div.classList.add('error-msg');
            div.textContent = text;
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
            return div;
        }

        function showTyping() {
            const div = document.createElement('div');
            div.className = 'msg agent';
            div.innerHTML = '<span class="typing"></span><span class="typing"></span><span class="typing"></span>';
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
            return div;
        }

        async function sendMessage(text) {
            if (!text.trim()) return;
            addMessage(text, 'user');
            input.value = '';
            sendBtn.disabled = true;

            const typingEl = showTyping();

            try {
                const url = `${BASE}/chat/stream?message=${encodeURIComponent(text)}&thread_id=${THREAD_ID}`;
                const resp = await fetch(url);
                if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

                const reader = resp.body.getReader();
                const decoder = new TextDecoder('utf-8');
                let buffer = '';
                let full = '';
                // 移除打字占位，准备正式消息
                typingEl.remove();
                const agentMsg = addMessage('', 'agent');

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    buffer += decoder.decode(value, { stream: true });
                    const parts = buffer.split('\n\n');
                    buffer = parts.pop() || '';
                    for (const part of parts) {
                        if (part.startsWith('data: ')) {
                            const data = part.slice(6).trim();
                            if (data === '[DONE]') continue;
                            try {
                                const json = JSON.parse(data);
                                const chunk = json.content || '';
                                if (chunk) {
                                    full += chunk;
                                    agentMsg.textContent = full;
                                    container.scrollTop = container.scrollHeight;
                                }
                            } catch (_) {}
                        }
                    }
                }
                if (!full.trim()) {
                    agentMsg.textContent = '（未收到有效回复）';
                }
            } catch (err) {
                typingEl.remove();
                addMessage(`❌ 请求失败：${err.message}`, 'agent', true);
            } finally {
                sendBtn.disabled = false;
                input.focus();
            }
        }

        sendBtn.addEventListener('click', () => sendMessage(input.value));
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage(input.value);
            }
        });

        // 欢迎消息
        addMessage('👋 你好！我是本地 Agent，可以查询校园知识，也能运行 Python 代码。试试问我吧。', 'agent');
    })();
</script>
</body>
</html>
```



------

## 第十一步：测试运行

1. 确保 `.env` 中的 Key 正确。
2. 确保已构建知识库（运行过 `build_vectordb.py`）。
3. 启动后端：`uvicorn app:app --reload`（或运行 `start.sh`）。
4. 双击打开 `frontend/index.html`。
5. 输入问题，例如：
   - “校园网怎么缴费？”
   - “帮我计算 1 到 100 的和”
   - “生成 10 个随机数并求平均值”（会调用代码执行工具）

------

## 附录：替换为本地 Docker 沙箱（不用 E2B）

如果你不想用 E2B，可将 `tools/analysis.py` 替换为以下（需安装 Docker Desktop 和 `docker` Python 包）：

python

```
import docker
import tempfile
import os
from langchain.tools import tool

client = docker.from_env()

@tool
def execute_python(code: str) -> str:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name
    try:
        container = client.containers.run(
            "python:3.10-slim",
            command="python /code.py",
            volumes={os.path.abspath(tmp_path): {'bind': '/code.py', 'mode': 'ro'}},
            network_disabled=True,
            mem_limit="512m",
            remove=True,
            timeout=30,
        )
        logs = container.decode('utf-8') if isinstance(container, bytes) else container
        return logs or "执行成功，无输出。"
    except Exception as e:
        return f"执行错误：{e}"
    finally:
        os.unlink(tmp_path)
```



并在 `requirements.txt` 中添加 `docker`。



好的，我为你整理一份**日常启动指南**，以后每次使用只需三步。

------

# 🚀 日常启动步骤（每次使用）

### 第一步：打开终端，进入项目目录并激活虚拟环境

cmd

```
F:
cd F:\my-agent
venv\Scripts\activate
```



看到提示符变成 `(venv) F:\my-agent>` 表示激活成功。

------

### 第二步：启动后端服务

cmd

```
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```



看到以下输出表示启动成功：

text

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```



**保持这个 CMD 窗口不要关闭**（后端需要一直运行）。

------

### 第三步：打开前端页面

**方式一（推荐）**：用 Python 静态服务器打开

1. **另开一个 CMD 窗口**（不要关掉刚才那个），进入项目目录：

   cmd

   ```
   cd F:\my-agent
   ```

   

2. 启动静态服务器：

   cmd

   ```
   python -m http.server 8080
   ```

   

3. 在浏览器中访问：`http://127.0.0.1:8080/frontend/index.html`

**方式二（简单粗暴）**：直接双击 `F:\my-agent\frontend\index.html` 文件

> ⚠️ 注意：双击打开可能会出现跨域错误（`Failed to fetch`），如果遇到就用方式一。

------

## 🔄 日常关闭

- **后端**：在运行 `uvicorn` 的 CMD 窗口中按 `Ctrl+C` 停止。
- **前端服务器**：在运行 `http.server` 的 CMD 窗口中按 `Ctrl+C` 停止。
- **虚拟环境**：在任意 CMD 窗口输入 `deactivate` 退出虚拟环境。

------

## 📌 小贴士

| 场景                                        | 操作                                                         |
| :------------------------------------------ | :----------------------------------------------------------- |
| **知识库更新了**（添加/修改了 `.txt` 文件） | 重新运行 `python build_vectordb.py`，然后重启后端            |
| **后端启动失败**                            | 检查端口是否被占用：`netstat -ano | findstr :8000`           |
| **前端连接不上后端**                        | 检查后端是否在运行，浏览器是否用 `http://` 方式打开          |
| **想换端口**                                | 启动时改 `--port 8080`，前端也要同步改 `fetch("http://127.0.0.1:8080/chat")` |

------

## 🧪 快速验证系统是否正常

在浏览器中打开 `http://127.0.0.1:8000/docs`，如果能出现 FastAPI 的自动文档页面，说明后端完全正常。

------

以后每次使用就这三步：**激活环境 → 启动后端 → 打开前端**。有任何问题随时叫我。

添加新资料后，重新 Embedding 的步骤如下：

------

# 📚 重新构建向量库（知识库更新后）

### 第一步：将新资料放入知识库目录

将你的 `.txt` 文件复制到：

text

```
F:\my-agent\data\documents\
```



> ⚠️ 确保文件编码为 **UTF-8**（用记事本打开，另存为时选择 UTF-8）。

------

### 第二步：删除旧的向量库（强制重建）

打开终端，进入项目目录并激活虚拟环境：

cmd

```
F:
cd F:\my-agent
venv\Scripts\activate
```



删除旧向量库：

cmd

```
rmdir /s vectordb
```



------

### 第三步：重新构建向量库

cmd

```
python build_vectordb.py
```



等待执行完毕，看到输出：

text

```
✅ 向量库构建完成，共 X 个文档块。
```



------

### 第四步：重启后端服务

如果后端正在运行，按 `Ctrl+C` 停止，然后重新启动：

cmd

```
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```



> 因为使用了 `--reload`，理论上会自动检测到知识库变化（但向量库文件变动可能不会触发热重载，建议手动重启确保生效）。

------

## ✅ 验证新知识是否生效

打开前端页面，问一个**只有新资料里才有**的问题，看 Agent 能否正确回答。

------

## 📌 快捷命令（一键重建）

cmd

```
F: && cd F:\my-agent && venv\Scripts\activate && rmdir /s vectordb && python build_vectordb.py
```



执行后等重建完成，再手动重启后端即可。

------

以后每次添加或修改 `data/documents/` 下的文件，重复以上步骤即可。如果构建过程中遇到报错，把错误信息贴给我，我帮你解决。