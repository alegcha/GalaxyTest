from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class CartForm(FlaskForm):
    term = StringField('Термин')
    definition = StringField('Напишите определение')
    add_cart = SubmitField('Добавить карточку')
    finish_test = SubmitField('Сохранить тест')
