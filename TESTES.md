# Validação — CodeCraftHub Parte 1

## Quinta página — execução local concluída

Em 12/11/2026, foram instalados Flask 3.0.0 e Werkzeug 3.0.1 conforme a página. Flask-Cors 6.0.5 foi mantido para o CORS. `pip check` confirmou dependências compatíveis.

A aplicação foi iniciada pelo Python de `.venv` executando `app.py`, em `127.0.0.1:5000`. As mensagens iniciais informam o endereço da API e o caminho do arquivo de dados.

| Verificação na versão atual | Resultado |
| --- | --- |
| POST, GET geral, GET por ID, PUT e DELETE via curl | Aprovados: 201 na criação e 200 nas demais operações. |
| Persistência em courses.json e consulta após reiniciar o processo | Aprovada; conteúdo e status preservados. |
| Status inválido e data impossível | 400, com erro JSON. |
| Conteúdo incorreto e recurso inexistente | 415 e 404, com erro JSON. |
| CORS e preflight | Aprovados. |
| Testes automatizados, incluindo campos ausentes e falhas de arquivo | 16 aprovados. |

Total: 14 verificações HTTP e 16 testes automatizados aprovados com as versões da quinta página. O curso de teste foi excluído, courses.json voltou a conter `[]` e o servidor foi encerrado. Para iniciar novamente na pasta do projeto: `.\.venv\Scripts\python.exe app.py`.

## Histórico das páginas anteriores

Terceira página: os oito casos solicitados foram executados com curl contra a versão atual e aprovados em 12/11/2026. Veja [TESTES_PAGINA_3.md](TESTES_PAGINA_3.md). A execução usou armazenamento temporário, preservou courses.json e encerrou o servidor de teste.

Executada em 12/11/2026 no Windows, com Python 3.12.14, Flask 3.1.3 e Flask-Cors 6.0.5. As dependências foram instaladas em `.venv`; a verificação `pip check` não identificou incompatibilidades.

## Testes automatizados: 16 aprovados

Execute na pasta do projeto: `.\.venv\Scripts\python.exe -m unittest -v test_app`.

| Área | Comportamento confirmado |
| --- | --- |
| CRUD e IDs | Criar, listar, consultar, atualizar, excluir; manter campos gerados; não duplicar IDs após exclusão intermediária. |
| Validação | Campos obrigatórios, tipos, textos vazios, JSON malformado, status e datas inválidos; campos do servidor protegidos. |
| HTTP e CORS | Erros JSON consistentes, métodos/rotas inválidos, Content-Type e preflight OPTIONS. |
| Persistência | Arquivo ausente criado automaticamente, releitura por requisição e JSON corrompido preservado. |
| Falha de gravação | Falha simulada na substituição do arquivo mantém os dados anteriores intactos. |
| Requisições simultâneas | 16 criações em 8 threads, sem cursos perdidos nem IDs duplicados, dentro de um processo. |

Os testes usam arquivos temporários. Foi confirmado que o arquivo de cursos da entrega permaneceu idêntico após sua execução. As mensagens de erro registradas durante os testes de falha são esperadas.

## Servidor real e curl: 14 verificações aprovadas na versão da primeira página

O servidor foi iniciado com `app.py`, acessado por curl e reiniciado durante a validação. Ele foi iniciado a partir de outra pasta para confirmar que o caminho de `courses.json` independe da pasta atual.

| Verificação | HTTP observado |
| --- | --- |
| Listagem inicial vazia | 200 |
| Criação de curso, incluindo caracteres acentuados | 201 |
| Consulta por ID | 200 |
| Listagem com curso criado | 200 |
| Atualização do status | 200 |
| Consulta após reiniciar o servidor, com dados preservados | 200 |
| Rejeição de status inválido | 400 |
| Rejeição de data impossível | 400 |
| Rejeição de Content-Type incorreto | 415 |
| Rota inexistente com resposta JSON | 404 |
| Preflight CORS com cabeçalhos de autorização de origem/método | 200 |
| Exclusão do curso | 200 |
| Consulta do curso excluído | 404 |
| Listagem final vazia | 200 |

**Estado da entrega:** servidor encerrado, `courses.json` contendo `[]`, dependências prontas nesta máquina. Para iniciar novamente: `.\.venv\Scripts\python.exe app.py`.

**Limites verificados:** backend local com uma instância, armazenamento JSON e nenhuma autenticação. Não houve validação de dashboard, publicação ou execução com múltiplos processos; esses itens não fazem parte desta entrega. Conferir as próximas páginas da Parte 1 e as evidências solicitadas antes da submissão. A Parte 2 não foi iniciada.
