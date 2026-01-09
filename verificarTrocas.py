# import streamlit as st
# import pandas as pd
# import copy
# from verificarFadiga import verificarFadiga_pura

# if "mes" not in st.session_state:
#     st.session_state.mes = datetime.datetime.now().month
# if "ano" not in st.session_state:
#     st.session_state.ano = datetime.datetime.now().year
# if "escalas" not in st.session_state:
#     st.session_state.escalas = []
#     # carrega automaticamente na primeira vez
#     carregar_arquivo(st.session_state.mes)
# if "df_escalas" not in st.session_state:
#     st.session_state.df_escalas = pd.DataFrame()
# if "df_filtrado" not in st.session_state:
#     st.session_state.df_filtrado = pd.DataFrame()
# if "filtro_ativo" not in st.session_state:
#     st.session_state.filtro_ativo = False
# if "df_erros" not in st.session_state:
#     st.session_state.df_erros = pd.DataFrame(columns=["Nome", "Dia", "Erro"])
# if "mostrar_tabela" not in st.session_state:
#     st.session_state.mostrar_tabela = False


# def aplicar_troca(df, operador_a, operador_b, dia):
#     col = f"D{dia}"

#     turno_a = df.loc[df["Operador"] == operador_a, col].values[0]
#     turno_b = df.loc[df["Operador"] == operador_b, col].values[0]

#     df.loc[df["Operador"] == operador_a, col] = turno_b
#     df.loc[df["Operador"] == operador_b, col] = turno_a

# def listar_candidatos(df, operador_origem):
#     return df[df["Operador"] != operador_origem]["Operador"].tolist()

# def encontrar_trocas_possiveis(df, operador, dia):
#     trocas_validas = []
#     candidatos = listar_candidatos(df, operador)

#     for candidato in candidatos:
#         df_simulado = df.copy(deep=True)

#         aplicar_troca(df_simulado, operador, candidato, dia)

#         erros = verificarFadiga_pura(df_simulado)

#         if not erros:
#             trocas_validas.append(candidato)

#     return trocas_validas


# st.title("🔄 Simulador de Trocas de Turno")

# if "df_escalas" not in st.session_state:
#     st.session_state.df_escalas = pd.DataFrame()

# st.dataframe(st.session_state.df_escala, use_container_width=True)

# st.subheader("Selecionar turno para troca")

# operador_selecionado = st.selectbox(
#     "Operador",
#     st.session_state.df_escala["Operador"].tolist()
# )

# dia_selecionado = st.selectbox(
#     "Dia",
#     list(range(1, 32))
# )

# if st.button("🔍 Ver trocas possíveis"):
#     trocas = encontrar_trocas_possiveis(
#         st.session_state.df_escala,
#         operador_selecionado,
#         dia_selecionado
#     )

#     if trocas:
#         st.success("Trocas possíveis encontradas:")
#         st.table(pd.DataFrame({
#             "Pode trocar com": trocas
#         }))
#     else:
#         st.warning("Nenhuma troca possível sem violar fadiga.")
