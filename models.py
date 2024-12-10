from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    processos = db.relationship('Processo', backref='responsavel', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def notificacoes_nao_lidas(self):
        return NotificacaoProcesso.query.filter_by(
            destinatario_id=self.id,
            lida=False
        ).count()

class Processo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_processo = db.Column(db.String(50), unique=True, nullable=False)
    objeto = db.Column(db.Text, nullable=False)
    modalidade = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='novo')
    valor_estimado = db.Column(db.Numeric(15, 2))
    data_recebimento = db.Column(db.Date, nullable=False)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    historico = db.relationship('ProcessoHistorico', backref='processo', lazy=True, order_by='ProcessoHistorico.created_at.desc()')

class ProcessoHistorico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    processo_id = db.Column(db.Integer, db.ForeignKey('processo.id'))
    status_anterior = db.Column(db.String(50))
    status_novo = db.Column(db.String(50))
    observacao = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProcessoFase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    descricao = db.Column(db.String(100), nullable=False)
    ordem = db.Column(db.Integer, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    cor = db.Column(db.String(20), default='primary')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NotificacaoProcesso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    processo_id = db.Column(db.Integer, db.ForeignKey('processo.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # 'mudanca_status', 'novo_processo', etc
    mensagem = db.Column(db.Text, nullable=False)
    lida = db.Column(db.Boolean, default=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    remetente_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    processo = db.relationship('Processo', backref='notificacoes')
    destinatario = db.relationship('User', foreign_keys=[destinatario_id], backref='notificacoes_recebidas')
    remetente = db.relationship('User', foreign_keys=[remetente_id], backref='notificacoes_enviadas')
