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












#barbaridade
#-----------------------------------------------------
#filtro de estabelecimentos
@app.route('/home', methods=['GET', 'POST'])
def home():
    result_est = []
    
    if request.method == 'POST':
        end_estado = request.form.get('estado', '').strip()
        end_cidade = request.form.get('cidade', '').strip()
        end_bairro = request.form.get('bairro', '').strip()
        est_nome = request.form.get('nome', '').strip()

        if not end_estado:
            flash('Estado é um campo obrigatório.', 'warning')
            return render_template('filtrar_estabelecimento.html', result_est=result_est)

        query_est = """
            SELECT est_id, est_nome, est_descricao, est_email, est_telefone, end_rua, end_numero, end_bairro, end_cidade, end_estado 
            FROM tb_endereco_estabelecimento 
            JOIN tb_estabelecimento ON est_id = end_est_id 
            WHERE end_estado = %s
        """
        parametros = [end_estado]

        if end_cidade:
            query_est += " AND end_cidade = %s"
            parametros.append(end_cidade)
        
        if end_bairro:
            query_est += " AND end_bairro = %s"
            parametros.append(end_bairro)

        if est_nome:
            query_est += " AND est_nome LIKE %s"
            parametros.append(f"%{est_nome}%")

        cur = mysql.connection.cursor()
        try:
            cur.execute(query_est, tuple(parametros))
            result_est = cur.fetchall()
        finally:
            cur.close()

        if not result_est:
            flash('Nenhum estabelecimento encontrado com esses filtros.', 'info')

    else:  # Método GET
        cur = mysql.connection.cursor()
        try:
            query = """
                SELECT est_id, est_nome, est_descricao, est_email, est_telefone, end_rua, end_numero, end_bairro, end_cidade, end_estado
                FROM tb_endereco_estabelecimento 
                JOIN tb_estabelecimento ON est_id = end_est_id 
                ORDER BY est_nome
                LIMIT 20
            """
            cur.execute(query)
            result_est = cur.fetchall()
        finally:
            cur.close()

    return render_template('filtrar_estabelecimento.html', result_est=result_est)
  
@app.route('/estabelecimento/<int:est_id>/servicos')
def perfil_estabelecimento(est_id):
    cur = mysql.connection.cursor()
    query_servicos = """
        SELECT est_nome, ser_nome, ser_preco,ser_id 
        FROM tb_estabelecimento 
        JOIN tb_servico ON ser_est_id = est_id
        WHERE est_id = %s
    """
    cur.execute(query_servicos, (est_id,))
    servicos = cur.fetchall()
    cur.close()
    return render_template('selecionar_servico.html', servicos=servicos, est_id=est_id)


@app.route('/gerenciar-perfil')
def gerenciar_perfil():
    return render_template('gerenciar_perfil.html')


@app.route('/confirmar-agendamento')
def confirmar_agendamento():
    return render_template('confirmar_agendamento.html')

#ROTA QUEBRADA!!!!!!
@app.route('/<int:ser_id>/agendar', methods=['GET', 'POST'])
def agendar(ser_id):
    data = request.args.get('data')  # Pega a data do input

    horarios_disponiveis = [
        "08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00"
    ]
    
    agendamentos = []
    
    if data:
        cur = mysql.connection.cursor()
        query = """
            SELECT age_horario, cli_nome
            FROM tb_agendamento
            INNER JOIN tb_cliente ON age_cli_id = cli_id
            WHERE age_data = %s AND age_ser_id = %s
        """
        cur.execute(query, (data, ser_id))
        resultados = cur.fetchall()
        cur.close()

        # Mapeia horários ocupados
        ocupados = {r[0]: r[1] for r in resultados}

        for hora in horarios_disponiveis:
            if hora in ocupados:
                agendamentos.append({
                    "horario": hora,
                    "status": "Indisponível",
                    "cliente": ocupados[hora],
                    "disponivel": False
                })
            else:
                agendamentos.append({
                    "horario": hora,
                    "status": "Disponível",
                    "cliente": "",
                    "disponivel": True
                })
    
    return render_template('agendar.html', agendamentos=agendamentos, data=data)
