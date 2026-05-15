from flask import Flask, render_template, redirect, abort, request, url_for, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.login_form import LoginForm
from forms.user import RegisterForm

from forms.quizzes.creation.quiz_form import QuizForm
from forms.quizzes.creation.question_form import QuestionForm
from forms.quizzes.creation.answer_form import AnswerForm
from forms.quizzes.creation.quiz_review_form import QuizReviewForm
from forms.quizzes.game.start_game import StartQuizForm
from forms.quizzes.game.question_with_answers_form import QuestionAnswerForm
from forms.tests.test_form import TestForm
from forms.tests.cart_form import CartForm
from forms.tests.test_review_form import TestReviewForm

from data.users import User
from data.quizzes.quizzes import Quiz
from data.quizzes.questions import Question
from data.quizzes.answers import Answer
from data.tests.tests import Test
from data.tests.carts import Cart

from data.api.constans import *
from data.api.functions import get_apod_filename, get_apod_data

from data import db_session
import secrets
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_urlsafe(32)

login_manager = LoginManager()
login_manager.init_app(app)


# вспомогательные функции
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route("/")
@app.route("/index")
def index():
    local_filename = get_apod_filename()
    image_url = None
    if local_filename:
        image_url = url_for('static', filename=f'api/{local_filename}')
    # Проверяем, есть ли данные в сессии (кэшируем на 1 день)
    apod_date = session.get('apod_date')
    apod_data = session.get('apod_data')

    # Если данных нет или они за вчерашний день - обновляем
    today = datetime.now().strftime('%Y-%m-%d')
    if not apod_data or apod_date != today:
        apod_data = get_apod_data()
        if apod_data:
            session['apod_data'] = apod_data
            session['apod_date'] = today
            session.modified = True

    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        quizzes = db_sess.query(Quiz).filter(Quiz.user_id == current_user.id).all()
        tests = db_sess.query(Test).filter(Test.user_id == current_user.id).all()
        return render_template("index.html", title="GalaxyTest", quizzes=quizzes, tests=tests, image_url=image_url,
                               apod=apod_data, day=today)
    return render_template("index.html", title="GalaxyTest", image_url=image_url, apod=apod_data, date=today)


@app.route('/register', methods=['GET', 'POST'])
def register():
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
        return redirect(url_for('login'))

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
        return redirect(url_for('review_quiz', quiz_id=quiz.id))
    return render_template('quizzes/create_quiz.html', form=form)


@app.route('/quiz/<int:quiz_id>/question/create', methods=['GET', 'POST'])
@login_required
def create_question(quiz_id):
    form = QuestionForm()
    db_sess = db_session.create_session()
    quiz_title = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first().title

    if form.validate_on_submit():
        quest = Question(content=form.content.data, quiz_id=quiz_id)
        db_sess.add(quest)
        db_sess.commit()
        return redirect(url_for('review_question', quiz_id=quiz_id, quest_id=quest.id))
    return render_template('quizzes/create_question.html', form=form, quiz_title=quiz_title)


@app.route('/quiz/<int:quiz_id>/question/<int:quest_id>/review', methods=['GET', 'POST'])
@login_required
def review_question(quiz_id, quest_id):
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first()
    question = db_sess.query(Question).filter(Question.id == quest_id).first()
    answers = db_sess.query(Answer).filter(Answer.quest_id == quest_id).all()
    return render_template('quizzes/review_question.html', quiz=quiz, question=question, answers=answers)


@app.route('/quiz/<int:quiz_id>/question/<int:quest_id>/answer/create', methods=['GET', 'POST'])
@login_required
def create_answer(quiz_id, quest_id):
    form = AnswerForm()
    db_sess = db_session.create_session()
    quiz_title = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first().title
    question_title = db_sess.query(Question).filter(Question.id == quest_id).first().content

    if form.validate_on_submit():
        status = form.status.data == 'correct'
        answer = Answer(text=form.text.data, status=status, quest_id=quest_id)
        db_sess.add(answer)
        db_sess.commit()
        return redirect(url_for('review_question', quiz_id=quiz_id, quest_id=quest_id))

    return render_template('quizzes/create_answer.html', quiz_title=quiz_title, question_title=question_title,
                           form=form)


@app.route('/quiz/<int:quiz_id>/review', methods=['GET', 'POST'])
@login_required
def review_quiz(quiz_id):
    # сделать html, где будет инфо квиза, вопросы с ответами; у каждого элемента кнопки для редакции/удаления
    form = QuizReviewForm()
    data = []
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first()
    questions = db_sess.query(Question).filter(Question.quiz_id == quiz_id).all()  # структура квиза: вопрос - ответы
    for question in questions:
        answers = db_sess.query(Answer).filter(Answer.quest_id == question.id).all()
        data.append((question, answers))
    if form.validate_on_submit():
        if form.add_question.data:
            return redirect(url_for('create_question', quiz_id=quiz_id))
        elif form.save_quiz.data:
            return redirect(url_for('index'))
    return render_template('quizzes/review_quiz.html', form=form, quiz=quiz,
                           questions=questions, data=data)


