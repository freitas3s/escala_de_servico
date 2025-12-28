import streamlit as st
import pandas as pd
import copy
from verificarFadiga import verificarFadiga


def aplicar_troca(df, operador_a, operador_b, dia):
    col = f"D{dia}"

    turno_a = df.loc[df["Operador"] == operador_a, col].values[0]
    turno_b = df.loc[df["Operador"] == operador_b, col].values[0]

    df.loc[df["Operador"] == operador_a, col] = turno_b
    df.loc[df["Operador"] == operador_b, col] = turno_a

def listar_candidatos(df, operador_origem):
    return df[df["Operador"] != operador_origem]["Operador"].tolist()

def encontrar_trocas_possiveis(df, operador, dia):
    trocas_validas = []
    candidatos = listar_candidatos(df, operador)

    for candidato in candidatos:
        df_simulado = df.copy(deep=True)

        aplicar_troca(df_simulado, operador, candidato, dia)

        erros = verificarFadiga(df_simulado)

        if not erros:
            trocas_validas.append(candidato)

    return trocas_validas


st.title("🔄 Simulador de Trocas de Turno")

df_escala = st.session_state.df_escala
st.dataframe(df_escala, use_container_width=True)

st.subheader("Selecionar turno para troca")

operador_selecionado = st.selectbox(
    "Operador",
    df_escala["Operador"].tolist()
)

dia_selecionado = st.selectbox(
    "Dia",
    list(range(1, 32))
)

if st.button("🔍 Ver trocas possíveis"):
    trocas = encontrar_trocas_possiveis(
        df_escala,
        operador_selecionado,
        dia_selecionado
    )

    if trocas:
        st.success("Trocas possíveis encontradas:")
        st.table(pd.DataFrame({
            "Pode trocar com": trocas
        }))
    else:
        st.warning("Nenhuma troca possível sem violar fadiga.")
