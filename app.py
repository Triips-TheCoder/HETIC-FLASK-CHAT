from flask import Flask, render_template, redirect, url_for, request
from models.models import db, User, Message
from db import SQLALCHEMY_DATABASE_URI
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True, 
    "pool_recycle": 300,
}
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'signin'
login_manager.init_app(app)

from models.models import User

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


@app.route('/')
@login_required
def index():
    return render_template('index.html', username=current_user.username)

@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup-test.html")

@app.route("/signin", methods=["GET"])
def signin():
    return render_template("signin-test.html")


@app.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        return redirect(url_for('signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('signin'))

@app.route('/signin', methods=['POST'])
def signin_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return redirect(url_for('signin'))
    
    user.is_logged_in = True
    db.session.commit()

    login_user(user, remember=True)
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    current_user.is_logged_in = False
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/messages", methods=["POST"])
@login_required
def messages_post():
    message = request.form.get("message")
    user_id = current_user.id
    new_message = Message(message=message, user_id=user_id)
    db.session.add(new_message)
    db.session.commit()
    return redirect(url_for("messages"))

@app.route("/messages", methods=["GET"])
def messages():
    messages = db.session.query(Message, User).join(User, Message.user_id == User.id).all()
    return render_template("messages-test.html", messages=messages)

@app.route('/gui')
def gui():
    return render_template('gui.html')



if __name__ == '__main__':
    app.run(debug=True)
