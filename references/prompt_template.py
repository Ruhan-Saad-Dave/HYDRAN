from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage 

'''
template = "tell me a {type} story about {topic}"
prompt_template = ChatPromptTemplate.from_template(template)

prompt = prompt_template.invoke({"type": "horror","topic": "cats"})
print(prompt)
'''

#with system and human
messages = [
    ("system", "You are a comedian who tells jokes about {topic}."),
    ("human", "Tell me {joke_count} jokes"), #using HumanMessage(content="Tell me 3 jokes") also works, but {jokes_count} wont be replaced
]
prompt_template = ChatPromptTemplate.from_messages(messages)
prompt = prompt_template.invoke({"topic": "lawyers", "joke_count": 3})
print(prompt.messages[1].content)
#model.invoke(prompt)