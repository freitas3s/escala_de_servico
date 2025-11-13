import gspread
from google.oauth2.service_account import Credentials
import re
import json

SERVICE_ACCOUNT_FILE = r"C:\Users\guije\Documents\GitHub\escala_de_servico\healthy-keyword-475022-f9-87fd6c066547.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

planilha = client.open_by_key("1rj5vw60BigeLnEZx5Zp1R0izCO9qrEBc6qV9UKnxrqo")
aba = planilha.worksheet("ESCALA")

nomes_1 = aba.get("B52:B74")
turnos_1 = aba.get("M52:AP74",pad_values=True)


ultima_linha = len(aba.col_values(1))
nomes_2 = aba.get(f"B80:B{ultima_linha}")
turnos_2 = aba.get(f"M80:AP{ultima_linha}",pad_values=True)

nomes = nomes_1 + nomes_2
turnos = turnos_1 + turnos_2

escala = []

for i, nome_celula in enumerate(nomes):
    if nome_celula and nome_celula[0].strip():  
        nome = nome_celula[0].strip()
        nome = re.sub(r"\(\d+\)", "", nome).strip()
        lista_turnos = turnos[i] if i < len(turnos) else []
        escala.append({
            "Nome": nome,
            "Turnos": lista_turnos
        })

def copiarEscala():
    with open("escala.json", "w", encoding="utf-8") as f:
        json.dump(escala, f, ensure_ascii=False, indent=4)
