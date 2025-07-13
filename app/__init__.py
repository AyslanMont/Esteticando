from flask import Flask, render_template
from flask_login import LoginManager,current_user
from flask_mail import Mail
from esteticando.database.database import init_db, mysql
from esteticando.models.user import User

# Blueprints
from esteticando.controllers.auth.users import auth_bp
from esteticando.controllers.estabelecimento.estabelecimento import estabelecimento_bp
from esteticando.controllers.profissional.profissional import profissional_bp
from esteticando.controllers.servico.cli_est import cli_est_bp
from esteticando.controllers.servico.agendamento import agendamento_bp
from esteticando.controllers.servico.servico import servico_bp


app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'esteticando80@gmail.com'
app.config['MAIL_PASSWORD'] = 'ipvp ggya szxs byno'  
app.config['MAIL_DEFAULT_SENDER'] = 'seuemail@gmail.com'

init_db(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

app.register_blueprint(auth_bp)
app.register_blueprint(estabelecimento_bp)
app.register_blueprint(profissional_bp)
app.register_blueprint(cli_est_bp, url_prefix='/cliente')
app.register_blueprint(agendamento_bp, url_prefix='/agendamento')
app.register_blueprint(servico_bp, url_prefix='/servico')

@login_manager.user_loader
def load_user(user_id):
    try:
        tipo_usuario, id = user_id.split('_', 1)
        id = int(id)
    except (ValueError, AttributeError):
        return None

    cur = mysql.connection.cursor()
    
    try:
        if tipo_usuario == 'cliente':
            cur.execute("""
                        SELECT cli_id as id, cli_nome as nome, cli_email as email FROM tb_cliente WHERE cli_id = %s""", (id,))

        elif tipo_usuario == 'profissional':
            cur.execute("""
                        SELECT pro_id as id, pro_nome as nome, pro_email as email FROM tb_profissional WHERE pro_id = %s""", (id,))
        else:
            return None

        user_data = cur.fetchone()
        
        if user_data:
            return User(
                id=user_data['id'],
                nome=user_data['nome'],
                email=user_data['email'],
                tipo_usuario=tipo_usuario
            )
        
        return None
    
    finally:
        cur.close()
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/gerenciar-perfil')
def gerenciar_perfil():
    return render_template('gerenciar_perfil.html')

@app.route('/confirmar-agendamento')
def confirmar_agendamento():
    return render_template('confirmar_agendamento.html')

@app.route('/debug-user')
def debug_user():
    return {
        "id": current_user.id,
        "nome": current_user.nome,
        "email": current_user.email,
        "tipo_usuario": current_user.tipo_usuario,
        "is_authenticated": current_user.is_authenticated,
        "is_active": current_user.is_active,
        "is_anonymous": current_user.is_anonymous
    }