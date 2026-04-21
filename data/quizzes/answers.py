from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Answer(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, nullable=False)
    status = Column(Boolean)
    quest_id = Column(Integer, ForeignKey('questions.id'), nullable=False)

    # связь с таблицей questions
    question = orm.relationship('Question')
