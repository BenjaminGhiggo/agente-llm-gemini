import os
from dotenv import load_dotenv
import google.generativeai as genai

# Cargar las variables de entorno desde un archivo .env
load_dotenv()

# Configurar tu clave de API desde la variable de entorno
api_key = os.getenv("GENAI_API_KEY")

if not api_key:
    raise ValueError("La clave API no se encontró. Asegúrate de configurar 'GENAI_API_KEY' en tu archivo .env")

genai.configure(api_key=api_key)

def test_gemini(prompt):
    try:
        # Definir el modelo que usaremos
        model_name = "models/gemini-1.5-flash"
        
        # Crear instancia del modelo
        model = genai.GenerativeModel(model_name)
        
        # Generar contenido a partir del prompt
        response = model.generate_content(prompt)
        print("Respuesta generada:")
        print(response.text)
        
    except Exception as e:
        print("Ocurrió un error:", str(e))

if __name__ == "__main__":
    test_prompt = "¿Cuál es el futuro de la inteligencia artificial?"  # Pregunta de prueba
    test_gemini(test_prompt)
