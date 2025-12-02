from typing import List, Optional
from sqlmodel import Session, select, col
from sqlalchemy.orm import selectinload
from app.models.topic import Topic, TopicCreate, TopicUpdate
from app.models.topic_member import TopicMember, TopicMemberCreate, TopicMemberUpdate
from app.models.enums import MemberStatus
from datetime import datetime


class TopicService:
    """Service for managing topics and topic memberships"""

    def __init__(self, session: Session):
        self.session = session

    def create_topic(self, topic_data: TopicCreate, user_id: int) -> Topic:
        """Create a new topic"""
        # Set the teacher_id to the current user's id

        db_topic = Topic(**topic_data.model_dump())
        db_topic.teacher_id = user_id
        self.session.add(db_topic)
        self.session.commit()
        self.session.refresh(db_topic)
        return db_topic

    def get_topic(self, topic_id: int) -> Optional[Topic]:
        """Get a topic by ID"""
        statement = (
            select(Topic)
            .options(selectinload(Topic.teacher))
            .where(Topic.id == topic_id)
        )
        return self.session.exec(statement).first()

    def get_topic_by_code(self, code: str) -> Optional[Topic]:
        """Get a topic by code"""
        statement = (
            select(Topic).options(selectinload(Topic.teacher)).where(Topic.code == code)
        )
        return self.session.exec(statement).first()

    def update_topic(
        self, topic_id: int, topic_data: TopicUpdate, user_id: int
    ) -> Optional[Topic]:
        """Update a topic"""
        db_topic = self.session.get(Topic, topic_id)
        if not db_topic:
            return None

        # Check permission - only teacher who created the topic can update it
        if db_topic.teacher_id != user_id:
            raise PermissionError("Not authorized to update this topic")

        # Update the topic
        topic_data_dict = topic_data.dict(exclude_unset=True)
        for key, value in topic_data_dict.items():
            setattr(db_topic, key, value)

        db_topic.updated_at = datetime.utcnow()
        self.session.add(db_topic)
        self.session.commit()
        self.session.refresh(db_topic)
        return db_topic

    def delete_topic(self, topic_id: int, user_id: int) -> bool:
        """Delete a topic"""
        db_topic = self.session.get(Topic, topic_id)
        if not db_topic:
            return False

        # Check permission - only teacher who created the topic can delete it
        if db_topic.teacher_id != user_id:
            raise PermissionError("Not authorized to delete this topic")

        self.session.delete(db_topic)
        self.session.commit()
        return True

    def search_topics(
        self,
        skip: int = 0,
        limit: int = 100,
        title: Optional[str] = None,
        code: Optional[str] = None,
        user_role: Optional[str] = None,
    ) -> List[Topic]:
        """Search topics with optional filters"""
        query = select(Topic).options(selectinload(Topic.teacher))

        # Apply filters
        if title:
            query = query.where(col(Topic.title).like(f"%{title}%"))
        if code:
            query = query.where(Topic.code == code)

        # Only show public topics to students, teachers can see all their own topics
        if user_role == "student":
            query = query.where(Topic.public)

        topics = list(self.session.exec(query.offset(skip).limit(limit)).all())
        return topics

    def request_join_topic(
        self, topic_id: int, student_id: int, note: Optional[str] = None
    ) -> TopicMember:
        """Request to join a topic"""
        # Check if topic exists
        db_topic = self.session.get(Topic, topic_id)
        if not db_topic:
            raise ValueError("Topic not found")

        # If topic doesn't require approval, automatically accept the student
        if not db_topic.require_approval:
            # Create accepted membership directly
            topic_member_data = TopicMemberCreate(
                topic_id=topic_id,
                student_id=student_id,
                status=MemberStatus.ACCEPTED,
                note=note,
            )

            db_topic_member = TopicMember(**topic_member_data.dict())
            db_topic_member.responded_at = datetime.utcnow()
            db_topic_member.responded_by = (
                db_topic.teacher_id
            )  # Teacher is automatically the approver

            self.session.add(db_topic_member)
            self.session.commit()
            self.session.refresh(db_topic_member)
            return db_topic_member

        # Check if user has already requested to join
        existing_request = self.session.exec(
            select(TopicMember)
            .where(TopicMember.topic_id == topic_id)
            .where(TopicMember.student_id == student_id)
        ).first()

        if existing_request:
            raise ValueError("You have already requested to join this topic")

        # Create join request
        topic_member_data = TopicMemberCreate(
            topic_id=topic_id,
            student_id=student_id,
            status=MemberStatus.PENDING,
            note=note,
        )

        db_topic_member = TopicMember(**topic_member_data.dict())
        self.session.add(db_topic_member)
        self.session.commit()
        self.session.refresh(db_topic_member)
        return db_topic_member

    def update_member_status(
        self,
        topic_id: int,
        member_id: int,
        member_data: TopicMemberUpdate,
        teacher_id: int,
    ) -> Optional[TopicMember]:
        """Approve or reject a join request"""
        # Check if topic exists
        db_topic = self.session.get(Topic, topic_id)
        if not db_topic:
            return None

        # Check if user is the teacher who created the topic
        if db_topic.teacher_id != teacher_id:
            raise PermissionError("Only the topic creator can manage members")

        # Get the topic member
        db_topic_member = self.session.get(TopicMember, member_id)
        if not db_topic_member:
            return None

        # Check if the member request is for this topic
        if db_topic_member.topic_id != topic_id:
            raise ValueError("Member request does not belong to this topic")

        # Update the member status
        member_data_dict = member_data.dict(exclude_unset=True)
        for key, value in member_data_dict.items():
            setattr(db_topic_member, key, value)

        # Set responded_at and responded_by
        db_topic_member.responded_at = datetime.utcnow()
        db_topic_member.responded_by = teacher_id

        self.session.add(db_topic_member)
        self.session.commit()
        self.session.refresh(db_topic_member)
        return db_topic_member

    def get_user_topics(
        self, user_id: int, user_role: str, skip: int = 0, limit: int = 100
    ) -> List[Topic]:
        """Get topics created by user (if teacher) or joined by user (if student)"""
        if user_role == "teacher":
            # Get topics created by the teacher with teacher information
            topics = list(
                self.session.exec(
                    select(Topic)
                    .options(selectinload(Topic.teacher))
                    .where(Topic.teacher_id == user_id)
                    .offset(skip)
                    .limit(limit)
                ).all()
            )
            return topics
        elif user_role == "student":
            # Get topic members for this student
            topic_members = list(
                self.session.exec(
                    select(TopicMember)
                    .where(TopicMember.student_id == user_id)
                    .offset(skip)
                    .limit(limit)
                ).all()
            )

            # Get the topics from the topic members
            topic_ids = [tm.topic_id for tm in topic_members]
            if not topic_ids:
                return []

            topics_query = (
                select(Topic)
                .options(selectinload(Topic.teacher))
                .where(col(Topic.id).in_(topic_ids))
            )
            topics = list(self.session.exec(topics_query).all())
            return topics
        else:
            return []

    def get_topic_students(
        self,
        topic_id: int,
        status: Optional[MemberStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TopicMember]:
        """Get students in a topic with full student information"""
        # Check if topic exists
        db_topic = self.session.get(Topic, topic_id)
        if not db_topic:
            raise ValueError("Topic not found")

        # Get topic members with student and student_profile information
        query = (
            select(TopicMember)
            .options(
                selectinload(TopicMember.student),  # Load student (User) information
                selectinload(
                    TopicMember.student_profile
                ),  # Load student profile information
            )
            .where(TopicMember.topic_id == topic_id)
        )

        # Apply status filter if provided
        if status:
            query = query.where(TopicMember.status == status)

        topic_members = list(self.session.exec(query.offset(skip).limit(limit)).all())

        return topic_members
