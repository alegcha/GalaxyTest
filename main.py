from flask import Flask, url_for, render_template, redirect, request, make_response, session, jsonify
from data import db_session
import secrets


app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_urlsafe(32)



# @login_manager.user_loader
# def load_user(user_id):
#     # db_sess = db_session.create_session()
#     # return db_sess.get(User, user_id)
#     pass


@app.route("/")
def index():
    # db_sess = db_session.create_session()
    # jobs = db_sess.query(Jobs)
    # return render_template("index.html", title="Главная", jobs=jobs, db_sess=db_sess, User=User)
    pass


if __name__ == '__main__':
    # db_session.global_init("db/mars_explorer.db")
    # app.run(host="127.0.0.1", port=8081, debug=True)
    pass