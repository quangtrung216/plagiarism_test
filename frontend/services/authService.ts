import { http } from '@/lib/http';

export interface LoginRequest {
    username: string;
    password: string;
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
}

export interface RegisterRequest {
    username: string;
    email: string;
    password: string;
    full_name: string;
    role: 'student' | 'teacher';
}

export interface RegisterResponse {
    user_id: string;
    username: string;
    email: string;
    role: string;
}

export const authService = {
    login: async (credentials: LoginRequest): Promise<LoginResponse> => {
        // Using FormData for login as per OAuth2 standard often used, or JSON?
        // The previous actions.ts used JSON structure passed to login.
        // Let's assume JSON for now based on typical modern APIs, 
        // but if it's OAuth2 'application/x-www-form-urlencoded' might be needed.
        // Given the previous code: `const result = await authService.login(credentials);`
        // I'll stick to JSON.
        return http<LoginResponse>('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials),
        });
    },

    register: async (data: RegisterRequest, classOrDepartment: string): Promise<RegisterResponse> => {
        // Combine data and classOrDepartment if needed, or send as separate fields.
        // Based on `classOrDepartment` name, it seems specific to student/teacher.
        // Let's assume the backend expects a unified payload.
        const payload = {
            ...data,
            class_or_department: classOrDepartment, // Adjust key as per backend requirement
        };

        return http<RegisterResponse>('/auth/register', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
    },

    // Add other auth methods if needed
    me: async () => {
        return http('/users/me');
    },
};

export default authService;
