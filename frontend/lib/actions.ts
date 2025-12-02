'use server';

import { cookies } from 'next/headers';
import authService, { LoginRequest, RegisterRequest } from '@/services/authService';

export async function signIn(formData: FormData) {
  try {
    const username = formData.get('username') as string;
    const password = formData.get('password') as string;

    if (!username || !password) {
      return { success: false, error: 'Vui lòng nhập đầy đủ thông tin.' };
    }

    // Call the authentication service
    const credentials: LoginRequest = { username, password };
    const result = await authService.login(credentials);

    if (result.access_token) {
      // Set the token in cookies
      const cookieStore = await cookies();
      cookieStore.set('token', result.access_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        maxAge: 60 * 60 * 24 * 7, // One week
        path: '/',
        sameSite: 'lax',
      });

      return { success: true };
    } else {
      return { success: false, error: 'Thông tin tài khoản không chính xác. Vui lòng thử lại.' };
    }
  } catch (error : any) {
    console.error('Sign in error:', error);
    return { success: false, error: error.message || 'Đăng nhập thất bại. Vui lòng thử lại.' };
  }
}

export async function register(formData: FormData, role: 'student' | 'teacher') {
  try {
    const username = formData.get('username') as string;
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    const fullName = formData.get('fullName') as string;
    const classOrDepartment = formData.get('classOrDepartment') as string;

    if (!username || !email || !password || !fullName || !classOrDepartment) {
      return { success: false, error: 'Vui lòng nhập đầy đủ thông tin.' };
    }

    // Prepare registration data
    const registerData: RegisterRequest = {
      username,
      email,
      password,
      full_name: fullName,
      role,
    };

    // Call the authentication service
    const result = await authService.register(registerData, classOrDepartment);

    if (result.user_id) {
      return { success: true };
    } else {
      return { success: false, error: 'Đăng ký thất bại' };
    }
  } catch (error: any) {
    console.error('Registration error:', error);
    return { success: false, error: error.message || 'Đăng ký thất bại. Vui lòng thử lại.' };
  }
}

export async function signOut() {
  try {
    const cookieStore = await cookies();
    cookieStore.delete('token');
    return { success: true };
  } catch (error) {
    console.error('Sign out error:', error);
    return { success: false, error: 'Đăng xuất thất bại' };
  }
}