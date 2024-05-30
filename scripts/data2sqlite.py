import sqlite3
import csv
from langchain_community.retrievers import *
import os

# Conectar a la base de datos (creará una nueva si no existe)
conn = sqlite3.connect("heart_data.db")
cursor = conn.cursor()

# Crear la tabla con la estructura adecuada
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS heart_disease (
        age FLOAT,
        sex TEXT,
        cp TEXT,
        trestbps FLOAT,
        chol FLOAT,
        fbs TEXT,
        restecg TEXT,
        thalach FLOAT,
        exang TEXT,
        oldpeak FLOAT,
        slope TEXT,
        ca FLOAT,
        thal TEXT,
        target TEXT
    )
    """
)

conn.commit()


# Función para convertir números a palabras según las claves proporcionadas
def convertir_numeros_a_palabras(fila):
    sex = "male" if fila[1] == 1 else "female"
    cp = (
        "angina"
        if fila[2] == 1
        else "abnang" if fila[2] == 2 else "notang" if fila[2] == 3 else "asympt"
    )
    fbs = "true" if fila[5] == 1 else "false" if fila[5] == 0 else None
    restecg = (
        "norm"
        if fila[6] == 0
        else "abn" if fila[6] == 1 else "hyper" if fila[6] == 2 else None
    )
    exang = "true" if fila[8] == 1 else "false" if fila[8] == 0 else None
    slope = (
        "up"
        if fila[10] == 1
        else "flat" if fila[10] == 2 else "down" if fila[10] == 3 else None
    )
    thal = (
        "norm"
        if fila[12] == 3
        else "fixed" if fila[12] == 6 else "rever" if fila[12] == 7 else None
    )
    clase = "buff" if fila[13] == 0 else "sick" if fila[13] == 1 else None

    # Reemplazar los valores "?" con None
    fila = [val if val != "?" else None for val in fila]

    return [
        fila[0],
        sex,
        cp,
        fila[3],
        fila[4],
        fbs,
        restecg,
        fila[7],
        exang,
        fila[9],
        slope,
        fila[11],
        thal,
        clase,
    ]


def save_csv(file):
    # Leer el archivo CSV y cargar los datos en la base de datos
    with open(file, "r") as f:
        reader = csv.reader(f, delimiter=",")

        # Iniciar una transacción
        conn.execute("BEGIN TRANSACTION")

        for line in reader:
            # Ignorar líneas de comentarios
            if line[0].startswith("%"):
                continue

            # Convertir los valores numéricos a palabras
            converted_row = convertir_numeros_a_palabras(
                [float(val) if val.replace(".", "").isdigit() else val for val in line]
            )

            # Insertar los datos en la tabla
            cursor.execute(
                """
                INSERT INTO heart_disease (age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, target)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                converted_row,
            )

        # Finalizar la transacción
        conn.commit()

    conn.close()


# data/heart/processed.cleveland.data to table heart_disease
# data/heart/processed.hungarian.data to table heart_disease_hungarian
# csv_file = "data/heart/processed.hungarian.data"

for file in os.listdir("data/heart"):
    if file.endswith(".data") and file.startswith("processed."):
        csv_file = os.path.join("data/heart", file)
        break
save_csv(csv_file)
