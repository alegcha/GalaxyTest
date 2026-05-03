from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class QuestionForm(FlaskForm):
    content = StringField('Напишите вопрос', validators=[DataRequired()])
    next_step = SubmitField('Далее: Добавить ответы')
