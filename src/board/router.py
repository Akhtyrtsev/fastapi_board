from fastapi import APIRouter, status, HTTPException, Depends
from starlette.status import HTTP_204_NO_CONTENT
from datetime import datetime
from src.auth.models import User as ModelUser
from src.auth.dependencies import get_current_user, RoleChecker
from src.board.models import (
    Profile as ModelProfile,
    Project as ModelProject,
    Ticket as ModelTicket,
)
from typing import List, Union
from src.board.schema import Profile as SchemaProfile
from src.auth.schema import UserUpdate as SchemaUser

from fastapi_sqlalchemy import db

from src.board.schema import (
    ProfileWithId as SchemaProfileWithId,
    Project as ProjectSchema,
    ProjectChange as ProjectChangeSchema,
    Ticket as TicketSchema,
    TicketChange as TicketChangeSchema,

)

router = APIRouter(prefix="/board")

admin_permission = RoleChecker(["admin"])


@router.get('/profiles', summary='Get list of profiles', dependencies=[Depends(admin_permission)])
async def get_profiles(user: ModelUser = Depends(get_current_user)):
    profiles_request = db.session.query(ModelProfile).all()
    response = [SchemaProfileWithId(id=profile.id, user_id=profile.user_id, first_name=profile.first_name,
                                    last_name=profile.last_name,
                                    phone_number=profile.phone_number, avatar_url=profile.avatar_url)
                for profile in profiles_request]

    return response


@router.get('/my_profile', summary='Get current user profile', response_model=SchemaProfileWithId)
async def get_profile(user: ModelUser = Depends(get_current_user)):
    profile = db.session.query(ModelProfile).filter_by(user_id=user.id).first()
    response = SchemaProfileWithId(id=profile.id, user_id=profile.user_id, first_name=profile.first_name,
                                   last_name=profile.last_name, phone_number=profile.phone_number,
                                   avatar_url=profile.avatar_url)

    return response


@router.post('/my_profile', summary='Create profile', response_model=SchemaProfileWithId)
async def create_profile(data: SchemaProfile, user: ModelUser = Depends(get_current_user)):
    user_id = data.user_id if user.role == "admin" else user.id
    db_profile = ModelProfile(user_id=user_id, first_name=data.first_name, last_name=data.last_name, phone_number=data.phone_number,
                              avatar_url=data.avatar_url)

    db.session.add(db_profile)
    db.session.commit()
    response = SchemaProfileWithId(id=db_profile.id, user_id=db_profile.user_id, first_name=db_profile.first_name,
                                   last_name=db_profile.last_name, phone_number=db_profile.phone_number,
                                   avatar_url=db_profile.avatar_url)
    return response


@router.patch('/my_profile', summary='Patch current user profile', response_model=SchemaProfileWithId)
async def update_profile(data: SchemaProfile, user: ModelUser = Depends(get_current_user)):
    profile = db.session.query(ModelProfile).filter_by(user_id=user.id).first()
    stored_item_model = SchemaProfileWithId(id=profile.id, user_id=profile.user_id, first_name=profile.first_name,
                                            last_name=profile.last_name, phone_number=profile.phone_number,
                                            avatar_url=profile.avatar_url)
    update_data = data.dict(exclude_unset=True)
    updated_item = stored_item_model.copy(update=update_data)
    db.session.query(ModelProfile).filter_by(id=profile.id).update(updated_item.dict(), synchronize_session=False)
    db.session.commit()
    return updated_item


@router.get('/projects', summary='Get list of projects')
async def get_projects(user: ModelUser = Depends(get_current_user)):
    if user.role == "admin":
        projects_request = db.session.query(ModelProject).all()
    else:
        projects_request = db.session.query(ModelProject).filter_by(user_id=user.id)

    response = [ProjectSchema(id=project.id, user_id=project.user_id, name=project.name,
                              description=project.description, created=project.created, updated=project.updated)
                for project in projects_request]

    return response


@router.get('/projects/{project_id}', summary='Get list of projects')
async def retrieve_project(project_id: int, user: ModelUser = Depends(get_current_user)):
    if user.role == "admin":
        projects_request = db.session.query(ModelProject).all()
    else:
        projects_request = db.session.query(ModelProject).filter_by(user_id=user.id)
    projects_request = projects_request.filter_by(id=project_id).first()
    if not projects_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )
    response = ProjectSchema(id=projects_request.id, user_id=projects_request.user_id, name=projects_request.name,
                              description=projects_request.description, created=projects_request.created, updated=projects_request.updated)
    return response


@router.post('/projects', summary="Create new project", response_model=ProjectSchema)
async def create_project(data: ProjectChangeSchema, user: ModelUser = Depends(get_current_user)):
    user_id = data.user_id if user.role == "admin" else user.id # only admins are allowed to assign projects not to themself
    db_project = ModelProject(name=data.name, description=data.description, user_id=user_id)
    db.session.add(db_project)
    db.session.commit()    # saving user to database
    response = ProjectSchema(id=db_project.id, name=db_project.name, description=db_project.description,
                             user_id=db_project.user_id,
                             created=db_project.created,
                             updated=db_project.updated)
    return response


