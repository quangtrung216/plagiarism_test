'use server';

import { http } from '@/lib/http';
import { Topic, TopicMember } from '@/types';

export interface TopicFormData {
    title: string;
    code?: string; // Make code optional since it's auto-generated
    description?: string;
    public: boolean;
    require_approval?: boolean;
    deadline?: string;
    max_file_size?: number;
    allowed_extensions?: string[];
    max_uploads?: number;
    threshold?: number;
}

export async function getMyTopics(): Promise<Topic[]> {
    return http<Topic[]>('/topics/my-topics');
}

export async function createTopic(data: TopicFormData): Promise<Topic> {
    return http<Topic>('/topics', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

export async function updateTopic(id: number, data: TopicFormData): Promise<Topic> {
    return http<Topic>(`/topics/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    });
}

export async function deleteTopic(id: number): Promise<void> {
    return http<void>(`/topics/${id}`, {
        method: 'DELETE',
    });
}

export async function getTopicStudents(topicId: number): Promise<TopicMember[]> {
    return http<TopicMember[]>(`/topics/${topicId}/students`);
}

export async function updateTopicMemberStatus(
    topicId: number,
    memberId: number,
    status: 'accepted' | 'rejected',
    note?: string
): Promise<TopicMember> {
    return http<TopicMember>(`/topics/${topicId}/members/${memberId}`, {
        method: 'PUT',
        body: JSON.stringify({ status, note }),
    });
}

// New function to request joining a topic by ID
export async function requestJoinTopic(topicId: number, note?: string): Promise<TopicMember> {
    return http<TopicMember>(`/topics/${topicId}/request-join`, {
        method: 'POST',
        body: JSON.stringify({ note }),
    });
}

// New function to request joining a topic by code
export async function requestJoinTopicByCode(code: string, note?: string): Promise<TopicMember> {
    return http<TopicMember>(`/topics/code/${code}/request-join`, {
        method: 'POST',
        body: JSON.stringify({ note }),
    });
}

// New function to search public topics
export async function searchPublicTopics(searchTerm?: string): Promise<Topic[]> {
    const params: Record<string, string | number | boolean> = {
        public: true,
        limit: 100
    };
    
    if (searchTerm) {
        params.title = searchTerm;
    }
    
    return http<Topic[]>('/topics', {
        params
    });
}

// New function to get user's joined topics
export async function getMyJoinedTopics(): Promise<Topic[]> {
    return http<Topic[]>('/topics/my-topics');
}

// Add function to get a single topic by ID
export async function getTopicById(id: number): Promise<Topic> {
    return http<Topic>(`/topics/${id}`);
}