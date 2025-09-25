# E:\projeto\pescaria2.0\routes\rotas_admin.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from database import db
from models import Usuario, Perfil, Peixe
from functools import wraps

rotas_admin = Blueprint('admin', __name__, template_folder='../templates/admin')

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.id_perfil != 1:
            flash('Acesso negado. Você não tem permissão de administrador.', 'danger')
            return redirect(url_for('user.painel_usuario'))
        return f(*args, **kwargs)
    return decorated_function

@rotas_admin.route('/painel_admin')
@admin_required
def painel_admin():
    return render_template('painel_admin.html')

@rotas_admin.route('/criar_usuario', methods=['GET', 'POST'])
@admin_required
def criar_usuario():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        id_perfil = request.form.get('id_perfil')

        email_existente = Usuario.query.filter_by(email=email).first()
        if email_existente:
            flash('Este e-mail já está cadastrado no sistema.', 'danger')
            return redirect(url_for('admin.criar_usuario'))

        bcrypt = current_app.extensions['bcrypt']
        hashed_senha = bcrypt.generate_password_hash(senha).decode('utf-8')

        novo_usuario = Usuario(nome=nome, email=email, senha=hashed_senha, id_perfil=id_perfil)
        db.session.add(novo_usuario)
        db.session.commit()

        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('admin.painel_admin'))

    perfis = Perfil.query.all()
    return render_template('criar_usuario.html', perfis=perfis)

@rotas_admin.route('/gerenciar_usuarios')
@admin_required
def gerenciar_usuarios():
    usuarios = Usuario.query.join(Perfil).order_by(Usuario.id).all()
    return render_template('gerenciar_usuarios.html', usuarios=usuarios)

@rotas_admin.route('/editar_usuario/<int:id_usuario>', methods=['GET', 'POST'])
@admin_required
def editar_usuario(id_usuario):
    usuario = Usuario.query.get_or_404(id_usuario)
    perfis = Perfil.query.all()

    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.email = request.form.get('email')
        usuario.id_perfil = request.form.get('id_perfil')
        nova_senha = request.form.get('senha')

        if nova_senha:
            bcrypt = current_app.extensions['bcrypt']
            usuario.senha = bcrypt.generate_password_hash(nova_senha).decode('utf-8')

        db.session.commit()
        flash('Informações do usuário atualizadas com sucesso!', 'success')
        return redirect(url_for('admin.gerenciar_usuarios'))

    return render_template('editar_usuario.html', usuario=usuario, perfis=perfis)

@rotas_admin.route('/excluir_usuario/<int:id_usuario>', methods=['POST'])
@admin_required
def excluir_usuario(id_usuario):
    usuario = Usuario.query.get_or_404(id_usuario)
    if usuario.id == current_user.id:
        flash('Você não pode deletar sua própria conta.', 'danger')
        return redirect(url_for('admin.gerenciar_usuarios'))

    db.session.delete(usuario)
    db.session.commit()
    flash(f'Usuário "{usuario.nome}" deletado com sucesso.', 'success')
    return redirect(url_for('admin.gerenciar_usuarios'))

@rotas_admin.route('/criar_peixe', methods=['GET', 'POST'])
@admin_required
def criar_peixe():
    if request.method == 'POST':
        nome_comum = request.form.get('nome_comum')
        nome_cientifico = request.form.get('nome_cientifico')
        foto_url = request.form.get('foto_url')
        habitat = request.form.get('habitat')
        periodo_atividade = request.form.get('periodo_atividade')
        tamanho_medio = request.form.get('tamanho_medio')
        equipamento_sugerido = request.form.get('equipamento_sugerido')
        dicas = request.form.get('dicas')

        novo_peixe = Peixe(
            nome_comum=nome_comum,
            nome_cientifico=nome_cientifico,
            foto_url=foto_url,
            habitat=habitat,
            periodo_atividade=periodo_atividade,
            tamanho_medio=tamanho_medio,
            equipamento_sugerido=equipamento_sugerido,
            dicas=dicas
        )

        db.session.add(novo_peixe)
        db.session.commit()
        
        flash('Peixe cadastrado com sucesso!', 'success')
        return redirect(url_for('admin.painel_admin'))

    return render_template('criar_peixe.html')

@rotas_admin.route('/gerenciar_peixes')
@admin_required
def gerenciar_peixes():
    peixes = Peixe.query.all()
    return render_template('gerenciar_peixes.html', peixes=peixes)

@rotas_admin.route('/detalhes_peixe/<int:id_peixe>')
@admin_required
def detalhes_peixe(id_peixe):
    peixe = Peixe.query.get_or_404(id_peixe)
    return render_template('detalhes_peixe.html', peixe=peixe)

@rotas_admin.route('/editar_peixe/<int:id_peixe>', methods=['GET', 'POST'])
@admin_required
def editar_peixe(id_peixe):
    peixe = Peixe.query.get_or_404(id_peixe)
    
    if request.method == 'POST':
        peixe.nome_comum = request.form.get('nome_comum')
        peixe.nome_cientifico = request.form.get('nome_cientifico')
        peixe.foto_url = request.form.get('foto_url')
        peixe.habitat = request.form.get('habitat')
        peixe.periodo_atividade = request.form.get('periodo_atividade')
        peixe.tamanho_medio = request.form.get('tamanho_medio')
        peixe.equipamento_sugerido = request.form.get('equipamento_sugerido')
        peixe.dicas = request.form.get('dicas')

        db.session.commit()
        flash('Informações do peixe atualizadas com sucesso!', 'success')
        return redirect(url_for('admin.gerenciar_peixes'))

    return render_template('editar_peixe.html', peixe=peixe)

@rotas_admin.route('/excluir_peixe/<int:id_peixe>', methods=['POST'])
@admin_required
def excluir_peixe(id_peixe):
    peixe = Peixe.query.get_or_404(id_peixe)
    db.session.delete(peixe)
    db.session.commit()
    flash('Peixe excluído com sucesso!', 'success')
    return