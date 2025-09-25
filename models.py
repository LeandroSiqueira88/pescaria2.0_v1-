# E:\projeto\pescaria2.0\models.py

from database import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from datetime import datetime


class Perfil(db.Model):
    __tablename__ = 'perfil'
    id_perfil = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    
    usuarios = relationship("Usuario", back_populates="perfil")


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column('id_usuario', db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    id_perfil = db.Column(db.Integer, db.ForeignKey('perfil.id_perfil'))

    perfil = relationship("Perfil", back_populates="usuarios")
    pescarias = relationship("Pescaria", back_populates="usuario")

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
    
    pescarias = relationship("Pescaria", back_populates="peixe")


class Pescaria(db.Model):
    __tablename__ = 'pescarias'
    id_pescaria = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, nullable=False)
    local = db.Column(db.String(255), nullable=False)
    peso_peixe = db.Column(db.Float)
    comprimento_peixe = db.Column(db.Float)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    foto_pescaria = db.Column(db.String(255))
    
    compartilhada = db.Column(db.Boolean, default=False)
    
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_peixe = db.Column(db.Integer, db.ForeignKey('peixes.id_peixe'), nullable=False)

    usuario = relationship("Usuario", back_populates="pescarias")
    peixe = relationship("Peixe", back_populates="pescarias")

class Legislacao(db.Model):
    __tablename__ = 'legislacao'
    id_legislacao = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    link_externo = db.Column(db.String(512))

class Material(db.Model):
    __tablename__ = 'material'
    id_material = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    foto_url = db.Column(db.String(512))
    link_compra = db.Column(db.String(512)) # Novo campo para o link
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

class Evento(db.Model):
    __tablename__ = 'evento'
    id_evento = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, nullable=False)
    local = db.Column(db.String(255), nullable=False)
    foto_url = db.Column(db.String(512))
    link_inscricao = db.Column(db.String(512))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)