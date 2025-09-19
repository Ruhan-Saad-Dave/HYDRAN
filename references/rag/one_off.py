import os 

from dotenv import load_dotenv 
from langchain_community.vectorstores import Chroma 
from langchain_core.messages import HumanMessage, SystemMessage 
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings 

load_dotenv() 

current_dir = os.path.dirname(os.path.abspath(__file__))
persistent_directory = os.path.join( 
    current_dir, "db", "chroma_db_with_metadata"
) 

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001") 

db = Chroma(persist_directory=persistent_directory, embedding_function=embeddings)

query = "How to win?"

retriever = db.as_retriever( 
    search_type = "similarity", 
    search_kwargs={"k" : 1},
)
relevant_docs = retriever.invoke(query) 

print("\n--- Relevant Documents ---") 
for i, doc in enumerate(relevant_docs, 1):
    print(f"Document {i}:\n{doc.page_content}\n")

combined_input = (
    "here are some documents that might hekp answer the question: "
    + query
    + "\n\nRelevant Documents:\n"
    + "\n\n".join([doc.page_content for doc in relevant_docs])
    + "\n\nPlease provide an answer based inly on the provided documents."
)

model = GoogleGenerativeAI(model="models/gemini-1.5-flash") 

messages = [
    SystemMessage(
        content="You are a helpful assistant that helps people find information."
    ),
    HumanMessage(content=combined_input),
]

response = model.invoke(messages) 
print(response.content)