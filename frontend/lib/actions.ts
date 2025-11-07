'use server';

import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';
import authService from '@/services/authService';
import { LoginRequest } from '@/services/authService';

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
        path: '/',
      });

      return { success: true };
    } else {
      return { success: false, error: 'Invalid credentials' };
    }
  } catch (error: unknown) {
    console.error('Sign in error:', error);
    if (error instanceof Error) {
      return { success: false, error: error.message || 'Failed to sign in' };
    }
    return { success: false, error: 'Failed to sign in' };
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
