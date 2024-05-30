### # ! /Users/ric/Library/Caches/pypoetry/virtualenvs/langchainpy-sRw7hIgd-py3.11/bin/python
# %%
import lark
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

# %%
import os
import openai
import sys

# sys.path.append("../..")

# from dotenv import load_dotenv, find_dotenv

# _ = load_dotenv(find_dotenv())  # read local .env file

# openai.api_key = os.environ["OPENAI_API_KEY"]

os.environ["TOKENIZERS_PARALLELISM"] = "true"
openai_api_key = "deezs"

# %%
ollama_url = "http://192.168.0.100:11434"
emb_model = "mxbai-embed-large"
embedings = OllamaEmbeddings(base_url=ollama_url, model=emb_model)
chroma_path = "chroma_db/heart_disease_openAI"

# %%
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

# # # %%# %%
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor


# %%
def pretty_print_docs(docs):
    print(
        f"\n{'-' * 100}\n".join(
            [f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]
        )
    )


# %%
# Wrap our vectorstore
# llm = Ollama(base_url=base_url, model=ollama_model, temperature=0)
compressor = LLMChainExtractor.from_llm(llm)

# %%
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=vectordb.as_retriever()
)

# %%
question = "what did they say about matlab?"
compressed_docs = compression_retriever.get_relevant_documents(question)
pretty_print_docs(compressed_docs)

# %% [markdown]
# ## Combining various techniques

# %%
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=vectordb.as_retriever(search_type="mmr")
)

# %%
question = "what did they say about matlab?"
compressed_docs = compression_retriever.get_relevant_documents(question)
pretty_print_docs(compressed_docs)

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

llm_url = "http://192.168.0.100:8000/v1"
llm = OpenAI(openai_api_key=openai_api_key, base_url=llm_url, temperature=0)

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
import lark

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
docs = retriever.get_relevant_documents(
    {"query": question, "filter": "heart_disease.csv"},
    k=100,
    # type="mmr"
)
small_db = Chroma.from_documents(
    documents=docs,
    embedding=embedings,
)

# %%
docs = retriever.get_relevant_documents(
    {"query": question, "filter": "heart_disease.csv"},
    k=100,
    # type="mmr"
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
question = f"whats are the most porobably disease for this case {docs_mmr}, firt about hear diseases, the general?"
result = qa_chain({"query": question})
print(f"datos: {docs_mmr[0]}")
print(result["result"])


# %%
qa_chain = RetrievalQA.from_chain_type(llm, retriever=small_db.as_retriever())
question = f"whats are the most porobably disease for this case {docs_mmr}, firt about hear diseases, the general?"
result = qa_chain({"query": question})
print(f"datos: {docs_mmr[0]}")
print("small_db", result["result"])

# %%
qa_chain = RetrievalQA.from_chain_type(llm, retriever=small_sum_db.as_retriever())
question = f"whats are the most porobably disease for this case {docs_mmr}, firt about hear diseases, the general?"
result = qa_chain({"query": question})
print(f"datos: {docs_mmr[0]}")
print("small_sum_db", result["result"])

# %%
# %%
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor


# %%
def pretty_print_docs(docs):
    print(
        f"\n{'-' * 100}\n".join(
            [f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]
        )
    )


# %%
# Wrap our vectorstore
# llm = Ollama(base_url=base_url, model=ollama_model, temperature=0)
compressor = LLMChainExtractor.from_llm(llm)

# %%
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=heart_db.as_retriever()
)

# %%
question = "what did they say about matlab?"
compressed_docs = compression_retriever.get_relevant_documents(question)
pretty_print_docs(compressed_docs)


# %%
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=heart_db.as_retriever(search_type="mmr")
)

# %%
question = "what did they say about matlab?"
compressed_docs = compression_retriever.get_relevant_documents(question)
pretty_print_docs(compressed_docs)

# %%
