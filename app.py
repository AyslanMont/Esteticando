from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("login.html")

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
