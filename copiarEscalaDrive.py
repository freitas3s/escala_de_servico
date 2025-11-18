import gspread
from google.oauth2.service_account import Credentials
import re
import streamlit as st

# 1️⃣ Coloque o conteúdo do JSON da chave em um Secret chamado "GDRIVE_KEY"
# Ex: st.secrets["GDRIVE_KEY"]

SERVICE_ACCOUNT_INFO = st.secrets["GDRIVE_KEY"]

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
client = gspread.authorize(creds)

planilha = client.open_by_key("1ry-PFpRg9iXwI2-YcSkP7pEsramIQfQjWSICSe434jA")
aba = planilha.worksheet("ESCALA")

# Leitura dos dados
nomes_1 = aba.get("B52:B74")
turnos_1 = aba.get("M52:AP74", pad_values=True)
carga_horaria_mensal_1 = aba.get("AT52:AT74")

ultima_linha = len(aba.col_values(1))
nomes_2 = aba.get(f"B80:B{ultima_linha}")
turnos_2 = aba.get(f"M80:AP{ultima_linha}", pad_values=True)
carga_horaria_mensal_2= aba.get(f"AT80:AT{ultima_linha}")

nomes = nomes_1 + nomes_2
turnos = turnos_1 + turnos_2
carga_horaria_mensal = carga_horaria_mensal_1 + carga_horaria_mensal_2

escala = []

for i, nome_celula in enumerate(nomes):
    if nome_celula and nome_celula[0].strip():  
        nome = nome_celula[0].strip()
        nome = re.sub(r"\(\d+\)", "", nome).strip()
        lista_turnos = turnos[i] if i < len(turnos) else []
        carga_horaria_mensal_operador = carga_horaria_mensal[i]
        escala.append({
            "Nome": nome,
            "Turnos": lista_turnos,
            "Carga horaria mensal": carga_horaria_mensal_operador
        })

# Não salva mais no disco, só retorna
def copiarEscala():
    return escala