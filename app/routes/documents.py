import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Document, SharedDocument, User
from app.forms import UploadDocumentForm, ShareDocumentForm

doc_bp = Blueprint('documents', __name__, url_prefix='/documents')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@doc_bp.route('/')
@login_required
def list_documents():
    own_docs = Document.query.filter_by(owner_id=current_user.id).all()
    shared_entries = SharedDocument.query.filter_by(shared_with_id=current_user.id).all()
    shared_docs = [entry.document for entry in shared_entries]
    public_docs = Document.query.filter(Document.is_public == True, Document.owner_id != current_user.id).all()
    return render_template('documents.html', own_docs=own_docs, shared_docs=shared_docs, public_docs=public_docs)


@doc_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadDocumentForm()
    if form.validate_on_submit():
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('No file selected.', 'warning')
            return render_template('upload.html', form=form)

        if not allowed_file(file.filename):
            flash('File type not allowed.', 'danger')
            return render_template('upload.html', form=form)

        original_name = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{original_name}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
        file.save(file_path)
        file_size = os.path.getsize(file_path)

        doc = Document(
            owner_id=current_user.id,
            filename=unique_name,
            original_name=original_name,
            file_size=file_size,
            is_public=form.is_public.data,
            description=form.description.data.strip()
        )
        db.session.add(doc)
        db.session.commit()
        flash('Document uploaded successfully!', 'success')
        return redirect(url_for('documents.list_documents'))

    return render_template('upload.html', form=form)


@doc_bp.route('/download/<int:doc_id>')
@login_required
def download(doc_id):
    doc = Document.query.get_or_404(doc_id)

    # Check access: owner, shared, or public
    is_owner = doc.owner_id == current_user.id
    is_shared = SharedDocument.query.filter_by(document_id=doc.id, shared_with_id=current_user.id).first()
    is_admin = current_user.role == 'admin'

    if not (is_owner or is_shared or doc.is_public or is_admin):
        flash('Access denied.', 'danger')
        return redirect(url_for('documents.list_documents'))

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], doc.filename,
                              as_attachment=True, download_name=doc.original_name)


@doc_bp.route('/share/<int:doc_id>', methods=['GET', 'POST'])
@login_required
def share(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if doc.owner_id != current_user.id:
        flash('You can only share your own documents.', 'danger')
        return redirect(url_for('documents.list_documents'))

    form = ShareDocumentForm()
    if form.validate_on_submit():
        target_user = User.query.filter_by(username=form.username.data.strip()).first()
        if not target_user:
            flash('User not found.', 'warning')
        elif target_user.id == current_user.id:
            flash('You cannot share a document with yourself.', 'warning')
        elif SharedDocument.query.filter_by(document_id=doc.id, shared_with_id=target_user.id).first():
            flash('Document already shared with this user.', 'info')
        else:
            shared = SharedDocument(document_id=doc.id, shared_with_id=target_user.id)
            db.session.add(shared)
            db.session.commit()
            flash(f'Document shared with {target_user.username}!', 'success')
            return redirect(url_for('documents.list_documents'))

    return render_template('share.html', form=form, doc=doc)


@doc_bp.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if doc.owner_id != current_user.id and current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('documents.list_documents'))

    # Delete file from disk
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(doc)
    db.session.commit()
    flash('Document deleted.', 'success')
    return redirect(url_for('documents.list_documents'))
