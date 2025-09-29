

combos={
    ("T","M"):"Manhã após Tarde",
    ("T","M1") : "Manhã após Tarde",
    ("T","MP") : "Manhã após Tarde",
    ("T","M1P") : "Manhã após Tarde",
    ("P","M"):"Manha apos pernoite",
    ("P","M1"):"Manha apos pernoite",
    ("P","T"): "Tarde apos pernoite",
    ("MP","T"): "Tarde apos pernoite",
    ("P","F","M") : "necessario 24 horas apos pernoite",
    ("P","F","M1") : "necessario 24 horas apos pernoite",
    ("P","F","MP"): "necessario 24 horas apos pernoite",
    ("P","F","M1P"):"necessario 24 horas apos pernoite",
    ("MP","F","M"):"necessario 24 horas apos pernoite",
    ("MP","F","M1"):"necessario 24 horas apos pernoite",
    ("MP","F","MP"):"necessario 24 horas apos pernoite",
    ("MP","F","M1P"):"necessario 24 horas apos pernoite",
    "dispensas": ["DM","A","FE","OS","EX","CP","CM","CT","AM","AT","SAM","SAT","SAMP","","F"],
    "Folgas" : "Mais de 5 folgas seguidas",
    "Pernoites" : ["MP","M1P","M2P","P"],
    "Consecutivos": "Mais de 6 dias consecutivos"
    }


erros=[]
dia = 1

def adicionarErros(escala,sequencia,dia):
    erros.append(
        {
            'nome' : escala["Nome"],
            'dia' : f'{dia}',
            'erro' : combos[sequencia]
        }
    )
    return erros


def verificarFadiga(escala):
    
    turnos = escala["Turnos"]
    dias_seguidos = 0
    folgas = 0
    for i in range(len(turnos)):
        dia = i + 1
        turno_anterior =turnos[i-1]
        turno_atual= turnos[i]
        sequencia_2 =(turno_anterior,turno_atual)
        # if para evitar erro de indice com a variável "turno seguinte"
        if i == len(turnos)-1:
            turno_seguinte = None
        else:
            turno_seguinte = turnos[i+1]

        sequencia_3=(turno_anterior,turno_atual,turno_seguinte)
        
        if turno_atual not in combos["dispensas"] and turno_atual!= '':
            dias_seguidos += 1
        elif turno_atual == '' and turno_anterior in combos["Pernoites"] :
            dias_seguidos += 1
        else:
            dias_seguidos = 0
        if i<len(turnos):
            if (dias_seguidos > 5 and turnos[i] not in combos["Pernoites"] and (turnos[i+1] or turnos[i+2]) not in combos["dispensas"]) :
                sequencia="Consecutivos"
                adicionarErros(escala,sequencia,dia)
                sequencia_3=(turno_anterior,turno_atual,turno_seguinte)
                dias_seguidos=0        


        if turno_atual == '':
            folgas += 1
        else:
            folgas = 0

        if folgas > 5 and turnos[i-6] not in combos["Pernoites"]:
            sequencia="Folgas"
            dia = i- 4
            adicionarErros(escala,sequencia,dia)
            folgas = 0
        sequencia_3=(turno_anterior,turno_atual,turno_seguinte)

        if sequencia_2 in combos:
            adicionarErros(escala,sequencia_2,dia)
        if sequencia_3 in combos:
            adicionarErros(escala,sequencia_3,dia+1)


        dia += 1

    return erros


