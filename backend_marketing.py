# backend_marketing.py

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
TABLA_PERMITIDA = "marketing"
COLUMNAS_PERMITIDAS = ["content"]

# Conectar a la base de datos PostgreSQL
def conectar_bd():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Determinar si la pregunta es cuantitativa o cualitativa usando Gemini
def determinar_tipo_pregunta(pregunta):
    prompt = f"""
Clasifica la siguiente pregunta como "cuantitativa" si busca una respuesta numérica o "cualitativa" si busca un análisis o descripción.

Pregunta: "{pregunta}"
Clasificación:
"""
    try:
        model_name = "models/gemini-1.5-flash"  # Asegúrate de que este modelo esté disponible
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        clasificacion = response.text.strip().lower()
        if "cuantitativa" in clasificacion:
            return "cuantitativa"
        elif "cualitativa" in clasificacion:
            return "cualitativa"
        else:
            # Por defecto, tratar como cualitativa
            return "cualitativa"
    except Exception as e:
        print("Error al determinar el tipo de pregunta con Gemini:", str(e))
        # Por defecto, tratar como cualitativa
        return "cualitativa"

# Generar una consulta SQL usando Gemini
def generar_consulta_sql(pregunta, tipo_pregunta):
    # Crear el prompt detallado, asegurando que Gemini genere solo la consulta SQL sin comentarios
    prompt = f"""
Eres un asistente que traduce preguntas en lenguaje natural a consultas SQL para una base de datos de comercio electrónico.
La base de datos tiene una única tabla llamada 'marketing' con una columna llamada 'content'.
Solo debes generar consultas SELECT válidas y seguras sobre la tabla 'marketing' y la columna 'content'.
No incluyas consultas que modifiquen la base de datos (como INSERT, UPDATE, DELETE).

Además, si la pregunta es de tipo "{tipo_pregunta}", adapta la consulta en consecuencia.

Por favor, genera únicamente la consulta SQL sin comentarios ni explicaciones adicionales.

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

        # Eliminar cualquier comentario que preceda al SELECT
        consulta_sql = re.sub(r'^--.*\n', '', consulta_sql, flags=re.MULTILINE)
        consulta_sql = re.sub(r'^```sql\s*', '', consulta_sql, flags=re.IGNORECASE)
        consulta_sql = re.sub(r'```\s*$', '', consulta_sql, flags=re.IGNORECASE)

        print(f"Consulta SQL generada: {consulta_sql}")
        return consulta_sql
    except Exception as e:
        print("Error al generar la consulta SQL con Gemini:", str(e))
        return None

# Validar la consulta SQL generada
def validar_consulta_sql(consulta_sql):
    # Eliminar comentarios y espacios en blanco al inicio
    consulta_sql_clean = re.sub(r'^(\s*--.*\n)*\s*', '', consulta_sql)

    # Verificar que la consulta comience con SELECT
    if not re.match(r'^SELECT\s', consulta_sql_clean, re.IGNORECASE):
        print("La consulta no es un SELECT.")
        return False

    # Verificar que solo se use la tabla permitida
    tablas = re.findall(r'FROM\s+(\w+)', consulta_sql_clean, re.IGNORECASE)
    for tabla in tablas:
        if tabla.lower() != TABLA_PERMITIDA:
            print(f"Tabla no permitida en la consulta: {tabla}")
            return False

    # Verificar que solo se usen las columnas permitidas
    select_clause = re.findall(r'SELECT\s+(.*?)\s+FROM', consulta_sql_clean, re.IGNORECASE)
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

# Realizar análisis cualitativo con Gemini
def realizar_analisis(pregunta, datos):
    if not datos:
        return "No se encontró información suficiente para realizar el análisis solicitado."

    # Concatenar los datos obtenidos en una sola cadena de texto
    contenidos = "\n".join([fila[0] for fila in datos])

    # Crear el prompt para Gemini
    prompt = f"""
Eres un analista de datos experto. A continuación se muestra un conjunto de datos:

{contenidos}

Basándote en estos datos, responde a la siguiente pregunta en español:

"{pregunta}"

Proporciona una respuesta precisa y concisa de máximo 2 párrafos, basada en la información disponible.
"""

    try:
        model_name = "models/gemini-1.5-flash"  # Asegúrate de que este modelo esté disponible
        model = genai.GenerativeModel(model_name)

        # Generar la respuesta del análisis
        response = model.generate_content(prompt)
        analisis = response.text.strip()

        print(f"Análisis generado: {analisis}")
        return analisis
    except Exception as e:
        print("Error al realizar el análisis con Gemini:", str(e))
        return "No se pudo realizar el análisis solicitado."

# Formatear los resultados para la respuesta al usuario
def formatear_respuesta(filas, columnas, tipo_pregunta, pregunta_original):
    if not filas:
        return "No se encontraron resultados para tu consulta."

    # Si es una pregunta cuantitativa y retorna un solo valor, devolver solo el valor
    if len(filas) == 1 and len(columnas) == 1 and tipo_pregunta == "cuantitativa":
        return str(filas[0][0])

    # Si es una pregunta cualitativa, realizar análisis
    if tipo_pregunta == "cualitativa":
        analisis = realizar_analisis(pregunta_original, filas)
        return analisis

    # Crear una tabla simple en formato markdown para múltiples resultados
    tabla = "| " + " | ".join(columnas) + " |\n"
    tabla += "| " + " | ".join(["---"] * len(columnas)) + " |\n"
    for fila in filas:
        fila_formateada = "| " + " | ".join([str(item) for item in fila]) + " |\n"
        tabla += fila_formateada

    return tabla

# Función para obtener todos los contenidos de la tabla 'marketing'
def obtener_todos_los_contenidos(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM marketing;")
        resultados = cursor.fetchall()
        cursor.close()
        return resultados
    except psycopg2.Error as e:
        print(f"Error al obtener contenidos: {e}")
        return []

# Función principal para manejar la consulta del usuario
def consulta(input_usuario):
    # Determinar el tipo de pregunta
    tipo_pregunta = determinar_tipo_pregunta(input_usuario)
    print(f"Tipo de pregunta: {tipo_pregunta}")

    # Conectar a la base de datos
    conn = conectar_bd()
    if not conn:
        return "Lo siento, no pude conectar a la base de datos."

    # Generar la consulta SQL
    consulta_sql = generar_consulta_sql(input_usuario, tipo_pregunta)
    if not consulta_sql:
        # Fall back antes de cerrar la conexión
        print("Generación de consulta SQL fallida. Realizando análisis cualitativo con toda la información.")
        respuesta = realizar_analisis(input_usuario, obtener_todos_los_contenidos(conn))
        conn.close()
        return respuesta

    # Ejecutar la consulta SQL
    filas, columnas = ejecutar_consulta_sql(consulta_sql, conn)
    if filas is None or columnas is None:
        # Fall back antes de cerrar la conexión
        print("Ejecución de consulta SQL fallida. Realizando análisis cualitativo con toda la información.")
        respuesta = realizar_analisis(input_usuario, obtener_todos_los_contenidos(conn))
        conn.close()
        return respuesta

    # Formatear la respuesta según el tipo de pregunta
    respuesta = formatear_respuesta(filas, columnas, tipo_pregunta, input_usuario)
    conn.close()
    return respuesta
