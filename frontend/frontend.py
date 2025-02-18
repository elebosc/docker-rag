import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from ollama import Client
from flask import Flask, request


def extract_context(query):

    chroma_client = chromadb.HttpClient(
        host='rag-backend_chroma',
        port=8000,
        settings=Settings(allow_reset=True),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE
    )

    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    db = Chroma(
        client=chroma_client,
        collection_name="data_collection",
        embedding_function=embedding_function,
    )

    relevant_chunks = db.similarity_search(query)

    context = ''
    for chunk in relevant_chunks:
        context ='. '.join([context, chunk.page_content])

    return context


def get_context_prompt(context):

    return f"""
    You are given the following context:
    {context}
    """


def get_query_prompt(query):

    return f"""
    Based on the provided context, please provide the answer to the following query:
    {query}
    """


def get_llm_answer(context, query):

    context_prompt = get_context_prompt(context)
    query_prompt = get_query_prompt(query)

    print(context_prompt)
    print(query_prompt)

    client = Client(host='rag-backend_ollama')
    answer_stream = client.chat(
        model='mistralgguf',
        messages=[
            {"role": "system", "content": context_prompt},            
            {"role": "user", "content": query_prompt}
        ],
        stream=True
    )

    print("Formulating an answer...")
    answer = ''
    for chunk in answer_stream:
        print(chunk['message']['content'], end='', flush=True)
        answer = ''.join([answer, chunk['message']['content']])
    
    return answer


app = Flask(__name__) 

@app.route('/', methods=['POST'])
def get_answer():
    if request.method == 'POST':
        data = request.get_json()
        query = data.get('query')
        context = extract_context(query)
        answer = f'This is the answer to your query:\n {get_llm_answer(context, query)}'
        return answer
    
if __name__ == '__main__':
    app.run()
