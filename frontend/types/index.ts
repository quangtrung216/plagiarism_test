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
  status?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Document {
  object_name: string;
  size: number;
  last_modified: string;
  content_type?: string;
}
