# E:\projeto\pescaria2.0\routes\rotas_admin.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from database import db
from models import Usuario, Perfil, Peixe, Pescaria, Legislacao, Material, Evento
from functools import wraps
from datetime import datetime
from flask_bcrypt import Bcrypt
from sqlalchemy import func
import os

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
    # Buscando dados para o painel
    total_usuarios = Usuario.query.count()
    total_peixes_cadastrados = Peixe.query.count()
    total_pescarias = Pescaria.query.count()
    pescarias_compartilhadas = Pescaria.query.filter_by(compartilhada=True).count()
    
    return render_template('painel_admin.html',
                           total_usuarios=total_usuarios,
                           total_peixes_cadastrados=total_peixes_cadastrados,
                           total_pescarias=total_pescarias,
                           pescarias_compartilhadas=pescarias_compartilhadas)

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

        bcrypt = current_app.extensions.get('bcrypt')
        if not bcrypt:
            flash('Erro de configuração de segurança.', 'danger')
            return redirect(url_for('admin.criar_usuario'))

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
    bcrypt = current_app.extensions.get('bcrypt')

    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        email_novo = request.form.get('email')
        senha_nova = request.form.get('senha')
        perfil_novo = request.form.get('id_perfil')

        if email_novo != usuario.email and Usuario.query.filter_by(email=email_novo).first():
            flash('Este e-mail já está em uso. Por favor, escolha outro.', 'danger')
            return redirect(url_for('admin.editar_usuario', id_usuario=id_usuario))

        usuario.email = email_novo
        usuario.id_perfil = perfil_novo

        if senha_nova:
            if not bcrypt:
                flash('Erro de configuração de segurança. Tente novamente mais tarde.', 'danger')
                return redirect(url_for('admin.editar_usuario', id_usuario=id_usuario))
            usuario.senha = bcrypt.generate_password_hash(senha_nova).decode('utf-8')

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
    # ... (código da sua função criar_peixe) ...
    # Substitua esta parte com a lógica correta da sua função
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
    return redirect(url_for('admin.gerenciar_peixes'))

@rotas_admin.route('/gerenciar_legislacao')
@admin_required
def gerenciar_legislacao():
    legislacoes = Legislacao.query.all()
    return render_template('gerenciar_legislacao.html', legislacoes=legislacoes)

@rotas_admin.route('/criar_legislacao', methods=['GET', 'POST'])
@admin_required
def criar_legislacao():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        conteudo = request.form.get('conteudo')
        link_externo = request.form.get('link_externo')
        
        nova_legislacao = Legislacao(titulo=titulo, conteudo=conteudo, link_externo=link_externo)
        db.session.add(nova_legislacao)
        db.session.commit()

        flash('Legislação criada com sucesso!', 'success')
        return redirect(url_for('admin.gerenciar_legislacao'))
    
    return render_template('criar_legislacao.html')

@rotas_admin.route('/editar_legislacao/<int:id_legislacao>', methods=['GET', 'POST'])
@admin_required
def editar_legislacao(id_legislacao):
    legislacao = Legislacao.query.get_or_404(id_legislacao)
    
    if request.method == 'POST':
        legislacao.titulo = request.form.get('titulo')
        legislacao.conteudo = request.form.get('conteudo')
        legislacao.link_externo = request.form.get('link_externo')

        db.session.commit()
        flash('Legislação atualizada com sucesso!', 'success')
        return redirect(url_for('admin.gerenciar_legislacao'))
    
    return render_template('editar_legislacao.html', legislacao=legislacao)

@rotas_admin.route('/excluir_legislacao/<int:id_legislacao>', methods=['POST'])
@admin_required
def excluir_legislacao(id_legislacao):
    legislacao = Legislacao.query.get_or_404(id_legislacao)
    
    db.session.delete(legislacao)
    db.session.commit()
    flash('Legislação excluída com sucesso!', 'success')
    return redirect(url_for('admin.gerenciar_legislacao'))

@rotas_admin.route('/gerenciar_comunidade')
@admin_required
def gerenciar_comunidade():
    # Busca todas as pescarias que foram compartilhadas
    pescarias_compartilhadas = Pescaria.query.filter_by(compartilhada=True).order_by(Pescaria.data.desc()).all()
    return render_template('gerenciar_comunidade.html', pescarias=pescarias_compartilhadas)

@rotas_admin.route('/excluir_pescaria_comunidade/<int:id_pescaria>', methods=['POST'])
@admin_required
def excluir_pescaria_comunidade(id_pescaria):
    pescaria = Pescaria.query.get_or_404(id_pescaria)
    
    # Exclui a foto do servidor antes de remover o registro do banco
    if pescaria.foto_pescaria:
        try:
            os.remove(os.path.join(current_app.root_path, 'static', pescaria.foto_pescaria))
        except FileNotFoundError:
            pass
            
    db.session.delete(pescaria)
    db.session.commit()
    flash('Pescaria da comunidade excluída com sucesso!', 'success')
    return redirect(url_for('admin.gerenciar_comunidade'))

