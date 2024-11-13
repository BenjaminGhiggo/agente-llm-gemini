# backend.py

import os
import sqlite3
from dotenv import load_dotenv
import google.generativeai as genai

# Cargar las variables de entorno desde un archivo .env
load_dotenv()

# Configurar la clave de API de Gemini
api_key = os.getenv("GENAI_API_KEY")

if not api_key:
    raise ValueError("La clave API no se encontró. Asegúrate de configurar 'GENAI_API_KEY' en tu archivo .env")

# Configurar la API de Gemini
genai.configure(api_key=api_key)

# Conectar a la base de datos SQLite
conexion = sqlite3.connect('ecommerce.db')
cursor = conexion.cursor()

# Función para generar la consulta SQL usando Gemini
def generar_consulta_sql(pregunta_usuario):
    prompt = f"""
    Eres un asistente que ayuda a generar consultas SQL para una base de datos SQLite llamada 'ecommerce.db'.
    Genera una consulta SQL válida para responder la siguiente pregunta:

    Pregunta: "{pregunta_usuario}"

    Reglas:
    - Utiliza sintaxis compatible con SQLite.
    - No incluyas comentarios ni explicaciones.
    - Solo devuelve la consulta SQL.

    Consulta SQL:
    """
    try:
        response = genai.generate_text(
            model='models/text-bison-001',  # Puedes ajustar el modelo si es necesario
            prompt=prompt,
            max_output_tokens=150,
            temperature=0.2,
            top_p=0.9
        )
        sql_query = response.generations[0].text.strip()
        return sql_query
    except Exception as e:
        print("Error al generar la consulta SQL:", str(e))
        return None

# Función para ejecutar la consulta SQL y obtener los resultados
def ejecutar_consulta(sql_query):
    try:
        cursor.execute(sql_query)
        resultados = cursor.fetchall()
        # Obtener los nombres de las columnas
        columnas = [descripcion[0] for descripcion in cursor.description]
        # Formatear los resultados en una lista de diccionarios
        resultados_formateados = [dict(zip(columnas, fila)) for fila in resultados]
        return resultados_formateados
    except Exception as e:
        print("Error al ejecutar la consulta SQL:", str(e))
        return None

# Función principal para procesar la pregunta del usuario
def consulta(pregunta_usuario):
    sql_query = generar_consulta_sql(pregunta_usuario)
    if sql_query:
        print("Consulta SQL generada:")
        print(sql_query)
        resultados = ejecutar_consulta(sql_query)
        if resultados is not None:
            if resultados:
                return resultados
            else:
                return "La consulta no devolvió resultados."
        else:
            return "Error al ejecutar la consulta SQL."
    else:
        return "No se pudo generar una consulta SQL."

if __name__ == "__main__":
    # Ejemplo de uso
    pregunta_de_prueba = "¿Cuáles son los productos más vendidos en el último mes?"
    respuesta = consulta(pregunta_de_prueba)
    print("Respuesta:")
    print(respuesta)
