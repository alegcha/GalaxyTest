from flask_wtf import FlaskForm
from wtforms import SubmitField


class TestReviewForm(FlaskForm):
    add_cart = SubmitField('Добавить новую карточку')
    save_test = SubmitField('Сохранить тест')