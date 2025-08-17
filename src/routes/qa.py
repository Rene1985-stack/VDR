from flask import Blueprint, jsonify, request, session
from src.models.user import Question, Answer, User, db
from src.routes.user import login_required

qa_bp = Blueprint('qa', __name__)

@qa_bp.route('/questions', methods=['GET'])
@login_required
def get_questions():
    questions = Question.query.order_by(Question.asked_at.desc()).all()
    return jsonify([question.to_dict() for question in questions])

@qa_bp.route('/questions', methods=['POST'])
@login_required
def create_question():
    data = request.json
    
    if not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Title and content are required'}), 400
    
    question = Question(
        title=data['title'],
        content=data['content'],
        asked_by=session['user_id']
    )
    
    db.session.add(question)
    db.session.commit()
    
    return jsonify({'message': 'Question created successfully', 'question': question.to_dict()}), 201

@qa_bp.route('/questions/<int:question_id>', methods=['GET'])
@login_required
def get_question(question_id):
    question = Question.query.get_or_404(question_id)
    return jsonify(question.to_dict())

@qa_bp.route('/questions/<int:question_id>', methods=['PUT'])
@login_required
def update_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    # Only allow the asker or admin to update
    user = User.query.get(session['user_id'])
    if question.asked_by != session['user_id'] and not user.is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.json
    question.title = data.get('title', question.title)
    question.content = data.get('content', question.content)
    
    db.session.commit()
    return jsonify(question.to_dict())

@qa_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@login_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    # Only allow the asker or admin to delete
    user = User.query.get(session['user_id'])
    if question.asked_by != session['user_id'] and not user.is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(question)
    db.session.commit()
    
    return jsonify({'message': 'Question deleted successfully'}), 200

@qa_bp.route('/questions/<int:question_id>/answers', methods=['GET'])
@login_required
def get_answers(question_id):
    question = Question.query.get_or_404(question_id)
    answers = Answer.query.filter_by(question_id=question_id).order_by(Answer.answered_at.asc()).all()
    return jsonify([answer.to_dict() for answer in answers])

@qa_bp.route('/questions/<int:question_id>/answers', methods=['POST'])
@login_required
def create_answer(question_id):
    question = Question.query.get_or_404(question_id)
    data = request.json
    
    if not data.get('content'):
        return jsonify({'error': 'Content is required'}), 400
    
    answer = Answer(
        content=data['content'],
        question_id=question_id,
        answered_by=session['user_id']
    )
    
    db.session.add(answer)
    
    # Mark question as answered
    question.is_answered = True
    
    db.session.commit()
    
    return jsonify({'message': 'Answer created successfully', 'answer': answer.to_dict()}), 201

@qa_bp.route('/answers/<int:answer_id>', methods=['GET'])
@login_required
def get_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    return jsonify(answer.to_dict())

@qa_bp.route('/answers/<int:answer_id>', methods=['PUT'])
@login_required
def update_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    
    # Only allow the answerer or admin to update
    user = User.query.get(session['user_id'])
    if answer.answered_by != session['user_id'] and not user.is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.json
    answer.content = data.get('content', answer.content)
    
    db.session.commit()
    return jsonify(answer.to_dict())

@qa_bp.route('/answers/<int:answer_id>', methods=['DELETE'])
@login_required
def delete_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    
    # Only allow the answerer or admin to delete
    user = User.query.get(session['user_id'])
    if answer.answered_by != session['user_id'] and not user.is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    
    question_id = answer.question_id
    db.session.delete(answer)
    
    # Check if question still has answers
    remaining_answers = Answer.query.filter_by(question_id=question_id).count()
    if remaining_answers == 0:
        question = Question.query.get(question_id)
        if question:
            question.is_answered = False
    
    db.session.commit()
    
    return jsonify({'message': 'Answer deleted successfully'}), 200