@app.route('/quiz/<int:quiz_id>/edit/quiz_info', methods=['GET', 'POST'])
@login_required
def edit_quiz_info(quiz_id):
    form = QuizForm()
    if request.method == 'GET':
        quiz = get_object_or_404(Quiz, quiz_id)
        form.title.data = quiz.title
        form.description.data = quiz.description
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        quiz = get_object_or_404(Quiz, quiz_id)
        quiz.title = form.title.data
        quiz.description = form.description.data
        db_sess.commit()
        return redirect(url_for('review_quiz', quiz_id=quiz_id))

    return render_template('quizzes/create_quiz.html', form=form)


@app.route('/quiz/<int:quiz_id>/delete')
@login_required
def delete_quiz(quiz_id):
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first()
    questions = db_sess.query(Question).filter(Question.quiz_id == quiz_id).all()
    for question in questions:
        answers = db_sess.query(Answer).filter(Answer.quest_id == question.id).all()
        for answer in answers:
            db_sess.delete(answer)
        db_sess.delete(question)
    db_sess.delete(quiz)
    db_sess.commit()
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
            return redirect(url_for('review_quiz', quiz_id=quiz_id))
        else:
            abort(404)
    return render_template('quizzes/create_question.html', form=form)


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
            return redirect(url_for('review_question', quiz_id=quiz_id, quest_id=quest_id))
        else:
            abort(404)
    return render_template('quizzes/create_answer.html', form=form)


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


@app.route('/quiz/<int:quiz_id>/game/preview')
@login_required
def preview_quiz_game(quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id)
    form = StartQuizForm()
    return render_template('games/preview_game.html', game=quiz, form=form, is_quiz=True)


@app.route('/quiz/<int:quiz_id>/game/start', methods=['POST'])
def play_quiz_start(quiz_id):
    # Инициализация сессии для игры
    session['playing_quiz_id'] = quiz_id
    session['question_index'] = 0
    session['score'] = 0
    session['question_checked'] = False  # Флаг: проверили ли мы уже текущий вопрос
    session['selected_answer_id'] = None

    # Редирект на первый вопрос
    return redirect(url_for('play_question', quiz_id=quiz_id, quest_index=0))


@app.route('/quiz/<int:quiz_id>/game/question/<int:quest_index>', methods=['GET', 'POST'])
@login_required
def play_question(quiz_id, quest_index):
    # Проверки безопасности
    if session.get('playing_quiz_id') != quiz_id:
        return redirect(url_for('preview_quiz_game', quiz_id=quiz_id))
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first()  # вынести в роут со стартом
    questions = db_sess.query(Question).filter(Question.quiz_id == quiz_id).all()
    if quest_index >= len(questions):
        return redirect(url_for('quiz_results', quiz_id=quiz_id))

    current_question = questions[quest_index]
    form = QuestionAnswerForm()

    # Динамическое заполнение вариантов ответа
    answers = db_sess.query(Answer).filter(Answer.quest_id == current_question.id).all()
    if answers:
        form.choice.choices = [(answer.id, answer.text) for answer in answers]
    else:
        session['question_index'] += 1
        session['question_checked'] = False
        session['selected_answer_id'] = None
        return redirect(url_for('play_question', quiz_id=quiz_id, quest_index=session['question_index']))

    #
    if form.validate_on_submit() and form.submit_check.data:
        selected_id = int(form.choice.data)
        session['selected_answer_id'] = selected_id
        session['question_checked'] = True  # Включаем режим просмотра результата
        session.modified = True

        # Подсчет очков (если правильно)
        # answers = db_sess.query(Answer).filter(Answer.id == selected_id).all()
        correct_answer = next((answer for answer in answers if answer.status), None)
        if correct_answer and correct_answer.id == selected_id:
            session['score'] += 10

        # Редирект на ту же страницу, но добавляем метку в URL (опционально) или просто рендерим
        # Важно: Redirect нужен, чтобы сбросить POST-данные и позволить странице отрисовать состояние "Checked"
        return redirect(url_for('play_question', quiz_id=quiz_id, quest_index=quest_index))

    if form.submit_next.data and session.get('question_checked'):
        session['question_index'] += 1
        session['question_checked'] = False
        session['selected_answer_id'] = None
        return redirect(url_for('play_question', quiz_id=quiz_id, quest_index=session['question_index']))

    # показывать ли правильные/неправильные ответы
    is_checked = session.get('question_checked', False)
    selected_id = session.get('selected_answer_id')

    # Подготовка данных для подсветки в шаблоне
    answers_data = []
    for answer in answers:
        state = 'default'
        if is_checked:
            if answer.id == selected_id:
                state = 'selected'  # Этот выбрал юзер
            if answer.status:
                state = 'correct' if state == 'selected' else 'missed_correct'  # Это правильный

        answers_data.append({
            'id': answer.id,
            'text': answer.text,
            'state': state
        })

    return render_template('games/game_question.html',
                           quiz=quiz,
                           question=current_question,
                           answers_data=answers_data,
                           is_checked=is_checked,
                           form=form)


