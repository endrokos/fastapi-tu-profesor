import json
import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

origins = ["http://localhost:3000", "https://endrokosai.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # ← origenes específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Usuario(BaseModel):
    nombre: str
    gmail: str


class Sugerencia(BaseModel):
    gmail: str
    sugerencia: str


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SPREADSHEET_NAME = "registro-usuarios"


def get_sheet(sheet_name="Hoja 1"):
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    client = gspread.authorize(creds)
    spreadsheet = client.open(SPREADSHEET_NAME)
    sheet = spreadsheet.worksheet(sheet_name)
    return sheet


@app.post("/registrar")
def registrar_usuario(usuario: Usuario):
    sheet = get_sheet("registros")
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([usuario.nombre, usuario.gmail, fecha_actual])
    return {"mensaje": "Usuario registrado correctamente"}


@app.post("/feedback")
def guardar_sugerencia(data: Sugerencia):
    sheet = get_sheet("sugerencias")
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([data.gmail, data.sugerencia, fecha_actual])
    return {"mensaje": "Sugerencia guardada correctamente"}
