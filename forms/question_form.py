from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class QuestionForm(FlaskForm):
    content = StringField('Напишите вопрос', validators=[DataRequired()])
    submit = SubmitField('Продолжить')