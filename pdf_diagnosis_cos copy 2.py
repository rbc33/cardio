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

# %%
patient1 = """Patient 1
Age: 62 years
Gender: Male
Family History: No known history
Smoking Status: Ex-smoker (quit 10 years ago)
BMI (Body Mass Index): 27 kg/m²
Blood Pressure: 140/85 mmHg
Total Cholesterol: 220 mg/dL
LDL Cholesterol: 140 mg/dL
HDL Cholesterol: 45 mg/dL
Triglycerides: 150 mg/dL
Fasting Glucose: 98 mg/dL
Physical Activity: Moderately active
Symptoms: Occasional chest discomfort, fatigue
ECG: Minor nonspecific ST changes
Echocardiogram: Mild left ventricular hypertrophy"""
patient2 = """Patient 2
- **Age:** 45 years
- **Gender:** Female
- **Family History:** Mother with hypertension
- **Smoking Status:** Non-smoker
- **BMI (Body Mass Index):** 24 kg/m²
- **Blood Pressure:** 115/75 mmHg
- **Total Cholesterol:** 190 mg/dL
- **LDL Cholesterol:** 110 mg/dL
- **HDL Cholesterol:** 55 mg/dL
- **Triglycerides:** 80 mg/dL
- **Fasting Glucose:** 90 mg/dL
- **Physical Activity:** Regular exercise (3-4 times per week)
- **Symptoms:** None relevant
- **ECG:** Normal
- **Echocardiogram:** Normal"""
patient3 = """### Patient 3
- **Age:** 50 years
- **Gender:** Male
- **Family History:** Father had a heart attack at 65
- **Smoking Status:** Current smoker (10 cigarettes/day)
- **BMI (Body Mass Index):** 30 kg/m²
- **Blood Pressure:** 150/95 mmHg
- **Total Cholesterol:** 240 mg/dL
- **LDL Cholesterol:** 150 mg/dL
- **HDL Cholesterol:** 40 mg/dL
- **Triglycerides:** 200 mg/dL
- **Fasting Glucose:** 110 mg/dL
- **Physical Activity:** Sedentary
- **Symptoms:** Shortness of breath, occasional palpitations
- **ECG:** ST depression in lateral leads
- **Echocardiogram:** Left ventricular hypertrophy, mild mitral regurgitation"""
question = f"""what is the probability for this patient {patient1}
to have a cardiovascular disease, and what disease it would be?"""

# %%
# from langchain_openai import OpenAI
# from langchain.chains.retrieval_qa.base import RetrievalQA
# from langchain.retrievers.self_query.base import SelfQueryRetriever
# from langchain.chains.query_constructor.base import AttributeInfo

# llm = OpenAI(base_url=base_url, api_key="no", temperature=0)

# qa_chain = RetrievalQA.from_chain_type(llm, retriever=diagnosis_db.as_retriever())
# result = qa_chain({"query": question})
# print(result["result"])
# %%
from langchain_openai import OpenAI
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

llm = OpenAI(base_url=base_url, api_key="no", temperature=0)

qachain = RetrievalQA.from_chain_type(llm, retriever=diagnosis_db.as_retriever())
response = qachain.invoke({"query": question})
print("question: ", question)
print("--------------------------------------")
print("response: ", response["result"])
