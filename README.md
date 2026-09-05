# MercadoDT

![CI](https://github.com/Souza0BR/mercadodt/actions/workflows/ci.yml/badge.svg)

Pequena API Flask para gerenciar promoções e encartes.

## Pré-requisitos

- Python 3.10+ instalado
- Git (opcional)

## Instalação

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

## Preparar o banco de dados

```bash
python create_db.py
python seed_db.py
```

## Executar a API

```bash
python app.py
```

## Docker

Executar via Docker:

```bash
docker build -t mercadodt:latest .
docker run -p 5000:5000 -v $(pwd)/logs:/app/logs mercadodt:latest
```

Ou com `docker-compose`:

```bash
docker-compose up --build
```


## Testes simples

```bash
python tests/test_endpoints.py
```

## Arquivos principais

- `app.py` - API Flask
- `schema.sql` - esquema do banco
- `create_db.py` - aplica `schema.sql` ao `promocoes.db`
- `seed_db.py` - insere dados de exemplo
- `tests/test_endpoints.py` - script de testes básicos

## Contribuições

- Faça um fork e envie PRs para melhorias.

## Licença

MIT
