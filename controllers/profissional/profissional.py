from flask import Blueprint, request, redirect, render_template, flash, url_for
from esteticando.database.database import mysql

profissional_bp = Blueprint('profissional', __name__, url_prefix="/profissional", template_folder="templates")


@profissional_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        cpf = request.form['cpf']
        telefone = request.form['telefone']
        estabelecimento = request.form['estabelecimento']
        categoria = request.form['categoria']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO tb_profissional (pro_dataCriacao, pro_nome, pro_email, pro_senha, pro_cpf, pro_telefone, pro_est_id, pro_cat_id) "
            "VALUES (CURDATE(), %s, %s, %s, %s, %s, %s, %s)",
            (nome, email, senha, cpf, telefone, estabelecimento, categoria)
        )
        mysql.connection.commit()
        cur.close()

        flash('Profissional cadastrado com sucesso!', 'success')
        return redirect(url_for('cadastro'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT est_id, est_nome FROM tb_estabelecimento")
    estabelecimentos = cur.fetchall()
    cur.execute("SELECT cat_id, cat_nome FROM tb_categoria")
    categorias = cur.fetchall()
    cur.close()

    return render_template('cadastro.html', estabelecimentos=estabelecimentos, categorias=categorias)