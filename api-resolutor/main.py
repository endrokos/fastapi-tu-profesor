import os
import base64
import logging
from typing import List, Dict, Union, Optional

from dotenv import load_dotenv
from config import MODEL_BASIC, MODEL_FOR_IMAGES_CALLS, PROMPT

load_dotenv()

from fastapi import FastAPI, UploadFile, Form, File, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import openai

# IMPORTACIONES NUEVAS PARA RATE LIMITING
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

# Limiter por IP del cliente
limiter = Limiter(key_func=get_remote_address)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Crear app de FastAPI
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.state.limiter = limiter


# Manejador de errores por rate limit
@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "respuesta": "Has hecho demasiadas peticiones. Intenta de nuevo más tarde."
        },
    )


# CORS
origins = ["http://localhost:3000", "https://endrokosai.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ENDPOINT PROTEGIDO CON LIMITADOR
@app.post("/resolver")
@limiter.limit("5/minute")  # ← Ajusta el límite aquí
async def resolver(
    request: Request,
    imagen: Optional[UploadFile] = File(None),
    pregunta: Optional[str] = Form(None),
):
    logger.info("🔄 Endpoint /resolver invocado")

    logger.info(f"📥 Pregunta recibida: {pregunta}")
    logger.info(
        f"📥 Imagen recibida: {imagen.filename if imagen and imagen.filename else 'Ninguna'}"
    )

    imagen_valida = imagen is not None and imagen.filename

    if not pregunta and not imagen_valida:
        logger.warning("⚠️ No se proporcionó ni pregunta ni imagen.")
        return {"respuesta": "Debes añadir al menos una imagen o una pregunta."}

    model_id = MODEL_BASIC
    prompt_total = PROMPT.replace("pregunta_estudiante", pregunta)
    message = defined_the_message_for_pregunta(pregunta=prompt_total or "")

    if imagen_valida:
        logger.info("🖼️ Procesando imagen para convertirla en base64...")
        base64_image = await process_image_content(imagen)
        message["content"].append(
            {"type": "image_url", "image_url": {"url": base64_image}}
        )
        model_id = MODEL_FOR_IMAGES_CALLS
        logger.info("✅ Imagen procesada y añadida al mensaje.")

    logger.info(f"🧠 Enviando mensaje al modelo: {model_id} (modo streaming)")

    async def stream_response():
        try:
            stream = openai.chat.completions.create(
                model=model_id,
                messages=[message],
                stream=True,
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            logger.error(f"❌ Error al hacer streaming del modelo: {e}")
            yield "\n[Error al generar la respuesta]"

    return StreamingResponse(stream_response(), media_type="text/plain")


async def process_image_content(imagen: UploadFile) -> str:
    contenido = await imagen.read()
    base64_image = (
        f"data:{imagen.content_type};base64,{base64.b64encode(contenido).decode()}"
    )
    return base64_image


def defined_the_message_for_pregunta(pregunta: str) -> Dict[str, Union[str, list]]:
    return {"role": "user", "content": [{"type": "text", "text": pregunta}]}
