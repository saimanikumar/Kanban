from .database import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100), unique=True)
    lists = db.relationship("Todo_list", backref = "user", cascade="all, delete")
    
    def __repr__(self):
        return f"<User {self.name}>"


class Todo_list(db.Model):
    list_id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    tasks_completed = db.Column(db.Integer, default=0)
    tasks_remaining = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    cards = db.relationship("Card", backref="todo_list", cascade="all, delete")

    def __repr__(self):
        return f"<Todo_list {self.list_name}>"


class Card(db.Model):
    card_id = db.Column(db.Integer, primary_key=True)
    card_title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    task_updated_date = db.Column(db.DateTime)
    is_complete = db.Column(db.Integer)
    li = db.Column(db.Integer, db.ForeignKey(
        "todo_list.list_id"), nullable=False)

    def __repr__(self):
        return f"<Card {self.card_title}>"
