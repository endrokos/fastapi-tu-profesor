import os
import base64
import logging
from typing import List, Dict, Union, Optional

from dotenv import load_dotenv

from config import MODEL_BASIC, MODEL_FOR_IMAGES_CALLS

load_dotenv()

from fastapi import FastAPI, UploadFile, Form, File
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

# Configurar el logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/resolver")
async def resolver(
    imagen: Optional[UploadFile] = File(None), pregunta: Optional[str] = Form(None)
):

    logger.info(f"📥 Pregunta recibida: {pregunta}")
    logger.info(f"📥 Imagen recibida: {imagen.filename if imagen else 'Ninguna'}")

    if pregunta is None:
        return {"respuesta": "Debes añadir una pregunta"}

    model_id = MODEL_BASIC
    message = defined_the_message_for_pregunta(pregunta=pregunta)
    if imagen is not None and imagen.filename:
        base64_image = await process_image_content(imagen)
        message["content"].append(
            {"type": "image_url", "image_url": {"url": base64_image}}
        )
        model_id = MODEL_FOR_IMAGES_CALLS

    response = openai.chat.completions.create(
        model=model_id,
        messages=[message],
    )

    respuesta = response.choices[0].message.content

    print(f"La respuesta a tu pregunta es: {respuesta}")

    return {"respuesta": respuesta}


async def process_image_content(imagen):
    contenido = await imagen.read()
    base64_image = (
        f"data:{imagen.content_type};base64,{base64.b64encode(contenido).decode()}"
    )
    return base64_image


def defined_the_message_for_pregunta(pregunta: str) -> Dict[str, Union[str, list]]:
    return {"role": "user", "content": [{"type": "text", "text": pregunta}]}
