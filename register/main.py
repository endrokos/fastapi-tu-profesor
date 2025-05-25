from fastapi import FastAPI
from pydantic import BaseModel
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime  # ← NUEVO

app = FastAPI()


class Usuario(BaseModel):
    nombre: str
    gmail: str


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
CREDS_FILE = "client_secret.json"
SPREADSHEET_NAME = "registro-usuarios"


def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).sheet1
    return sheet


@app.post("/registrar")
def registrar_usuario(usuario: Usuario):
    sheet = get_sheet()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # ← FECHA ACTUAL
    sheet.append_row([usuario.nombre, usuario.gmail, fecha_actual])  # ← AÑADE FECHA
    return {"mensaje": "Usuario registrado correctamente"}
