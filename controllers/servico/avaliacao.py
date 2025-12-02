from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from esteticando.database.database import mysql
from datetime import datetime

avaliacao_bp = Blueprint('avaliacao', __name__, url_prefix='/avaliacao')

# --- ROTA PARA REGISTRAR AVALIAÇÃO ---
@avaliacao_bp.route('/cadastrar', methods=['POST'])
@login_required
def cadastrar_avaliacao():
    agendamento_id = request.form.get('agendamento_id')
    nota = request.form.get('nota')
    comentario = request.form.get('comentario', '').strip()

    if not agendamento_id or not nota:
        flash("Preencha todos os campos obrigatórios.", "danger")
        return redirect(request.referrer)

    nota = int(nota)

    # valida nota
    if nota < 1 or nota > 5:
        flash("A nota deve ser entre 1 e 5 estrelas.", "danger")
        return redirect(request.referrer)

    try:
        with mysql.connection.cursor() as cur:

            # verifica se o agendamento existe e pertence ao cliente
            cur.execute("""
                SELECT age_id, age_cli_id, age_status 
                FROM tb_agendamento 
                WHERE age_id=%s
            """, (agendamento_id,))
            agendamento = cur.fetchone()

            if not agendamento:
                flash("Agendamento não encontrado.", "danger")
                return redirect(request.referrer)

            if agendamento["age_cli_id"] != current_user.id:
                flash("Você não pode avaliar um agendamento que não lhe pertence.", "danger")
                return redirect(request.referrer)

            # (opcional) só permite avaliar agendamento concluído
            # if agendamento["age_status"] != "Concluído":
            #     flash("Você só pode avaliar serviços concluídos.", "warning")
            #     return redirect(request.referrer)

            # verificar se o usuário já avaliou esse agendamento
            cur.execute("""
                SELECT ava_id 
                FROM tb_avaliacao 
                WHERE ava_age_id=%s AND ava_cli_id=%s
            """, (agendamento_id, current_user.id))
            avaliacao_existente = cur.fetchone()

            if avaliacao_existente:
                flash("Você já avaliou este atendimento.", "warning")
                return redirect(request.referrer)

            # inserir avaliação
            cur.execute("""
                INSERT INTO tb_avaliacao 
                    (ava_nota, ava_comentario, ava_dataCriacao, 
                     ava_cli_id, ava_age_id)
                VALUES (%s, %s, NOW(), %s, %s)
            """, (nota, comentario, current_user.id, agendamento_id))

            mysql.connection.commit()

        flash("Avaliação registrada com sucesso!", "success")

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Erro ao enviar avaliação: {e}", "danger")

    return redirect(request.referrer)


# --- ROTA PARA LISTAR AVALIAÇÕES DE UM SERVIÇO ---
@avaliacao_bp.route('/listar/<int:servico_id>')
def listar_avaliacoes(servico_id):
    try:
        with mysql.connection.cursor() as cur:
            cur.execute("""
                SELECT 
                    ava_nota, ava_comentario, ava_dataCriacao,
                    cli_nome
                FROM tb_avaliacao
                JOIN tb_agendamento ON ava_age_id = age_id
                JOIN tb_cliente ON ava_cli_id = cli_id
                WHERE age_ser_id=%s
                ORDER BY ava_dataCriacao DESC
            """, (servico_id,))
            avaliacoes = cur.fetchall()

        return render_template("avaliacoes.html", avaliacoes=avaliacoes)

    except Exception as e:
        flash(f"Erro ao carregar avaliações: {e}", "danger")
        return redirect(request.referrer)
