"""
Interface gráfica do LLM Chat.

Este módulo implementa a janela principal e todos os widgets
para interação do usuário com os modelos Ollama.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from typing import Optional

from .ollama_client import OllamaClient
from .chat import ChatManager


class ChatUI:
    """Interface gráfica principal do chat."""
    
    def __init__(self):
        """Inicializa a interface gráfica."""
        self.root = tk.Tk()
        self.root.title("LLM Chat - Ollama")
        self.root.geometry("900x700")
        
        # Clientes e gerenciadores
        self.ollama_client = OllamaClient()
        self.chat_manager = ChatManager()
        
        # Estado da aplicação
        self.selected_model = tk.StringVar()
        self.is_generating = False
        self.stop_generation = False  # Flag para interromper geração
        self.current_response = ""
        
        # Informações do modelo
        self.model_info = {}
        self.last_sent_messages = []  # Últimas mensagens enviadas ao modelo
        
        # Prompts personalizados
        self.custom_prompts = []  # Lista de {'label': str, 'role': str, 'content': str}
        
        # Parâmetros do modelo
        self.temperature = tk.DoubleVar(value=0.7)
        self.num_predict = tk.IntVar(value=-1)  # -1 = ilimitado
        self.num_ctx = tk.IntVar(value=2048)
        self.stop_sequences = tk.StringVar(value="")  # Separadas por vírgula

        self.system_prompt = tk.StringVar(value="")  # Prompt de sistema principal (opcional)
        self.tools_prompt = tk.StringVar(value="")  # Prompt para descrição de ferramentas (opcional)
        
        
        # Construir interface
        self._build_ui()
        
        # Carregar modelos ao iniciar
        self._load_models()
    
    def _build_ui(self):
        """Constrói todos os elementos da interface."""
        
        # === FRAME SUPERIOR: Seleção de modelo ===
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Modelo:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.model_combo = ttk.Combobox(
            top_frame, 
            textvariable=self.selected_model,
            state="readonly",
            width=30
        )
        self.model_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.model_combo.bind('<<ComboboxSelected>>', lambda e: self._on_model_selected())
        
        self.refresh_btn = ttk.Button(
            top_frame, 
            text="🔄 Atualizar",
            command=self._load_models
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_btn = ttk.Button(
            top_frame,
            text="🗑️ Limpar Chat",
            command=self._clear_chat
        )
        self.clear_btn.pack(side=tk.LEFT)
        
        # Status
        self.status_label = ttk.Label(top_frame, text="", foreground="gray")
        self.status_label.pack(side=tk.RIGHT)
        
        # === FRAME DE CONFIGURAÇÕES: Parâmetros do modelo (expansível) ===
        self.config_frame = ttk.LabelFrame(self.root, text="⚙️ Parâmetros do Modelo", padding="10")
        self.config_visible = False  # Inicialmente oculto
        
        # Botão para mostrar/ocultar configurações
        self.toggle_config_btn = ttk.Button(
            self.root,
            text="▼ Mostrar Configurações",
            command=self._toggle_config
        )
        self.toggle_config_btn.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        # Conteúdo das configurações (3 linhas de parâmetros)
        # Linha 1: Temperature
        temp_frame = ttk.Frame(self.config_frame)
        temp_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(temp_frame, text="Temperature:", width=15).pack(side=tk.LEFT)
        temp_scale = ttk.Scale(
            temp_frame,
            from_=0.0,
            to=2.0,
            variable=self.temperature,
            orient=tk.HORIZONTAL
        )
        temp_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.temp_label = ttk.Label(temp_frame, text="0.70", width=5)
        self.temp_label.pack(side=tk.LEFT)
        temp_scale.config(command=lambda v: self.temp_label.config(text=f"{float(v):.2f}"))
        
        ttk.Label(temp_frame, text="(0=determinístico, 2=criativo)", foreground="gray").pack(side=tk.LEFT, padx=10)
        
        # Linha 2: num_predict e num_ctx
        predict_ctx_frame = ttk.Frame(self.config_frame)
        predict_ctx_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(predict_ctx_frame, text="Max Tokens:", width=15).pack(side=tk.LEFT)
        num_predict_entry = ttk.Entry(predict_ctx_frame, textvariable=self.num_predict, width=10)
        num_predict_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(predict_ctx_frame, text="(-1 = ilimitado)", foreground="gray").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(predict_ctx_frame, text="Context Size:", width=15).pack(side=tk.LEFT, padx=(30, 0))
        num_ctx_entry = ttk.Entry(predict_ctx_frame, textvariable=self.num_ctx, width=10)
        num_ctx_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(predict_ctx_frame, text="(ex: 2048, 4096, 8192)", foreground="gray").pack(side=tk.LEFT, padx=5)
        
        # Linha 3: Stop sequences
        stop_frame = ttk.Frame(self.config_frame)
        stop_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(stop_frame, text="Stop Sequences:", width=15).pack(side=tk.LEFT)
        stop_entry = ttk.Entry(stop_frame, textvariable=self.stop_sequences)
        stop_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(stop_frame, text="(separadas por vírgula, ex: \\n,User:,###)", foreground="gray").pack(side=tk.LEFT, padx=5)
        
        # Botão de reset para valores padrão
        reset_btn = ttk.Button(
            self.config_frame,
            text="🔄 Restaurar Padrões",
            command=self._reset_parameters
        )
        reset_btn.pack(pady=5)
        
        # === NOTEBOOK: Abas para Chat e Informações ===
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # === ABA 1: CHAT ===
        chat_tab = ttk.Frame(self.notebook)
        self.notebook.add(chat_tab, text="💬 Chat")
        
        # Área de exibição do chat
        self.chat_display = scrolledtext.ScrolledText(
            chat_tab,
            wrap=tk.WORD,
            font=("Arial", 13),
            state=tk.DISABLED,
            bg="#f5f5f5"
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurar tags para formatação
        self.chat_display.tag_config("user", foreground="#0066cc", font=("Arial", 12, "bold"))
        self.chat_display.tag_config("assistant", foreground="#009900", font=("Arial", 12, "bold"))
        self.chat_display.tag_config("system", foreground="#cc6600", font=("Arial", 12, "italic"))
        
        # === ABA 2: INFORMAÇÕES DO MODELO ===
        info_tab = ttk.Frame(self.notebook)
        self.notebook.add(info_tab, text="ℹ️ Informações do Modelo")
        
        # Frame com scroll para as informações
        info_canvas = tk.Canvas(info_tab)
        info_scrollbar = ttk.Scrollbar(info_tab, orient="vertical", command=info_canvas.yview)
        info_scroll_frame = ttk.Frame(info_canvas)
        
        info_scroll_frame.bind(
            "<Configure>",
            lambda e: info_canvas.configure(scrollregion=info_canvas.bbox("all"))
        )
        
        info_canvas.create_window((0, 0), window=info_scroll_frame, anchor="nw")
        info_canvas.configure(yscrollcommand=info_scrollbar.set)
        
        info_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === Seção 1: Informações Gerais ===
        general_frame = ttk.LabelFrame(info_scroll_frame, text="📋 Informações Gerais", padding="10")
        general_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.info_general_text = scrolledtext.ScrolledText(
            general_frame,
            wrap=tk.WORD,
            font=("Courier", 11),
            height=8,
            state=tk.DISABLED
        )
        self.info_general_text.pack(fill=tk.BOTH, expand=True)
        
        # === Seção 2: Template do Modelo ===
        template_frame = ttk.LabelFrame(info_scroll_frame, text="📝 Template do Modelo", padding="10")
        template_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.info_template_text = scrolledtext.ScrolledText(
            template_frame,
            wrap=tk.WORD,
            font=("Courier", 11),
            height=10,
            state=tk.DISABLED
        )
        self.info_template_text.pack(fill=tk.BOTH, expand=True)
        
        # === Seção 3: Última Requisição Enviada ===
        request_frame = ttk.LabelFrame(info_scroll_frame, text="📤 Última Requisição Enviada ao Modelo", padding="10")
        request_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.info_request_text = scrolledtext.ScrolledText(
            request_frame,
            wrap=tk.WORD,
            font=("Courier", 11),
            height=15,
            state=tk.DISABLED
        )
        self.info_request_text.pack(fill=tk.BOTH, expand=True)
        
        # Botão para atualizar informações
        refresh_info_btn = ttk.Button(
            info_scroll_frame,
            text="🔄 Atualizar Informações do Modelo",
            command=self._refresh_model_info
        )
        refresh_info_btn.pack(pady=10)
              
        # === ABA 3: PROMPTS PERSONALIZADOS ===
        prompts_tab = ttk.Frame(self.notebook)
        self.notebook.add(prompts_tab, text="✏️ Prompts Personalizados")
        
        # Frame principal com padding
        prompts_main = ttk.Frame(prompts_tab, padding="10")
        prompts_main.pack(fill=tk.BOTH, expand=True)
        
        # Descrição
        desc_label = ttk.Label(
            prompts_main,
            text="Adicione prompts personalizados que serão enviados ANTES das suas mensagens de chat.\n"
                 "Use 'system' para definir o comportamento do modelo, 'user' para exemplos, etc.",
            wraplength=800,
            foreground="gray",
            font=("Arial", 10)
        )
        desc_label.pack(pady=(0, 10))
        
        # Frame para adicionar novo prompt
        add_frame = ttk.LabelFrame(prompts_main, text="➕ Adicionar Novo Prompt", padding="10")
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Linha 1: Role
        role_frame = ttk.Frame(add_frame)
        role_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(role_frame, text="Role:", width=12).pack(side=tk.LEFT)
        self.prompt_role_var = tk.StringVar(value="system")
        role_combo = ttk.Combobox(
            role_frame,
            textvariable=self.prompt_role_var,
            values=["system", "user", "assistant"],
            state="readonly",
            width=15
        )
        role_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(role_frame, text="(system = instruções, user = exemplo usuário, assistant = exemplo resposta)", foreground="gray").pack(side=tk.LEFT, padx=10)
        
        # Linha 2: Conteúdo
        content_frame = ttk.Frame(add_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(content_frame, text="Conteúdo:", width=12).pack(side=tk.LEFT, anchor=tk.N, pady=5)
        
        self.prompt_content_text = scrolledtext.ScrolledText(
            content_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            height=5
        )
        self.prompt_content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Linha 3: Botões
        buttons_frame = ttk.Frame(add_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            buttons_frame,
            text="➕ Adicionar Prompt",
            command=self._add_custom_prompt
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="🗑️ Limpar Campos",
            command=self._clear_prompt_fields
        ).pack(side=tk.LEFT, padx=5)
        
        # Frame para lista de prompts existentes
        list_frame = ttk.LabelFrame(prompts_main, text="📋 Prompts Ativos (serão enviados nesta ordem)", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de prompts
        self.prompts_listbox = tk.Listbox(
            list_frame,
            font=("Courier", 10),
            height=10
        )
        self.prompts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar para a lista
        prompts_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.prompts_listbox.yview)
        prompts_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.prompts_listbox.config(yscrollcommand=prompts_scroll.set)
        
        # Botões de gerenciamento
        manage_frame = ttk.Frame(prompts_main)
        manage_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            manage_frame,
            text="⬆️ Mover para Cima",
            command=self._move_prompt_up
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            manage_frame,
            text="⬇️ Mover para Baixo",
            command=self._move_prompt_down
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            manage_frame,
            text="🗑️ Remover Selecionado",
            command=self._remove_selected_prompt
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            manage_frame,
            text="🔄 Limpar Todos",
            command=self._clear_all_prompts
        ).pack(side=tk.LEFT, padx=5)
        
        # Aviso sobre reiniciar chat
        warning_label = ttk.Label(
            prompts_main,
            text="⚠️ Os prompts personalizados serão incluídos nas próximas mensagens. Para aplicar em conversa nova, use 'Limpar Chat'.",
            wraplength=800,
            foreground="#cc6600",
            font=("Arial", 9, "italic")
        )
        warning_label.pack(pady=10)
        
        
        # === FRAME INFERIOR: Input do usuário ===
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(fill=tk.X)
        
        # Campo de entrada
        self.input_text = scrolledtext.ScrolledText(
            input_frame,
            wrap=tk.WORD,
            font=("Arial", 12),
            height=3
        )
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Bind da tecla Enter (Ctrl+Enter para enviar, Enter para quebra de linha)
        self.input_text.bind('<Control-Return>', lambda e: self._send_message())
        
        # Botão de enviar
        self.send_btn = ttk.Button(
            input_frame,
            text="Enviar\n(Ctrl+Enter)",
            command=self._send_message,
            width=15
        )
        self.send_btn.pack(side=tk.RIGHT)
        
        # Botão de parar (inicialmente oculto)
        self.stop_btn = ttk.Button(
            input_frame,
            text="⏹ Parar",
            command=self._stop_generation,
            width=15
        )
        # Não fazemos pack() ainda - será mostrado apenas durante geração
    
    def _load_models(self):
        """Carrega a lista de modelos disponíveis do Ollama."""
        self.status_label.config(text="Carregando modelos...")
        
        def load():
            try:
                models = self.ollama_client.list_models()
                
                if not models:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Aviso",
                        "Nenhum modelo encontrado.\n\nCertifique-se de que o Ollama está rodando e que você tem modelos instalados.\n\nUse: ollama pull llama3"
                    ))
                    self.root.after(0, lambda: self.status_label.config(text="❌ Nenhum modelo encontrado"))
                else:
                    # Capturar valores antes dos lambdas
                    models_list = models
                    count = len(models)
                    self.root.after(0, lambda m=models_list: self._update_model_list(m))
                    self.root.after(0, lambda c=count: self.status_label.config(text=f"✓ {c} modelo(s) disponível(is)"))
            
            except Exception as e:
                error_msg = str(e)  # Capturar antes do lambda
                self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                    "Erro",
                    f"Erro ao conectar com o Ollama:\n\n{msg}\n\nVerifique se o Ollama está rodando."
                ))
                self.root.after(0, lambda: self.status_label.config(text="❌ Erro de conexão"))
        
        thread = threading.Thread(target=load, daemon=True)
        thread.start()
    
    def _update_model_list(self, models):
        """Atualiza o combobox com a lista de modelos."""
        self.model_combo['values'] = models
        if models and not self.selected_model.get():
            self.selected_model.set(models[0])
            # Carregar info do primeiro modelo automaticamente
            self._refresh_model_info()
    
    def _on_model_selected(self):
        """Chamado quando o usuário seleciona um modelo diferente."""
        self._refresh_model_info()
    
    def _send_message(self):
        """Envia mensagem do usuário para o modelo."""
        # Validações
        if not self.selected_model.get():
            messagebox.showwarning("Aviso", "Selecione um modelo primeiro.")
            return
        
        if self.is_generating:
            messagebox.showinfo("Aguarde", "Aguarde a resposta anterior terminar.")
            return
        
        user_message = self.input_text.get("1.0", tk.END).strip()
        
        if not user_message:
            return
        
        # Adicionar mensagem do usuário ao chat
        self.chat_manager.add_user_message(user_message)
        self._append_to_chat("Você", user_message, "user")
        
        # Limpar campo de input
        self.input_text.delete("1.0", tk.END)
        
        # Desabilitar input durante geração
        self.is_generating = True
        self.stop_generation = False  # Resetar flag de parada
        self.send_btn.pack_forget()  # Esconder botão de enviar
        self.stop_btn.pack(side=tk.RIGHT)  # Mostrar botão de parar
        self.input_text.config(state=tk.DISABLED)
        self.status_label.config(text="⏳ Gerando resposta...")
        
        # Iniciar label do assistente
        self._append_to_chat("Assistente", "", "assistant")
        self.current_response = ""
        
        # Enviar para o modelo em thread separada
        def generate():
            try:
                # Preparar stop sequences
                stop_list = None
                if self.stop_sequences.get().strip():
                    # Converter string separada por vírgula em lista
                    stop_list = [s.strip() for s in self.stop_sequences.get().split(',') if s.strip()]
                
                # Obter valores de num_predict e num_ctx
                num_predict_val = self.num_predict.get() if self.num_predict.get() != -1 else None
                num_ctx_val = self.num_ctx.get()
                
                # Construir mensagens: prompts personalizados + histórico do chat
                messages_to_send = []
                
                # Adicionar prompts personalizados primeiro
                for prompt in self.custom_prompts:
                    messages_to_send.append({
                        'role': prompt['role'],
                        'content': prompt['content']
                    })
                
                # Adicionar histórico da conversa
                messages_to_send.extend(self.chat_manager.get_messages())
                
                # Salvar mensagens que serão enviadas (para exibir na aba de informações)
                self.last_sent_messages = messages_to_send
                
                stream = self.ollama_client.chat_stream(
                    model=self.selected_model.get(),
                    messages=messages_to_send,
                    temperature=self.temperature.get(),
                    stop=stop_list,
                    num_predict=num_predict_val,
                    num_ctx=num_ctx_val
                )
                
                for token in stream:
                    # Verificar se usuário pediu para parar
                    if self.stop_generation:
                        break
                    
                    self.current_response += token
                    # Atualizar UI na thread principal
                    self.root.after(0, lambda t=token: self._append_token(t))
                
                # Adicionar resposta completa ao histórico (mesmo se incompleta)
                if self.current_response:
                    self.chat_manager.add_assistant_message(self.current_response)
                
                # Atualizar display da última requisição
                self.root.after(0, self._update_last_request_display)
                
                # Finalizar
                if self.stop_generation:
                    self.root.after(0, lambda: self._finish_generation(interrupted=True))
                else:
                    self.root.after(0, self._finish_generation)
                
            except Exception as e:
                error_msg = str(e)  # Capturar o valor antes do lambda
                self.root.after(0, lambda msg=error_msg: self._handle_error(msg))
        
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
    
    def _append_to_chat(self, sender: str, message: str, tag: str):
        """Adiciona mensagem à área de chat."""
        self.chat_display.config(state=tk.NORMAL)
        
        if self.chat_display.get("1.0", tk.END).strip():
            self.chat_display.insert(tk.END, "\n\n")
        
        self.chat_display.insert(tk.END, f"{sender}:\n", tag)
        if message:
            self.chat_display.insert(tk.END, message)
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def _append_token(self, token: str):
        """Adiciona um token à resposta do assistente em tempo real."""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, token)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def _finish_generation(self, interrupted: bool = False):
        """Finaliza a geração da resposta."""
        self.is_generating = False
        self.stop_btn.pack_forget()  # Esconder botão de parar
        self.send_btn.pack(side=tk.RIGHT)  # Mostrar botão de enviar
        self.input_text.config(state=tk.NORMAL)
        
        if interrupted:
            self.status_label.config(text="⏸ Interrompido")
        else:
            self.status_label.config(text="✓ Pronto")
        
        self.input_text.focus()
    
    def _handle_error(self, error_message: str):
        """Trata erros durante a geração."""
        self.is_generating = False
        self.stop_btn.pack_forget()  # Esconder botão de parar
        self.send_btn.pack(side=tk.RIGHT)  # Mostrar botão de enviar
        self.input_text.config(state=tk.NORMAL)
        self.status_label.config(text="❌ Erro")
        
        messagebox.showerror("Erro", f"Erro ao gerar resposta:\n\n{error_message}")
    
    def _stop_generation(self):
        """Interrompe a geração da resposta."""
        self.stop_generation = True
        self.status_label.config(text="⏸ Parando...")
    
    def _toggle_config(self):
        """Mostra ou oculta o painel de configurações."""
        if self.config_visible:
            # Ocultar configurações
            self.config_frame.pack_forget()
            self.toggle_config_btn.config(text="▼ Mostrar Configurações")
            self.config_visible = False
        else:
            # Mostrar configurações (depois do botão toggle, antes do chat)
            self.config_frame.pack(fill=tk.X, padx=10, pady=(0, 10), after=self.toggle_config_btn)
            self.toggle_config_btn.config(text="▲ Ocultar Configurações")
            self.config_visible = True
    
    def _reset_parameters(self):
        """Restaura os parâmetros para valores padrão."""
        self.temperature.set(0.7)
        self.num_predict.set(-1)
        self.num_ctx.set(2048)
        self.stop_sequences.set("")
        self.status_label.config(text="✓ Parâmetros restaurados")
    
    def _refresh_model_info(self):
        """Atualiza as informações do modelo selecionado."""
        self.selected_model.get()
        
        if not self.selected_model.get():
            return  # Silenciosamente não fazer nada se não há modelo
        
        # Atualizar status
        self.status_label.config(text="Carregando info do modelo...")
        
        def fetch_info():
            try:
                # Buscar informações do modelo
                model_name = self.selected_model.get()
                info = self.ollama_client.get_model_info(model_name)
                self.model_info = info
                
                # Atualizar UI na thread principal
                self.root.after(0, self._update_model_info_display)
                self.root.after(0, lambda: self.status_label.config(text="✓ Info do modelo carregada"))
                
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                    "Erro",
                    f"Erro ao buscar informações do modelo:\n\n{msg}"
                ))
                self.root.after(0, lambda: self.status_label.config(text="❌ Erro ao carregar info"))
        
        thread = threading.Thread(target=fetch_info, daemon=True)
        thread.start()
    
    def _update_model_info_display(self):
        """Atualiza os widgets de informação do modelo com os dados obtidos."""
        import json
                
        # === Atualizar Informações Gerais ===
        self.info_general_text.config(state=tk.NORMAL)
        self.info_general_text.delete("1.0", tk.END)
        
        # Extrair informações com fallback
        details = self.model_info.get('details', {})
        model_info = self.model_info.get('model_info', {})
        
        # Tentar diferentes campos que podem existir
        family = details.get('family', details.get('families', 'N/A')) if isinstance(details, dict) else 'N/A'
        parameter_size = details.get('parameter_size', details.get('parameters', 'N/A')) if isinstance(details, dict) else 'N/A'
        quantization = details.get('quantization_level', details.get('quantization', 'N/A')) if isinstance(details, dict) else 'N/A'
        
        general_info = f"""Modelo: {self.selected_model.get()}

