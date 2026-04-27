from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class QuizForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = StringField('Опишите о чем квиз', validators=[DataRequired()])
    submit = SubmitField('Продолжить')

