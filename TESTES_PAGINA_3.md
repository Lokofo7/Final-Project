# Terceira página — testes da API

Comandos para Windows/PowerShell. Na pasta codecrafthub, inicie o servidor em um terminal:

```powershell
.\.venv\Scripts\python.exe app.py
```

Em outro terminal, execute os oito testes abaixo em ordem. Eles criam e depois excluem um curso de exemplo. O ID é capturado automaticamente, preservando os cursos existentes.

```powershell
$base = 'http://127.0.0.1:5000/api/courses'
```

As respostas abaixo foram obtidas com curl contra um servidor local usando arquivo temporário vazio. IDs e created_at variam; a listagem pode incluir seus cursos existentes. A data de 2025 foi mantida como no laboratório: datas passadas são permitidas.

O enunciado permite variações da resposta gerada. Nossa API devolve o curso diretamente e uma lista no GET geral; não utiliza o envelope success/course/count do exemplo. Os exemplos abaixo refletem a implementação real.

## 1. Criar curso — POST

```powershell
$payload = '{"name": "Python Basics", "description": "Learn Python fundamentals including variables, loops, and functions", "target_date": "2025-12-31", "status": "Not Started"}'
$raw = $payload | curl.exe -sS -w '
%{http_code}' -X POST $base -H 'Content-Type: application/json' --data-binary '@-'
$raw
$course = ($raw[0..($raw.Count - 2)] -join "`n") | ConvertFrom-Json
$courseId = $course.id
```

Resposta esperada: **HTTP 201**.

```json
{
  "created_at": "2026-11-12 15:00:49",
  "description": "Learn Python fundamentals including variables, loops, and functions",
  "id": 1,
  "name": "Python Basics",
  "status": "Not Started",
  "target_date": "2025-12-31"
}
```

## 2. Listar cursos — GET

```powershell
curl.exe -i $base
```

Resposta esperada: **HTTP 200**.

```json
[
  {
    "created_at": "2026-11-12 15:00:49",
    "description": "Learn Python fundamentals including variables, loops, and functions",
    "id": 1,
    "name": "Python Basics",
    "status": "Not Started",
    "target_date": "2025-12-31"
  }
]
```

## 3. Consultar curso — GET

```powershell
curl.exe -i "$base/$courseId"
```

Resposta esperada: **HTTP 200**.

```json
{
  "created_at": "2026-11-12 15:00:49",
  "description": "Learn Python fundamentals including variables, loops, and functions",
  "id": 1,
  "name": "Python Basics",
  "status": "Not Started",
  "target_date": "2025-12-31"
}
```

## 4. Atualizar curso — PUT

```powershell
'{"status":"In Progress"}' | curl.exe -i -X PUT "$base/$courseId" -H 'Content-Type: application/json' --data-binary '@-'
```

Resposta esperada: **HTTP 200**.

```json
{
  "created_at": "2026-11-12 15:00:49",
  "description": "Learn Python fundamentals including variables, loops, and functions",
  "id": 1,
  "name": "Python Basics",
  "status": "In Progress",
  "target_date": "2025-12-31"
}
```

## 5. Excluir curso — DELETE

```powershell
curl.exe -i -X DELETE "$base/$courseId"
```

Resposta esperada: **HTTP 200**.

```json
{
  "message": "Curso excluído com sucesso."
}
```

## 6. Campos obrigatórios ausentes

```powershell
'{"name":"Incomplete Course"}' | curl.exe -i -X POST $base -H 'Content-Type: application/json' --data-binary '@-'
```

Resposta esperada: **HTTP 400**.

```json
{
  "error": {
    "code": "bad_request",
    "message": "Campos obrigatórios: description, status, target_date."
  }
}
```

## 7. Status inválido

```powershell
'{"name": "Python Basics", "description": "Learn Python fundamentals including variables, loops, and functions", "target_date": "2025-12-31", "status": "Invalid Status"}' | curl.exe -i -X POST $base -H 'Content-Type: application/json' --data-binary '@-'
```

Resposta esperada: **HTTP 400**.

```json
{
  "error": {
    "code": "bad_request",
    "message": "status deve ser Not Started, In Progress ou Completed."
  }
}
```

## 8. Curso não encontrado

```powershell
curl.exe -i "$base/$courseId"
```

Resposta esperada: **HTTP 404**.

```json
{
  "error": {
    "code": "not_found",
    "message": "Curso não encontrado."
  }
}
```

Usamos o ID excluído no teste 5 para garantir o cenário 404. O ID 999 do exemplo pode existir caso você já tenha muitos cursos.

## Resultado da execução

Os oito casos passaram em 12/11/2026. Também foram conferidos os conteúdos retornados no fluxo CRUD e a lista final vazia. O arquivo de cursos do projeto foi preservado; o servidor temporário de testes foi encerrado.
