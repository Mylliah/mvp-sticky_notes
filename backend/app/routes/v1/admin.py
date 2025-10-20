"""
Routes d'administration (réservées aux administrateurs).
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ... import db
from ...models import User, Note, Contact, Assignment, ActionLog
from ...decorators import admin_required

bp = Blueprint('admin', __name__)


@bp.get('/admin/users')
@jwt_required()
@admin_required()
def list_all_users():
    """
    Liste TOUS les utilisateurs (admin only).
    """
    users = User.query.order_by(User.id.asc()).all()
    return jsonify([u.to_dict() for u in users]), 200


@bp.get('/admin/notes')
@jwt_required()
@admin_required()
def list_all_notes():
    """
    Liste TOUTES les notes de tous les utilisateurs (admin only).
    """
    notes = Note.query.order_by(Note.id.desc()).all()
    return jsonify([n.to_dict() for n in notes]), 200


@bp.get('/admin/stats')
@jwt_required()
@admin_required()
def get_stats():
    """
    Statistiques globales de la plateforme (admin only).
    """
    stats = {
        "total_users": User.query.count(),
        "total_notes": Note.query.count(),
        "total_contacts": Contact.query.count(),
        "total_assignments": Assignment.query.count(),
        "total_action_logs": ActionLog.query.count(),
        "important_notes": Note.query.filter_by(important=True).count(),
        "deleted_notes": Note.query.filter(Note.delete_date.isnot(None)).count(),
    }
    return jsonify(stats), 200


@bp.delete('/admin/users/<int:user_id>')
@jwt_required()
@admin_required()
def delete_user_admin(user_id):
    """
    Supprimer un utilisateur (admin only).
    Attention : supprime aussi toutes ses notes, contacts, etc. (cascade).
    """
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200


@bp.put('/admin/users/<int:user_id>/role')
@jwt_required()
@admin_required()
def update_user_role(user_id):
    """
    Changer le rôle d'un utilisateur (admin only).
    """
    from flask import request
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if not data or 'role' not in data:
        return jsonify({"error": "Missing role field"}), 400
    
    new_role = data['role']
    if new_role not in ['user', 'admin']:
        return jsonify({"error": "Invalid role. Must be 'user' or 'admin'"}), 400
    
    user.role = new_role
    db.session.commit()
    
    return jsonify({
        "message": "User role updated",
        "role": user.role,
        "user": user.to_dict()
    }), 200


# ========== NOTES ADMIN CRUD ==========

@bp.get('/admin/notes/<int:note_id>')
@jwt_required()
@admin_required()
def get_note_admin(note_id):
    """
    Récupérer une note spécifique (admin only).
    Accès complet à n'importe quelle note, même supprimée.
    """
    note = Note.query.get_or_404(note_id)
    return jsonify(note.to_dict()), 200


@bp.put('/admin/notes/<int:note_id>')
@jwt_required()
@admin_required()
def update_note_admin(note_id):
    """
    Modifier une note (admin only).
    L'admin peut modifier n'importe quelle note pour corriger un problème.
    """
    from flask import request
    note = Note.query.get_or_404(note_id)
    data = request.get_json()
    
    # Update fields if provided
    if 'content' in data:
        note.content = data['content']
    if 'important' in data:
        note.important = data['important']
    if 'status' in data:
        note.status = data['status']
    
    db.session.commit()
    return jsonify({
        "message": "Note updated by admin",
        "note": note.to_dict()
    }), 200


@bp.delete('/admin/notes/<int:note_id>')
@jwt_required()
@admin_required()
def delete_note_admin(note_id):
    """
    Supprimer une note (hard delete, admin only).
    Suppression définitive pour résoudre des problèmes.
    """
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Note permanently deleted by admin"}), 200


# ========== CONTACTS ADMIN CRUD ==========

@bp.get('/admin/contacts')
@jwt_required()
@admin_required()
def list_all_contacts():
    """
    Liste TOUS les contacts (admin only).
    """
    contacts = Contact.query.order_by(Contact.id.asc()).all()
    return jsonify([c.to_dict() for c in contacts]), 200


@bp.get('/admin/contacts/<int:contact_id>')
@jwt_required()
@admin_required()
def get_contact_admin(contact_id):
    """
    Récupérer un contact spécifique (admin only).
    """
    contact = Contact.query.get_or_404(contact_id)
    return jsonify(contact.to_dict()), 200


@bp.put('/admin/contacts/<int:contact_id>')
@jwt_required()
@admin_required()
def update_contact_admin(contact_id):
    """
    Modifier un contact (admin only).
    """
    from flask import request
    contact = Contact.query.get_or_404(contact_id)
    data = request.get_json()
    
    if 'nickname' in data:
        contact.nickname = data['nickname']
    
    db.session.commit()
    return jsonify({
        "message": "Contact updated by admin",
        "contact": contact.to_dict()
    }), 200


@bp.delete('/admin/contacts/<int:contact_id>')
@jwt_required()
@admin_required()
def delete_contact_admin(contact_id):
    """
    Supprimer un contact (admin only).
    """
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({"message": "Contact deleted by admin"}), 200


# ========== ASSIGNMENTS ADMIN CRUD ==========

@bp.get('/admin/assignments')
@jwt_required()
@admin_required()
def list_all_assignments():
    """
    Liste TOUTES les assignations (admin only).
    """
    assignments = Assignment.query.order_by(Assignment.id.desc()).all()
    return jsonify([a.to_dict() for a in assignments]), 200


@bp.get('/admin/assignments/<int:assignment_id>')
@jwt_required()
@admin_required()
def get_assignment_admin(assignment_id):
    """
    Récupérer une assignation spécifique (admin only).
    """
    assignment = Assignment.query.get_or_404(assignment_id)
    return jsonify(assignment.to_dict()), 200


@bp.put('/admin/assignments/<int:assignment_id>')
@jwt_required()
@admin_required()
def update_assignment_admin(assignment_id):
    """
    Modifier une assignation (admin only).
    """
    from flask import request
    assignment = Assignment.query.get_or_404(assignment_id)
    data = request.get_json()
    
    if 'is_read' in data:
        assignment.is_read = data['is_read']
    if 'recipient_priority' in data:
        assignment.recipient_priority = data['recipient_priority']
    if 'recipient_status' in data:
        assignment.recipient_status = data['recipient_status']
    if 'user_id' in data:
        assignment.user_id = data['user_id']
    
    db.session.commit()
    return jsonify({
        "message": "Assignment updated by admin",
        "assignment": assignment.to_dict()
    }), 200


@bp.delete('/admin/assignments/<int:assignment_id>')
@jwt_required()
@admin_required()
def delete_assignment_admin(assignment_id):
    """
    Supprimer une assignation (admin only).
    """
    assignment = Assignment.query.get_or_404(assignment_id)
    db.session.delete(assignment)
    db.session.commit()
    return jsonify({"message": "Assignment deleted by admin"}), 200
