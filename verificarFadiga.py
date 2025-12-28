import streamlit as st
import pandas as pd
combos={
    "erro tarde": "Manhã após Tarde",
    "erro pernoite":"Necessário 24 horas de folga após Pernoite",
    
    "folgas possíveis": ['',"F","f",None,""],
    "dispensas": ["SAE","DM","A","FE","OS","EX","CP","CM","CT","AM","AT","SAM","SAT","SAMP","","F","f","TO","NU",'',"",'',"F","f",None,""],

    "Manhas":["SAM","SAMSP","SAMP","SAMP.","SAMCP","M","MSP","MP","MP.","MCP","MSAP","SIMSP","SIMP","SIM","M.","M.SP","M.P","M.P.","SM","SMP","SMSP","SMCP,","M1","M1SP","M1P","M1P.","M1.","M1.SP","M1.P","M1.P.","M1CP","SRM","SRMP","SRMSP","SRMCP"],
    "M1": ["SRM","M1.","M1"],
    "M2":["M2","M2SP","M2P","M2P.","M2CP","M2.CP"],
    "Tardes" : ["CT","ST","SAT","T","SIT","T.","T2","T2."],
    "T1":["SRT","T1","T1."],
    "T2":["T2","T2."],
    "Pernoites" : ["P","SMP","SRMP","MP","M1P","M2P","AMP","SAMP","TO/P","SIMP","MEXP","CMP","M.P","M1.P","M2.P","M.P.","M1.P.","M2.P.","P.","SMP","SRMP.","MP.","M1P.","M2P.""AMP.""SAMP.","TO/P.","RE/P.","MEXP.","SP","SRMSP","MSP","M1SP","M2SP","SAMSP",'SMSP',"TO/SP","AMSP","RE/SP","MEXSP","CMSP","M.SP"],
    "Pernoite sozinho" : {"P","P.","SP"},
    "manhas ate 14h" : {"M","M.","M2.","M2","SM","SAM"},
    "Folgas" : "Mais de 5 folgas seguidas",
    "Consecutivos": "Mais de 6 dias consecutivos",


    }

turnos_possiveis ={
    "M": {"SAM","SAMSP","SAMP","SAMP.","SAMCP","M","MSP","MP","MP.","MCP","MSAP","SIMSP","SIMP","SIM","M.","M.SP","M.P","M.P.","SM","SMP","SMSP","SMCP,"},#7.75
    "M1": {"M1","M1SP","M1P","M1P.","M1.","M1.SP","M1.P","M1.P.","M1CP","SRM","SRMP","SRMSP","SRMCP"},#5.75
    "M2":{"M2","M2SP","M2P","M2P.","M2CP","M2.","M2.SP","M2.P","M2.P."}, #6.0
    "AM": {"AM","AMSP","AMP","AMP.","AMCP"},#2.58
    "T" : {"CT","ST","SAT","T","SIT","T."}, #9.25
    "AT" : {"AT"}, #3.08
    "SRT": {"SRT"}, #7.00
    "RT": {"SRT","T1","T1.","T2","T2."}, #7.25
    "P": {"P","SMP","SRMP","MP","M1P","M2P","AMP","SAMP","TO/P","SIMP","MEXP","CMP","M.P","M1.P","M2.P","M.P.","M1.P.","M2.P.","P.","SMP","SRMP.","MP.","M1P.","M2P.""AMP.""SAMP.","TO/P.","RE/P.","MEXP.","SP","SRMSP","MSP","M1SP","M2SP","SAMSP",'SMSP',"TO/SP","AMSP","RE/SP","MEXSP","CMSP","M.SP"},
    "MEX" : {"MEX","MC","MSO","MEXSP","MEXP","RE/MEX","MEXCP","RE","RE/SP","RE/P","RE/CP"}, #4.00
    "folgas possíveis": {'',"F","f",None,""},
    "dispensas": {"SAE","DM","A","FE","OS","EX","CP","CM","CT","AM","AT","SAM","SAT","SAMP","","F","f","TO","NU",'',""},
    "Cameras": {"CM","CMP","CMSP","CMCP","M.CP","CT","CP","SRMCP","MCP","M1CP","M2CP","SAMCP","SMCP","TO/CP","AMCP","RE/CP","MEXCP","CMCP","M.CP","M1.CP","M2.CP","EX","C","SO","RE/EX","EXP"}#8.00
}

