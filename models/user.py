from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, nome, email, tipo_usuario):
        self._id = id
        self.nome = nome
        self.email = email
        self._tipo_usuario = tipo_usuario

    @property
    def id(self):
        return self._id

    @property
    def tipo_usuario(self):
        return self._tipo_usuario

    def get_tipo_usuario(self):
        return self._tipo_usuario

    def __repr__(self):
        return f"<User {self.nome} ({self.tipo_usuario})>"
