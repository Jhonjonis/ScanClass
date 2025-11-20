

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import base64
import requests
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configurações do banco Neon PostgreSQL
DB_URL = "postgresql://neondb_owner:npg_0cBWG1gZKzxI@ep-silent-tree-a8y98xqg-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require"

# Face++ API
FACEPP_API_KEY = "6l33ri1N4hSM2g2VHfNag80IFfQJ1MlK"
FACEPP_API_SECRET = "PnPRljUfsnm9ioNEVCVE4K-Z1qTwXYjw"
CONFIDENCE_THRESHOLD = 80

def get_db_connection():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

# ------------------------------
# Salvar rosto no banco
# ------------------------------
@app.route('/salvar_rosto', methods=['POST'])
def salvar_rosto():
    data = request.get_json() or {}
    usuario = data.get('usuario', '').strip()
    imagem_data = data.get('imagem', '')
    nome = data.get('nome', '').strip()
    email = data.get('email', '').strip()
    senha = data.get('senha', '')
    curso = data.get('curso','').strip()
    matricula = data.get('matricula', '').strip()
    
   
    if not usuario or not imagem_data or not nome or not email or not senha or not curso or not matricula:
        return jsonify({"erro": "Dados incompletos"}), 400

   
    if not imagem_data or imagem_data.strip() == '':
        return jsonify({"erro": "É necessário cadastrar um rosto para prosseguir"}), 400

    if imagem_data == 'data:,' or len(imagem_data) < 100:  
        return jsonify({"erro": "Imagem do rosto inválida ou muito pequena"}), 400

    try:
       
        if ',' in imagem_data:
            img_base64 = imagem_data.split(',', 1)[1]
            # Verifica se há dados após a vírgula
            if not img_base64.strip():
                return jsonify({"erro": "Imagem do rosto está vazia"}), 400
        else:
         
            if not imagem_data.strip():
                return jsonify({"erro": "Imagem do rosto não fornecida"}), 400
            img_base64 = imagem_data
        
  
        rosto_bytes = base64.b64decode(img_base64)
        

        if len(rosto_bytes) < 1000:  
            return jsonify({"erro": "Imagem do rosto muito pequena ou inválida"}), 400
            
    except Exception as e:
        print(f"Erro ao processar imagem: {e}")
        return jsonify({"erro": "Imagem do rosto inválida ou corrompida"}), 400

    senha_hash = generate_password_hash(senha)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM usuarios WHERE usuario=%s OR email=%s", (usuario, email))
            existing = cur.fetchone()
            if existing:
                return jsonify({"erro": "Usuário ou email já cadastrado"}), 400

            cur.execute(
                "INSERT INTO usuarios (nome, usuario, email, senha, rosto, curso, matricula) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (nome, usuario, email, senha_hash, psycopg2.Binary(rosto_bytes),curso,matricula)
            )
            conn.commit()
    except psycopg2.Error as e:
        print(f"Erro no banco de dados: {e}")
        return jsonify({"erro": "Erro interno do servidor"}), 500
    finally:
        conn.close()

    return jsonify({
        "mensagem": "Cadastro concluído com sucesso!",
        "redirect": url_for('login')
    })

@app.route('/health')
def health():
    return 'OK', 200
