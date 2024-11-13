import google.generativeai as genai

class MyGeminiAI:
    def __init__(self, model_name):
        self.model_name = model_name
        self.api_key = "AIzaSyCF02A7uVq2uvAhpjgm_x15B2B2JPGABXo"  # Reemplaza con tu clave real
        
        # Configura la API Key
        genai.configure(api_key=self.api_key)

    def generate_response(self, input_text):
        """Genera una respuesta usando el modelo Gemini"""
        response = genai.generate_text(
            model=self.model_name,
            prompt=input_text
        )
        return response.result  # Ajustamos aquí según la estructura de la respuesta.
