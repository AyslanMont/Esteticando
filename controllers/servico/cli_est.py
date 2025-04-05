from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from esteticando.database.database import mysql

cli_est_bp = Blueprint('estabelecimento_cliente', __name__, url_prefix='/est', template_folder='templates')

@cli_est_bp.route('/listar', methods=['GET', 'POST'])
def listar_estabelecimentos():
    result_est = []
    
    if request.method == 'POST':
        end_estado = request.form.get('estado', '').strip()
        end_cidade = request.form.get('cidade', '').strip()
        end_bairro = request.form.get('bairro', '').strip()
        est_nome = request.form.get('nome', '').strip()

        if not end_estado:
            flash('Estado é um campo obrigatório.', 'warning')
            return render_template('listar_est.html', result_est=result_est)

        query_est = """
            SELECT est_id, est_nome, est_descricao, est_email, est_telefone, end_rua, end_numero, end_bairro, end_cidade, end_estado 
            FROM tb_endereco_estabelecimento 
            JOIN tb_estabelecimento ON est_id = end_est_id 
            WHERE end_estado = %s
        """
        parametros = [end_estado]

        if end_cidade:
            query_est += " AND end_cidade = %s"
            parametros.append(end_cidade)
        
        if end_bairro:
            query_est += " AND end_bairro = %s"
            parametros.append(end_bairro)

        if est_nome:
            query_est += " AND est_nome LIKE %s"
            parametros.append(f"%{est_nome}%")

        cur = mysql.connection.cursor()
        try:
            cur.execute(query_est, tuple(parametros))
            result_est = cur.fetchall()
        finally:
            cur.close()

        if not result_est:
            flash('Nenhum estabelecimento encontrado com esses filtros.', 'info')

    else:  # Método GET
        cur = mysql.connection.cursor()
        try:
            query = """
                SELECT est_id, est_nome, est_descricao, est_email, est_telefone, end_rua, end_numero, end_bairro, end_cidade, end_estado
                FROM tb_endereco_estabelecimento 
                JOIN tb_estabelecimento ON est_id = end_est_id 
                ORDER BY est_nome
                LIMIT 20
            """
            cur.execute(query)
            result_est = cur.fetchall()
        finally:
            cur.close()

    return render_template('listar_est.html', result_est=result_est)

@cli_est_bp.route('/<int:est_id>/funcionarios')
def listar_funcionarios(est_id):
    # Busca os funcionários do estabelecimento no banco de dados
    cur = mysql.connection.cursor()
    query = """
        SELECT pro_id, pro_nome, pro_telefone
        FROM tb_profissional
        WHERE pro_est_id = %s
    """
    cur.execute(query, (est_id,))
    funcionarios = cur.fetchall()
    cur.close()
    
    return render_template('funcionarios.html', funcionarios=funcionarios, est_id=est_id)