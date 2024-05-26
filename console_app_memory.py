import os
import openai
import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory import ChatMessageHistory

dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4", temperature=0.9)

output_parser = StrOutputParser()

# Initialisieren des Chains mit Message Liste
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

chain = prompt | llm | output_parser

# Initialisieren der Chat Historie
chat_history = ChatMessageHistory()

def conversation():
    print("Willkommen beim LangChain-gesteuerten Chatbot! Diesmal mit Gedächtnis!")
    while True:
        user_input = input("Du: ")
        if user_input.lower() == "exit":
            break
        
        chat_history.add_user_message(user_input)
        response = chain.invoke(chat_history.messages)
        chat_history.add_ai_message(response)

        print(f"Bot: {response}")

conversation()