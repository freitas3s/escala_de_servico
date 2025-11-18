from verificarFadiga import verificarFadiga,limparErros,verificarCargaHoraria,adicionarErros
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
    """Transforma lista de escalas em DataFrame editável"""
    if not escalas:
        return pd.DataFrame()
    
    max_dias = max(len(e["Turnos"]) for e in escalas)
    colunas = ["Nome"] + [f"{i+1}" for i in range(max_dias)] + ["CHM"]

    tabela = []
    for e in escalas:
        linha = {"Nome": e["Nome"], "CHM": e.get("Carga horaria mensal", [""])[0]}
        for i, turno in enumerate(e["Turnos"]):
            linha[str(i+1)] = turno
        tabela.append(linha)
    df = pd.DataFrame(tabela)
    df = df.reindex(columns=colunas)
    return df

def carregar_arquivo():
    try:
        dados = copiarEscala()
        st.session_state.escalas = dados
        st.session_state.df_escalas = escalas_para_df(dados)
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
            adicionarErros(esc, f"Carga Horária extrapolada {carga_horaria} de {carga_horaria_maxima} ", 1)

    

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
    filtradas = [
        e for e in st.session_state.escalas
        if "Nome" in e and termo in str(e["Nome"]).lower()
    ]
    if not filtradas:
        st.warning(f"Operador '{termo}' não encontrado.")
        return
    st.session_state.df_escalas = escalas_para_df(filtradas)

def mostrar_todos():
    st.session_state.df_escalas = escalas_para_df(st.session_state.escalas)



st.title("📋 Escala RSP ")

st.markdown("---")

st.header("🔎 Pesquisar Operador")
col1, col2 = st.columns([3,1])

with col1:
    termo_pesquisa = st.text_input("")

with col2:
    if st.button("🔎 Pesquisar"):
        pesquisar_funcionario(termo_pesquisa)
        st.session_state.mostrar_tabela = True  # habilita tabela

    if st.button("Listar Todos"):
        mostrar_todos()
        st.session_state.mostrar_tabela = True  # habilita tabela

st.markdown("---")

st.header("Escala de Novembro")

# Botão carregar
if st.button("Carregar Escala Original"):
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

if st.button(" Verificar Fadiga"):
    executar_verificacao()

if not st.session_state.df_erros.empty:
    st.subheader("Erros Encontrados:")
    st.dataframe(st.session_state.df_erros, use_container_width=True)

# st.set_page_config(page_title="Escala", layout="wide")
# # Inicialização dos estados
# if "escalas" not in st.session_state:
#     st.session_state.escalas = []

# if "df_erros" not in st.session_state:
#     st.session_state.df_erros = pd.DataFrame(columns=["Nome", "Dia", "Erro"])
    
# def escalas_para_df(escalas):
#     """Transforma lista de escalas em DataFrame editável"""
#     if not escalas:
#         return pd.DataFrame()
    
#     max_dias = max(len(e["Turnos"]) for e in escalas)
#     colunas = ["Nome"] + [f"{i+1}" for i in range(max_dias)] + ["CHM"]

#     tabela = []
#     for e in escalas:
#         linha = {"Nome": e["Nome"], "CHM": e.get("Carga horaria mensal", [""])[0]}
#         for i, turno in enumerate(e["Turnos"]):
#             linha[str(i+1)] = turno
#         tabela.append(linha)
#     df = pd.DataFrame(tabela)
#     df = df.reindex(columns=colunas)
#     return df


# def carregar_arquivo():
#     try:
#         dados = copiarEscala()
#         st.session_state.escalas = dados
#         st.session_state.df_escalas = escalas_para_df(dados)
#         st.success("Escala carregada com sucesso!")
#     except Exception as e:
#         st.error(f"Falha ao carregar a escala: {e}")

# def editarTabela():
#     import pandas as pd

#     df = st.session_state.get("df_escalas", pd.DataFrame())
#     if df.empty:
#         st.session_state.escalas = []
#         return

