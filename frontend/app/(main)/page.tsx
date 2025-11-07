'use client';

import { useAuthorization } from '@/providers/AuthorizationProvider';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Header from '@/app/(main)/components/Header';

export default function HomePage() {
  const { user, token } = useAuthorization();
  const router = useRouter();
  // Redirect to sign-in if no token
  useEffect(() => {
    if (!token) {
      router.push('/sign-in');
    }
  }, [token, router]);

  if (!token) {
    return null; // or a loading spinner
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 p-4">
              <h2 className="text-2xl font-semibold mb-4">
                Welcome, {user?.name || user?.email}!
              </h2>
              <p className="text-gray-600">
                This is the plagiarism detection dashboard. You can upload
                documents here to check for plagiarism.
              </p>
              <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="px-4 py-5 sm:p-6">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Upload Document
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">
                      Upload a document to check for plagiarism.
                    </p>
                    <button className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                      Upload
                    </button>
                  </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="px-4 py-5 sm:p-6">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Recent Reports
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">
                      View your recent plagiarism reports.
                    </p>
                    <button className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                      View Reports
                    </button>
                  </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="px-4 py-5 sm:p-6">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Account Settings
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">
                      Manage your account settings and preferences.
                    </p>
                    <button className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                      Settings
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
