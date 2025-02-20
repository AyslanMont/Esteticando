from flask import Flask, render_template, redirect, url_for, request, flash
from database import init_db, mysql
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)

init_db(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT cli_id, cli_nome, cli_email FROM tb_cliente WHERE cli_id = %s", (user_id,))
    user_data = cur.fetchone()
    cur.close()
    if user_data:
        return User(user_data['cli_id'], user_data['cli_nome'], user_data['cli_email'])
    return None


@app.route('/')
def index():
    return render_template("dashboard.html")


@app.route('/login', methods=['GET', 'POST'])
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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
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


@app.route('/gerenciar_perfil')
def gerenciar_perfil():
    return render_template('gerenciar_perfil.html')


@app.route('/estabelecimento')
def estabelecimento():
    return render_template('estabelecimento.html')


@app.route('/resu_estabelecimento')
@login_required
def resu_estabelecimento():
    return render_template('resu_estabelecimento.html')


@app.route('/dentro_estabelecimento')
def dentro_estabelecimento():
    return render_template('dentro_estabelecimento.html')


@app.route('/confirmar_agendamento')
def confirmar_agendamento():
    return render_template('confirmar_agendamento.html')


@app.route('/agendar')
def agendar():
    return render_template('agendar.html')
