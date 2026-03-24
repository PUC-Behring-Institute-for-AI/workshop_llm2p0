"""
Gerenciador de conversas de chat.

Este módulo mantém o histórico de mensagens e fornece métodos
para adicionar mensagens e limpar o histórico.
"""

from typing import List, Dict, Optional


class ChatManager:
    """Gerencia o histórico e estado de uma conversa."""
    
    def __init__(self, system_prompt: Optional[str] = None):
        """
        Inicializa o gerenciador de chat.
        
        Args:
            system_prompt: Prompt de sistema opcional que define o comportamento do modelo.
        """
        self.messages: List[Dict[str, str]] = []
        self.system_prompt = system_prompt
        
        # Se houver system prompt, adiciona como primeira mensagem
        if system_prompt:
            self.messages.append({
                'role': 'system',
                'content': system_prompt
            })
    
    def add_user_message(self, content: str) -> None:
        """
        Adiciona uma mensagem do usuário ao histórico.
        
        Args:
            content: Conteúdo da mensagem do usuário.
        """
        self.messages.append({
            'role': 'user',
            'content': content
        })
    
    def add_assistant_message(self, content: str) -> None:
        """
        Adiciona uma mensagem do assistente ao histórico.
        
        Args:
            content: Conteúdo da mensagem do assistente.
        """
        self.messages.append({
            'role': 'assistant',
            'content': content
        })
    
    def get_messages(self) -> List[Dict[str, str]]:
        """
        Retorna todas as mensagens do histórico.
        
        Returns:
            List[Dict[str, str]]: Lista de mensagens no formato do Ollama.
        """
        return self.messages.copy()
    
    def clear_history(self, keep_system_prompt: bool = True) -> None:
        """
        Limpa o histórico de mensagens.
        
        Args:
            keep_system_prompt: Se True, mantém o system prompt (se houver).
        """
        if keep_system_prompt and self.system_prompt:
            self.messages = [{
                'role': 'system',
                'content': self.system_prompt
            }]
        else:
            self.messages = []
    
    def set_system_prompt(self, prompt: str) -> None:
        """
        Define ou atualiza o system prompt.
        
        Args:
            prompt: Novo prompt de sistema.
        """
        self.system_prompt = prompt
        
        # Remove system prompt anterior se existir
        if self.messages and self.messages[0]['role'] == 'system':
            self.messages.pop(0)
        
        # Adiciona novo system prompt no início
        self.messages.insert(0, {
            'role': 'system',
            'content': prompt
        })
    
    def get_conversation_summary(self) -> str:
        """
        Retorna um resumo formatado da conversa.
        
        Returns:
            str: Resumo legível da conversa.
        """
        summary_lines = []
        for msg in self.messages:
            role = msg['role'].upper()
            content = msg['content'][:100] + ('...' if len(msg['content']) > 100 else '')
            summary_lines.append(f"[{role}] {content}")
        
        return '\n'.join(summary_lines)
    
    def message_count(self) -> int:
        """
        Retorna o número de mensagens no histórico (excluindo system prompt).
        
        Returns:
            int: Número de mensagens de usuário e assistente.
        """
        count = len(self.messages)
        # Desconta system prompt se existir
        if self.messages and self.messages[0]['role'] == 'system':
            count -= 1
        return count
