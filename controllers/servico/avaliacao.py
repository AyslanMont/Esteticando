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
        print("DEBUG >>> SERVICO RECEBIDO:", request.form.get("ser_id"))
        with mysql.connection.cursor() as cur:
            cur.execute("""
                INSERT INTO tb_avaliacao (ava_dataCriacao, ava_nota, ava_comentario, ava_cli_id, ava_ser_id)
                VALUES (CURDATE(), %s, %s, %s, %s)
            """, (nota, comentario, current_user.id, ser_id))

            mysql.connection.commit()

        flash("Avaliação registrada com sucesso!", "success")
        return redirect(request.referrer)

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Erro ao registrar avaliação: {e}", "danger")
        return redirect(request.referrer)


# --- ROTA PARA LISTAR AVALIAÇÕES DE UM SERVIÇO ---
@avaliacao_bp.route('/listar/<int:est_id>')
def listar_avaliacoes(est_id):
    try:
        with mysql.connection.cursor(dictionary=True) as cur:  # importante: dictionary=True
            # Média e total
            cur.execute("""
                SELECT AVG(a.ava_nota) AS media, COUNT(*) AS total
                FROM tb_avaliacao a
                JOIN tb_servico s ON a.ava_ser_id = s.ser_id
                WHERE s.ser_est_id = %s
            """, (est_id,))
            avaliacoes = cur.fetchone()
            media_avaliacao = float(avaliacoes['media'] or 0)
            qtd_avaliacoes = int(avaliacoes['total'] or 0)

            # Lista completa
            cur.execute("""
                SELECT 
                    a.ava_nota,
                    a.ava_comentario,
                    cli.cli_nome,
                    s.ser_nome
                FROM tb_avaliacao a
                JOIN tb_cliente cli ON a.ava_cli_id = cli.cli_id
                JOIN tb_servico s ON a.ava_ser_id = s.ser_id
                WHERE s.ser_est_id = %s
                ORDER BY a.ava_id DESC
            """, (est_id,))
            lista_avaliacoes = cur.fetchall()

        return render_template("estabelecimento.html",
                               media_avaliacao=media_avaliacao,
                               qtd_avaliacoes=qtd_avaliacoes,
                               lista_avaliacoes=lista_avaliacoes)

    except Exception as e:
        flash(f"Erro ao carregar avaliações: {e}", "danger")
        return redirect(request.referrer)
