import gspread
from google.oauth2.service_account import Credentials
import re
import streamlit as st
import datetime
import calendar

SERVICE_ACCOUNT_INFO = st.secrets["GDRIVE_KEY"]

def copiarEscala(mes):

    meses_com_31_dias = {1, 3, 5, 7, 8, 10, 12}
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
    client = gspread.authorize(creds)

    planilha = client.open_by_key(f"{ID_PLANILHAS[mes]}")
    aba = planilha.worksheet("ESCALA")


    nomes_1 = aba.get("C53:C75")
    turnos_1 = aba.get("N53:AR75", pad_values=True) if mes in meses_com_31_dias else aba.get("N53:AR75", pad_values=True)
    carga_horaria_mensal_1 = aba.get("AU53:AU75")

    ultima_linha = len(aba.col_values(1))
    nomes_2 = aba.get(f"C81:C{ultima_linha}")
    turnos_2 = aba.get(f"N81:AR{ultima_linha}", pad_values=True)if mes in meses_com_31_dias else aba.get(f"N81:AR{ultima_linha}", pad_values=True)
    carga_horaria_mensal_2= aba.get(f"AU81:AU{ultima_linha}")

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

    return escala


FERIADOS_DF = {
    "2025-01-01": "Confraternização Universal (feriado)",
    "2025-03-03": "Carnaval (ponto facultativo)",
    "2025-03-04": "Carnaval (ponto facultativo)",
    "2025-03-05": "Quarta-feira de Cinzas (ponto facultativo até às 14h)",
    "2025-04-18": "Paixão de Cristo (feriado)",
    "2025-04-21": "Tiradentes / Aniversário de Brasília (feriado)",
    "2025-05-01": "Dia do Trabalho (feriado)",
    "2025-06-19": "Corpus Christi (ponto facultativo)",
    "2025-06-20": "Ponto facultativo (GDF)",
    "2025-09-07": "Independência do Brasil (feriado)",
    "2025-10-12": "Nossa Senhora Aparecida (feriado)",
    "2025-10-28": "Dia do Servidor Público (ponto facultativo)",
    "2025-11-02": "Finados (feriado)",
    "2025-11-15": "Proclamação da República (feriado)",
    "2025-11-20": "Dia da Consciência Negra (feriado)",
    "2025-11-30": "Dia do Evangélico (feriado local DF)",
    "2025-12-24": "Véspera de Natal (ponto facultativo após 14h)",
    "2025-12-25": "Natal (feriado)",
    "2025-12-31": "Véspera de Ano Novo (ponto facultativo após 14h)",

    "2026-01-01": "Confraternização Universal (feriado)",
    "2026-02-16": "Carnaval (ponto facultativo)",
    "2026-02-17": "Carnaval (ponto facultativo)",
    "2026-02-18": "Quarta-feira de Cinzas (ponto facultativo até às 14h)",
    "2026-04-03": "Sexta-feira Santa / Paixão de Cristo (feriado)",
    "2026-04-21": "Tiradentes / Aniversário de Brasília (feriado)",
    "2026-05-01": "Dia do Trabalho (feriado)",
    "2026-06-04": "Corpus Christi (ponto facultativo)",
    "2026-09-07": "Independência do Brasil (feriado)",
    "2026-10-12": "Nossa Senhora Aparecida (feriado)",
    "2026-10-28": "Dia do Servidor Público (ponto facultativo)",
    "2026-11-02": "Finados (feriado)",
    "2026-11-15": "Proclamação da República (feriado)",
    "2026-11-20": "Dia da Consciência Negra (feriado)",
    "2026-11-30": "Dia do Evangélico (feriado local DF)",
    "2026-12-24": "Véspera de Natal (ponto facultativo)",
    "2026-12-25": "Natal (feriado)",
    "2026-12-31": "Véspera de Ano Novo (ponto facultativo)",
}

DIAS_SEMANA = {
    "Mon": "Seg",
    "Tue": "Ter",
    "Wed": "Qua",
    "Thu": "Qui",
    "Fri": "Sex",
    "Sat": "Sáb",
    "Sun": "Dom",
}

ID_PLANILHAS = {
    1: "1G7Jc21d9VGSiyObP4awVkAsO9f9tacGx9oW4HwnRRFs",
    2: None,
    3: None,
    4: None,
    5: None,
    6: None,
    7: None,
    8: None,
    9: None,
    10: None,
    11: "1ry-PFpRg9iXwI2-YcSkP7pEsramIQfQjWSICSe434jA",
    12: "1npvVB_9Akl9IK2lfDGMDPha0nLfGyb3hJhmteFqN-KA",
}

MESES ={

    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",

}
def gerar_colunas_com_dia_semana(ano, mes):

    dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]

    data_atual = datetime.date(ano, mes, 1)
    dias_no_mes = calendar.monthrange(ano, mes)[1]
    data_final = datetime.date(ano, mes, dias_no_mes)

    colunas = []

    FERIADOS = {
        datetime.datetime.strptime(d, "%Y-%m-%d").date()
        for d in FERIADOS_DF.keys()
    }

    while data_atual <= data_final:
        nome_semana = dias_semana[data_atual.weekday()]

        
        if data_atual in FERIADOS:
            marcador = "🏖️"     
        elif nome_semana == "Sab":
            marcador = "🔴"     
        elif nome_semana == "Dom":
            marcador = "🔴"     
        else:
            marcador = ""

        
        if marcador:
            texto = f"{data_atual.day:02d}\n{nome_semana} {marcador}"
        else:
            texto = f"{data_atual.day:02d}\n{nome_semana}"

        colunas.append(texto)
        data_atual += datetime.timedelta(days=1)

    return colunas
