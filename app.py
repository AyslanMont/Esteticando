from flask import Flask,render_template
from flask_login import LoginManager,login_required
from esteticando.database.database import init_db
from esteticando.controllers.users import auth_bp
from esteticando.models.user import User  

app = Flask(__name__)


init_db(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

app.register_blueprint(auth_bp)


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
