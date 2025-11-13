combos={
    "erro tarde": "Manhã após Tarde",
    "erro pernoite":"Necessário 24 horas de folga após Pernoite",
    
    "folgas possíveis": ["","F","f"],
    "dispensas": ["SAE","DM","A","FE","OS","EX","CP","CM","CT","AM","AT","SAM","SAT","SAMP","","F","f","TO","NU"],

    "Manhas": ["SM","SMP","SMSP","SMCP","SRM","SRMP","SRMSP","SRMCP","SAM","SAMSP","SAMP","SAMP.","SAMCP","M1","M1SP","M1P","M1P.","M1CP"],
    "M2":["M2","M2SP","M2P","M2P.","M2CP"],
    "Tardes" : ["CT","ST","SAT","T","T2"],
    "T1":["SRT","T1"],
    "Pernoites" : ["P","SMP","SRMP","MP","M1P","M2P","AMP","SAMP","TO/P","SIMP","MEXP","CMP","M.P","M1.P","M2.P","M.P.","M1.P.","M2.P.","P.","SMP","SRMP.","MP.","M1P.","M2P.""AMP.""SAMP.","TO/P.","RE/P.","MEXP.","SP","SRMSP","MSP","M1SP","M2SP","SAMSP",'SMSP',"TO/SP","AMSP","RE/SP","MEXSP","CMSP","M.SP"],
    
    "Folgas" : "Mais de 5 folgas seguidas",
    "Consecutivos": "Mais de 6 dias consecutivos",

    }



erros=[]
dia = 1

def adicionarErros(escala,erro,dia):

    erros.append(
        {
            'Nome' : escala["Nome"],
            'dia' : f'{dia}',
            'erro' : combos[erro]
        }
    )
    return erros
def limparErros():
    erros.clear()

def verificarFadiga(escala):

    turnos = escala["Turnos"]
    dias_seguidos = 0
    folgas = 0
    for i in range(len(turnos)):
        dia = i + 1
        turno_anterior =turnos[i-1]
        turno_atual= turnos[i]
        
        
        if i == len(turnos)-1:
            turno_seguinte = None
        else:
            turno_seguinte = turnos[i+1]
        
        if turno_atual not in combos["dispensas"] and turno_atual not in combos["folgas possíveis"]:
            dias_seguidos += 1
        elif turno_atual in combos["folgas possíveis"] and turno_anterior in combos["Pernoites"] :
            dias_seguidos += 1
        else:
            dias_seguidos = 0
        if i+1<len(turnos) :
            if dias_seguidos == 5 and turno_atual in combos["Pernoites"] and turnos[i + 2] not in combos["dispensas"]:
                sequencia="Consecutivos"
                adicionarErros(escala,sequencia,dia)
                dias_seguidos=0
            
            if (dias_seguidos > 5 and turno_anterior not in combos["Pernoites"] and (turnos[i+1] or turnos[i+2]) not in combos["dispensas"]) :
                sequencia="Consecutivos"
                adicionarErros(escala,sequencia,dia)
                dias_seguidos=0

        if turno_atual in combos["folgas possíveis"]:
            folgas += 1
        else:
            folgas = 0

        if folgas > 5 and turnos[i-6] not in combos["Pernoites"]:
            sequencia="Folgas"
            dia = i- 4
            adicionarErros(escala,sequencia,dia)
            folgas = 0
        #erros envolvendo pernoite
        if turno_anterior in combos["Pernoites"] and turno_atual not in combos["dispensas"] or turno_anterior in combos["Pernoites"] and turno_seguinte in combos["Manhas"]:
            erro= "erro pernoite"
            adicionarErros(escala,erro,dia)
        #erros envolvendo tarde
        if turno_atual in combos["Tardes"] and turno_seguinte in combos["Manhas"]:
            erro= "erro tarde"
            adicionarErros(escala,erro,dia)

        dia += 1

    return erros
