# interactive_gemini_sql.py

import os
from dotenv import load_dotenv
import google.generativeai as genai
import psycopg2

# Cargar las variables de entorno desde un archivo .env
load_dotenv()

# Configurar tu clave de API desde la variable de entorno
api_key = os.getenv("GENAI_API_KEY")

if not api_key:
    raise ValueError("La clave API no se encontró. Asegúrate de configurar 'GENAI_API_KEY' en tu archivo .env")

genai.configure(api_key=api_key)

# Obtener las credenciales de la base de datos desde las variables de entorno
DB_HOST = os.getenv("HOST")
DB_USER = os.getenv("USER")
DB_PASSWORD = os.getenv("PASSWORD")
DB_DATABASE = os.getenv("DATABASE")
DB_PORT = os.getenv("PORT")

if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE, DB_PORT]):
    raise ValueError("Faltan credenciales de la base de datos. Asegúrate de configurar 'HOST', 'USER', 'PASSWORD', 'DATABASE' y 'PORT' en tu archivo .env")

def generate_sql_query(prompt):
    try:
        # Definir el modelo que usaremos
        model_name = "models/gemini-1.5-flash"
        
        # Crear instancia del modelo
        model = genai.GenerativeModel(model_name)
        
        # Instrucciones para el modelo
        instruction = f"""
Eres un asistente que convierte preguntas en lenguaje natural en consultas SQL válidas para una base de datos PostgreSQL.
La base de datos contiene una tabla llamada 'mercado' con una columna 'content'.
Genera una consulta SQL segura que solo realiza operaciones SELECT sobre la columna 'content' de la tabla 'mercado'.
No incluyas operaciones que modifiquen la base de datos.
"""
        # Construir el prompt para el modelo
        full_prompt = instruction + "\nPregunta: " + prompt + "\nConsulta SQL:"
        
        # Generar contenido a partir del prompt
        response = model.generate_content(full_prompt)
        
        # Obtener la consulta SQL generada
        sql_query = response.text.strip()
        return sql_query
    except Exception as e:
        print("Ocurrió un error al generar la consulta SQL:", str(e))
        return None

def execute_sql_query(sql_query):
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )
        cursor = conn.cursor()
        
        # Ejecutar la consulta SQL
        cursor.execute(sql_query)
        # Obtener los resultados
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print("Ocurrió un error al ejecutar la consulta SQL:", str(e))
        return None

def main():
    print("Bienvenido al asistente de consultas. Escribe 'salir' para terminar.")
    while True:
        user_input = input("Haz tu pregunta: ")
        if user_input.lower() == 'salir':
            break
        # Generar la consulta SQL a partir de la pregunta del usuario
        sql_query = generate_sql_query(user_input)
        if sql_query:
            print("Consulta SQL generada:")
            print(sql_query)
            # Validar que la consulta sea segura
            if not sql_query.strip().upper().startswith("SELECT"):
                print("La consulta generada no es una consulta SELECT válida. Por razones de seguridad, no se ejecutará.")
                continue
            # Ejecutar la consulta SQL
            results = execute_sql_query(sql_query)
            if results is not None:
                # Mostrar los resultados al usuario
                print("Resultados:")
                for row in results:
                    print(row)
            else:
                print("No se pudieron obtener resultados.")
        else:
            print("No se pudo generar una consulta SQL.")

if __name__ == "__main__":
    main()
