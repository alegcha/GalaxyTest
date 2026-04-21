import datetime

from flask_login import UserMixin
from sqlalchemy import orm, Column, Integer, String, DateTime
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    surname = Column(String, nullable=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    modified_date = Column(DateTime, default=datetime.datetime.now)

    # связь с таблицей quizzes
    quiz = orm.relationship("Quiz", back_populates='user')


    def set_password(self, password):
        self.hashed_password = generate_password_hash(password, method='pbkdf2')

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
