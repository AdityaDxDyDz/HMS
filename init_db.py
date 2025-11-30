from app import create_app
from extensions import db, bcrypt
from models import User, ROLE_ADMIN, Department

app = create_app()

def initialize_database():
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(role=ROLE_ADMIN).first():
            hashed = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(username='admin', password_hash=hashed, role=ROLE_ADMIN)
            db.session.add(admin)
            db.session.commit()
            print("Admin created.")

        if not Department.query.first():
            for name in ['Cardiology','Dermatology','Pediatrics','Orthopedics','Psychiatry']:
                db.session.add(Department(name=name))
            db.session.commit()
            print("Departments seeded.")

if __name__ == "__main__":
    initialize_database()
