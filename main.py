from verificarFadiga import verificarFadiga,limparErros
import json
from copiarEscalaDrive import copiarEscala
import streamlit as st
import pandas as pd
st.set_page_config(page_title="Escala", layout="wide")
# Inicialização dos estados
if "escalas" not in st.session_state:
    st.session_state.escalas = []

if "df_erros" not in st.session_state:
    st.session_state.df_erros = pd.DataFrame(columns=["Nome", "Dia", "Erro"])

def escalas_para_df(escalas):
    
    if not escalas:
        return pd.DataFrame()

    max_dias = max(len(e.get("Turnos", [])) for e in escalas)
    cols = ["Nome"] + [str(i+1) for i in range(max_dias)] + ["CHM"]

    linhas = []
    for e in escalas:
        linha = {"Nome": e.get("Nome", "")}

        turnos = e.get("Turnos", []) or []
        turnos = turnos + [""] * (max_dias - len(turnos))

        for i, t in enumerate(turnos):
            linha[str(i+1)] = "" if t is None else t

        ch = e.get("Carga horaria mensal", e.get("Carga horaria mensal", ""))
        if isinstance(ch, list):
            ch = ch[0] if ch else ""

        linha["CHM"] = ch
        linhas.append(linha)

    return pd.DataFrame(linhas, columns=cols)

def carregar_arquivo():
    try:
        # copia escala direto da planilha (em memória)
        dados = copiarEscala()  

        # popula session_state
        st.session_state.escalas = dados
        st.session_state.df_escalas = escalas_para_df(dados)

        mostrar_todos()
        st.success("Escala carregada com sucesso!")

    except Exception as e:
        st.error(f"Falha ao carregar a escala: {e}")
        
def editarTabela():
    import pandas as pd

    df = st.session_state.get("df_escalas", pd.DataFrame())
    if df.empty:
        st.session_state.escalas = []
        return

    col_dias = [c for c in df.columns if c not in ("Nome", "CHM")]
    col_dias = sorted(col_dias, key=lambda x: int(x))

    novas = []

    for _, row in df.iterrows():
        nome = row.get("Nome", "")

        turnos = []
        for c in col_dias:
            v = row.get(c, "")
            if pd.isna(v) or v is None:
                v = ""
            turnos.append(v)

        ch = row.get("CHM", "")
        if isinstance(ch, list):
            ch = ch[0] if ch else ""

        novas.append({
            "Nome": nome,
            "Turnos": turnos,
            "CHM": ch
        })

    st.session_state.escalas = novas

def executar_verificacao():
    if "df_escalas" in st.session_state:
        editarTabela()   # converte df -> listas em st.session_state.escalas

    if not st.session_state.escalas:
        st.warning("Nenhuma escala carregada")
        return

    limparErros()
    for esc in st.session_state.escalas:
        verificarFadiga(esc)
    st.success(f"Foram encontrados {len(st.session_state.df_erros)} erros.")

def atualizar_tabela_escalas(escalas):
    if not escalas:
        st.session_state.df_escalas = pd.DataFrame()
        return

    max_dias = max(len(e["Turnos"]) for e in escalas)
    colunas = ["Nome"] + [f"{i+1}" for i in range(max_dias)] + ["CHM"]

    tabela = []

    for e in escalas:
        linha = {"Nome": e["Nome"], "CHM": e.get("CHM", "")}

        # Preenche os turnos
        for i, turno in enumerate(e["Turnos"]):
            linha[str(i+1)] = turno

        tabela.append(linha)

    df = pd.DataFrame(tabela)
    df = df.reindex(columns=colunas)  # garante ordem e colunas obrigatórias

    st.session_state.df_escalas = df

def pesquisar_funcionario(termo):
    termo = termo.strip().lower()

    if not termo:
        st.info("Digite o nome do operador.")
        mostrar_todos()
        return

    filtradas = [e for e in st.session_state.escalas if termo in e["Nome"].lower()]

    if not filtradas:
        st.warning(f"Operador '{termo}' não encontrado.")
        return

    atualizar_tabela_escalas(filtradas)

def mostrar_todos():
    atualizar_tabela_escalas(st.session_state.escalas)


st.title("📋 Sistema de Escala ")

st.header("🔎 Pesquisa de Operador")
col1, col2 = st.columns([3,1])

with col1:
    termo_pesquisa = st.text_input("Pesquisar operador:")

with col2:
    if st.button("🔎 Pesquisar"):
        pesquisar_funcionario(termo_pesquisa)
        st.session_state.mostrar_tabela = True  # habilita tabela

    if st.button("📋 Mostrar Todos"):
        mostrar_todos()
        st.session_state.mostrar_tabela = True  # habilita tabela

st.markdown("---")

st.header("📂 Escala Matriz")

# Botão carregar
if st.button("Carregar Escala"):
    st.session_state.escalas = copiarEscala()
    st.session_state.mostrar_tabela = True

# Mostra tabela SOMENTE se existir e se estiver habilitada
if st.session_state.get("mostrar_tabela", False):
    if "df_escalas" in st.session_state and not st.session_state.df_escalas.empty:
        df_editado = st.data_editor(
            st.session_state.df_escalas,
            num_rows="dynamic",
            use_container_width=True
        )
        # Só atualiza aqui, evitando recursão infinita
        st.session_state.df_escalas = df_editado

st.markdown("---")

st.header("⚠️ Verificação de Fadiga")

if st.button("🔍 Verificar Fadiga"):
    executar_verificacao()

# Mostra erros
if not st.session_state.df_erros.empty:
    st.subheader("Erros Encontrados:")
    st.dataframe(st.session_state.df_erros, use_container_width=True)
