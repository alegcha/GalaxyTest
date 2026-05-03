from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class TestForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = StringField('Опишите о чем будет тест')
    next_step = SubmitField('Далее: Добавить карточку')
