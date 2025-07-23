from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from esteticando.database.database import mysql
from werkzeug.security import generate_password_hash, check_password_hash


cli_est_bp = Blueprint('cliente', __name__, url_prefix='/cliente', template_folder='templates')

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


@cli_est_bp.route('/perfil')
@login_required
def perfil():
    if not hasattr(current_user, 'tipo_usuario') or current_user.tipo_usuario != 'cliente':
        return redirect(url_for('estabelecimento.filtrar_estabelecimento'))
    
    dados_user = None

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT cli_id, cli_nome, cli_email, cli_telefone
            FROM tb_cliente WHERE cli_id = %s
        """, (current_user.id,))
        resultado = cur.fetchone()
    finally:
        cur.close()

    if resultado:
        dados_user = {
            'cli_id': resultado['cli_id'],
            'cli_nome': resultado['cli_nome'],
            'cli_email': resultado['cli_email'],
            'cli_telefone': resultado['cli_telefone']
        }

    return render_template('perfil_cliente.html', user=dados_user)

@cli_est_bp.route('/editar_perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    if not hasattr(current_user, 'tipo_usuario') or current_user.tipo_usuario != 'cliente':
        return redirect(url_for('estabelecimento.filtrar_estabelecimento'))
    
    def formatar_telefone(telefone):
        if not telefone or len(telefone) < 10:
            return telefone
        telefone = ''.join(filter(str.isdigit, telefone))
        if len(telefone) == 10:
            return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
        elif len(telefone) == 11:
            return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
        return telefone

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        cur.execute("""
            SELECT cli_nome, cli_senha, cli_telefone 
            FROM tb_cliente 
            WHERE cli_id = %s
        """, (current_user.id,))
        dados_atuais = cur.fetchone()

        if not dados_atuais:
            flash('Usuário não encontrado', 'danger')
            cur.close()
            return redirect(url_for('cliente.editar_perfil'))

        nome = request.form.get('nome', dados_atuais['cli_nome'])
        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('senha')
        check_senha = request.form.get('check_senha')
        telefone = request.form.get('telefone', dados_atuais['cli_telefone'])

        try:
            senha_db = dados_atuais['cli_senha']

            if nova_senha:
                if not check_password_hash(senha_db, senha_atual):
                    flash('Senha atual incorreta', 'danger')
                    return redirect(url_for('cliente.editar_perfil'))

                if nova_senha != check_senha:
                    flash('As novas senhas não coincidem', 'danger')
                    return redirect(url_for('cliente.editar_perfil'))

                senha_hash = generate_password_hash(nova_senha)
            else:
                senha_hash = senha_db

            cur.execute("""
                UPDATE tb_cliente 
                SET cli_nome = %s, cli_senha = %s, cli_telefone = %s
                WHERE cli_id = %s
            """, (nome, senha_hash, telefone, current_user.id))
            mysql.connection.commit()
            flash('Perfil atualizado com sucesso', 'success')

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao atualizar perfil: {str(e)}', 'danger')
        finally:
            cur.close()

        return redirect(url_for('cliente.editar_perfil'))

    cur.execute("""
        SELECT cli_nome, cli_cpf, cli_email, cli_telefone 
        FROM tb_cliente 
        WHERE cli_id = %s
    """, (current_user.id,))
    user = cur.fetchone()
    cur.close()

    if user:
        user['cli_telefone'] = formatar_telefone(user['cli_telefone'])

    return render_template('editar_perfilCliente.html', user=user)
