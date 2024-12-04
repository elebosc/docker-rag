import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from ollama import Client
from flask import Flask, request

def extract_context(query):

    """
    Specifies another Chroma client to escape our container and perform a similarity search on
    our transformed documents in the vector database, returning the results which we will use
    as context for the query.
    """

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
        collection_name="my_collection",
        embedding_function=embedding_function,
    )
    docs = db.similarity_search(query)
    fullcontent = ''
    for doc in docs:
        fullcontent ='. '.join([fullcontent,doc.page_content])

    return fullcontent

def get_context_prompt(context):

    """
    Prepends the text content given as argument with a set of instructions to be used as the
    system prompt for our query.
    """

    return f"""You are an expert consultant helping executive advisors to get relevant information from internal documents.

    Generate your response by following the steps below:
    1. Recursively break down the question into smaller questions.
    2. For each question/directive:
        2a. Select the most relevant information from the context in light of the conversation history.
    3. Generate a draft response using selected information.
    4. Remove duplicate content from draft response.
    5. Generate your final response after adjusting it to increase accuracy and relevance.
    6. Do not try to summarise the answers, explain it properly.
    6. Only show your final response! 
    
    Constraints:
    1. DO NOT PROVIDE ANY EXPLANATION OR DETAILS OR MENTION THAT YOU WERE GIVEN CONTEXT.
    2. Don't mention that you are not able to find the answer in the provided context.
    3. Don't make up the answers by yourself.
    4. Try your best to provide answer from the given context.

    CONTEXT:
    {context}
    """

def get_question_prompt(question):

    """
    Forms the user query following the system message containing the context.
    """

    return f"""
    ==============================================================
    Based on the above context, please provide the answer to the following question:
    {question}
    """

def generate_rag_response(context, question):

    """
    Specifies the Ollama client, model and input we want to use for our query.
    """

    client = Client(host='rag-backend_ollama')
    stream = client.chat(
        model='mistralgguf',
        messages=[
            {"role": "system", "content": get_context_prompt(context)},            
            {"role": "user", "content": get_question_prompt(question)}
        ],
        stream=True
    )
    print(get_context_prompt(context))
    print(get_question_prompt(question))
    print("####### THINKING OF ANSWER............ ")
    full_answer = ''
    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)
        full_answer =''.join([full_answer,chunk['message']['content']])

    return full_answer

# Flask server creation

app = Flask(__name__) 

@app.route('/query', methods=['POST'])
def respond_to_query():
    if request.method == 'POST':
        data = request.get_json()
        # Assuming the query is sent as a JSON object with a key named 'query'
        query = data.get('query')
        # Here you can process the query and generate a response
        response = f'This is the response to your query:\n {generate_rag_response(extract_context(query), query)}'
        return response
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
