from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired


class QuestionReviewForm(FlaskForm):
    add_answer = SubmitField('Добавить ответ')
    finish_question = SubmitField('Завершить вопрос')