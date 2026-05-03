from flask_wtf import FlaskForm
from wtforms import SubmitField


class ReviewForm(FlaskForm):
    add_question = SubmitField('Добавить новый вопрос')
    save_quiz = SubmitField('Сохранить квиз')
