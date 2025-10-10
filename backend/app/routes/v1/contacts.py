"""
Routes pour la gestion des contacts.
"""
from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from ... import db
from ...models import Contact, User

bp = Blueprint('contacts', __name__)

@bp.post('/contacts')
@jwt_required()
def create_contact():
    """Ajouter un utilisateur existant à ses contacts."""
    data = request.get_json()
    if not data or not data.get("contact_username") or not data.get("nickname"):
        abort(400, description="Missing contact_username or nickname")
    
    current_user_id = int(get_jwt_identity())
    
    # Vérifier que l'utilisateur à ajouter existe
    contact_user = User.query.filter_by(username=data["contact_username"]).first()
    if not contact_user:
        abort(404, description="User not found")
    
    # Vérifier qu'on ne s'ajoute pas soi-même
    if contact_user.id == current_user_id:
        abort(400, description="Cannot add yourself as contact")
        
    # Vérifier que ce contact n'existe pas déjà
    existing_contact = Contact.query.filter_by(
        user_id=current_user_id, 
        contact_user_id=contact_user.id
    ).first()
    if existing_contact:
        abort(400, description="Contact already exists")
        
    contact = Contact(
        user_id=current_user_id,
        contact_user_id=contact_user.id,
        nickname=data["nickname"],
        contact_action=data.get("contact_action")
    )
    db.session.add(contact)
    db.session.commit()
    return contact.to_dict(), 201

@bp.get('/contacts')
def list_contacts():
    """Lister tous les contacts."""
    contacts = Contact.query.order_by(Contact.name.asc()).all()
    return [c.to_dict() for c in contacts]

@bp.get('/contacts/<int:contact_id>')
def get_contact(contact_id):
    """Récupérer un contact par son ID."""
    contact = Contact.query.get_or_404(contact_id)
    return contact.to_dict()

@bp.put('/contacts/<int:contact_id>')
def update_contact(contact_id):
    """Mettre à jour un contact."""
    contact = Contact.query.get_or_404(contact_id)
    data = request.get_json()
    
    if "name" in data:
        contact.name = data["name"]
        
    if "email" in data:
        # Vérifier que le nouvel email n'existe pas déjà
        existing_contact = Contact.query.filter_by(email=data["email"]).filter(Contact.id != contact_id).first()
        if existing_contact:
            abort(400, description="Email already exists")
        contact.email = data["email"]
        
    if "phone" in data:
        contact.phone = data["phone"]
        
    if "company" in data:
        contact.company = data["company"]
        
    if "notes" in data:
        contact.notes = data["notes"]
        
    db.session.commit()
    return contact.to_dict()

@bp.delete('/contacts/<int:contact_id>')
def delete_contact(contact_id):
    """Supprimer un contact."""
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return {"deleted": True}