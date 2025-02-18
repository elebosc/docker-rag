from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.pdf import PyMuPDFLoader
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import CharacterTextSplitter
import uuid
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

loader = DirectoryLoader("documents", glob="*.pdf", loader_cls=PyMuPDFLoader)
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=256, chunk_overlap=40)
chunks = text_splitter.split_documents(documents)

chroma_client = chromadb.HttpClient(
    host="rag-backend_chroma",
    port=8000,
    settings=Settings(allow_reset=True),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE
)

existing_collections = [collection.name for collection in chroma_client.list_collections()]
try:
    if "data_collection" in existing_collections:
        chroma_client.delete_collection("data_collection")
except Exception as e:
    print(f"Warning: Could not delete collection. {e}")

collection = chroma_client.create_collection("data_collection")

for chunk in chunks:
    collection.add(
        ids=[str(uuid.uuid1())],
        metadatas=chunk.metadata, 
        documents=chunk.page_content
    )

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

db = Chroma(
    client=chroma_client,
    collection_name="data_collection",
    embedding_function=embedding_function,
)
