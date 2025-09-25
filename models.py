# E:\projeto\pescaria2.0\models.py

from database import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship

class Perfil(db.Model):
    __tablename__ = 'perfil'
    id_perfil = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    
    usuarios = relationship("Usuario", backref="perfil_rel", lazy=True)


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column('id_usuario', db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    id_perfil = db.Column(db.Integer, db.ForeignKey('perfil.id_perfil'))

    perfil = relationship("Perfil", backref="usuarios_rel", lazy=True)

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

class Peixe(db.Model):
    __tablename__ = 'peixes'
    id_peixe = db.Column(db.Integer, primary_key=True)
    nome_comum = db.Column(db.String(100), nullable=False)
    nome_cientifico = db.Column(db.String(100))
    foto_url = db.Column(db.String(255))
    habitat = db.Column(db.String(255))
    periodo_atividade = db.Column(db.String(100))
    tamanho_medio = db.Column(db.String(50))
    equipamento_sugerido = db.Column(db.Text)
    dicas = db.Column(db.Text)