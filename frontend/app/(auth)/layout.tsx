import React from 'react';
import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';
import { validateRequest } from '../auth';

export default async function AuthLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Get token from cookies using next/headers
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  // Validate the request
  const { user } = await validateRequest();
  // Redirect if already authenticated
  if (token && user) {
    redirect('/dashboard');
  }

  return <div>{children}</div>;
}
