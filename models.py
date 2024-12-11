from datetime import datetime
from main import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    view_all_processes = db.Column(db.Boolean, default=False)
    can_view_all_processes = db.Column(db.Boolean, default=False)  # Permissão para ver todos os processos
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
    numero_publicacao = db.Column(db.String(10))
    data_publicacao = db.Column(db.Date)
    data_sessao = db.Column(db.Date)
    publicado = db.Column(db.Boolean, default=False)
    link_publicacao = db.Column(db.String(500))  # URL da publicação oficial

class ProcessoHistorico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    processo_id = db.Column(db.Integer, db.ForeignKey('processo.id'))
    status_anterior = db.Column(db.String(50))
    status_novo = db.Column(db.String(50))
    observacao = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    data_registro = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    prazo_inicio = db.Column(db.DateTime)
    prazo_fim = db.Column(db.DateTime)
    dias_prazo = db.Column(db.Integer)
    tipo_prazo = db.Column(db.String(20))  # 'util' ou 'corrido'
    
    @property
    def prazo_status(self):
        if not self.prazo_fim:
            return None
        # Considera vencido apenas após o dia do vencimento
        data_fim = self.prazo_fim.replace(hour=23, minute=59, second=59)
        return 'no_prazo' if datetime.utcnow() <= data_fim else 'vencido'

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

class Contrato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True)
    objeto = db.Column(db.Text)
    processo_id = db.Column(db.Integer, db.ForeignKey('processo.id'), nullable=False)
    fornecedor = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Numeric(15, 2), nullable=True)  # Valor pode ser nulo para contratos sem valor definido
    data_assinatura = db.Column(db.Date)
    data_vigencia = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False, default='vigente')
    responsavel_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    processo = db.relationship('Processo', backref='contratos')
    responsavel = db.relationship('User', backref='contratos_responsavel')
