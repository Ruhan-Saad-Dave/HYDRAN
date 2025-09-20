import os
import glob
from dotenv import load_dotenv
from supabase import create_client, Client
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_google_community import GoogleSearchAPIWrapper
from langchain.tools.retriever import create_retriever_tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# --- Configuration & Setup ---
api_key = os.getenv("GOOGLE_API_KEY")
cse_id = os.getenv("GOOGLE_CSE_ID")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")
if not cse_id:
    print("WARNING: GOOGLE_CSE_ID not set. Web search functionality will be disabled.")
    cse_id = None
if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables not set.")

# --- Supabase Client ---
supabase: Client = create_client(supabase_url, supabase_key)

# --- Knowledge Base Loading ---
def load_and_index_documents():
    # Define a folder to store the FAISS index
    script_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(script_dir, "faiss_index")

    print("Initializing local embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Check if the index already exists
    if os.path.exists(index_path):
        print(f"Loading existing FAISS index from {index_path}")
        vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        print("FAISS index loaded successfully.")
    else:
        print("No existing FAISS index found. Building a new one...")
        documents = []
        # Construct path to 'data' directory relative to this script file
        data_dir = os.path.join(script_dir, 'data')
        
        if not os.path.exists(data_dir) or not os.path.isdir(data_dir):
            print(f"Directory '{data_dir}' not found. Please create it and add your CSV files.")
            return None

        csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
        if not csv_files:
            print(f"No CSV files found in '{data_dir}'.")
            return None

        for file_path in csv_files:
            print(f"Loading data from: {file_path}")
            loader = CSVLoader(file_path=file_path)
            docs = loader.load()
            documents.extend(docs)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = text_splitter.split_documents(documents)

        vectorstore = FAISS.from_documents(split_docs, embeddings)
        print("Knowledge base created successfully.")
        
        print(f"Saving new FAISS index to {index_path}")
        vectorstore.save_local(index_path)
        print("FAISS index saved.")
    
    return vectorstore.as_retriever()

# --- Chat History Management ---
def get_chat_history(session_id: str):
    """Retrieves chat history from Supabase."""
    try:
        data = supabase.table("chat_history").select("history").eq("session_id", session_id).execute()
        if data.data:
            return data.data[0]['history']
        return []
    except Exception as e:
        print(f"Error getting chat history: {e}")
        return []

def update_chat_history(session_id: str, query: str, response: str):
    """Updates chat history in Supabase, keeping only the last 10 messages."""
    try:
        result = supabase.table("chat_history").select("history").eq("session_id", session_id).execute()
        
        new_message = {"human": query, "ai": response}
        
        if result.data:
            history = result.data[0]['history'] or []
            history.append(new_message)
            history = history[-10:]
            supabase.table("chat_history").update({"history": history}).eq("session_id", session_id).execute()
        else:
            history = [new_message]
            supabase.table("chat_history").insert({"session_id": session_id, "history": history}).execute()
            
    except Exception as e:
        print(f"Error updating chat history: {e}")

# --- Main Logic ---
def get_symptom_checker_response(session_id: str, query: str):
    """Main function to run the RAG agent."""
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)

    print("--- Performing LLM Health Check ---")
    try:
        health_check_response = llm.invoke("Hello, world!")
        print("--- LLM Health Check Passed. Response: ---")
        print(health_check_response)
        print("------------------------------------")
    except Exception as e:
        print(f"--- LLM Health Check FAILED: {e} ---")
        return "Error: Could not connect to the language model. Please check your GOOGLE_API_KEY and network connection."

    retriever = load_and_index_documents()

    tools = []
    if retriever:
        local_db_tool = create_retriever_tool(
            retriever,
            "local_knowledge_base",
            "Searches and returns documents about information present in the local CSV files."
        )
        tools.append(local_db_tool)

    if cse_id:
        search = GoogleSearchAPIWrapper()
        web_search_tool = Tool(
            name="google_search",
            description="Use this tool to search the internet for up-to-date information. "
                        "It is a fallback to be used only if the local_knowledge_base does not contain a relevant answer.",
            func=search.run
        )
        tools.append(web_search_tool)

    if not tools:
        return "No tools available. Please check the configuration."

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are an AI Symptom Checker. Your primary goal is to indentify the illness and precausions for it based on the "
             "symptom mentioned by the user. You MUST use the 'local_knowledge_base' tool to find information about symptoms and diseases. "
             "If and only if the 'local_knowledge_base' returns no relevant information, you MUST then use the 'google_search' tool. "
             "Do not answer health-related queries from your own internal knowledge. Always cite the source of your information."),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    raw_history = get_chat_history(session_id)
    chat_history = []
    for record in raw_history:
        if record.get("human"):
            chat_history.append(HumanMessage(content=record["human"]))
        if record.get("ai"):
            chat_history.append(AIMessage(content=record["ai"]))

    try:
        response = agent_executor.invoke({"input": query, "chat_history": chat_history})
        ai_response = response["output"]
        update_chat_history(session_id, query, ai_response)
        return ai_response

    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while processing your request."