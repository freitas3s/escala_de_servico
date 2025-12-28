import streamlit as st
import datetime
from copiarEscalaDrive import copiarEscala
from main import carregar_arquivo
import pandas as pd

if "mes" not in st.session_state:
    st.session_state.mes = datetime.datetime.now().month
if "ano" not in st.session_state:
    st.session_state.ano = datetime.datetime.now().year
if "escalas" not in st.session_state:
    st.session_state.escalas = []
    # carrega automaticamente na primeira vez
    carregar_arquivo(st.session_state.mes)
if "df_escalas" not in st.session_state:
    st.session_state.df_escalas = pd.DataFrame()
if "df_filtrado" not in st.session_state:
    st.session_state.df_filtrado = pd.DataFrame()
if "filtro_ativo" not in st.session_state:
    st.session_state.filtro_ativo = False
if "df_erros" not in st.session_state:
    st.session_state.df_erros = pd.DataFrame(columns=["Nome", "Dia", "Erro"])
if "mostrar_tabela" not in st.session_state:
    st.session_state.mostrar_tabela = False

pg = st.navigation([
    st.Page("main.py", title="Home"),
    st.Page("verificarTrocas.py", title="Verificar Trocas"),

],
    position = "top"
)

pg.run()