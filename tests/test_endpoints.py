import json
from unittest.mock import patch

from app import app


class FakeResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


def fake_requests_get(url, params=None, headers=None, timeout=None):
    # ViaCEP
    if "viacep.com.br" in url:
        # return address for CEP 01001000
        return FakeResponse({
            "cep": params.get('cep', '01001000') if isinstance(params, dict) else "01001000",
            "logradouro": "Praça da Sé",
            "localidade": "São Paulo",
            "uf": "SP",
        })

    # Nominatim
    if "nominatim.openstreetmap.org" in url:
        return FakeResponse([
            {"lat": "-23.5503898", "lon": "-46.633081"}
        ])

    return FakeResponse({}, status_code=404)


def run_tests():
    client = app.test_client()

    with patch("requests.get", side_effect=fake_requests_get):
        # /
        r = client.get("/")
        data = r.get_json()
        print("/ ->", r.status_code, data)
        assert r.status_code == 200
        assert data.get("status") == "ok"

        # /promocoes
        r = client.get("/promocoes")
        data = r.get_json()
        print("/promocoes ->", r.status_code)
        assert r.status_code == 200
        assert isinstance(data, list)

        # /encartes
        r = client.get("/encartes")
        data = r.get_json()
        print("/encartes ->", r.status_code, data)
        assert r.status_code == 200
        assert isinstance(data, list)

        # /geocodificar
        r = client.get('/geocodificar', query_string={"cep": "01001000"})
        data = r.get_json()
        print("/geocodificar ->", r.status_code, data)
        assert r.status_code == 200
        assert "lat" in data and "lng" in data

        print("Testes concluídos sem falhas >=500")


if __name__ == "__main__":
    run_tests()
