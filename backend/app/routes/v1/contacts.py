"""
Routes pour la gestion des contacts.
"""
import json
from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from ... import db
from ...models import Contact, User, ActionLog

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
    
    # Log de création de contact
    action_log = ActionLog(
        user_id=current_user_id,
        action_type="contact_created",
        target_id=contact.id,
        payload=json.dumps({"contact_username": contact_user.username, "nickname": data["nickname"]})
    )
    db.session.add(action_log)
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
        # is_mutual est déjà dans contact.to_dict()
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
            "is_self": False,
            "is_mutual": contact.is_mutual()
        })
    
    return assignable

@bp.get('/contacts/<int:contact_id>')
@jwt_required()
def get_contact(contact_id):
    """Récupérer un contact par son ID."""
    contact = Contact.query.get_or_404(contact_id)
    current_user_id = int(get_jwt_identity())
    
    # Vérifier que l'utilisateur est bien le propriétaire du contact
    if contact.user_id != current_user_id:
        abort(403, description="You can only view your own contacts")
    
    return contact.to_dict()

@bp.put('/contacts/<int:contact_id>')
@jwt_required()
def update_contact(contact_id):
    """Mettre à jour un contact."""
    contact = Contact.query.get_or_404(contact_id)
    current_user_id = int(get_jwt_identity())
    
    # Vérifier que l'utilisateur est bien le propriétaire du contact
    if contact.user_id != current_user_id:
        abort(403, description="You can only update your own contacts")
    
    data = request.get_json()
    
    if "nickname" in data:
        contact.nickname = data["nickname"]
        
    if "contact_action" in data:
        contact.contact_action = data["contact_action"]
        
    db.session.commit()
    
    # Log de modification de contact
    action_log = ActionLog(
        user_id=current_user_id,
        action_type="contact_updated",
        target_id=contact.id,
        payload=json.dumps({"nickname": contact.nickname})
    )
    db.session.add(action_log)
    db.session.commit()
    
    return contact.to_dict()

@bp.delete('/contacts/<int:contact_id>')
@jwt_required()
def delete_contact(contact_id):
    """Supprimer un contact."""
    contact = Contact.query.get_or_404(contact_id)
    current_user_id = int(get_jwt_identity())
    
    # Vérifier que l'utilisateur est bien le propriétaire du contact
    if contact.user_id != current_user_id:
        abort(403, description="You can only delete your own contacts")
    
    # Sauvegarder info pour le log
    contact_username = contact.contact_user.username if contact.contact_user else None
    
    db.session.delete(contact)
    db.session.commit()
    
    # Log de suppression de contact
    action_log = ActionLog(
        user_id=current_user_id,
        action_type="contact_deleted",
        target_id=contact_id,
        payload=json.dumps({"contact_username": contact_username})
    )
    db.session.add(action_log)
    db.session.commit()
    
    return {"deleted": True}

@bp.get('/contacts/<int:contact_id>/notes')
@jwt_required()
def get_contact_notes(contact_id):
    """
    Récupérer toutes les notes échangées avec un contact spécifique.
    Retourne les notes où :
    - L'utilisateur connecté est créateur ET le contact est destinataire
    - OU le contact est créateur ET l'utilisateur connecté est destinataire
    
    Supporte les mêmes paramètres de pagination que GET /notes
    """
    from ...models import Note, Assignment
    from sqlalchemy import and_, or_
    
    current_user_id = int(get_jwt_identity())
    
    # Vérifier que le contact existe et appartient à l'utilisateur
    contact = Contact.query.get_or_404(contact_id)
    if contact.user_id != current_user_id:
        abort(403, description="You can only view notes for your own contacts")
    
    contact_user_id = contact.contact_user_id
    
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Limiter per_page
    if per_page > 100:
        per_page = 100
    if per_page < 1:
        per_page = 20
    if page < 1:
        page = 1
    
    # Query : notes échangées entre l'utilisateur connecté et le contact
    # Cas 1 : Je suis créateur ET le contact est destinataire
    # Cas 2 : Le contact est créateur ET je suis destinataire
    query = Note.query.join(
        Assignment, Note.id == Assignment.note_id
    ).filter(
        or_(
            # Cas 1 : mes notes envoyées à ce contact
            and_(
                Note.creator_id == current_user_id,
                Assignment.user_id == contact_user_id
            ),
            # Cas 2 : notes du contact reçues par moi
            and_(
                Note.creator_id == contact_user_id,
                Assignment.user_id == current_user_id
            )
        )
    )
    
    # Filtres optionnels
    filter_param = request.args.get('filter')
    if filter_param:
        if filter_param == 'received':
            # Seulement les notes reçues de ce contact
            query = query.filter(
                Note.creator_id == contact_user_id,
                Assignment.user_id == current_user_id
            )
        elif filter_param == 'sent':
            # Seulement mes notes envoyées à ce contact
            query = query.filter(
                Note.creator_id == current_user_id,
                Assignment.user_id == contact_user_id
            )
        elif filter_param == 'unread':
            # Notes non lues (si je suis destinataire)
            query = query.filter(
                Note.creator_id == contact_user_id,
                Assignment.user_id == current_user_id,
                Assignment.is_read == False
            )
        elif filter_param == 'important':
            # Notes marquées importantes par le créateur
            query = query.filter(Note.important == True)
    
    # Tri
    sort_param = request.args.get('sort', 'date_desc')
    if sort_param == 'date_asc':
        query = query.order_by(Note.created_date.asc())
    elif sort_param == 'important_first':
        query = query.order_by(Note.important.desc(), Note.created_date.desc())
    else:
        # Par défaut : date décroissante
        query = query.order_by(Note.created_date.desc())
    
    # Pagination
    pagination = query.distinct().paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Récupérer les informations du contact pour la réponse
    contact_info = {
        "id": contact.id,
        "contact_user_id": contact_user_id,
        "username": contact.contact_user.username,
        "nickname": contact.nickname,
        "is_mutual": contact.is_mutual()
    }
    
    return {
        "contact": contact_info,
        "notes": [note.to_dict() for note in pagination.items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev
    }, 200
