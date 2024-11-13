from gemini_class import MyGeminiAI

model_name = "gemini-1.5-flash"  # Nombre del modelo
my_ai = MyGeminiAI(model_name=model_name)

if __name__ == "__main__":
    input_text = "How are you today?"
    response = my_ai.generate_response(input_text=input_text)
    print("Generated Response:")
    print(response)
