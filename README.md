# ZYNVU

**Advisor local de arquitetura de IA — versão inicial 0.1.0.**

Descreva um agente, revise os requisitos e receba combinações de modelos que
respeitam o hardware informado ou diagnosticado. Exporta Blueprint JSON e relatório
em português. Core gratuito, Apache-2.0, sem conta, cobrança ou conexão durante o uso.

## Começar no Windows

Python 3.11 ou superior. A instalação de dependências usa internet; o Advisor funciona offline.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\zynvu.exe desktop
```

Interface nativa inicial com Tkinter (incluído no instalador oficial do Python para
Windows); não é ainda um instalador Tauri. Em Linux, Tkinter pode exigir o pacote do SO.

## CLI

```powershell
.\.venv\Scripts\zynvu.exe diagnose --out output/hardware.json
.\.venv\Scripts\zynvu.exe parse "Quero conversar e programar" --out output/requirements.json
# Edite o JSON para revisar contexto, privacidade, capacidades e política.
.\.venv\Scripts\zynvu.exe advise --requirements output/requirements.json --hardware output/hardware.json --out output/blueprint.json --report output/report.md
.\.venv\Scripts\zynvu.exe validate output/blueprint.json
```

Omitir `--hardware` faz diagnóstico real. `--require-installed` exige runtime no
PATH (ainda sem validar sua versão). `--policy caminho.json` aplica uma política de
consumidor, como os exemplos do kit. Saídas: `0` sucesso, `2` entrada/arquivo inválido,
`3` nenhuma combinação viável. A recomendação não instala nem executa modelos.

## SDK e API local

```python
from zynvu import advise, diagnose, parse_goal

blueprint = advise(parse_goal("Quero ajuda para programar"), diagnose())
```

API opcional: defina `ZYNVU_API_TOKEN` com um segredo aleatório de pelo menos 32
caracteres e execute `zynvu serve --port 8765`. Escuta somente em `127.0.0.1`.
Todos os endpoints exigem `Authorization: Bearer <segredo>`; não aceita chamadas
com Origin de navegador nem habilita CORS.

- `GET /v1/hardware`: diagnóstico local.
- `GET /v1/catalog`: catálogo empacotado.
- `POST /v1/advise`: JSON com objetos `requirements` e `hardware`.

Não é um servidor público ou serviço de produção. Não exponha a porta por proxy.

## O que funciona

- Diagnóstico real CPU/RAM/disco e inventário Windows de GPU/driver, com proveniência.
- Extração heurística local de requisitos, editáveis em JSON.
- Seis entradas oficiais Qwen2.5/Qwen2.5-Coder Q4_K_M (0.5B, 1.5B, 7B), fixadas
  por revisão e hashes dos arquivos, para conversa e código.
- Filtros de OS/arquitetura/licença/contexto/runtime/tool calling, orçamento de
  memória e disco, cargas sequenciais/concorrentes e múltiplos agentes.
- Três perfis determinísticos, no-fit explícito, Blueprint validado no schema do kit.
- Política de executores com deny prioritário; HID-only sem fallback de software.
- Interface desktop inicial, CLI, SDK e API local autenticada.

## Limites desta versão

Recomendações em CPU; não presume aceleração ou mede VRAM. GPU integrada/unificada
não aumenta o orçamento de RAM. Linux/macOS têm diagnóstico básico, sem profiler
GPU. Velocidade/qualidade são heurísticas de tamanho/memória, **não benchmarks**.
Os três perfis podem coincidir. Parser por palavras-chave pode interpretar negações
incorretamente; revise o JSON. O catálogo não prova aptidão para todo idioma/tarefa.

Visão, voz, embeddings, validação de tool calling, conectores autenticados,
memória persistente, instalação/execução de agentes, treinamento e comércio estão
no roadmap. Memória/MCP aparecem apenas como plano, nunca como execução disponível.
Nenhuma cobrança, checkout ou implantação de produção foi configurada.

## Desenvolvimento

```powershell
.\.venv\Scripts\python.exe -m ruff check src tests scripts
.\.venv\Scripts\python.exe -m ruff format --check src tests scripts
.\.venv\Scripts\python.exe -m mypy src
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m build
```

Em outros sistemas use `.venv/bin/python`. CI cobre Windows e Linux com Python
3.11/3.13. Catálogo offline incluído no wheel. `scripts/refresh_catalog.py` é uma
ferramenta manual de manutenção que acessa somente metadados oficiais, não pesos;
revise seu diff e licenças antes de publicar atualização.

## Base de conhecimento

Especificações originais preservadas em
[`context`](context/ZYNVU_Codex_Knowledge_Pack/zynvu_codex_kit/README.md).
Veja [plano](docs/IMPLEMENTATION_PLAN.md), [decisões](docs/ASSUMPTIONS.md),
[metodologia](docs/ESTIMATES.md) e [segurança](SECURITY.md).
ZYNVU é universal; VOKI é apenas um consumidor com política própria.

Serviços pagos de implantação e suporte são previstos, separados do core gratuito.
Ainda não há checkout ou oferta comercial publicada.
