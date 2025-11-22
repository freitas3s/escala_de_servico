from verificarFadiga import verificarFadiga, limparErros, verificarCargaHoraria, adicionarErros
from copiarEscalaDrive import copiarEscala, gerar_colunas_com_dia_semana, MESES
import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Escala", layout="wide")


# ----------------------
# Helpers / utilitários
# ----------------------
def escalas_para_df(escalas):
    """
    Converte lista de dicts (escalas) em DataFrame.
    Usa gerar_colunas_com_dia_semana para gerar os nomes das colunas (dinâmicos).
    Ajusta colunas de acordo com o número de turnos retornados.
    """
    if not escalas:
        return pd.DataFrame()

    # Quantidade de dias = quantidade de turnos no arquivo vindo do drive
    max_dias = max(len(e.get("Turnos", [])) for e in escalas)

    # Gera os nomes das colunas dinamicamente (começando 24 do mês anterior)
    colunas_dinamicas = gerar_colunas_com_dia_semana(
        st.session_state.ano,
        st.session_state.mes
    )

    # Ajusta para ter a mesma quantidade de colunas do arquivo
    while len(colunas_dinamicas) < max_dias:
        colunas_dinamicas.append(f"Dia {len(colunas_dinamicas)+1}")

# Se sobrar, corta
    colunas_dinamicas = colunas_dinamicas[:max_dias]

    # Colunas finais
    colunas = ["Nome"] + colunas_dinamicas + ["CHM"]

    # Monta dataframe
    tabela = []
    for e in escalas:
        ch_val = e.get("CHM") or e.get("Carga horaria mensal") or ""
        if isinstance(ch_val, list):
            ch_val = ch_val[0] if ch_val else ""
        linha = {"Nome": e.get("Nome", ""), "CHM": ch_val}
        for i, turno in enumerate(e.get("Turnos", [])):
            # coloca turno na coluna com nome dinâmico correspondente
            linha[colunas_dinamicas[i]] = turno
        tabela.append(linha)

    df = pd.DataFrame(tabela)

    # Garante colunas ausentes
    for c in colunas:
        if c not in df.columns:
            df[c] = ""

    df = df.reindex(columns=colunas)
    return df


def df_para_escalas(df):
    """
    Converte DataFrame de volta para lista de escalas (lista de dicts).
    Mantém a ordem das colunas tal como aparecem no DataFrame (exceto Nome/CHM).
    """
    if df is None or df.empty:
        return []

    col_dias = [c for c in df.columns if c not in ("Nome", "CHM")]  # mantém ordem
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
            "CHM": row.get("CHM", "")
        })
    return novas


def carregar_arquivo(mes=None):
    """
    Chama copiarEscala(mes) e atualiza session_state.
    Se mes for None, copiarEscala deve usar st.session_state.mes internamente ou padrão.
    """
    try:
        dados = copiarEscala(mes) or []
        st.session_state.escalas = dados  # lista de dict escala
        st.session_state.df_escalas = escalas_para_df(dados)  # dataframe da escala com colunas dinâmicas
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
        if termo in str(e.get("Nome", "")).lower()
    ]
    if not filtradas:
        st.warning(f"Operador '{termo}' não encontrado.")
        return
    # ao filtrar, geramos um df com as mesmas colunas dinâmicas (mesma quantidade)
    st.session_state.df_filtrado = escalas_para_df(filtradas)
    st.session_state.filtro_ativo = True


def dynamic_input_data_editor(data, key, **_kwargs):
    """
    Wrapper para contornar bug do data_editor (preserva initial data entre runs).
    """
    changed_key = f'{key}__changed_state'
    initial_data_key = f'{key}__initial_data'

    def on_data_editor_changed():
        if 'on_change' in _kwargs:
            args = _kwargs.get('args', ())
            kwargs = _kwargs.get('kwargs', {})
            _kwargs['on_change'](*args, **kwargs)

        st.session_state[changed_key] = True

    if changed_key in st.session_state and st.session_state[changed_key]:
        data = st.session_state[initial_data_key]
        st.session_state[changed_key] = False
    else:
        st.session_state[initial_data_key] = data

    __kwargs = _kwargs.copy()
    __kwargs.update({'data': data, 'key': key, 'on_change': on_data_editor_changed})

    return st.data_editor(**__kwargs)


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
    if not st.session_state.df_erros.empty:
        st.error(f"Foram encontrados {len(st.session_state.df_erros)} erros.", icon=":material/warning:")
    else:
        st.success("Nenhum erro encontrado", icon=":material/check:")


# ----------------------
# Inicia variáveis de sessão
# ----------------------
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


# ----------------------
# Layout
# ----------------------
st.title("Escala RSP")

st.subheader("Buscar Operador")
col1, col2 = st.columns([3, 1])

with col1:
    termo_pesquisa = st.text_input("", placeholder="Nome do operador", key="termo_pesquisa", on_change=pesquisar_funcionario)

with col2:
    if st.button("Buscar", icon=":material/search:"):
        pesquisar_funcionario()
    if st.button("Mostrar Todos", icon=":material/patient_list:"):
        st.session_state.df_filtrado = pd.DataFrame()
        st.session_state.filtro_ativo = False


if st.button(f"Escala de {MESES[datetime.datetime.now().month]}", icon=":material/calendar_month:"):
    st.session_state.mes =  datetime.datetime.now().month
    carregar_arquivo(st.session_state.mes)

if st.button(f"Escala de {MESES[datetime.datetime.now().month + 1]}", icon=":material/calendar_month:"):
    st.session_state.mes =  datetime.datetime.now().month + 1
    carregar_arquivo(st.session_state.mes)

st.header(f"Escala de {MESES[st.session_state.mes]}")

if st.button("Desfazer Alterações", icon=":material/refresh:"):
    carregar_arquivo(st.session_state.mes)
    limparErros()

# Mostrar tabela
if st.session_state.mostrar_tabela:
    # cria column_config dinâmico baseado nas colunas reais do df (Nome/CHM + dias dinâmicos)
    base_column_config = {
        "Nome": st.column_config.Column(disabled=True, pinned=True),
        "CHM": st.column_config.Column(disabled=True),
    }

    # adiciona colunas de dia automaticamente
    for col in st.session_state.df_escalas.columns:
        if col not in ("Nome", "CHM"):
            # ajuda (help) com o texto do cabeçalho para feriado/sáb/dom já com emoji vindo de gerar_colunas...
            base_column_config[col] = st.column_config.Column(
                help=f"Turno do dia {col}",
                width=100,
            )

    if st.session_state.filtro_ativo:
        df_editado = dynamic_input_data_editor(
            st.session_state.df_filtrado,
            key="editor_filtrado",
            use_container_width=True,
            column_config=base_column_config
        )
        if df_editado is not None:
            st.session_state.df_filtrado = df_editado.copy()
            atualizar_escala(df_editado)
    else:
        df_editado = dynamic_input_data_editor(
            st.session_state.df_escalas,
            key="editor_todos",
            use_container_width=True,
            hide_index=True,
            column_config=base_column_config
        )
        if df_editado is not None:
            st.session_state.df_escalas = df_editado.copy()

if st.button("Verificar Fadiga", icon=":material/download_done:", help="Carrega todas as suas edições e mostra se tem algum erro de fadiga."):
    executar_verificacao()

if not st.session_state.df_erros.empty:
    st.subheader("Erros Encontrados")
    st.dataframe(st.session_state.df_erros, use_container_width=True, hide_index=True)
