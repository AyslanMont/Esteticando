from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required,current_user
from esteticando.database.database import mysql
from datetime import datetime, date

estabelecimento_bp = Blueprint('estabelecimento', __name__, url_prefix='/estabelecimento', template_folder='templates')



@estabelecimento_bp.route('/')
def estabelecimento():
    return render_template('estabelecimento.html')



@estabelecimento_bp.route('/filtrar_estabelecimento', methods=['GET', 'POST'])
def filtrar_estabelecimento():

    result_est = []
    
    if request.method == 'POST':
        end_estado = request.form.get('estado', '').strip()
        end_cidade = request.form.get('cidade', '').strip()
        end_bairro = request.form.get('bairro', '').strip()
        est_nome = request.form.get('nome', '').strip()

        if not end_estado:
            flash('Estado é um campo obrigatório.', 'warning')
            return render_template('filtrar_estabelecimento.html', result_est=result_est)

        query_est = """
            SELECT est_id, est_nome, est_descricao, est_email, est_telefone, end_rua, end_numero, end_bairro, end_cidade, end_estado 
            FROM tb_endereco_estabelecimento 
            JOIN tb_estabelecimento ON est_id = end_est_id 
            WHERE end_estado = %s
        """
        parametros = [end_estado]

        if end_cidade:
            query_est += " AND end_cidade = %s"
            parametros.append(end_cidade)
        
        if end_bairro:
            query_est += " AND end_bairro = %s"
            parametros.append(end_bairro)

        if est_nome:
            query_est += " AND est_nome LIKE %s"
            parametros.append(f"%{est_nome}%")

        cur = mysql.connection.cursor()
        try:
            cur.execute(query_est, tuple(parametros))
            result_est = cur.fetchall()
        finally:
            cur.close()

        if not result_est:
            flash('Nenhum estabelecimento encontrado com esses filtros.', 'info')

    else:  # Método GET
        cur = mysql.connection.cursor()
        try:
            query = """
                SELECT est_id, est_nome, est_descricao, est_email, est_telefone, end_rua, end_numero, end_bairro, end_cidade, end_estado
                FROM tb_endereco_estabelecimento 
                JOIN tb_estabelecimento ON est_id = end_est_id 
                ORDER BY est_nome
                LIMIT 20
            """
            cur.execute(query)
            result_est = cur.fetchall()
        finally:
            cur.close()

    return render_template('filtrar_estabelecimento.html', result_est=result_est)





@estabelecimento_bp.route('/estabelecimento/<int:est_id>/servicos')
@login_required
def perfil_estabelecimento(est_id):
    cur = mysql.connection.cursor()
    query_servicos = """
        SELECT est_nome, ser_nome, ser_preco, ser_id 
        FROM tb_estabelecimento 
        JOIN tb_servico ON ser_est_id = est_id
        WHERE est_id = %s
    """
    cur.execute(query_servicos, (est_id,))
    servicos = cur.fetchall()
    cur.close()
    # Verifica se não há serviços
    if not servicos:
        return render_template('selecionar_servico.html', servicos=servicos, est_id=est_id, mensagem="Esse estabelecimento não tem serviços disponíveis.")

    data_atual = datetime.now().strftime('%Y-%m-%d') 
    
    return render_template('selecionar_servico.html', servicos=servicos, data=data_atual, est_id=est_id)



HORARIOS_DISPONIVEIS = [
    "08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00"
]

#primeira rota serve para carregar a pagina sem data
@estabelecimento_bp.route('/agendar/<int:ser_id>', methods=['GET', 'POST'])
#segunda rota serve para carregar a lista de horários já filtrada pela data selecionada
@estabelecimento_bp.route('/agendar/<int:ser_id>/<data>', methods=['GET', 'POST'])

def agendar(ser_id, data=None):
    if request.method == 'POST':
        selected_date = request.form.get('data')
        if not selected_date:
            flash("Selecione uma data válida.", "warning")
            return redirect(url_for('estabelecimento.agendar', ser_id=ser_id))
        return redirect(url_for('estabelecimento.agendar', ser_id=ser_id, data=selected_date))

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


