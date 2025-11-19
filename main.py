from verificarFadiga import verificarFadiga,limparErros,verificarCargaHoraria,adicionarErros
from copiarEscalaDrive import copiarEscala
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Escala", layout="wide")

if "escalas" not in st.session_state:
    st.session_state.escalas = []

if "df_erros" not in st.session_state:
    st.session_state.df_erros = pd.DataFrame(columns=["Nome", "Dia", "Erro"])

def escalas_para_df(escalas):
    """Transforma lista de escalas em DataFrame editável"""
    if not escalas:
        return pd.DataFrame()
    
    max_dias = max(len(e.get("Turnos", [])) for e in escalas)
    colunas = ["Nome"] + [f"{i+1}" for i in range(max_dias)] + ["CHM"]

    tabela = []
    for e in escalas:
        # aceita tanto "CHM" quanto "Carga horaria mensal"
        ch_val = e.get("CHM")
        if ch_val in (None, ""):
            ch_val = e.get("Carga horaria mensal", "")
            # se vier como lista, pega o primeiro elemento
            if isinstance(ch_val, list):
                ch_val = ch_val[0] if ch_val else ""
        linha = {"Nome": e.get("Nome", ""), "CHM": ch_val}
        for i, turno in enumerate(e.get("Turnos", [])):
            linha[str(i+1)] = turno
        tabela.append(linha)
    df = pd.DataFrame(tabela)
    df = df.reindex(columns=colunas)
    return df

def carregar_arquivo():
    try:
        dados = copiarEscala()
        # atualiza a fonte de verdade
        st.session_state.escalas = dados or []
        # gera o df a partir do dado carregado (force refresh)
        st.session_state.df_escalas = escalas_para_df(st.session_state.escalas)
        # marca que acabamos de carregar uma nova escala (forçar exibição)
        st.session_state._df_last_source = "carregado"
        st.success("Escala carregada com sucesso!")
    except Exception as e:
        st.error(f"Falha ao carregar a escala: {e}")
def editarTabela():

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
            turnos.append(v.upper())

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
        carga_horaria = verificarCargaHoraria(esc)
        carga_horaria_maxima = float(esc.get("CHM", [0]))
        
        # Verifica se a carga excede
        if carga_horaria > carga_horaria_maxima:
            adicionarErros(esc, f"Carga Horária extrapolada {carga_horaria:.2f} de {carga_horaria_maxima} ", 1)

    

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

def pesquisar_funcionario():
    termo = st.session_state.termo_pesquisa.lower()
    df = st.session_state.df_escalas

    st.session_state.df_filtrado = df[df["Nome"].str.lower().str.contains(termo)]
    st.session_state.mostrar_tabela = True

# def mostrar_todos():
#     # Apenas exibe tudo SEM resetar as edições do usuário
#     st.session_state.df_escalas = escalas_para_df(st.session_state.escalas)

st.title("📋 Escala RSP ")

st.markdown("---")

st.header("🔎 Pesquisar Operador")
col1, col2 = st.columns([3,1])

with col1:
    termo_pesquisa = st.text_input("Pesquisar funcionário", key="termo_pesquisa", on_change=pesquisar_funcionario)


# with col2:
#     if st.button("🔎 Pesquisar"):
#         pesquisar_funcionario(termo_pesquisa)
#         st.session_state.mostrar_tabela = True  # habilita tabela  

# /if st.button("Listar Todos"):
#     st.session_state.mostrar_tabela = True
#     st.session_state.df_filtrado = st.session_state.df_escalas 

st.markdown("---")

st.header("Escala de Novembro")

# Botão carregar
if st.button("Carregar Escala Original"):
    carregar_arquivo()   # NÃO ASSIGNAR NADA
    st.session_state.df_escalas = escalas_para_df(st.session_state.escalas)
    st.session_state.df_escalas_original = st.session_state.df_escalas.copy()
    st.session_state.mostrar_tabela = True

# Mostra tabela SOMENTE se existir e se estiver habilitada
if st.session_state.get("mostrar_tabela", False):
    if "df_escalas" in st.session_state and not st.session_state.df_escalas.empty:

        df_editado = st.data_editor(
            st.session_state.df_escalas,
            num_rows="dynamic",
            use_container_width=True,
            key="tabela_escalas"
        )

        if df_editado is not None:
            st.session_state.df_escalas = df_editado.copy()
            st.session_state.df_escalas_original = df_editado.copy()
            editarTabela()  # atualiza st.session_state.escalas

if st.button(" Verificar Fadiga"):
    executar_verificacao()

if not st.session_state.df_erros.empty:
    st.subheader("Erros Encontrados:")
    st.dataframe(st.session_state.df_erros, use_container_width=True)