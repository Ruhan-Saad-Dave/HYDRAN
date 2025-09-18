import os
from langchain.text_splitter import CharacterTextSplitter 
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma 
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

current_dir = os.path.dirname(os.path.abspath(__file__)) #define directory containing the text file 
file_path = os.path.join(current_dir, "books", "odyssey.txt")
persistent_directory = os.path.join(current_dir, "db", "chroma_db")

#check if vector store already exists 
if not os.path.exists(persistent_directory):
    print("Persistent directory not exist. Initializing vector store...")

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"File not found: {file_path}. Please ensure the file exists."
        )
    
    loader = TextLoader(file_path) 
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0)
    docs = text_splitter.split_documents(documents)

    print("\n--- Document Chunks Information ---")
    print(f"Number of document chunks: {len(docs)}")
    print(f"Sample chunk:\n{docs[0].page_content}\n")

    print("\n--- Creating embeddings ---")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    print("\n--- Creating vector store ---")
    db = Chroma.from_documents(
        docs, embeddings, persist_directory=persistent_directory
    )

else:
    print("Vector store already exists. Skipping initialization.")