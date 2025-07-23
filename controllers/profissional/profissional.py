from flask import Blueprint, request, redirect, render_template, flash, url_for
from flask_login import login_required, current_user
from esteticando.database.database import mysql
from werkzeug.security import generate_password_hash, check_password_hash

profissional_bp = Blueprint('profissional', __name__, url_prefix="/profissional", template_folder="templates")

@profissional_bp.route('/perfil', methods=['GET'])
@login_required
def perfil():
    if not hasattr(current_user, 'tipo_usuario') or current_user.tipo_usuario != 'profissional':
        flash('Você precisa estar logado como profissional para cadastrar um estabelecimento.', 'danger')
        return redirect(url_for('estabelecimento.filtrar_estabelecimento'))
    
    pro_id = current_user.id
    cur = None

    dados_user = None
    estabelecimentos = []

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            pro_id, pro_nome, pro_email, pro_telefone,
            est_id, est_nome, est_email, est_descricao
        FROM tb_profissional
        LEFT JOIN tb_estabelecimento ON est_dono_id = pro_id
        WHERE pro_id = %s
    """, (current_user.id,))
    resultados = cur.fetchall()
    cur.close()

    if resultados:
        dados_user = {
            'pro_id': resultados[0]['pro_id'],
            'pro_nome': resultados[0]['pro_nome'],
            'pro_email': resultados[0]['pro_email'],
            'pro_telefone': resultados[0]['pro_telefone']
        }
        estabelecimentos = [
            {
                'est_id': row['est_id'],
                'est_nome': row['est_nome'],
                'est_email': row['est_email'],
                'est_descricao': row['est_descricao']
            }
            for row in resultados if row['est_id'] is not None
        ]

    return render_template('perfil.html', user=dados_user, estabelecimentos=estabelecimentos)

@profissional_bp.route('/editar_perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        # Busca os dados atuais
        cur.execute("""
            SELECT pro_nome, pro_senha, pro_telefone 
            FROM tb_profissional 
            WHERE pro_id = %s
        """, (current_user.id,))
        dados_atuais = cur.fetchone()

        if not dados_atuais:
            flash('Usuário não encontrado', 'danger')
            cur.close()
            return redirect(url_for('profissional.editar_perfil'))

        nome = request.form.get('nome', dados_atuais['pro_nome'])
        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('senha')
        check_senha = request.form.get('check_senha')
        telefone = request.form.get('telefone', dados_atuais['pro_telefone'])

        try:
            senha_db = dados_atuais['pro_senha']

            # Se usuário preencheu nova senha
            if nova_senha:
                if not check_password_hash(senha_db, senha_atual):
                    flash('Senha atual incorreta', 'danger')
                    return redirect(url_for('profissional.editar_perfil'))

                if nova_senha != check_senha:
                    flash('As novas senhas não coincidem', 'danger')
                    return redirect(url_for('profissional.editar_perfil'))

                senha_hash = generate_password_hash(nova_senha)
            else:
                senha_hash = senha_db  # Mantém senha antiga

            # Atualiza dados no banco
            cur.execute("""
                UPDATE tb_profissional 
                SET pro_nome = %s, pro_senha = %s, pro_telefone = %s
                WHERE pro_id = %s
            """, (nome, senha_hash, telefone, current_user.id))
            mysql.connection.commit()
            flash('Perfil atualizado com sucesso', 'success')

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao atualizar perfil: {str(e)}', 'danger')
        finally:
            cur.close()

        return redirect(url_for('profissional.editar_perfil'))

    # Método GET: Carrega dados para o formulário
    cur.execute("""
        SELECT pro_nome, pro_telefone 
        FROM tb_profissional 
        WHERE pro_id = %s
    """, (current_user.id,))
    user = cur.fetchone()
    cur.close()

    return render_template('perfil_editar.html', user=user)


@profissional_bp.route('/disponibilidade', methods=['GET','POST'])
def disponibilidade():
    if not hasattr(current_user, 'tipo_usuario') or current_user.tipo_usuario != 'profissional':
        return redirect(url_for('index'))  # ou outra rota pública

    if request.method == 'POST':
        dia = request.form.get('dia')
        horario_inicio = request.form.get('horario_inicio')
        horario_fim = request.form.get('horario_fim')

        if not dia or not horario_inicio or not horario_fim:
            flash('Preencha todos os campos.', 'warning')
            return redirect(url_for('profissional.disponibilidade'))

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO tb_disponibilidade_profissional 
                (dip_pro_id, dip_dia, dip_horarioInicio, dip_horarioFim)
                VALUES (%s, %s, %s, %s)
            """, (current_user.id, dia, horario_inicio, horario_fim))
            mysql.connection.commit()
            flash('Disponibilidade cadastrada com sucesso!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao cadastrar: {str(e)}', 'danger')
        finally:
            cur.close()

        return redirect(url_for('profissional.disponibilidade'))

    return render_template('disponibilidade.html')

@profissional_bp.route('/agendamentos', methods=['GET','POST'])
def agendamentos():
    pass