@rotas_admin.route('/gerenciar_material')
@admin_required
def gerenciar_material():
    materiais = Material.query.all()
    return render_template('gerenciar_material.html', materiais=materiais)

@rotas_admin.route('/criar_material', methods=['GET', 'POST'])
@admin_required
def criar_material():
    tipos_material = ['Vara', 'Molinete', 'Carretilha', 'Isca Artificial', 'Isca Natural', 'Linha', 'Anzol', 'Outros']
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        tipo = request.form.get('tipo')
        foto_url = request.form.get('foto_url')
        link_compra = request.form.get('link_compra')
        
        novo_material = Material(nome=nome, descricao=descricao, tipo=tipo, foto_url=foto_url, link_compra=link_compra)
        db.session.add(novo_material)
        db.session.commit()

        flash('Material cadastrado com sucesso!', 'success')
        return redirect(url_for('admin.gerenciar_material'))
    
    return render_template('criar_material.html', tipos=tipos_material)

@rotas_admin.route('/editar_material/<int:id_material>', methods=['GET', 'POST'])
@admin_required
def editar_material(id_material):
    material = Material.query.get_or_404(id_material)
    tipos_material = ['Vara', 'Molinete', 'Carretilha', 'Isca Artificial', 'Isca Natural', 'Linha', 'Anzol', 'Outros']

    if request.method == 'POST':
        material.nome = request.form.get('nome')
        material.descricao = request.form.get('descricao')
        material.tipo = request.form.get('tipo')
        material.foto_url = request.form.get('foto_url')
        material.link_compra = request.form.get('link_compra')

        db.session.commit()
        flash('Material atualizado com sucesso!', 'success')
        return redirect(url_for('admin.gerenciar_material'))
    
    return render_template('editar_material.html', material=material, tipos=tipos_material)

@rotas_admin.route('/excluir_material/<int:id_material>', methods=['POST'])
@admin_required
def excluir_material(id_material):
    material = Material.query.get_or_404(id_material)
    
    db.session.delete(material)
    db.session.commit()
    flash('Material excluído com sucesso!', 'success')
    return redirect(url_for('admin.gerenciar_material'))

@rotas_admin.route('/gerenciar_eventos')
@admin_required
def gerenciar_eventos():
    eventos = Evento.query.order_by(Evento.data.desc()).all()
    return render_template('gerenciar_eventos.html', eventos=eventos)

@rotas_admin.route('/criar_evento', methods=['GET', 'POST'])
@admin_required
def criar_evento():
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        data_str = request.form.get('data')
        local = request.form.get('local')
        foto_url = request.form.get('foto_url')
        link_inscricao = request.form.get('link_inscricao')

        try:
            data_evento = datetime.strptime(data_str, '%Y-%m-%dT%H:%M')
        except (ValueError, TypeError):
            flash('Formato de data e hora inválido.', 'danger')
            return render_template('criar_evento.html')
        
        novo_evento = Evento(nome=nome, descricao=descricao, data=data_evento, local=local, foto_url=foto_url, link_inscricao=link_inscricao)
        db.session.add(novo_evento)
        db.session.commit()

        flash('Evento cadastrado com sucesso!', 'success')
        return redirect(url_for('admin.gerenciar_eventos'))
    
    return render_template('criar_evento.html')

@rotas_admin.route('/editar_evento/<int:id_evento>', methods=['GET', 'POST'])
@admin_required
def editar_evento(id_evento):
    evento = Evento.query.get_or_404(id_evento)
    
    if request.method == 'POST':
        evento.nome = request.form.get('nome')
        evento.descricao = request.form.get('descricao')
        data_str = request.form.get('data')
        evento.local = request.form.get('local')
        evento.foto_url = request.form.get('foto_url')
        evento.link_inscricao = request.form.get('link_inscricao')
        
        try:
            evento.data = datetime.strptime(data_str, '%Y-%m-%dT%H:%M')
        except (ValueError, TypeError):
            flash('Formato de data e hora inválido.', 'danger')
            return render_template('editar_evento.html', evento=evento)

        db.session.commit()
        flash('Evento atualizado com sucesso!', 'success')
        return redirect(url_for('admin.gerenciar_eventos'))
    
    return render_template('editar_evento.html', evento=evento)

@rotas_admin.route('/excluir_evento/<int:id_evento>', methods=['POST'])
@admin_required
def excluir_evento(id_evento):
    evento = Evento.query.get_or_404(id_evento)
    
    db.session.delete(evento)
    db.session.commit()
    flash('Evento excluído com sucesso!', 'success')
    return redirect(url_for('admin.gerenciar_eventos'))