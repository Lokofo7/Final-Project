# CodeCraftHub — Parte 1, Opção B (Python/Flask)

CodeCraftHub é uma plataforma de aprendizagem para desenvolvedores acompanharem os cursos que desejam estudar. Este projeto contém o backend em Python/Flask da Parte 1, com implementação, testes e documentação correspondentes às quatro primeiras páginas do laboratório IBM. Os dados ficam em `courses.json`, sem banco de dados ou autenticação.

Uma API recebe pedidos de outros programas e devolve dados. Aqui, cada endpoint é um endereço que permite uma operação: criar (POST), consultar (GET), atualizar (PUT) ou excluir (DELETE). Esse conjunto é chamado CRUD. As informações são enviadas e recebidas em JSON, um formato de texto com campos e valores.

## Funcionalidades

- Cadastrar cursos com nome, descrição, data prevista de conclusão e status.
- Listar todos os cursos e consultar um curso pelo ID.
- Atualizar informações e acompanhar o progresso com três status permitidos.
- Excluir cursos em qualquer status.
- Persistir os dados em JSON e criar o arquivo automaticamente quando ausente.
- Validar entradas e retornar mensagens de erro JSON com códigos HTTP adequados.
- Permitir chamadas de navegador por CORS e verificar o comportamento com testes automatizados e curl.

## Arquivos e requisitos atendidos

| Arquivo | Responsabilidade |
| --- | --- |
| `app.py` | Cinco endpoints, validação, erros JSON, CORS e funções auxiliares. |
| `courses.json` | Lista de cursos; começa com `[]` e é criada automaticamente se ausente. |
| `requirements.txt` | Dependências Flask e Flask-Cors. |
| `README.md` | Instalação, execução, exemplos e solução de problemas. |
| `test_app.py` | Testes automatizados que usam apenas arquivos temporários. |
| `TESTES.md` | Resultados da validação desta entrega. |
| `TESTES_PAGINA_3.md` | Oito casos com comandos curl, exemplos JSON e respostas esperadas. |
| `.venv/` | Ambiente Python local com as dependências do projeto. |
| `.gitignore` | Evita incluir o ambiente e arquivos temporários no controle de versão. |

`load_courses()` lê o arquivo a cada operação; `save_courses(courses)` salva as alterações; `get_next_id(courses)` retorna o maior ID atual + 1, ou 1 na lista vazia. Por essa regra simples, excluir o maior ID permite reutilizá-lo posteriormente.

## Executar no Windows / PowerShell

Abra o terminal na pasta `codecrafthub`. Nesta máquina, o ambiente `.venv` foi preparado para o projeto. Execute:

```powershell
.\.venv\Scripts\python.exe app.py
```

Consulte a API em <http://127.0.0.1:5000/api/courses>. A resposta inicial é `[]`. Mantenha esse terminal aberto e use outro para os testes. Para encerrar, pressione `Ctrl+C`.

## Instalação passo a passo

Conforme a quinta página, `requirements.txt` fixa Flask 3.0.0 e Werkzeug 3.0.1. Flask-Cors 6.0.5 permanece como dependência adicional para o CORS já solicitado no projeto. Essas versões foram instaladas e verificadas localmente.

