from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import base64
import os
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from pyngrok import ngrok

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # defina FLASK_SECRET no ambiente em produção

# Configuração do banco Neon PostgreSQL
DB_URL = "postgresql://neondb_owner:npg_0cBWG1gZKzxI@ep-silent-tree-a8y98xqg-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require"

# Face++ API (substitua pelas suas chaves)
FACEPP_API_KEY = "6l33ri1N4hSM2g2VHfNag80IFfQJ1MlK"
FACEPP_API_SECRET = "PnPRljUfsnm9ioNEVCVE4K-Z1qTwXYjw"

# Threshold de confiança para considerar reconhecimento
CONFIDENCE_THRESHOLD = 80

# Pasta para salvar rostos
ROSTOS_DIR = "rostos"
if not os.path.exists(ROSTOS_DIR):
    os.makedirs(ROSTOS_DIR, exist_ok=True)

def get_db_connection():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

# ------------------------------
# ROTA: Login (usuário + senha)
# ------------------------------
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario_email = request.form.get('usuario', '').strip()
        senha = request.form.get('senha', '')

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM usuarios WHERE usuario=%s OR email=%s", (usuario_email, usuario_email))
                user = cur.fetchone()
        finally:
            conn.close()

        if user and check_password_hash(user['senha'], senha):
            session['user_id'] = user['id']
            session['usuario'] = user['usuario']
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha incorretos', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# ------------------------------
# ROTA: Cadastro
# ------------------------------
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        usuario = request.form.get('usuario', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        senha_hash = generate_password_hash(senha)

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM usuarios WHERE usuario=%s OR email=%s", (usuario, email))
                existing_user = cur.fetchone()
                if existing_user:
                    flash("Usuário ou email já existe.", "danger")
                    return redirect(url_for('cadastro'))

                cur.execute(
                    "INSERT INTO usuarios (nome, usuario, email, senha) VALUES (%s, %s, %s, %s)",
                    (nome, usuario, email, senha_hash)
                )
                conn.commit()
        finally:
            conn.close()

        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for('login'))

    return render_template('cadastro.html')

# ------------------------------
# ROTA: Salvar rosto (Cadastro)
# Recebe JSON { usuario: 'username', imagem: 'data:image/jpeg;base64,...' }
# ------------------------------
@app.route('/salvar_rosto', methods=['POST'])
def salvar_rosto():
    data = request.get_json() or {}
    imagem_data = data.get('imagem', '')
    usuario = data.get('usuario', '').strip()

    if not usuario or not imagem_data:
        return jsonify({"erro": "usuario ou imagem ausente"}), 400

    try:
        img_base64 = imagem_data.split(',', 1)[1] if ',' in imagem_data else imagem_data
        img_bytes = base64.b64decode(img_base64)
    except Exception:
        return jsonify({"erro": "imagem inválida"}), 400

    # Salva imagem no banco
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE usuarios SET rosto=%s WHERE usuario=%s", (psycopg2.Binary(img_bytes), usuario))
            conn.commit()
    finally:
        conn.close()

    return jsonify({"mensagem": "Rosto salvo no banco com sucesso!"})


# ------------------------------
# ROTA: Reconhecimento facial (entrada/saida)
# Recebe JSON { imagem: 'data:...,', acao: 'entrada'|'saida' }
# ------------------------------
@app.route('/reconhecimento_facial', methods=['POST'])
def reconhecimento_facial():
    data = request.get_json() or {}
    imagem_data = data.get('imagem', '')
    acao = data.get('acao', 'entrada')
    if acao not in ('entrada', 'saida'):
        acao = 'entrada'

    if not imagem_data:
        return jsonify({"erro": "imagem ausente"}), 400

    try:
        img_base64 = imagem_data.split(',', 1)[1] if ',' in imagem_data else imagem_data
        img_bytes = base64.b64decode(img_base64)
    except Exception:
        return jsonify({"erro": "imagem inválida"}), 400

    temp_path = os.path.join(ROSTOS_DIR, "temp.jpg")
    with open(temp_path, "wb") as f:
        f.write(img_bytes)

    # Percorre arquivos de rostos salvos e compara com a imagem temporária
    matched = None
    for fname in os.listdir(ROSTOS_DIR):
        if not fname.lower().endswith(('.jpg', '.jpeg', '.png')) or fname == "temp.jpg":
            continue
        stored_path = os.path.join(ROSTOS_DIR, fname)
        files = {
            'image_file1': open(temp_path, 'rb'),
            'image_file2': open(stored_path, 'rb')
        }
        data_api = {'api_key': FACEPP_API_KEY, 'api_secret': FACEPP_API_SECRET}
        try:
            response = requests.post("https://api-us.faceplusplus.com/facepp/v3/compare", files=files, data=data_api, timeout=10)
            res_json = response.json()
        except Exception:
            res_json = {}
        finally:
            for fh in files.values():
                try:
                    fh.close()
                except Exception:
                    pass

        confidence = res_json.get('confidence', 0)
        if confidence >= CONFIDENCE_THRESHOLD:
            matched = fname.rsplit('.', 1)[0]  # username (filename without extension)
            break

    if not matched:
        return jsonify({"mensagem": "Rosto não reconhecido!"}), 200

    # Encontrar usuário no banco e registrar presença
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM usuarios WHERE usuario=%s", (matched,))
            user = cur.fetchone()
            if not user:
                return jsonify({"mensagem": "Usuário reconhecido não existe no banco."}), 200
            user_id = user['id']
            # cria registro de presença
            cur.execute("INSERT INTO presencas (usuario_id, status) VALUES (%s, %s)", (user_id, acao))
            conn.commit()
    finally:
        conn.close()

    return jsonify({"mensagem": f"{acao.capitalize()} registrada para {matched}.", "confidence": confidence})

# ------------------------------
# ROTA: Página principal (index)
# Exibe contagem de presenças (entradas/saidas) e última presença
# ------------------------------
@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                  COUNT(*) FILTER (WHERE status IS NOT NULL) AS total_registros,
                  COUNT(*) FILTER (WHERE status = 'entrada') AS total_entradas,
                  COUNT(*) FILTER (WHERE status = 'saida') AS total_saidas,
                  MAX(data_hora) AS ultima_presenca
                FROM presencas
                WHERE usuario_id = %s
            """, (user_id,))
            stats = cur.fetchone()
    finally:
        conn.close()

    total_registros = stats['total_registros'] or 0
    total_entradas = stats['total_entradas'] or 0
    total_saidas = stats['total_saidas'] or 0
    ultima = stats['ultima_presenca']
    ultima_presenca = ultima.strftime('%d/%m/%Y %H:%M') if ultima else 'Nunca'

    # Passe os dados para o template index.html
    return render_template(
        'index.html',
        total_faltas=total_registros,      # se preferir outro cálculo, ajuste aqui
        limite_faltas=20,
        data_atualizacao=ultima_presenca,
        total_entradas=total_entradas,
        total_saidas=total_saidas
    )

# ------------------------------
# ROTA: Logout
# ------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ------------------------------
# EXECUÇÃO
# ------------------------------
if __name__ == "__main__":
    # Permite acesso via celular na mesma rede Wi-Fi
    app.run(host="0.0.0.0", port=5000, debug=True)