# %%
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.vectorstores.chroma import Chroma

doc_path = "data/oxford-handbook-of-cardiology-2nbsped-9780199643219_compress.pdf"
ollama_url = "http://192.168.0.100:11434"
base_url = "http://192.168.0.100:8000/v1"
chroma_path = "chroma_db/diad_man"
ollama_embeddings = OllamaEmbeddings(model="mxbai-embed-large", base_url=ollama_url)

# %%
# loader = PyPDFLoader(doc_path)
# docs = loader.load()

# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
# texts = text_splitter.split_documents(docs)


# %%

# diagnosis_db = Chroma.from_documents(
#     texts,
#     ollama_embeddings,
#     persist_directory=chroma_path,
#     collection_metadata={"hnsw:space": "cosine"},
# )

# %%
diagnosis_db = Chroma(
    embedding_function=ollama_embeddings,
    persist_directory=chroma_path,
)

# # %%
# chroma_path = "chroma_db/heart_disease"

# db_loader = CSVLoader(
#     file_path="heart_disease.csv",
#     csv_args={
#         "delimiter": ",",
#         "quotechar": '"',
#         "fieldnames": [
#             "age",
#             "sex",
#             "cp",
#             "trestbps",
#             "chol",
#             "fbs",
#             "restecg",
#             "thalach",
#             "exang",
#             "oldpeak",
#             "slope",
#             "ca",
#             "thal",
#             "target",
#         ],
#     },
# )

# loader = db_loader.load()
# heart_db = Chroma(
#     collection_name="heart_disease",
#     embedding_function=ollama_embeddings,
#     persist_directory=chroma_path,
# )
# %%
question = "What is the most common metric of each heart disease?"
from langchain_community.llms.openai import OpenAI
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

llm = OpenAI(base_url=base_url, api_key="no", temperature=0)

qa_chain = RetrievalQA.from_chain_type(llm, retriever=diagnosis_db.as_retriever())
result = qa_chain({"query": question})
print(result["result"])

# %%
metadata_field_info = [
    AttributeInfo(
        name="page",
        description="The page from the PDF",
        type="int",
    ),
]
# %%
import lark

content = "standard cardiology diagnosis"
retriever = SelfQueryRetriever.from_llm(
    llm,
    diagnosis_db,
    content,
    metadata_field_info=metadata_field_info,
    embedding_function=ollama_embeddings,
)

docs_mmr = retriever.get_relevant_documents(
    {"query": question, "filter": "", "k": 15}, type="mmr"
)

for doc in docs_mmr:
    print(doc)

# %%
for doc in docs_mmr:
    print(doc.page_content)
    print(doc.metadata)
print(len(docs_mmr))

# %%
# Assuming you're setting up a LangChain-based retriever
from langchain.chains.query_constructor.base import AttributeInfo

metadata_field_info = [
    AttributeInfo(
        name="page",
        description="The page from the lecture",
        type="integer",
    ),
]
# %%
# Proper query construction
content = "anonymous data from heart disease patients"
retriever = SelfQueryRetriever.from_llm(
    llm,
    diagnosis_db,
    content,
    metadata_field_info=metadata_field_info,
    embedding_function=ollama_embeddings,
)

# Example of a correct query
question = "What is the most common metric of each heart disease?"
docs_ss = retriever.get_relevant_documents(question, k=25)

for doc in docs_ss:
    print(doc.page_content)
    print(doc.metadata)
print(len(docs_ss))

# %%
