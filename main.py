from flask import Flask, render_template, redirect, abort, request, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.login_form import LoginForm
from forms.user import RegisterForm
from forms.quizzes.quiz_form import QuizForm
from forms.quizzes.question_form import QuestionForm
from forms.quizzes.answer_form import AnswerForm
from forms.quizzes.quiz_review_form import ReviewForm
from forms.quizzes.question_review_form import QuestionReviewForm
from forms.tests.test_form import TestForm
from forms.tests.cart_form import CartForm

from data.users import User
from data.quizzes.quizzes import Quiz
from data.quizzes.questions import Question
from data.quizzes.answers import Answer
from data.tests.tests import Test
from data.tests.carts import Cart

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
@app.route("/index")
def index():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        quizzes = db_sess.query(Quiz).filter(Quiz.user_id == current_user.id).all()
        tests = db_sess.query(Test).filter(Test.user_id == current_user.id).all()
        return render_template("index.html", title="GalaxyTest", quizzes=quizzes, tests=tests)
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


@app.route('/quiz/create', methods=['GET', 'POST'])
@login_required
def create_quiz():
    form = QuizForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        quiz = Quiz(title=form.title.data, description=form.description.data, user_id=current_user.id)
        db_sess.add(quiz)
        db_sess.commit()
        return redirect(f'/quiz/{quiz.id}/review')
    return render_template('quizzes/create_quiz.html', form=form)


@app.route('/quiz/<int:quiz_id>/question/create', methods=['GET', 'POST'])
@login_required
def create_questions(quiz_id):
    form = QuestionForm()
    db_sess = db_session.create_session()
    quiz_title = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first().title

    if form.validate_on_submit():
        quest = Question(content=form.content.data, quiz_id=quiz_id)
        db_sess.add(quest)
        db_sess.commit()
        return redirect(f'/quiz/{quiz_id}/question/{quest.id}/review')
    return render_template('quizzes/create_questions.html', form=form, quiz_title=quiz_title)


@app.route('/quiz/<int:quiz_id>/question/<int:quest_id>/review', methods=['GET', 'POST'])
@login_required
def review_question(quiz_id, quest_id):
    form = QuestionReviewForm()
    print("-" * 20)
    # if form.validate_on_submit():
    #
    #     if form.add_answer.data:
    #         return redirect(f"/quiz/{quiz_id}/question/{quest_id}/answer/create")
    #     elif form.finish_question.data:
    #         return redirect(f'/quiz/{quiz_id}/review')

    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first()
    question = db_sess.query(Question).filter(Question.id == quest_id).first()
    answers = db_sess.query(Answer).filter(Answer.quest_id == quest_id).all()
    return render_template('quizzes/question_review.html', quiz=quiz, question=question,
                           form=form, answers=answers)


@app.route('/quiz/<int:quiz_id>/question/<int:quest_id>/answer/create', methods=['GET', 'POST'])
@login_required
def create_answers(quiz_id, quest_id):
    form = AnswerForm()
    db_sess = db_session.create_session()
    quiz_title = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first().title
    question_title = db_sess.query(Question).filter(Question.id == quest_id).first().content

    if form.validate_on_submit():
        status = form.status.data == 'correct'
        answer = Answer(text=form.text.data, status=status, quest_id=quest_id)
        db_sess.add(answer)
        db_sess.commit()
        return redirect(f"/quiz/{quiz_id}/question/{quest_id}/review")

    return render_template('quizzes/create_answers.html', quiz_title=quiz_title, question_title=question_title,
                           form=form)


@app.route('/quiz/<int:quiz_id>/review', methods=['GET', 'POST'])
@login_required
def review_quiz(quiz_id):
    # сделать html, где будет инфо квиза, вопросы с ответами; у каждого элемента кнопки для редакции/удаления
    form = ReviewForm()
    data = []
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first()
    questions = db_sess.query(Question).filter(Question.quiz_id == quiz_id).all()  # структура квиза: вопрос - ответы
    for question in questions:
        answers = db_sess.query(Answer).filter(Answer.quest_id == question.id).all()
        data.append((question, answers))
    if form.validate_on_submit():
        if form.add_question.data:
            return redirect(f"/quiz/{quiz_id}/question/create")
        elif form.save_quiz.data:
            return redirect("/")
    return render_template('quizzes/quiz_review.html', form=form, quiz=quiz,
                           questions=questions, data=data)


@app.route('/quiz/<int:quiz_id>/edit/quiz_info', methods=['GET', 'POST'])
@login_required
def edit_quiz_info(quiz_id):
    # quiz_form.py, create_quiz.html
    form = QuizForm()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
        if quiz:
            form.title.data = quiz.title
            form.description.data = quiz.description
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
        if quiz:
            quiz.title = form.title.data
            quiz.description = form.description.data
            db_sess.commit()
            return redirect(f'/quiz/{quiz_id}/review')
        else:
            abort(404)
    return render_template('quizzes/create_quiz.html', form=form)


