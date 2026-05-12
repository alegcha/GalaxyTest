from flask_wtf import FlaskForm
from wtforms import SubmitField

class StartQuizForm(FlaskForm):
    start_btn = SubmitField('Начать квиз')
    back_btn = SubmitField('Вернуться к обзору')