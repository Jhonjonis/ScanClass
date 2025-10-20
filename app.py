from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # altere para algo mais seguro em produção

# Configuração do banco Neon PostgreSQL
DB_URL = "postgresql://neondb_owner:npg_0cBWG1gZKzxI@ep-silent-tree-a8y98xqg-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require"

# Função para conectar ao banco
def get_db_connection():
    conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
    return conn

# Página de login
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario_email = request.form['usuario']
        senha = request.form['senha']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE usuario=%s OR email=%s", (usuario_email, usuario_email))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user['senha'], senha):
            session['user_id'] = user['id']
            session['usuario'] = user['usuario']
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha incorretos', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Página de cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        usuario = request.form['usuario']
        email = request.form['email']
        senha = request.form['senha']
        senha_hash = generate_password_hash(senha)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE usuario=%s OR email=%s", (usuario, email))
        existing_user = cur.fetchone()
        if existing_user:
            flash("Usuário ou email já existe.", "danger")
            conn.close()
            return redirect(url_for('cadastro'))

        cur.execute(
            "INSERT INTO usuarios (nome, usuario, email, senha) VALUES (%s, %s, %s, %s)",
            (nome, usuario, email, senha_hash)
        )
        conn.commit()
        conn.close()
        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for('login'))

    return render_template('cadastro.html')

# Página principal (index) com dados de frequência
@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT total_faltas, limite_faltas FROM frequencias WHERE usuario_id=%s", (user_id,))
    frequencia = cur.fetchone()
    conn.close()

    total_faltas = frequencia['total_faltas'] if frequencia else 0
    limite_faltas = frequencia['limite_faltas'] if frequencia else 20
    data_atualizacao = datetime.now().strftime('%d/%m/%Y %H:%M')

    return render_template(
        'index.html',
        total_faltas=total_faltas,
        limite_faltas=limite_faltas,
        data_atualizacao=data_atualizacao
    )

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
