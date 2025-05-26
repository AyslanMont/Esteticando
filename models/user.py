from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, nome, email, tipo_usuario):
        self.id = id 
        self.nome = nome
        self.email = email
        self.tipo_usuario = tipo_usuario

    def get_tipo_usuario(self):
        return self.tipo_usuario

    def __repr__(self):
        return f"<User {self.nome} ({self.tipo_usuario})>"