def verificarCargaHoraria(escala):
    carga_horaria = 0
    
    for turno in escala["Turnos"]:
        if not escala["Turnos"][6]:
            if turno in turnos_possiveis["M"]:
                carga_horaria += 7.75
            elif turno in turnos_possiveis["M1"]:
                carga_horaria += 5.75
            elif turno in turnos_possiveis["M2"]:
                carga_horaria += 6.00
            elif turno in turnos_possiveis["AM"]:
                carga_horaria += 2.58
            elif turno in turnos_possiveis["T"]:
                carga_horaria += 9.25
            elif turno in turnos_possiveis["AT"]:
                carga_horaria += 3.08
            elif turno in turnos_possiveis["SRT"]:
                carga_horaria += 7.00
            elif turno in turnos_possiveis["RT"]:
                carga_horaria += 7.25 
            elif turno in turnos_possiveis["MEX"]:
                carga_horaria += 4.00
            elif turno in turnos_possiveis["Cameras"]:
                carga_horaria += 8.00 
            if turno in turnos_possiveis["P"]:
                carga_horaria += 7.75
    return carga_horaria

dia = 1

def adicionarErros(escala, erro, dia):
    nome = escala.get("Nome", "Sem nome")
    descricao = erro
    nova_linha = {"Nome": nome, "Dia": str(dia), "Erro": descricao}
    st.session_state.df_erros = pd.concat(
        [st.session_state.df_erros, pd.DataFrame([nova_linha])],
        ignore_index=True,
    )

def limparErros():
    st.session_state.df_erros = st.session_state.df_erros.iloc[0:0]

def verificarFadiga_pura(escala):
    """
    Versão pura da verificação de fadiga.
    NÃO usa Streamlit.
    Retorna lista de erros.
    """
    erros = []

    raw = escala.get("Turnos", []) or []
    turnos = []
    for t in raw:
        if t is None:
            turnos.append("")
        else:
            s = str(t).strip()
            if s == "" or s.lower() == "nan":
                turnos.append("")
            else:
                turnos.append(s)

    n = len(turnos)
    dias_seguidos = 0
    folgas = 0

    dispensas = set(combos.get("dispensas", []))
    folgas_possiveis = set(combos.get("folgas possíveis", []))
    pernoites = set(combos.get("Pernoites", []))
    manhas = set(combos.get("Manhas", []))
    tardes = set(combos.get("Tardes", []))

    seen_errors = set()

    for i in range(n):
        dia = i + 1
        turno_atual = turnos[i]
        turno_anterior = turnos[i - 1] if i > 0 else ""
        prox1 = turnos[i + 1] if i + 1 < n else ""
        prox2 = turnos[i + 2] if i + 2 < n else ""
        prox3 = turnos[i + 3] if i + 3 < n else ""

        if (turno_atual not in dispensas) and (turno_atual not in folgas_possiveis):
            dias_seguidos += 1
        elif (turno_atual in folgas_possiveis) and (turno_anterior in pernoites):
            dias_seguidos += 1
        else:
            dias_seguidos = 0

        if dias_seguidos > 5:
            key = ("Consecutivos", dia)
            if key not in seen_errors:
                erros.append({
                    "Nome": escala.get("Nome"),
                    "Dia": dia,
                    "Erro": combos["Consecutivos"]
                })
                seen_errors.add(key)
            dias_seguidos = 0

        if turno_anterior in pernoites and turno_atual not in dispensas:
            key = ("erro pernoite", dia)
            if key not in seen_errors:
                erros.append({
                    "Nome": escala.get("Nome"),
                    "Dia": dia,
                    "Erro": combos["erro pernoite"]
                })
                seen_errors.add(key)

        if turno_atual in tardes and prox1 in manhas and prox1 != "":
            key = ("erro tarde", dia)
            if key not in seen_errors:
                erros.append({
                    "Nome": escala.get("Nome"),
                    "Dia": dia,
                    "Erro": combos["erro tarde"]
                })
                seen_errors.add(key)

    return erros

def verificarFadiga_escala(escalas):
    """
    Recebe lista de escalas (list[dict]).
    Retorna lista de erros.
    """
    erros = []
    for esc in escalas:
        erros.extend(verificarFadiga_pura(esc))
    return erros