@estabelecimento_bp.route('/confirmar_agendamento', methods=['POST'])
@login_required
def confirmar_agendamento():
    form = request.form.to_dict()
    ser_id = form.get('ser_id')
    data = form.get('data')
    horario = form.get('horario')

    if not ser_id or not data or not horario:
        flash("Dados insuficientes.", "danger")
        return redirect(url_for('estabelecimento.agendar',
                                ser_id=int(ser_id) if ser_id else 0,
                                data=data or date.today().isoformat()))

    ser_id = int(ser_id)
    horario_completo = horario + ":00"
    try:
        with mysql.connection.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS total
                FROM tb_agendamento WHERE age_cli_id= %s AND DATE (age_data) = %s """, (current_user.id, data))
            res = cur.fetchone()
            if res['total'] >= 2:
                flash("Você já possui 2 agendamentos para este dia.", "danger")
                return redirect(url_for('estabelecimento.agendar', ser_id=ser_id, data=data))            

            # Checa conflito
            cur.execute("""
                SELECT 1 FROM tb_agendamento
                WHERE age_ser_id=%s AND DATE(age_data)=%s AND age_horario=%s
            """, (ser_id, data, horario_completo))
            if cur.fetchone():
                flash("Este horário já está ocupado.", "danger")
                return redirect(url_for('estabelecimento.agendar',
                                        ser_id=ser_id, data=data))

            # Busca dados do serviço
            cur.execute("""
                SELECT ser_preco, ser_duracao, ser_est_id 
                FROM tb_servico 
                WHERE ser_id=%s
            """, (ser_id,))
            serv = cur.fetchone()
            preco = serv['ser_preco']
            duracao = serv['ser_duracao']
            est_id = serv['ser_est_id']

            # Busca profissional
            cur.execute("""
                SELECT pro_id 
                FROM tb_profissional 
                WHERE pro_est_id=%s 
                LIMIT 1
            """, (est_id,))
            prof = cur.fetchone()
            pro_id = prof['pro_id'] if prof else None

            # Insere agendamento
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

    return redirect(url_for('estabelecimento.agendar', ser_id=ser_id, data=data))


@estabelecimento_bp.route('/cancelar_agendamento', methods=['POST'])
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








@estabelecimento_bp.route('/cadastrar_estabelecimento', methods=['POST', 'GET'])
@login_required
def cadastrar_estabelecimento():
    # Verifica se o usuário logado é profissional
    if getattr(current_user, 'tipo_usuario', None) != 'profissional':
        flash('Você precisa estar logado como profissional para cadastrar um estabelecimento.', 'danger')
        return redirect(url_for('auth.login'))

    pro_id = current_user.id  # pega o id do profissional logado

    if request.method == 'POST':
        try:
            required_fields = [
                'est_nome', 'est_descricao', 'est_cnpj', 'est_email',
                'est_telefone', 'est_cat_id', 'end_numero', 'end_bairro',
                'end_rua', 'end_cidade', 'end_estado', 'end_cep'
            ]
            
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'O campo {field} é obrigatório!', 'danger')
                    return redirect(url_for('estabelecimento.cadastrar_estabelecimento'))

            est_data = {
                'nome': request.form['est_nome'].strip(),
                'descricao': request.form['est_descricao'].strip(),
                'cnpj': ''.join(filter(str.isdigit, request.form['est_cnpj'])),
                'email': request.form['est_email'].strip().lower(),
                'telefone': ''.join(filter(str.isdigit, request.form['est_telefone'])),
                'cat_id': int(request.form['est_cat_id'])
            }

            end_data = {
                'numero': request.form['end_numero'].strip(),
                'complemento': request.form.get('end_complemento', '').strip(),
                'bairro': request.form['end_bairro'].strip(),
                'rua': request.form['end_rua'].strip(),
                'cidade': request.form['end_cidade'].strip(),
                'estado': request.form['end_estado'].strip().upper(),
                'cep': ''.join(filter(str.isdigit, request.form['end_cep']))
            }

            if len(est_data['cnpj']) != 14:
                flash('CNPJ deve conter 14 dígitos', 'danger')
                return redirect(url_for('estabelecimento.cadastrar_estabelecimento'))

            if len(end_data['cep']) != 8:
                flash('CEP deve conter 8 dígitos', 'danger')
                return redirect(url_for('estabelecimento.cadastrar_estabelecimento'))

            cur = mysql.connection.cursor()

            cur.execute("SELECT est_id FROM tb_estabelecimento WHERE est_cnpj = %s", (est_data['cnpj'],))
            if cur.fetchone():
                flash('CNPJ já cadastrado!', 'danger')
                return redirect(url_for('estabelecimento.cadastrar_estabelecimento'))

            # Insere estabelecimento
            cur.execute(
                """INSERT INTO tb_estabelecimento 
                (est_dataCriacao, est_nome, est_descricao, est_cnpj, est_email, est_telefone, est_cat_id) 
                VALUES (CURDATE(), %s, %s, %s, %s, %s, %s)""",
                (est_data['nome'], est_data['descricao'], est_data['cnpj'], 
                 est_data['email'], est_data['telefone'], est_data['cat_id'])
            )
            mysql.connection.commit()
            est_id = cur.lastrowid

            # Insere endereço
            cur.execute(
                """INSERT INTO tb_endereco_estabelecimento 
                (end_numero, end_complemento, end_bairro, end_rua, end_cidade, end_estado, end_cep, end_est_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (end_data['numero'], end_data['complemento'], end_data['bairro'], 
                 end_data['rua'], end_data['cidade'], end_data['estado'], 
                 end_data['cep'], est_id)
            )
            mysql.connection.commit()

            # Atualiza o profissional logado para referenciar o estabelecimento cadastrado
            cur.execute(
                "UPDATE tb_profissional SET pro_est_id = %s WHERE pro_id = %s",
                (est_id, pro_id)
            )
            mysql.connection.commit()

            flash('Estabelecimento cadastrado com sucesso!', 'success')
            return redirect(url_for('estabelecimento.filtrar_estabelecimento', est_id=est_id))

        except ValueError as e:
            flash('Dados inválidos fornecidos!', 'danger')
            return redirect(url_for('estabelecimento.cadastrar_estabelecimento'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao cadastrar estabelecimento: {str(e)}', 'danger')
            return redirect(url_for('estabelecimento.cadastrar_estabelecimento'))
        finally:
            cur.close() if 'cur' in locals() else None

    # GET request: carregar form
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT cat_id, cat_nome FROM tb_categoria")
        categorias = cur.fetchall()
        estados = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
                  'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
                  'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
        return render_template('cadastrar_estabelecimento.html', 
                            categorias=categorias,
                            estados=estados)
    except Exception as e:
        flash(f'Erro ao carregar categorias: {str(e)}', 'danger')
        return redirect(url_for('estabelecimento.filtrar_estabelecimento'))
    finally:
        cur.close()