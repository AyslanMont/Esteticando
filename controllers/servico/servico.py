from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from esteticando.database.database import mysql

servico_bp = Blueprint('servico', __name__, url_prefix='/servico')

@servico_bp.route('/adicionar/<int:est_id>', methods=['GET', 'POST'])
@login_required
def adicionar_servico(est_id):
    if not hasattr(current_user, 'tipo_usuario') or current_user.tipo_usuario != 'profissional':
        flash('Apenas profissionais podem adicionar serviços.', 'danger')
        return redirect(url_for('auth.login'))

    try:
        with mysql.connection.cursor() as cur:
            cur.execute("""
                SELECT est_nome, est_dono_id 
                FROM tb_estabelecimento 
                WHERE est_id = %s
            """, (est_id,))
            estabelecimento = cur.fetchone()
            
            if not estabelecimento:
                flash("Estabelecimento não encontrado.", "danger")
                return redirect(url_for('estabelecimento.filtrar_estabelecimento'))

            if estabelecimento['est_dono_id'] != current_user.id:
                flash("Você não tem permissão para adicionar serviços a este estabelecimento.", "danger")
                return redirect(url_for('estabelecimento.perfil_estabelecimento', est_id=est_id))

            cur.execute("SELECT cat_id, cat_nome FROM tb_categoria")
            categorias = cur.fetchall()

            if request.method == 'POST':
                nome = request.form.get('nome')
                descricao = request.form.get('descricao')
                preco = request.form.get('preco')
                categoria_id = request.form.get('categoria')
                duracao = request.form.get('duracao')

                if not all([nome, descricao, preco, categoria_id, duracao]):
                    flash("Todos os campos são obrigatórios.", "warning")
                    return render_template('adicionar_servico.html', 
                                        est_id=est_id, 
                                        est_nome=estabelecimento['est_nome'], 
                                        categorias=categorias)

                try:
                    preco_float = float(preco)
                    duracao_int = int(duracao)
                    if preco_float <= 0 or duracao_int <= 0:
                        raise ValueError
                except ValueError:
                    flash("Valores inválidos para preço ou duração.", "warning")
                    return render_template('adicionar_servico.html', 
                                        est_id=est_id, 
                                        est_nome=estabelecimento['est_nome'], 
                                        categorias=categorias)

                cur.execute("""
                    INSERT INTO tb_servico 
                    (ser_nome, ser_descricao, ser_preco, ser_duracao, ser_est_id, ser_cat_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (nome, descricao, preco_float, duracao_int, est_id, categoria_id))
                
                mysql.connection.commit()
                flash("Serviço adicionado com sucesso!", "success")
                return redirect(url_for('estabelecimento.perfil_estabelecimento', est_id=est_id))

            return render_template('adicionar_servico.html', 
                                est_id=est_id, 
                                est_nome=estabelecimento['est_nome'], 
                                categorias=categorias)

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Erro ao processar solicitação: {str(e)}", "danger")
        return redirect(url_for('estabelecimento.perfil_estabelecimento', est_id=est_id))


@servico_bp.route('/funcionarios/<int:est_id>')
@login_required
def listar_funcionarios(est_id):
    try:
        with mysql.connection.cursor() as cur:
            cur.execute("SELECT est_dono_id FROM tb_estabelecimento WHERE est_id = %s", (est_id,))
            estabelecimento = cur.fetchone()
            
            if not estabelecimento:
                flash("Estabelecimento não encontrado.", "danger")
                return redirect(url_for('estabelecimento.filtrar_estabelecimento'))

            if estabelecimento['est_dono_id'] != current_user.id:
                flash("Apenas o dono pode ver os funcionários.", "danger")
                return redirect(url_for('estabelecimento.perfil_estabelecimento', est_id=est_id))

            cur.execute("""
                SELECT pro_id, pro_nome, pro_telefone
                FROM tb_profissional
                WHERE pro_est_id = %s
            """, (est_id,))
            funcionarios = cur.fetchall()

            cur.execute("SELECT est_nome FROM tb_estabelecimento WHERE est_id = %s", (est_id,))
            est_nome = cur.fetchone()['est_nome']

        return render_template('funcionarios.html', 
                            funcionarios=funcionarios, 
                            est_nome=est_nome, 
                            est_id=est_id)

    except Exception as e:
        flash(f"Erro ao carregar funcionários: {str(e)}", "danger")
        return redirect(url_for('estabelecimento.filtrar_estabelecimento'))


@servico_bp.route('/funcionarios/adicionar/<int:est_id>', methods=['GET', 'POST'])
@login_required
def adicionar_funcionario(est_id):
    try:
        with mysql.connection.cursor() as cur:
            cur.execute("SELECT est_dono_id, est_nome FROM tb_estabelecimento WHERE est_id = %s", (est_id,))
            estabelecimento = cur.fetchone()
            
            if not estabelecimento:
                flash("Estabelecimento não encontrado.", "danger")
                return redirect(url_for('estabelecimento.filtrar_estabelecimento'))

            if estabelecimento['est_dono_id'] != current_user.id:
                flash("Apenas o dono pode adicionar funcionários.", "danger")
                return redirect(url_for('estabelecimento.perfil_estabelecimento', est_id=est_id))

            if request.method == 'POST':
                nome = request.form.get('nome')
                telefone = request.form.get('telefone')

                if not nome or not telefone:
                    flash("Nome e telefone são obrigatórios.", "warning")
                    return render_template('adicionar_funcionario.html', 
                                        est_id=est_id, 
                                        est_nome=estabelecimento['est_nome'])

                cur.execute("""
                    INSERT INTO tb_profissional 
                    (pro_nome, pro_telefone, pro_est_id)
                    VALUES (%s, %s, %s)
                """, (nome, telefone, est_id))
                
                mysql.connection.commit()
                flash("Funcionário adicionado com sucesso!", "success")
                return redirect(url_for('servico.listar_funcionarios', est_id=est_id))

            return render_template('adicionar_funcionario.html', 
                                est_id=est_id, 
                                est_nome=estabelecimento['est_nome'])

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Erro ao adicionar funcionário: {str(e)}", "danger")
        return redirect(url_for('estabelecimento.perfil_estabelecimento', est_id=est_id))