import apiClient from './apiClient';
import { Topic } from '../types/index';

const BASE_PATH = '/api/v1/topics';

class TopicService {
    async getTopics(): Promise<Topic[]> {
        return apiClient.get<Topic[]>(BASE_PATH);
    }

    async getMyTopics(): Promise<Topic[]> {
        return apiClient.get<Topic[]>(`${BASE_PATH}/my-topics`);
    }

    async createTopic(topicData: Partial<Topic>): Promise<Topic> {
        return apiClient.post<Topic, Partial<Topic>>(BASE_PATH, topicData);
    }

    async updateTopic(topicId: number, topicData: Partial<Topic>): Promise<Topic> {
        return apiClient.put<Topic, Partial<Topic>>(`${BASE_PATH}/${topicId}`, topicData);
    }

    async deleteTopic(topicId: number): Promise<void> {
        return apiClient.delete<void>(`${BASE_PATH}/${topicId}`);
    }
}

const topicService = new TopicService();

export default topicService;