1. Copie a pasta `codecrafthub` ou baixe o código do [repositório do projeto](https://github.com/Lokofo7/Final-Project). Se usar Git, execute `git clone https://github.com/Lokofo7/Final-Project.git` e abra a pasta `Final-Project`; nesse caso ela é a pasta do projeto nos passos seguintes.
2. Tenha Python 3.9 ou superior com pip instalado. Confira a instalação com `py -3 --version`. Para os testes manuais, confira também `curl.exe --version`.
3. Abra a pasta `codecrafthub` no Explorador de Arquivos e escolha **Abrir no Terminal**. Os comandos abaixo devem ser executados nessa pasta, onde está `app.py`.
4. Crie o ambiente Python isolado:

```powershell
py -3 -m venv .venv
```

5. Instale as dependências. Esta etapa precisa de acesso à internet em uma instalação nova:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

6. Inicie a aplicação e mantenha o terminal aberto:

```powershell
.\.venv\Scripts\python.exe app.py
```

Se `py` não estiver disponível, substitua `py -3` pelo comando `python` de uma instalação funcional. Não é necessário ativar o ambiente nem alterar a política de execução do PowerShell. A pasta `.venv` é local; recrie-a se mover o projeto ou trocar de computador.

## Modelo e validação

```json
{
  "id": 1,
  "name": "Python Basics",
  "description": "Learn Python fundamentals",
  "target_date": "2026-12-31",
  "status": "Not Started",
  "created_at": "2026-11-12 12:00:00"
}
```

- No POST, `name`, `description`, `target_date` e `status` são obrigatórios; textos vazios, tipos incorretos e campos desconhecidos são rejeitados.
- `target_date` aceita uma data real no formato `YYYY-MM-DD`. Datas passadas são permitidas, pois o laboratório não exige restringi-las.
- `status` aceita exatamente `Not Started`, `In Progress` ou `Completed`. Se omitido no POST, a API retorna 400, conforme a segunda página.
- `id` é inteiro positivo e `created_at` é gerado em UTC no formato do exemplo acima. Ambos são definidos pelo servidor e não podem ser enviados ou alterados pelo cliente.
- O PUT aceita um ou mais campos editáveis e preserva os demais. Um objeto vazio é rejeitado; `id` e `created_at` são preservados.
- POST e PUT exigem `Content-Type: application/json`. Espaços nas extremidades dos textos são removidos.

## Endpoints

| Método | Caminho | Sucesso |
| --- | --- | --- |
| POST | `/api/courses` | `201` + curso criado e cabeçalho `Location`. |
| GET | `/api/courses` | `200` + lista de cursos. |
| GET | `/api/courses/<id>` | `200` + curso encontrado. |
| PUT | `/api/courses/<id>` | `200` + curso atualizado. |
| DELETE | `/api/courses/<id>` | `200` + mensagem de confirmação. |

Substitua `<id>` pelo número retornado na criação; por exemplo, `/api/courses/1`. O GET geral retorna uma lista JSON; POST, GET por ID e PUT retornam o objeto do curso diretamente. IDs e horários dos exemplos são ilustrativos.

Corpo JSON de exemplo para **POST /api/courses** (não envie `id` nem `created_at`):

```json
{
  "name": "Python Basics",
  "description": "Learn Python fundamentals",
  "target_date": "2026-12-31",
  "status": "Not Started"
}
```

Corpo JSON de exemplo para **PUT /api/courses/1**:

```json
{"status": "In Progress"}
```

GET e DELETE não precisam de corpo JSON. Após excluir, a resposta é `{"message":"Curso excluído com sucesso."}`. A seção de testes abaixo contém comandos para os cinco endpoints.

Erros seguem o mesmo formato, incluindo rotas e métodos inexistentes:

```json
{"error": {"code": "not_found", "message": "Curso não encontrado."}}
```

Códigos: `400` para dados/JSON inválidos; `404` para recurso inexistente; `405` para método não permitido; `415` para conteúdo que não seja JSON; `500` para falha interna ou no armazenamento.

## Testar o CRUD com curl no PowerShell

Com o servidor ativo, abra outro PowerShell na pasta do projeto. Usar `curl.exe` evita confusão com o alias `curl` de versões antigas do PowerShell. Os exemplos alteram os dados locais; a última operação remove o curso de exemplo.

```powershell
$base = 'http://127.0.0.1:5000/api/courses'
$payload = '{"name":"Python Basics","description":"Learn Python fundamentals","target_date":"2026-12-31","status":"Not Started"}'

# Criar: o status HTTP esperado é 201. Captura o ID real retornado.
$result = $payload | curl.exe -sS -w '\n%{http_code}' -X POST "$base" -H 'Content-Type: application/json' --data-binary '@-'
$result
$course = ($result[0..($result.Count - 2)] -join "`n") | ConvertFrom-Json
$courseId = $course.id

# Listar e consultar: 200.
curl.exe -i "$base"
curl.exe -i "$base/$courseId"

# Atualizar: 200; mantém os campos que não foram enviados.
'{"status":"In Progress"}' | curl.exe -i -X PUT "$base/$courseId" -H 'Content-Type: application/json' --data-binary '@-'

# Excluir: 200. Consultar depois: 404 com erro JSON.
curl.exe -i -X DELETE "$base/$courseId"
curl.exe -i "$base/$courseId"
```

Validação e CORS:

```powershell
# Status inválido: 400, sem criar um curso.
'{"name":"Test","description":"Test","target_date":"2026-12-31","status":"Done"}' | curl.exe -i -X POST "$base" -H 'Content-Type: application/json' --data-binary '@-'

# Preflight: 200 e cabeçalhos Access-Control-Allow-*.
curl.exe -i -X OPTIONS "$base" -H 'Origin: http://localhost:5173' -H 'Access-Control-Request-Method: POST' -H 'Access-Control-Request-Headers: Content-Type'
```

Para conferir persistência, crie um curso, reinicie o servidor e consulte seu ID antes de excluí-lo. O arquivo é localizado ao lado de `app.py`, independentemente da pasta usada para iniciar o servidor.

## Testes automatizados

Para a terceira página do laboratório, consulte [TESTES_PAGINA_3.md](TESTES_PAGINA_3.md): oito casos com comandos curl para PowerShell, payloads JSON e respostas esperadas, conferidos contra o servidor local.

Na pasta do projeto, execute sem precisar iniciar o servidor:

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_app
```

Os 16 testes passaram e não alteram seu `courses.json`. Na versão da segunda página, eles incluem a obrigatoriedade de `status`. Na terceira página, os oito casos com curl passaram contra a versão atual; as 14 verificações HTTP da versão inicial estão registradas como histórico em [TESTES.md](TESTES.md). Os servidores de teste foram encerrados após as verificações.

## Armazenamento e CORS

A gravação usa um arquivo temporário e substituição do JSON após concluir. Requisições de alteração são coordenadas dentro do mesmo processo; execute uma única instância da API usando esse arquivo. JSON corrompido ou com estrutura inválida retorna erro 500 e é preservado para correção, em vez de ser apagado.

CORS está habilitado em `/api/*` para qualquer origem, sem credenciais, com GET, POST, PUT, DELETE e OPTIONS. O servidor de desenvolvimento escuta somente em `127.0.0.1`, com depuração desativada.

## Solução de problemas e próximos passos

| Situação | Ação |
| --- | --- |
| `python` ou `py` abre a loja ou falha | Use o Python de `.venv` já preparado; para recriá-lo, instale Python e confirme `python --version`. |
| `No module named flask` | Execute o comando de instalação usando o Python de `.venv`. |
| Porta 5000 ocupada | Encerre a outra instância ou use `.\.venv\Scripts\python.exe -m flask --app app run --port 5001`. |
| A página `/` mostra 404 | Use `/api/courses`; este backend ainda não tem página inicial. |
| curl não consegue conectar | Inicie o servidor, mantenha o terminal aberto e confira a porta. Se usar 5001, atualize também a URL nos comandos de teste. |
| POST retorna 400 | Envie os quatro campos obrigatórios, uma data válida e um dos três status aceitos. Leia a mensagem JSON retornada. |
| POST ou PUT retorna 415 | Inclua o cabeçalho `Content-Type: application/json`. |
| Erro 500 ao ler/salvar | Confira a permissão da pasta e a estrutura de `courses.json`. Faça uma cópia antes de corrigir dados manualmente. |

Próximo passo do curso: conferir as próximas páginas da **Parte 1** e eventuais evidências solicitadas. Não foram implementados dashboard, busca, estatísticas, banco ou autenticação. A Parte 2 não foi iniciada.

Referências técnicas: [instalação do Flask](https://flask.palletsprojects.com/en/stable/installation/) e [configuração do Flask-Cors](https://flask-cors.readthedocs.io/en/latest/).
