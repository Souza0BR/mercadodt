"""
Endpoints:
    GET /                 -> status da API
    GET /promocoes        -> lista de promoções (produto/preço) - tabelas prontas pro futuro (OCR)
    GET /encartes          -> lista de encartes (imagem do tabloide), com filtro opcional por localização
    GET /geocodificar      -> converte CEP em lat/lng (ViaCEP + Nominatim)
"""

import math
import logging
import sqlite3

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

DATABASE = "promocoes.db"

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Erro global: garante resposta JSON em exceções não tratadas
@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception("Unhandled exception: %s", e)
    return jsonify({"erro": "Erro interno no servidor"}), 500


def calcular_distancia_km(lat1, lng1, lat2, lng2):

    raio_terra_km = 6371

    lat1_rad, lng1_rad = math.radians(lat1), math.radians(lng1)
    lat2_rad, lng2_rad = math.radians(lat2), math.radians(lng2)

    delta_lat = lat2_rad - lat1_rad
    delta_lng = lng2_rad - lng1_rad

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return raio_terra_km * c


@app.route("/")
def home():
    logger.info("GET / -> status da API")
    return jsonify({"status": "ok", "mensagem": "API de promoções rodando"})


@app.route("/promocoes")
def listar_promocoes():
    logger.info("GET /promocoes chamada")
    query = """
        SELECT
            promocoes.id,
            produtos.nome AS produto,
            produtos.categoria,
            lojas.nome AS loja,
            lojas.rede,
            lojas.cidade,
            promocoes.preco_normal,
            promocoes.preco_promo,
            promocoes.data_inicio,
            promocoes.data_fim,
            promocoes.data_coleta
        FROM promocoes
        JOIN produtos ON promocoes.produto_id = produtos.id
        JOIN lojas ON promocoes.loja_id = lojas.id
        ORDER BY promocoes.data_coleta DESC
    """
    conn = None
    try:
        conn = get_db_connection()
        rows = conn.execute(query).fetchall()
    except sqlite3.Error as e:
        logger.exception("Erro ao acessar banco de dados ao listar promoções")
        if conn:
            conn.close()
        return jsonify({"erro": "Erro ao acessar banco de dados"}), 500
    finally:
        if conn:
            conn.close()

    promocoes = [dict(row) for row in rows]
    return jsonify(promocoes)


@app.route("/encartes")
def listar_encartes():
    """
    Retorna os encartes (imagem do tabloide de ofertas) por loja.

    Sem parâmetros: devolve todos os encartes, mais recentes primeiro.
    Com ?lat=X&lng=Y: devolve todos, cada um com a distância até o usuário,
        ordenados do mais perto pro mais longe.
    Com ?lat=X&lng=Y&raio=N: além de ordenar, só devolve os encartes de lojas
        dentro de N km.
    """
    conn = get_db_connection()

    query = """
        SELECT
            encartes.id,
            encartes.url_imagem,
            encartes.data_publicacao,
            encartes.data_validade,
            encartes.data_coleta,
            lojas.id AS loja_id,
            lojas.nome AS loja,
            lojas.rede,
            lojas.endereco,
            lojas.cidade,
            lojas.lat,
            lojas.lng
        FROM encartes
        JOIN lojas ON encartes.loja_id = lojas.id
        ORDER BY encartes.data_coleta DESC
    """
    logger.info("GET /encartes chamada")
    try:
        rows = conn.execute(query).fetchall()
    except sqlite3.Error as e:
        conn.close()
        logger.exception("Erro ao acessar banco de dados ao listar encartes")
        return jsonify({"erro": "Erro ao acessar banco de dados"}), 500
    finally:
        conn.close()

    encartes = [dict(row) for row in rows]


    lat_usuario = request.args.get("lat", type=float)
    lng_usuario = request.args.get("lng", type=float)
    raio_km = request.args.get("raio", type=float)

    if lat_usuario is not None and lng_usuario is not None:
        for encarte in encartes:
            lat = encarte.get("lat")
            lng = encarte.get("lng")
            if lat is None or lng is None:
                encarte["distancia_km"] = None
                continue
            try:
                encarte["distancia_km"] = round(
                    calcular_distancia_km(lat_usuario, lng_usuario, lat, lng), 2
                )
            except Exception:
                logger.exception("Erro ao calcular distância para encarte %s", encarte.get("id"))
                encarte["distancia_km"] = None

        if raio_km is not None:
            encartes = [e for e in encartes if e.get("distancia_km") is not None and e["distancia_km"] <= raio_km]

        encartes.sort(key=lambda e: e["distancia_km"] if e.get("distancia_km") is not None else float("inf"))

    return jsonify(encartes)


@app.route("/geocodificar")
def geocodificar_cep():
    """
    Converte um CEP em coordenadas (lat/lng), em duas etapas:
      1. ViaCEP: CEP -> endereço (rua, bairro, cidade, UF)
      2. Nominatim (OpenStreetMap): endereço -> lat/lng

    Uso: GET /geocodificar?cep=89160-000
    """
    cep = request.args.get("cep", "").replace("-", "").replace(".", "").strip()

    if not cep or not cep.isdigit() or len(cep) != 8:
        return jsonify({"erro": "Informe um CEP válido, ex: ?cep=89160000"}), 400

    # Etapa 1: ViaCEP - CEP para endereço
    logger.info("GET /geocodificar?cep=%s", cep)
    try:
        resposta_viacep = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
        resposta_viacep.raise_for_status()
        dados_endereco = resposta_viacep.json()
    except requests.RequestException:
        logger.exception("Erro ao consultar ViaCEP para cep=%s", cep)
        return jsonify({"erro": "Erro ao consultar ViaCEP"}), 502
    except ValueError:
        logger.exception("Resposta inválida do ViaCEP para cep=%s", cep)
        return jsonify({"erro": "Resposta inválida do ViaCEP"}), 502

    if dados_endereco.get("erro"):
        return jsonify({"erro": "CEP não encontrado"}), 404

    endereco_completo = (
        f"{dados_endereco.get('logradouro', '')}, "
        f"{dados_endereco.get('localidade', '')}, "
        f"{dados_endereco.get('uf', '')}, Brasil"
    )

    # Nominatim - endereço para lat/lng
    try:
        resposta_nominatim = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": endereco_completo, "format": "json", "limit": 1},
            headers={"User-Agent": "site-promocoes-supermercado"},
            timeout=5,
        )
        resposta_nominatim.raise_for_status()
        resultados = resposta_nominatim.json()
    except requests.RequestException:
        logger.exception("Erro ao consultar Nominatim para endereco=%s", endereco_completo)
        return jsonify({"erro": "Erro ao consultar Nominatim"}), 502
    except ValueError:
        logger.exception("Resposta inválida do Nominatim para endereco=%s", endereco_completo)
        return jsonify({"erro": "Resposta inválida do Nominatim"}), 502

    if not resultados:
        return jsonify({"erro": "Não foi possível localizar coordenadas para esse CEP"}), 404

    try:
        lat = float(resultados[0]["lat"])
        lng = float(resultados[0]["lon"])
    except (KeyError, ValueError, IndexError):
        logger.exception("Resposta inválida do Nominatim ao extrair lat/lng")
        return jsonify({"erro": "Resposta inválida do Nominatim"}), 502

    return jsonify(
        {
            "cep": cep,
            "endereco": endereco_completo,
            "lat": lat,
            "lng": lng,
        }
    )


if __name__ == "__main__":

    app.run(debug=True, port=5000)
