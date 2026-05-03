from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class QuizForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = StringField('Опишите о чем квиз')
    next_step = SubmitField('Далее: Добавить вопрос')
