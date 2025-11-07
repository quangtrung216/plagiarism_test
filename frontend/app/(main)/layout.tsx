import React from 'react';
import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';
import AuthorizationProvider from '@/providers/AuthorizationProvider';
import { validateRequest } from '../auth';

export default async function AuthenticatedLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Get token from cookies using next/headers
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  // Validate the request
  const { user } = await validateRequest();

  // Redirect if not authenticated
  if (!token || !user) {
    redirect('/sign-in');
  }

  // Pass user and token to the provider
  return (
    <AuthorizationProvider value={{ user: user, token: token }}>
      {children}
    </AuthorizationProvider>
  );
}
