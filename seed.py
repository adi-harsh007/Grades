"""
Seed script — populates the database with sample users and grades.
Run: python seed.py
"""
from app import create_app, db
from app.models import User, Grade

app = create_app()

with app.app_context():
    db.create_all()

    # Check if already seeded
    if User.query.filter_by(username='admin').first():
        print('Database already seeded. Skipping.')
    else:
        # --- Admin User ---
        admin = User(
            username='admin',
            email='admin@securevault.com',
            full_name='Admin User',
            role='admin'
        )
        admin.set_password('admin123')
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
        print('  Admin  → admin@securevault.com / admin123')
        print('  Student → student1@securevault.com / student123')
