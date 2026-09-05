import time
import requests

BASE = "http://127.0.0.1:5000"

endpoints = [
    ("/", {}),
    ("/promocoes", {}),
    ("/encartes", {}),
    # CEP conhecido válido para testes (Praça da Sé, SP)
    ("/geocodificar", {"cep": "01001000"}),
]


def call(ep, params=None):
    url = BASE + ep
    try:
        r = requests.get(url, params=params, timeout=10)
        print(f"{ep} -> {r.status_code}")
        try:
            print(r.json())
        except Exception:
            print(r.text[:200])
        return r.status_code
    except Exception as e:
        print(f"{ep} -> ERROR: {e}")
        return None


if __name__ == "__main__":
    # espera o servidor subir
    print("Aguardando servidor local...")
    time.sleep(1)
    failures = 0
    for ep, params in endpoints:
        status = call(ep, params)
        if status is None or status >= 500:
            failures += 1

    if failures:
        print(f"Testes terminaram com {failures} falhas")
        raise SystemExit(1)
    print("Testes concluídos sem falhas >=500")
