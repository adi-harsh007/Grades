"""
Seed script — populates the database with sample users and grades.
Run: python seed.py
"""
import os
from dotenv import load_dotenv
from app import create_app, db
from app.models import User, Grade

load_dotenv()

app = create_app()

# Read admin credentials from environment variables
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
ADMIN_FULL_NAME = os.environ.get('ADMIN_FULL_NAME', 'Admin User')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

if not ADMIN_EMAIL or not ADMIN_PASSWORD:
    print('ERROR: ADMIN_EMAIL and ADMIN_PASSWORD must be set in the .env file.')
    exit(1)

with app.app_context():
    db.create_all()

    # Check if already seeded
    if User.query.filter_by(username=ADMIN_USERNAME).first():
        print('Database already seeded. Skipping.')
    else:
        # --- Admin User ---
        admin = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            full_name=ADMIN_FULL_NAME,
            role='admin'
        )
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)

        # --- Student User ---
        student = User(
            username='student1',
            email='student1@securevault.com',
            full_name='Alice Johnson',
            phone='+1 555 0101',
            role='user'
        )
        student.set_password('student123')
        db.session.add(student)
        db.session.flush()  # get student.id

        # --- Sample Grades ---
        sample_grades = [
            Grade(user_id=student.id, subject='Mathematics', score='A', semester='Fall 2025'),
            Grade(user_id=student.id, subject='Data Structures', score='A+', semester='Fall 2025'),
            Grade(user_id=student.id, subject='Operating Systems', score='B+', semester='Fall 2025'),
            Grade(user_id=student.id, subject='Computer Networks', score='A', semester='Fall 2025'),
            Grade(user_id=student.id, subject='Database Systems', score='A-', semester='Fall 2025'),
        ]
        db.session.add_all(sample_grades)
        db.session.commit()

        print('Database seeded successfully!')
        print(f'  Admin  → {ADMIN_EMAIL}')
        print('  Student → student1@securevault.com')
