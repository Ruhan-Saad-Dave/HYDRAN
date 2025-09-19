import os
import glob
from dotenv import load_dotenv

# LangChain components
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_google_community import GoogleSearchAPIWrapper
from langchain.tools.retriever import create_retriever_tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables from a .env file
load_dotenv()

# --- Configuration & Setup ---
# Set up your API keys from environment variables.
# GOOGLE_API_KEY is still needed for the Gemini-Pro LLM.
# You need to have GOOGLE_CSE_ID set for web search functionality.
# If you don't have it, web search will be disabled.

api_key = os.getenv("GOOGLE_API_KEY")
cse_id = os.getenv("GOOGLE_CSE_ID")

if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")
if not cse_id:
    print("WARNING: GOOGLE_CSE_ID not set. Web search functionality will be disabled.")
    cse_id = None

# --- Knowledge Base Loading ---
# This function loads all CSV files, splits them, and uses a local model for embeddings.
def load_and_index_documents():
    """Loads CSV files, splits them into chunks, and creates a vector store."""
    documents = []
    data_dir = "./data"
    
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

    # Split documents into chunks for better retrieval
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)

    # Use a local, open-source embedding model from Hugging Face
    # 'all-MiniLM-L6-v2' is a good, fast, and light model for many tasks.
    # The model will be downloaded automatically the first time you run the script.
    print("Initializing local embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create an in-memory vector store (FAISS)
    vectorstore = FAISS.from_documents(split_docs, embeddings)
    print("Knowledge base created successfully.")
    
    return vectorstore.as_retriever()

# --- Main Logic ---
def main():
    """Main function to run the RAG agent."""
    
    # 1. Set up the LLM (requires an API key for Google's service)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)

    # 2. Set up the local knowledge base retriever
    retriever = load_and_index_documents()

    # 3. Define the tools for the agent
    tools = []
    if retriever:
        # Tool for the local knowledge base
        local_db_tool = create_retriever_tool(
            retriever,
            "local_knowledge_base",
            "Searches and returns documents about information present in the local CSV files."
        )
        tools.append(local_db_tool)

    if cse_id:
        # Tool for Google web search
        search = GoogleSearchAPIWrapper()
        web_search_tool = Tool(
            name = "google_search",
            description="Use this tool to search the internet for up-to-date information. "
                        "It is a fallback to be used only if the local_knowledge_base does not contain a relevant answer.",
            func=search.run
        )
        tools.append(web_search_tool)

    if not tools:
        print("No tools available. Exiting.")
        return

    # 4. Define the agent's prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", 
             "You are a helpful assistant. Your primary goal is to answer questions based on the "
             "provided tools. First, try to use the 'local_knowledge_base' to find the answer. "
             "If the local database does not contain relevant information, use the 'google_search' "
             "tool to find the answer on the web. Always show the source of your information."),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    # 5. Create the agent and executor
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # 6. User interaction loop
    while True:
        question = input("\nAsk a question (or type 'exit' to quit): ")
        if question.lower() == 'exit':
            break
        
        try:
            response = agent_executor.invoke({"input": question})
            print("\n" + "="*50)
            print("Final Answer:")
            print(response["output"])
            print("="*50)

        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
