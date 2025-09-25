# E:\projeto\pescaria2.0\routes\rotas_user.py

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from models import Peixe
from functools import wraps

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
    return render_template('painel_usuario.html')

@rotas_user.route('/peixes')
def listar_peixes():
    query = request.args.get('q') # Pega o termo de busca da URL
    
    if query:
        # Filtra os peixes pelo nome comum ou nome científico
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