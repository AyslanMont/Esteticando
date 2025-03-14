from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from esteticando.database.database import mysql

estabelecimento_bp = Blueprint('estabelecimento', __name__, url_prefix='/estabelecimento', template_folder='templates')

@estabelecimento_bp.route('/')
@login_required
def estabelecimento():
    return render_template('estabelecimento.html')

@estabelecimento_bp.route('/resu_estabelecimento')
@login_required
def resu_estabelecimento():
    return render_template('resu_estabelecimento.html')

@estabelecimento_bp.route('/dentro_estabelecimento')
@login_required
def dentro_estabelecimento():
    return render_template('dentro_estabelecimento.html')

@estabelecimento_bp.route('/cadastrar_estabelecimento', methods=['POST', 'GET'])
@login_required
def cadastrar_estabelecimento():
    if request.method == 'POST':
        est_nome = request.form['est_nome']
        est_descricao = request.form['est_descricao']
        est_cnpj = request.form['est_cnpj']
        est_email = request.form['est_email']
        est_telefone = request.form['est_telefone']
        #est_cat_id = request.form['est_cat_id']


        # cur = mysql.connection.cursor()
        # try:
        #     cur.execute(
        #         "INSERT INTO tb_estabelecimento (est_dataCriacao, est_nome, est_descricao, est_cnpj, est_email, est_telefone, est_cat_id) "
        #         "VALUES (CURDATE(), %s, %s, %s, %s, %s, %s)",
        #         (est_nome, est_descricao, est_cnpj, est_email, est_telefone,est_cat_id)
        #     )
        #     mysql.connection.commit()
        #     flash('Estabelecimento cadastrado com sucesso!', 'success')
        # except Exception as e:
        #     mysql.connection.rollback()
        #     flash(f'Erro ao cadastrar estabelecimento: {str(e)}', 'danger')
        # finally:
        #     cur.close()


        return redirect(url_for('estabelecimento.dentro_estabelecimento'))

    # cur = mysql.connection.cursor()
    # cur.execute("SELECT cat_id, cat_nome FROM tb_categoria")
    # categorias = cur.fetchall()
    # cur.close()

    return render_template('cadastrar_estabelecimento.html')#, categorias=categorias)