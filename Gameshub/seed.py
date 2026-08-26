from app import create_app, db
from app.models import Genre, Game, Post, User

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # ── Géneros ──
    deportes   = Genre(name='Deportes',   slug='deportes',   icon_emoji='⚽')
    shooter    = Genre(name='Shooter',    slug='shooter',    icon_emoji='🎯')
    rpg        = Genre(name='RPG',        slug='rpg',        icon_emoji='⚔️')
    estrategia = Genre(name='Estrategia', slug='estrategia', icon_emoji='♟️')

    db.session.add_all([deportes, shooter, rpg, estrategia])
    db.session.flush()

    # ── Juego: Rocket League ──
    rl = Game(
        name         = 'Rocket League',
        slug         = 'rocket-league',
        icon_emoji   = '🚗',
        description  = 'Noticias, guías y actualizaciones de Rocket League.',
        banner_color = '#0d1b2a',
        accent_color = '#00aaff',
        genre_id     = deportes.id
    )
    db.session.add(rl)
    db.session.flush()

    # ── Posts de ejemplo ──
    posts = [
        Post(title='Temporada 14 ya disponible',
             content='La nueva temporada trae mapas y autos exclusivos...',
             post_type='news', game_id=rl.id),
        Post(title='Guía para mejorar tus aéreos',
             content='Los aéreos son clave para subir de rango en Rocket League...',
             post_type='guide', game_id=rl.id),
        Post(title='Parche v2.45 disponible',
             content='Corrección de bugs y mejoras de rendimiento...',
             post_type='update', game_id=rl.id),
    ]
    db.session.add_all(posts)

    # ── Usuarios ──
    superadmin = User(username='admin', email='admin@gamehub.com', role='superadmin', game_id=None)
    superadmin.set_password('admin1234')

    rl_admin = User(username='rl_admin', email='rl@gamehub.com', role='category_admin', game_id=rl.id)
    rl_admin.set_password('rl1234')

    db.session.add_all([superadmin, rl_admin])
    db.session.commit()

    print('✅ Base de datos inicializada correctamente')
    print('─' * 40)
    print('  Superadmin → admin@gamehub.com / admin1234')
    print('  RL Admin   → rl@gamehub.com / rl1234')
    print('─' * 40)