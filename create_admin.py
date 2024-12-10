from app import app, db
from models import User

def create_admin_user():
    with app.app_context():
        # Verificar se o usuário admin já existe
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True,
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Usuário admin criado com sucesso!")
        else:
            print("Usuário admin já existe!")

if __name__ == '__main__':
    create_admin_user()
