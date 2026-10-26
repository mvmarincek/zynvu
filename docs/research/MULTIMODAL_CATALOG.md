# Avaliação de áudio e visão — 2026-10-26

## Transcrição incluída como candidata de planejamento

- [whisper.cpp](https://github.com/ggml-org/whisper.cpp/blob/231638a0717b7822784297e5980965ffcec05810/README.md):
  documenta execução CPU e plataformas Windows/Linux/macOS, além da tabela de RAM.
- [Artefatos do publicador](https://huggingface.co/ggerganov/whisper.cpp/tree/5359861c739e955e79d9a303bcbc70fb988958b1):
  tiny/base/small multilíngues GGML. A manutenção consultou somente metadados,
  tamanhos e hashes LFS, nunca os arquivos de pesos.
- [Whisper original](https://github.com/openai/whisper/blob/86098128c0b4f24f0e2aa2994de830614b474227/README.md)
  e [licença](https://github.com/openai/whisper/blob/86098128c0b4f24f0e2aa2994de830614b474227/LICENSE).

Planejamento CPU com estimativa publicada e margem documentada em ESTIMATES.md.
Português disponível no modelo multilíngue; qualidade, latência e throughput não
testados localmente. Não confundir ASR com TTS ou execução de comandos de voz.

## Visão avaliada, ainda fora do catálogo

- [SmolVLM 500M original](https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct/tree/a7da5b986cb59b408707209984f360a5f4ad7e47)
  tem licença Apache-2.0, model card em inglês e configuração textual de 8192 posições.
- [Conversão ggml-org](https://huggingface.co/ggml-org/SmolVLM-500M-Instruct-GGUF/tree/72e986006ef53e37cdd3f6d4241c90b0f01df376)
  contém modelo Q8_0 de 436806912 bytes e projetor visual Q8_0 de 108783360 bytes.
  Contar somente o decoder subestimaria disco e RAM.
- [Documentação multimodal do llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/multimodal.md).

Antes de incluir: definir orçamento por resolução/número de imagens/crops, memória
do encoder, contexto disponível após tokens visuais e tratamento de PT-BR.
O simples tamanho dos pesos ou um benchmark GPU de outro runtime não basta para
afirmar viabilidade em CPU. Ainda não há estimador visual implementado nem garantia
de leitura de telas, OCR ou automação. Nenhum peso foi baixado ou executado.
