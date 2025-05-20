import os

from dotenv import load_dotenv
print(f"load_dotenv() {load_dotenv()}")

from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import openai


openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # cámbialo por tu dominio si quieres seguridad
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/resolver")
async def resolver(imagen: UploadFile, pregunta: str = Form(...)):
    contenido = await imagen.read()

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Corrige y explica el ejercicio de forma clara."},
            {"role": "user", "content": pregunta}
        ],
        files=[{"file": contenido, "name": imagen.filename}]
    )

    return {"respuesta": response.choices[0].message.content}
