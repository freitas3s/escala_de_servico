from verificarFadiga import verificarFadiga,erros,limparErros
import tkinter as tk
from tkinter import  messagebox, ttk
import json
from copiarEscalaDrive import copiarEscala

def carregar_arquivo():
    copiarEscala()
    caminho = r"C:\Users\guije\Documents\GitHub\escala_de_servico\escala.json"
    if not caminho:
        return
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        if isinstance(dados, dict):
            dados = [dados]
        global escalas
        escalas = dados

        # 🧠 FORMATAÇÃO
        texto_formatado = ""
        for esc in escalas:
            nome = esc.get("Nome", "Sem nome")
            turnos = ", ".join(esc.get("Turnos", []))
            carga_horaria_mensal = esc.get("Carga Horaria Mensal", "NA")
            texto_formatado += f" {nome}\n {turnos}\n {carga_horaria_mensal}\n\n"

        mostrar_todos()
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao carregar o arquivo:\n{e}")

def editarTabela():
    # monta lista com nomes na ordem exibida
    ordem_exibida = []

    for item in tree_escalas.get_children():
        valores = tree_escalas.item(item)["values"]
        nome = valores[0]
        turnos = valores[1:-1]
        carga_horaria= valores[-1]
        ordem_exibida.append((nome, turnos,carga_horaria))

    # atualiza apenas operadores que estão visíveis
    for nome, turnos, carga_horaria in ordem_exibida:
        for operador in escalas:
            if operador["Nome"] == nome:
                operador["Turnos"] = turnos
                operador["CHM"] =carga_horaria
                break
    
def executar_verificacao():
    """Executa verificarFadiga() em todas as escalas e mostra os erros"""
    if not escalas:
        messagebox.showwarning("Aviso", "Nenhuma escala carregada!")
        return
    editarTabela()
    #limpa a lista de erros 
    limparErros()
    # processa todas as escalas e junta os resultados
    for escala in escalas:
        verificarFadiga(escala)

    # limpa tabela
    for item in tree.get_children():
        tree.delete(item)

    # exibe todos os erros retornados por adicionarErros()
    for e in erros:
        tree.insert("", "end", values=(e["Nome"], e["dia"], e["erro"]))

    messagebox.showinfo(
        "Concluído",
        f"Foram encontrados {len(erros)} erros."
    )
    

def atualizar_tabela_escalas(escalas):

    for item in tree_escalas.get_children():
        tree_escalas.delete(item)

    if not escalas:
        return

    max_dias = max(len(e["Turnos"]) for e in escalas)
    colunas = ["Nome"] + [f"{i+1}" for i in range(max_dias)] + ["CHM"]
    tree_escalas["columns"] = colunas
    tree_escalas["show"] = "headings"

    for col in colunas:
        tree_escalas.heading(col, text=col)
        tree_escalas.column(col, width=60 if col != "Nome" else 140)

    for e in escalas:
        nome = e["Nome"]
        turnos = e["Turnos"]
        carga_lista = e.get("Carga horaria mensal", [""])
        carga = carga_lista[0] if carga_lista else ""
        valores = [nome] + turnos + [""] * (max_dias - len(turnos))  + [carga]
        tree_escalas.insert("", "end", values=valores)

def editar_celula(event):
    item = tree_escalas.identify_row(event.y)
    coluna = tree_escalas.identify_column(event.x)

    if not item or not coluna:
        return

    # posição da célula
    x, y, largura, altura = tree_escalas.bbox(item, coluna)

    texto_atual = tree_escalas.set(item, coluna)

    # cria um entry sobre a célula selecionada
    entry = tk.Entry(tree_escalas)
    entry.place(x=x, y=y, width=largura, height=altura)
    entry.insert(0, texto_atual)
    entry.focus()

    # função que salva quando o usuário pressiona Enter
    def salvar(event):
        novo_valor = entry.get()
        tree_escalas.set(item, coluna, novo_valor)
        entry.destroy()

    entry.bind("<Return>", salvar)
    entry.bind("<FocusOut>", lambda e: entry.destroy())  # fecha se perder foco

def pesquisar_funcionario():
    """Filtra a tabela de escalas com base no nome pesquisado"""
    termo = entrada_pesquisa.get().strip().lower()
    if not termo:
        messagebox.showinfo("Pesquisa", "Digite o nome do operador.")
        mostrar_todos()
        return

    filtradas = [e for e in escalas if termo in e["Nome"].lower()]

    if not filtradas:
        messagebox.showinfo("Pesquisa", f"Operador '{termo}' não encontrado.")
        return

    # Atualiza a tabela com os resultados filtrados
    atualizar_tabela_escalas(filtradas)

    # Quando o usuário apertar ENTER na caixa de pesquisa, repete a busca
    # entrada_pesquisa.bind("<Return>", lambda event: atualizar_tabela_escalas(filtradas))

def mostrar_todos():
    """Restaura a exibição completa das escalas"""
    atualizar_tabela_escalas(escalas)
    entrada_pesquisa.delete(0, tk.END)


# ========= INTERFACE =========
janela = tk.Tk()
janela.title("Verificador de Fadiga")
janela.geometry("750x550")


# Botões


# === Campo de pesquisa ===
campo_pesquisa = tk.Frame(janela)
campo_pesquisa.pack(pady=10)

tk.Label(campo_pesquisa, text="Pesquisar operador:").grid(row=0, column=0, padx=5)
entrada_pesquisa = tk.Entry(campo_pesquisa, width=40)
entrada_pesquisa.grid(row=0, column=1, padx=5)
entrada_pesquisa.bind("<Return>", lambda event: pesquisar_funcionario())

tk.Button(campo_pesquisa, text="🔎 Pesquisar", command=pesquisar_funcionario).grid(row=0, column=2, padx=5)
tk.Button(campo_pesquisa, text="📋 Mostrar Todos", command=mostrar_todos).grid(row=0, column=3, padx=5)

# Tabela das escalas
tk.Label(janela, text="📋 Escala Matriz:").pack()
campo_escalas = tk.Frame(janela)
campo_escalas.pack(pady=5, fill="x")

tree_escalas = ttk.Treeview(campo_escalas)
tree_escalas.pack(side="left", fill="x", expand=True)

scroll_escalas = ttk.Scrollbar(
    campo_escalas, orient="horizontal", command=tree_escalas.xview
)
tree_escalas.configure(xscrollcommand=scroll_escalas.set)
scroll_escalas.pack(side="bottom", fill="x")
# ativa a edição com duplo clique
tree_escalas.bind("<Double-1>", editar_celula)

tk.Button(janela, text="📂 Carregar Escala", command=carregar_arquivo).pack(pady=4)
# tk.Button(janela, text="💾 Salvar alterações", command=salvarAlteracoes).pack(pady=4)
tk.Button(janela, text="🔍 Verificar Fadiga", command=executar_verificacao).pack(pady=4)

# Tabela de erros
cols = ("Nome", "Dia", "Erro")
tree = ttk.Treeview(janela, columns=cols, show="headings", height=10)
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=220)
tree.pack(pady=10, fill="x")


janela.mainloop()