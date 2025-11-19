# Escala RSP – Aplicativo de Gerenciamento de Turnos

Este é um aplicativo web desenvolvido em **Python** com **Streamlit** para gerenciar escalas de trabalho, verificar cargas horárias e detectar possíveis erros ou fadiga entre operadores. Ele busca os dados diretamente do Google Sheets, permite edição interativa e análise em tempo real.

---

## 📝 Funcionalidades

1. **Carregar Escala Original**  
   - Busca automaticamente os dados de um Google Sheet configurado.
   - Organiza nomes, turnos e carga horária mensal em uma tabela editável.

2. **Filtrar Operadores**  
   - Permite pesquisar por nome.
   - Mostra apenas os operadores filtrados, mantendo a possibilidade de edição.

3. **Edição de Escala**  
   - A tabela é totalmente editável dentro do app.
   - Alterações feitas na tabela filtrada são refletidas na lista principal.

4. **Verificação de Fadiga e Carga Horária**  
   - Verifica se o operador cumpre regras de descanso e folgas.  
   - Detecta turnos consecutivos, excesso de folgas seguidas ou carga horária extrapolada.  
   - Erros são listados em uma tabela de forma clara e interativa.

---

## 📂 Estrutura de Arquivos

├─ main.py # Interface principal do Streamlit
├─ verificarFadiga.py # Funções de verificação de fadiga e carga horária
├─ copiarEscalaDrive.py # Função para ler os dados do Google Sheets
├─ README.md # Este arquivo


---

##  Instalação

1. Clone o repositório:
bash git clone <URL_DO_REPOSITORIO>
      cd <NOME_DO_REPOSITORIO>

2. Crie um ambiente virtual (opcional, mas recomendado):
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

3. Instale as dependências:

pip install -r requirements.txt

Dependências principais:

streamlit
pandas
gspread
google-auth

 Configuração do Google Drive

O app acessa um Google Sheet usando Service Account. Para isso:

Crie uma Service Account no Google Cloud.
Gere a chave JSON e adicione como secret no Streamlit:
st.secrets["GDRIVE_KEY"] = <CONTEÚDO_DO_JSON>
Compartilhe a planilha com o e-mail da Service Account.

Como Usar.
Execute o aplicativo:
streamlit run main.py


Carregar Escala Original: carrega os dados da planilha e exibe a tabela.
Pesquisar Operador: digite o nome para filtrar a tabela.
A edição ainda é possível mesmo com filtro ativo.
Editar Turnos e Carga Horária: clique nas células da tabela para alterar valores.
Verificar Fadiga: clique no botão para executar todas as validações:
Carga horária máxima
Folgas seguidas
Dias consecutivos
Turnos tarde → manhã
Pernoites sem descanso adequado
Erros Encontrados: a tabela de erros será exibida abaixo, mostrando dia e tipo de erro.

  Regras de Verificação

As regras são definidas em verificarFadiga.py:
Carga Horária: Cada tipo de turno possui valor específico em horas.
Folgas: Mais de 5 folgas consecutivas gera alerta.
Dias consecutivos: Mais de 6 dias seguidos de trabalho sem descanso adequado gera alerta.
Turnos Tarde → Manhã: Não permitido; gera alerta.
Pernoites: Necessário 24h de folga após pernoite.
  
  Observações

As alterações feitas na tabela filtrada atualizam a lista principal.
O botão “Listar Todos” mostra novamente todos os operadores sem resetar edições.
O app não salva alterações no Google Sheets; apenas manipula os dados localmente.

Sugestão de Melhorias

Implementar salvamento das alterações no Google Sheets.
Adicionar alertas visuais ou cores na tabela para destacar erros.
Criar histórico de escalas para comparação mensal.

 Tecnologias Utilizadas

Python 3.10+
Streamlit
Pandas
Google Sheets API (gspread, google-auth)
