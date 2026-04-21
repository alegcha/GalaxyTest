import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Quiz(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'quizzes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # связь с таблицей users
    user = orm.relationship('User')

    # связь с таблицей questions
    question = orm.relationship("Question", back_populates='quiz')

