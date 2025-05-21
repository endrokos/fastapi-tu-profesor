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

# Configurar la clave de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Crear app de FastAPI
app = FastAPI()

# Permitir CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # cámbialo por tu dominio si quieres seguridad
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/resolver")
async def resolver(
    imagen: Optional[UploadFile] = File(None),
    pregunta: Optional[str] = Form(None)
):
    logger.info("🔄 Endpoint /resolver invocado")

    logger.info(f"📥 Pregunta recibida: {pregunta}")
    logger.info(f"📥 Imagen recibida: {imagen.filename if imagen and imagen.filename else 'Ninguna'}")

    imagen_valida = imagen is not None and imagen.filename

    if not pregunta and not imagen_valida:
        logger.warning("⚠️ No se proporcionó ni pregunta ni imagen.")
        return {"respuesta": "Debes añadir al menos una imagen o una pregunta."}

    model_id = MODEL_BASIC
    message = defined_the_message_for_pregunta(pregunta=pregunta or "")

    if imagen_valida:
        logger.info("🖼️ Procesando imagen para convertirla en base64...")
        base64_image = await process_image_content(imagen)
        message["content"].append({
            "type": "image_url",
            "image_url": {"url": base64_image}
        })
        model_id = MODEL_FOR_IMAGES_CALLS
        logger.info("✅ Imagen procesada y añadida al mensaje.")

    logger.info(f"🧠 Enviando mensaje al modelo: {model_id}")
    try:
        response = openai.chat.completions.create(
            model=model_id,
            messages=[message],
        )
        respuesta = response.choices[0].message.content
        logger.info(f"🤖 Respuesta del modelo: {respuesta}")
        return {"respuesta": respuesta}
    except Exception as e:
        logger.error(f"❌ Error al llamar al modelo de OpenAI: {e}")
        return {"respuesta": "Ocurrió un error al procesar tu solicitud. Disculpe las molestias."}


async def process_image_content(imagen: UploadFile) -> str:
    contenido = await imagen.read()
    base64_image = (
        f"data:{imagen.content_type};base64,{base64.b64encode(contenido).decode()}"
    )
    return base64_image


def defined_the_message_for_pregunta(pregunta: str) -> Dict[str, Union[str, list]]:
    return {"role": "user", "content": [{"type": "text", "text": pregunta}]}
