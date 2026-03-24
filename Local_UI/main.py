"""
LLM Chat - Interface gráfica para interação com modelos Ollama

Este é o ponto de entrada da aplicação. Execute este arquivo para iniciar o chat.

Uso:
    python main.py
"""

from app.ui import ChatUI


def main():
    """Função principal - inicializa e executa a aplicação."""
    print("🚀 Iniciando LLM Chat...")
    print("📋 Certifique-se de que o Ollama está rodando: ollama serve")
    print()
    
    app = ChatUI()
    app.run()


if __name__ == "__main__":
    main()
