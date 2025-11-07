import { MyUser } from '@/types';
import { cookies } from 'next/headers';
import { cache } from 'react';
import authService from '@/services/authService';

export const validateRequest = cache(
  async (): Promise<
    { user: MyUser; token: string } | { user: null; token: null }
  > => {
    try {
      // Get token from cookies using next/headers
      const cookieStore = await cookies();
      const token = cookieStore.get('token')?.value ?? null;

      if (!token) {
        return { user: null, token: null };
      }

      // Set the token in the auth service
      authService.setToken(token);

      // Fetch user data
      const user = await authService.getCurrentUser();

      if (!user) {
        return { user: null, token: null };
      }

      return { user, token };
    } catch (error: unknown) {
      console.error('Authentication error:', error);
      return { user: null, token: null };
    }
  }
);
