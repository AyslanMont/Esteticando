from flask import Blueprint, redirect, url_for, render_template, request, flash
from esteticando.database.database import mysql
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from esteticando.models.user import User

auth_professional_bp = Blueprint('auth_professional', __name__, url_prefix="/auth/professional", template_folder='templates')

@auth_professional_bp.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['password']
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
        return redirect(url_for('auth_professional.login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT est_id, est_nome FROM tb_estabelecimento")
    estabelecimentos = cur.fetchall()
    cur.execute("SELECT cat_id, cat_nome FROM tb_categoria")
    categorias = cur.fetchall()
    cur.close()

    # Renderiza o template de cadastro com os dados dos estabelecimentos e categorias
    return render_template('professional/register.html', estabelecimentos=estabelecimentos, categorias=categorias)


@auth_professional_bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT cli_id, pro_nome, pro_email, pro_senha FROM tb_profissional WHERE pro_email = %s", (email,))
        user_data = cur.fetchone()
        cur.close()


        if user_data and check_password_hash(user_data['pro_senha'], password):
            user = User(user_data['cli_id'], user_data['pro_nome'], user_data['pro_email'])
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('estabelecimento.resu_estabelecimento'))
        else:
            flash('E-mail ou senha incorretos', 'danger')

    return render_template('professional/login.html')


auth_professional_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('index'))