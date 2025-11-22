'use server';

import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';
import authService from '@/services/authService';
import { LoginRequest, RegisterRequest } from '@/services/authService';

export async function signIn(formData: FormData) {
  try {
    const username = formData.get('username') as string;
    const password = formData.get('password') as string;

    // Call the authentication service
    const credentials: LoginRequest = { username, password };
    const result = await authService.login(credentials);

    if (result.access_token) {
      // Set the token in cookies
      (await cookies()).set('token', result.access_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        maxAge: 60 * 60 * 24 * 7, // One week
      });

      return { success: true };
    } else {
      return { success: false, error: 'Thông tin tài khoản không chính xác. Vui lòng thử lại.' };
    }
  } catch (error: unknown) {
    console.error('Sign in error:', error);
    if (error instanceof Error) {
      return { success: false, error: error.message || 'Đăng nhập thất bại. Vui lòng thử lại.' };
    }
    return { success: false, error: 'Đăng nhập thất bại' };
  }
}

export async function register(formData: FormData, role: 'student' | 'teacher') {
  try {
    const username = formData.get('username') as string;
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    const fullName = formData.get('fullName') as string;
    const classOrDepartment = formData.get('classOrDepartment') as string;

    // Prepare registration data
    const registerData: RegisterRequest = {
      username,
      email,
      password,
      full_name: fullName,
      role: role === 'student' ? 'student' : 'teacher',
    };

    // Call the authentication service with enhanced registration
    const result = await authService.register(registerData, classOrDepartment);

    if (result.user_id) {
      return { success: true };
    } else {
      return { success: false, error: 'Đăng ký thất bại' };
    }
  } catch (error: unknown) {
    console.error('Registration error:', error);
    if (error instanceof Error) {

      return { success: false, error: error.message || 'Đăng ký thất bại. Vui lòng thử lại.' };
    }
    return { success: false, error: 'Đăng ký thất bại. Vui lòng thử lại.' };
  }
}

export async function signOut() {
  try {
    // Clear the token cookie
    (await cookies()).delete('token');

    // Redirect to sign-in page
    redirect('/sign-in');
  } catch (error: unknown) {
    console.error('Sign out error:', error);
    // Even if there's an error, we still want to redirect to sign-in
    redirect('/sign-in');
  }
}