"""
LLM Chat Application

Um sistema de chat com interface gráfica para interagir com modelos
Ollama rodando localmente.
"""

from .ui import ChatUI
from .chat import ChatManager
from .ollama_client import OllamaClient

__version__ = "1.0.0"
__author__ = "Curso LLM na Prática"

__all__ = [
    'ChatUI',
    'ChatManager',
    'OllamaClient',
]
