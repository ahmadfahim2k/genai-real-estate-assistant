from uuid import uuid4

from dotenv import load_dotenv

from pathlib import Path

from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

from chains import RetrievalQAWithSourcesChain

from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()

# constants
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
LLM = 'llama-3.1-8b-instant'
COLLECTION_NAME = 'real_estate'
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
VECTORSTORE_DIR = Path(__file__).parent / "resources/vectorstore"

# ------------------------------------------

# global

llm = None
vector_store = None

# --------------------------------------------

def initialize_components():
    
    global llm, vector_store
    
    if llm is None:
        llm = ChatGroq(model=LLM, temperature=0.9, max_tokens=500)
    
    if vector_store is None:
        ef = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            encode_kwargs={"normalize_embeddings": True, "batch_size": 4},
        )
        
        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=ef,
            persist_directory=str(VECTORSTORE_DIR)
        )

def process_urls(urls):
    """
    This function scraps from the urls and stores it in vector db
    :param urls: input urls
    :return:
    """
    
    yield "Initialize components"
    initialize_components()
    
    yield "Resetting vector store"
    vector_store.reset_collection()
    
    yield "Loading Data"
    loader = WebBaseLoader(urls)
    data = loader.load()    
    
    yield "Chunking documents"
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " "],
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    docs = text_splitter.split_documents(data)
    
    yield "Adding documents to vector store"
    uuids = [str(uuid4()) for _ in range(len(docs))]
    vector_store.add_documents(docs, ids=uuids)
    
    yield "Done adding docs to vector store"

def generate_answer(query):
    if not vector_store:
        raise RuntimeError("Vector DB is not initialized")
    initialize_components()
    chain = RetrievalQAWithSourcesChain(llm, vector_store)
    result = chain.invoke(query)
    answer = result["answer"]
    sources = result["sources"]
    return (answer, sources)

if __name__ == "__main__":
    urls = [
        "https://www.cnbc.com/2024/12/21/how-the-federal-reserves-rate-policy-affects-mortgages.html",
        "https://www.cnbc.com/2026/01/09/heres-whats-happening-now-with-mortgage-rates-.html",
        "https://www.cnbc.com/2024/12/20/why-mortgage-rates-jumped-despite-fed-interest-rate-cut.html",
    ]
    
    process_urls(urls)

    myQuery = "What was the 30 year fixed mortgage rate along with the date?"
    (answer, sources) = generate_answer(myQuery)

    print(f"Answer: {answer}")
    print(f"Sources: {sources}")