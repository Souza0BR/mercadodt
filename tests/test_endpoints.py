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
        failures = 0

        r = client.get("/")
        print("/ ->", r.status_code, r.json)
        if r.status_code >= 500:
            failures += 1

        r = client.get("/promocoes")
        print("/promocoes ->", r.status_code)
        if r.status_code >= 500:
            failures += 1

        r = client.get("/encartes")
        print("/encartes ->", r.status_code, r.json)
        if r.status_code >= 500:
            failures += 1

        r = client.get('/geocodificar', query_string={"cep": "01001000"})
        print("/geocodificar ->", r.status_code, r.json)
        if r.status_code >= 500:
            failures += 1

        if failures:
            print(f"Testes terminaram com {failures} falhas")
            raise SystemExit(1)
        print("Testes concluídos sem falhas >=500")


if __name__ == "__main__":
    run_tests()