DETALHES:
{details if details else 'Nenhum detalhe disponível'}

MODEL INFO:
{model_info if model_info else 'Nenhuma info adicional'}
"""
        
        self.info_general_text.insert("1.0", general_info)
        self.info_general_text.config(state=tk.DISABLED)
        
        # === Atualizar Template ===
        self.info_template_text.config(state=tk.NORMAL)
        self.info_template_text.delete("1.0", tk.END)
        
        template = self.model_info.get('template', 'Template não disponível')
        if template:
            # Tentar formatar de forma legível
            template_formatted = template.replace('{{', '\n{{').replace('}}', '}}\n')
            self.info_template_text.insert("1.0", template_formatted)
        else:
            self.info_template_text.insert("1.0", "Template não disponível para este modelo.")
        
        self.info_template_text.config(state=tk.DISABLED)
        
        # === Atualizar Última Requisição ===
        self._update_last_request_display()
    
    def _update_last_request_display(self):
        """Atualiza a exibição da última requisição enviada."""
        import json
        
        self.info_request_text.config(state=tk.NORMAL)
        self.info_request_text.delete("1.0", tk.END)
        
        if not self.last_sent_messages:
            self.info_request_text.insert("1.0", "Nenhuma mensagem enviada ainda.\n\nEnvie uma mensagem no chat para ver como ela é formatada.")
        else:
            # Contar prompts personalizados vs histórico do chat
            num_custom = len(self.custom_prompts)
            num_chat = len(self.last_sent_messages) - num_custom
            
            # Mostrar as mensagens formatadas
            request_info = f"""=== MENSAGENS ENVIADAS AO MODELO ===

