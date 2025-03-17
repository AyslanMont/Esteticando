from flask import Blueprint, request, redirect, render_template, flash, url_for
import datetime
from esteticando.database.database import mysql

# Cria um Blueprint para as rotas relacionadas a profissionais
profissional_bp = Blueprint('profissional', __name__, url_prefix="/profissional", template_folder="templates")

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