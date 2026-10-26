# Plano de implementação

Fonte: `context/ZYNVU_Codex_Knowledge_Pack/zynvu_codex_kit/`. Preservar os originais.

## Ordem e critérios

1. M0: pacote instalável, contratos, documentação, CI, lint, tipos e testes.
2. M1: CLI/SDK offline, requisitos revisáveis, profiler Windows com proveniência,
   catálogo fixado em revisões oficiais, combinações determinísticas, orçamento de
   recursos, três perfis e no-fit, Blueprint validado e relatório PT-BR.
3. M2: interface local e API sobre o mesmo núcleo; empacotamento desktop posteriormente.
4. M3: catálogo de conectores e comércio independente com adapters de sandbox,
   sem habilitar produção sem credenciais e validações.
5. M4/M5: runtime e aprendizado somente após os gates da Fase 1.
6. Criar/publicar repositório GitHub ao final da entrega validada.

## Escolha técnica

Python 3.11+ para o primeiro núcleo/CLI/SDK: disponível neste ambiente, bibliotecas
de diagnóstico e validação maduras, facilita distribuição sem toolchain Rust.
Não acoplar o algoritmo à interface. Tauri/React permanece candidato para o
instalador desktop; esta escolha não altera os contratos JSON do kit.

## Estrutura

`src/zynvu/`: contratos, hardware, catálogo, requisitos, políticas, engine e CLI.
`src/zynvu/data/`: schema e catálogo offline com proveniência.
`tests/`: fixtures e testes de compatibilidade, memória, política, exportação e CLI.
`docs/`: decisões, metodologia, operação e limitações.

## Verificação

Ruff (formato/lint), mypy, pytest, build do wheel e smoke test da instalação.
RAM 4/8/16/32 GiB; VRAM 4/8/16 GiB; memória compartilhada, VM, drivers ausentes,
disco baixo, OS não suportado, concorrência, catálogos incompletos e HID-only.
Recomendações são estimativas, não benchmarks. Não executar modelos nesta fase.

## Riscos e pendências

Metadados oficiais não comprovam performance local. Catálogo inicial limitado;
capacidades sem candidatos devem produzir no-fit explícito. Licença do projeto
Apache-2.0 aprovada pelo usuário. Credenciais/domínio de comércio não fornecidos.

## Progresso

- M0: pacote, licença, documentação, regras de contribuição e CI implementados.
- M1 inicial: CLI/SDK, diagnóstico Windows, seis modelos oficiais conversa/código,
  estimador CPU, filtros, ranking, política e Blueprint implementados. Catálogo
  multimodal, medição VRAM e verificação de versões/runtime continuam pendentes;
  não declarar o gate completo da Fase 1 atingido.
- M2: ZYNVU Studio web local responsivo, comparação visual, catálogo, diagnóstico,
  requisitos avançados e exportação implementados; API de integração independente.
  Instalador desktop e auditoria completa de acessibilidade permanecem pendentes.
- 55 testes, lint e typecheck passaram no Windows. Diagnóstico real e exportação
  CLI validados. Studio revisado visualmente em desktop e viewport de 390 px,
  sem overflow horizontal observado. A revisão anterior do Tkinter foi substituída
  por esta validação do novo frontend.
- Wheel/sdist construídos; instalação em ambiente separado, geração de Blueprint
  offline e `pip check` validados. Saída CLI em UTF-8 inclusive em pipes Windows.
- GitHub: código publicado no repositório público `mvmarincek/zynvu`, com licença
  Apache-2.0 e workflow de CI para Windows/Linux, Python 3.11/3.13.
- M3/M4/M5 não iniciados. Não habilitar runtime antes de completar gates da Fase 1.

## Evolução visual solicitada pelo usuário

- Substituição da tela Tkinter por Studio com sidebar, badges de estado, identidade
  escura/verde-lima, fluxo de briefing, cards de hardware e três perfis comparáveis.
- Rotas Studio/Catálogo/Blueprint funcionais; requisitos avançados e feedback de
  resultados desatualizados. Assets locais, sem download de fontes ou scripts.
- Teste visual no navegador: briefing de código, diagnóstico real e comparação
  concluídos; Blueprint e catálogo navegáveis, sem erros de console observados.
- Requisitos avançados: erro de JSON, aplicação de contexto personalizado e
  capacidades sem candidatos verificados pela interface. Resultados anteriores
  ficam identificados quando o briefing muda. Não há persistência oculta.
