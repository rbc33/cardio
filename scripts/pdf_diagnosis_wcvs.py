# %%
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.ollama import OllamaEmbeddings
from langchain_community.vectorstores.chroma import Chroma

doc_path = "data/oxford-handbook-of-cardiology-2nbsped-9780199643219_compress.pdf"
ollama_url = "http://192.168.0.100:11434"
base_url = "http://192.168.0.100:8000/v1"
chroma_path = "chroma_db/diad_man"

loader = PyPDFLoader(doc_path)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
texts = text_splitter.split_documents(docs)

ollama_embeddings = OllamaEmbeddings(model="mxbai-embed-large", base_url=ollama_url)

diagnosis_db = Chroma.from_documents(
    texts, ollama_embeddings, persist_directory=chroma_path
)

# %%
chroma_path = "chroma_db/heart_disease"

db_loader = CSVLoader(
    file_path="heart_disease.csv",
    csv_args={
        "delimiter": ",",
        "quotechar": '"',
        "fieldnames": [
            "age",
            "sex",
            "cp",
            "trestbps",
            "chol",
            "fbs",
            "restecg",
            "thalach",
            "exang",
            "oldpeak",
            "slope",
            "ca",
            "thal",
            "target",
        ],
    },
)

loader = db_loader.load()
heart_db = Chroma(
    collection_name="heart_disease",
    embedding_function=ollama_embeddings,
    persist_directory=chroma_path,
)
# %%
question = "What is the main diagnosis of the patient?"
from langchain_community.llms.openai import OpenAI
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

llm = OpenAI(base_url=base_url, temperature=0)

qa_chain = RetrievalQA.from_chain_type(llm, retriever=diagnosis_db.as_retriever())
result = qa_chain({"query": question})
print(result["result"])
