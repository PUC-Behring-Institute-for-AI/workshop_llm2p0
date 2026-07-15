from guardrail_agents import GuardrailPipeline

pipeline = GuardrailPipeline()

while True:

    print()

    prompt = input("Você: ")

    if prompt.lower() == "exit":
        break

    resposta = pipeline.run(prompt)

    print()
    print("IA:")
    print(resposta)