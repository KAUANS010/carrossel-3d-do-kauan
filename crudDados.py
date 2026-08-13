import json
import os
import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from PIL import Image, ImageGrab

ARQUIVO_DADOS = 'dados.json'
PASTA_IMAGENS = './imagens'

class AppCRUD:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Carrossel 3D - Kauan")
        self.root.geometry("950x650")
        self.root.minsize(850, 550)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=6, font=('Segoe UI', 10))
        style.configure("TLabel", font=('Segoe UI', 10))
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        style.configure("Treeview", font=('Segoe UI', 10), rowheight=25)

        self.dados = self.carregar_dados()
        self.indice_selecionado = None

        os.makedirs(PASTA_IMAGENS, exist_ok=True)

        self.criar_interface()
        self.atualizar_tabela()

    def carregar_dados(self):
        if os.path.exists(ARQUIVO_DADOS):
            try:
                with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler o arquivo JSON:\n{e}")
                return []
        return []

    def salvar_dados(self):
        try:
            with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
                json.dump(self.dados, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar o arquivo JSON:\n{e}")

    def criar_interface(self):
        # --- Frame Superior (Busca) ---
        frame_busca = ttk.Frame(self.root, padding="10")
        frame_busca.pack(fill=tk.X)

        ttk.Label(frame_busca, text="Buscar por Nome (Alt):").pack(side=tk.LEFT, padx=(0, 10))
        self.var_busca = tk.StringVar()
        self.var_busca.trace_add('write', self.filtrar_tabela)
        entry_busca = ttk.Entry(frame_busca, textvariable=self.var_busca, width=40)
        entry_busca.pack(side=tk.LEFT)

        # --- Frame Central (Tabela de Dados e Ordenação) ---
        frame_tabela = ttk.Frame(self.root, padding="10")
        frame_tabela.pack(fill=tk.BOTH, expand=True)

        # Botões de ordenação à direita
        frame_ordem = ttk.Frame(frame_tabela)
        frame_ordem.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        ttk.Button(frame_ordem, text="⬆️ Subir", command=self.mover_cima, width=10).pack(side=tk.TOP, pady=(40, 5))
        ttk.Button(frame_ordem, text="⬇️ Descer", command=self.mover_baixo, width=10).pack(side=tk.TOP, pady=5)

        # Barra de rolagem
        scrollbar = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tabela (Treeview)
        colunas = ("alt", "href", "img")
        self.tree = ttk.Treeview(frame_tabela, columns=colunas, show="headings", selectmode="browse", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)

        self.tree.heading("alt", text="Nome (Alt)")
        self.tree.heading("href", text="Link (Href)")
        self.tree.heading("img", text="Caminho da Imagem (Img)")
        
        self.tree.column("alt", width=200)
        self.tree.column("href", width=300)
        self.tree.column("img", width=300)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.selecionar_item)

        # --- Frame Inferior (Formulário) ---
        frame_form = ttk.LabelFrame(self.root, text="Dados do Item", padding="15")
        frame_form.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frame_form, text="Nome (Alt):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_alt = ttk.Entry(frame_form, width=72)
        self.entry_alt.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

        ttk.Label(frame_form, text="Link (Href):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_href = ttk.Entry(frame_form, width=72)
        self.entry_href.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)

        ttk.Label(frame_form, text="Imagem (Img):").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        frame_img_actions = ttk.Frame(frame_form)
        frame_img_actions.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        self.entry_img = ttk.Entry(frame_img_actions, width=38)
        self.entry_img.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(frame_img_actions, text="Upload", command=self.acao_upload, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_img_actions, text="Colar (Clip)", command=self.acao_clipboard, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_img_actions, text="Baixar URL", command=self.acao_url, width=10).pack(side=tk.LEFT, padx=2)

        frame_botoes = ttk.Frame(frame_form)
        frame_botoes.grid(row=3, column=0, columnspan=2, pady=15)

        ttk.Button(frame_botoes, text="Novo / Limpar", command=self.limpar_formulario).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Salvar Dados", command=self.salvar_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Excluir", command=self.excluir_item).pack(side=tk.LEFT, padx=5)

    def mover_cima(self):
        if self.indice_selecionado is None:
            messagebox.showwarning("Aviso", "Selecione um item na tabela para mover.")
            return
            
        idx = self.indice_selecionado
        if idx > 0:
            self.dados[idx], self.dados[idx-1] = self.dados[idx-1], self.dados[idx]
            self.salvar_dados()
            
            if self.var_busca.get():
                self.var_busca.set("")
            else:
                self.atualizar_tabela()
            
            novo_idx = idx - 1
            self.tree.selection_set(novo_idx)
            self.tree.focus(novo_idx)
            self.tree.see(novo_idx)

    def mover_baixo(self):
        if self.indice_selecionado is None:
            messagebox.showwarning("Aviso", "Selecione um item na tabela para mover.")
            return
            
        idx = self.indice_selecionado
        if idx < len(self.dados) - 1:
            self.dados[idx], self.dados[idx+1] = self.dados[idx+1], self.dados[idx]
            self.salvar_dados()
            
            if self.var_busca.get():
                self.var_busca.set("")
            else:
                self.atualizar_tabela()
            
            novo_idx = idx + 1
            self.tree.selection_set(novo_idx)
            self.tree.focus(novo_idx)
            self.tree.see(novo_idx)

    def gerar_caminho_imagem(self):
        alt_text = self.entry_alt.get().strip()
        if not alt_text:
            messagebox.showwarning("Aviso", "Preencha primeiro o campo 'Nome (Alt)'. Ele será o nome do arquivo da imagem.")
            return None
        
        nome_arquivo = alt_text.replace(" ", "_") + ".png"
        return os.path.join(PASTA_IMAGENS, nome_arquivo)

    def processar_e_salvar_imagem(self, img_obj):
        caminho = self.gerar_caminho_imagem()
        if not caminho:
            return

        try:
            img_obj = img_obj.convert("RGBA")
            img_obj = img_obj.resize((100, 100), Image.Resampling.LANCZOS)
            img_obj.save(caminho, "PNG")
            
            caminho_relativo = f"./imagens/{os.path.basename(caminho)}"
            self.entry_img.delete(0, tk.END)
            self.entry_img.insert(0, caminho_relativo)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao processar e salvar a imagem:\n{e}")

    def acao_upload(self):
        caminho_origem = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp *.gif *.bmp")]
        )
        if caminho_origem:
            try:
                img = Image.open(caminho_origem)
                self.processar_e_salvar_imagem(img)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao abrir arquivo de imagem:\n{e}")

    def acao_clipboard(self):
        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                self.processar_e_salvar_imagem(img)
            else:
                messagebox.showinfo("Aviso", "Nenhuma imagem válida encontrada na área de transferência.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao colar da área de transferência:\n{e}")

    def acao_url(self):
        url = simpledialog.askstring("Baixar da Web", "Insira o link direto (URL) da imagem:")
        if url:
            try:
                response = requests.get(url, stream=True, timeout=10)
                response.raise_for_status() 
                img = Image.open(response.raw)
                self.processar_e_salvar_imagem(img)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao baixar imagem pela URL:\n{e}")

    def atualizar_tabela(self, termo_busca=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for index, item in enumerate(self.dados):
            if termo_busca.lower() in item.get('alt', '').lower():
                self.tree.insert("", tk.END, iid=index, values=(item.get("alt"), item.get("href"), item.get("img")))

    def filtrar_tabela(self, *args):
        termo = self.var_busca.get()
        self.atualizar_tabela(termo)

    def selecionar_item(self, event):
        selecionado = self.tree.selection()
        if selecionado:
            self.indice_selecionado = int(selecionado[0])
            item = self.dados[self.indice_selecionado]
            
            self.limpar_formulario(manter_selecao=True)
            self.entry_alt.insert(0, item.get("alt", ""))
            self.entry_href.insert(0, item.get("href", ""))
            self.entry_img.insert(0, item.get("img", ""))

    def limpar_formulario(self, manter_selecao=False):
        self.entry_alt.delete(0, tk.END)
        self.entry_href.delete(0, tk.END)
        self.entry_img.delete(0, tk.END)
        if not manter_selecao:
            self.indice_selecionado = None
            self.tree.selection_remove(self.tree.selection())

    def salvar_item(self):
        alt = self.entry_alt.get().strip()
        href = self.entry_href.get().strip()
        img = self.entry_img.get().strip()

        if not alt or not href or not img:
            messagebox.showwarning("Aviso", "Todos os campos devem ser preenchidos!")
            return

        novo_item = {"href": href, "img": img, "alt": alt}

        if self.indice_selecionado is not None:
            self.dados[self.indice_selecionado] = novo_item
        else:
            self.dados.append(novo_item)

        self.salvar_dados()
        self.atualizar_tabela(self.var_busca.get())
        self.limpar_formulario()

    def excluir_item(self):
        if self.indice_selecionado is None:
            messagebox.showwarning("Aviso", "Selecione um item na tabela para excluir.")
            return

        resposta = messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este item?")
        if resposta:
            del self.dados[self.indice_selecionado]
            self.salvar_dados()
            self.atualizar_tabela(self.var_busca.get())
            self.limpar_formulario()

if __name__ == "__main__":
    root = tk.Tk()
    app = AppCRUD(root)
    root.mainloop()