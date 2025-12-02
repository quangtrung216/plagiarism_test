from app.schemas.topic import TopicOut, TeacherInfo
from datetime import datetime

# Test creating a TopicOut object with minimal data
try:
    teacher_info = TeacherInfo(id=1, full_name="John Doe", username="johndoe")

    topic_out = TopicOut(
        id=1,
        title="Test Topic",
        description="This is a test topic",
        teacher_id=1,
        deadline=None,
        max_file_size=10485760,
        allowed_extensions=["pdf", "doc"],
        code="TEST123",
        public=True,
        require_approval=True,
        max_uploads=1,
        threshold=0.8,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        teacher_info=teacher_info,
    )

    print("Successfully created TopicOut object:")
    print(topic_out)
except Exception as e:
    print(f"Error creating TopicOut object: {e}")
    import traceback

    traceback.print_exc()
