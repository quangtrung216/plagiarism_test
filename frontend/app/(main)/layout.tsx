import React from 'react';
import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';
import AuthorizationProvider from '@/providers/AuthorizationProvider';
import { validateRequest } from '../auth';
import Sidebar from '@/components/Sidebar';
import UserMenu from '@/components/UserMenu';

export default async function DashboardLayout({
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
      <div className="flex h-screen">
        {/* Sidebar */}
        <Sidebar role={user.role} />

        {/* Main Content */}
        <div className="flex flex-col flex-1 overflow-hidden bg-[#C0EEC033]">
          {/* Top Bar */}
          <header className="flex items-center justify-end p-5 gap-2">
            <UserMenu />
            <span className="font-bold text-md">Xin chào, {user.full_name}</span>
          </header>

          {/* Page Content */}
          <main className="flex-1 overflow-y-auto p-4">
            {children}
          </main>
        </div>
      </div>
    </AuthorizationProvider>
  );
}