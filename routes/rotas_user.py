# E:\projeto\pescaria2.0\routes\rotas_user.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from database import db
from models import Peixe, Pescaria, Usuario, Legislacao, Material, Evento # Nova importação
from functools import wraps
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from sqlalchemy import func

rotas_user = Blueprint('user', __name__, template_folder='../templates/user')

def user_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.id_perfil != 2:
            flash('Acesso negado. Esta página é exclusiva para usuários.', 'danger')
            return redirect(url_for('admin.painel_admin'))
        return f(*args, **kwargs)
    return decorated_function

@rotas_user.route('/painel_usuario')
@user_required
def painel_usuario():
    # Buscando dados para o painel
    total_pescarias = Pescaria.query.filter_by(id_usuario=current_user.id).count()
    maior_peixe = Pescaria.query.filter_by(id_usuario=current_user.id).order_by(Pescaria.peso_peixe.desc()).first()
    
    return render_template('painel_usuario.html',
                           total_pescarias=total_pescarias,
                           maior_peixe=maior_peixe)

@rotas_user.route('/peixes')
def listar_peixes():
    query = request.args.get('q')
    
    if query:
        peixes = Peixe.query.filter(
            (Peixe.nome_comum.ilike(f'%{query}%')) | 
            (Peixe.nome_cientifico.ilike(f'%{query}%'))
        ).all()
    else:
        peixes = Peixe.query.all()
    
    return render_template('listar_peixes.html', peixes=peixes, query=query)

@rotas_user.route('/detalhes_peixe/<int:id_peixe>')
def detalhes_peixe(id_peixe):
    peixe = Peixe.query.get_or_404(id_peixe)
    return render_template('detalhes_peixe.html', peixe=peixe)

