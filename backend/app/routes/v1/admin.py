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
        "notes_by_status": {
            "en_cours": Note.query.filter_by(status="en_cours").count(),
            # Ajouter d'autres statuts si nécessaire
        },
        "important_notes": Note.query.filter_by(important=True).count(),
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
    return jsonify({"msg": f"User {user.username} deleted successfully"}), 200


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
        "msg": f"User {user.username} role updated to {new_role}",
        "user": user.to_dict()
    }), 200
