from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Question(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String, nullable=False)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'), nullable=False)

    # связь с таблицей quizzes
    quiz = orm.relationship('Quiz')
    # связь с таблицей answers
    answer = orm.relationship("Answer", back_populates='question')