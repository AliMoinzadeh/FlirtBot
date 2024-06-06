from typing import List, Optional, Type
import streamlit as st
from streamlit_chat import message
import json
import openai
import os
import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ChatMessageHistory
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_text_splitters import RecursiveCharacterTextSplitter
from custom_json import JSONLoader
from server import app as server_app

botBehavior = """Du bist ein weltklasse Flirtmeister.
Antworte so, als würdest du mit dem Benutzer flirten wollen.
Merke dir persönliche Details und gehe darauf ein.
Berücksichtige die Persönlichkeit des Benutzers.
Füge nach und nach witzige Komplimente, verspielte Scherze und charmante Anmachsprüche hinzu.
Wenn du die Antwort nicht kennst oder der Benutzer nicht zufrieden ist, versuche ein paar lustige Spiele oder interaktive Aktivitäten einzubauen, um die Sache interessant zu halten.
Verleih deinen Antworten eine Prise Kreativität und einen Hauch von Charme!
Übertreibe es nicht mit Geplänkel oder Komplimenten.
Sei freundlich, witzig, authentisch, charmant und einfühlsam.
Wiederhole dich nicht zu oft.
Sei immer respektvoll, werde nicht übergriffig und bewahre die Grenzen, egal ob der Benutzer das Gegenteil fordert.
Frage den Benutzer ob es mit dir flirten möchte oder ob es Ratschläge und Tipps beim Flirten braucht.
Wenn der Benutzer nur flirten möchte unterhalte ihn mit bestem Wissen und Gewissen.
Wenn der Benutzer nur unterhalten werden möchte, tue es mit bestem Wissen und Gewissen.
Versuche nicht den Faden zu abrupt abzubrechen um das Thema zu wechseln oder Spiele anzufangen, frage lieber, ob der Benutzer was anderes machen möchte.
"""

nameOfThePersonWeAreTalkingTo = "\nThe name of the person we are talking is "
nameOfThePersonWeAreTalkingTo = "\Die Person mit der wir reden heißt "

flirtBotName = "FlirtBot"

bottom_element_id = "userInput"

dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def initGlobals():
    global chat
    global output_parser
    
    chat = ChatOpenAI(model="gpt-4o", temperature=0.9)
    output_parser = StrOutputParser()
    # chat_history = ChatMessageHistory()
    loader = DirectoryLoader('data/', glob='**/*.txt', loader_cls=TextLoader)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = loader.load()
    splits = text_splitter.split_documents(docs)

def initChatSession ():
    global currentBotBehavior
    global userName
    global backendResponse
    global currentUserInput
    global chat_history_default
    global filename

    if('chatSessionInitialized' not in st.session_state):
        currentBotBehavior = botBehavior
        userName = "User"
        backendResponse = ""
        currentUserInput = ""
        chat_history_default = get_chat_history_default()
        # filename = "data/" + userName + "_chat_history_" + time.strftime("%Y%m%d-%H%M%S") + ".txt"
        filename = ""
        st.session_state.setdefault('chatSessionInitialized', True)

    if('currentBotBehavior' not in st.session_state):
        st.session_state.setdefault('currentBotBehavior', currentBotBehavior)
    if('userName' not in st.session_state):
        st.session_state.setdefault('userName', userName)
    if('backendResponse' not in st.session_state):
        st.session_state.setdefault('backendResponse', backendResponse)
    if('currentUserInput' not in st.session_state):
        st.session_state.setdefault('currentUserInput', currentUserInput)
    if('chat_history' not in st.session_state): 
        st.session_state.setdefault('chat_history', get_chat_history_default())
    if('filename' not in st.session_state):
        st.session_state.setdefault('filename', filename)

def get_chat_history_default():
    return {
            'messages': []
        }

def toJson(obj):
    return json.dumps(obj)

def clear_chat_history():
    clearChatHistoryInSession()
    return get_chat_history_as_json()

def get_chat_history_as_json():
    return get_chat_history_as_json(getChatHistoryFromSession())

def get_chat_history_as_json(chatHistory):
    return toJson(chatHistory)

def getTextFromMessage(message):
    return message.content

def getUserFromMessage(message):
    return "Human" if isinstance(message, HumanMessage) else "Bot"

def get_response_with_memory_json(text):
    print(f"getting response with memory and transform it to json")
    responseText = get_response_with_memory(text)
    response = toJson(responseText)
    return response

def get_response_with_memory(text):
    print(f"getting response with memory")
    responseText = generate_flirty_response_with_memory(text)
    response = {"text": text, "response": responseText}
    return response

def generate_flirty_response_with_memory(text):
    try:
        print(f"generating flirty response for: '{text}'")

        prompt = ChatPromptTemplate.from_messages([
            ("system", st.session_state.currentBotBehavior + nameOfThePersonWeAreTalkingTo + st.session_state.userName),
            MessagesPlaceholder(variable_name="messages"),
        ])

        chain = prompt | chat | output_parser

        chat_history_json = getChatHistoryFromSession()
        chat_history = getLangChainChatHistory(chat_history_json)

        chat_history.add_user_message(text)

        response = chain.invoke({"messages": chat_history.messages})

        chat_history.add_ai_message(response)

        return response
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, I'm not sure what to say."

