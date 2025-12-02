import { http } from '@/lib/http';
import { Document } from '@/types';

export const documentService = {
    listDocuments: async (): Promise<Document[]> => {
        return http<Document[]>('/documents');
    },

    searchDocuments: async (query: string): Promise<Document[]> => {
        return http<Document[]>('/documents/search/', {
            params: { query: query },
        });
    },

    uploadDocument: async (file: File): Promise<void> => {
        const formData = new FormData();
        formData.append('file', file);

        return http<void>('/documents/upload/', {
            method: 'POST',
            body: formData,
        });
    },

    deleteDocument: async (objectName: string): Promise<void> => {
        return http<void>(`/documents/${encodeURIComponent(objectName)}`, {
            method: 'DELETE',
        });
    },
};

export default documentService;