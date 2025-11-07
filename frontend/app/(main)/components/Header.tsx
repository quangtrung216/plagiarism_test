'use client';

import { useAuthorization } from '@/providers/AuthorizationProvider';
import { signOut } from '@/lib/actions';

export default function Header() {
  const { user } = useAuthorization();

  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">
          Plagiarism Detection
        </h1>
        <div className="flex items-center space-x-4">
          <span className="text-gray-700">
            Welcome, {user?.name || user?.email}
          </span>
          <form action={signOut}>
            <button
              type="submit"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Logout
            </button>
          </form>
        </div>
      </div>
    </header>
  );
}
