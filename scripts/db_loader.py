from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("sqlite:///heart_data.db")
print(db.dialect)
print(db.get_usable_table_names())
# db.run("SELECT * FROM heart_disease ") # cleveland

query = db.run("SELECT * FROM heart_disease_hungarian")
print(type(query))
print(len(query))
print(query)

if isinstance(query, list):
    print("Número de entradas devueltas:", len(query))
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI

base_url = "http://192.168.0.100:8000/v1"
openai_api_key = "deez-nuts"

llm = ChatOpenAI(base_url=base_url, openai_api_key=openai_api_key, temperature=0)
agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)
# db_exp = """ Attributes: 8 symbolic, 6 numeric.
# Age; sex; chest pain type (angina, abnang, notang, asympt)
# Trestbps (resting blood pres); cholesteral; fasting blood sugar < 120
# (true or false); resting ecg (norm, abn, hyper); max heart rate;
# exercise induced angina (true or false); oldpeak; slope (up, flat, down)
# number of vessels colored (???); thal (norm, fixed, rever). Finally, the
# class is either healthy (buff) or with heart-disease (sick)."""

# agent_executor.invoke("what is the most common symptom in heart_disease_hungarian")
agent_executor.invoke("how many records and tables are in the db")
