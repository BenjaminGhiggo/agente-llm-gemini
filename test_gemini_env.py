import google.generativeai as genai

# Configurar tu clave de API
api_key = "AIzaSyAsaDK2MGpqu9XzLQgsOMmn3m74DaZJDwE"  # Reemplaza con tu clave API válida
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
