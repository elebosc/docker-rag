from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.pdf import PyMuPDFLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import CharacterTextSplitter

import uuid
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

# Load the documents
loader = DirectoryLoader("documents", glob="*.pdf", loader_cls=PyMuPDFLoader)
documents = loader.load()

# Split them into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
chunks = text_splitter.split_documents(documents)

# Create the open-source embedding function
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Creation of Chroma vectors db

client = chromadb.HttpClient(
    host="rag-llm-chroma-1",
    port=8000,
    settings=Settings(allow_reset=True),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE
)

try:
    client.get_collection("my_collection")
    client.delete_collection("my_collection")
except:
    pass
collection = client.create_collection("my_collection")

for chunk in chunks:
    collection.add(
        ids=[str(uuid.uuid1())], metadatas=chunk.metadata, documents=chunk.page_content
    )

db = Chroma(
    client=client,
    collection_name="my_collection",
    embedding_function=embedding_function,
)
