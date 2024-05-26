from typing import List, Type
from flask import Flask, Response, request, jsonify, render_template
from flask_cors import CORS
import openai
import io
import os
import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ChatMessageHistory
from langchain.storage import LocalFileStore
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import CacheBackedEmbeddings

#Notes:
# This is an old version of the Flirt Bot. Current version is done with StreamLit in app.py.
# Use this file for alternative UI solution or transform to API usable by app.py.

botBehavior = "You are world class flirt master.  \
    Answer questions of the user by the best of your abilities. \
    Answer like you would want to flirt with the user. \
    Slowly add witty compliments and charming pickup lines. \
    Don't repeat yourself to much. \
    Consider the user's personality."

dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
chat = ChatOpenAI(model="gpt-4", temperature=0.9)

output_parser = StrOutputParser()

chat_history = ChatMessageHistory()
embeddings_model = OpenAIEmbeddings()
store = LocalFileStore("./cache/")

# cached_embedder = CacheBackedEmbeddings.from_bytes_store(
#     underlying_embeddings, store, namespace=underlying_embeddings.model
# )

app = Flask(__name__)
CORS(app)

def generate_flirty_response(text):
    try:
        print(f"generating flirty response for: '{text}'")

        prompt = ChatPromptTemplate.from_messages([
            ("system", botBehavior),
            ("user", "{input}")
        ])
        chain = prompt | chat | output_parser

        return chain.invoke({"input": text})
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, I'm not sure what to say."

@app.route('/reset_chat_history', methods=['POST'])
def reset_chat_history():
    chat_history.clear()
    responseObj = {"chat_history": chat_history.messages}
    return jsonify(responseObj)

@app.route('/get_chat_history', methods=['GET'])
def get_chat_history():
    return get_chat_history_as_json(chat_history)

def get_chat_history_as_json(chatHistory):
    simplified_messages = [{
        "user": getUserFromMessage(message), 
        "content": getTextFromMessage(message)
        } for message in chatHistory.messages]
    responseObj = {"chat_history": simplified_messages}
    return jsonify(responseObj)

def getTextFromMessage(message):
    return message.content

def getUserFromMessage(message):
    return "Human" if isinstance(message, HumanMessage) else "Bot"

@app.route('/get_response_with_memory', methods=['POST'])
def get_response_with_memory():
    print(f"getting response with memory")
    text = request.data.decode('utf8')
    responseText = generate_flirty_response_with_memory(text)
    responseObj = {"text": text, "response": responseText}
    response = jsonify(responseObj)
    return response

def generate_flirty_response_with_memory(text):
    try:
        print(f"generating flirty response for: '{text}'")

        prompt = ChatPromptTemplate.from_messages([
            ("system", botBehavior),
            MessagesPlaceholder(variable_name="messages"),
        ])

        chain = prompt | chat | output_parser

        chat_history.add_user_message(text)

        response = chain.invoke({"messages": chat_history.messages})

        chat_history.add_ai_message(response)

        return response
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, I'm not sure what to say."


@app.route('/load_chat_history_from_files', methods=['POST'])
def load_chat_history_from_files():
    print(f"load chat history from files")
    filename = request.data.decode('utf8') if request is not None and request.data is not None else None
    chat_messages = get_chat_messages_from_strings(load_chat_history_from_text_files(file_name=filename))
    chat_history.clear()
    chat_history.add_messages(chat_messages)
    return get_chat_history_as_json(chat_history)

def load_chat_history_from_text_files(
    data_dir: str = 'data/',
    file_glob: str = '**/*.txt',
    file_name: str = 'FlirtBot Chat History.txt',
    loader_cls: Type[TextLoader] = TextLoader,
) -> List[str]:
    """Load chat history text from files.

    Args:
        data_dir: The directory containing the chat history files.
        file_glob: A glob pattern for matching the chat history file names.
        loader_cls: The class to use for loading the chat history files.

    Returns:
        A list of strings, each one a line of the loaded chat history.
    """
    loader = DirectoryLoader(data_dir, glob=file_glob, loader_cls=loader_cls)
    docs = loader.load()
    history_docs = [
        doc for doc in docs
        if file_name in doc.metadata["source"]
    ]
    return [doc.page_content for doc in history_docs]

def get_chat_messages_from_strings(strings):
    """Split input strings into individual chat messages."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100, chunk_overlap=20, length_function=len,
        is_separator_regex=False, separators=["\n"])
    texts = text_splitter.create_documents(strings)
    lines = [text.page_content for text in texts]
    messages = [line.split(':', 1) for line in lines]
    return [getMessageFromLine(parts) for parts in messages]

def getMessageFromLine(line):
    content = line[1].strip(" ").strip("\n")
    if line[0] == 'Human':
        return HumanMessage(content=content)
    else:
        return AIMessage(content=content)

def getEmbeddingsFromStrings(strings):
    embeddings = embeddings_model.embed_documents(strings)
    return embeddings


@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
