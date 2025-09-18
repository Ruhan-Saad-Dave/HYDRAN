import os 

from langchain.text_splitter import CharacterTextSplitter 
from langchain_community.document_loaders import CSVLoader 
from langchain_community.vectorstores import Chroma 
from langchain_google_genai import GoogleGenerativeAIEmbeddings 
from dotenv import load_dotenv

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, "data")
db_dir = os.path.join(current_dir, "db")
persistent_directory = os.path.join(db_dir, "chroma_db")

print(f"Data directory: {data_dir}")
print(f"Persistent directory: {persistent_directory}")

if not os.path.exists(persistent_directory):
    print("Persistent directory does not exist. Initializing vector store...")

    if not os.path.exists(data_dir):
        raise FileNotFoundError(
            f"The directory {data_dir} does not exist. Please check the path."
        )
    
    data_files = [f for f in os.listdir(data_dir) if f.endswith(".txt")]

    documents = [] 
    for data_file in data_files:
        file_path = os.path.join(data_dir, data_file) 
        loader = CSVLoader(file_path)
        data_docs = loader.load() 
        for doc in data_docs:
            doc.metadata ={"source": data_file}
            documents.append(doc)

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    print("\n--- Document CHunks Information ---")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    print("--- Finished creating embeddings ---")

    db = Chroma.from_documents(
        docs, embeddings, persist_directory = persistent_directory
    )
else: 
    print("Vector store already exists. No need to initialize")