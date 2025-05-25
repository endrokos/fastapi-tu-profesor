import json
import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# IMPORTACIONES PARA RATE LIMITING
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

# Configurar rate limiter
limiter = Limiter(key_func=get_remote_address)

# Crear app
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.state.limiter = limiter

# Manejador de errores por límite excedido
@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"mensaje": "Demasiadas peticiones. Intenta de nuevo más tarde."},
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

# Modelos
class Usuario(BaseModel):
    nombre: str
    gmail: str

class Sugerencia(BaseModel):
    gmail: str
    sugerencia: str

# Google Sheets
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SPREADSHEET_NAME = "registro-usuarios"

def get_sheet(sheet_name="Registros"):
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    client = gspread.authorize(creds)
    spreadsheet = client.open(SPREADSHEET_NAME)
    sheet = spreadsheet.worksheet(sheet_name)
    return sheet

# ENDPOINTS CON RATE LIMIT
@app.post("/registrar")
@limiter.limit("5/minute")  # ← puedes ajustar este valor
def registrar_usuario(usuario: Usuario, request: Request):
    sheet = get_sheet("Registros")
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([usuario.nombre, usuario.gmail, fecha_actual])
    return {"mensaje": "Usuario registrado correctamente"}

@app.post("/feedback")
@limiter.limit("5/minute")  # ← puedes ajustar este también
def guardar_sugerencia(data: Sugerencia, request: Request):
    sheet = get_sheet("Sugerencias")
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([data.gmail, data.sugerencia, fecha_actual])
    return {"mensaje": "Sugerencia guardada correctamente"}
