from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required,current_user
from esteticando.database.database import mysql
from datetime import datetime, date

agendamento_bp = Blueprint('agendamento', __name__, url_prefix='/agendamento')

HORARIOS_DISPONIVEIS = [
    "08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00"
]

@agendamento_bp.route('/agendar/<int:ser_id>', methods=['GET', 'POST'])
@agendamento_bp.route('/agendar/<int:ser_id>/<data>', methods=['GET', 'POST'])
def agendar(ser_id, data=None):
    if request.method == 'POST':
        selected_date = request.form.get('data')
        if not selected_date:
            flash("Selecione uma data válida.", "warning")
            return redirect(url_for('agendamento.agendar', ser_id=ser_id))
        return redirect(url_for('agendamento.agendar', ser_id=ser_id, data=selected_date))

    if not data:
        data = date.today().isoformat()

    with mysql.connection.cursor() as cur:
        cur.execute("""
            SELECT age_id, TIME_FORMAT(age_horario, '%%H:%%i') AS horario, cli_nome, age_cli_id
            FROM tb_agendamento
            JOIN tb_cliente ON age_cli_id = cli_id
            WHERE DATE(age_data) = %s AND age_ser_id = %s
        """, (data, ser_id))
        resultados = cur.fetchall()

    ocupados = {}
    for row in resultados:
        if isinstance(row, dict):
            horario = row['horario']
            ocupados[horario] = {
                'cliente_nome': row['cli_nome'],
                'cli_id': row['age_cli_id'],
                'age_id': row['age_id']
            }
        else:
            horario, nome, cli_id, age_id = row
            ocupados[horario] = {
                'cliente_nome': nome,
                'cli_id': cli_id,
                'age_id': age_id
            }

    agendamentos = []
    for hora in HORARIOS_DISPONIVEIS:
        ocupado = ocupados.get(hora)
        agendamentos.append({
            'hora': hora,
            'status': 'Indisponível' if ocupado else 'Disponível',
            'cliente_nome': ocupado['cliente_nome'] if ocupado else None,
            'disponivel': not ocupado,
            'proprio_agendamento': ocupado and ocupado['cli_id'] == current_user.id,
            'agendamento_id': ocupado['age_id'] if ocupado else None
        })

    return render_template('agendar.html',
                           ser_id=ser_id,
                           data=data,
                           agendamentos=agendamentos)


@agendamento_bp.route('/confirmar_agendamento', methods=['POST'])
@login_required
def confirmar_agendamento():
    form = request.form.to_dict()
    ser_id = form.get('ser_id')
    data = form.get('data')
    horario = form.get('horario')

    if not ser_id or not data or not horario:
        flash("Dados insuficientes.", "danger")
        return redirect(url_for('agendamento.agendar',
                                ser_id=int(ser_id) if ser_id else 0,
                                data=data or date.today().isoformat()))

    ser_id = int(ser_id)
    horario_completo = horario + ":00"
    try:
        with mysql.connection.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS total
                FROM tb_agendamento WHERE age_cli_id= %s AND DATE(age_data) = %s
            """, (current_user.id, data))
            res = cur.fetchone()
            if res['total'] >= 2:
                flash("Você já possui 2 agendamentos para este dia.", "danger")
                return redirect(url_for('agendamento.agendar', ser_id=ser_id, data=data))            

            cur.execute("""
                SELECT 1 FROM tb_agendamento
                WHERE age_ser_id=%s AND DATE(age_data)=%s AND age_horario=%s
            """, (ser_id, data, horario_completo))
            if cur.fetchone():
                flash("Este horário já está ocupado.", "danger")
                return redirect(url_for('agendamento.agendar',
                                        ser_id=ser_id, data=data))

            cur.execute("""
                SELECT ser_preco, ser_duracao, ser_est_id 
                FROM tb_servico 
                WHERE ser_id=%s
            """, (ser_id,))
            serv = cur.fetchone()
            preco = serv['ser_preco']
            duracao = serv['ser_duracao']
            est_id = serv['ser_est_id']

            cur.execute("""
                SELECT pro_id 
                FROM tb_profissional 
                WHERE pro_est_id=%s 
                LIMIT 1
            """, (est_id,))
            prof = cur.fetchone()
            pro_id = prof['pro_id'] if prof else None

            cur.execute("""
                INSERT INTO tb_agendamento (
                  age_ser_id, age_cli_id, age_data, age_horario,
                  age_dataCriacao, age_valorTotal, age_quantidade,
                  age_duracao, age_status, age_pro_id
                ) VALUES (
                  %s, %s, %s, %s,
                  NOW(), %s, 1,
                  %s, 'Agendado', %s
                )
            """, (ser_id, current_user.id, data, horario_completo,
                  preco, duracao, pro_id))

        mysql.connection.commit()
        flash(f"Agendamento confirmado para {data} às {horario}.", "success")

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Erro ao confirmar agendamento: {e}", "danger")

    return redirect(url_for('agendamento.agendar', ser_id=ser_id, data=data))


@agendamento_bp.route('/cancelar_agendamento', methods=['POST'])
@login_required
def cancelar_agendamento():
    form = request.form.to_dict()
    agendamento_id = form.get('agendamento_id')

    if not agendamento_id:
        flash("ID de agendamento inválido.", "danger")
        return redirect(url_for('estabelecimento.filtrar_estabelecimento'))

    try:
        with mysql.connection.cursor() as cur:
            cur.execute("""
                DELETE FROM tb_agendamento 
                WHERE age_id=%s AND age_cli_id=%s
            """, (agendamento_id, current_user.id))
            mysql.connection.commit()

        flash("Agendamento cancelado com sucesso.", "success")

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Erro ao cancelar agendamento: {e}", "danger")

    return redirect(url_for('estabelecimento.filtrar_estabelecimento'))