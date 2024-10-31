import langchain_community
import langchain_text_splitters
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import CharacterTextSplitter

import uuid
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

# Load the document and split it into pages
loader = PyPDFLoader("2404.07143v2.pdf")
pages = loader.load_and_split()

# Split it into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(pages)

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

for doc in docs:
    collection.add(
        ids=[str(uuid.uuid1())], metadatas=doc.metadata, documents=doc.page_content
    )

db = Chroma(
    client=client,
    collection_name="my_collection",
    embedding_function=embedding_function,
)
