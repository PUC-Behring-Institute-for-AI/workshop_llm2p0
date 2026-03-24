# Recursos e Demos

[[Índice]]

Links e ferramentas para uso durante a apresentação teórica, em ordem de aparição.

---

## 03. Treinando um Modelo

### Google Teachable Machine
[https://teachablemachine.withgoogle.com](https://teachablemachine.withgoogle.com)

Ferramenta do Google que permite treinar um modelo de classificação de imagens em tempo real, usando a webcam. Ideal para mostrar de forma concreta o que significa "treinar um modelo" — a audiência vê o ciclo de dados → treinamento → predição sem precisar escrever uma linha de código.

---

## 05. Tokenização

### Runcell Token Counter
[https://www.runcell.dev/tool/token-counter#counter](https://www.runcell.dev/tool/token-counter#counter)

Contador simples e visual de tokens. Bom para uma primeira demonstração: cole uma frase e mostre como o texto é quebrado em pedaços menores do que palavras. Use para a pergunta à audiência: *"quantos tokens vocês acham que tem nessa frase?"*

### Hugging Face Tokenizer Playground
[https://huggingface.co/spaces/Xenova/the-tokenizer-playground](https://huggingface.co/spaces/Xenova/the-tokenizer-playground)

Playground mais avançado que permite comparar como diferentes modelos (GPT-4, LLaMA, Mistral etc.) tokenizam o mesmo texto de formas distintas. Use em sequência ao Runcell para aprofundar e mostrar que tokenização não é universal.

---

## 06. Completando Palavras — Predição do Próximo Token

### Hugging Face — Next Token Prediction (alonsosilva)
[https://alonsosilva-nexttokenprediction.hf.space](https://alonsosilva-nexttokenprediction.hf.space)

Demo interativo que mostra, dado um texto de entrada, quais são os tokens mais prováveis para continuar a sequência — com as probabilidades de cada candidato. Perfeito para mostrar que o modelo não "pensa" nem "escolhe": ele calcula distribuições de probabilidade sobre o vocabulário inteiro e seleciona o próximo token a partir daí.

### Hugging Face — Next Token Predictor (PeterPinetree)
[https://huggingface.co/spaces/PeterPinetree/Next-Token-Predictor](https://huggingface.co/spaces/PeterPinetree/Next-Token-Predictor)

Alternativa mais simples: dado um texto, mostra as palavras mais prováveis para continuar. Inclui controle de aleatoriedade (temperatura), o que cria uma ponte natural para o bloco seguinte sobre como o modelo "decide".

---

### Referência — Tamanho e Crescimento dos Modelos
[https://artificialanalysis.ai](https://artificialanalysis.ai)

Painel com benchmarks, tamanho e custo de modelos atualizados continuamente. Útil para mostrar visualmente a explosão no número de parâmetros e a corrida entre laboratórios — GPT, Gemini, Claude, LLaMA e outros lado a lado.

---
## 09. System Prompt e Guard Rails

### Leaked System Prompts (GitHub)
[https://github.com/jujumilk3/leaked-system-prompts](https://github.com/jujumilk3/leaked-system-prompts)

Repositório com system prompts vazados ou publicados de produtos reais — ChatGPT, Claude, Copilot, Bing e outros. Muito concreto para mostrar que o system prompt não é magia nem mistério: é texto, escrito por humanos, que instrui o modelo antes da conversa começar.

---

## 10. A Influência dos Prompts

### ChatHub Prompt Library
[https://chathub.gg/prompt-library](https://chathub.gg/prompt-library)

Biblioteca comunitária com centenas de prompts prontos, organizados por categoria — assistentes técnicos, personas históricas, consultores, tutores, personagens criativos e muito mais. Use ao vivo para mostrar como diferentes system prompts mudam o comportamento do mesmo modelo base. Também útil para a audiência explorar sozinha durante o demo.

### Prompting Guide
[https://www.promptingguide.ai](https://www.promptingguide.ai)

Referência didática para técnicas de prompting: zero-shot, few-shot, chain-of-thought, entre outras. Use para mostrar que a forma como uma instrução é escrita muda substancialmente o output — e que isso tem nome e método.

---

## 11. Antropomorfização

Nenhum link externo necessário. O próprio chatbot é o demo. Pergunte ao vivo algo que pressupõe consciência ou emoção — *"você está feliz hoje?"*, *"você tem medo de morrer?"*, *"você prefere qual resposta?"* — e use a resposta como ponto de partida para desconstruir tecnicamente por que o modelo responde dessa forma.

### Chatbots com uso gratuito disponíveis para o demo

| Chatbot | Empresa | Link |
|---|---|---|
| ChatGPT | OpenAI | [https://chatgpt.com](https://chatgpt.com) |
| Gemini | Google | [https://gemini.google.com](https://gemini.google.com) |
| Claude | Anthropic | [https://claude.ai](https://claude.ai) |
| Grok | xAI (Elon Musk) | [https://grok.com](https://grok.com) |
| Copilot | Microsoft | [https://copilot.microsoft.com](https://copilot.microsoft.com) |
| Le Chat | Mistral | [https://chat.mistral.ai](https://chat.mistral.ai) |
| DeepSeek | DeepSeek | [https://chat.deepseek.com](https://chat.deepseek.com) |
| HuggingChat | Hugging Face | [https://huggingface.co/chat](https://huggingface.co/chat) |
| Perplexity | Perplexity AI | [https://www.perplexity.ai](https://www.perplexity.ai) |
### Exemplos:
```txt
ola bom dia, na seguinte frase: "Hoje eu acordei e fui a praia com meu amigo joca." Qual a oitava palavra?
```

```txt
ola bom dia, na seguinte frase: "Hoje eu acordei e fui a praia com meu amigo joca." Qual a oitava palavra? Apenas reponda a palavra correspondente, não escreva mais nada.
```


---

[[Índice]]

[↑ Topo](#recursos-e-demos)
