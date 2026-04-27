from flask import Flask, url_for, render_template, redirect, request, make_response, session, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.login_form import LoginForm
from forms.user import RegisterForm
from forms.quiz_form import QuizForm
from forms.question_form import QuestionForm

from data.users import User
from data.quizzes.quizzes import Quiz
from data.quizzes.questions import Question
from data.quizzes.answers import Answer

from data import db_session
import secrets

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_urlsafe(32)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route("/")
def index():
    # db_sess = db_session.create_session()
    # jobs = db_sess.query(Jobs)
    return render_template("index.html", title="GalaxyTest")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(surname=form.surname.data,
                    name=form.name.data,
                    email=form.email.data
                    )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/create_quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    form = QuizForm()
    quest_form = QuestionForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        quiz = Quiz(title=form.title.data, description=form.description.data, user_id=current_user.id)
        db_sess.add(quiz)
        db_sess.commit()
        return redirect(f'/create_quiz/create_questions/{quiz.id}')

    return render_template('create_quiz.html', form=form)


@app.route('/create_quiz/create_questions/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def create_questions(quiz_id):
    form = QuestionForm()
    db_sess = db_session.create_session()
    quiz_title = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first().title
    if form.validate_on_submit():

        quest = Question(content=form.content.data, quiz_id=quiz_id)
        db_sess.add(quest)
        db_sess.commit()
        return redirect(f'/create_quiz/create_questions/{quiz_id}/create_answers/{quest.id}')

    return render_template('create_questions.html', quest_form=form, quiz_title=quiz_title)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    db_session.global_init("db/galaxy_test.db")
    app.run(host="127.0.0.1", port=8081, debug=True)
