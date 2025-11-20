'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useSearchParams } from 'next/navigation';
import { signIn } from '@/lib/actions';
import Link from 'next/link';

export default function SignInPage() {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const registered = searchParams.get('registered');

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const formData = new FormData(e.currentTarget);

    try {
      const result = await signIn(formData);

      if (result.success) {
        // Redirect to home page
        router.push('/');
        router.refresh();
      } else {
        setError(result.error || 'Failed to sign in');
      }
    } catch (err) {
      setError((err as Error).message || 'Failed to sign in');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      {/* Left side - Green background with welcome text */}
      <div className="w-full md:w-[40%] bg-gradient-to-br from-green-800 to-green-400 p-10 flex flex-col justify-center text-white relative">
        <div className="max-w-md mx-auto text-center">
          <h1 className="text-3xl font-bold mb-4">Chào mừng trở lại!</h1>
          <p className="text-gray-200 opacity-80 mb-12">
            Đăng nhập để tiếp tục sử dụng dịch vụ của chúng tôi
          </p>
          <div className="font-bold text-lg py-3 px-6 rounded-lg inline-block">
            <span>Chưa có tài khoản? </span>
            <Link href="/sign-up" className='text-orange-300'>Đăng ký ngay</Link>
          </div>
        </div>
      </div>

      {/* Right side - Form section with light green background */}
      <div className="w-full md:w-[60%] bg-green-50 p-10 flex items-center">
        <div className="w-full max-w-md mx-auto bg-white p-8 rounded-xl shadow-lg">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-800">Đăng nhập</h2>
            <p className="text-gray-600 opacity-80 mt-2">
              Nhập thông tin của bạn để đăng nhập vào tài khoản.
            </p>
          </div>

          {registered && (
            <div className="mt-4 rounded-md bg-green-50 p-4">
              <div className="text-sm text-green-700">
                Đăng ký thành công! Vui lòng đăng nhập với thông tin đã tạo.
              </div>
            </div>
          )}

          <form className="space-y-6 mt-8" onSubmit={handleSubmit}>
            {error && (
              <div className="rounded-md bg-red-50 p-4">
                <div className="text-sm text-red-700">{error}</div>
              </div>
            )}

            <div className="space-y-5">
              {/* Username */}
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                  Tên đăng nhập
                </label>
                <div className="relative">
                  <input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-full focus:ring-2 focus:ring-green-500 focus:border-green-500 transition duration-200 shadow-sm"
                    placeholder="Tên đăng nhập"
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                  Mật khẩu
                </label>
                <div className="relative">
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-full focus:ring-2 focus:ring-green-500 focus:border-green-500 transition duration-200 shadow-sm"
                    placeholder="Mật khẩu"
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                />
                <label
                  htmlFor="remember-me"
                  className="ml-2 block text-sm text-gray-900"
                >
                  Ghi nhớ đăng nhập
                </label>
              </div>

              <div className="text-sm">
                <a
                  href="#"
                  className="font-medium text-green-600 hover:text-green-500"
                >
                  Quên mật khẩu?
                </a>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex justify-center mt-8">
              <button
                type="submit"
                disabled={loading}
                className="bg-green-700 hover:bg-green-800 text-white font-bold py-3 px-12 rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition duration-300 shadow-lg hover:shadow-xl"
              >
                {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
              </button>
            </div>
            
            <div className="text-center mt-8">
              <p className="text-sm text-gray-600">
                Chưa có tài khoản?{' '}
                <Link href="/sign-up" className="font-medium text-green-600 hover:text-green-500">
                  Đăng ký ngay
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}