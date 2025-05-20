import os
import base64

from dotenv import load_dotenv
load_dotenv()

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

    # Codificamos la imagen a base64
    base64_image = f"data:{imagen.content_type};base64,{base64.b64encode(contenido).decode()}"

    # Enviamos imagen + texto como entrada multimodal
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": pregunta},
                    {"type": "image_url", "image_url": {"url": base64_image}}
                ]
            }
        ]
    )

    return {"respuesta": response.choices[0].message.content}
