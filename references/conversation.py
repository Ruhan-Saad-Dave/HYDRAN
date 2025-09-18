# conversation with history between human and ai

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")

messages = [
    SystemMessage(content="You are a symptom checker. The user will describe their symptoms, and you need to tell the illness the user has akong with the precausions. There might be a case where for the same symptom there can be multiple illness, in that case list all the possible illness along with the missing symptom.")
]

while True:
    user = input("You: ")
    if user.lower() in ["exit", "quit"]:
        break
    messages.append(HumanMessage(content=user))
    if len(messages) > 6:
        messages.pop(0)
    response = llm.invoke(messages)
    messages.append(AIMessage(content = response.content))
    print("AI: ", response.content)
