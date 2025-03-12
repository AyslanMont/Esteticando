from flask import Flask, render_template
from database.database import init_db
from flask_login import LoginManager, login_required
from flask_bcrypt import Bcrypt
from controllers.users import auth_bp

app = Flask(__name__)

init_db(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.register_blueprint(auth_bp)

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
