from flask import render_template, Blueprint, request, jsonify, session, redirect
from app.models import Genre, Game, Post, User, Comment
from app import db
import os

home = Blueprint('home', __name__)

@home.route('/')
def index():
    genres = Genre.query.all()
    games  = Game.query.all()
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('home.html', genres=genres, games=games, posts=posts)

@home.route('/guardados')
def guardados():
    if 'user_id' not in session: return redirect('/login')
    user = User.query.get(session['user_id'])
    genres = Genre.query.all()
    games = Game.query.all()
    return render_template('home.html', genres=genres, games=games, posts=user.saved_posts, section_title="Tus Publicaciones Guardadas")

@home.route('/mis-comunidades')
def mis_comunidades():
    if 'user_id' not in session: return redirect('/login')
    user = User.query.get(session['user_id'])
    genres = Genre.query.all()
    games = Game.query.all()
    
    joined_ids = [g.id for g in user.joined_games]
    if joined_ids:
        posts = Post.query.filter(Post.game_id.in_(joined_ids)).order_by(Post.created_at.desc()).all()
    else:
        posts = []
        
    return render_template('home.html', genres=genres, games=games, posts=posts, section_title="Novedades de tus Comunidades")

@home.route('/buscar')
def buscar():
    q = request.args.get('q', '').strip()
    resultados = []
    if q:
        resultados = Post.query.filter(Post.title.ilike(f'%{q}%') | Post.content.ilike(f'%{q}%')).order_by(Post.created_at.desc()).all()
    genres = Genre.query.all()
    games  = Game.query.all()
    return render_template('home.html', posts=resultados, genres=genres, games=games, query=q)

@home.route('/categoria/<slug>')
def categoria(slug):
    game = Game.query.filter_by(slug=slug).first_or_404()
    posts = Post.query.filter_by(game_id=game.id).order_by(Post.created_at.desc()).all()
    genres = Genre.query.all()
    games = Game.query.all()
    multimedia = [p for p in posts if '<img' in p.content or '<iframe' in p.content]
    template_path = f'comunidades/{slug}.html'
    if os.path.exists(os.path.join('app', 'templates', template_path)):
        return render_template(template_path, game=game, posts=posts, genres=genres, games=games, multimedia=multimedia)
    return render_template('comunidades/generica.html', game=game, posts=posts, genres=genres, games=games, multimedia=multimedia)

# --- RUTAS DE INTERACCIÓN ---

@home.route('/post/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    user = User.query.get(session['user_id'])
    post = Post.query.get_or_404(post_id)
    if user in post.liked_by:
        post.liked_by.remove(user)
        liked = False
    else:
        post.liked_by.append(user)
        liked = True
    db.session.commit()
    return jsonify({'likes': len(post.liked_by), 'liked': liked})

@home.route('/post/<int:post_id>/save', methods=['POST'])
def save_post(post_id):
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    user = User.query.get(session['user_id'])
    post = Post.query.get_or_404(post_id)
    if user in post.saved_by:
        post.saved_by.remove(user)
        saved = False
    else:
        post.saved_by.append(user)
        saved = True
    db.session.commit()
    return jsonify({'saved': saved})

@home.route('/game/<int:game_id>/join', methods=['POST'])
def join_game(game_id):
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    user = User.query.get(session['user_id'])
    game = Game.query.get_or_404(game_id)
    if user in game.members:
        game.members.remove(user)
        joined = False
    else:
        game.members.append(user)
        joined = True
    db.session.commit()
    return jsonify({'joined': joined})

# --- RUTAS DE COMENTARIOS (AJAX - SIN RECARGAR) ---

@home.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    content = data.get('content').strip() if data else request.form.get('content').strip()
    
    if content:
        com = Comment(content=content, user_id=session['user_id'], post_id=post_id)
        db.session.add(com)
        db.session.commit()
        
        user = User.query.get(session['user_id'])
        return jsonify({
            'success': True,
            'id': com.id,
            'content': com.content,
            'username': user.username,
            'date': com.created_at.strftime('%d/%m/%Y'),
        })
    return jsonify({'success': False})

@home.route('/comment/<int:comment_id>/edit', methods=['POST'])
def edit_comment(comment_id):
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.user_id == session['user_id']:
        data = request.get_json()
        new_content = data.get('content').strip() if data else request.form.get('content').strip()
        
        if new_content:
            comment.content = new_content
            db.session.commit()
            return jsonify({'success': True, 'content': new_content})
            
    return jsonify({'success': False})

@home.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.user_id == session['user_id']:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'success': True})
        
    return jsonify({'success': False})