from flask import Blueprint, request, redirect, render_template, flash, url_for
from esteticando.database.database import mysql
from flask_login import login_user, logout_user, login_required
from esteticando.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    tipo_usuario = request.form.get("tipo_usuario")

    if tipo_usuario == "profissional":
        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['password']
            cpf = request.form['cpf']
            telefone = request.form['telefone']

            hashed_password = generate_password_hash(senha)

            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO tb_profissional (pro_dataCriacao, pro_nome, pro_email, pro_senha, pro_cpf, pro_telefone) 
                VALUES (CURDATE(), %s, %s, %s, %s, %s)
            """, (nome, email, hashed_password, cpf, telefone))
            mysql.connection.commit()
            cur.close()

            flash('Profissional cadastrado com sucesso!', 'success')
            return redirect(url_for('auth.login'))

        return render_template('professional/register.html')
    

    #cliente
    else:  
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
                return redirect(url_for('auth.register'))
            
            hashed_password = generate_password_hash(password)

            cur.execute("""
                INSERT INTO tb_cliente (cli_nome, cli_email, cli_senha, cli_cpf, cli_telefone, cli_dataCriacao) 
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (username, email, hashed_password, cpf, telefone))
            mysql.connection.commit()
            cur.close()

            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('auth.login'))

        return render_template('user/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    tipo_usuario = request.form.get("tipo_usuario")

    if tipo_usuario == "profissional":
        tipo_usuario = request.form.get("tipo_usuario")
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            cur = mysql.connection.cursor()
            cur.execute("SELECT pro_id, pro_nome, pro_email, pro_senha FROM tb_profissional WHERE pro_email = %s", (email,))
            user_data = cur.fetchone()
            cur.close()

            if user_data and check_password_hash(user_data['pro_senha'], password):
                user = User(user_data['pro_id'], user_data['pro_nome'], user_data['pro_email'])
                login_user(user)
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('estabelecimento.resu_estabelecimento'))
            else:
                flash('E-mail ou senha incorretos', 'danger')
                print("Senha incorreta ou e-mail não encontrado")

        return render_template('professional/login.html')
    
    #cliente
    else:
        if request.method == 'POST':
            tipo_usuario = request.form.get("tipo_usuario")
            email = request.form['email']
            password = request.form['password']


            cur = mysql.connection.cursor()
            cur.execute("SELECT cli_id, cli_nome, cli_email, cli_senha FROM tb_cliente WHERE cli_email = %s", (email,))
            user_data = cur.fetchone()
            cur.close()

            if user_data and check_password_hash(user_data['cli_senha'], password):
                user = User(user_data['cli_id'], user_data['cli_nome'], user_data['cli_email'])
                login_user(user)
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('estabelecimento.resu_estabelecimento'))
            else:
                flash('E-mail ou senha incorretos', 'danger')
                print("Senha incorreta ou e-mail não encontrado")

        return render_template('user/login.html')


@auth_bp.route('/endereco', methods=["GET", "POST"])
def endereco():
    return render_template("user/endereco.html")

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('auth.login'))
