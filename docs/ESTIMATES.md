# Metodologia e proveniência

Cada entrada em `src/zynvu/data/catalog.json` aponta para a revisão oficial do
publicador, configuração da arquitetura, licença e hashes LFS dos pesos. As seis
entradas iniciais vêm de https://huggingface.co/Qwen. Suporte GGUF/CPU é baseado
nos model cards e em https://github.com/ggml-org/llama.cpp. Nenhum peso foi baixado.
O catálogo não atesta uma versão instalada de runtime nem benchmarks locais.

Unidades em GiB, inclusive campos históricos terminados em `_gb`.

- Pesos: soma dos bytes de todos os shards GGUF Q4_K_M oficiais.
- KV FP16: `2 × camadas × cabeças KV × dimensão da cabeça × contexto × 2 bytes`.
- Buffers: maior entre 0,25 GiB e 20% dos pesos (hipótese conservadora não medida).
- Overhead: 0,5 GiB; mais 0,25 GiB para planejar memória local.
- Reserva do SO: maior entre 2 GiB e 20% da RAM física.
- Limite de carga: RAM física menos reserva, limitado ainda à RAM disponível
  menos 0,5 GiB quando essa medição existe.
- Sequencial: maior etapa; concorrente: soma das etapas. Pesos iguais carregados
  uma vez no processo; KV multiplicado por agentes. Não cobre processos separados.
- Disco: todos os pesos × 1,1 + 0,5 GiB. Não estima coleção documental futura.

VRAM não entra no orçamento CPU; memória compartilhada nunca é somada à RAM.
Driver desconhecido não impede plano CPU e não habilita GPU.

Ranking: `fastest` minimiza memória; `highest_quality` maximiza soma de `log1p`
do tamanho em bilhões de parâmetros; `balanced` subtrai 0,4 × GiB de carga desse
indicador. São heurísticas explícitas, sem promessa de velocidade ou qualidade.
Desempate por identificador do catálogo. Perfis podem recomendar a mesma combinação.

O parser não é uma LLM e não interpreta toda a semântica/negação do português.
Use os requisitos estruturados para decisões confiáveis. Toda recomendação tem
status `candidate`; `verified` exige futuras medições e validações empíricas.

## Transcrição — catálogo 2026-10-26.1

Whisper tiny/base/small multilíngues usam artefatos GGML F16/F32 do publicador
do whisper.cpp, fixados por revisão e SHA-256. Licença MIT de pesos e código;
não aplicar a licença Apache-2.0 do ZYNVU aos modelos.

A tabela do runtime informa aproximadamente 273/388/852 MB de RAM,
respectivamente. Fonte fixada em `memory_source` de cada entrada. Convertemos MB
decimais para GiB e estimamos `max(pesos, RAM publicada) × 1,5 + 0,25 GiB`.
Os 50% e 0,25 GiB são hipóteses nossas, não medições do publicador. O overhead
global e a reserva do sistema continuam aplicados. Cada agente replica a parcela
de memória além dos pesos; os pesos são compartilhados somente no mesmo processo.

O escopo é áudio em blocos de até 30 segundos, uma entrada por agente. Não cobre
gravações inteiras em RAM, múltiplos arquivos por entrada, buffers de streaming
ilimitados, captura de microfone, síntese de voz ou execução de comandos. A janela
de contexto de conversa não se aplica a ASR; o cálculo de KV de LLM não é usado.
Português é coberto pelo modelo multilíngue, mas sua qualidade não foi medida aqui.

Modelos e runtimes não são instalados/executados pela Fase 1. Encontrar whisper-cli
no PATH não valida versão, plataforma ou desempenho. Fontes e notas permanecem no
catálogo e no Blueprint/relatório; os candidatos não são suporte testado localmente.
