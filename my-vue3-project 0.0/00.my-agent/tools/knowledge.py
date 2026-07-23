import os
# 设置镜像源（虽然离线也用不上，但保留以防万一）
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
# 强制离线，避免启动时联网检查
os.environ["HF_HUB_OFFLINE"] = "1"

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.tools import tool

# 使用相同的新模型，且仅使用本地缓存
_vectorstore = Chroma(
    persist_directory="vectordb",
    embedding_function=HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-zh-v1.5",          # 与构建时一致
        model_kwargs={'device': 'cpu', 'local_files_only': True},
        encode_kwargs={'normalize_embeddings': True}
    )
)

@tool
def search_knowledge_base(query: str) -> str:
    """搜索内部知识库，包含校园服务、常用链接、实验室规定等。"""
    docs = _vectorstore.similarity_search(query, k=5)
    if not docs:
        return "未找到相关信息。"
    parts = []
    for d in docs:
        src = d.metadata.get("source", "未知")
        parts.append(f"[来源：{src}]\n{d.page_content}")
    return "\n\n".join(parts)