import sqlalchemy
from .db_session import SqlAlchemyBase


association_table_quiz = sqlalchemy.Table(
        'quiz_to_category',
        SqlAlchemyBase.metadata,
        sqlalchemy.Column('test', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('tests.id')),
        sqlalchemy.Column('category', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('category.id')))
association_table_test = sqlalchemy.Table(
        'test_to_category',
        SqlAlchemyBase.metadata,
        sqlalchemy.Column('quiz', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('quizzes.id')),
        sqlalchemy.Column('category', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('category.id')))

class Category(SqlAlchemyBase):
    __tablename__ = 'category'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)