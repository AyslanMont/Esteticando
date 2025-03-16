from flask import Blueprint, request, redirect, render_template, flash, url_for
import datetime
from esteticando.database.database import mysql

# Cria um Blueprint para as rotas relacionadas a profissionais
profissional_bp = Blueprint('profissional', __name__, url_prefix="/profissional", template_folder="templates")

# Rota para cadastro de profissionais
@profissional_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # Obtém os dados do formulário de cadastro
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        cpf = request.form['cpf']
        telefone = request.form['telefone']
        estabelecimento = request.form['estabelecimento']
        categoria = request.form['categoria']

        # Conecta ao banco de dados e insere o novo profissional
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO tb_profissional (pro_dataCriacao, pro_nome, pro_email, pro_senha, pro_cpf, pro_telefone, pro_est_id, pro_cat_id) "
            "VALUES (CURDATE(), %s, %s, %s, %s, %s, %s, %s)",
            (nome, email, senha, cpf, telefone, estabelecimento, categoria)
        )
        mysql.connection.commit()
        cur.close()

        # Exibe uma mensagem de sucesso e redireciona para a página de cadastro
        flash('Profissional cadastrado com sucesso!', 'success')
        return redirect(url_for('cadastro'))

    # Se for um GET, busca os estabelecimentos e categorias para preencher o formulário
    cur = mysql.connection.cursor()
    cur.execute("SELECT est_id, est_nome FROM tb_estabelecimento")
    estabelecimentos = cur.fetchall()
    cur.execute("SELECT cat_id, cat_nome FROM tb_categoria")
    categorias = cur.fetchall()
    cur.close()

    # Renderiza o template de cadastro com os dados dos estabelecimentos e categorias
    return render_template('cadastro.html', estabelecimentos=estabelecimentos, categorias=categorias)

# Rota para verificar a disponibilidade de profissionais
@profissional_bp.route('/disponibilidade', methods=['GET', 'POST'])
def disponibilidade():
    if request.method == 'POST':
        # Obtém os dados do formulário de disponibilidade
        estabelecimento = request.form.get('estabelecimento')
        data_agendamento = request.form.get('data')

        # Validação dos campos obrigatórios
        if not estabelecimento or not data_agendamento:
            flash('Estabelecimento e data de agendamento são obrigatórios', 'warning')
            return render_template('profi_disponivel.html')

        try:
            # Converte a data de agendamento para o formato correto
            data_agendamento = datetime.strptime(data_agendamento, '%Y-%m-%d %H:%M:%S')
            dia_semana = data_agendamento.strftime('%A').lower()

            # Conecta ao banco de dados
            cur = mysql.connection.cursor()

            # Busca o ID do estabelecimento com base no nome
            query_estabelecimento = "SELECT est_id FROM tb_estabelecimento WHERE est_nome = %s"
            cur.execute(query_estabelecimento, (estabelecimento,))
            estabelecimento_result = cur.fetchone()

            if not estabelecimento_result:
                flash('Estabelecimento não encontrado', 'warning')
                return render_template('profi_disponivel.html')

            estabelecimento_id = estabelecimento_result['est_id']

            # Busca profissionais disponíveis no estabelecimento e na data especificada
            query_profissionais = ''' SELECT pro_nome FROM tb_profissional JOIN tb_disponibilidade_profissional ON pro_id = dip_pro_id
            WHERE pro_est_id = %s AND dip_dia = %s AND dip_horarioInicio <= %s AND dip_horarioFim >= %s AND pro_id NOT IN (
            SELECT age_pro_id FROM tb_agendamento WHERE age_horario = %s) '''
           
            cur.execute(query_profissionais, (
                estabelecimento_id, 
                dia_semana, 
                data_agendamento.time(), 
                data_agendamento.time(), 
                data_agendamento.time()
            ))
            profissionais = cur.fetchall()

            cur.close()

            # Passa os profissionais para o template
            return render_template('profi_disponivel.html', profissionais=profissionais)

        except Exception as e:
            # Em caso de erro, exibe uma mensagem de erro
            flash(f'Erro ao buscar profissionais: {str(e)}', 'error')
            return render_template('profi_disponivel.html')

    # Se for um GET, apenas renderiza o template
    return render_template('profi_disponivel.html')