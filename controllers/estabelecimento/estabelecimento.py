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
            SELECT est_id, est_nome, est_descricao, est_imagem, est_email, est_telefone, end_rua, end_numero, end_bairro, end_cidade, end_estado 
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
                SELECT est_id, est_nome, est_descricao, est_email, est_telefone,est_imagem, end_rua, end_numero, end_bairro, end_cidade, end_estado
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


@estabelecimento_bp.route('/estabelecimento/<int:est_id>')
@login_required
def perfil_estabelecimento(est_id):
    cur = None
    try:
        cur = mysql.connection.cursor()
        
        # 1. Busca informações básicas do estabelecimento (incluindo imagem)
        cur.execute("""
            SELECT est_nome, est_imagem, est_descricao 
            FROM tb_estabelecimento 
            WHERE est_id = %s
        """, (est_id,))
        estabelecimento = cur.fetchone()
        
        # Converter imagem binária para base64 se existir
        imagem_base64 = None
        if estabelecimento and estabelecimento['est_imagem']:
            import base64
            imagem_base64 = base64.b64encode(estabelecimento['est_imagem']).decode('utf-8')
        
        # 2. Busca serviços do estabelecimento
        cur.execute("""
            SELECT ser_id, ser_nome, ser_preco, ser_duracao 
            FROM tb_servico 
            WHERE ser_est_id = %s
        """, (est_id,))
        servicos = cur.fetchall()
        
        # 3. Busca informações do profissional dono
        cur.execute("""
            SELECT pro_id, pro_nome 
            FROM tb_profissional 
            WHERE pro_est_id = %s 
            LIMIT 1
        """, (est_id,))
        profissional = cur.fetchone()
        
        # 4. Verifica se o usuário atual é o dono
        dono = False
        pro_id = None
        if profissional:
            pro_id = profissional['pro_id']
            dono = current_user.is_authenticated and (current_user.id == pro_id)
        
        # 5. Formatação dos dados
        data_atual = datetime.now().strftime('%Y-%m-%d')
        
        # 6. Verifica se há serviços para exibir
        if not servicos:
            if dono:
                return redirect(url_for('servico.adicionar_servico', est_id=est_id))
            else:
                return render_template('selecionar_servico.html',
                                    mensagem="Este estabelecimento não possui serviços cadastrados.",
                                    est_id=est_id,
                                    est_nome=estabelecimento['est_nome'] if estabelecimento else 'Estabelecimento',
                                    est_descricao=estabelecimento['est_descricao'] if estabelecimento else '',
                                    imagem_base64=imagem_base64,
                                    pro_id=pro_id)
        
        # 7. Renderiza template com todos os dados
        return render_template('selecionar_servico.html',
                            servicos=servicos,
                            data=data_atual,
                            est_id=est_id,
                            est_nome=estabelecimento['est_nome'] if estabelecimento else 'Estabelecimento',
                            est_descricao=estabelecimento['est_descricao'] if estabelecimento else '',
                            imagem_base64=imagem_base64,
                            pro_id=pro_id,
                            dono=dono)
            
    except Exception as e:
        print(f"Erro ao carregar perfil do estabelecimento: {str(e)}")
        flash("Ocorreu um erro ao carregar o perfil do estabelecimento.", "danger")
        return redirect(url_for('principal.index'))
    finally:
        if cur:
            cur.close()


@estabelecimento_bp.route('/cadastrar_estabelecimento', methods=['POST', 'GET'])
@login_required
def cadastrar_estabelecimento():
    if getattr(current_user, 'tipo_usuario', None) != 'profissional':
        flash('Você precisa estar logado como profissional para cadastrar um estabelecimento.', 'danger')
        return redirect(url_for('auth.login'))

    pro_id = current_user.id
    cur = None  # Declara a variável no início da função

    if request.method == 'POST':
        try:
            required_fields = [
                'est_nome', 'est_descricao', 'est_cnpj', 'est_email',
                'est_telefone', 'est_cat_id', 'end_numero', 'end_bairro',
                'end_rua', 'end_cidade', 'end_estado', 'end_cep'
            ]
            
            # Verificação dos campos obrigatórios
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'O campo {field} é obrigatório!', 'danger')
                    return redirect(url_for('estabelecimento.cadastrar_estabelecimento'))

            # Verificação da imagem
            if 'est_imagem' not in request.files:
                flash('A imagem do estabelecimento é obrigatória', 'danger')
                return redirect(url_for('estabelecimento.cadastrar_estabelecimento'))
                
            imagem_arquivo = request.files['est_imagem']
            if imagem_arquivo.filename == '':
                flash('Nenhuma imagem selecionada', 'danger')
                return redirect(url_for('estabelecimento.cadastrar_estabelecimento'))
                
            imagem_binaria = imagem_arquivo.read()

            # Preparação dos dados
            est_data = {
                'nome': request.form['est_nome'].strip(),
                'descricao': request.form['est_descricao'].strip(),
                'foto': imagem_binaria,
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

            # Validações
            if len(est_data['cnpj']) != 14:
                flash('CNPJ deve conter 14 dígitos', 'danger')
                return redirect(url_for('estabelecimento.cadastrar_estabelecimento'))

            if len(end_data['cep']) != 8:
                flash('CEP deve conter 8 dígitos', 'danger')
                return redirect(url_for('estabelecimento.cadastrar_estabelecimento'))

            # Conexão com o banco de dados
            cur = mysql.connection.cursor()

            # Verifica se CNPJ já existe
            cur.execute("SELECT est_id FROM tb_estabelecimento WHERE est_cnpj = %s", (est_data['cnpj'],))
            if cur.fetchone():
                flash('CNPJ já cadastrado!', 'danger')
                return redirect(url_for('estabelecimento.cadastrar_estabelecimento'))

            # Insere estabelecimento
            cur.execute(
                """INSERT INTO tb_estabelecimento 
                (est_dataCriacao, est_nome, est_descricao, est_cnpj, est_email, est_telefone, est_imagem, est_cat_id) 
                VALUES (CURDATE(), %s, %s, %s, %s, %s, %s, %s)""",
                (est_data['nome'], est_data['descricao'], est_data['cnpj'], 
                 est_data['email'], est_data['telefone'], est_data['foto'], est_data['cat_id'])
            )
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

            # Atualiza o profissional
            cur.execute(
                "UPDATE tb_profissional SET pro_est_id = %s WHERE pro_id = %s",
                (est_id, pro_id)
            )

            # Commit das alterações
            mysql.connection.commit()

            flash("Estabelecimento cadastrado com sucesso! Agora você pode adicionar serviços.", "success")
            return redirect(url_for('servico.adicionar_servico', est_id=est_id))

        except ValueError as e:
            mysql.connection.rollback()
            flash('Dados inválidos fornecidos!', 'danger')
            return redirect(url_for('estabelecimento.cadastrar_estabelecimento'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Erro ao cadastrar estabelecimento: {str(e)}', 'danger')
            return redirect(url_for('estabelecimento.cadastrar_estabelecimento'))
        finally:
            if cur is not None:  # Verifica se o cursor existe antes de tentar fechar
                cur.close()

    # Método GET
    try:
        cur = mysql.connection.cursor()
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
        if cur is not None:  # Verifica se o cursor existe antes de tentar fechar
            cur.close()