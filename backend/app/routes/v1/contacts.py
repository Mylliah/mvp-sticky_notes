"""
Routes pour la gestion des contacts.
"""
from flask import Blueprint, request, abort
from .. import db
from ..models import Contact

bp = Blueprint('contacts', __name__, url_prefix='/contacts')

@bp.post('')
def create_contact():
    """Créer un nouveau contact."""
    data = request.get_json()
    if not data or not data.get("name") or not data.get("email"):
        abort(400, description="Missing name or email")
        
    # Vérifier que l'email n'existe pas déjà
    existing_contact = Contact.query.filter_by(email=data["email"]).first()
    if existing_contact:
        abort(400, description="Email already exists")
        
    contact = Contact(
        name=data["name"],
        email=data["email"],
        phone=data.get("phone"),
        company=data.get("company"),
        notes=data.get("notes")
    )
    db.session.add(contact)
    db.session.commit()
    return contact.to_dict(), 201

@bp.get('')
def list_contacts():
    """Lister tous les contacts."""
    contacts = Contact.query.order_by(Contact.name.asc()).all()
    return [c.to_dict() for c in contacts]

@bp.get('/<int:contact_id>')
def get_contact(contact_id):
    """Récupérer un contact par son ID."""
    contact = Contact.query.get_or_404(contact_id)
    return contact.to_dict()

@bp.put('/<int:contact_id>')
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

@bp.delete('/<int:contact_id>')
def delete_contact(contact_id):
    """Supprimer un contact."""
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return {"deleted": True}