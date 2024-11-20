from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("dashboard.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/gerenciar_perfil')
def gerenciar_perfil():
    return render_template('gerenciar_perfil.html')

@app.route('/estabelecimento')
def estabelecimento():
    return render_template ('estabelecimento.html')

@app.route('/resu_estabelecimento')
def resu_estabelecimento():
    return render_template ('resu_estabelecimento.html')

@app.route('/dentro_estabelecimento')
def dentro_estabelecimento():
    return render_template('dentro_estabelecimento.html')

@app.route('/confirmar_agendamento')
def confirmar_agendamento():
    return render_template ('confirmar_agendamento.html')

@app.route('/agendar')
def agendar():
    return render_template ('agendar.html')