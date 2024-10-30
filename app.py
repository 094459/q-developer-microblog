from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///microblog.db')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models

favorites_table = db.Table('favorites',
    db.Column('user_id', db.BigInteger, db.ForeignKey('users.id'), primary_key=True),
    db.Column('message_id', db.BigInteger, db.ForeignKey('messages.id'), primary_key=True),
    db.Column('created_at', db.DateTime(timezone=True), server_default=db.func.now())
)
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())
    messages = db.relationship('Message', backref='author', lazy='dynamic')
    favorites = db.relationship('Message',
        secondary=favorites_table,
        lazy='dynamic',
        backref=db.backref('favorited_by', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())



@app.route('/favorite/<int:message_id>', methods=['POST'])
@login_required
def favorite_message(message_id):
    message = Message.query.get_or_404(message_id)
    if message not in current_user.favorites:
        current_user.favorites.append(message)
        db.session.commit()
        flash('Message added to favorites!')
    return redirect(url_for('index'))

@app.route('/unfavorite/<int:message_id>', methods=['POST'])
@login_required
def unfavorite_message(message_id):
    message = Message.query.get_or_404(message_id)
    if message in current_user.favorites:
        current_user.favorites.remove(message)
        db.session.commit()
        flash('Message removed from favorites!')
    return redirect(url_for('index'))

@app.route('/favorites')
@login_required
def show_favorites():
    favorites = current_user.favorites.order_by(Message.created_at.desc()).all()
    return render_template('favorites.html', messages=favorites)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            flash('Email address already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        content = request.form['content']
        if content:
            message = Message(content=content, author=current_user)
            db.session.add(message)
            db.session.commit()
            flash('Your message has been posted!')
            return redirect(url_for('index'))
    
    messages = Message.query.order_by(Message.created_at.desc()).limit(20).all()
    return render_template('index.html', messages=messages)

@app.route('/create_post', methods=['POST'])
@login_required
def create_post():
    content = request.form['content']
    if content and len(content) <= 200:
        message = Message(content=content, author=current_user)
        db.session.add(message)
        db.session.commit()
        flash('Your message has been posted!')
    elif len(content) > 200:
        flash('Message content must be 200 characters or less.')
    else:
        flash('Message content cannot be empty.')
    return redirect(url_for('index'))

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    messages = Message.query.filter_by(author=user).order_by(Message.created_at.desc()).all()
    return render_template('profile.html', user=user, messages=messages)

@app.route('/profile/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    if current_user.username != username:
        flash('You can only edit your own profile.')
        return redirect(url_for('profile', username=username))
    
    user = User.query.filter_by(username=username).first_or_404()
    if request.method == 'POST':
        user.display_name = request.form['display_name']
        user.bio = request.form['bio']
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('profile', username=username))
    
    return render_template('edit_profile.html', user=user)

@app.route('/users')
def users():
    users = User.query.order_by(User.username).all()
    return render_template('users.html', users=users)
@app.route('/favorites')
@login_required
def favorites():
    favorite_messages = current_user.favorites.order_by(Message.created_at.desc()).all()
    return render_template('favorites.html', messages=favorite_messages)


# if __name__ == '__main__':
#     app.run(debug=True)

def init_db():
    with app.app_context():
        db.create_all()
        print("Database tables created.")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)