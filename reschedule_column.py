from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        db.session.execute(
            text('ALTER TABLE appointment ADD COLUMN reschedule_count INTEGER NOT NULL DEFAULT 0;')
        )
        db.session.commit()
        print("Column 'reschedule_count' added successfully to Appointment table.")
    except Exception as e:
        print("Error:", e)
