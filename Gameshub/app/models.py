from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Tablas intermedias de interacciones
likes_table = db.Table('likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)

saves_table = db.Table('saves',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)

# NUEVA TABLA: Para registrar a qué comunidades se une el usuario
joins_table = db.Table('joins',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('game_id', db.Integer, db.ForeignKey('game.id'), primary_key=True)
)

class Genre(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(64), nullable=False)
    slug       = db.Column(db.String(64), unique=True, nullable=False)
    icon_emoji = db.Column(db.String(10), default='🎮')
    games      = db.relationship('Game', backref='genre', lazy=True)

class Game(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(64), nullable=False)
    slug         = db.Column(db.String(64), unique=True, nullable=False)
    description  = db.Column(db.Text, nullable=True)
    icon_emoji   = db.Column(db.String(10), default='🎮')
    banner_color = db.Column(db.String(7), default='#1a1a2e')
    accent_color = db.Column(db.String(7), default='#2374e1')
    banner_image = db.Column(db.String(255), nullable=True) 
    music_url    = db.Column(db.String(255), nullable=True) 
    genre_id     = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)
    posts        = db.relationship('Post', backref='game', lazy=True)

class Comment(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id    = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Post(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(200), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    post_type  = db.Column(db.String(20), default='news')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    game_id    = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    
    liked_by   = db.relationship('User', secondary=likes_table, backref='liked_posts')
    saved_by   = db.relationship('User', secondary=saves_table, backref='saved_posts')
    comments   = db.relationship('Comment', backref='post', cascade="all, delete-orphan")

class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(20), default='user', nullable=False)
    game_id       = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    
    comments      = db.relationship('Comment', backref='author', lazy=True)
    # Nueva relación para acceder a los juegos a los que se unió
    joined_games  = db.relationship('Game', secondary=joins_table, backref='members')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)