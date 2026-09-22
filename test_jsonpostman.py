import re
import pytest


class TestGet:

    def test_status_code_200(self, session, base_url):
        response = session.get(f"{base_url}/get", params={"user_id": "1"})
        assert response.status_code == 200

    def test_content_type_json(self, session, base_url):
        response = session.get(f"{base_url}/get")
        assert "application/json" in response.headers["Content-Type"]

    def test_query_param_echoed(self, session, base_url):
        data = session.get(f"{base_url}/get", params={"user_id": "1"}).json()
        # httpbin всегда возвращает значения в виде списка
        assert data["args"]["user_id"] == ["1"]

    def test_url_contains_param(self, session, base_url):
        data = session.get(f"{base_url}/get", params={"user_id": "1"}).json()
        assert "user_id=1" in data["url"]

    def test_response_time(self, session, base_url):
        response = session.get(f"{base_url}/get")
        # публичный httpbin может отвечать медленно — порог 10 с
        assert response.elapsed.total_seconds() < 10.0

    def test_custom_header_echoed(self, session, base_url):
        response = session.get(
            f"{base_url}/get",
            headers={"X-Custom-Header": "test-value"}
        )
        data = response.json()
        # заголовки тоже возвращаются списком
        assert data["headers"]["X-Custom-Header"] == ["test-value"]


class TestPost:

    PAYLOAD = {"name": "Иван Иванов", "email": "ivan@example.com"}

    @pytest.fixture(scope="class")
    def post_response(self, session, base_url):
        return session.post(f"{base_url}/post", json=self.PAYLOAD)

    def test_status_code_200(self, post_response):
        assert post_response.status_code == 200

    def test_json_body_echoed(self, post_response):
        data = post_response.json()
        assert data["json"]["name"] == "Иван Иванов"
        assert data["json"]["email"] == "ivan@example.com"

    def test_content_type_sent(self, post_response):
        data = post_response.json()
        assert "application/json" in data["headers"]["Content-Type"]

    def test_response_time(self, post_response):
        assert post_response.elapsed.total_seconds() < 10.0


class TestPut:

    PAYLOAD = {"id": 1, "name": "Пётр Петров", "email": "petr@example.com"}

    @pytest.fixture(scope="class")
    def put_response(self, session, base_url):
        return session.put(f"{base_url}/put", json=self.PAYLOAD)

    def test_status_code_200(self, put_response):
        assert put_response.status_code == 200

    def test_data_is_updated(self, put_response):
        data = put_response.json()
        assert data["json"]["id"] == 1
        assert data["json"]["name"] == "Пётр Петров"
        assert data["json"]["email"] == "petr@example.com"

    def test_all_required_fields_present(self, put_response):
        data = put_response.json()["json"]
        for field in ("id", "name", "email"):
            assert field in data, f"Поле {field} отсутствует"


class TestNegativeCases:

    def test_status_404(self, session, base_url):
        response = session.get(f"{base_url}/status/404")
        assert response.status_code == 404

    def test_status_500(self, session, base_url):
        response = session.get(f"{base_url}/status/500")
        assert response.status_code == 500

    def test_get_with_invalid_query(self, session, base_url):
        response = session.get(f"{base_url}/get")
        assert response.status_code == 200
        assert response.json()["args"] == {}


class TestEmailValidation:

    def test_email_is_valid(self, session, base_url):
        data = session.post(
            f"{base_url}/post",
            json={"email": "test@example.com"}
        ).json()
        email = data["json"]["email"]
        assert "@" in email, f"Email без @: {email!r}"
        local, _, domain = email.partition("@")
        assert local, f"Пустая локальная часть: {email!r}"
        assert "." in domain, f"Домен без точки: {email!r}"
        assert " " not in email, f"Email содержит пробел: {email!r}"