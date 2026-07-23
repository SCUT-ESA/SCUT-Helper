import os
# 设置 HuggingFace 镜像源（国内加速）
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
# 强制离线（下载后使用本地缓存，避免启动时联网）
os.environ["HF_HUB_OFFLINE"] = "1"

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

# 加载文档
loader = DirectoryLoader(
    "data/documents/",
    glob="*.txt",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"}
)
docs = loader.load()
print(f"📄 加载了 {len(docs)} 个文档")

# 分割文档
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)
print(f"✂️ 分割为 {len(chunks)} 个文档块")

# 使用更强的 BGE-large-zh-v1.5（1.3GB，中文 SOTA）
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-zh-v1.5",          # 新模型
    model_kwargs={'device': 'cpu', 'local_files_only': True},   # 使用本地缓存
    encode_kwargs={'normalize_embeddings': True}
)

# 构建向量库（会保存到 vectordb 目录）
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="vectordb"
)
print(f"✅ 向量库构建完成，共 {len(chunks)} 个文档块。")