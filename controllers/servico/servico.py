from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from esteticando.database.database import mysql

servico_bp = Blueprint('servico', __name__, url_prefix='/servico')



@servico_bp.route('/adicionar/<int:est_id>', methods=['GET', 'POST'])
@login_required
def adicionar_servico(est_id):
    with mysql.connection.cursor() as cur:
        # Buscar o nome do estabelecimento
        cur.execute("SELECT est_nome FROM tb_estabelecimento WHERE est_id = %s", (est_id,))
        est = cur.fetchone()
        if not est:
            flash("Estabelecimento não encontrado.", "danger")
            return redirect(url_for('estabelecimento.filtrar_estabelecimento'))
        est_nome = est['est_nome']

        # Verificar se o profissional está vinculado ao estabelecimento
        cur.execute("SELECT pro_id FROM tb_profissional WHERE pro_est_id = %s LIMIT 1", (est_id,))
        dono = cur.fetchone()

        # Carregar categorias disponíveis
        cur.execute("SELECT cat_id, cat_nome FROM tb_categoria")
        categorias = cur.fetchall()

    if not dono:
        flash("Estabelecimento sem profissional associado.", "danger")
        return redirect(url_for('estabelecimento.filtrar_estabelecimento'))

    if dono['pro_id'] != current_user.id:
        flash("Você não tem permissão para adicionar serviços a este estabelecimento.", "danger")
        return redirect(url_for('estabelecimento.perfil_estabelecimento', est_id=est_id))

    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        preco = request.form.get('preco')
        categoria_id = request.form.get('categoria')

        if not nome or not descricao or not preco or not categoria_id:
            flash("Todos os campos são obrigatórios.", "warning")
            return redirect(url_for('servico.adicionar_servico', est_id=est_id))

        try:
            preco_float = float(preco)
            categoria_id = int(categoria_id)
        except ValueError:
            flash("Preço ou categoria inválidos.", "warning")
            return redirect(url_for('servico.adicionar_servico', est_id=est_id))

        with mysql.connection.cursor() as cur:
            cur.execute("""
                INSERT INTO tb_servico (ser_nome, ser_descricao, ser_preco, ser_est_id, ser_cat_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (nome, descricao, preco_float, est_id, categoria_id))
            mysql.connection.commit()
            last_id = cur.lastrowid

        flash("Serviço adicionado com sucesso!", "success")
        return redirect(url_for('agendamento.agendar', ser_id=last_id))

    return render_template('adicionar_servico.html',est_id=est_id,est_nome=est_nome,categorias=categorias)


