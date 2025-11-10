"""
Routes pour la gestion des notes.
"""
import json
from datetime import datetime, timezone
from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from ...models import Note, Assignment, ActionLog
from ...services.note_service import NoteService
from ...repositories import ActionLogRepository

bp = Blueprint('notes', __name__)

# Instancier le service
note_service = NoteService()


@bp.post('/notes')
@jwt_required()
def create_note():
    """
    Créer une nouvelle note (requiert authentification).
    
    ✅ REFACTORÉ : Architecture 3 couches
    """
    data = request.get_json()
    current_user_id = int(get_jwt_identity())
    
    # ✅ Délégation au service
    note_dict = note_service.create_note(
        content=data.get("content"),
        creator_id=current_user_id,
        important=data.get("important", False)
    )
    
    # Log de création de note
    action_log = ActionLog(
        user_id=current_user_id,
        action_type="note_created",
        target_id=note_dict["id"],
        payload=json.dumps({"important": note_dict["important"]})
    )
    action_log_repo = ActionLogRepository()
    action_log_repo.save(action_log)
    
    return note_dict, 201


@bp.route('/notes', methods=['GET'])
@jwt_required()
def get_notes():
    """
    Get all notes with their assignments
    ---
    Returns list of notes created by OR assigned to current user
    Query Parameters:
      - filter: 'important', 'important_by_me', 'unread', 'received', 'sent', 'in_progress', 'completed'
      - sort: 'date_asc', 'date_desc', 'important_first'
      - q: search query (searches in note content)
      - page: page number (default: 1)
      - per_page: items per page (default: 20, max: 100)
    """
    current_user_id = int(get_jwt_identity())
    
    # Paramètres de pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Limiter per_page à 100 max pour éviter surcharge
    if per_page > 100:
        per_page = 100
    if per_page < 1:
        per_page = 20
    if page < 1:
        page = 1
    
    # Query de base - toujours LEFT JOIN pour voir toutes les notes accessibles
    filter_param = request.args.get('filter')
    
    query = Note.query.join(
        Assignment, Note.id == Assignment.note_id, isouter=True
    ).filter(
        or_(
            Note.creator_id == current_user_id,
            Assignment.user_id == current_user_id
        ),
        Note.delete_date.is_(None)  # Exclure les notes supprimées (soft delete)
    )
    
    # Recherche textuelle
    search_query = request.args.get('q', '').strip()
    if search_query:
        # Recherche insensible à la casse dans le contenu de la note
        search_pattern = f"%{search_query}%"
        query = query.filter(Note.content.ilike(search_pattern))
    
    # Filtre par créateur (pour afficher les notes d'un contact spécifique)
    creator_id = request.args.get('creator_id', type=int)
    if creator_id is not None:
        query = query.filter(Note.creator_id == creator_id)
    
    # Filtre direct par important (booléen)
    important_filter = request.args.get('important', type=lambda v: v.lower() == 'true')
    if important_filter is not None:
        query = query.filter(Note.important == important_filter)
    
    # Filtres
    if filter_param:
        if filter_param == 'important':
            # Notes marquées importantes par le créateur
            query = query.filter(Note.important == True)
        elif filter_param == 'important_by_me':
            # Notes marquées prioritaires par le destinataire
            query = query.filter(
                Assignment.user_id == current_user_id,
                Assignment.recipient_priority == True
            )
        elif filter_param == 'unread':
            # Assignations non lues
            query = query.filter(
                Assignment.user_id == current_user_id,
                Assignment.is_read == False
            )
        elif filter_param == 'received':
            # Notes assignées à l'utilisateur
            query = query.filter(Assignment.user_id == current_user_id)
        elif filter_param == 'sent':
            # Notes créées par l'utilisateur ET assignées à quelqu'un
            query = query.filter(
                Note.creator_id == current_user_id,
                Assignment.id.isnot(None)  # Doit avoir au moins 1 assignation
            )
        elif filter_param == 'in_progress':
            # Toutes les notes avec des assignations en cours (visibles par l'utilisateur)
            query = query.filter(
                Assignment.recipient_status == 'en_cours',
                Assignment.id.isnot(None)
            )
        elif filter_param == 'completed':
            # Toutes les notes avec des assignations terminées (visibles par l'utilisateur)
            query = query.filter(
                Assignment.recipient_status == 'terminé',
                Assignment.id.isnot(None)
            )
    
    # Tri
    sort_param = request.args.get('sort', 'date_desc')
    sort_by = request.args.get('sort_by')  # Support pour sort_by alternatif
    sort_order = request.args.get('sort_order', 'desc')  # Support pour sort_order alternatif
    
    # Utiliser sort_by/sort_order si fournis, sinon utiliser sort
    if sort_by:
        if sort_by == 'created_date':
            if sort_order == 'asc':
                query = query.order_by(Note.created_date.asc())
            else:
                query = query.order_by(Note.created_date.desc())
        elif sort_by == 'important':
            query = query.order_by(Note.important.desc(), Note.created_date.desc())
        else:
            # Par défaut : date décroissante
            query = query.order_by(Note.created_date.desc())
    elif sort_param == 'date_asc':
        query = query.order_by(Note.created_date.asc())
    elif sort_param == 'date_desc':
        query = query.order_by(Note.created_date.desc())
    elif sort_param == 'important_first':
        # Important d'abord, puis par date décroissante
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
    
    return {
        "notes": [note.to_dict() for note in pagination.items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev
    }, 200


@bp.get('/notes/<int:note_id>')
@jwt_required()
def get_note(note_id):
    """
    Récupérer une note par son ID avec infos contextuelles selon le rôle.
    
    ✅ REFACTORÉ : Architecture 3 couches
    Cette route délègue toute la logique métier au NoteService.
    """
    current_user_id = int(get_jwt_identity())
    
    # ✅ Délégation complète au service
    response = note_service.get_note_for_user(note_id, current_user_id)
    
    return response


@bp.get('/notes/<int:note_id>/details')
@jwt_required()
def get_note_details(note_id):
    """
    Récupérer les détails d'une note sans contenu, pour survol ou audit côté front.
    
    ✅ REFACTORÉ : Architecture 3 couches
    """
    current_user_id = int(get_jwt_identity())
    
    # ✅ Délégation au service
    return note_service.get_note_details(note_id, current_user_id)


@bp.get('/notes/<int:note_id>/assignments')
@jwt_required()
def get_note_assignments(note_id):
    """
    Récupérer tous les destinataires avec leur statut (créateur uniquement).
    
    ✅ REFACTORÉ : Architecture 3 couches
    """
    current_user_id = int(get_jwt_identity())
    
    # ✅ Délégation au service
    return note_service.get_note_assignments(note_id, current_user_id)


@bp.put('/notes/<int:note_id>')
@jwt_required()
def update_note(note_id):
    """
    Mettre à jour une note (authentifié).
    
    ✅ REFACTORÉ : Architecture 3 couches
    """
    data = request.get_json()
    current_user_id = int(get_jwt_identity())
    
    # ✅ Délégation au service
    note_dict = note_service.update_note(
        note_id=note_id,
        user_id=current_user_id,
        content=data.get("content"),
        important=data.get("important")
    )
    
    # Log de modification de note
    action_log = ActionLog(
        user_id=current_user_id,
        action_type="note_updated",
        target_id=note_dict["id"],
        payload=json.dumps({"important": note_dict["important"]})
    )
    action_log_repo = ActionLogRepository()
    action_log_repo.save(action_log)
    
    return note_dict


@bp.get('/notes/orphans')
@jwt_required()
def get_orphan_notes():
    """
    Récupérer les notes orphelines (sans aucune assignation active).
    Ces notes peuvent être supprimées définitivement par le créateur.
    
    ✅ REFACTORÉ : Architecture 3 couches
    """
    current_user_id = int(get_jwt_identity())
    
    # ✅ Délégation au service
    orphan_notes = note_service.get_orphan_notes(current_user_id)
    
    return {"notes": orphan_notes, "count": len(orphan_notes)}


@bp.delete('/notes/<int:note_id>')
@jwt_required()
def delete_note(note_id):
    """
    Soft delete : pose la date de suppression et enregistre qui a supprimé.
    Autorisé pour le créateur OU le destinataire de la note (traçabilité complète).
    
    ✅ REFACTORÉ : Architecture 3 couches
    """
    current_user_id = int(get_jwt_identity())
    
    # ✅ Délégation au service
    note_dict = note_service.delete_note(note_id, current_user_id)
    
    # Vérifier si c'est le créateur pour le log
    is_creator = note_dict["creator_id"] == current_user_id
    
    # Log de suppression de note
    action_log = ActionLog(
        user_id=current_user_id,
        action_type="note_deleted",
        target_id=note_dict["id"],
        payload=json.dumps({"is_creator": is_creator})
    )
    action_log_repo = ActionLogRepository()
    action_log_repo.save(action_log)
    
    return note_dict


@bp.get('/notes/<int:note_id>/deletion-history')
@jwt_required()
def get_deletion_history(note_id):
    """
    Récupérer l'historique des suppressions d'assignations pour une note.
    Accessible uniquement au créateur de la note.
    
    ✅ REFACTORÉ : Architecture 3 couches
    """
    current_user_id = int(get_jwt_identity())
    
    # ✅ Délégation au service
    deletions = note_service.get_deletion_history(note_id, current_user_id)
    
    return {"deletions": deletions}


@bp.get('/notes/<int:note_id>/completion-history')
@jwt_required()
def get_completion_history(note_id):
    """
    Récupérer l'historique des completions d'assignations pour une note.
    Accessible uniquement au créateur de la note.
    Retourne uniquement les completions actives (celles qui n'ont pas été décochées).
    
    ✅ REFACTORÉ : Architecture 3 couches
    """
    current_user_id = int(get_jwt_identity())
    
    # ✅ Délégation au service
    completions = note_service.get_completion_history(note_id, current_user_id)
    
    return {"completions": completions}