@router.patch('/projects/{project_id}', summary="Update project", response_model=ProjectSchema)
async def update_project(project_id: int, data: ProjectChangeSchema, user: ModelUser = Depends(get_current_user)):
    if user.role != "admin":
        db_project = db.session.query(ModelProject).filter_by(user_id=user.id)
    else:
        db_project = db.session.query(ModelProject).all()
    db_project = db_project.filter_by(id=project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )
    project_stored = ProjectSchema(id=db_project.id, name=db_project.name, description=db_project.description,
                                   user_id=db_project.user_id,
                                   created=db_project.created
                                   )
    update_data = data.dict(exclude_unset=True)
    updated_item = project_stored.copy(update=update_data)
    updated_item.updated = datetime.utcnow()
    db.session.query(ModelProject).filter_by(id=project_id).update(updated_item.dict(), synchronize_session=False)
    db.session.commit()
    return updated_item


@router.delete("/projects/{project_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, user: ModelUser = Depends(get_current_user)):
    if user.role != "admin":
        db_project = db.session.query(ModelProject).filter_by(user_id=user.id)
    else:
        db_project = db.session.query(ModelProject).all()
    db_project = db_project.filter_by(id=project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )
    db.session.delete(db_project)
    db.session.commit()
    return None

###############


@router.get('/tickets', summary='Get list of tickets')
async def get_tickets(project_id: Union[int, None] = None, user: ModelUser = Depends(get_current_user)):
    if user.role == "admin":
        tickets_request = db.session.query(ModelTicket).all()
    else:
        tickets_request = db.session.query(ModelTicket).join(ModelTicket.project).filter_by(user_id=user.id)
    if project_id:
        tickets_request = tickets_request.filter(ModelTicket.project_id == project_id)

    response = [TicketSchema(id=ticket.id,
                             project_id=ticket.project_id,
                             name=ticket.name,
                             description=ticket.description,
                             status=ticket.status,
                             created=ticket.created,
                             updated=ticket.updated
                             )
                for ticket in tickets_request]

    return response


@router.get('/tickets/{ticket_id}', summary='Get ticket by id')
async def retrieve_tickets(ticket_id: int, user: ModelUser = Depends(get_current_user)):
    if user.role == "admin":
        tickets_request = db.session.query(ModelTicket).all()
    else:
        tickets_request = db.session.query(ModelTicket).join(ModelTicket.project).filter_by(user_id=user.id)
    tickets_request = tickets_request.filter(ModelTicket.id == ticket_id).first()
    if not tickets_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )
    response = TicketSchema(id=tickets_request.id, project_id=tickets_request.project_id, name=tickets_request.name,
                            description=tickets_request.description, status=tickets_request.status,
                            created=tickets_request.created, updated=tickets_request.updated)
    return response


@router.post('/tickets', summary="Create new ticket", response_model=TicketSchema)
async def create_tickets(data: TicketChangeSchema, user: ModelUser = Depends(get_current_user)):
    db_ticket = ModelTicket(name=data.name, description=data.description, project_id=data.project_id, status=data.status)
    db.session.add(db_ticket)
    db.session.commit()    # saving user to database
    response = TicketSchema(id=db_ticket.id, name=db_ticket.name, description=db_ticket.description,
                            project_id=db_ticket.project_id,
                            status=db_ticket.status,
                            created=db_ticket.created,
                            updated=db_ticket.updated)
    return response


@router.patch('/tickets/{ticket_id}', summary="Update ticket", response_model=TicketSchema)
async def update_tickets(ticket_id: int, data: TicketChangeSchema, user: ModelUser = Depends(get_current_user)):
    if user.role == "admin":
        db_ticket = db.session.query(ModelTicket).all()
    else:
        db_ticket = db.session.query(ModelTicket).join(ModelTicket.project).filter_by(user_id=user.id)

    db_ticket = db_ticket.filter(ModelTicket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )
    ticket_stored = TicketSchema(id=db_ticket.id, name=db_ticket.name, description=db_ticket.description,
                                 project_id=db_ticket.project_id,
                                 status=db_ticket.status,
                                 created=db_ticket.created
                                 )
    update_data = data.dict(exclude_unset=True)
    updated_item = ticket_stored.copy(update=update_data)
    updated_item.updated = datetime.utcnow()
    db.session.query(ModelTicket).filter_by(id=ticket_id).update(updated_item.dict(), synchronize_session=False)
    db.session.commit()
    return updated_item


@router.delete("/tickets/{ticket_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_ticket(ticket_id: int, user: ModelUser = Depends(get_current_user)):
    if user.role == "admin":
        db_ticket = db.session.query(ModelTicket).all()
    else:
        db_ticket = db.session.query(ModelTicket).join(ModelTicket.project).filter_by(user_id=user.id)

    db_ticket = db_ticket.filter(ModelTicket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )
    db.session.delete(db_ticket)
    db.session.commit()
    return None






