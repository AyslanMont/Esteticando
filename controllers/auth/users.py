from flask import Blueprint, request, redirect, render_template, flash, url_for
from esteticando.database.database import mysql
from flask_login import login_user, logout_user, login_required
from esteticando.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from flask import current_app
import secrets
import re

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        tipo_usuario = request.form.get("tipo_usuario")

        # Validação do tipo de usuário
        if not tipo_usuario or tipo_usuario not in ['cliente', 'profissional']:
            flash('Você precisa selecionar se é cliente ou profissional.', 'danger')
            return redirect(url_for('auth.register'))

        # Validação do checkbox de termos de uso
        termos_aceitos = request.form.get("termos")
        if not termos_aceitos:
            flash('Você precisa aceitar os termos de uso para se cadastrar.', 'danger')
            return redirect(url_for('auth.register'))

        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['password']
        cpf_raw = request.form['cpf']
        telefone = request.form['telefone']

        # Limpeza e validação de CPF e telefone
        cpf_limpo = re.sub(r'\D', '', cpf_raw)  # só números
        telefone_limpo = re.sub(r'\D', '', telefone)

        if not cpf_limpo.isdigit() or len(cpf_limpo) != 11:
            flash('CPF inválido! Verifique e tente novamente.', 'danger')
            return redirect(url_for('auth.register'))

        if not telefone_limpo.isdigit() or len(telefone_limpo) < 10:
            flash('Telefone inválido! Verifique e tente novamente.', 'danger')
            return redirect(url_for('auth.register'))

        cur = mysql.connection.cursor()

        if tipo_usuario == "profissional":
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['password']
            cpf_raw = request.form['cpf']
            telefone = request.form['telefone']

            # Limpeza e validação de CPF e telefone
            cpf_limpo = re.sub(r'\D', '', cpf_raw)  # só números
            telefone_limpo = re.sub(r'\D', '', telefone)

            if not cpf_limpo.isdigit() or len(cpf_limpo) != 11:
                flash('CPF inválido! Verifique e tente novamente.', 'danger')
                return redirect(url_for('auth.register'))

            if not telefone_limpo.isdigit() or len(telefone_limpo) < 10:
                flash('Telefone inválido! Verifique e tente novamente.', 'danger')
                return redirect(url_for('auth.register'))
            
            # Verifica se CPF já cadastrado
            cur.execute("SELECT pro_id FROM tb_profissional WHERE pro_cpf = %s", (cpf_limpo,))
            if cur.fetchone():
                flash('CPF já cadastrado!', 'danger')
                cur.close()
                return redirect(url_for('auth.register'))

            hashed_password = generate_password_hash(senha)

            cur.execute("""
                INSERT INTO tb_profissional (pro_dataCriacao, pro_nome, pro_email, pro_senha, pro_cpf, pro_telefone) 
                VALUES (CURDATE(), %s, %s, %s, %s, %s)
            """, (nome, email, hashed_password, cpf_limpo, telefone_limpo))

            mysql.connection.commit()
            cur.close()

            flash('Profissional cadastrado com sucesso!', 'success')
            return redirect(url_for('auth.login'))

        else:  # cliente
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['password']
            cpf_raw = request.form['cpf']
            telefone = request.form['telefone']

            # Limpeza e validação de CPF e telefone
            cpf_limpo = re.sub(r'\D', '', cpf_raw)  # só números
            telefone_limpo = re.sub(r'\D', '', telefone)

            if not cpf_limpo.isdigit() or len(cpf_limpo) != 11:
                flash('CPF inválido! Verifique e tente novamente.', 'danger')
                return redirect(url_for('auth.register'))

            if not telefone_limpo.isdigit() or len(telefone_limpo) < 10:
                flash('Telefone inválido! Verifique e tente novamente.', 'danger')
                return redirect(url_for('auth.register'))
            

            # Verifica se email já cadastrado
            cur.execute("SELECT cli_id FROM tb_cliente WHERE cli_email = %s", (email,))
            if cur.fetchone():
                flash('E-mail já cadastrado!', 'danger')
                cur.close()
                return redirect(url_for('auth.register'))

            # Verifica se CPF já cadastrado
            cur.execute("SELECT cli_id FROM tb_cliente WHERE cli_cpf = %s", (cpf_limpo,))
            if cur.fetchone():
                flash('CPF já cadastrado!', 'danger')
                cur.close()
                return redirect(url_for('auth.register'))

            hashed_password = generate_password_hash(senha)

            cur.execute("""
                INSERT INTO tb_cliente (cli_nome, cli_email, cli_senha, cli_cpf, cli_telefone, cli_dataCriacao) 
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (nome, email, hashed_password, cpf_limpo, telefone_limpo))

            mysql.connection.commit()
            cur.close()

            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('auth.login'))

    return render_template('user/register.html')

@auth_bp.route('/esqueci-senha', methods=['POST'])
def esqueci_senha():
    email = request.form.get('email')

    if not email:
        flash('Informe um e-mail válido.', 'warning')
        return redirect(url_for('auth.login'))

    cur = mysql.connection.cursor()

    # Verifica se é cliente
    cur.execute("SELECT cli_id FROM tb_cliente WHERE cli_email = %s", (email,))
    user_data = cur.fetchone()
    tipo = 'cliente' if user_data else None

    if not user_data:
        # Verifica se é profissional
        cur.execute("SELECT pro_id FROM tb_profissional WHERE pro_email = %s", (email,))
        user_data = cur.fetchone()
        tipo = 'profissional' if user_data else None

    if not user_data:
        flash('E-mail não encontrado.', 'danger')
        cur.close()
        return redirect(url_for('auth.login'))

    token = secrets.token_urlsafe(32)

    # Salva o token
    cur.execute("INSERT INTO tb_tokens_redefinicao (email, token) VALUES (%s, %s)", (email, token))
    mysql.connection.commit()
    cur.close()

    # Envia o e-mail
    msg = Message('Redefinição de Senha - Esteticando',
                  recipients=[email])
    msg.body = f'''Olá!

Você solicitou a redefinição de senha. Clique no link abaixo para redefinir sua senha:

{url_for('auth.redefinir_senha', token=token, _external=True)}

Se não foi você, ignore este e-mail.
'''
    mail = current_app.extensions['mail']
    mail.send(msg)

    flash('E-mail de recuperação enviado!', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/redefinir_senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM tb_tokens_redefinicao WHERE token = %s", (token,))
    token_data = cur.fetchone()

    if not token_data:
        flash('Token inválido ou expirado.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        nova_senha = request.form.get('password')
        hashed = generate_password_hash(nova_senha)
        email = token_data['email']

        # Atualiza a senha
        cur.execute("UPDATE tb_cliente SET cli_senha = %s WHERE cli_email = %s", (hashed, email))
        if cur.rowcount == 0:
            cur.execute("UPDATE tb_profissional SET pro_senha = %s WHERE pro_email = %s", (hashed, email))

        # Remove o token
        cur.execute("DELETE FROM tb_tokens_redefinicao WHERE token = %s", (token,))
        mysql.connection.commit()
        cur.close()

        flash('Senha redefinida com sucesso!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('redefinir_senha.html', token=token)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        tipo_usuario = request.form.get("tipo_usuario", "cliente")

        cur = mysql.connection.cursor()
        
        try:
            if tipo_usuario == "profissional":
                cur.execute("""
                    SELECT 
                        pro_id as id, 
                        pro_nome as nome, 
                        pro_email as email, 
                        pro_senha as senha 
                    FROM tb_profissional 
                    WHERE pro_email = %s
                """, (email,))
            else:
                cur.execute("""
                    SELECT 
                        cli_id as id, 
                        cli_nome as nome, 
                        cli_email as email, 
                        cli_senha as senha 
                    FROM tb_cliente 
                    WHERE cli_email = %s
                """, (email,))

            user_data = cur.fetchone()

            if user_data and check_password_hash(user_data['senha'], password):
                user = User(
                    id=user_data['id'],
                    nome=user_data['nome'],
                    email=user_data['email'],
                    tipo_usuario=tipo_usuario
                )
                login_user(user)
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('estabelecimento.filtrar_estabelecimento'))
            
            flash('E-mail ou senha incorretos', 'danger')
        
        except Exception as e:
            flash('Erro ao processar login', 'danger')
            print(f"Erro no login: {str(e)}")
        
        finally:
            cur.close()

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
