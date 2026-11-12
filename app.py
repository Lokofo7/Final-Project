"""CodeCraftHub, Parte 1: API Flask com armazenamento em arquivo JSON."""

import json
import os
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from threading import RLock

from flask import Flask, jsonify, request, url_for
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, HTTPException, NotFound, UnsupportedMediaType

app = Flask(__name__)
app.json.ensure_ascii = False
app.config["COURSES_FILE"] = Path(__file__).resolve().with_name("courses.json")
CORS(
    app,
    resources={r"/api/.*": {"origins": "*"}},
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
    expose_headers=["Location"],
)

VALID_STATUSES = ("Not Started", "In Progress", "Completed")
EDITABLE_FIELDS = {"name", "description", "target_date", "status"}
REQUIRED_FIELDS = {"name", "description", "target_date", "status"}
# Protege o ciclo ler-alterar-salvar entre requisições do mesmo processo.
storage_lock = RLock()


class StorageError(Exception):
    """O arquivo não pode ser lido ou salvo com segurança."""


def validate_course_data(data, partial=False):
    """Valida os campos enviados e devolve uma cópia normalizada."""
    if not isinstance(data, dict) or not data:
        raise BadRequest("Envie um objeto JSON não vazio.")
    unknown = set(data) - EDITABLE_FIELDS
    if unknown:
        raise BadRequest("Campos não permitidos: " + ", ".join(sorted(unknown)) + ".")
    if not partial:
        missing = REQUIRED_FIELDS - set(data)
        if missing:
            raise BadRequest("Campos obrigatórios: " + ", ".join(sorted(missing)) + ".")

    cleaned = {}
    for field, value in data.items():
        if not isinstance(value, str) or not value.strip():
            raise BadRequest(f"O campo '{field}' deve ser um texto não vazio.")
        cleaned[field] = value.strip()

    if "target_date" in cleaned:
        try:
            parsed_date = date.fromisoformat(cleaned["target_date"])
        except ValueError as exc:
            raise BadRequest("target_date deve ser uma data válida no formato YYYY-MM-DD.") from exc
        if parsed_date.isoformat() != cleaned["target_date"]:
            raise BadRequest("target_date deve usar o formato YYYY-MM-DD.")
    if "status" in cleaned and cleaned["status"] not in VALID_STATUSES:
        raise BadRequest("status deve ser Not Started, In Progress ou Completed.")
    return cleaned


def load_courses():
    """Lê o JSON a cada chamada; cria [] somente se o arquivo não existir."""
    path = Path(app.config["COURSES_FILE"])
    with storage_lock:
        try:
            if not path.exists():
                save_courses([])
            with path.open("r", encoding="utf-8-sig") as file:
                courses = json.load(file)
            if not isinstance(courses, list):
                raise ValueError("O conteúdo deve ser uma lista.")
            seen_ids = set()
            for course in courses:
                if not isinstance(course, dict) or set(course) != EDITABLE_FIELDS | {"id", "created_at"}:
                    raise ValueError("Registro de curso inválido.")
                course_id = course["id"]
                if type(course_id) is not int or course_id < 1 or course_id in seen_ids:
                    raise ValueError("Identificador inválido ou duplicado.")
                seen_ids.add(course_id)
                validate_course_data({key: course[key] for key in EDITABLE_FIELDS})
                if not isinstance(course["created_at"], str):
                    raise ValueError("created_at inválido.")
                datetime.strptime(course["created_at"], "%Y-%m-%d %H:%M:%S")
            return courses
        except (OSError, UnicodeError, ValueError, BadRequest) as exc:
            raise StorageError("Não foi possível ler os cursos. Verifique courses.json; o arquivo foi preservado.") from exc


def save_courses(courses):
    """Grava primeiro em arquivo temporário e substitui o JSON após concluir."""
    path = Path(app.config["COURSES_FILE"])
    temporary_path = None
    with storage_lock:
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=path.parent,
                prefix=path.name + ".", suffix=".tmp", delete=False,
            ) as file:
                temporary_path = Path(file.name)
                json.dump(courses, file, ensure_ascii=False, indent=2)
                file.write("\n")
            os.replace(temporary_path, path)
        except (OSError, TypeError, ValueError) as exc:
            raise StorageError("Não foi possível salvar os cursos. Verifique a permissão de escrita.") from exc
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink(missing_ok=True)


def get_next_id(courses):
    """Gera o próximo ID como o maior ID existente mais um (ou 1)."""
    return max((course["id"] for course in courses), default=0) + 1


def read_course_payload(partial=False):
    """Exige Content-Type JSON e trata JSON malformado como erro 400."""
    if not request.is_json:
        raise UnsupportedMediaType("Use Content-Type: application/json.")
    try:
        data = request.get_json()
    except BadRequest as exc:
        raise BadRequest("O corpo da requisição contém JSON inválido.") from exc
    return validate_course_data(data, partial=partial)


def find_course(courses, course_id):
    """Localiza um curso ou informa que ele não existe."""
    for course in courses:
        if course["id"] == course_id:
            return course
    raise NotFound("Curso não encontrado.")


@app.get("/api/courses")
def list_courses():
    """Lista todos os cursos, inclusive uma lista vazia."""
    return jsonify(load_courses())


@app.get("/api/courses/<int:course_id>")
def get_course(course_id):
    """Consulta um curso pelo ID."""
    return jsonify(find_course(load_courses(), course_id))


@app.post("/api/courses")
def create_course():
    """Cria um curso e gera os campos id e created_at no servidor."""
    data = read_course_payload()
    with storage_lock:
        courses = load_courses()
        course = {
            "id": get_next_id(courses),
            **data,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        }
        courses.append(course)
        save_courses(courses)
    response = jsonify(course)
    response.status_code = 201
    response.headers["Location"] = url_for("get_course", course_id=course["id"])
    return response


@app.put("/api/courses/<int:course_id>")
def update_course(course_id):
    """Atualiza os campos enviados; mantém os demais e os campos gerados."""
    data = read_course_payload(partial=True)
    with storage_lock:
        courses = load_courses()
        course = find_course(courses, course_id)
        course.update(data)
        save_courses(courses)
    return jsonify(course)


@app.delete("/api/courses/<int:course_id>")
def delete_course(course_id):
    """Exclui um curso e confirma a operação em JSON."""
    with storage_lock:
        courses = load_courses()
        course = find_course(courses, course_id)
        courses.remove(course)
        save_courses(courses)
    return jsonify({"message": "Curso excluído com sucesso."})


@app.errorhandler(HTTPException)
def handle_http_error(error):
    """Converte também erros de rota e método em JSON, mantendo os headers."""
    response = error.get_response()
    response.data = app.json.dumps({
        "error": {
            "code": error.name.lower().replace(" ", "_"),
            "message": error.description,
        }
    })
    response.content_type = "application/json"
    return response


@app.errorhandler(StorageError)
def handle_storage_error(error):
    app.logger.error("Falha no armazenamento: %s", error)
    return jsonify({"error": {"code": "storage_error", "message": str(error)}}), 500


@app.errorhandler(500)
def handle_unexpected_error(error):
    return jsonify({"error": {
        "code": "internal_server_error", "message": "Erro interno ao processar a requisição."
    }}), 500


if __name__ == "__main__":
    print("CodeCraftHub API is starting...", flush=True)
    print(f"Data will be stored in: {app.config['COURSES_FILE']}", flush=True)
    print("API will be available at: http://localhost:5000", flush=True)
    app.run(host="127.0.0.1", port=5000, debug=False)
