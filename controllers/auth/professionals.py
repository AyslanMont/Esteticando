from flask import Blueprint, redirect, url_for, render_template, request, flash
from esteticando.database.database import mysql

auth_professional_bp = Blueprint('auth_professional', __name__, url_prefix="/auth/professional", template_folder='templates')

@auth_professional_bp.route('/register')
def register():
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

    # Renderiza o template de cadastro com os dados dos estabelecimentos e categorias
    return render_template('professional/register.html', estabelecimentos=estabelecimentos, categorias=categorias)