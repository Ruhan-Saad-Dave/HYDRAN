import os 

from langchain.text_splitter import CharacterTextSplitter 
from langchain_community.document_loaders import TextLoader 
from langchain_community.vectorstores import Chroma 
from langchain_google_genai import GoogleGenerativeAIEmbeddings 

current_dir = os.path.dirname(os.path.abspath(__file__))
books_dir = os.path.join(current_dir, "books")
db_dir = os.path.join(current_dir, "db")
persistent_directory = os.path.join(db_dir, "chroma_db_with_metadata")

print(f"Books directory: {books_dir}")
print(f"Persistent directory: {persistent_directory}")

if not os.path.exists(persistent_directory):
    print("Persistent directory does not exist. Initializing vector store...")

    if not os.path.exists(books_dir):
        raise FileNotFoundError(
            f"The directory {books_dir} does not exist. Please check the path."
        )
    
    book_files = [f for f in os.listdir(books_dir) if f.endswith(".txt")]

    documents = [] 
    for book_file in book_files:
        file_path = os.path.join(books_dir, book_file) 
        loader = TextLoader(file_path)
        book_docs = loader.load() 
        for doc in book_docs:
            doc.metadata ={"source": book_file}
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