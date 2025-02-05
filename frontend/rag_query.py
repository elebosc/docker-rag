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

def generate_rag_response(context, query):

    client = Client(host='rag-backend_ollama')
    response_stream = client.chat(
        model='mistralgguf',
        messages=[
            {"role": "system", "content": get_context_prompt(context)},            
            {"role": "user", "content": get_query_prompt(query)}
        ],
        stream=True
    )

    print(get_context_prompt(context))
    print(get_query_prompt(query))

    print("Formulating a response...")
    full_answer = ''
    for chunk in response_stream:
        print(chunk['message']['content'], end='', flush=True)
        full_answer =''.join([full_answer, chunk['message']['content']])

    return full_answer

# Flask server creation

app = Flask(__name__) 

@app.route('/query', methods=['POST'])
def get_answer():
    if request.method == 'POST':
        data = request.get_json()
        query = data.get('query')
        response = f'This is the response to your query:\n {generate_rag_response(extract_context(query), query)}'
        return response
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
