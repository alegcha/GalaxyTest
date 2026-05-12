from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField
from wtforms.validators import DataRequired


class QuestionAnswerForm(FlaskForm):
    choice = RadioField('Варианты ответов', validators=[DataRequired()])

    submit_check = SubmitField('Ответить')
    submit_next = SubmitField('Далее')
