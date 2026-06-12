from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from functools import wraps

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            flash('Debes iniciar sesión.', 'error')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'superadmin':
            flash('No tienes permisos para acceder.', 'error')
            return redirect(url_for('home.index'))
        return f(*args, **kwargs)
    return decorated

@admin.route('/admin')
@admin_required
def dashboard():
    from app import db
    from app.models import Post, Game
    posts       = Post.query.order_by(Post.created_at.desc()).all()
    games       = Game.query.all()
    return render_template('admin/dashboard.html', posts=posts, games=games)

@admin.route('/admin/genero/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_genero():
    from app import db
    from app.models import Genre
    if request.method == 'POST':
        nuevo = Genre(
            name=request.form.get('name').strip(),
            slug=request.form.get('slug').strip().lower(),
            icon_emoji=request.form.get('icon_emoji').strip() or '🎮'
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('Categoría creada.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/nuevo_genero.html')

@admin.route('/admin/juego/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_juego():
    from app import db
    from app.models import Game, Genre
    genres = Genre.query.all()
    if request.method == 'POST':
        nuevo = Game(
            name=request.form.get('name').strip(),
            slug=request.form.get('slug').strip().lower(),
            description=request.form.get('description').strip(),
            icon_emoji=request.form.get('icon_emoji').strip() or '🎮',
            banner_color=request.form.get('banner_color'),
            accent_color=request.form.get('accent_color'),
            banner_image=request.form.get('banner_image').strip(),
            music_url=request.form.get('music_url').strip(),
            genre_id=request.form.get('genre_id', type=int)
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('Juego creado.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/nuevo_juego.html', genres=genres)

@admin.route('/admin/juego/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_juego(id):
    from app import db
    from app.models import Game, Genre
    game = Game.query.get_or_404(id)
    genres = Genre.query.all()
    if request.method == 'POST':
        game.name = request.form.get('name').strip()
        game.slug = request.form.get('slug').strip().lower()
        game.description = request.form.get('description').strip()
        game.icon_emoji = request.form.get('icon_emoji').strip()
        game.banner_color = request.form.get('banner_color')
        game.accent_color = request.form.get('accent_color')
        game.banner_image = request.form.get('banner_image').strip()
        game.music_url = request.form.get('music_url').strip()
        game.genre_id = request.form.get('genre_id', type=int)
        db.session.commit()
        flash('Juego actualizado.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/editar_juego.html', game=game, genres=genres)

@admin.route('/admin/juego/eliminar/<int:id>')
@admin_required
def eliminar_juego(id):
    from app import db
    from app.models import Game, Post
    game = Game.query.get_or_404(id)
    # Borramos los posts uno por uno para que se borren también sus comentarios
    posts = Post.query.filter_by(game_id=game.id).all()
    for p in posts:
        db.session.delete(p)
    # Luego borramos el juego
    db.session.delete(game)
    db.session.commit()
    flash(f'Comunidad {game.name} y todos sus posts han sido eliminados.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/admin/nuevo', methods=['GET', 'POST'])
def nuevo_post():
    from app import db
    from app.models import Post, Game
    if not session.get('user_id'): return redirect(url_for('auth.login'))
    games = Game.query.all()
    
    if request.method == 'POST':
        game_id = request.form.get('game_id', type=int)
        post = Post(
            title=request.form.get('title').strip(), 
            content=request.form.get('content').strip(),
            post_type=request.form.get('post_type', 'news'), 
            game_id=game_id
        )
        db.session.add(post)
        db.session.commit()
        
        # Obtenemos el juego para redireccionar de vuelta a la página correcta
        game = Game.query.get(game_id)
        if game:
            return redirect(f'/categoria/{game.slug}')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/nuevo_post.html', games=games)

@admin.route('/admin/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_post(id):
    from app import db
    from app.models import Post, Game
    post = Post.query.get_or_404(id)
    games = Game.query.all()
    if request.method == 'POST':
        post.title = request.form.get('title').strip()
        post.content = request.form.get('content').strip()
        post.post_type = request.form.get('post_type', 'news')
        post.game_id = request.form.get('game_id', type=int)
        db.session.commit()
        flash('Post actualizado.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/editar_post.html', post=post, games=games)

@admin.route('/admin/eliminar/<int:id>')
@admin_required
def eliminar_post(id):
    from app import db
    from app.models import Post
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))