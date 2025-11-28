from flask import Flask, render_template, request, redirect, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = 'chave_secreta_123'

# Configuração do Firebase
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase-config.json")
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    print("Firebase conectado com sucesso!")
    
except Exception as e:
    print(f"Erro Firebase: {e}")
    db = None

# Página inicial
@app.route('/')
def index():
    if 'user_email' in session:
        return render_template('principal.html')
    return redirect('/login')

# Página de login - GET e POST
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if not email or not senha:
            return render_template('login.html', erro='Email e senha são obrigatórios')
        
        # Verifica no Firebase
        if db:
            users_ref = db.collection('users')
            query = users_ref.where('email', '==', email).limit(1)
            results = query.get()
            
            if len(results) > 0:
                user_data = results[0].to_dict()
                if user_data['senha'] == senha:
                    session['user_email'] = email
                    session['user_name'] = user_data['nome']
                    session['user_id'] = results[0].id
                    return redirect('/')
        
        return render_template('login.html', erro='Email ou senha incorretos')
    
    # Se for GET, mostra o formulário
    return render_template('login.html')

# Página de cadastro - GET e POST
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirma_senha = request.form.get('confirma_senha')
        
        # Validações
        if not all([nome, email, senha, confirma_senha]):
            return render_template('cadastro.html', erro='Todos os campos são obrigatórios')
        
        if senha != confirma_senha:
            return render_template('cadastro.html', erro='As senhas não coincidem')
        
        if len(senha) < 6:
            return render_template('cadastro.html', erro='A senha deve ter pelo menos 6 caracteres')
        
        # Salva no Firebase
        if db:
            users_ref = db.collection('users')
            query = users_ref.where('email', '==', email).limit(1)
            results = query.get()
            
            if len(results) > 0:
                return render_template('cadastro.html', erro='Este email já está cadastrado')
            
            user_data = {
                'nome': nome,
                'email': email,
                'senha': senha
            }
            
            users_ref.add(user_data)
            
            session['user_email'] = email
            session['user_name'] = nome
            
            return redirect('/')
    
    # Se for GET, mostra o formulário
    return render_template('cadastro.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)