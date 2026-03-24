[[Índice]] | [[05 LLMs e Como Surgiram|← Anterior]] | [[07 Como o Modelo Decide|Próximo →]]

# 06 Como os LLMs Aprendem

[[#Aprendizado supervisionado vs auto-supervisionado]]
[[#Next Token Prediction — o caminho do GPT]]
[[#Masked Language Modeling — o caminho do BERT]]
[[#Por que isso permite escalar sem rótulos humanos]]
[[#Tokenização — as unidades do aprendizado]]
[[#Completando palavras — geração token a token]]

---

## Aprendizado supervisionado vs auto-supervisionado

No aprendizado supervisionado clássico, cada exemplo de treinamento precisa de um **rótulo** produzido por um humano: esta foto é um gato, este e-mail é spam, este tumor é maligno. O rótulo é o sinal que guia o modelo — sem ele, não há aprendizado.

Isso funciona bem em escala pequena. Mas para treinar um modelo sobre toda a linguagem humana — bilhões de documentos, dezenas de idiomas, código, ciência, literatura — seria necessário um exército de anotadores trabalhando por décadas. O custo é proibitivo.

O **aprendizado auto-supervisionado** contorna esse problema com uma ideia elegante:

> *O próprio texto é o rótulo.*

Não é necessário nenhum trabalho humano de anotação. O sinal de treinamento está escondido dentro dos dados — basta saber onde procurar.

---

## Next Token Prediction — o caminho do GPT

A estratégia do GPT é direta: **ocultar o fim da sequência e pedir ao modelo que o preveja**.

Dado o texto:

```
A Torre Eiffel fica em ___
```

O modelo deve prever: `Paris`. Dado:

```
Paris é a capital da ___
```

Deve prever: `França`. E assim por diante, sobre trilhões de sequências.

A cada previsão, o modelo compara sua resposta com a resposta correta (que estava no texto original) e ajusta seus pesos na direção certa. Sem nenhum rótulo externo — o próprio corpus é o professor.

O resultado é um modelo que internalizou uma enorme quantidade de estrutura sobre linguagem, fatos, relações e raciocínio — não porque foi ensinado explicitamente sobre esses tópicos, mas porque prever bem o próximo token *exige* modelar tudo isso.

---

## Masked Language Modeling — o caminho do BERT

O BERT usa uma variação: em vez de prever o que vem *depois*, ele **mascara palavras no meio da sequência** e pede ao modelo que as recupere a partir do contexto bidirecional.

Dado:

```
A Torre Eiffel fica em [MASK], capital da França.
```

O modelo deve prever: `Paris` — mas agora pode usar tanto o que vem antes quanto o que vem depois do token mascarado.

Isso força o modelo a construir representações ricas de significado contextual, o que o torna excelente para tarefas de *compreensão*. A desvantagem é que o modelo bidirecional não gera texto de forma natural — ele não foi treinado para escrever, mas para entender.

| | Next Token Prediction | Masked Language Modeling |
|---|---|---|
| Modelo | GPT | BERT |
| O que é ocultado | O fim da sequência | Tokens aleatórios no meio |
| Direção de leitura | Esquerda → direita | Bidirecional |
| Ponto forte | Geração de texto | Compreensão e classificação |

---

## Por que isso permite escalar sem rótulos humanos

A consequência prática é enorme. Todo texto que já foi escrito — livros, artigos, código, fóruns, notícias, legislação, receitas, enciclopédias — se torna automaticamente dado de treinamento, sem custo adicional de anotação.

A internet inteira é um conjunto de treinamento auto-supervisionado.

Isso explica a trajetória de escala dos LLMs. O GPT-2 foi treinado em ~40 GB de texto. O GPT-3 em ~570 GB. Modelos posteriores ultrapassaram trilhões de tokens. Cada incremento foi possível porque não havia gargalo humano no processo de anotação — bastava coletar mais texto e mais GPUs.

O aprendizado auto-supervisionado transformou um problema de *custo de anotação* num problema de *custo computacional*. E o custo computacional, diferente do custo humano, escala com dinheiro e hardware.

---

## Tokenização — as unidades do aprendizado

Antes de qualquer aprendizado, o texto precisa ser convertido numa forma que o modelo possa processar: uma sequência de números. Esse processo é a **tokenização**.

Um token não é necessariamente uma palavra. É um fragmento de texto — pode ser uma palavra inteira, uma sílaba, um prefixo, um sufixo, ou até um único caractere. A granularidade depende do algoritmo de tokenização e do vocabulário do modelo.

Por exemplo, a frase `"tokenização"` pode ser dividida como:

```
["token", "iza", "ção"]  →  [15432, 7891, 234]
```

Cada fragmento recebe um número inteiro — seu ID no vocabulário do modelo. É sobre essa sequência de IDs que todo o aprendizado acontece.

Algumas consequências não óbvias da tokenização:

**Palavras raras ou técnicas são divididas em mais tokens** — e portanto "custam mais" ao modelo processar e gerar. Uma palavra comum em inglês é frequentemente 1 token; uma palavra técnica em português pode ser 3 ou 4.

**O modelo não vê letras, vê tokens** — erros de ortografia, variações de capitalização e palavras compostas podem ser tokenizados de formas inesperadas, afetando o comportamento do modelo.

**Idiomas diferentes têm eficiências diferentes** — modelos treinados majoritariamente em inglês tokenizam inglês de forma mais compacta do que outros idiomas. Um texto em português pode exigir 20–30% mais tokens do que o equivalente em inglês.

**Números e código têm tokenizações próprias** — `12345` pode virar `["123", "45"]` dependendo do modelo, o que explica parte da dificuldade de LLMs com aritmética.

> 🛠️ **Demo — faça agora:**
>
> **1. [Runcell Token Counter](https://www.runcell.dev/tool/token-counter#counter)** — cole qualquer frase e veja quantos tokens ela tem. Tente a mesma frase em português e em inglês e compare.
>
> **2. [HuggingFace Tokenizer Playground](https://huggingface.co/spaces/Xenova/the-tokenizer-playground)** — escolha diferentes modelos (GPT-4, LLaMA, Mistral) e veja como o mesmo texto é dividido de formas distintas. Tente palavras técnicas, números, emojis e código.
>
> *Pergunta para a audiência: quantos tokens vocês acham que tem a frase "Inteligência Artificial Generativa"?*

---

## Completando palavras — geração token a token

Quando um LLM gera texto, ele não produz a resposta inteira de uma vez. Ele a constrói **um token por vez**, de forma autorregressiva:

1. Recebe a sequência de tokens até o momento
2. Calcula a distribuição de probabilidade sobre todos os tokens do vocabulário
3. Seleciona o próximo token (por argmax ou amostragem)
4. Acrescenta esse token à sequência
5. Repete — agora com a sequência um token mais longa

É por isso que os chatbots "escrevem" na sua frente em tempo real: cada token que aparece na tela é uma iteração desse ciclo. O modelo não estava "pensando" e depois "digitou" — ele foi construindo a resposta token a token, cada escolha condicionada em tudo que veio antes.

Isso tem uma implicação importante: **o modelo não pode "corrigir" um token que já emitiu**. Uma vez que um token foi gerado, ele entra no contexto e influencia todos os tokens seguintes. Se o modelo "errou" cedo numa resposta, os tokens seguintes foram condicionados nesse erro — o que pode amplificar o problema em vez de corrigi-lo.

Esse mecanismo também explica por que **o prompt importa tanto**: os tokens do prompt são o contexto inicial sobre o qual toda a geração é condicionada. Mudar uma palavra no prompt pode mudar completamente a direção da resposta — porque muda a distribuição de probabilidade do primeiro token gerado, que muda a do segundo, e assim por diante.

> 🛠️ **Demo — faça agora:**
>
> **1. [Next Token Prediction](https://alonsosilva-nexttokenprediction.hf.space)** — veja ao vivo as probabilidades dos candidatos ao próximo token para qualquer sequência que você digitar.


---

[[Índice]] | [[05 LLMs e Como Surgiram|← Anterior]] | [[07 Como o Modelo Decide|Próximo →]]

[[#06 Como os LLMs Aprendem|↑ Topo]]
