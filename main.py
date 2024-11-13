from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend_mercado import consulta as consulta_mercado
from backend_financiamiento import consulta as consulta_financiamiento
from backend_marketing import consulta as consulta_marketing
from backend_historial import consulta as consulta_historial

# Crear instancia de FastAPI
app = FastAPI(title="API de Bots", version="1.1")

# Modelo de datos para la solicitud
class Consulta(BaseModel):
    pregunta: str

# Endpoint para el bot de Mercado
@app.post("/mercado")
async def bot_mercado(consulta: Consulta):
    if not consulta.pregunta:
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")
    
    respuesta = consulta_mercado(consulta.pregunta)
    return {"respuesta": respuesta}

# Endpoint para el bot de Financiamiento
@app.post("/financiamiento")
async def bot_financiamiento(consulta: Consulta):
    if not consulta.pregunta:
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")
    
    respuesta = consulta_financiamiento(consulta.pregunta)
    return {"respuesta": respuesta}

# Endpoint para el bot de Marketing
@app.post("/marketing")
async def bot_marketing(consulta: Consulta):
    if not consulta.pregunta:
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")
    
    respuesta = consulta_marketing(consulta.pregunta)
    return {"respuesta": respuesta}

# Endpoint para el bot de Historial
@app.post("/historial")
async def bot_historial(consulta: Consulta):
    if not consulta.pregunta:
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")
    
    respuesta = consulta_historial(consulta.pregunta)
    return {"respuesta": respuesta}
