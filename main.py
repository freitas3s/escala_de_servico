from verificarFadiga import verificarFadiga,erros
from copiarEscala import escala

# escala = [
#     {
#     "nome": "Hayanne",
#     "Turnos" : ['','','','','T','M','','','','','','','','','M2','M','','M2P','','','T1','','T','T','T1','','M2P','','M2P','','','M1P','','','T1','T','','P','','',]
#     },
#     {
#     "nome": "Pedro",
#     "Turnos" : ['','','','','T','M','','P','','','','','P','','M2','M','','M2P','','','T1','','T','T','T1','','M2P','','M2P','','','M1P','','','T1','T','','P','','',]
#     },
#     {
#     "nome": "Freitas",
#     "Turnos" : ['','','','','T','M','','P','','M','','','','','M2','M','','M2P','','','T1','','T','T','T1','','M2P','','M2P','','','M1P','','','T1','T','','P','','',]
#     },


# ]
# def adicionarOperador():
#     escala['nome'] = input("Operador: ") 4 8 10 19
#     escala['Turnos'] = [input("Turno dia "+ str(i + 1) + " :") for i in range(30)]

if __name__ == '__main__':
    for operador in escala:
        verificarFadiga(operador)
    print(erros)