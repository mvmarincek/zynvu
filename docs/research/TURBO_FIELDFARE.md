# TurboFieldfare: candidato de runtime para Apple Silicon

Avaliação documental em 2026-10-26. Referência:
[`drumih/turbo-fieldfare`, revisão 2e9ea50](https://github.com/drumih/turbo-fieldfare/tree/2e9ea50e8c35a65d9170e3bff9d1063be8931ec0).
Não instalado, executado ou medido pelo ZYNVU. Não integra o catálogo de suporte.

O runtime Swift/Metal é específico para Gemma 4 26B-A4B e usa especialistas MoE
carregados do SSD. Manter parte dos pesos e caches na memória permite trabalhar
com um modelo maior que a RAM disponível. Suporte documentado: Apple Silicon,
macOS 26/Metal 4, Swift 6.2+ e armazenamento para cerca de 14,3 GB de modelo.
Os três comandos da imagem compilam o software; instalar os pesos é outra etapa.
[Requisitos e instalação](https://github.com/drumih/turbo-fieldfare/blob/2e9ea50e8c35a65d9170e3bff9d1063be8931ec0/README.md).

O autor reporta 5,10–6,30 tokens/s em um M2 de 8 GB, com aproximadamente 1,9–2,1 GB
de footprint. Um teste com 1.017 tokens de entrada levou 37.656 ms até o primeiro
token. Decode exclui instalação, carregamento e prefill; os resultados não são uma
garantia para outra máquina ou contexto.
[Metodologia e medições](https://github.com/drumih/turbo-fieldfare/blob/2e9ea50e8c35a65d9170e3bff9d1063be8931ec0/docs/BENCHMARKS.md).

## Implicação para o Advisor

O estimador atual atende os modelos GGUF residentes do catálogo inicial. Uma
extensão deve representar a combinação modelo/runtime/modo de carregamento,
separando armazenamento, memória residente, KV e buffers. Streaming exige estimar
I/O do SSD, cache, prefill e latência inicial; reduzir memória pelo quociente entre
parâmetros ativos e totais seria incorreto.
[Arquitetura e recursos](https://github.com/drumih/turbo-fieldfare/blob/2e9ea50e8c35a65d9170e3bff9d1063be8931ec0/docs/SYSTEM_DESIGN.md).

Antes de habilitar recomendações: revisar licenças do runtime e dos pesos, verificar
versões e APIs, modelar o orçamento específico e reproduzir testes em um Mac
compatível. A Fase 1 continua somente recomendação; eventual adapter de execução
pertence à Fase 2. Não extrapolar os números para Windows, Linux ou outro modelo.
