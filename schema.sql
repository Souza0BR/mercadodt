

CREATE TABLE lojas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rede TEXT NOT NULL,
    nome TEXT NOT NULL,
    endereco TEXT NOT NULL,
    cidade TEXT NOT NULL,
    lat REAL,
    lng REAL,
    data_cadastro TEXT DEFAULT (datetime('now'))
);

CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    categoria TEXT,
    marca TEXT
);

CREATE TABLE promocoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    loja_id INTEGER NOT NULL,
    preco_normal REAL,
    preco_promo REAL NOT NULL,
    data_inicio TEXT,
    data_fim TEXT,
    data_coleta TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (produto_id) REFERENCES produtos(id),
    FOREIGN KEY (loja_id) REFERENCES lojas(id)
);

CREATE INDEX idx_promocoes_loja ON promocoes(loja_id);
CREATE INDEX idx_promocoes_produto ON promocoes(produto_id);
CREATE INDEX idx_produtos_nome ON produtos(nome);


CREATE TABLE encartes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loja_id INTEGER NOT NULL,
    url_imagem TEXT NOT NULL,        
    data_publicacao TEXT,            
    data_validade TEXT,              
    data_coleta TEXT DEFAULT (datetime('now')),  

    FOREIGN KEY (loja_id) REFERENCES lojas(id)
);

CREATE INDEX idx_encartes_loja ON encartes(loja_id);
