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
@jwt_required()
def list_contacts():
    """
    Lister les contacts de l'utilisateur connecté.
    Inclut l'utilisateur lui-même en premier (pour s'auto-assigner des notes).
    """
    current_user_id = int(get_jwt_identity())  # Récupère l'ID de l'utilisateur CONNECTÉ
    current_user = db.session.get(User, current_user_id)  # Seulement cet utilisateur CONNECTÉ
    
    # Construire la liste avec l'utilisateur lui-même en premier
    result = []
    
    # Ajouter soi-même
    result.append({
        "id": current_user.id,  # SON propre ID
        "user_id": current_user.id,
        "contact_user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "nickname": "Moi",
        "is_self": True,
        "contact_action": None,
        "created_date": None
    })
    
    # Ajouter SES contacts
    contacts = Contact.query.filter_by(user_id=current_user_id).order_by(Contact.nickname.asc()).all()  # Filtré par SON user_id
    for contact in contacts:
        contact_dict = contact.to_dict()
        contact_dict["username"] = contact.contact_user.username
        contact_dict["email"] = contact.contact_user.email
        contact_dict["is_self"] = False
        result.append(contact_dict)
    
    return result

@bp.get('/contacts/assignable')  
@jwt_required()
def list_assignable_users():
    """
    Liste les utilisateurs à qui on peut assigner des notes :
    - L'utilisateur courant lui-même (pour s'auto-assigner)
    - Ses contacts
    """
    current_user_id = int(get_jwt_identity())  # L'utilisateur connecté
    current_user = db.session.get(User, current_user_id)  # Lui uniquement
    
    # Construire la liste : soi-même + contacts
    assignable = []
    
    # Ajouter soi-même en premier
    assignable.append({
        "id": current_user.id,  # ← SON ID
        "username": current_user.username,
        "email": current_user.email,
        "nickname": "Moi",  # Affichage spécial
        "is_self": True
    })
    
    # Ajouter SES contacts
    contacts = Contact.query.filter_by(user_id=current_user_id).all()  # SES contacts seulement
    for contact in contacts:
        assignable.append({
            "id": contact.contact_user.id,
            "username": contact.contact_user.username,
            "email": contact.contact_user.email,
            "nickname": contact.nickname,
            "is_self": False
        })
    
    return assignable

@bp.get('/contacts/<int:contact_id>')
@jwt_required()
def get_contact(contact_id):
    """Récupérer un contact par son ID."""
    contact = Contact.query.get_or_404(contact_id)
    return contact.to_dict()

@bp.put('/contacts/<int:contact_id>')
@jwt_required()
def update_contact(contact_id):
    """Mettre à jour un contact."""
    contact = Contact.query.get_or_404(contact_id)
    data = request.get_json()
    
    if "nickname" in data:
        contact.nickname = data["nickname"]
        
    if "contact_action" in data:
        contact.contact_action = data["contact_action"]
        
    db.session.commit()
    return contact.to_dict()

@bp.delete('/contacts/<int:contact_id>')
@jwt_required()
def delete_contact(contact_id):
    """Supprimer un contact."""
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return {"deleted": True}
