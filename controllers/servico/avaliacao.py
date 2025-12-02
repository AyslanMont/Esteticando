from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from esteticando.database.database import mysql
from datetime import datetime

avaliacao_bp = Blueprint('avaliacao', __name__, url_prefix='/avaliacao')

# --- ROTA PARA REGISTRAR AVALIAÇÃO ---


@avaliacao_bp.route('/cadastrar', methods=['POST'])
@login_required
def cadastrar_avaliacao():
    nota = request.form.get("nota")
    comentario = request.form.get("comentario")
    ser_id = request.form.get("ser_id")
    age_id = request.form.get("agendamento_id")

    if not age_id:
        age_id = None

    if not nota:
        flash("Selecione uma nota para avaliar o serviço.", "danger")
        return redirect(request.referrer)

    try:
        with mysql.connection.cursor() as cur:
            cur.execute("""
            INSERT INTO tb_avaliacao
            (ava_dataCriacao, ava_nota, ava_comentario, ava_cli_id, ava_age_id)
            VALUES (CURDATE(), %s, %s, %s, %s)
""", (nota, comentario, current_user.id, age_id))

            mysql.connection.commit()

        flash("Avaliação registrada com sucesso!", "success")
        return redirect(request.referrer)

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Erro ao registrar avaliação: {e}", "danger")
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
