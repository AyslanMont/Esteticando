from flask import Blueprint, request, redirect, render_template, flash, url_for
from flask_login import login_required,current_user
from esteticando.database.database import mysql

# Cria um Blueprint para as rotas relacionadas a profissionais
profissional_bp = Blueprint('profissional', __name__, url_prefix="/profissional", template_folder="templates")

@profissional_bp.route('/editar_perfil', methods = ['GET','POST'])
@login_required
def editar_perfil():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        telefone = request.form['telefone']
        
        cur = mysql.connection.cusor()
        query_update = """
            UPDATE tb_profissional 
            SET  pro_nome = %s, pro_senha = %s, pro_telefone = %s
            WHERE pro_id = %s
        """
        cur.execute(query_update, (nome, senha, telefone, current_user.id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('profissional.editar_perfil'))
    
    cur = mysql.connection.cursor()
    query = "SELECT pro_nome, pro_cpf, pro_email, pro_senha, pro_telefone FROM tb_profissional WHERE pro_id = %s"
    cur.execute(query,(current_user.id,))
    user = cur.fetchone()
    cur.close()

    return render_template('perfil_profissional.html', user = user)