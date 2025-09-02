# import chromadb
# import os
# import time
# import tempfile
# from chromadb.utils import embedding_functions
# from langchain_community.embeddings import HuggingFaceEmbeddings as HFEmbeddings
#  #use the huggingface embeddings.
# # from langchain_chroma import Chroma as LangChainChroma
# # #use the chroma vectorstore
# from langchain_community.vectorstores import Chroma as LangChainChroma

# # def initialize_vectorstore():
# #     # Initialize ChromaDB client with persistence
# #     client = chromadb.PersistentClient(path="vectorized_db")
# #     if client.get_collection(name="iitkgp_data") is None:
# #         print("Collection not found!")

# #     # Create Embedding Function
# #     sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")

# #     # Load the collection
# #     collection = client.get_collection(name="iitkgp_data", embedding_function=sentence_transformer_ef)

# #     # Create LangChain embeddings object (using HuggingFaceEmbeddings to match chromadb embeddings)
# #     embeddings = HFEmbeddings(model_name="all-mpnet-base-v2") #use the huggingface embeddings

# #     # Create LangChain Chroma vectorstore
# #     vectorstore = LangChainChroma(client=client, collection_name="iitkgp_data", embedding_function=embeddings) #use the chroma vectorstore

# #     # Create retriever
# #     retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
# #     return vectorstore, retriever

# def initialize_vectorstore(files=None):
#     # Initialize embeddings (to be used for both default and custom collections)
#     # embeddings = HFEmbeddings(model_name="all-mpnet-base-v2")
#     # sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")
#     embeddings = HFEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

#     # If no files are provided, return the default knowledge base
#     if files is None:
#         # Initialize ChromaDB client with persistence for default knowledge base
#         client = chromadb.PersistentClient(path="vectorized_db")
        
#         # Load the collection
#         # collection = client.get_collection(name="iitkgp_data", embedding_function=sentence_transformer_ef)
        
#         # Create LangChain Chroma vectorstore
#         vectorstore = LangChainChroma(client=client, collection_name="iitkgp_data", embedding_function=embeddings)
        
#         # Create retriever
#         retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
#         return vectorstore, retriever
    
#     # If files are provided, create a temporary vector store
#     else:
#         # Create a temporary directory for the ChromaDB instance
#         temp_db_path = os.path.join(tempfile.gettempdir(), f"temp_db_{int(time.time())}")
#         os.makedirs(temp_db_path, exist_ok=True)
        
#         # Initialize ChromaDB client for the temporary database
#         temp_client = chromadb.PersistentClient(path=temp_db_path)
        
#         # Create a new collection for the uploaded document
#         collection_name = f"uploaded_doc_{int(time.time())}"
#         temp_collection = temp_client.create_collection(name=collection_name, embedding_function=sentence_transformer_ef)
        
#         # Process and load documents
#         from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
        
#         documents = []
#         for file_path in files:
#             file_extension = os.path.splitext(file_path)[1].lower()
            
#             if file_extension == '.txt':
#                 loader = TextLoader(file_path)
#             elif file_extension == '.pdf':
#                 loader = PyPDFLoader(file_path)
#             elif file_extension in ['.docx', '.doc']:
#                 loader = Docx2txtLoader(file_path)
#             else:
#                 continue  # Skip unsupported file types
                
#             documents.extend(loader.load())
        
#         # Split documents into chunks
#         from langchain.text_splitter import RecursiveCharacterTextSplitter
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#         splits = text_splitter.split_documents(documents)
        
#         # Create vectorstore from the loaded documents
#         temp_vectorstore = LangChainChroma.from_documents(
#             documents=splits,
#             embedding=embeddings,
#             client=temp_client,
#             collection_name=collection_name
#         )
        
#         # Create retriever for the temporary vectorstore
#         temp_retriever = temp_vectorstore.as_retriever(search_kwargs={"k": 5})
        
#         return temp_vectorstore, temp_retriever


# # Format documents
# def format_docs(docs):
#     return "\n\n".join(doc.page_content for doc in docs)

# # RAG prompt
# rag_prompt = """You are an assistant for question-answering tasks. 

# Here is the context to use to answer the question:

# {context} 

# Think carefully about the above context. 

# Now, review the user question:

# {question}

# Provide an answer to this questions using only the above context. 

# Use three sentences maximum and keep the answer concise.

# Answer:"""
import os
# Disable TensorFlow/Keras so Transformers never tries to import TF
os.environ["USE_TF"] = "0"

import chromadb
import time
import tempfile
from langchain_community.embeddings import HuggingFaceEmbeddings as HFEmbeddings
from langchain_community.vectorstores import Chroma as LangChainChroma
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def initialize_vectorstore(files=None):
    # Use the same model name that was used to build any existing persisted collection
    embeddings = HFEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    if files is None:
        # Use the persisted default knowledge base
        client = chromadb.PersistentClient(path="vectorized_db")

        # IMPORTANT: use embedding= (LangChain embeddings), not embedding_function=
        vectorstore = LangChainChroma(
            client=client,
            collection_name="iitkgp_data",
            embedding=embeddings,
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
        return vectorstore, retriever

    else:
        # Create a temporary Chroma instance for uploaded files
        temp_db_path = os.path.join(tempfile.gettempdir(), f"temp_db_{int(time.time())}")
        os.makedirs(temp_db_path, exist_ok=True)
        temp_client = chromadb.PersistentClient(path=temp_db_path)

        # Unique collection name for this upload session
        collection_name = f"uploaded_doc_{int(time.time())}"

        # Load documents
        documents = []
        for file_path in files:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".txt":
                loader = TextLoader(file_path)
            elif ext == ".pdf":
                loader = PyPDFLoader(file_path)
            elif ext == ".docx":  # Docx2txtLoader is for .docx, not .doc
                loader = Docx2txtLoader(file_path)
            else:
                continue
            documents.extend(loader.load())

        # Chunk
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)

        # Build the temporary vectorstore (this will internally create the collection)
        temp_vectorstore = LangChainChroma.from_documents(
            documents=splits,
            embedding=embeddings,
            client=temp_client,
            collection_name=collection_name,
        )

        temp_retriever = temp_vectorstore.as_retriever(search_kwargs={"k": 5})
        return temp_vectorstore, temp_retriever


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_prompt = """You are an assistant for question-answering tasks. 

Here is the context to use to answer the question:

{context} 

Think carefully about the above context. 

Now, review the user question:

{question}

Provide an answer to this questions using only the above context. 

Use three sentences maximum and keep the answer concise.

Answer:"""
