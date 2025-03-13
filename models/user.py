from flask_login import UserMixin
from esteticando.database.database import mysql

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    def __str__(self):
        return f"User {self.username} ({self.email})"
