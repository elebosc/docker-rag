from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.pdf import PyMuPDFLoader
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import CharacterTextSplitter

import uuid
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

# Load documents
loader = DirectoryLoader("documents", glob="*.pdf", loader_cls=PyMuPDFLoader)
documents = loader.load()

# Split documents into chunks
text_splitter = CharacterTextSplitter(chunk_size=256, chunk_overlap=40)
chunks = text_splitter.split_documents(documents)

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Creation of Chroma vectors db

chroma_client = chromadb.HttpClient(
    host="rag-backend_chroma",
    port=8000,
    settings=Settings(allow_reset=True),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE
)

try:
    chroma_client.get_collection("data_collection")
    chroma_client.delete_collection("data_collection")
except:
    pass
collection = chroma_client.create_collection("data_collection")

for chunk in chunks:
    collection.add(
        ids=[str(uuid.uuid1())],
        metadatas=chunk.metadata, 
        documents=chunk.page_content
    )

db = Chroma(
    client=chroma_client,
    collection_name="data_collection",
    embedding_function=embedding_function,
)
