# Base de conhecimento do ZYNVU

A pasta `context/` integra a base de conhecimento do projeto, complementando o trabalho existente e as instruções explícitas do usuário.

## Leitura antes de implementar

- Consulte `context/ZYNVU_Codex_Knowledge_Pack/zynvu_codex_kit/README.md` e leia todos os arquivos desse kit antes de escrever código, incluindo schemas e exemplos.
- Use `docs/DECISIONS_AND_SCOPE.md` dentro do kit para resolver divergências entre suas especificações. Instruções explícitas mais recentes do usuário prevalecem.
- Preserve o kit como referência. Concilie os requisitos com o código e as decisões existentes; não substitua trabalho anterior sem examinar seu estado.
- Diferencie requisitos, propostas, exemplos e funcionalidades realmente implementadas. Registre suposições e progresso na documentação da implementação.

## Diretrizes essenciais

- ZYNVU é universal, local-first, com advisor/SDK gratuitos; VOKI é apenas um consumidor opcional.
- Fase 1: diagnóstico real, recomendações, estimativas e exportação de Blueprint. Não instalar, baixar ou executar modelos/agentes nessa fase.
- Priorizar fundação e CLI/core; seguir os marcos e critérios de aceitação do kit.
- Validar compatibilidade, licenças e integrações em fontes oficiais antes de tratar candidatos como suporte confirmado.
- Aplicar políticas de execução em código; respeitar HID-only quando exigido pelo consumidor, com captura de tela separada.
- Manter comércio opcional e separado do core; pagamentos dependem de confirmação autenticada e idempotente do provedor.
- Interface e conteúdo para clientes em PT-BR por padrão; não incluir segredos em código, logs ou Blueprints.

## Estado observado em 2026-10-25

Na incorporação desta base, a raiz local continha somente `context/`, sem código-fonte de implementação ou repositório Git visível. Isso descreve este diretório, não presume ausência de trabalho em outros locais.
