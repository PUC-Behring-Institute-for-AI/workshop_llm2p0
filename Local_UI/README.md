# Local UI

Interface gráfica desktop (Tkinter) como alternativa ao servidor web para interagir com modelos Ollama localmente.

## Quando usar

Use a Local UI quando:
- Não quiser rodar um servidor web
- Precisar de uma interface standalone sem browser

Para o workshop com participantes, prefira o [`workshop_server/`](../workshop_server/) — ele permite acesso via rede local.

## Requisitos

- Python 3.10+
- [Ollama](https://ollama.com) instalado e rodando
- `tkinter` (incluído na instalação padrão do Python no macOS e Windows)

## Como rodar

```bash
# Na raiz do repositório
pip install -r requirements.txt

# Em outro terminal
ollama serve

# Iniciar a interface
python Local_UI/main.py
```