# ------------------------------
# Reconhecimento facial
# ------------------------------
@app.route('/reconhecimento_facial', methods=['POST'])
def reconhecimento_facial():
    data = request.get_json() or {}
    imagem_data = data.get('imagem', '')
    acao = data.get('acao', 'entrada')
    usuario_input = data.get('usuario', '').strip()

    # Validações iniciais
    if not imagem_data:
        return jsonify({"erro": "Imagem ausente"}), 400

    try:
        img_base64 = imagem_data.split(',', 1)[1] if ',' in imagem_data else imagem_data
        img_bytes = base64.b64decode(img_base64)
        
        # Verificar se a imagem não está vazia
        if len(img_bytes) < 1000:
            return jsonify({"erro": "Imagem muito pequena ou inválida"}), 400
            
    except Exception as e:
        print(f"Erro ao decodificar imagem: {e}")
        return jsonify({"erro": "Imagem inválida"}), 400

    matched = None
    confidence_matched = 0

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Se usuário foi informado, buscar apenas esse usuário
            if usuario_input:
                cur.execute("SELECT usuario, rosto FROM usuarios WHERE (usuario=%s OR email=%s) AND rosto IS NOT NULL", 
                           (usuario_input, usuario_input))
            else:
                # Buscar todos os usuários com rosto cadastrado
                cur.execute("SELECT usuario, rosto FROM usuarios WHERE rosto IS NOT NULL")
            
            usuarios = cur.fetchall()

            if not usuarios:
                return jsonify({"erro": "Nenhum usuário com rosto cadastrado encontrado"}), 400

            for u in usuarios:
                username = u['usuario']
                rosto_bytes_db = u['rosto']

                files = {
                    'image_file1': ('captura.jpg', img_bytes, 'image/jpeg'),
                    'image_file2': ('rosto.jpg', rosto_bytes_db, 'image/jpeg')
                }
                data_api = {
                    'api_key': FACEPP_API_KEY, 
                    'api_secret': FACEPP_API_SECRET
                }

                try:
                    response = requests.post(
                        "https://api-us.faceplusplus.com/facepp/v3/compare",
                        files=files,
                        data=data_api,
                        timeout=15
                    )
                    
                    # Verificar se a resposta é JSON válido
                    if response.status_code != 200:
                        print(f"API Face++ retornou status {response.status_code}: {response.text}")
                        continue
                        
                    res_json = response.json()
                    
                    # Verificar erros da API Face++
                    if 'error_message' in res_json:
                        print(f"Erro Face++: {res_json['error_message']}")
                        continue
                        
                except Exception as e:
                    print(f"[ERROR] Erro API Face++: {e}")
                    continue

                faces1 = res_json.get('faces1', [])
                faces2 = res_json.get('faces2', [])
                confidence = res_json.get('confidence', 0) if faces1 and faces2 else 0

                print(f"Comparando com {username}: confidence = {confidence}")

                if confidence >= CONFIDENCE_THRESHOLD:
                    matched = username
                    confidence_matched = confidence
                    break
                    
    except psycopg2.Error as e:
        print(f"Erro no banco de dados: {e}")
        return jsonify({"erro": "Erro interno do servidor"}), 500
    finally:
        conn.close()

    # AGORA verificamos se matched foi encontrado
    if not matched:
        return jsonify({
            "erro": "Rosto não reconhecido!",
            "debug": "Verifique iluminação e posição do rosto."
        }), 400

    # Verificação adicional: o usuário do rosto bate com o informado?
    if usuario_input and matched.lower() != usuario_input.lower():
        return jsonify({
            "erro": f"Rosto reconhecido como {matched}, mas você informou {usuario_input}."
        }), 400

    # Registrar presença
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM usuarios WHERE usuario=%s", (matched,))
            user = cur.fetchone()
            if user:
                user_id = user['id']
                cur.execute(
                    "INSERT INTO presencas (usuario_id, status) VALUES (%s, %s)", 
                    (user_id, acao)
                )
                conn.commit()
    except psycopg2.Error as e:
        print(f"Erro ao registrar presença: {e}")
        return jsonify({"erro": "Erro ao registrar presença"}), 500
    finally:
        conn.close()

    return jsonify({
        "mensagem": f"{acao.capitalize()} registrada para {matched}.",
        "confidence": confidence_matched
    })

# ------------------------------
# Login, cadastro e páginas principais
# ------------------------------
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario_email = request.form.get('usuario', '').strip()
        senha = request.form.get('senha', '')

        if not usuario_email or not senha:
            flash('Preencha todos os campos', 'danger')
            return redirect(url_for('login'))

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM usuarios WHERE usuario=%s OR email=%s", 
                    (usuario_email, usuario_email)
                )
                user = cur.fetchone()
        except psycopg2.Error as e:
            print(f"Erro no banco de dados: {e}")
            flash('Erro interno do servidor', 'danger')
            return redirect(url_for('login'))
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

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        usuario = request.form.get('usuario', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        curso = request.form.get('curso','').strio()
        matricula= request.form.get('matricula','').strip();
        if not all([nome, usuario, email, senha,curso,matricula]):
            flash('Preencha todos os campos', 'danger')
            return redirect(url_for('cadastro'))
            
    return render_template('cadastro.html')

@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT nome, usuario, email, rosto,curso,matricula,data_cadastro FROM usuarios WHERE id = %s", (user_id,))
            user = cur.fetchone()
            
            cur.execute("""
                SELECT 
                  COUNT(*) FILTER (WHERE status IS NOT NULL) AS total_registros,
                  MAX(data_hora) AS ultima_presenca
                FROM presencas
                WHERE usuario_id = %s
            """, (user_id,))
            stats = cur.fetchone()
    finally:
        conn.close()

    if user and user['rosto']:
        user['rosto'] = base64.b64encode(bytes(user['rosto'])).decode('utf-8')

    ultima = stats['ultima_presenca']
    ultima_presenca = ultima.strftime('%d/%m/%Y %H:%M') if ultima else 'Nunca'

    return render_template(
        'index.html',
        user=user,
        total_faltas=stats['total_registros'] or 0,
        limite_faltas=20,
        data_atualizacao=ultima_presenca
    )

@app.route('/perfil')
def perfil():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT nome, usuario, email, curso, data_cadastro, rosto FROM usuarios WHERE id = %s", (user_id,))
            user = cur.fetchone()
    finally:
        conn.close()

    if user and user['rosto']:
        user['rosto'] = base64.b64encode(bytes(user['rosto'])).decode('utf-8')

    return render_template('perfil.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/captura_facial')
def captura_facial():
    return render_template('captura_facial.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


@app.route('/perfil')
def perfil():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT nome, usuario, email, curso, data_cadastro, rosto FROM usuarios WHERE id = %s", (user_id,))
            user = cur.fetchone()
    finally:
        conn.close()

    if user and user['rosto']:
        user['rosto'] = base64.b64encode(bytes(user['rosto'])).decode('utf-8')

    return render_template('perfil.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/captura_facial')
def captura_facial():
    return render_template('captura_facial.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
