# backend.py

import os
import psycopg2
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Cargar las variables de entorno desde un archivo .env
load_dotenv()

# Configurar la clave API de Gemini desde la variable de entorno
api_key = os.getenv("GENAI_API_KEY")
if not api_key:
    raise ValueError("La clave API de Gemini no se encontró. Asegúrate de configurar 'GENAI_API_KEY' en tu archivo .env")

genai.configure(api_key=api_key)

# Configuración de la base de datos PostgreSQL
DB_CONFIG = {
    "host": os.getenv("HOST"),
    "database": os.getenv("DATABASE"),
    "user": os.getenv("USER"),
    "password": os.getenv("PASSWORD"),
    "port": os.getenv("PORT", "5432")  # Puerto por defecto para PostgreSQL
}

# Definir esquema permitido
TABLA_PERMITIDA = "mercado"
COLUMNAS_PERMITIDAS = ["content"]

# Conectar a la base de datos PostgreSQL
def conectar_bd():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Generar una consulta SQL usando Gemini
def generar_consulta_sql(pregunta):
    # Crear el prompt detallado
    prompt = f"""
    Eres un asistente que traduce preguntas en lenguaje natural a consultas SQL para una base de datos de comercio electrónico.
    La base de datos tiene una única tabla llamada 'mercado' con una columna llamada 'content'.
    Solo debes generar consultas SELECT válidas y seguras sobre la tabla 'mercado' y la columna 'content'.
    No incluyas consultas que modifiquen la base de datos (como INSERT, UPDATE, DELETE).

    Pregunta del usuario: "{pregunta}"
    Consulta SQL:
    """

    try:
        # Definir el modelo a utilizar
        model_name = "models/gemini-1.5-flash"  # Asegúrate de que este modelo esté disponible

        # Crear instancia del modelo
        model = genai.GenerativeModel(model_name)

        # Generar contenido a partir del prompt
        response = model.generate_content(prompt)

        # Obtener el texto de la respuesta
        consulta_sql = response.text.strip()

        # Eliminar bloques de código Markdown si existen
        consulta_sql = re.sub(r'^```sql\s*', '', consulta_sql, flags=re.IGNORECASE)
        consulta_sql = re.sub(r'```\s*$', '', consulta_sql, flags=re.IGNORECASE)

        print(f"Consulta SQL generada: {consulta_sql}")
        return consulta_sql
    except Exception as e:
        print("Error al generar la consulta SQL con Gemini:", str(e))
        return None

# Validar la consulta SQL generada
def validar_consulta_sql(consulta_sql):
    # Verificar que la consulta comience con SELECT
    if not re.match(r'^\s*SELECT\s', consulta_sql, re.IGNORECASE):
        print("La consulta no es un SELECT.")
        return False

    # Verificar que solo se use la tabla permitida
    tablas = re.findall(r'FROM\s+(\w+)', consulta_sql, re.IGNORECASE)
    for tabla in tablas:
        if tabla.lower() != TABLA_PERMITIDA:
            print(f"Tabla no permitida en la consulta: {tabla}")
            return False

    # Verificar que solo se usen las columnas permitidas
    select_clause = re.findall(r'SELECT\s+(.*?)\s+FROM', consulta_sql, re.IGNORECASE)
    if select_clause:
        select_clause = select_clause[0]
        # Extraer todas las columnas permitidas presentes en el SELECT
        columnas_en_query = re.findall(r'\b(' + '|'.join(COLUMNAS_PERMITIDAS) + r')\b', select_clause)

        # Extraer todas las columnas usadas en el SELECT (incluyendo las dentro de funciones)
        all_column_refs = re.findall(r'\b\w+\b', select_clause)
        # Excluir palabras clave de SQL y funciones
        sql_keywords = set([
            'COUNT', 'DISTINCT', 'AS', 'SUM', 'AVG', 'MIN', 'MAX', 'GROUP', 'BY', 'ORDER', 'WHERE', 'AND', 'OR'
        ])
        columns_used = [word for word in all_column_refs if word.upper() not in sql_keywords]

        # Verificar que todas las columnas usadas estén permitidas
        for columna in columns_used:
            if columna not in COLUMNAS_PERMITIDAS:
                print(f"Columna no permitida en la consulta: {columna}")
                return False

    return True

# Ejecutar la consulta SQL en la base de datos
def ejecutar_consulta_sql(consulta_sql, conn):
    # Validar la consulta SQL antes de ejecutarla
    if not validar_consulta_sql(consulta_sql):
        print("Consulta SQL no válida.")
        return None, None

    try:
        cursor = conn.cursor()
        cursor.execute(consulta_sql)
        filas = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]
        cursor.close()
        return filas, columnas
    except psycopg2.Error as e:
        print(f"Error al ejecutar la consulta SQL: {e}")
        return None, None

# Formatear los resultados para la respuesta al usuario
def formatear_respuesta(filas, columnas):
    if not filas:
        return "No se encontraron resultados para tu consulta."

    # Si es una sola fila y una sola columna, devolver solo el valor
    if len(filas) == 1 and len(columnas) == 1:
        return str(filas[0][0])

    # Crear una tabla simple en formato markdown para múltiples resultados
    tabla = "| " + " | ".join(columnas) + " |\n"
    tabla += "| " + " | ".join(["---"] * len(columnas)) + " |\n"
    for fila in filas:
        fila_formateada = "| " + " | ".join([str(item) for item in fila]) + " |\n"
        tabla += fila_formateada

    return tabla

# Función principal para manejar la consulta del usuario
def consulta(input_usuario):
    conn = conectar_bd()
    if not conn:
        return "Lo siento, no pude conectar a la base de datos."

    consulta_sql = generar_consulta_sql(input_usuario)
    if not consulta_sql:
        conn.close()
        return "Lo siento, no pude generar una consulta para tu solicitud."

    filas, columnas = ejecutar_consulta_sql(consulta_sql, conn)
    conn.close()

    if filas is None or columnas is None:
        return "Lo siento, ocurrió un error al ejecutar tu solicitud."

    respuesta = formatear_respuesta(filas, columnas)
    return respuesta
