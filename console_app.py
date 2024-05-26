import os
import openai
import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# Laden der Umgebungsvariablen
dotenv.load_dotenv()
# Initialisieren der API-Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialisieren des Sprachmodells
llm = ChatOpenAI(model="gpt-4", temperature=0.9)

# Initialisieren des OutputParsers
output_parser = StrOutputParser()

# Initialisieren des Chains
chain = llm | output_parser

def conversation():
    print("Willkommen beim LangChain-gesteuerten Chatbot!")
    while True:
        user_input = input("Du: ")
        if user_input.lower() == "exit":
            break
        response = chain.invoke(user_input)
        print(f"Bot: {response}")

conversation()