Total de mensagens: {len(self.last_sent_messages)}
  - Prompts personalizados: {num_custom}
  - Histórico do chat: {num_chat}

"""
            
            # Mostrar prompts personalizados separadamente se houver
            if num_custom > 0:
                request_info += "--- PROMPTS PERSONALIZADOS (enviados primeiro) ---\n"
                for i, msg in enumerate(self.last_sent_messages[:num_custom]):
                    # Buscar label do prompt original
                    label = self.custom_prompts[i]['label'] if i < len(self.custom_prompts) else f"Prompt {i+1}"
                    request_info += f"\n[{i+1}] {label} - Role: {msg['role']}\n"
                    request_info += f"Content: {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}\n"
                
                request_info += "\n--- HISTÓRICO DO CHAT ---\n"
                for i, msg in enumerate(self.last_sent_messages[num_custom:]):
                    request_info += f"\n[{i+1}] Role: {msg['role']}\n"
                    request_info += f"Content: {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}\n"
            
            request_info += f"""

--- FORMATO JSON COMPLETO ---
{json.dumps(self.last_sent_messages, indent=2, ensure_ascii=False)}

--- PARÂMETROS USADOS ---
- Temperature: {self.temperature.get()}
- Max Tokens: {self.num_predict.get() if self.num_predict.get() != -1 else 'Ilimitado'}
- Context Size: {self.num_ctx.get()}
- Stop Sequences: {self.stop_sequences.get() if self.stop_sequences.get() else 'Nenhuma'}
"""
            self.info_request_text.insert("1.0", request_info)
        
        self.info_request_text.config(state=tk.DISABLED)
    
    def _clear_prompt_fields(self):
        """Limpa os campos de adição de prompt."""
        self.prompt_role_var.set("system")
        self.prompt_content_text.delete("1.0", tk.END)
    
    def _add_custom_prompt(self):
        """Adiciona um novo prompt personalizado à lista."""
        label = self.prompt_role_var.get().strip()
        role = self.prompt_role_var.get()
        content = self.prompt_content_text.get("1.0", tk.END).strip()
        
        if not label:
            messagebox.showwarning("Aviso", "Digite um nome/label para o prompt.")
            return
        
        if not content:
            messagebox.showwarning("Aviso", "Digite o conteúdo do prompt antes de adicionar.")
            return
        
        # Adicionar à lista
        self.custom_prompts.append({
            "label": label,
            "role": role,
            "content": content
        })
        
        # Atualizar listbox
        self._update_prompts_listbox()
        
        # Limpar campos
        self._clear_prompt_fields()
        
        self.status_label.config(text=f"✓ Prompt '{label}' adicionado")
    
    def _update_prompts_listbox(self):
        """Atualiza a listbox com os prompts atuais."""
        self.prompts_listbox.delete(0, tk.END)
        
        for i, prompt in enumerate(self.custom_prompts):
            label = prompt['label']
            role = prompt['role']
            content = prompt['content']
            # Truncar conteúdo para exibição
            preview = content[:50] + "..." if len(content) > 50 else content
            preview = preview.replace('\n', ' ')  # Remover quebras de linha
            
            display_text = f"[{i+1}] {label} ({role.upper()}): {preview}"
            self.prompts_listbox.insert(tk.END, display_text)
    
    def _move_prompt_up(self):
        """Move o prompt selecionado para cima na lista."""
        selection = self.prompts_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Selecione um prompt primeiro.")
            return
        
        index = selection[0]
        if index == 0:
            messagebox.showinfo("Info", "Já está no topo da lista.")
            return
        
        # Trocar posições
        self.custom_prompts[index], self.custom_prompts[index-1] = \
            self.custom_prompts[index-1], self.custom_prompts[index]
        
        # Atualizar e manter seleção
        self._update_prompts_listbox()
        self.prompts_listbox.selection_set(index-1)
    
    def _move_prompt_down(self):
        """Move o prompt selecionado para baixo na lista."""
        selection = self.prompts_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Selecione um prompt primeiro.")
            return
        
        index = selection[0]
        if index >= len(self.custom_prompts) - 1:
            messagebox.showinfo("Info", "Já está no final da lista.")
            return
        
        # Trocar posições
        self.custom_prompts[index], self.custom_prompts[index+1] = \
            self.custom_prompts[index+1], self.custom_prompts[index]
        
        # Atualizar e manter seleção
        self._update_prompts_listbox()
        self.prompts_listbox.selection_set(index+1)
    
    def _remove_selected_prompt(self):
        """Remove o prompt selecionado da lista."""
        selection = self.prompts_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Selecione um prompt para remover.")
            return
        
        index = selection[0]
        prompt = self.custom_prompts[index]
        
        if messagebox.askyesno("Confirmar", f"Remover prompt '{prompt['label']}'?"):
            self.custom_prompts.pop(index)
            self._update_prompts_listbox()
            self.status_label.config(text="✓ Prompt removido")
    
    def _clear_all_prompts(self):
        """Limpa todos os prompts personalizados."""
        if self.custom_prompts and messagebox.askyesno("Confirmar", "Remover todos os prompts personalizados?"):
            self.custom_prompts.clear()
            self._update_prompts_listbox()
            self.status_label.config(text="✓ Prompts personalizados limpos")
    
    def _clear_chat(self):
        """Limpa o histórico do chat."""
        if messagebox.askyesno("Confirmar", "Limpar todo o histórico do chat?"):
            self.chat_manager.clear_history()
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.status_label.config(text="Chat limpo")
    
    def run(self):
        """Inicia o loop principal da interface."""
        self.root.mainloop()