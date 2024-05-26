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

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability.",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

chain = prompt | llm | output_parser

chat_history_for_chain = ChatMessageHistory()

chain_with_message_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: chat_history_for_chain,
    input_messages_key="input",
    history_messages_key="chat_history",
) | output_parser

def conversation():
    print("Willkommen beim LangChain-gesteuerten Chatbot!")
    while True:
        user_input = input("Du: ")
        if user_input.lower() == "exit":
            break
        response = chain_with_message_history.invoke(
            {"input": {user_input}},
            {"configurable": {"session_id": "unused"}},
        )
        print(f"Bot: {response}")

conversation()