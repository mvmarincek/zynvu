# Segurança e privacidade

Versão 0.1.x é um Advisor local experimental. Não executa agentes, instala modelos
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

Relate vulnerabilidades de forma privada por GitHub Security Advisories quando
habilitado no repositório. Não publique credenciais ou dados pessoais em issues.