@app.route('/quiz/<int:quiz_id>/delete')
@login_required
def delete_quiz(quiz_id):
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if quiz:
        questions = db_sess.query(Question).filter(Question.quiz_id == quiz_id).all()
        for question in questions:
            answers = db_sess.query(Answer).filter(Answer.quest_id == question.id).all()
            for answer in answers:
                db_sess.delete(answer)
            db_sess.delete(question)
        db_sess.delete(quiz)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/quiz/<int:quiz_id>/edit/question/<int:quest_id>', methods=['GET', 'POST'])
@login_required
def edit_question(quiz_id, quest_id):
    form = QuestionForm()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        question = db_sess.query(Question).filter(Question.id == quest_id).first()
        if question:
            form.content.data = question.content
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        question = db_sess.query(Question).filter(Question.id == quest_id).first()
        if question:
            question.content = form.content.data
            db_sess.commit()
            return redirect(f'/quiz/{quiz_id}/review')
        else:
            abort(404)
    return render_template('quizzes/create_questions.html', form=form)


@app.route('/question/<int:quest_id>/delete')
@login_required
def delete_question(quest_id):
    db_sess = db_session.create_session()
    question = db_sess.query(Question).filter(Question.id == quest_id).first()
    # quiz_id = question.quiz_id
    if question:
        answers = db_sess.query(Answer).filter(Answer.quest_id == question.id).all()
        for answer in answers:
            db_sess.delete(answer)
        db_sess.delete(question)
        db_sess.commit()
    else:
        abort(404)
    # return redirect(f'/quiz/{quiz_id}/review')
    return redirect(request.referrer or url_for('index'))


@app.route('/quiz/<int:quiz_id>/edit/question/<int:quest_id>/answer/<int:answer_id>', methods=['GET', 'POST'])
@login_required
def edit_answer(quiz_id, quest_id, answer_id):
    form = AnswerForm()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        answer = db_sess.query(Answer).filter(Answer.id == answer_id).first()
        if answer:
            form.text.data = answer.text
            form.status.data = "correct" if answer.status else "incorrect"
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        answer = db_sess.query(Answer).filter(Answer.id == answer_id).first()
        if answer:
            answer.text = form.text.data
            answer.status = form.status.data == "correct"
            db_sess.commit()
            return redirect(f'/quiz/{quiz_id}/question/{quest_id}/review')
        else:
            abort(404)
    return render_template('quizzes/create_answers.html', form=form)


@app.route('/answer/<int:answer_id>/delete')
@login_required
def delete_answer(answer_id):
    db_sess = db_session.create_session()
    answers = db_sess.query(Answer).filter(Answer.id == answer_id).all()
    if answers:
        for answer in answers:
            db_sess.delete(answer)
        db_sess.commit()
    else:
        abort(404)
    return redirect(request.referrer or url_for('index'))


@app.route('/test/create', methods=['GET', 'POST'])
@login_required
def create_test():
    form = TestForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        test = Test(title=form.title.data, description=form.description.data, user_id=current_user.id)
        db_sess.add(test)
        db_sess.commit()
        return redirect(f'/test/{test.id}/carts/create')
    return render_template('tests/create_test.html', form=form)


@app.route('/test/<int:test_id>/carts/create', methods=['GET', 'POST'])
@login_required
def create_carts(test_id):
    form = CartForm()
    db_sess = db_session.create_session()
    test_title = db_sess.query(Test).filter(Test.id == test_id).first().title

    if form.validate_on_submit():
        if form.add_cart.data:
            cart = Cart(term=form.term.data, definition=form.definition.data, test_id=test_id)
            db_sess.add(cart)
            db_sess.commit()
            carts = db_sess.query(Cart).filter(Cart.test_id == test_id).all()

            form.term.data = ""
            form.definition.data = ""

            return render_template('tests/create_carts.html', test_title=test_title,
                                   form=form, carts=carts)

        elif form.finish_test.data:
            return redirect(f'/')
    carts = db_sess.query(Cart).filter(Cart.test_id == test_id).all()
    return render_template('tests/create_carts.html', form=form, test_title=test_title, carts=carts)


@app.route('/test/<int:test_id>/delete')
@login_required
def delete_test(test_id):
    db_sess = db_session.create_session()
    test = db_sess.query(Test).filter(Test.id == test_id, Test.user_id == current_user.id).first()
    if test:
        carts = db_sess.query(Cart).filter(Cart.test_id == test_id).all()
        for cart in carts:
            db_sess.delete(cart)
        db_sess.delete(test)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


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
