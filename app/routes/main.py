from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Grade, User
from app.forms import UpdateProfileForm, ChangePasswordForm
from functools import wraps

main_bp = Blueprint('main', __name__)


def admin_required(f):
    """Decorator to restrict access to admin users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@main_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.phone = form.phone.data.strip()
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))

    # Pre-fill form
    form.full_name.data = current_user.full_name
    form.phone.data = current_user.phone
    return render_template('profile.html', form=form)


@main_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template('change_password.html', form=form)

        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('main.profile'))

    return render_template('change_password.html', form=form)


@main_bp.route('/grades')
@login_required
def grades():
    user_grades = Grade.query.filter_by(user_id=current_user.id).all()
    return render_template('grades.html', grades=user_grades)


@main_bp.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@main_bp.route('/admin/grades/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_manage_grades(user_id):
    from flask import request
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        score = request.form.get('score', '').strip()
        semester = request.form.get('semester', '').strip()

        if subject and score:
            grade = Grade(user_id=user.id, subject=subject, score=score, semester=semester)
            db.session.add(grade)
            db.session.commit()
            flash(f'Grade added for {user.username}.', 'success')
        else:
            flash('Subject and score are required.', 'warning')

        return redirect(url_for('main.admin_manage_grades', user_id=user.id))

    grades = Grade.query.filter_by(user_id=user.id).all()
    return render_template('admin_grades.html', user=user, grades=grades)
