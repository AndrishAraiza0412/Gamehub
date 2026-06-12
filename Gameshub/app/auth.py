from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from functools import wraps
from app import db
from app.models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user     = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id']  = user.id
            session['username'] = user.username
            session['role']     = user.role
            session['game_id']  = user.game_id  # ← nuevo
            return redirect(url_for('home.index'))

        flash('Correo o contraseña incorrectos.', 'error')

    return render_template('auth/login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if User.query.filter_by(email=email).first():
            flash('Ese correo ya está registrado.', 'error')
        elif User.query.filter_by(username=username).first():
            flash('Ese nombre de usuario ya existe.', 'error')
        else:
            user = User(username=username, email=email, role='user', game_id=None)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            session['user_id']  = user.id
            session['username'] = user.username
            session['role']     = user.role
            session['game_id']  = user.game_id  # ← nuevo
            return redirect(url_for('home.index'))

    return render_template('auth/register.html')


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home.index'))