@app.route('/quiz/<int:quiz_id>/game/results')
@login_required
def quiz_results(quiz_id):
    if session.get('playing_quiz_id') != quiz_id:
        return redirect(url_for('index'))

    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first()
    score = session.get('score', 0)
    total = len(db_sess.query(Question).filter(Question.quiz_id == quiz_id).all()) * 10

    # Очистка сессии игры
    session.pop('playing_quiz_id', None)
    session.pop('question_index', None)
    session.pop('score', None)

    return render_template('games/game_results.html', game=quiz, score=score, total=total, is_quiz=True)


@app.route('/test/create', methods=['GET', 'POST'])
@login_required
def create_test():
    form = TestForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        test = Test(title=form.title.data, description=form.description.data, user_id=current_user.id)
        db_sess.add(test)
        db_sess.commit()
        return redirect(url_for('review_test', test_id=test.id))
    return render_template('tests/create_test.html', form=form)


@app.route('/test/<int:test_id>/edit/test_info', methods=['GET', 'POST'])
@login_required
def edit_test_info(test_id):
    form = TestForm()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        test = db_sess.query(Test).filter(Test.id == test_id, Test.user_id == current_user.id).first()
        if test:
            form.title.data = test.title
            form.description.data = test.description
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        test = db_sess.query(Test).filter(Test.id == test_id, Test.user_id == current_user.id).first()
        if test:
            test.title = form.title.data
            test.description = form.description.data
            db_sess.commit()
            return redirect(url_for('review_test', test_id=test.id))
        else:
            abort(404)
    return render_template('tests/create_test.html', form=form)


@app.route('/test/<int:test_id>/review', methods=['GET', 'POST'])
@login_required
def review_test(test_id):
    form = TestReviewForm()
    db_sess = db_session.create_session()
    test = db_sess.query(Test).filter(Test.id == test_id).first()
    carts = db_sess.query(Cart).filter(Cart.test_id == test_id).all()
    if form.validate_on_submit():
        if form.add_cart.data:
            return redirect(url_for('create_cart', test_id=test_id))
        elif form.save_test.data:
            return redirect(url_for('index'))
    return render_template('tests/review_test.html', form=form, test=test, carts=carts)


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
    return redirect(url_for('index'))


@app.route('/test/<int:test_id>/cart/create', methods=['GET', 'POST'])
@login_required
def create_cart(test_id):
    form = CartForm()
    db_sess = db_session.create_session()
    test_title = db_sess.query(Test).filter(Test.id == test_id).first().title

    if form.validate_on_submit():
        cart = Cart(term=form.term.data, definition=form.definition.data, test_id=test_id)
        db_sess.add(cart)
        db_sess.commit()
        return redirect(url_for('review_test', test_id=test_id))
    carts = db_sess.query(Cart).filter(Cart.test_id == test_id).all()
    return render_template('tests/create_cart.html', form=form, test_title=test_title, carts=carts)


@app.route('/test/<int:test_id>/edit/cart/<int:cart_id>', methods=['GET', 'POST'])
@login_required
def edit_cart(test_id, cart_id):
    form = CartForm()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        cart = db_sess.query(Cart).filter(Cart.id == cart_id).first()
        if cart:
            form.term.data = cart.term
            form.definition.data = cart.definition
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        cart = db_sess.query(Cart).filter(Cart.id == cart_id).first()
        if cart:
            cart.term = form.term.data
            cart.definition = form.definition.data
            db_sess.commit()
            return redirect(url_for('review_test', test_id=test_id))
        else:
            abort(404)
    return render_template('tests/create_cart.html', form=form)


@app.route('/cart/<int:cart_id>/delete')
@login_required
def delete_cart(cart_id):
    db_sess = db_session.create_session()
    cart = db_sess.query(Cart).filter(Cart.id == cart_id).first()
    if cart:
        db_sess.delete(cart)
        db_sess.commit()
    else:
        abort(404)
    return redirect(request.referrer or url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('index'))
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    db_session.global_init("db/galaxy_test.db")
    # app.run(host="127.0.0.1", port=8081, debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
