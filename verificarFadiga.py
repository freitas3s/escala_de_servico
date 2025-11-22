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

def verificarFadiga(escala):
    """
    Versão corrigida e deduplicada da verificação de fadiga.
    Retorna o DataFrame de erros atualizado em st.session_state.df_erros.
    """
    # Normaliza turnos (None / "" / nan -> 'f')
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

    # precomputar conjuntos (usar lower() se quiser normalizar)
    dispensas = set(combos.get("dispensas", []))
    folgas_possiveis = set(combos.get("folgas possíveis", []))
    pernoites = set(combos.get("Pernoites", []))
    manhas = set(combos.get("Manhas", []))
    tardes = set(combos.get("Tardes", []))
    m2 = set(combos.get("M2", []))

    # para evitar erros duplicados (mesmo tipo + mesmo dia)
    seen_errors = set()

    for i in range(n):
        dia = i + 1
        turno_atual = turnos[i]
        turno_anterior = turnos[i - 1] if i > 0 else ""
        prox1 = turnos[i + 1] if i + 1 < n else ""
        prox2 = turnos[i + 2] if i + 2 < n else ""
        prox3 = turnos[i + 3] if i + 3 < n else ""

        # dias consecutivos trabalhando
        if (turno_atual not in dispensas) and (turno_atual not in folgas_possiveis):
            dias_seguidos += 1
        elif (turno_atual in folgas_possiveis) and (turno_anterior in pernoites):
            dias_seguidos += 1
        else:
            dias_seguidos = 0

        # --- Detecta consecutivos (6 ou mais dias consecutivos) ---
        # condição onde pernoite está presente e o dia +2 não é dispensa e o dia +3 é tudo menos manhã
        if dias_seguidos == 5 and (turno_atual in pernoites) and (prox2 not in dispensas) and (prox3 in manhas):
            key = ("Consecutivos", dia)
            erro = combos["Consecutivos"]
            if key not in seen_errors:
                adicionarErros(escala, erro, dia)
                seen_errors.add(key)
            dias_seguidos = 0

        # condição geral: mais de 5 dias consecutivos (>=6),
        # e próximos dois dias NÃO são dispensa -> gerar erro
        if dias_seguidos > 5:           
            if turno_atual in combos["manhas ate 14h"] and prox1 not in dispensas and (prox2 not in combos["T2"] or prox2 not in ["Pernoite sozinho"]) :
                key = ("Consecutivos", dia)
                erro = combos["Consecutivos"]
                if key not in seen_errors:
                    adicionarErros(escala, erro, dia)
                    seen_errors.add(key)
                dias_seguidos = 0
            elif turno_atual in combos["M1"] and prox1 not in dispensas and (prox2 not in combos["T1"] or prox2 not in ["Pernoite sozinho"]):
                key = ("Consecutivos", dia)
                erro = combos["Consecutivos"]
                if key not in seen_errors:
                    adicionarErros(escala, erro, dia)
                    seen_errors.add(key)
                dias_seguidos = 0
            elif turno_atual in combos["T1"] and prox1 not in dispensas and prox2 not in ["Pernoite sozinho"]:
                key = ("Consecutivos", dia)
                erro = combos["Consecutivos"]
                if key not in seen_errors:
                    adicionarErros(escala, erro, dia)
                    seen_errors.add(key)
                dias_seguidos = 0

        # --- Folgas seguidas ---
        if turno_atual in folgas_possiveis:
            folgas += 1
        else:
            folgas = 0

        if folgas > 5 and (i - 6) >= 0:
            # verificar se dia de -6 não foi pernoite
            if turnos[i - 6] not in pernoites:
                day_to_report = max(1, i - 4)  # garanta >= 1
                key = ("Folgas", day_to_report)
                erro = combos["Folgas"]
                if key not in seen_errors:
                    adicionarErros(escala, erro, day_to_report)
                    seen_errors.add(key)
            folgas = 0

        # --- Erros envolvendo pernoite ---
        if (turno_anterior in pernoites) and ( (turno_atual not in dispensas) or (prox1 in manhas)):
            key = ("erro pernoite", dia)
            erro = combos["erro pernoite"]
            if key not in seen_errors:
                adicionarErros(escala, erro, dia)
                seen_errors.add(key)

        # --- Erros tarde -> manhã ---
        if (turno_atual in tardes) and (prox1 in manhas) and (prox1 != ""):
            key = ("erro tarde", dia)
            erro = combos["erro tarde"]
            if key not in seen_errors:
                adicionarErros(escala, erro, dia)
                seen_errors.add(key)
    #checa se todos os turnos digitados existem
    for turno_procurado in turnos_possiveis.values():
        if turno_atual in turno_procurado:
                break
    else:
            erro = f"Turno {turno_atual} não existe"
            adicionarErros(escala,erro,dia)

    return st.session_state.df_erros
