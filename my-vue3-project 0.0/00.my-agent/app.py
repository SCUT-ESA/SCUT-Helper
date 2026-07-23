from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agent import agent, memory
from device_context import wrap_user_message
import uuid
import json
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    thread_id: str = None
    # 阶段二再用；阶段一可忽略
    device_context: dict = None


class ResetRequest(BaseModel):
    thread_id: str


def _clear_thread_memory(thread_id: str) -> bool:
    """清理 MemorySaver 中指定会话；兼容新旧 API。"""
    if not thread_id:
        return False
    try:
        if hasattr(memory, "delete_thread"):
            memory.delete_thread(thread_id)
            return True
    except Exception:
        traceback.print_exc()
    # 旧版兜底：直接清内部 storage
    try:
        storage = getattr(memory, "storage", None)
        if isinstance(storage, dict) and thread_id in storage:
            del storage[thread_id]
            return True
    except Exception:
        traceback.print_exc()
    return False


def _chunk_text(content):
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict):
                # 兼容 text / thinking 分片
                t = p.get("type")
                if t in ("thinking", "reasoning"):
                    text = p.get("thinking") or p.get("text") or p.get("content") or ""
                    if text:
                        parts.append(str(text))
                else:
                    text = p.get("text") or p.get("content") or ""
                    if text:
                        parts.append(str(text))
            else:
                text = getattr(p, "text", None) or getattr(p, "content", None)
                if text:
                    parts.append(str(text))
        return "".join(parts)
    return str(content)


def _parse_tool_payload(raw):
    """从工具返回内容中解析 JSON（可能整段 JSON，或夹杂文本）。"""
    if raw is None:
        return None
    text = raw if isinstance(raw, str) else _chunk_text(raw)
    text = (text or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        pass
    # 尝试截取第一个 { ... } 块
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except Exception:
            return None
    return None


def _extract_actions(messages):
    """只收集「本轮用户消息之后」的 ToolMessage actions，避免会话记忆导致历史跳转累积。"""
    msgs = list(messages or [])
    # 找到本轮最后一条用户消息，只扫描其后的工具结果
    start = 0
    for i in range(len(msgs) - 1, -1, -1):
        msg = msgs[i]
        msg_type = getattr(msg, "type", None)
        if msg_type in ("human", "user"):
            start = i + 1
            break
        # 兼容纯元组形态少见情况
        if isinstance(msg, (tuple, list)) and msg and msg[0] in ("human", "user"):
            start = i + 1
            break

    actions = []
    seen = set()
    for msg in msgs[start:]:
        msg_type = getattr(msg, "type", None)
        if msg_type not in ("tool", "function"):
            name = type(msg).__name__
            if name not in ("ToolMessage", "FunctionMessage"):
                continue
        payload = _parse_tool_payload(getattr(msg, "content", None))
        if not isinstance(payload, dict):
            continue
        for act in payload.get("actions") or []:
            if not isinstance(act, dict):
                continue
            t = act.get("type")
            if t == "switch_tab":
                key = ("switch_tab", act.get("path") or "")
            elif t == "navigate_to":
                key = ("navigate_to", act.get("path") or "")
            elif t in ("open_campus_web", "open_webview"):
                key = (t, act.get("url") or "")
            else:
                continue
            if not key[1] or key in seen:
                continue
            seen.add(key)
            actions.append(act)
    return actions


def _sse(data):
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


async def _stream_events(message: str, tid: str):
    config = {"configurable": {"thread_id": tid}}
    yield _sse({"thread_id": tid})
    try:
        # 优先 messages 流：比 astream_events v1 更稳，且不会打 deprecation
        async for item in agent.astream(
            {"messages": [("user", message)]},
            config,
            stream_mode="messages",
        ):
            msg = item[0] if isinstance(item, (tuple, list)) else item
            # 跳过工具相关空片
            additional = getattr(msg, "additional_kwargs", None) or {}
            if additional.get("tool_calls") and not getattr(msg, "content", None):
                continue
            chunk = _chunk_text(getattr(msg, "content", None))
            if chunk:
                yield _sse({"content": chunk})
    except Exception as e:
        traceback.print_exc()
        yield _sse({"error": str(e)})
    # 无论成功失败都发结束标记，避免前端卡在“生成中”
    yield "data: [DONE]\n\n"


def _sse_response(message: str, thread_id: str = None):
    tid = thread_id or str(uuid.uuid4())
    return StreamingResponse(
        _stream_events(message, tid),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/chat")
def chat(req: ChatRequest):
    tid = req.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": tid}}
    user_text = wrap_user_message(req.message, req.device_context)
    result = agent.invoke({"messages": [("user", user_text)]}, config)
    messages = result.get("messages") or []
    answer = "未获取到回答"
    # 取最后一条「有可见正文」的 AI 消息，跳过纯 tool_calls 空片
    for msg in reversed(messages):
        if getattr(msg, "type", None) != "ai":
            continue
        content = getattr(msg, "content", None)
        text = content if isinstance(content, str) else _chunk_text(content)
        if text and str(text).strip():
            answer = str(text).strip()
            break
    actions = _extract_actions(messages)
    return {"thread_id": tid, "answer": answer, "actions": actions}


@app.post("/chat/reset")
def reset_chat(req: ResetRequest):
    """前端「新对话」：丢掉旧 thread_id 的会话记忆。"""
    ok = _clear_thread_memory(req.thread_id)
    return {"ok": ok, "thread_id": req.thread_id}


@app.get("/chat/stream")
async def stream_get(message: str, thread_id: str = None):
    return _sse_response(message, thread_id)


@app.post("/chat/stream")
async def stream_post(req: ChatRequest):
    text = wrap_user_message(req.message, req.device_context)
    return _sse_response(text, req.thread_id)