@rotas_user.route('/registrar_pescaria', methods=['GET', 'POST'])
@user_required
def registrar_pescaria():
    peixes_disponiveis = Peixe.query.all()
    if request.method == 'POST':
        local = request.form.get('local')
        data = request.form.get('data')
        id_peixe = request.form.get('peixe_id')
        
        # CORREÇÃO AQUI: TRATANDO VALORES VAZIOS
        peso = float(request.form.get('peso')) if request.form.get('peso') else None
        comprimento = float(request.form.get('comprimento')) if request.form.get('comprimento') else None
        
        latitude_str = request.form.get('latitude')
        longitude_str = request.form.get('longitude')
        
        latitude = float(latitude_str) if latitude_str else None
        longitude = float(longitude_str) if longitude_str else None

        foto_pescaria_path = None
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto.filename != '':
                filename = secure_filename(f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{foto.filename}")
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                foto.save(os.path.join(upload_folder, filename))
                foto_pescaria_path = os.path.join('uploads', filename)

        data_formatada = datetime.strptime(data, '%Y-%m-%dT%H:%M')

        nova_pescaria = Pescaria(
            local=local,
            data=data_formatada,
            id_peixe=id_peixe,
            peso_peixe=peso,
            comprimento_peixe=comprimento,
            latitude=latitude,
            longitude=longitude,
            foto_pescaria=foto_pescaria_path,
            id_usuario=current_user.id
        )

        db.session.add(nova_pescaria)
        db.session.commit()
        
        flash('Pescaria registrada com sucesso!', 'success')
        return redirect(url_for('user.painel_usuario'))

    return render_template('registrar_pescaria.html', peixes=peixes_disponiveis)
@rotas_user.route('/minhas_pescarias')
@user_required
def minhas_pescarias():
    pescarias = Pescaria.query.filter_by(id_usuario=current_user.id).order_by(Pescaria.data.desc()).all()
    return render_template('minhas_pescarias.html', pescarias=pescarias)

@rotas_user.route('/compartilhar_pescaria/<int:id_pescaria>', methods=['POST'])
@user_required
def compartilhar_pescaria(id_pescaria):
    pescaria = Pescaria.query.get_or_404(id_pescaria)

    if pescaria.id_usuario != current_user.id:
        flash('Acesso negado. Você não pode alterar a pescaria de outro usuário.', 'danger')
        return redirect(url_for('user.minhas_pescarias'))

    pescaria.compartilhada = not pescaria.compartilhada
    db.session.commit()

    if pescaria.compartilhada:
        flash('Pescaria compartilhada com a comunidade!', 'success')
    else:
        flash('Pescaria tornada privada.', 'info')
        
    return redirect(url_for('user.minhas_pescarias'))

@rotas_user.route('/editar_pescaria/<int:id_pescaria>', methods=['GET', 'POST'])
@user_required
def editar_pescaria(id_pescaria):
    pescaria = Pescaria.query.get_or_404(id_pescaria)

    if pescaria.id_usuario != current_user.id:
        flash('Acesso negado. Você não pode editar a pescaria de outro usuário.', 'danger')
        return redirect(url_for('user.minhas_pescarias'))

    if request.method == 'POST':
        pescaria.local = request.form.get('local')
        pescaria.data = datetime.strptime(request.form.get('data'), '%Y-%m-%dT%H:%M')
        pescaria.id_peixe = request.form.get('peixe_id')
        pescaria.peso_peixe = float(request.form.get('peso')) if request.form.get('peso') else None
        pescaria.comprimento_peixe = float(request.form.get('comprimento')) if request.form.get('comprimento') else None
        
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto.filename != '':
                if pescaria.foto_pescaria:
                    try:
                        os.remove(os.path.join(current_app.root_path, 'static', pescaria.foto_pescaria))
                    except FileNotFoundError:
                        pass
                
                filename = secure_filename(f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{foto.filename}")
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                foto.save(os.path.join(upload_folder, filename))
                pescaria.foto_pescaria = os.path.join('uploads', filename)

        db.session.commit()
        flash('Pescaria atualizada com sucesso!', 'success')
        return redirect(url_for('user.minhas_pescarias'))

    peixes_disponiveis = Peixe.query.all()
    return render_template('editar_pescaria.html', pescaria=pescaria, peixes=peixes_disponiveis)

@rotas_user.route('/excluir_pescaria/<int:id_pescaria>', methods=['POST'])
@user_required
def excluir_pescaria(id_pescaria):
    pescaria = Pescaria.query.get_or_404(id_pescaria)

    if pescaria.id_usuario != current_user.id:
        flash('Acesso negado. Você não pode excluir a pescaria de outro usuário.', 'danger')
        return redirect(url_for('user.minhas_pescarias'))

    if pescaria.foto_pescaria:
        try:
            os.remove(os.path.join(current_app.root_path, 'static', pescaria.foto_pescaria))
        except FileNotFoundError:
            pass
    
    db.session.delete(pescaria)
    db.session.commit()
    
    flash('Pescaria excluída com sucesso.', 'info')
    return redirect(url_for('user.minhas_pescarias'))

@rotas_user.route('/comunidade')
def comunidade():
    pescarias_comunitarias = Pescaria.query.filter_by(compartilhada=True).order_by(Pescaria.data.desc()).all()
    return render_template('comunidade.html', pescarias=pescarias_comunitarias)

@rotas_user.route('/editar_perfil', methods=['GET', 'POST'])
@user_required
def editar_perfil():
    usuario = Usuario.query.get_or_404(current_user.id)
    bcrypt = current_app.extensions.get('bcrypt')

    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        email_novo = request.form.get('email')
        senha_nova = request.form.get('senha')

        if email_novo != usuario.email and Usuario.query.filter_by(email=email_novo).first():
            flash('Este e-mail já está em uso. Por favor, escolha outro.', 'danger')
            return redirect(url_for('user.editar_perfil'))

        usuario.email = email_novo

        if senha_nova:
            if not bcrypt:
                flash('Erro de configuração de segurança. Tente novamente mais tarde.', 'danger')
                return redirect(url_for('user.editar_perfil'))
            usuario.senha = bcrypt.generate_password_hash(senha_nova).decode('utf-8')

        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('user.painel_usuario'))

    return render_template('editar_perfil.html', usuario=usuario)

@rotas_user.route('/legislacao')
def listar_legislacao():
    legislacoes = Legislacao.query.order_by(Legislacao.data_criacao.desc()).all()
    return render_template('legislacao.html', legislacoes=legislacoes)

@rotas_user.route('/legislacao/<int:id_legislacao>')
def detalhes_legislacao(id_legislacao):
    legislacao = Legislacao.query.get_or_404(id_legislacao)
    return render_template('detalhes_legislacao.html', legislacao=legislacao)

@rotas_user.route('/material')
def listar_material():
    materiais = Material.query.order_by(Material.nome).all()
    return render_template('material.html', materiais=materiais)

@rotas_user.route('/material/<int:id_material>')
def detalhes_material(id_material):
    material = Material.query.get_or_404(id_material)
    return render_template('detalhes_material.html', material=material)

@rotas_user.route('/eventos')
def listar_eventos():
    eventos = Evento.query.order_by(Evento.data.desc()).all()
    return render_template('eventos.html', eventos=eventos)

@rotas_user.route('/eventos/<int:id_evento>')
def detalhes_evento(id_evento):
    evento = Evento.query.get_or_404(id_evento)
    return render_template('detalhes_evento.html', evento=evento)