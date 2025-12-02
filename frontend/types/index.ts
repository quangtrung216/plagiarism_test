export interface MyUser {
  id: number;
  username: string;
  full_name: string;
  email: string;
  role: string;
  createdAt: string;
  updatedAt: string;
}

export interface Topic {
  id: number;
  title: string;
  code: string;
  description?: string;
  public: boolean;
  teacher_id: number;
  createdAt: string;
  updatedAt: string;
  deadline?: string;
  max_file_size?: number;
  allowed_extensions?: string[];
  require_approval?: boolean;
  max_uploads?: number;
  threshold?: number;
  // New field for teacher information
  teacher_info?: {
    id: number;
    full_name?: string;
    username: string;
  };
}

export interface Document {
  object_name: string;
  size: number;
  last_modified: string;
  content_type?: string;
}

export interface TopicMember {
  id: number;
  topic_id: number;
  student_id: number;
  status: 'pending' | 'accepted' | 'rejected';
  note?: string;
  requested_at: string;
  responded_at?: string;
  responded_by?: number;
  student: {
    id: number;
    username: string;
    full_name?: string;
    email: string;
    student_profile?: {
      student_id: string;
      major?: string;
    };
  };
}