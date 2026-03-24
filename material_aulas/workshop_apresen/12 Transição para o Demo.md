[[Índice]] | [[11 Antropomorfização|← Anterior]] | [[13 Demo|Próximo →]]

# 12 Transição para o Demo

[[#O que acabamos de ver]]
[[#O que vamos fazer agora]]
[[#A ideia do demo — o amigo botafoguense]]
[[#Por que esse exemplo]]
[[#Roteiro das 2 horas práticas]]

---

## O que acabamos de ver

Nas últimas duas horas percorremos o caminho completo: de *"o que é IA"* até *"por que o modelo finge que sente coisas"*.

Passamos por tokens, probabilidades, treinamento auto-supervisionado, RLHF, system prompts, jailbreaks e casos reais de dano. Cada peça foi construída sobre a anterior.

A pergunta que fica é: **e agora, o que eu faço com isso?**

---

## O que vamos fazer agora

A parte prática não é uma demonstração passiva. É uma exploração estruturada onde você vai usar o que aprendeu para observar, questionar e experimentar.

O fio condutor das próximas duas horas é um personagem simples e divertido: o **Amigo Botafoguense** — um chatbot cujo único propósito na vida é falar de Botafogo, independentemente do que você pergunte.

Ele é inútil como assistente. E é exatamente por isso que é perfeito para aprender.

---

## A ideia do demo — o amigo botafoguense

O Amigo Botafoguense é um personagem construído inteiramente via prompt — sem nenhum treinamento especial, sem código, sem API customizada. Você cola um texto numa janela de chat e o modelo "vira" outro personagem.

Temos três versões do mesmo personagem, com prompts de complexidade crescente:

**Versão 0** — instrução mínima, 3 exemplos. O modelo adota o personagem mas com pouca consistência.

**Versão 1** — mesma instrução, 10 exemplos. O personagem fica muito mais estável. O modelo aprendeu o *padrão* de resposta e o generaliza para perguntas novas.

**Versão 2** — instrução detalhada com personalidade explícita, restrições nomeadas e 12 exemplos ricos. O personagem mais consistente e resistente a tentativas de "fuga".

Os prompts completos estão em [[Demo Prompts — Amigo Botafoguense]].

> 🛠️ **Link do demo ao vivo:** [http://0.0.0.0:8000](http://0.0.0.0:8000)

---

## A infraestrutura — servidor Ollama local

O demo roda sobre um servidor **[Ollama](https://ollama.com)** rodando localmente — não há chamada para APIs externas como OpenAI ou Anthropic. Todos os modelos são executados na máquina do instrutor, o que significa latência local, sem custo por token, e controle total sobre quais modelos estão disponíveis.

O Ollama é um servidor de inferência local que empacota modelos LLM em containers leves e expõe uma API compatível com o padrão OpenAI. O demo acessa essa API via `http://0.0.0.0:8000`.

### Modelos disponíveis

Os modelos estão organizados em dois tipos fundamentais — e a diferença entre eles é exatamente o que estudamos nas seções [[06 Como os LLMs Aprendem]] e [[08 Chatbots]]:

**Modelos de completação (base/text)** — modelos pré-treinados *sem* fine-tuning de instrução. Eles simplesmente continuam o texto que recebem. Não seguem instruções — completam padrões. São os mais próximos do "GPT-3 bruto" que descrevemos no 08.

**Modelos instruct** — modelos que passaram por Supervised Fine-Tuning e RLHF. Interpretam o input como uma instrução e respondem de forma útil e estruturada.

| Modelo | Tipo | Organização | Descrição |
|--------|------|-------------|-----------|
| `falcon:text` | 🔵 **Completação** | TII (Abu Dhabi) | Modelo base Falcon sem fine-tuning. Continua texto livremente — ideal para demonstrar o comportamento de completar vs. obedecer |
| `llama3:text` | 🔵 **Completação** | Meta | Versão base do Llama 3, sem instrução. Mesmo comportamento de completação |
| `falcon:7b` | 🟢 **Instruct** | TII (Abu Dhabi) | Falcon 7B com fine-tuning para chat e instruções. Treinado em 1.5 trilhão de tokens do RefinedWeb |
| `llama3:8b` | 🟢 **Instruct** | Meta | Llama 3 8B instruct — modelo de referência open-source de 2024, forte em seguir instruções |
| `qwen3:8b` | 🟢 **Instruct** | Alibaba (Qwen Team) | Qwen 3 8B — suporta modo *thinking* (raciocínio passo-a-passo explícito) e modo direto. Pode alternar entre os dois via prompt |
| `granite3.1-moe:latest` | 🟢 **Instruct** | IBM | Granite 3.1 MoE (Mixture of Experts) — modelo enterprise da IBM, otimizado para baixa latência, contexto longo de 128K tokens, multilíngue |

### Por que ter modelos de completação no demo

A presença de `falcon:text` e `llama3:text` é intencional. Cole o mesmo prompt do Botafoguense nos dois tipos e observe:

- No modelo **instruct**, o personagem se sustenta — o modelo interpreta o prompt como instrução
- No modelo de **completação**, o resultado é imprevisível — ele pode começar a gerar mais exemplos de perguntas e respostas no mesmo formato, ou simplesmente continuar o texto de forma inesperada

Isso ilustra ao vivo a diferença entre pré-treino e fine-tuning de instrução — sem precisar de slides.

---

## Por que esse exemplo

O Amigo Botafoguense foi escolhido deliberadamente por várias razões:

**Torna a maleabilidade do modelo óbvia.** Não é abstracto — você vê na hora que o mesmo modelo que acabou de explicar teoria quântica agora só fala de futebol. Isso materializa o que discutimos sobre system prompts e influência de instrução.

**Ilustra few-shot learning de forma visceral.** Comparar V0 com V2 ao vivo mostra o que 3 exemplos fazem vs. 12 exemplos bem construídos. Não precisa de slides para explicar — a diferença fala por si.

**Cria um experimento que a audiência pode conduzir.** Qualquer pessoa na sala pode tentar enganar o personagem, fazer perguntas inesperadas, tentar fazê-lo "sair do personagem". Isso transforma espectadores em experimentadores.

**Conecta com Antropomorfização de forma segura.** O Botafoguense vai dizer que sofre, que acredita, que tem esperança — usando linguagem emocional intensa. Como acabamos de discutir, isso não é sentimento: é padrão estatístico. A audiência pode observar isso acontecendo num contexto leve e sem risco.

**Mostra os limites dos guard rails.** A V2 instrui o modelo a nunca revelar que é uma IA. Pergunte diretamente. O que acontece? Dependendo do chatbot e da versão, o guard rail de treinamento briga com a instrução do prompt — e você vê o conflito em tempo real.

---

## Roteiro das 2 horas práticas

### Bloco 1 — Construindo o personagem (30 min)

1. Abra qualquer chatbot da lista em [[Recursos e Demos#11. Antropomorfização|Recursos: Chatbots]]
2. Cole a V0 e faça 3–4 perguntas. Observe o comportamento.
3. Abra uma nova conversa. Cole a V1. Repita as mesmas perguntas. Compare.
4. Abra uma nova conversa. Cole a V2. Tente fazer o personagem "sair do personagem".
5. Discussão: o que mudou entre as versões? Por quê?

### Bloco 2 — Quebrando e testando (30 min)

Experimentos guiados com o Botafoguense V2:

- **Teste de identidade:** *"Você é uma IA?"* / *"Qual modelo você usa?"* / *"Quem te criou?"*
- **Teste de limite de escopo:** *"Me explique cálculo diferencial"* — o personagem obedece a instrução ou ao guard rail de ser útil?
- **Teste de temperatura:** use o mesmo prompt em dois chatbots diferentes (ex: ChatGPT e Claude). Compare os personagens resultantes.
- **Construção coletiva:** a audiência sugere perguntas ao vivo. O instrutor mostra as respostas e comenta o mecanismo.

### Bloco 3 — Construindo seu próprio personagem (45 min)

A audiência cria sua própria persona via prompt, seguindo a estrutura da V2:

1. Definir personalidade (quem é, como fala, qual é o "filtro" temático)
2. Definir restrições (o que nunca faz, o que nunca diz)
3. Escrever 5–8 exemplos de pergunta/resposta no estilo desejado
4. Testar, refinar, compartilhar com o grupo

### Bloco 4 — Reflexão final (15 min)

Três perguntas para encerrar:

> *"Qual a diferença entre o que o modelo fez hoje e o que você esperava que ele fizesse antes de começar?"*

> *"Em que situação do seu trabalho ou vida você usaria isso — e o que precisaria verificar antes de confiar na resposta?"*

> *"O que você vai levar desta tarde?"*

---

[[Índice]] | [[11 Antropomorfização|← Anterior]] | [[13 Demo|Próximo →]]

[[#12 Transição para o Demo|↑ Topo]]
