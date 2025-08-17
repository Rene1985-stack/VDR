from flask import Blueprint, request, jsonify, session
from models.user import db, Folder, Document, User

folders_bp = Blueprint('folders', __name__)

@folders_bp.route('/folders', methods=['GET'])
def get_folders():
    """Get all folders or folders in a specific parent folder"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    parent_id = request.args.get('parent_id', type=int)
    
    if parent_id:
        folders = Folder.query.filter_by(parent_id=parent_id).all()
    else:
        # Get root folders (no parent)
        folders = Folder.query.filter_by(parent_id=None).all()
    
    return jsonify([folder.to_dict() for folder in folders])

@folders_bp.route('/folders', methods=['POST'])
def create_folder():
    """Create a new folder"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Folder name is required'}), 400
    
    # Check if folder with same name exists in the same parent
    parent_id = data.get('parent_id')
    existing = Folder.query.filter_by(
        name=data['name'], 
        parent_id=parent_id
    ).first()
    
    if existing:
        return jsonify({'error': 'Folder with this name already exists in this location'}), 400
    
    folder = Folder(
        name=data['name'],
        parent_id=parent_id,
        created_by=session['user_id'],
        description=data.get('description', '')
    )
    
    try:
        db.session.add(folder)
        db.session.commit()
        return jsonify(folder.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create folder'}), 500

@folders_bp.route('/folders/<int:folder_id>', methods=['GET'])
def get_folder(folder_id):
    """Get a specific folder with its contents"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    folder = Folder.query.get_or_404(folder_id)
    
    # Get subfolders
    subfolders = Folder.query.filter_by(parent_id=folder_id).all()
    
    # Get documents in this folder
    documents = Document.query.filter_by(folder_id=folder_id).all()
    
    folder_data = folder.to_dict()
    folder_data['subfolders'] = [f.to_dict() for f in subfolders]
    folder_data['documents'] = [d.to_dict() for d in documents]
    
    return jsonify(folder_data)

@folders_bp.route('/folders/<int:folder_id>', methods=['PUT'])
def update_folder(folder_id):
    """Update a folder"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    folder = Folder.query.get_or_404(folder_id)
    
    # Check if user is admin or folder creator
    user = User.query.get(session['user_id'])
    if not user.is_admin and folder.created_by != session['user_id']:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update folder properties
    if 'name' in data:
        # Check if new name conflicts with existing folder
        existing = Folder.query.filter_by(
            name=data['name'], 
            parent_id=folder.parent_id
        ).filter(Folder.id != folder_id).first()
        
        if existing:
            return jsonify({'error': 'Folder with this name already exists in this location'}), 400
        
        folder.name = data['name']
    
    if 'description' in data:
        folder.description = data['description']
    
    if 'parent_id' in data:
        # Prevent moving folder into itself or its subfolders
        new_parent_id = data['parent_id']
        if new_parent_id == folder_id:
            return jsonify({'error': 'Cannot move folder into itself'}), 400
        
        # Check for circular reference
        if new_parent_id:
            parent = Folder.query.get(new_parent_id)
            if parent:
                current = parent
                while current:
                    if current.id == folder_id:
                        return jsonify({'error': 'Cannot move folder into its subfolder'}), 400
                    current = current.parent
        
        folder.parent_id = new_parent_id
    
    try:
        db.session.commit()
        return jsonify(folder.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update folder'}), 500

@folders_bp.route('/folders/<int:folder_id>', methods=['DELETE'])
def delete_folder(folder_id):
    """Delete a folder and optionally its contents"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    folder = Folder.query.get_or_404(folder_id)
    
    # Check if user is admin or folder creator
    user = User.query.get(session['user_id'])
    if not user.is_admin and folder.created_by != session['user_id']:
        return jsonify({'error': 'Permission denied'}), 403
    
    # Check if folder has contents
    has_subfolders = Folder.query.filter_by(parent_id=folder_id).count() > 0
    has_documents = Document.query.filter_by(folder_id=folder_id).count() > 0
    
    force_delete = request.args.get('force', 'false').lower() == 'true'
    
    if (has_subfolders or has_documents) and not force_delete:
        return jsonify({
            'error': 'Folder is not empty',
            'has_subfolders': has_subfolders,
            'has_documents': has_documents,
            'message': 'Use force=true parameter to delete folder and all its contents'
        }), 400
    
    try:
        if force_delete:
            # Delete all documents in folder (move to root or delete files)
            documents = Document.query.filter_by(folder_id=folder_id).all()
            for doc in documents:
                doc.folder_id = None  # Move to root instead of deleting
            
            # Recursively delete subfolders
            def delete_subfolder(parent_id):
                subfolders = Folder.query.filter_by(parent_id=parent_id).all()
                for subfolder in subfolders:
                    delete_subfolder(subfolder.id)
                    # Move documents to root
                    docs = Document.query.filter_by(folder_id=subfolder.id).all()
                    for doc in docs:
                        doc.folder_id = None
                    db.session.delete(subfolder)
            
            delete_subfolder(folder_id)
        
        db.session.delete(folder)
        db.session.commit()
        return jsonify({'message': 'Folder deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete folder'}), 500

@folders_bp.route('/folders/<int:folder_id>/breadcrumb', methods=['GET'])
def get_folder_breadcrumb(folder_id):
    """Get breadcrumb path for a folder"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    folder = Folder.query.get_or_404(folder_id)
    
    breadcrumb = []
    current = folder
    
    while current:
        breadcrumb.insert(0, {
            'id': current.id,
            'name': current.name
        })
        current = current.parent
    
    return jsonify(breadcrumb)

