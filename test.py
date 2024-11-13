import requests

def ask_gemini(question):
    api_key = "AIzaSyAsaDK2MGpqu9XzLQgsOMmn3m74DaZJDwE"  # Reemplaza con tu clave API
    url = "https://generativelanguage.googleapis.com/v1beta2/models/gemini-1.5-bison:generateText"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": {
            "text": question
        },
        "model": "models/gemini-1.5-bison"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Lanza una excepción para errores HTTP
        data = response.json()
        print("Respuesta generada:")
        print(data["candidates"][0]["output"])
    except requests.exceptions.RequestException as e:
        print("Ocurrió un error al realizar la solicitud:", e)
    except KeyError:
        print("Ocurrió un error con la respuesta de la API:", response.text)

if __name__ == "__main__":
    question = "What is the future of artificial intelligence?"  # Tu pregunta aquí
    ask_gemini(question)
