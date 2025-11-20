from verificarFadiga import verificarFadiga, limparErros, verificarCargaHoraria, adicionarErros
from copiarEscalaDrive import copiarEscala
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Escala", layout="wide")

# ----------------------
# Inicialização do session_state
# ----------------------
if "escalas" not in st.session_state:
    st.session_state.escalas = []


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

# ----------------------
# Funções auxiliares
# ----------------------
def escalas_para_df(escalas): #converte para dataframe
    if not escalas:
        return pd.DataFrame()
    
    max_dias = max(len(e.get("Turnos", [])) for e in escalas)
    colunas = ["Nome"] + [f"{i+1}" for i in range(max_dias)] + ["CHM"]

    tabela = []
    for e in escalas:
        ch_val = e.get("CHM") or e.get("Carga horaria mensal") or ""
        if isinstance(ch_val, list):
            ch_val = ch_val[0] if ch_val else ""
        linha = {"Nome": e.get("Nome", ""), "CHM": ch_val}
        for i, turno in enumerate(e.get("Turnos", [])):
            linha[str(i+1)] = turno
        tabela.append(linha)
    
    df = pd.DataFrame(tabela)
    for c in colunas:
        if c not in df.columns:
            df[c] = ""
    df = df.reindex(columns=colunas)
    return df

def df_para_escalas(df): # coloca as alterações no dict
    col_dias = [c for c in df.columns if c not in ("Nome", "CHM")]
    col_dias = sorted(col_dias, key=lambda x: int(x))
    novas = []
    for _, row in df.iterrows():
        turnos = []
        for c in col_dias:
            v = row.get(c, "")
            if pd.isna(v) or v is None:
                v = ""
            turnos.append(str(v).upper())
        novas.append({
            "Nome": row["Nome"],
            "Turnos": turnos,
            "CHM": row["CHM"]
        })
    return novas

def carregar_arquivo():
    try:
        dados = copiarEscala() or []
        st.session_state.escalas = dados #lista de dict escala
        st.session_state.df_escalas = escalas_para_df(dados)# dataframe da escala
        st.session_state.df_filtrado = pd.DataFrame() 
        st.session_state.filtro_ativo = False
        st.session_state.mostrar_tabela = True
        st.success("Escala carregada com sucesso!")
    except Exception as e:
        st.error(f"Falha ao carregar a escala: {e}")

def pesquisar_funcionario():
    termo = st.session_state.get("termo_pesquisa", "").strip().lower()
    if not termo:
        st.info("Digite o nome do operador.")
        return

    filtradas = [
        e for e in st.session_state.escalas
        if termo in str(e["Nome"]).lower()
    ]
    if st.session_state.escalas == [] :
        st.warning("Carregue uma escala antes!!")
        return
    if not filtradas:
        st.warning(f"Operador '{termo}' não encontrado.")
        return
    st.session_state.df_filtrado = escalas_para_df(filtradas)
    st.session_state.filtro_ativo = True

def atualizar_escala(df_editado):
    """Atualiza a lista de escalas principal a partir de um DataFrame editado"""
    if df_editado is None or df_editado.empty:
        return
    for i, row in df_editado.iterrows():
        nome = row["Nome"]
        idx = st.session_state.df_escalas[st.session_state.df_escalas["Nome"] == nome].index
        if len(idx) > 0:
            st.session_state.df_escalas.loc[idx[0]] = row

def executar_verificacao():
    if st.session_state.filtro_ativo:
        df_para_analisar = st.session_state.df_filtrado
    else:
        df_para_analisar = st.session_state.df_escalas

    st.session_state.escalas = df_para_escalas(df_para_analisar)

    if not st.session_state.escalas:
        st.warning("Nenhuma escala carregada")
        return

    limparErros()
    for esc in st.session_state.escalas:
        verificarFadiga(esc)
        carga_horaria = verificarCargaHoraria(esc)
        try:
            carga_horaria_maxima = float(esc.get("CHM", 0))
        except:
            carga_horaria_maxima = 0.0
        if carga_horaria > carga_horaria_maxima:
            adicionarErros(esc, f"Carga Horária extrapolada {carga_horaria:.2f} de {carga_horaria_maxima}", 1)
    st.success(f"Foram encontrados {len(st.session_state.df_erros)} erros.")

# ----------------------
# Layout
# ----------------------
st.title("Escala RSP")
st.markdown("---")
st.header("Pesquisar Operador")

col1, col2 = st.columns([3,1])

with col1:
    st.text_input("",placeholder="nome do operador", key="termo_pesquisa", on_change=pesquisar_funcionario, )

with col2:
    if st.button("Pesquisar",icon=":material/search:"):
        pesquisar_funcionario()
        
    if st.button("Listar Todos"):
        st.session_state.df_filtrado = pd.DataFrame()
        st.session_state.filtro_ativo = False

st.markdown("---")


st.header("Escala de Novembro")

if st.button("Carregar Escala Original"):
    carregar_arquivo()

# Mostrar tabela
if st.session_state.mostrar_tabela:
    if st.session_state.filtro_ativo:
        df_editado = st.data_editor(
            st.session_state.df_filtrado,
            key="editor_filtrado",
            use_container_width=True,
            hide_index=True,
            column_config={
                "Nome": st.column_config.Column(disabled=True,pinned=True),
                "CHM": st.column_config.Column(disabled=True,pinned=True),
                **{str(i): st.column_config.Column(validate=None)
                for i in st.session_state.df_filtrado.columns if i not in ("Nome", "CHM")
                }
            }
        )
        st.session_state.df_filtrado = df_editado.copy()
    else:
        df_editado = st.data_editor(
            st.session_state.df_escalas,
            key="editor_todos",
            use_container_width=True,
            hide_index= True,
            column_config={
                "Nome": st.column_config.Column(disabled=True,pinned=True),
                "CHM": st.column_config.Column(disabled=True,pinned=True),
                **{str(i): st.column_config.Column(validate=None)
                for i in st.session_state.df_filtrado.columns if i not in ("Nome", "CHM")
                }
            }

        )
        st.session_state.df_escalas = df_editado.copy()

if st.button("Verificar Fadiga"):
    executar_verificacao()

if not st.session_state.df_erros.empty:
    st.subheader("Erros Encontrados:")
    st.dataframe(st.session_state.df_erros, use_container_width=True)
