import sqlite3

conn = sqlite3.connect("database.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS consultas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receita_alpha REAL,
    receita_beta REAL,
    custo_alpha REAL,
    custo_beta REAL,
    interacao REAL,
    x_otimo REAL,
    y_otimo REAL,
    lucro REAL,
    classificacao TEXT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()
print("Banco criado com sucesso!")