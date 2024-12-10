from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])

class UserForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[])
    is_admin = BooleanField('Administrador')

class AlterarSenhaForm(FlaskForm):
    senha_atual = PasswordField('Senha Atual', validators=[DataRequired()])
    nova_senha = PasswordField('Nova Senha', validators=[DataRequired()])
    confirmar_senha = PasswordField('Confirmar Nova Senha', validators=[DataRequired(), EqualTo('nova_senha')])

class ProcessoForm(FlaskForm):
    objeto = TextAreaField('Objeto', validators=[DataRequired()])
    modalidade = SelectField('Modalidade', choices=[
        ('adesao', 'Adesão'),
        ('chamamento_publico', 'Chamamento Público'),
        ('concorrencia_eletronica', 'Concorrência Eletrônica'),
        ('concorrencia_presencial', 'Concorrência Presencial'),
        ('credenciamento', 'Credenciamento'),
        ('dispensa', 'Dispensa'),
        ('dispensa_eletronica', 'Dispensa Eletrônica'),
        ('inexigibilidade', 'Inexigibilidade'),
        ('leilao_eletronico', 'Leilão Eletrônico'),
        ('leilao_presencial', 'Leilão Presencial'),
        ('pregao_eletronico', 'Pregão Eletrônico'),
        ('pregao_presencial', 'Pregão Presencial')
    ], validators=[DataRequired()])
    valor_estimado = StringField('Valor Estimado')
    data_recebimento = StringField('Data de Recebimento')
    responsavel_id = SelectField('Responsável', coerce=int, validators=[DataRequired()])
    observacao = TextAreaField('Observação')

class TramitacaoForm(FlaskForm):
    status = SelectField('Fase', validators=[DataRequired()])
    observacao = TextAreaField('Observação', validators=[DataRequired()])
    data_registro = StringField('Data do Registro', validators=[])
    habilitar_prazo = BooleanField('Habilitar Prazo', default=False)
    dias_prazo = IntegerField('Dias de Prazo', validators=[], default=None)
    tipo_prazo = SelectField('Tipo de Prazo', 
        choices=[('util', 'Dias Úteis'), ('corrido', 'Dias Corridos')],
        default='util',
        validators=[])
    
    def validate(self):
        if not super().validate():
            return False
        
        if self.habilitar_prazo.data:
            if not self.dias_prazo.data:
                self.dias_prazo.errors.append('Informe o número de dias quando habilitar o prazo')
                return False
            if self.dias_prazo.data <= 0:
                self.dias_prazo.errors.append('O número de dias deve ser maior que zero')
                return False
        return True

class ProcessoFaseForm(FlaskForm):
    codigo = StringField('Código', validators=[DataRequired(), Length(max=50)])
    descricao = StringField('Descrição', validators=[DataRequired(), Length(max=100)])
    ordem = IntegerField('Ordem', validators=[DataRequired()])
    cor = SelectField('Cor do Badge', choices=[
        ('primary', 'Azul'),
        ('secondary', 'Cinza'),
        ('success', 'Verde'),
        ('danger', 'Vermelho'),
        ('warning', 'Amarelo'),
        ('info', 'Azul Claro')
    ], validators=[DataRequired()])
    ativo = BooleanField('Ativo')
