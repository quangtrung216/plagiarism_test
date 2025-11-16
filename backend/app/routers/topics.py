from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status as fastapi_status
from sqlmodel import Session, select, col
from app.database.session import get_session
from app.core.auth import get_current_user
from app.core.topic_service import TopicService
from app.models.user import User
from app.models.topic import Topic, TopicCreate, TopicUpdate
from app.models.topic_member import TopicMember, TopicMemberUpdate
from app.models.enums import MemberStatus, TopicStatus

router = APIRouter()


# Create a new topic
@router.post("/", response_model=Topic)
def create_topic(
    *,
    session: Session = Depends(get_session),
    topic_data: TopicCreate,
    current_user: User = Depends(get_current_user),
):
    """Create a new topic"""
    # Check permission
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=fastapi_status.HTTP_403_FORBIDDEN,
            detail="Only teachers can create topics",
        )

    # Ensure user ID is not None
    if current_user.id is None:
        raise HTTPException(
            status_code=fastapi_status.HTTP_400_BAD_REQUEST,
            detail="User ID is required",
        )

    topic_service = TopicService(session)
    return topic_service.create_topic(topic_data, current_user.id)


# Update a topic
@router.put("/{topic_id}", response_model=Topic)
def update_topic(
    *,
    topic_id: int,
    topic_data: TopicUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Update a topic"""
    # Ensure user ID is not None
    if current_user.id is None:
        raise HTTPException(
            status_code=fastapi_status.HTTP_400_BAD_REQUEST,
            detail="User ID is required",
        )

    topic_service = TopicService(session)
    try:
        db_topic = topic_service.update_topic(topic_id, topic_data, current_user.id)
        if not db_topic:
            raise HTTPException(
                status_code=fastapi_status.HTTP_404_NOT_FOUND, detail="Topic not found"
            )
        return db_topic
    except PermissionError as e:
        raise HTTPException(
            status_code=fastapi_status.HTTP_403_FORBIDDEN, detail=str(e)
        )


# Delete a topic
@router.delete("/{topic_id}", status_code=fastapi_status.HTTP_204_NO_CONTENT)
def delete_topic(
    *,
    topic_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete a topic"""
    # Ensure user ID is not None
    if current_user.id is None:
        raise HTTPException(
            status_code=fastapi_status.HTTP_400_BAD_REQUEST,
            detail="User ID is required",
        )

    topic_service = TopicService(session)
    try:
        success = topic_service.delete_topic(topic_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=fastapi_status.HTTP_404_NOT_FOUND, detail="Topic not found"
            )
        return
    except PermissionError as e:
        raise HTTPException(
            status_code=fastapi_status.HTTP_403_FORBIDDEN, detail=str(e)
        )


# Search topics
@router.get("/", response_model=List[Topic])
def search_topics(
    *,
    skip: int = 0,
    limit: int = 100,
    status: Optional[TopicStatus] = None,
    title: Optional[str] = None,
    code: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Search topics with optional filters"""
    topic_service = TopicService(session)
    return topic_service.search_topics(
        skip, limit, status, title, code, current_user.role
    )


# Get topic by code
@router.get("/code/{code}", response_model=Topic)
def get_topic_by_code(
    *,
    code: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get a topic by its code"""
    topic_service = TopicService(session)
    db_topic = topic_service.get_topic_by_code(code)

    if not db_topic:
        raise HTTPException(
            status_code=fastapi_status.HTTP_404_NOT_FOUND, detail="Topic not found"
        )

    # If topic is not public, only teacher or admin can view it
    if (
        not db_topic.public
        and db_topic.teacher_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=fastapi_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this topic",
        )

    return db_topic


# Request to join a topic
@router.post("/{topic_id}/request-join", response_model=TopicMember)
def request_join_topic(
    *,
    topic_id: int,
    note: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Request to join a topic"""
    # Check if user is a student
    if current_user.role != "student":
        raise HTTPException(
            status_code=fastapi_status.HTTP_403_FORBIDDEN,
            detail="Only students can request to join topics",
        )

    # Ensure user ID is not None
    if current_user.id is None:
        raise HTTPException(
            status_code=fastapi_status.HTTP_400_BAD_REQUEST,
            detail="User ID is required",
        )

    topic_service = TopicService(session)
    try:
        return topic_service.request_join_topic(topic_id, current_user.id, note)
    except ValueError as e:
        raise HTTPException(
            status_code=fastapi_status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=fastapi_status.HTTP_404_NOT_FOUND, detail="Topic not found"
        )


# Request to join a topic by code
@router.post("/code/{code}/request-join", response_model=TopicMember)
def request_join_topic_by_code(
    *,
    code: str,
    note: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Request to join a topic by its code"""
    # Check if user is a student
    if current_user.role != "student":
        raise HTTPException(
            status_code=fastapi_status.HTTP_403_FORBIDDEN,
            detail="Only students can request to join topics",
        )

    # Ensure user ID is not None
    if current_user.id is None:
        raise HTTPException(
            status_code=fastapi_status.HTTP_400_BAD_REQUEST,
            detail="User ID is required",
        )

    topic_service = TopicService(session)

    # Get topic by code
    db_topic = topic_service.get_topic_by_code(code)
    if not db_topic:
        raise HTTPException(
            status_code=fastapi_status.HTTP_404_NOT_FOUND, detail="Topic not found"
        )

    # Ensure topic ID is not None
    if db_topic.id is None:
        raise HTTPException(
            status_code=fastapi_status.HTTP_400_BAD_REQUEST,
            detail="Topic ID is required",
        )

    try:
        return topic_service.request_join_topic(db_topic.id, current_user.id, note)
    except ValueError as e:
        raise HTTPException(
            status_code=fastapi_status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


# Approve/reject join request
@router.put("/{topic_id}/members/{member_id}", response_model=TopicMember)
def update_member_status(
    *,
    topic_id: int,
    member_id: int,
    member_data: TopicMemberUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Approve or reject a join request"""
    # Ensure user ID is not None
    if current_user.id is None:
        raise HTTPException(
            status_code=fastapi_status.HTTP_400_BAD_REQUEST,
            detail="User ID is required",
        )

    topic_service = TopicService(session)
    try:
        db_topic_member = topic_service.update_member_status(
            topic_id, member_id, member_data, current_user.id
        )
        if not db_topic_member:
            raise HTTPException(
                status_code=fastapi_status.HTTP_404_NOT_FOUND,
                detail="Member request not found",
            )
        return db_topic_member
    except PermissionError as e:
        raise HTTPException(
            status_code=fastapi_status.HTTP_403_FORBIDDEN, detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=fastapi_status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


# Get topics created by current user (teacher) or joined by user (student)
@router.get("/my-topics", response_model=List[Topic])
def get_my_topics(
    *,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get topics created by the current user (teacher) or joined by user (student)"""
    # Ensure user ID is not None
    if current_user.id is None:
        raise HTTPException(
            status_code=fastapi_status.HTTP_400_BAD_REQUEST,
            detail="User ID is required",
        )

    topic_service = TopicService(session)
    return topic_service.get_user_topics(
        current_user.id, current_user.role, skip, limit
    )


# Get students in a topic
@router.get("/{topic_id}/students", response_model=List[TopicMember])
def get_topic_students(
    *,
    topic_id: int,
    status: Optional[MemberStatus] = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get students in a topic"""
    topic_service = TopicService(session)
    try:
        # Check if user is authorized to view students
        db_topic = topic_service.get_topic(topic_id)
        if not db_topic:
            raise HTTPException(
                status_code=fastapi_status.HTTP_404_NOT_FOUND, detail="Topic not found"
            )

        # Check permission - only teacher who created the topic or admin can view students
        if db_topic.teacher_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=fastapi_status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view students in this topic",
            )

        return topic_service.get_topic_students(topic_id, status, skip, limit)
    except ValueError as e:
        raise HTTPException(
            status_code=fastapi_status.HTTP_404_NOT_FOUND, detail=str(e)
        )


# Get topics user has joined (student) - alternative endpoint
@router.get("/my-joined-topics", response_model=List[Topic])
def get_my_joined_topics(
    *,
    status: Optional[MemberStatus] = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get topics the current user has joined"""
    # Ensure user ID is not None
    if current_user.id is None:
        raise HTTPException(
            status_code=fastapi_status.HTTP_400_BAD_REQUEST,
            detail="User ID is required",
        )

    # This is the same as my-topics for students, but with explicit status filtering
    topic_service = TopicService(session)

    # For students, we want to filter by membership status
    if current_user.role == "student":
        # Get topic members for this student with specified status
        query = select(TopicMember).where(TopicMember.student_id == current_user.id)

        # Apply status filter if provided
        if status:
            query = query.where(TopicMember.status == status)

        topic_members = list(session.exec(query.offset(skip).limit(limit)).all())

        # Get the topics from the topic members
        topic_ids = [tm.topic_id for tm in topic_members]
        if not topic_ids:
            return []

        # Use col() function for proper SQL IN clause
        topics_query = select(Topic).where(col(Topic.id).in_(topic_ids))
        topics = list(session.exec(topics_query).all())
        return topics
    else:
        # For teachers, return their created topics
        return topic_service.get_user_topics(
            current_user.id, current_user.role, skip, limit
        )
