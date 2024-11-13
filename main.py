# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend_mercado import consulta as consulta_mercado

app = FastAPI(title="API de Bot de Mercado", version="1.0")

class Consulta(BaseModel):
    pregunta: str

@app.post("/mercado")
async def bot_mercado(consulta: Consulta):
    if not consulta.pregunta:
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")

    respuesta = consulta_mercado(consulta.pregunta)
    return {"respuesta": respuesta}
