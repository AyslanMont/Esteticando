from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required,current_user
from esteticando.database.database import mysql

estabelecimento_bp = Blueprint('estabelecimento', __name__, url_prefix='/estabelecimento', template_folder='templates')


#rapaz não sei para que serve essa rota
@estabelecimento_bp.route('/')
def estabelecimento():
    return render_template('estabelecimento.html')



@estabelecimento_bp.route('/resu_estabelecimento')
def resu_estabelecimento():
    ordem = request.args.get('ordem', 'asc')
    nome_filtro = request.args.get('nome', '')

    query = """SELECT est_nome, est_descricao, est_email, est_telefone,end_rua, end_numero, end_bairro, end_cidade, end_estado
        FROM tb_estabelecimento LEFT JOIN tb_endereco_estabelecimento end ON est_id = end_est_id
        WHERE est_nome LIKE %s ORDER BY est_nome {} """.format("ASC" if ordem == "asc" else "DESC")
    cursor = mysql.connection.cursor()
    cursor.execute(query, (f"%{nome_filtro}%",))
    dados = cursor.fetchall()
    cursor.close()
    
    return render_template('resu_estabelecimento.html',dados=dados, ordem=ordem, nome_filtro=nome_filtro)


#não esta finalizada mas ja da pra ter uma noção, falta a verificação de profissional
@estabelecimento_bp.route('/dentro_estabelecimento')
def dentro_estabelecimento():
    cur = mysql.connection.cursor()
    
    
    cur.execute("SELECT est_nome FROM tb_estabelecimento ORDER BY est_id DESC LIMIT 1")
    estabelecimento = cur.fetchone()

    cur.execute("SELECT ser_nome, ser_preco FROM tb_servico WHERE ser_est_id = (SELECT est_id FROM tb_estabelecimento ORDER BY est_id DESC LIMIT 1)")
    cortes = cur.fetchall()
    cur.close()

    if estabelecimento:
        return render_template('dentro_estabelecimento.html', estabelecimento=estabelecimento, cortes=cortes)
    else:
        flash('Nenhum estabelecimento encontrado!', 'danger')
        return redirect(url_for('estabelecimento.cadastrar_estabelecimento'))



#esta bugado, não esta adcionando nem listando
@estabelecimento_bp.route('/adicionar_servico', methods=['POST'])
def adicionar_servico():
    if request.method == 'POST':
        servico_nome = request.form['servico_nome']
        servico_preco = request.form['servico_preco']

        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO tb_servico (ser_nome, ser_preco, ser_est_id) "
                "VALUES (%s, %s, %s)",
                (servico_nome, servico_preco, current_user.est_id)
            )
            mysql.connection.commit()
            flash('Serviço adicionado com sucesso!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao adicionar serviço: {str(e)}', 'danger')
        finally:
            cur.close()

        return redirect(url_for('estabelecimento.dentro_estabelecimento'))



@estabelecimento_bp.route('/cadastrar_estabelecimento', methods=['POST', 'GET'])
def cadastrar_estabelecimento():
    if request.method == 'POST':
        est_nome = request.form['est_nome']
        est_descricao = request.form['est_descricao']
        est_cnpj = request.form['est_cnpj']
        est_email = request.form['est_email']
        est_telefone = request.form['est_telefone']
        est_cat_id = request.form['est_cat_id']
        
        # Dados do endereço
        end_numero = request.form['end_numero']
        end_complemento = request.form['end_complemento']
        end_bairro = request.form['end_bairro']
        end_rua = request.form['end_rua']
        end_cidade = request.form['end_cidade']
        end_estado = request.form['end_estado']
        end_cep = request.form['end_cep']

        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO tb_estabelecimento (est_dataCriacao, est_nome, est_descricao, est_cnpj, est_email, est_telefone, est_cat_id) "
                "VALUES (CURDATE(), %s, %s, %s, %s, %s, %s)",
                (est_nome, est_descricao, est_cnpj, est_email, est_telefone, est_cat_id)
            )
            mysql.connection.commit()
            

            est_id = cur.lastrowid #pega o ultimo id gerado pelo bd            
            cur.execute(
                "INSERT INTO tb_endereco_estabelecimento (end_numero, end_complemento, end_bairro, end_rua, end_cidade, end_estado, end_cep, end_est_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (end_numero, end_complemento, end_bairro, end_rua, end_cidade, end_estado, end_cep, est_id)
            )
            mysql.connection.commit()

            flash('Estabelecimento cadastrado com sucesso!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao cadastrar estabelecimento: {str(e)}', 'danger')
        finally:
            cur.close()

        return redirect(url_for('estabelecimento.dentro_estabelecimento'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT cat_id, cat_nome FROM tb_categoria")
    categorias = cur.fetchall()
    cur.close()

    return render_template('cadastrar_estabelecimento.html', categorias=categorias)
