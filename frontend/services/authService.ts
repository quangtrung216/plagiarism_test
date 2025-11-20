import apiClient from './apiClient';
import { MyUser } from '@/types';

export interface LoginRequest extends Record<string, unknown> {
  username: string;
  password: string;
}

export interface RegisterRequest extends Record<string, unknown> {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  role?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterResponse {
  message: string;
  user_id: number;
}

export interface ForgotPasswordRequest extends Record<string, unknown> {
  email: string;
}

export interface ResetPasswordRequest extends Record<string, unknown> {
  token: string;
  new_password: string;
}

export interface ForgotPasswordResponse {
  message: string;
  token?: string;
}

export interface ResetPasswordResponse {
  message: string;
}

class AuthService {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    return apiClient.post<AuthResponse, LoginRequest>(
      '/api/v1/auth/login',
      credentials
    );
  }

  async register(
    userData: RegisterRequest,
    classOrDepartment?: string
  ): Promise<RegisterResponse> {
    // If we have role-specific data, use the enhanced registration endpoint
    if (((userData.role === 'student' || userData.role === 'teacher') && classOrDepartment)) {
      // Create the request payload
      const payload = {
        ...userData,
        class_or_department: classOrDepartment
      };

      // Make the request with JSON data
      return apiClient.post<RegisterResponse, typeof payload>(
        '/api/v1/auth/register',
        payload
      );
    } else {
      // Use the standard registration endpoint
      return apiClient.post<RegisterResponse, RegisterRequest>(
        '/api/v1/auth/register',
        userData
      );
    }
  }

  async getCurrentUser(token?: string): Promise<MyUser> {
    // If a token is provided, we need to make a request with that specific token
    if (token) {
      // Create a temporary client with the provided token
      const tempClient = new (apiClient.constructor as new (
        baseUrl: string
      ) => typeof apiClient)(apiClient.getBaseUrl());
      tempClient.setToken(token);
      return await tempClient.get<MyUser>('/api/v1/users/me');
    }
    return apiClient.get<MyUser>('/api/v1/users/me');
  }

  async forgotPassword(
    data: ForgotPasswordRequest
  ): Promise<ForgotPasswordResponse> {
    return apiClient.post<ForgotPasswordResponse, ForgotPasswordRequest>(
      '/api/v1/auth/forgot-password',
      data
    );
  }

  async resetPassword(
    data: ResetPasswordRequest
  ): Promise<ResetPasswordResponse> {
    return apiClient.post<ResetPasswordResponse, ResetPasswordRequest>(
      '/api/v1/auth/reset-password',
      data
    );
  }

  setToken(token: string) {
    apiClient.setToken(token);
  }
}

const authService = new AuthService();

export default authService;