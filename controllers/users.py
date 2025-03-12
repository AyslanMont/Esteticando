from flask import Blueprint, request, redirect, render_template, flash, url_for
from database.database import mysql
from flask_login import login_user, logout_user, login_required
from app import bcrypt
from models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix="/auth", template_folder="templates")


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['nome']
        email = request.form['email']
        password = request.form['password']
        cpf = request.form['cpf']
        telefone = request.form['telefone']

        cur = mysql.connection.cursor()
        cur.execute("SELECT cli_id FROM tb_cliente WHERE cli_email = %s", (email,))
        if cur.fetchone():
            flash('E-mail já cadastrado!', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cur.execute("""
            INSERT INTO tb_cliente (cli_nome, cli_email, cli_senha, cli_cpf, cli_telefone, cli_dataCriacao)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (username, email, hashed_password, cpf, telefone))
        mysql.connection.commit()
        cur.close()

        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT cli_id, cli_nome, cli_email, cli_senha FROM tb_cliente WHERE cli_email = %s", (email,))
        user_data = cur.fetchone()
        cur.close()

        if user_data and bcrypt.check_password_hash(user_data['cli_senha'], password):
            user = User(user_data['cli_id'], user_data['cli_nome'], user_data['cli_email'])
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('resu_estabelecimento'))
        else:
            flash('E-mail ou senha incorretos', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('login'))
