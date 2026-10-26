# Segurança e privacidade

Versão 0.2.x é um Advisor local experimental. Não executa agentes, instala modelos
ou acessa provedores durante uso. O script de atualização de catálogo é separado
e acessa metadados públicos somente quando executado explicitamente.

Diagnóstico usa psutil e consulta CIM somente de leitura. Dados permanecem locais;
exportação é explícita. `output/`, ambientes, bancos e segredos são ignorados no Git.
Exportação remove chaves e padrões comuns de credenciais; isso não reconhece todo
tipo possível de segredo em texto livre. Não inclua credenciais no objetivo e
revise o arquivo antes de compartilhá-lo.

API somente loopback com bearer token obrigatório; sem CORS e sem logs de payload.
Não é adequada para exposição pública. Não usa TLS por ser local. O núcleo aplica
política de executores com deny prioritário; não há executor real nesta versão.

ZYNVU Studio usa servidor loopback separado, nonce temporário por execução, validação
de Host/Origin e recusa solicitações cross-site. CSP restringe scripts, estilos e
conexões à própria origem. Não usa fontes, analytics ou assets externos; links de
procedência só abrem sites externos por ação do usuário. Os resultados ficam em
memória até exportação explícita; não usa localStorage para dados de hardware.

Relate vulnerabilidades de forma privada por GitHub Security Advisories quando
habilitado no repositório. Não publique credenciais ou dados pessoais em issues.
