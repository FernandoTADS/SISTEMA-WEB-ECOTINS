from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime

# Configuração de caminhos das pastas do projeto EcoTins
app = Flask(__name__, template_folder='../web', static_folder='../web')
app.secret_key = 'unitins_tads_ecotins'

# Função auxiliar de conexão com o banco de dados SQLite
def conectar_db():
    conn = sqlite3.connect('ecotins.db')
    conn.row_factory = sqlite3.Row  
    return conn

# ==========================================
# ROTAS DE ACESSO LIVRE
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pontos')
def pontos():
    return render_template('pontosdecoleta.html')

# ==========================================
# AUTENTICAÇÃO (LOGIN / CADASTRO / SAIR)
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    email_preenchido = ""
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        conn = conectar_db()
        user = conn.execute('SELECT * FROM usuarios WHERE email = ? AND senha = ?', (email, senha)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['nome']
            session['user_tipo'] = user['tipo']  
            
            if user['tipo'] == 'admin':
                return redirect(url_for('admin_dashboard'))
                
            return redirect(url_for('index'))
        else:
            flash("E-mail ou senha incorretos!")
            email_preenchido = email
            
    return render_template('login.html', email_preenchido=email_preenchido)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        senha = request.form.get('senha')
        
        conn = conectar_db()
        
        # ESPAÇAMENTO ALINHADO: Insere todos os dados incluindo o novo telefone
        conn.execute('''
            INSERT INTO usuarios (nome, email, telefone, senha, tipo, status) 
            VALUES (?, ?, ?, ?, 'user', 'Ativo')
        ''', (nome, email, telefone, senha))
        
        conn.commit()
        conn.close()
        
        flash("Conta criada com sucesso! Faça login.")
        return redirect(url_for('login'))
        
    return render_template('cadastro.html')

@app.route('/sair')
def sair():
    session.clear()
    return redirect(url_for('index'))

# ==========================================
# ROTAS DO USUÁRIO COMUM (EXIGEM LOGIN)
# ==========================================
@app.route('/solicitar', methods=['GET', 'POST'])
def solicitar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    conn = conectar_db()
    
    # 1. Busca o nome completo do usuário logado na sessão
    usuario = conn.execute('SELECT nome FROM usuarios WHERE id = ?', (user_id,)).fetchone()
    user_nome = usuario['nome'] if usuario else "Usuário"

    if request.method == 'POST':
        # 2. Captura os dados do novo formulário
        endereco = request.form.get('endereco')
        tipo_residuo = request.form.get('tipo')
        descricao = request.form.get('descricao')
        
        # Formato de data padrão do seu histórico (Ex: 01/01/2026 00:00)
        from datetime import datetime
        data_atual = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        # 3. Salva no banco incluindo o novo campo 'endereco'
        conn.execute('''
            INSERT INTO solicitacoes (usuario_id, endereco, tipo_residuo, descricao, status, data_pedido)
            VALUES (?, ?, ?, ?, 'Aguardando Coleta', ?)
        ''', (user_id, endereco, tipo_residuo, descricao, data_atual))
        
        conn.commit()
        conn.close()
        
        flash("Solicitação de coleta enviada com sucesso!")
        
        
        # ou mude para 'admin_dashboard' / o endpoint correto do seu histórico se preferir.
        return redirect(url_for('solicitar'))
        
    conn.close()
    return render_template('solicitar.html', user_nome=user_nome)


# ASSOCIAÇÃO EXATA DA ROTA 
@app.route('/solicitacoes')
def solicitacoes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    conn = conectar_db()
    
    # Busca apenas os registros ativos do usuário logado (sem os excluídos)
    pedidos = conn.execute('''
        SELECT * FROM solicitacoes 
        WHERE usuario_id = ? AND status != "Excluído" AND status != "Excluido"
        ORDER BY id DESC
    ''', (user_id,)).fetchall()
    
    conn.close()
    
    # Garante que o Flask vai abrir exatamente o arquivo solicitacoes.html
    return render_template('solicitacoes.html', pedidos=pedidos, solicitacoes=pedidos)


# ROTA POST PARA O USUÁRIO EDITAR A PRÓPRIA SOLICITAÇÃO (SÓ SE ESTIVER AGUARDANDO)
@app.route('/solicitacoes/editar', methods=['POST'])
def editar_solicitacao_usuario():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    id_pedido = request.form.get('id_solicitacao')
    novo_tipo = request.form.get('tipo')
    nova_descricao = request.form.get('descricao')
    
    conn = conectar_db()
    # Segurança: Verifica se o pedido pertence ao usuário e se ainda está aguardando coleta
    pedido = conn.execute('SELECT * FROM solicitacoes WHERE id = ? AND usuario_id = ?', (id_pedido, user_id)).fetchone()
    
    if pedido:
        if pedido['status'] == 'Aguardando Coleta':
            conn.execute('''
                UPDATE solicitacoes 
                SET tipo_residuo = ?, descricao = ? 
                WHERE id = ?
            ''', (novo_tipo, nova_descricao, id_pedido))
            conn.commit()
            flash("Solicitação atualizada com sucesso!")
        else:
            flash("Erro: Não é possível editar uma solicitação que já está em andamento.")
    else:
        flash("Solicitação não encontrada.")
        
    conn.close()
    return redirect(url_for('solicitacoes'))






@app.route('/solicitacoes/excluir', methods=['POST'])
def excluir_solicitacao_usuario():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    id_solicitacao = request.form.get('id_solicitacao')
    
    # Captura data e hora atual do cancelamento
    data_atual = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    conn = conectar_db()
    
    # Salva o status como Excluído e registra o momento exato
    conn.execute('''
        UPDATE solicitacoes 
        SET status = "Excluído", data_exclusao = ? 
        WHERE id = ? AND usuario_id = ?
    ''', (data_atual, id_solicitacao, user_id))
    
    conn.commit()
    conn.close()
    
    flash("Sua solicitação foi cancelada com sucesso!")
    return redirect(url_for('solicitacoes'))



# ==========================================
# PAINEL DO ADMINISTRADOR CENTRALIZADO
# ==========================================
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('user_tipo') != 'admin':
        return redirect(url_for('login'))
        
    conn = conectar_db()
    
    # 1. Busca solicitações ativas trazendo o nome e o telefone do usuário
    solicitacoes = conn.execute('''
        SELECT solicitacoes.*, usuarios.nome AS nome_usuario, usuarios.telefone AS tel_usuario 
        FROM solicitacoes 
        JOIN usuarios ON solicitacoes.usuario_id = usuarios.id
        WHERE solicitacoes.status != "Excluído" AND solicitacoes.status != "Excluido" AND solicitacoes.status != "Cancelado"
        ORDER BY solicitacoes.id DESC
    ''').fetchall()
    
    # 2. Busca todos os usuários cadastrados
    usuarios = conn.execute('SELECT * FROM usuarios').fetchall()
    
    # 3. INDENTAÇÃO: Busca itens da lixeira com nome e telefone
    lixeira = conn.execute('''
        SELECT solicitacoes.*, usuarios.nome AS nome_usuario, usuarios.telefone AS tel_usuario 
        FROM solicitacoes 
        JOIN usuarios ON solicitacoes.usuario_id = usuarios.id
        WHERE solicitacoes.status = "Excluído" OR solicitacoes.status = "Excluido" OR solicitacoes.status = "Cancelado"
        ORDER BY solicitacoes.id DESC
    ''').fetchall()
    
    # Contadores para os Cards superiores
    coletas_ativas = len(solicitacoes)
    usuarios_cadastrados = len(usuarios)
    total_excluidas = len(lixeira)
    
    conn.close()
    
    return render_template(
        'admin.html', 
        solicitacoes=solicitacoes, 
        solicitacoes_ativas=solicitacoes,
        pedidos=solicitacoes,
        usuarios=usuarios, 
        usuarios_sistema=usuarios,
        lixeira=lixeira,
        solicitacoes_excluidas=lixeira,
        excluidos=lixeira,
        coletas_ativas=coletas_ativas,
        total_ativas=coletas_ativas,
        usuarios_cadastrados=usuarios_cadastrados,
        total_usuarios=usuarios_cadastrados,
        total_excluidas=total_excluidas,
        itens_lixeira=total_excluidas
    )

# ROTA POST PARA ATUALIZAR STATUS VIA MODAL POP-UP

@app.route('/admin/solicitacoes/status/atualizar', methods=['POST'])
def admin_atualizar_status_modal():
    if 'user_id' not in session or session.get('user_tipo') != 'admin':
        return redirect(url_for('login'))
        
    id_solicitacao = request.form.get('id_solicitacao')
    novo_status = request.form.get('status')
    data_recolhimento = request.form.get('data_recolhimento', '')
    data_hora_realizada = request.form.get('data_hora_realizada', '').strip()
    
    horario_atual = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    # 1. Se foi um SUCESSO, carimba a data/hora limpa automaticamente
    if novo_status == 'Coleta Realizada':
        data_hora_realizada = horario_atual
        
    # 2. Se foi um INSUCESSO (Não Realizada), preserva a justificativa digitada
    elif novo_status == 'Coleta Não Realizada':
        if data_hora_realizada:
            # Mantém o texto puro digitado no pop-up (Ex: "carro quebrou")
            data_hora_realizada = data_hora_realizada 
        else:
            data_hora_realizada = f"Não realizada ({horario_atual})"
            
    # 3. Status intermediários automáticos
    elif novo_status in ['Coleta Aceita', 'Coleta Processada'] and not data_hora_realizada:
        data_hora_realizada = horario_atual
        
    conn = conectar_db()
    conn.execute('''
        UPDATE solicitacoes 
        SET status = ?, data_recolhimento = ?, data_hora_realizada = ? 
        WHERE id = ?
    ''', (novo_status, data_recolhimento, data_hora_realizada, id_solicitacao))
    conn.commit()
    conn.close()
    
    flash("Status da coleta atualizado com sucesso!")
    return redirect(url_for('admin_dashboard'))





# ROTA: Gerenciamento dos 5 estágios de status da coleta
@app.route('/admin/solicitacoes/status/<int:id>', methods=['GET', 'POST'])
def admin_status_coleta(id):
    if 'user_id' not in session or session.get('user_tipo') != 'admin':
        return redirect(url_for('login'))
        
    conn = conectar_db()
    
    if request.method == 'POST':
        novo_status = request.form['status']
        data_recolhimento = request.form.get('data_recolhimento', '')
        data_hora_realizada = request.form.get('data_hora_realizada', '')
        
        # Se mudar para concluída e deixar a hora vazia, o sistema pega o horário atual do servidor automaticamente
        if novo_status == 'Coleta Realizada' and not data_hora_realizada:
            data_hora_realizada = datetime.now().strftime('%d/%m/%Y %H:%M')
            
        conn.execute('''
            UPDATE solicitacoes 
            SET status = ?, data_recolhimento = ?, data_hora_realizada = ? 
            WHERE id = ?
        ''', (novo_status, data_recolhimento, data_hora_realizada, id))
        conn.commit()
        conn.close()
        
        flash("Status da coleta atualizado com sucesso!")
        return redirect(url_for('admin_dashboard'))
        
    pedido = conn.execute('SELECT * FROM solicitacoes WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if not pedido:
        flash("Solicitação não encontrada.")
        return redirect(url_for('admin_dashboard'))
        
    return render_template('admin_status_coleta.html', pedido=pedido)



# ROTA POST: ADMIN EDITA DADOS DA SOLICITAÇÃO VIA MODAL
@app.route('/admin/solicitacoes/editar/salvar', methods=['POST'])
def admin_editar_solicitacao_modal():
    if 'user_id' not in session or session.get('user_tipo') != 'admin':
        return redirect(url_for('login'))
        
    id_solicitacao = request.form.get('id_solicitacao')
    novo_tipo = request.form.get('tipo')
    nova_descricao = request.form.get('descricao')
    
    conn = conectar_db()
    conn.execute('''
        UPDATE solicitacoes 
        SET tipo_residuo = ?, descricao = ? 
        WHERE id = ?
    ''', (novo_tipo, nova_descricao, id_solicitacao))
    conn.commit()
    conn.close()
    
    flash("Dados da solicitação corrigidos com sucesso!")
    return redirect(url_for('admin_dashboard'))



@app.route('/admin/solicitacoes/excluir', methods=['POST'])
def admin_excluir_solicitacao():
    if 'user_id' not in session or session.get('user_tipo') != 'admin':
        return redirect(url_for('login'))
        
    id_solicitacao = request.form.get('id_solicitacao')
    
    # Captura data e hora atual da exclusão administrativa
    data_atual = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    conn = conectar_db()
    
    # Atualiza o status para 'Excluído' e adiciona a data de descarte
    conn.execute('''
        UPDATE solicitacoes 
        SET status = "Excluído", data_exclusao = ? 
        WHERE id = ?
    ''', (data_atual, id_solicitacao))
    
    conn.commit()
    conn.close()
    
    flash("Solicitação movida para a lixeira com sucesso!")
    return redirect(url_for('admin_dashboard'))










# ROTA POST PARA ATUALIZAR USUÁRIO VIA MODAL POP-UP
@app.route('/admin/usuarios/editar/atualizar', methods=['POST'])
def admin_atualizar_usuario_modal():
    if 'user_id' not in session or session.get('user_tipo') != 'admin':
        return redirect(url_for('login'))
        
    id_usuario = request.form.get('id_usuario')
    nome = request.form.get('nome')
    email = request.form.get('email')
    tipo = request.form.get('tipo', 'user')
    
    conn = conectar_db()
    try:
        conn.execute('''
            UPDATE usuarios 
            SET nome = ?, email = ?, tipo = ? 
            WHERE id = ?
        ''', (nome, email, tipo, id_usuario))
        conn.commit()
        flash("Usuário atualizado com sucesso!")
    except sqlite3.IntegrityError:
        flash("Erro: Este e-mail já está em uso por outro usuário.")
    finally:
        conn.close()
        
    return redirect(url_for('admin_dashboard'))




@app.route('/admin/usuarios/excluir', methods=['POST'])
def admin_excluir_usuario():
    if 'user_id' not in session or session.get('user_tipo') != 'admin':
        return redirect(url_for('login'))
    id_usuario = request.form.get('id_usuario')
    if id_usuario:
        conn = conectar_db()
        conn.execute('DELETE FROM usuarios WHERE id = ?', (id_usuario,))
        conn.commit()
        conn.close()
        flash("Usuário removido com sucesso!")
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)