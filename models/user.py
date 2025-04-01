from flask_login import UserMixin
from esteticando.database.database import mysql

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    def __str__(self):
        return f"User {self.username} ({self.email})"

    @classmethod
    def get_by_email(cls, email):
        """Recupera o usuário (cliente ou profissional) pelo e-mail"""
        cur = mysql.connection.cursor()
        # Tenta buscar primeiro na tabela de clientes
        cur.execute("SELECT cli_id, cli_nome, cli_email, cli_senha FROM tb_cliente WHERE cli_email = %s", (email,))
        user_data = cur.fetchone()

        # Se não encontrar como cliente, tenta na tabela de profissionais
        if not user_data:
            cur.execute("SELECT pro_id, pro_nome, pro_email, pro_senha FROM tb_profissional WHERE pro_email = %s", (email,))
            user_data = cur.fetchone()

        cur.close()

        if user_data:
            # Se encontrado como cliente ou profissional, retorna o usuário
            return cls(user_data['cli_id'] if 'cli_id' in user_data else user_data['pro_id'],
                       user_data['cli_nome'] if 'cli_nome' in user_data else user_data['pro_nome'],
                       user_data['cli_email'] if 'cli_email' in user_data else user_data['pro_email'])
        return None