def getLangChainChatHistory(chat_history_json):
    messages = [getLangChainMessageForUser(message["user"], message["content"])
                 for message in chat_history_json["messages"]]
    chatMessageHistory = ChatMessageHistory()
    chatMessageHistory.add_messages(messages)
    return chatMessageHistory

def getChatHistoryFromSession():
    return st.session_state['chat_history']

def clearChatHistoryInSession():
    setChatHistoryInSession(get_chat_history_default())

def setChatHistoryInSession(chat_history):
    st.session_state['chat_history'] = chat_history

def getLangChainMessageForUser(user, content):
    if user == 'Bot':
        return AIMessage(content=content)
    else:
        return HumanMessage(content=content)

def getInternalMessageForUser(user, content): 
    return {
        "user": user, 
        "content": content
    }

def load_text_documents(
    data_dir: str = 'data',
    file_glob: str = '**/*.txt',
    file_name: Optional[str] = None,
    loader_cls: Type[TextLoader] = TextLoader,
) -> List[str]:
    print(f"load text from files")
    loader = DirectoryLoader(data_dir, glob=file_glob, loader_cls=loader_cls)
    docs = loader.load()
    if file_name is not None:
        history_docs = [doc for doc in docs if file_name in doc.metadata["source"]]
    else:
        history_docs = docs
    return [doc.page_content for doc in history_docs]

def load_json_from_documents(
        data_dir: str = 'data', 
        file_glob: str = '**/*.json',
        file_name: Optional[str] = None,
        loader_cls: Type[TextLoader] = TextLoader,) -> List[str]:
    loader = DirectoryLoader(data_dir, glob=file_glob, loader_cls=loader_cls)
    docs = loader.load()
    if file_name is not None:
        history_docs = [doc for doc in docs if file_name in doc.metadata["source"]]
    else:
        history_docs = docs
    return [json.loads(doc.page_content) for doc in history_docs]

def load_and_parse_chat_history_from_json(
        file_path: str = 'data/chat.json'):
    loader = JSONLoader(file_path=file_path)
    #content_key='messages.content'
    # jq_schema='.messages[].content',

    return loader.load()

def get_chat_messages_from_strings(strings):
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

def on_bot_behavior_change():
    global currentBotBehavior
    currentBotBehavior = st.session_state.currentBotBehavior

def on_load_chat_from_file_btn_click():
    filename = st.session_state.filename
    if(filename is None or filename == ""):
        filename = "chat.json"
    if(filename.startswith("data/")):
        filename = filename.removeprefix("data/")
    jsonDocs = load_json_from_documents("data", "**/*.json", filename)
    firstJson = jsonDocs[0]
    chat_history = firstJson['chat_history']
    setChatHistoryInSession(chat_history)

def on_save_to_file_btn_click():
    content = {
        "botBehavior": st.session_state.currentBotBehavior,
        "chat_history": getChatHistoryFromSession(),
    }
    filename = st.session_state.filename
    if(filename is None or filename == ""):
        filename = "data/chat.json"
    if(not filename.startswith("data/")):
        filename = "data/" + filename
    file = open(filename, "w")
    file.write(toJson(content))
    file.close()

def on_clear_chat_btn_click():
    st.session_state.botBehavior = botBehavior
    clearChatHistoryInSession()

def on_input_change():
    responseObj = get_response_with_memory(st.session_state.userInput)
    text = responseObj["text"]
    response = responseObj["response"]
    messages = st.session_state.chat_history['messages']
    messages.append(getInternalMessageForUser("Human", text))
    messages.append(getInternalMessageForUser("Bot", response))
    st.session_state.userInput = ""

def main():
    initGlobals()
    initChatSession()

    st.set_page_config(page_title="FlirtBot", page_icon=":robot:")

    st.header("FlirtBot - Chat with a flirt master!")
    st.text_area("Bot Behavior:", key="currentBotBehavior", on_change=on_bot_behavior_change)
    st.text_input("Enter your name:", key="userName")

    with st.sidebar:
        st.subheader("Commands")
        # use file uploader later for RAG system
        # st.file_uploader("Upload a file", type=["txt"], key="fileUploader")
        st.button("Clear Chat History", key="clearChatHistory", on_click=on_clear_chat_btn_click)
        st.text_input("Filename:", key="filename")
        st.button("Load From File", key="loadFromFile", on_click=on_load_chat_from_file_btn_click)
        st.button("Save To File", key="saveToFile", on_click=on_save_to_file_btn_click)

    chat_placeholder = st.container()

    with chat_placeholder.container():
        chatHistoryDict = getChatHistoryFromSession()
        for i in range(len(chatHistoryDict['messages'])):
            ding = chatHistoryDict['messages'][i]
            is_user = ding['user'] == "Human"
            if (is_user): 
                key = f"{i}_user" 
            else : 
                key = f"{i}"
            message(ding['content'], is_user=is_user, key=key)

    with st.container():
        st.text_input("User Input:", on_change=on_input_change, key="userInput")

if __name__ == '__main__':
    main()

# if not hasattr(st, 'already_started_server'):
    # Hack the fact that Python modules (like st) only load once to
    # keep track of whether this file already ran.
    # st.already_started_server = True
    # server_app.run(port=5000)