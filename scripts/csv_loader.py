### # ! /Users/ric/Library/Caches/pypoetry/virtualenvs/langchainpy-sRw7hIgd-py3.11/bin/python
# %%
import lark
from langchain_openai import OpenAI
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain_community.embeddings.openai import OpenAIEmbeddings

# %%
import os

os.environ["TOKENIZERS_PARALLELISM"] = "true"

# %%

embedings = OllamaEmbeddings(
    base_url="http://192.168.0.100:11434", model="mxbai-embed-large"
)
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

# %%
# loader = db_loader.load()
# heart_db = Chroma.from_documents(
#     documents=loader,
#     collection_name="heart_disease",
#     embedding=embedings,
#     persist_directory=chroma_path,
# )

# %%
heart_db = Chroma(
    collection_name="heart_disease",
    embedding_function=embedings,
    persist_directory=chroma_path,
)
# %%
question = "for what could be usefull this data, or conexion with values that indicates a heart malfunction?"
# %%
docs_ss = heart_db.similarity_search(query=question, k=50)
if docs_ss:
    print(len(docs_ss))
    for doc in docs_ss:
        print(doc.metadata)
        print(doc.page_content)

# %%
docs_mmr = heart_db.max_marginal_relevance_search(question, k=50)
if docs_mmr:
    print(len(docs_mmr))
    for doc in docs_mmr:
        print(doc.metadata)
        print(doc.page_content)

# %%
base_url = "http://192.168.0.100:8000/v1"
openai_api_key = "deez-nuts"

llm = OpenAI(base_url=base_url, openai_api_key=openai_api_key, temperature=0)

# %%
qa_chain = RetrievalQA.from_chain_type(llm, retriever=heart_db.as_retriever())
result = qa_chain({"query": question})
print(result["result"])

# %%
metadata_field_info = [
    AttributeInfo(
        name="source",
        description="data from patients with cardiovascular diseases",
        type="string",
    ),
]


# %%
content = "anonimous data from heart diseases patients"
retriever = SelfQueryRetriever.from_llm(
    llm,
    heart_db,
    content,
    metadata_field_info=metadata_field_info,
    embedding_function=embedings,
)

docs = retriever.get_relevant_documents(
    {"query": question, "filter": "heart_disease.csv"},
    k=100,
    # type="mmr"
)

# %%
small_db = Chroma.from_documents(
    documents=docs,
    embedding=embedings,
)
small_sum_db = Chroma.from_documents(
    documents=docs_mmr + docs_ss,
    embedding=embedings,
)
for doc in docs:
    print(doc.metadata)
    print(doc.page_content)
    print("---")

# %%
# qa_chain = RetrievalQA.from_chain_type(llm, retriever=small_db.as_retriever())
qa_chain = RetrievalQA.from_chain_type(llm, retriever=heart_db.as_retriever())
question = (
    "acording to this data whats the average age of a person with heart disiases?"
)
result = qa_chain({"query": question})

# %%
print(result["result"])

# %%
qa_chain = RetrievalQA.from_chain_type(llm, retriever=heart_db.as_retriever())
# qa_chain = RetrievalQA.from_chain_type(llm, retriever=small_db.as_retriever())
# qa_chain = RetrievalQA.from_chain_type(llm, retriever=small_sum_db.as_retriever())
question = (
    "whats the most common symptoms related with cardiopaties acording to the data?"
)
result = qa_chain({"query": question})


# %%
print(result["result"])


# %%
print(len(docs_mmr))
# %%
qa_chain = RetrievalQA.from_chain_type(llm, retriever=heart_db.as_retriever())
question = f"whats the most porobably diagnostic for this case {docs_mmr}?"
result = qa_chain({"query": question})
print(result["result"])

# %%
qa_chain = RetrievalQA.from_chain_type(llm, retriever=heart_db.as_retriever())
question = f"whats are the most porobably disease for this case {docs_mmr[0]}, firt about hear diseases, the general?"
result = qa_chain({"query": question})
print(f"datos: {docs_mmr[0]}")
print(result["result"])


# %%
qa_chain = RetrievalQA.from_chain_type(llm, retriever=small_db.as_retriever())
question = f"whats are the most porobably disease for this case {docs_mmr[0:15]}, firt about hear diseases, the general?"
result = qa_chain({"query": question})
print(f"datos: {docs_mmr[0]}")
print(result["result"])

# %%
