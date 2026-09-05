import sqlite3
from datetime import datetime, timedelta

DB = "promocoes.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Inserir lojas
lojas = [
    ("Catarinão", "Catarinão - Rio do Sul Centro", "Rua Principal 1", "Rio do Sul", -27.2146, -49.6426),
    ("Mercado Ficticio", "Mercado Ficticio - Centro", "Av. Central 100", "São Paulo", -23.5505, -46.6333),
]
cur.executemany(
    "INSERT INTO lojas (rede, nome, endereco, cidade, lat, lng) VALUES (?,?,?,?,?,?)",
    lojas,
)

# Inserir produtos
produtos = [
    ("Arroz 5kg", "Mercearia", "MarcaX"),
    ("Carne Moída kg", "Açougue", "MarcaY"),
    ("Detergente 500ml", "Limpeza", "MarcaZ"),
]
cur.executemany(
    "INSERT INTO produtos (nome, categoria, marca) VALUES (?,?,?)",
    produtos,
)

# Obter ids
conn.commit()
cur.execute("SELECT id FROM lojas ORDER BY id ASC")
loja_ids = [r[0] for r in cur.fetchall()]
cur.execute("SELECT id FROM produtos ORDER BY id ASC")
produto_ids = [r[0] for r in cur.fetchall()]

# Inserir promocoes
hoje = datetime.now().date()
promocoes = [
    (produto_ids[0], loja_ids[0], 4.82, 4.23, str(hoje - timedelta(days=1)), str(hoje + timedelta(days=6))),
    (produto_ids[1], loja_ids[0], 13.16, 9.86, str(hoje - timedelta(days=1)), str(hoje + timedelta(days=6))),
    (produto_ids[2], loja_ids[0], 39.58, 28.11, str(hoje - timedelta(days=1)), str(hoje + timedelta(days=6))),
]
cur.executemany(
    "INSERT INTO promocoes (produto_id, loja_id, preco_normal, preco_promo, data_inicio, data_fim) VALUES (?,?,?,?,?,?)",
    promocoes,
)

# Inserir encartes (vazio de oferta, só para teste)
encartes = [
    (loja_ids[0], "https://example.com/encarte1.jpg", str(hoje - timedelta(days=2)), str(hoje + timedelta(days=5))),
]
cur.executemany(
    "INSERT INTO encartes (loja_id, url_imagem, data_publicacao, data_validade) VALUES (?,?,?,?)",
    encartes,
)

conn.commit()
print("Dados de exemplo inseridos em", DB)
conn.close()
