import pandas as pd
import csv

caminho_df = r'C:\Users\guije\Documents\GitHub\escala_de_servico\ESCALAS RSP - SETEMBRO 2025 - ESCALAS RSP - SETEMBRO 2025.csv.csv'

df = pd.read_csv(caminho_df)
df=df.fillna('')
    
escala= [
    {"Nome": linha[0], "Turnos":list(linha[1:30]) }
    for linha in df.itertuples(index=False, name=None)
]