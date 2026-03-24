"""
Cliente para comunicação com o Ollama.

Este módulo encapsula toda a lógica de comunicação com a API do Ollama,
incluindo listagem de modelos e envio de mensagens com streaming.
"""

import ollama
from typing import List, Dict, Generator, Any, Optional


class OllamaClient:
    """Cliente para interagir com modelos Ollama locais."""
    
    def __init__(self):
        """Inicializa o cliente Ollama."""
        self.client = ollama
    
    def list_models(self) -> List[str]:
        """
        Lista todos os modelos disponíveis no Ollama local.
        
        Returns:
            List[str]: Lista com os nomes dos modelos instalados.
            
        Raises:
            Exception: Se houver erro na comunicação com o Ollama.
        """
        try:
            response = self.client.list()
            # A resposta tem formato: {'models': [{'model': 'llama3:latest', ...}, ...]}
            models = [model['model'] for model in response.get('models', [])]
            return models
        except Exception as e:
            raise Exception(f"Erro ao listar modelos: {str(e)}")
    
    def chat_stream(
        self, 
        model: str, 
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        stop: Optional[List[str]] = None,
        num_predict: Optional[int] = None,
        num_ctx: Optional[int] = None
    ) -> Generator[str, None, None]:
        """
        Envia mensagens para o modelo e retorna a resposta em streaming.
        
        Args:
            model: Nome do modelo a ser usado (ex: 'llama3:latest')
            messages: Lista de mensagens no formato [{'role': 'user', 'content': '...'}]
            temperature: Controla a aleatoriedade (0.0 = determinístico, 1.0 = criativo)
            stop: Sequências que param a geração (ex: ['\\n', 'User:'])
            num_predict: Número máximo de tokens a gerar (-1 = ilimitado)
            num_ctx: Tamanho da janela de contexto (ex: 2048, 4096)
            
        Yields:
            str: Cada token da resposta conforme é gerado.
            
        Raises:
            Exception: Se houver erro na comunicação com o Ollama.
        """
        try:
            # Construir opções dinamicamente
            options = {'temperature': temperature}
            
            if num_predict is not None:
                options['num_predict'] = num_predict
            
            if num_ctx is not None:
                options['num_ctx'] = num_ctx
            
            # Stop sequences vão dentro de options
            if stop is not None and stop:
                options['stop'] = stop
            
            stream = self.client.chat(
                model=model,
                messages=messages,
                stream=True,
                options=options
            )
            
            for chunk in stream:
                # Cada chunk tem formato: {'message': {'content': 'token'}, 'done': False}
                content = chunk.get('message', {}).get('content', '')
                if content:
                    yield content
                    
        except Exception as e:
            raise Exception(f"Erro ao enviar mensagem: {str(e)}")
    
    def check_connection(self) -> bool:
        """
        Verifica se o Ollama está rodando e acessível.
        
        Returns:
            bool: True se o Ollama está acessível, False caso contrário.
        """
        try:
            self.list_models()
            return True
        except:
            return False
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Obtém informações detalhadas sobre um modelo.
        
        Args:
            model: Nome do modelo (ex: 'llama3:latest')
            
        Returns:
            Dict: Informações do modelo incluindo modelfile, template, etc.
            
        Raises:
            Exception: Se houver erro ao buscar informações.
        """
        try:
            response = self.client.show(model)
            info = { k[0]: k[1] for k in response}
            return info
        except Exception as e:
            raise Exception(f"Erro ao obter informações do modelo: {str(e)}")
