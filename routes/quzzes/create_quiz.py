from flask import Flask, render_template, redirect, abort, request, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.quizzes.quiz_form import QuizForm
from forms.quizzes.question_form import QuestionForm
from forms.quizzes.answer_form import AnswerForm
from forms.quizzes.quiz_review_form import QuizReviewForm

from data.users import User
from data.quizzes.quizzes import Quiz
from data.quizzes.questions import Question
from data.quizzes.answers import Answer

from data import db_session
from main import app

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
    return render_template('quizzes/create_question.html', form=form, quiz_title=quiz_title)


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

    return render_template('quizzes/create_answer.html', quiz_title=quiz_title, question_title=question_title,
                           form=form)
