import os
import uuid
from flask import Blueprint, jsonify, request, session, send_file
from werkzeug.utils import secure_filename
from src.models.user import Document, User, Folder, db
from src.routes.user import login_required

documents_bp = Blueprint('documents', __name__)

UPLOAD_FOLDER = os.environ.get('UPLOADS_DIR', '/tmp/vdr_uploads')
RAILWAY_MODE = os.environ.get('RAILWAY_STATIC_URL') is not None
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

@documents_bp.route('/documents', methods=['GET'])
@login_required
def get_documents():
    folder_id = request.args.get('folder_id', type=int)
    
    if folder_id:
        documents = Document.query.filter_by(folder_id=folder_id).all()
    else:
        # Get documents in root (no folder)
        documents = Document.query.filter_by(folder_id=None).all()
    
    return jsonify([doc.to_dict() for doc in documents])

@documents_bp.route('/documents', methods=['POST'])
@login_required
def upload_document():
    # Check if running on Railway - disable file uploads
    if RAILWAY_MODE:
        return jsonify({'error': 'File uploads are disabled on Railway due to read-only filesystem. Use local deployment or Azure for file uploads.'}), 400
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    ensure_upload_folder()
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    file_extension = original_filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    # Save file
    file.save(file_path)
    file_size = os.path.getsize(file_path)
    
    # Get folder_id from form data
    folder_id = request.form.get('folder_id', type=int)
    
    # Validate folder exists if provided
    if folder_id:
        folder = Folder.query.get(folder_id)
        if not folder:
            os.remove(file_path)  # Clean up uploaded file
            return jsonify({'error': 'Folder not found'}), 404
    
    # Save to database
    document = Document(
        filename=unique_filename,
        original_filename=original_filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type or 'application/octet-stream',
        uploaded_by=session['user_id'],
        description=request.form.get('description', ''),
        folder_id=folder_id
    )
    
    db.session.add(document)
    db.session.commit()
    
    return jsonify({'message': 'File uploaded successfully', 'document': document.to_dict()}), 201

@documents_bp.route('/documents/<int:doc_id>', methods=['GET'])
@login_required
def get_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    return jsonify(document.to_dict())

@documents_bp.route('/documents/<int:doc_id>/download', methods=['GET'])
@login_required
def download_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    
    if not os.path.exists(document.file_path):
        return jsonify({'error': 'File not found on disk'}), 404
    
    return send_file(
        document.file_path,
        as_attachment=True,
        download_name=document.original_filename,
        mimetype=document.mime_type
    )

@documents_bp.route('/documents/<int:doc_id>', methods=['PUT'])
@login_required
def update_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    
    # Only allow the uploader or admin to update
    user = User.query.get(session['user_id'])
    if document.uploaded_by != session['user_id'] and not user.is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.json
    
    # Update description
    if 'description' in data:
        document.description = data['description']
    
    # Update folder
    if 'folder_id' in data:
        folder_id = data['folder_id']
        if folder_id:
            folder = Folder.query.get(folder_id)
            if not folder:
                return jsonify({'error': 'Folder not found'}), 404
        document.folder_id = folder_id
    
    db.session.commit()
    return jsonify(document.to_dict())

@documents_bp.route('/documents/<int:doc_id>', methods=['DELETE'])
@login_required
def delete_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    
    # Only allow the uploader or admin to delete
    user = User.query.get(session['user_id'])
    if document.uploaded_by != session['user_id'] and not user.is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    
    # Delete file from disk
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    # Delete from database
    db.session.delete(document)
    db.session.commit()
    
    return jsonify({'message': 'Document deleted successfully'}), 200

@documents_bp.route('/documents/<int:doc_id>/move', methods=['POST'])
@login_required
def move_document(doc_id):
    """Move document to a different folder"""
    document = Document.query.get_or_404(doc_id)
    
    # Only allow the uploader or admin to move
    user = User.query.get(session['user_id'])
    if document.uploaded_by != session['user_id'] and not user.is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.json
    if 'folder_id' not in data:
        return jsonify({'error': 'folder_id is required'}), 400
    
    folder_id = data['folder_id']
    
    # Validate folder exists if provided
    if folder_id:
        folder = Folder.query.get(folder_id)
        if not folder:
            return jsonify({'error': 'Folder not found'}), 404
    
    document.folder_id = folder_id
    db.session.commit()
    
    return jsonify({'message': 'Document moved successfully', 'document': document.to_dict()})

