# FlirtBot

This is demo project to show the capabilities of LLM frameworks like LangChain.
The application uses the framework to make a custom chat bot, where the user can chat wit a flirt master.
That so called flirt master could be used as a training playground.

Primary goal:

- nice and flexible chat bot quick exploration of "prompt" engineering.

Secondary goals:

- chat bot can be used as RAG System with any document or link the user provides.

Future goals:

- impersonate and answer with knowledge of the user.
- allow the chat bot to interact with APIs of other services.

# Technologies used:

- Language:
  - Python
- AI-Framework:
  - LangChain (https://github.com/langchain-ai/langchain)
- LLM:
  - OpenAi
- UI:
  - Streamlit
  - Alternative UI solution with html, js, css (not maintained atm.)

# Setting up environment:

- Install Python (https://www.python.org/)
- Install PIP (Run script from "https://bootstrap.pypa.io/get-pip.py" with "py get-pip.py")
  - Upgrade: py -m pip install --upgrade pip
- Install Python packages:
  - pip install openai
  - pip install langchain
  - pip install langchain-openai
  - pip install dotenv
