# E:\projeto\pescaria2.0\app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from config import Config
from database import db
from models import Usuario, Perfil
from routes.rotas_user import rotas_user
from routes.rotas_admin import rotas_admin

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    
    bcrypt = Bcrypt(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Adiciona a instância do bcrypt para que ela possa ser acessada nas rotas
    app.extensions['bcrypt'] = bcrypt

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Rotas de autenticação
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.id_perfil == 1:
                return redirect(url_for('admin.painel_admin'))
            else:
                return redirect(url_for('user.painel_usuario'))
        return render_template('index.html')

    @app.route('/cadastro', methods=['GET', 'POST'])
    def cadastro():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
            
        if request.method == 'POST':
            nome = request.form.get('nome')
            email = request.form.get('email')
            senha = request.form.get('senha')
            confirmar_senha = request.form.get('confirmar_senha')

            if senha != confirmar_senha:
                flash('As senhas não coincidem.', 'danger')
                return redirect(url_for('cadastro'))

            email_existente = Usuario.query.filter_by(email=email).first()
            if email_existente:
                flash('Este e-mail já está cadastrado.', 'danger')
                return redirect(url_for('cadastro'))

            hashed_senha = bcrypt.generate_password_hash(senha).decode('utf-8')
            perfil_user = Perfil.query.filter_by(nome='user').first()
            if not perfil_user:
                flash('Erro de configuração: perfil de usuário não encontrado.', 'danger')
                return redirect(url_for('cadastro'))

            novo_usuario = Usuario(nome=nome, email=email, senha=hashed_senha, id_perfil=perfil_user.id_perfil)
            db.session.add(novo_usuario)
            db.session.commit()

            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
        
        return render_template('cadastro.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
            
        if request.method == 'POST':
            email = request.form.get('email')
            senha = request.form.get('senha')

            usuario = Usuario.query.filter_by(email=email).first()
            
            if usuario and bcrypt.check_password_hash(usuario.senha, senha):
                login_user(usuario)
                if usuario.id_perfil == 1:
                    return redirect(url_for('admin.painel_admin'))
                else:
                    return redirect(url_for('user.painel_usuario'))
            else:
                flash('E-mail ou senha inválidos.', 'danger')
        
        return render_template('login.html')

    @app.route('/sair')
    @login_required
    def sair():
        logout_user()
        flash('Você saiu da sua conta.', 'info')
        return redirect(url_for('index'))

    @app.route('/recuperar_usuario', methods=['GET', 'POST'])
    def recuperar_usuario():
        if request.method == 'POST':
            email = request.form.get('email')
            flash(f'Se o e-mail {email} estiver cadastrado, as instruções foram enviadas para ele.', 'info')
            return redirect(url_for('login'))
        return render_template('recuperar_usuario.html')

    # Registra os Blueprints (rotas)
    app.register_blueprint(rotas_user, url_prefix='/usuario')
    app.register_blueprint(rotas_admin, url_prefix='/admin')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        # Garante que os perfis 'admin' e 'user' existam
        if not Perfil.query.filter_by(nome='admin').first():
            db.session.add(Perfil(nome='admin'))
        if not Perfil.query.filter_by(nome='user').first():
            db.session.add(Perfil(nome='user'))
        db.session.commit()

        # Cria um usuário administrador padrão se ele não existir
        admin_email = 'admin@admin.com'
        if not Usuario.query.filter_by(email=admin_email).first():
            bcrypt = app.extensions['bcrypt']
            hashed_senha = bcrypt.generate_password_hash('123456').decode('utf-8')
            perfil_admin = Perfil.query.filter_by(nome='admin').first()
            novo_admin = Usuario(nome='Administrador', email=admin_email, senha=hashed_senha, id_perfil=perfil_admin.id_perfil)
            db.session.add(novo_admin)
            db.session.commit()
            print(f'Usuário administrador padrão criado: {admin_email}')

    app.run(debug=True)