from flask import render_template, redirect, url_for, flash, request
from datetime import datetime, timedelta
from flask_login import login_user, logout_user, login_required, current_user
from main import app, db, login_manager
from models import User, Processo, ProcessoHistorico, ProcessoFase, NotificacaoProcesso
from forms import LoginForm, UserForm, ProcessoForm, TramitacaoForm, AlterarSenhaForm, ProcessoFaseForm

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Usuário ou senha inválidos')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.')
    return redirect(url_for('login'))

@app.route('/perfil/alterar-senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    form = AlterarSenhaForm()
    if form.validate_on_submit():
        if current_user.check_password(form.senha_atual.data):
            current_user.set_password(form.nova_senha.data)
            db.session.commit()
            flash('Sua senha foi alterada com sucesso!')
            return redirect(url_for('index'))
        else:
            flash('Senha atual incorreta')
    return render_template('alterar_senha.html', form=form)

@app.route('/usuarios')
@login_required
def listar_usuarios():
    if not current_user.is_admin:
        flash('Acesso não autorizado')
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('user_list.html', users=users)

@app.route('/usuarios/novo', methods=['GET', 'POST'])
@login_required
def criar_usuario():
    if not current_user.is_admin:
        flash('Acesso não autorizado')
        return redirect(url_for('index'))
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Usuário criado com sucesso!')
            return redirect(url_for('listar_usuarios'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar usuário. Este usuário ou email já existe.')
    return render_template('user_form.html', form=form)

@app.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    if not current_user.is_admin:
        flash('Acesso não autorizado')
        return redirect(url_for('index'))
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        try:
            db.session.commit()
            flash('Usuário atualizado com sucesso!')
            return redirect(url_for('listar_usuarios'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar usuário. Este usuário ou email já existe.')
    return render_template('user_form.html', form=form, user=user)

@app.route('/usuarios/<int:id>/senha', methods=['GET', 'POST'])
@login_required
def redefinir_senha_usuario(id):
    if not current_user.is_admin:
        flash('Acesso não autorizado')
        return redirect(url_for('index'))
    user = User.query.get_or_404(id)
    form = AlterarSenhaForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Senha redefinida com sucesso!')
        return redirect(url_for('listar_usuarios'))
    return render_template('user_form.html', form=form, user=user, password_reset=True)

@app.route('/usuarios/<int:id>/toggle_status')
@login_required
def toggle_status_usuario(id):
    if not current_user.is_admin:
        flash('Acesso não autorizado')
        return redirect(url_for('index'))
    user = User.query.get_or_404(id)
    if user == current_user:
        flash('Não é possível alterar o próprio status')
        return redirect(url_for('listar_usuarios'))
    user.is_active = not user.is_active
    db.session.commit()
    flash(f'Status do usuário alterado para {"ativo" if user.is_active else "inativo"}!')
    return redirect(url_for('listar_usuarios'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        processos = Processo.query.all()
    else:
        processos = Processo.query.filter_by(responsavel_id=current_user.id).all()
    
    # Métricas
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    total_processos = len(processos)
    processos_por_status = {}
    processos_por_modalidade = {}
    valor_total = 0
    
    for processo in processos:
        # Contagem por status
        status = processo.status
        fase = ProcessoFase.query.filter_by(codigo=status).first()
        status_desc = fase.descricao if fase else status
        processos_por_status[status_desc] = processos_por_status.get(status_desc, 0) + 1
        
        # Contagem por modalidade
        modalidade = processo.modalidade
        processos_por_modalidade[modalidade] = processos_por_modalidade.get(modalidade, 0) + 1
        
        # Soma dos valores
        if processo.valor_estimado:
            valor_total += float(processo.valor_estimado)
    
    logging.debug(f"Status: {processos_por_status}")
    logging.debug(f"Modalidades: {processos_por_modalidade}")
    
    return render_template('dashboard.html',
                         processos=processos,
                         ProcessoFase=ProcessoFase,
                         total_processos=total_processos,
                         processos_por_status=processos_por_status,
                         processos_por_modalidade=processos_por_modalidade,
                         valor_total=valor_total)

@app.route('/lista_processos')
@login_required
def lista_processos():
    page = request.args.get('page', 1, type=int)
    query = Processo.query
    
    # Filtros
    if numero_processo := request.args.get('numero_processo'):
        query = query.filter(Processo.numero_processo.ilike(f'%{numero_processo}%'))
    if modalidade := request.args.get('modalidade'):
        query = query.filter(Processo.modalidade == modalidade)
    if status := request.args.get('status'):
        query = query.filter(Processo.status == status)
    if data_inicio := request.args.get('data_inicio'):
        query = query.filter(Processo.data_abertura >= datetime.strptime(data_inicio, '%Y-%m-%d'))
    if data_fim := request.args.get('data_fim'):
        query = query.filter(Processo.data_abertura <= datetime.strptime(data_fim, '%Y-%m-%d'))
    
    # Ordenação
    sort = request.args.get('sort', 'data_abertura')
    direction = request.args.get('direction', 'desc')
    
    if direction == 'desc':
        query = query.order_by(getattr(Processo, sort).desc())
    else:
        query = query.order_by(getattr(Processo, sort).asc())
    
    processos = query.paginate(page=page, per_page=10)
    return render_template('processo_list.html', processos=processos)

@app.route('/processo/<int:id>')
@login_required
def visualizar_processo(id):
    from models import User
    processo = Processo.query.get_or_404(id)
    return render_template('processo_view.html', processo=processo, User=User, ProcessoFase=ProcessoFase)

@app.route('/processo/novo', methods=['GET', 'POST'])
@login_required
def novo_processo():
    if not current_user.is_admin:
        flash('Acesso não autorizado')
        return redirect(url_for('index'))
    form = ProcessoForm()
    usuarios_ativos = User.query.filter_by(is_active=True).all()
    form.responsavel_id.choices = [(u.id, u.username) for u in usuarios_ativos]
    
    if form.validate_on_submit():
        valor_estimado = None
        if form.valor_estimado.data and form.valor_estimado.data.strip():
            try:
                valor_str = ''.join(c for c in form.valor_estimado.data if c.isdigit() or c in '.,')
                valor_str = valor_str.replace(',', '.')
                valor_estimado = float(valor_str)
            except ValueError:
                flash('Valor estimado inválido. Use apenas números e vírgula.')
                return render_template('processo_form.html', form=form)

        processo = Processo(
            numero_processo=f"PROC{datetime.now().year}{str(Processo.query.filter(Processo.created_at.between(datetime(datetime.now().year, 1, 1), datetime(datetime.now().year + 1, 1, 1))).count() + 1).zfill(4)}",
            objeto=form.objeto.data,
            modalidade=form.modalidade.data,
            valor_estimado=valor_estimado,
            status='novo',
            data_recebimento=form.data_recebimento.data,
            responsavel_id=form.responsavel_id.data
        )
        db.session.add(processo)
        db.session.commit()
        
        historico = ProcessoHistorico(
            processo_id=processo.id,
            status_novo='novo',
            observacao=form.observacao.data or "Processo cadastrado",
            usuario_id=current_user.id
        )
        db.session.add(historico)
        db.session.commit()
        
        flash('Processo cadastrado com sucesso!')
        return redirect(url_for('dashboard'))
    return render_template('processo_form.html', form=form)

@app.route('/processo/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_processo(id):
    if not current_user.is_admin:
        flash('Acesso não autorizado')
        return redirect(url_for('index'))
    processo = Processo.query.get_or_404(id)
    form = ProcessoForm(obj=processo)
    
    usuarios_ativos = User.query.filter_by(is_active=True).all()
    form.responsavel_id.choices = [(u.id, u.username) for u in usuarios_ativos]
    
    if form.validate_on_submit():
        status_anterior = processo.status
        responsavel_anterior = processo.responsavel_id
        form.populate_obj(processo)
        
        if status_anterior != processo.status:
            historico = ProcessoHistorico(
                processo_id=processo.id,
                status_anterior=status_anterior,
                status_novo=processo.status,
                observacao=f"Status alterado de {status_anterior} para {processo.status}",
                usuario_id=current_user.id
            )
            db.session.add(historico)
        
        if responsavel_anterior != processo.responsavel_id:
            responsavel_novo = User.query.get(processo.responsavel_id)
            historico = ProcessoHistorico(
                processo_id=processo.id,
                observacao=f"Responsável alterado para {responsavel_novo.username}",
                usuario_id=current_user.id
            )
            db.session.add(historico)
        
        db.session.commit()
        flash('Processo atualizado com sucesso!')
        return redirect(url_for('dashboard'))
    
    return render_template('processo_form.html', form=form, processo=processo)

@app.route('/processo/<int:id>/tramitar', methods=['GET', 'POST'])
@login_required
def tramitar_processo(id):
    from datetime import datetime
    processo = Processo.query.get_or_404(id)
    fases_ativas = ProcessoFase.query.filter_by(ativo=True).order_by(ProcessoFase.ordem).all()
    form = TramitacaoForm(obj=processo)
    form.status.choices = [(fase.codigo, fase.descricao) for fase in fases_ativas]
    
    data_atual = datetime.now()
    form.data_registro.data = data_atual.strftime('%Y-%m-%d')  # Data padrão
    hoje = data_atual.strftime('%Y-%m-%d')
    
    if form.validate_on_submit():
        status_anterior = processo.status
        processo.status = form.status.data
        
        data_registro = datetime.strptime(form.data_registro.data, '%Y-%m-%d')
        historico = ProcessoHistorico(
            processo_id=processo.id,
            status_anterior=status_anterior,
            status_novo=processo.status,
            observacao=form.observacao.data,
            usuario_id=current_user.id,
            data_registro=data_registro
        )

        # Se o prazo estiver habilitado, adiciona as informações de prazo
        if form.habilitar_prazo.data:
            from datetime import timedelta, datetime
            
            historico.dias_prazo = form.dias_prazo.data
            historico.tipo_prazo = form.tipo_prazo.data
            historico.prazo_inicio = datetime.utcnow()
            
            # Calcula a data final do prazo considerando dias úteis ou corridos
            if form.tipo_prazo.data == 'util':
                # Função para verificar se é dia útil (não é sábado nem domingo)
                def is_workday(date):
                    return date.weekday() < 5  # 5 = Sábado, 6 = Domingo
                
                dias_contados = 0
                data_atual = historico.prazo_inicio
                while dias_contados < historico.dias_prazo:
                    data_atual += timedelta(days=1)
                    if is_workday(data_atual):
                        dias_contados += 1
                historico.prazo_fim = data_atual
            else:
                # Se for dias corridos, soma direto
                historico.prazo_fim = historico.prazo_inicio + timedelta(days=historico.dias_prazo)
        db.session.add(historico)
        
        # Criar notificação para o responsável do processo
        if processo.responsavel_id != current_user.id:
            notificacao = NotificacaoProcesso(
                processo_id=processo.id,
                tipo='mudanca_status',
                mensagem=f'O processo {processo.numero_processo} mudou de status para {processo.status}',
                destinatario_id=processo.responsavel_id,
                remetente_id=current_user.id
            )
            db.session.add(notificacao)
        
        db.session.commit()
        
        flash('Processo tramitado com sucesso!')
        return redirect(url_for('dashboard'))
    
    return render_template('processo_tramitar.html', form=form, processo=processo)

@app.route('/admin/fases')
@login_required
def listar_fases():
    if not current_user.is_admin:
        flash('Acesso não autorizado')
        return redirect(url_for('index'))
    fases = ProcessoFase.query.order_by(ProcessoFase.ordem).all()
    return render_template('fase_list.html', fases=fases)

@app.route('/admin/fases/nova', methods=['GET', 'POST'])
@login_required
def criar_fase():
    if not current_user.is_admin:
        flash('Acesso não autorizado')
        return redirect(url_for('index'))
    form = ProcessoFaseForm()
    if form.validate_on_submit():
        fase = ProcessoFase(
            codigo=form.codigo.data,
            descricao=form.descricao.data,
            ordem=form.ordem.data,
            cor=form.cor.data,
            ativo=form.ativo.data
        )
        try:
            db.session.add(fase)
            db.session.commit()
            flash('Fase criada com sucesso!')
            return redirect(url_for('listar_fases'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar fase. Este código já existe.')
    return render_template('fase_form.html', form=form)

@app.route('/admin/fases/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_fase(id):
    if not current_user.is_admin:
        flash('Acesso não autorizado')
        return redirect(url_for('index'))
    fase = ProcessoFase.query.get_or_404(id)
    form = ProcessoFaseForm(obj=fase)
    if form.validate_on_submit():
        fase.codigo = form.codigo.data
        fase.descricao = form.descricao.data
        fase.ordem = form.ordem.data
        fase.cor = form.cor.data
        fase.ativo = form.ativo.data
        try:
            db.session.commit()
            flash('Fase atualizada com sucesso!')
            return redirect(url_for('listar_fases'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar fase. Este código já existe.')
    return render_template('fase_form.html', form=form, fase=fase)

@app.route('/notificacoes')
@login_required
def listar_notificacoes():
    notificacoes = NotificacaoProcesso.query.filter_by(
        destinatario_id=current_user.id
    ).order_by(NotificacaoProcesso.created_at.desc()).all()
    return render_template('notificacoes.html', notificacoes=notificacoes)

@app.route('/notificacoes/<int:id>/lida', methods=['POST'])
@login_required
def marcar_notificacao_lida(id):
    notificacao = NotificacaoProcesso.query.get_or_404(id)
    if notificacao.destinatario_id != current_user.id:
        flash('Acesso não autorizado')
        return redirect(url_for('index'))
    
    notificacao.lida = True
    db.session.commit()
    return redirect(url_for('listar_notificacoes'))

@app.route('/exportar_processos')
@login_required
def exportar_processos():
    from openpyxl import Workbook
    from io import BytesIO
    from flask import send_file
    
    # Usar os mesmos filtros da listagem
    query = Processo.query
    
    if numero_processo := request.args.get('numero_processo'):
        query = query.filter(Processo.numero_processo.ilike(f'%{numero_processo}%'))
    if modalidade := request.args.get('modalidade'):
        query = query.filter(Processo.modalidade == modalidade)
    if status := request.args.get('status'):
        query = query.filter(Processo.status == status)
    if data_inicio := request.args.get('data_inicio'):
        query = query.filter(Processo.data_abertura >= datetime.strptime(data_inicio, '%Y-%m-%d'))
    if data_fim := request.args.get('data_fim'):
        query = query.filter(Processo.data_abertura <= datetime.strptime(data_fim, '%Y-%m-%d'))
    
    processos = query.all()
    
    # Criar arquivo Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Processos"
    
    # Cabeçalhos
    headers = [
        'Número do Processo', 'Objeto', 'Modalidade', 'Status',
        'Valor Estimado', 'Data Recebimento', 'Responsável',
        'Data Criação', 'Última Atualização'
    ]
    ws.append(headers)
    
    # Dados
    for processo in processos:
        ws.append([
            processo.numero_processo,
            processo.objeto,
            processo.modalidade,
            processo.status,
            float(processo.valor_estimado) if processo.valor_estimado else 0,
            processo.data_recebimento.strftime('%d/%m/%Y') if processo.data_recebimento else '',
            processo.responsavel.username,
            processo.created_at.strftime('%d/%m/%Y %H:%M'),
            processo.updated_at.strftime('%d/%m/%Y %H:%M') if processo.updated_at else ''
        ])
    
    # Ajustar largura das colunas
    for column in ws.columns:
        max_length = 0
        column = list(column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column[0].column_letter].width = adjusted_width
    
    # Salvar em buffer e retornar
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    
    return send_file(
        excel_file,
        download_name='processos.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
