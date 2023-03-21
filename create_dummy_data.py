from main import app, db
from main.models import User


def create_users():
    with app.app_context():
        db.create_all()
        user_1 = User(username='Num1', email='some@se.com', password='password')
        user_2 = User(username='Num2', email='some2@se.com', password='password')
        db.session.add(user_1)
        db.session.add(user_2)
        db.session.commit()
