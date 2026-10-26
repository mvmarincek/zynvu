# Decisões de implementação

- Licença Apache-2.0 aprovada explicitamente pelo usuário em 2026-10-25.

- GiB (2^30 bytes) é a unidade dos campos históricos `*_gb` do contrato.
- A recomendação inicial usa CPU; VRAM detectada é informativa até validar um
  backend GPU. Não inferir aceleração pela presença de uma placa.
- Ausência de runtime permite planejamento com requisito de instalação explícito;
  `--require-installed` exige um executável local. Presença no PATH não comprova
  versão, drivers ou compatibilidade: toda recomendação permanece `candidate`.
- Estimativas incluem pesos GGUF, KV FP16, buffers, overhead e reserva do SO.
- Perfis podem coincidir quando o catálogo não oferece três combinações distintas.
- Parser local por palavras-chave é heurístico: requisitos estruturados explícitos
  prevalecem e devem ser revisados. Não existe chamada oculta a LLM/cloud.
- Catálogo inicial serve conversação e código; a versão 0.3 adiciona planejamento
  de transcrição Whisper multilíngue. Visão e síntese de voz ainda exigem expansão.
  Memória de ASR usa tabela publicada com margem explícita, sem benchmark local.
- Interface inicial em Tkinter substituída pelo ZYNVU Studio a pedido do usuário:
  HTML/CSS/JavaScript locais, responsivos e sem build obrigatório. Servidor Python
  reutiliza o SDK; API de integração permanece independente. Instalador Tauri futuro.
