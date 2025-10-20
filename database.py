import psycopg2
from psycopg2 import sql

# sua string de conexão Neon
DATABASE_URL = "postgresql://neondb_owner:npg_0cBWG1gZKzxI@ep-silent-tree-a8y98xqg-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Cria as tabelas se não existirem
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        nome TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS presencas (
        id SERIAL PRIMARY KEY,
        usuario_id INTEGER REFERENCES usuarios(id),
        data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
