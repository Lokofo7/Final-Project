"""Testes de contrato da Parte 1, sempre usando armazenamento temporário."""

import importlib.util
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


PROJECT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("codecrafthub_app", PROJECT / "app.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CourseApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "courses.json"
        MODULE.app.config.update(TESTING=True, COURSES_FILE=self.path)
        self.client = MODULE.app.test_client()
        self.course = {
            "name": "Python básico",
            "description": "Introdução à programação",
            "target_date": "2026-12-31",
            "status": "Not Started",
        }

    def create(self, **changes):
        return self.client.post("/api/courses", json={**self.course, **changes})

    def assert_error(self, response, status):
        self.assertEqual(response.status_code, status, response.get_data(as_text=True))
        self.assertTrue(response.is_json)
        error = response.get_json()["error"]
        for key in ("code", "message"):
            self.assertIsInstance(error[key], str)
            self.assertTrue(error[key])

    def test_missing_file_created_as_empty_list(self):
        response = self.client.get("/api/courses")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), [])

    def test_complete_crud_preserves_server_fields(self):
        response = self.create()
        self.assertEqual(response.status_code, 201)
        course = response.get_json()
        self.assertEqual(set(course), set(self.course) | {"id", "status", "created_at"})
        self.assertEqual(course["status"], "Not Started")
        self.assertIs(type(course["id"]), int)
        self.assertGreater(course["id"], 0)
        datetime.fromisoformat(course["created_at"])
        url = f"/api/courses/{course['id']}"
        self.assertEqual(self.client.get(url).get_json(), course)
        self.assertEqual(self.client.get("/api/courses").get_json(), [course])
        response = self.client.put(url, json={"status": "In Progress"})
        self.assertEqual(response.status_code, 200)
        updated = response.get_json()
        self.assertEqual(updated, {**course, "status": "In Progress"})
        response = self.client.put(url, json={**self.course, "status": "Completed"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["created_at"], course["created_at"])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json()["message"], str)
        self.assert_error(self.client.get(url), 404)
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), [])

    def test_json_persists_and_is_reloaded_each_request(self):
        course = self.create(status="Completed").get_json()
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), [course])
        course["description"] = "Editado no arquivo"
        self.path.write_text(json.dumps([course], ensure_ascii=False), encoding="utf-8")
        fresh_client = MODULE.app.test_client()
        self.assertEqual(fresh_client.get("/api/courses").get_json(), [course])

    def test_ids_after_middle_deletion(self):
        courses = [self.create(name=f"Curso {n}").get_json() for n in range(3)]
        self.client.delete(f"/api/courses/{courses[1]['id']}")
        created = self.create().get_json()
        self.assertGreater(created["id"], courses[2]["id"])
        ids = [course["id"] for course in self.client.get("/api/courses").get_json()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(MODULE.get_next_id([]), 1)

    def test_required_fields(self):
        for key in self.course:
            with self.subTest(key=key):
                payload = {k: v for k, v in self.course.items() if k != key}
                self.assert_error(self.client.post("/api/courses", json=payload), 400)

    def test_invalid_text_fields(self):
        for field in ("name", "description"):
            for value in ("", "   ", None, 7, True, [], {}):
                with self.subTest(field=field, value=value):
                    self.assert_error(self.create(**{field: value}), 400)

    def test_invalid_dates(self):
        for value in ("2026-02-30", "2026-1-01", "20261112", "2026-12-31T00:00:00", "", None, 7):
            with self.subTest(value=value):
                self.assert_error(self.create(target_date=value), 400)
        self.assertEqual(self.create(target_date="2028-02-29").status_code, 201)

    def test_status_enum(self):
        for value in ("Not Started", "In Progress", "Completed"):
            with self.subTest(valid=value):
                self.assertEqual(self.create(status=value).status_code, 201)
        for value in ("completed", "Paused", "", None, 2, []):
            with self.subTest(invalid=value):
                self.assert_error(self.create(status=value), 400)

    def test_unknown_and_server_fields_rejected(self):
        course = self.create().get_json()
        for field, value in (("id", 99), ("created_at", "forged"), ("extra", "x")):
            with self.subTest(field=field):
                self.assert_error(self.create(**{field: value}), 400)
                response = self.client.put(f"/api/courses/{course['id']}", json={field: value})
                self.assert_error(response, 400)

    def test_invalid_update_does_not_change_storage(self):
        course = self.create().get_json()
        url = f"/api/courses/{course['id']}"
        original = self.path.read_bytes()
        for payload in ({}, {"name": ""}, {"description": None}, {"status": "Paused"}, {"target_date": "2026-02-30"}):
            with self.subTest(payload=payload):
                self.assert_error(self.client.put(url, json=payload), 400)
                self.assertEqual(self.path.read_bytes(), original)

    def test_malformed_json_and_non_object_body(self):
        for raw in ("{", "[]", "null", '"text"', "42", "true"):
            with self.subTest(raw=raw):
                response = self.client.post("/api/courses", data=raw, content_type="application/json")
                self.assert_error(response, 400)
        self.assert_error(self.client.post("/api/courses", data="name=Python"), 415)

    def test_missing_resource_route_and_method_errors(self):
        for method in ("get", "delete"):
            self.assert_error(getattr(self.client, method)("/api/courses/999"), 404)
        self.assert_error(self.client.put("/api/courses/999", json={"status": "Completed"}), 404)
        self.assert_error(self.client.get("/missing"), 404)
        self.assert_error(self.client.patch("/api/courses", json={}), 405)

    def test_cors_get_error_and_preflight(self):
        origin = "http://localhost:5173"
        headers = {"Origin": origin}
        for url in ("/api/courses", "/api/courses/999"):
            response = self.client.get(url, headers=headers)
            self.assertIn(response.headers.get("Access-Control-Allow-Origin"), (origin, "*"))
        response = self.client.options("/api/courses/1", headers={
            **headers,
            "Access-Control-Request-Method": "PUT",
            "Access-Control-Request-Headers": "Content-Type",
        })
        self.assertLess(response.status_code, 300)
        self.assertIn(response.headers.get("Access-Control-Allow-Origin"), (origin, "*"))
        self.assertIn("PUT", response.headers.get("Access-Control-Allow-Methods", ""))
        self.assertIn("content-type", response.headers.get("Access-Control-Allow-Headers", "").lower())

    def test_corrupt_file_returns_json_error_without_overwriting(self):
        original = b'{"broken":'
        self.path.write_bytes(original)
        self.assert_error(self.client.get("/api/courses"), 500)
        self.assert_error(self.create(), 500)
        self.assertEqual(self.path.read_bytes(), original)

    def test_failed_replace_preserves_previous_data(self):
        self.assertEqual(self.create().status_code, 201)
        original = self.path.read_bytes()
        with patch.object(MODULE.os, "replace", side_effect=PermissionError("Teste de falha de escrita")):
            self.assert_error(self.create(name="Não deve ser salvo"), 500)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(self.path.parent.glob("*.tmp")), [])

    def test_concurrent_creates_keep_every_course_and_unique_ids(self):
        def create_in_own_client(number):
            with MODULE.app.test_client() as client:
                response = client.post("/api/courses", json={**self.course, "name": f"Curso {number}"})
                return response.status_code, response.get_json()

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(create_in_own_client, range(16)))
        self.assertTrue(all(status == 201 for status, _ in results), results)
        courses = self.client.get("/api/courses").get_json()
        self.assertEqual(len(courses), 16)
        self.assertEqual(len({course["id"] for course in courses}), 16)
        self.assertEqual({course["name"] for course in courses}, {f"Curso {n}" for n in range(16)})


if __name__ == "__main__":
    unittest.main(verbosity=2)
