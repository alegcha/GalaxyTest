from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired


class AnswerForm(FlaskForm):
    text = StringField('Ответ')
    status = RadioField('Статус', choices=[('correct', 'Верный'), ('incorrect', 'Нeверный')], default='incorrect')
    add_answer = SubmitField('Добавить ответ')
    finish_question = SubmitField('Продолжить')
