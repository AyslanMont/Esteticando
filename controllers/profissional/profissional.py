from flask import Blueprint, request, redirect, render_template, flash, url_for
from flask_login import login_required,current_user
from esteticando.database.database import mysql
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash


# Cria um Blueprint para as rotas relacionadas a profissionais
profissional_bp = Blueprint('profissional', __name__, url_prefix="/profissional", template_folder="templates")

@profissional_bp.route('/editar_perfil', methods = ['GET','POST'])
@login_required
def editar_perfil():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT pro_nome, pro_senha, pro_telefone 
            FROM tb_profissional 
            WHERE pro_id = %s
        """, (current_user.id,))
        dados_atuais = cur.fetchone()

        if not dados_atuais:
            flash('Usuário não encontrado', 'danger')
            return redirect(url_for('profissional.editar_perfil'))
        
        nome = request.form['nome', dados_atuais[0]]
        senha_atual = request.form['senha_atual']
        senha = request.form['senha']
        check_senha = request.form['check_senha']
        telefone = request.form['telefone', dados_atuais]
        
        try:
            cur = mysql.connection.cursor()
            query = "SELECT pro_senha FROM tb_profissional WHERE pro_id = %s"
            cur.execute(query,(current_user))
            resultado = cur.fetchone() 

            if not resultado:
                flash('usuario não encontrado', 'danger')
                return redirect(url_for(profissional.editar_perfil))
            
            senha_db = resultado[0]

            if senha:
                if not check_password_hash(senha_db, senha_atual):
                    flash('Senha atual incorreta', 'danger')
                    return redirect(url_for('profissional.editar_perfil'))
                
                if senha != check_senha:
                    flash('As novas senhas não coincidem', 'danger')
                    return redirect(url_for('profissional.editar_perfil'))
                
                senha_hash = generate_password_hash(check_senha)
            else:
                senha_hash = senha_db  

            cur = mysql.connection.cusor()
            query_update = """
                UPDATE tb_profissional 
                SET  pro_nome = %s, pro_senha = %s, pro_telefone = %s
                WHERE pro_id = %s
            """
            cur.execute(query_update, (nome, senha_hash, telefone, current_user.id))
            mysql.connection.commit()
            cur.close()
            flash('perfil atualizado com sucesso', 'success')
        
         
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao atualizar perfil: {str(e)}', 'danger')
            
        finally:
            cur.close()

        return redirect(url_for('profissional.editar_perfil'))
    
    cur = mysql.connection.cursor()
    query = "SELECT pro_nome, pro_cpf, pro_email, pro_senha, pro_telefone FROM tb_profissional WHERE pro_id = %s"
    cur.execute(query,(current_user.id,))
    user = cur.fetchone()
    cur.close()

    return render_template('perfil_profissional.html', user = user)