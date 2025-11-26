import apiClient from './apiClient';

const BASE_PATH = '/api/v1/documents';

class DocumentService {
    async listDocuments(skip = 0, limit = 100) {
        return apiClient.get(`${BASE_PATH}?skip=${skip}&limit=${limit}`);
    }

    async uploadDocument(file: File) {
        const formData = new FormData();
        formData.append('file', file);
        return apiClient.post(`${BASE_PATH}/upload/`, formData);
    }

    async deleteDocument(objectName: string) {
        return apiClient.delete(`${BASE_PATH}/${encodeURIComponent(objectName)}`);
    }

    async searchDocuments(query: string, skip = 0, limit = 100) {
        return apiClient.get(`${BASE_PATH}/search/?query=${encodeURIComponent(query)}&skip=${skip}&limit=${limit}`);
    }
}

const documentService = new DocumentService();
export default documentService;
