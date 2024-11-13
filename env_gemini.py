# env_gemini.py

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

def get_gemini_model(model_name="models/gemini-1.5-flash"):
    return genai.GenerativeModel(model_name)