#     col_dias = [c for c in df.columns if c not in ("Nome", "CHM")]
#     col_dias = sorted(col_dias, key=lambda x: int(x))

#     novas = []

#     for _, row in df.iterrows():
#         nome = row.get("Nome", "")

#         turnos = []
#         for c in col_dias:
#             v = row.get(c, "")
#             if pd.isna(v) or v is None:
#                 v = ""
#             turnos.append(v)

#         ch = row.get("CHM", "")
#         if isinstance(ch, list):
#             ch = ch[0] if ch else ""

#         novas.append({
#             "Nome": nome,
#             "Turnos": turnos,
#             "CHM": ch
#         })

#     st.session_state.escalas = novas

# def executar_verificacao():
#     if "df_escalas" in st.session_state:
#         editarTabela()   # converte df -> listas em st.session_state.escalas

#     if not st.session_state.escalas:
#         st.warning("Nenhuma escala carregada")
#         return

#     limparErros()
#     for esc in st.session_state.escalas:
#         verificarFadiga(esc)
#     st.success(f"Foram encontrados {len(st.session_state.df_erros)} erros.")

# def atualizar_tabela_escalas(escalas):
#     if not escalas:
#         st.session_state.df_escalas = pd.DataFrame()
#         return

#     max_dias = max(len(e["Turnos"]) for e in escalas)
#     colunas = ["Nome"] + [f"{i+1}" for i in range(max_dias)] + ["CHM"]

#     tabela = []

#     for e in escalas:
#         linha = {"Nome": e["Nome"], "CHM": e.get("CHM", "")}

#         # Preenche os turnos
#         for i, turno in enumerate(e["Turnos"]):
#             linha[str(i+1)] = turno

#         tabela.append(linha)

#     df = pd.DataFrame(tabela)
#     df = df.reindex(columns=colunas)  # garante ordem e colunas obrigatórias

#     st.session_state.df_escalas = df

# def pesquisar_funcionario(termo):
#     termo = termo.strip().lower()
#     if not termo:
#         st.info("Digite o nome do operador.")
#         mostrar_todos()
#         return
#     filtradas = [e for e in st.session_state.escalas if termo in e["Nome"].lower()]
#     if not filtradas:
#         st.warning(f"Operador '{termo}' não encontrado.")
#         return
#     st.session_state.df_escalas = escalas_para_df(filtradas)

# def mostrar_todos():
#     st.session_state.df_escalas = escalas_para_df(st.session_state.escalas)


# st.title("📋 Escala RSP ")

# st.markdown("---")

# st.header("🔎 Pesquisar Operador")
# col1, col2 = st.columns([3,1])

# with col1:
#     termo_pesquisa = st.text_input("")

# with col2:
#     if st.button("🔎 Pesquisar"):
#         pesquisar_funcionario(termo_pesquisa)
#         st.session_state.mostrar_tabela = True  # habilita tabela

#     if st.button("Listar Todos"):
#         mostrar_todos()
#         st.session_state.mostrar_tabela = True  # habilita tabela

# st.markdown("---")

# st.header("Escala de Novembro")

# # Botão carregar
# if st.button("Carregar Escala Original"):
#     st.session_state.escalas = copiarEscala()
#     st.session_state.mostrar_tabela = True

# # Mostra tabela SOMENTE se existir e se estiver habilitada
# if st.session_state.get("mostrar_tabela", False):
#     if "df_escalas" in st.session_state and not st.session_state.df_escalas.empty:
#         df_editado = st.data_editor(
#             st.session_state.df_escalas,
#             num_rows="dynamic",
#             use_container_width=True
#         )
#         # Só atualiza aqui, evitando recursão infinita
#         st.session_state.df_escalas = df_editado

# if st.button(" Verificar Fadiga"):
#     executar_verificacao()

# if not st.session_state.df_erros.empty:
#     st.subheader("Erros Encontrados:")
#     st.dataframe(st.session_state.df_erros, use_container_width=True