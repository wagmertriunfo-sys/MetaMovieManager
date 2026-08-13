import os
import requests
import shutil
from io import BytesIO
from PIL import Image, ImageTk
import customtkinter as ctk

# Configuração inicial do tema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ==================== SUAS CHAVES DE API ====================
# Insira suas chaves aqui antes de rodar o programa
TMDB_API_KEY = "SUA_CHAVE_TMDB_AQUI"
PORNDB_API_TOKEN = "SEU_TOKEN_PORNDB_AQUI"
# ============================================================

class MetaMovieManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MetaMovie Manager - Linux Edition")
        self.geometry("1150x750")

        # Configurar o ícone da janela com a logo personalizada
        try:
            caminho_icone = os.path.expanduser("~/.local/share/icons/metamovie_logo.png")
            if not os.path.exists(caminho_icone):
                caminho_icone = os.path.expanduser("~/logo_metamovie.png")
            if os.path.exists(caminho_icone):
                img_icone = Image.open(caminho_icone)
                self.iconphoto(False, ImageTk.PhotoImage(img_icone))
        except Exception as e:
            print(f"Erro ao definir ícone da janela: {e}")

        self.download_path = os.path.expanduser("~/Downloads")
        self.arquivo_selecionado = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Painel Esquerdo: Lista de Vídeos e Botão de Refresh
        self.frame_esquerda = ctk.CTkFrame(self, width=300)
        self.frame_esquerda.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.label_titulo_esq = ctk.CTkLabel(
            self.frame_esquerda, 
            text="Vídeos na Pasta Download", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.label_titulo_esq.pack(padx=10, pady=(10, 5))

        self.btn_refresh = ctk.CTkButton(
            self.frame_esquerda, 
            text="🔄 Atualizar Lista", 
            fg_color="#333333", 
            hover_color="#444444",
            height=30,
            command=self.carregar_videos_pasta
        )
        self.btn_refresh.pack(padx=10, pady=(0, 10), fill="x")

        self.scroll_arquivos = ctk.CTkScrollableFrame(self.frame_esquerda, width=280, height=570)
        self.scroll_arquivos.pack(padx=5, pady=5, fill="both", expand=True)

        # Painel Direito: Busca e Abas
        self.frame_direita = ctk.CTkFrame(self)
        self.frame_direita.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.frame_direita.grid_rowconfigure(1, weight=1)
        self.frame_direita.grid_columnconfigure(0, weight=1)

        self.frame_busca = ctk.CTkFrame(self.frame_direita, fg_color="transparent")
        self.frame_busca.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.entry_busca = ctk.CTkEntry(self.frame_busca, placeholder_text="Digite o nome para buscar...", width=500)
        self.entry_busca.pack(side="left", padx=(0, 10))

        self.btn_buscar = ctk.CTkButton(
            self.frame_busca, 
            text="Buscar nas APIs", 
            fg_color="#1f538d", 
            command=self.executar_busca_apis
        )
        self.btn_buscar.pack(side="left")

        self.tabview_apis = ctk.CTkTabview(self.frame_direita)
        self.tabview_apis.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.tab_tmdb = self.tabview_apis.add("TMDb (Geral & Adulto)")
        self.tab_porndb = self.tabview_apis.add("ThePornDB (+18 Filmes)")

        self.scroll_tmdb = ctk.CTkScrollableFrame(self.tab_tmdb, fg_color="transparent")
        self.scroll_tmdb.pack(fill="both", expand=True)

        self.scroll_porndb = ctk.CTkScrollableFrame(self.tab_porndb, fg_color="transparent")
        self.scroll_porndb.pack(fill="both", expand=True)

        self.carregar_videos_pasta()

    def carregar_videos_pasta(self):
        for widget in self.scroll_arquivos.winfo_children():
            widget.destroy()

        if not os.path.exists(self.download_path):
            return

        extensoes_video = ('.mp4', '.mkv', '.avi', '.mov', '.webm')
        
        for arquivo in os.listdir(self.download_path):
            if arquivo.lower().endswith(extensoes_video):
                btn_arquivo = ctk.CTkButton(
                    self.scroll_arquivos, 
                    text=arquivo, 
                    fg_color="transparent", 
                    text_color=("black", "white"),
                    hover_color=("#dbdbdb", "#2b2b2b"),
                    anchor="w",
                    command=lambda a=arquivo: self.selecionar_video(a)
                )
                btn_arquivo.pack(fill="x", pady=2)

    def selecionar_video(self, nome_arquivo):
        self.arquivo_selecionado = nome_arquivo
        nome_limpo = os.path.splitext(nome_arquivo)[0]
        self.entry_busca.delete(0, "end")
        self.entry_busca.insert(0, nome_limpo)

    def executar_busca_apis(self):
        termo = self.entry_busca.get()
        if not termo:
            return
            
        for widget in self.scroll_tmdb.winfo_children():
            widget.destroy()
        for widget in self.scroll_porndb.winfo_children():
            widget.destroy()

        self.buscar_tmdb(termo)
        self.buscar_porndb(termo)

    def criar_card_resultado(self, scroll_container, dados):
        item_frame = ctk.CTkFrame(scroll_container, height=110)
        item_frame.pack(fill="x", pady=6, padx=5)
        item_frame.pack_propagate(False)

        img_tk = None
        if dados["poster_url"]:
            try:
                response = requests.get(dados["poster_url"], timeout=5)
                if response.status_code == 200:
                    pil_img = Image.open(BytesIO(response.content))
                    img_tk = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(65, 95))
            except Exception:
                pass

        if img_tk:
            lbl_poster = ctk.CTkLabel(item_frame, image=img_tk, text="")
        else:
            lbl_poster = ctk.CTkLabel(item_frame, text="[Sem Capa]", width=65, height=95, fg_color="gray")
        
        lbl_poster.pack(side="left", padx=10, pady=7)

        info_texto = f"{dados['titulo']} ({dados['ano']})\nEstúdio: {dados['studio']}"
        lbl_item = ctk.CTkLabel(
            item_frame, 
            text=info_texto, 
            anchor="w", 
            justify="left",
            wraplength=380,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        lbl_item.pack(side="left", padx=10, fill="x", expand=True)

        btn_escolher = ctk.CTkButton(
            item_frame, 
            text="Organizar & Baixar", 
            fg_color="#28a745",
            hover_color="#218838",
            width=140,
            height=35,
            command=lambda d=dados: self.aplicar_metadados(d)
        )
        btn_escolher.pack(side="right", padx=15)

    def buscar_tmdb(self, termo):
        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": termo,
            "include_adult": "true",
            "language": "pt-BR"
        }
        try:
            resposta = requests.get(url, params=params)
            dados = resposta.json()
            resultados = dados.get("results", [])
            
            if not resultados:
                ctk.CTkLabel(self.scroll_tmdb, text="Nenhum resultado encontrado no TMDb.").pack(pady=20)
                return

            for filme in resultados:
                titulo = filme.get("title", "Sem título")
                ano = filme.get("release_date", "----")[:4]
                poster_path = filme.get("poster_path")
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
                plot = filme.get("overview", "")

                info = {
                    "titulo": titulo,
                    "ano": ano,
                    "studio": "TMDb / Geral",
                    "plot": plot,
                    "actors": [],
                    "poster_url": poster_url
                }
                self.criar_card_resultado(self.scroll_tmdb, info)
                
        except Exception as e:
            print(f"Erro TMDb: {e}")

    def buscar_porndb(self, termo):
        url = f"https://api.theporndb.net/movies?q={termo}"
        headers = {
            "Authorization": f"Bearer {PORNDB_API_TOKEN}",
            "Accept": "application/json"
        }
        try:
            resposta = requests.get(url, headers=headers)
            if resposta.status_code == 200:
                dados_json = resposta.json().get("data", [])
                if not dados_json:
                    ctk.CTkLabel(self.scroll_porndb, text="Nenhum filme encontrado no ThePornDB.").pack(pady=20)
                    return

                for filme in dados_json:
                    titulo = filme.get("title", "Sem título")
                    data_lancamento = filme.get("date", "----")
                    ano = data_lancamento[:4] if data_lancamento else "----"
                    
                    site = filme.get("site", {})
                    estudio_nome = site.get("name", "Desconhecido") if site else "Desconhecido"
                    plot = filme.get("description", "")
                    poster_url = filme.get("poster") or ""
                    
                    performers = filme.get("performers", [])
                    lista_atores = [p.get("name") for p in performers if p.get("name")]

                    info = {
                        "titulo": titulo,
                        "ano": ano,
                        "studio": estudio_nome,
                        "plot": plot,
                        "actors": lista_atores,
                        "poster_url": poster_url
                    }
                    self.criar_card_resultado(self.scroll_porndb, info)
            else:
                ctk.CTkLabel(self.scroll_porndb, text=f"Erro na API (Status: {resposta.status_code})").pack(pady=20)
        except Exception as e:
            print(f"Erro ThePornDB: {e}")

    def aplicar_metadados(self, dados):
        titulo_limpo = "".join(c for c in dados["titulo"] if c.isalnum() or c in " -_").strip()
        caminho_destino = os.path.join(self.download_path, titulo_limpo)

        if not os.path.exists(caminho_destino):
            os.makedirs(caminho_destino)

        movimento_realizado = False
        if self.arquivo_selecionado:
            origem = os.path.join(self.download_path, self.arquivo_selecionado)
            if os.path.exists(origem):
                ext = os.path.splitext(self.arquivo_selecionado)[1]
                destino = os.path.join(caminho_destino, f"{titulo_limpo}{ext}")
                shutil.move(origem, destino)
                movimento_realizado = True

        if not movimento_realizado:
            termo_atual = self.entry_busca.get()
            extensoes_video = ('.mp4', '.mkv', '.avi', '.mov', '.webm')
            for arquivo in os.listdir(self.download_path):
                if arquivo.lower().endswith(extensoes_video):
                    nome_base = os.path.splitext(arquivo)[0]
                    if nome_base.lower() in termo_atual.lower() or termo_atual.lower() in nome_base.lower():
                        origem = os.path.join(self.download_path, arquivo)
                        ext = os.path.splitext(arquivo)[1]
                        destino = os.path.join(caminho_destino, f"{titulo_limpo}{ext}")
                        shutil.move(origem, destino)
                        break

        if dados["poster_url"]:
            try:
                img_data = requests.get(dados["poster_url"]).content
                with open(os.path.join(caminho_destino, "poster.jpg"), 'wb') as handler:
                    handler.write(img_data)
            except Exception as e:
                print(f"Erro ao baixar imagem: {e}")

        nfo_path = os.path.join(caminho_destino, "movie.nfo")
        try:
            xml_conteudo = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<movie>
    <title>{dados['titulo']}</title>
    <originaltitle>{dados['titulo']}</originaltitle>
    <year>{dados['ano']}</year>
    <studio>{dados['studio']}</studio>
    <plot>{dados['plot']}</plot>
"""
            for ator in dados['actors']:
                xml_conteudo += f"    <actor>\n        <name>{ator}</name>\n    </actor>\n"
            
            xml_conteudo += "</movie>"

            with open(nfo_path, 'w', encoding='utf-8') as nfo_file:
                nfo_file.write(xml_conteudo)
        except Exception as e:
            print(f"Erro ao gerar arquivo NFO: {e}")

        self.arquivo_selecionado = None
        self.entry_busca.delete(0, "end")
        
        for widget in self.scroll_tmdb.winfo_children():
            widget.destroy()
        for widget in self.scroll_porndb.winfo_children():
            widget.destroy()

        self.carregar_videos_pasta()
        print("Organização e download concluídos!")

if __name__ == "__main__":
    app = MetaMovieManager()
    app.mainloop()
