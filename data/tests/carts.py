from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Cart(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'carts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    term = Column(String, nullable=True)
    definition = Column(String, nullable=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=True)

    # связь с таблицей tests
    test = orm.relationship('Test')