from flask import Flask, render_template, request, flash
from flask_login import LoginManager
from flask_mail import Mail
from esteticando.database.database import init_db, mysql
from esteticando.models.user import User

# Blueprints
from esteticando.controllers.auth.users import auth_bp
from esteticando.controllers.estabelecimento.estabelecimento import estabelecimento_bp
from esteticando.controllers.profissional.profissional import profissional_bp
from esteticando.controllers.servico.cli_est import cli_est_bp

# Inicialização da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'

# Configuração do Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'esteticando80@gmail.com'
app.config['MAIL_PASSWORD'] = 'ipvp ggya szxs byno'  
app.config['MAIL_DEFAULT_SENDER'] = 'seuemail@gmail.com'

# Inicializa extensões
init_db(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Registro dos blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(estabelecimento_bp)
app.register_blueprint(profissional_bp)
app.register_blueprint(cli_est_bp)



@login_manager.user_loader
def load_user(user_id):
    # Tenta carregar como cliente
    cur = mysql.connection.cursor()
    cur.execute("SELECT cli_id, cli_nome, cli_email FROM tb_cliente WHERE cli_id = %s", (user_id,))
    user_data = cur.fetchone()

    # Se não encontrar como cliente, tenta como profissional
    if not user_data:
        cur.execute("SELECT pro_id, pro_nome, pro_email FROM tb_profissional WHERE pro_id = %s", (user_id,))
        user_data = cur.fetchone()

    cur.close()

    if user_data:
        # Retorna o objeto User (para ambos cliente e profissional)
        return User(user_data['cli_id'] if 'cli_id' in user_data else user_data['pro_id'],
                    user_data['cli_nome'] if 'cli_nome' in user_data else user_data['pro_nome'],
                    user_data['cli_email'] if 'cli_email' in user_data else user_data['pro_email'])
    
    return None





@app.route('/')
def index():
    return render_template("index.html")





@app.route('/gerenciar-perfil')
def gerenciar_perfil():
    return render_template('gerenciar_perfil.html')


@app.route('/confirmar-agendamento')
def confirmar_agendamento():
    return render_template('confirmar_agendamento.html')


