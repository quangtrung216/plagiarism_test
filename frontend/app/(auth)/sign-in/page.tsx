'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useSearchParams } from 'next/navigation';
import { signIn } from '@/lib/actions';
import Link from 'next/link';
import Image from 'next/image';

export default function SignInPage() {
  const [role, setRole] = useState<'student' | 'teacher' | 'admin'>('student');
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
        router.push('/dashboard');
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
      <div className="w-full md:w-[40%] bg-gradient-to-br bg-[#2E7D32BF] p-10 flex flex-col justify-center text-white relative space-y-40">
        <div className="max-w-md mx-auto text-center">
          <h1 className="text-3xl font-bold mb-4">Chào mừng trở lại!</h1>
          <p className="text-gray-200 opacity-80">
            Hãy đăng nhập để trải nghiệm các tính năng của chúng tôi ngay bây giờ
          </p>
        </div>
        <div className="max-w-md mx-auto text-center">
          <div className="font-bold text-lg py-3 px-6 rounded-lg inline-block">
            <span>Chưa có tài khoản? </span>
            <Link href="/sign-up" className='text-orange-300'>Đăng ký ngay</Link>
          </div>
        </div>
      </div>

      {/* Right side - Form section with light green background */}
      <div className="w-full md:w-[60%] bg-[#C0EEC0] p-10 flex items-center">
        <div className="w-full max-w-lg mx-auto p-8 rounded-xl">
          <div className="text-center mb-8">
            <h1 className="text-6xl font-bold text-[#F69F3BBF] mt-2">
              Nhập thông tin
            </h1>
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
              <div className="rounded-lg bg-red-100 p-4">
                <div className="text-sm text-red-700">{error}</div>
              </div>
            )}

            {/* Role Selection */}
            <label htmlFor="Role" className="block text-lg font-medium text-[#000000] mb-1">
              Chọn vai trò
            </label>

            {/* Role Toggle Buttons */}
            <div className="flex justify-center space-x-6 mb-1">
              <button
                type="button"
                onClick={() => setRole('student')}
                className={`p-3 rounded-full font-medium border-3 transition-all duration-200 cursor-pointer ${role === 'student'
                  ? 'border-orange-400 text-white shadow-md'
                  : 'hover:bg-gray-100 border-[#000000]'
                  }`}
              >
                <Image src="/icons/graduated.png" alt="Icon Graduated" width={'25'} height={'22'} />
              </button>
              <button
                type="button"
                onClick={() => setRole('teacher')}
                className={`p-3 rounded-full font-medium border-3 transition-all duration-200 cursor-pointer ${role === 'teacher'
                  ? 'border-orange-400 text-white shadow-md'
                  : 'hover:bg-gray-100 border-[#000000]'
                  }`}
              >
                <Image src="/icons/teacher.png" alt="Icon Teacher" width={'25'} height={'22'} />
              </button>
              <button
                type="button"
                onClick={() => setRole('admin')}
                className={`p-3 rounded-full font-medium border-3 transition-all duration-200 cursor-pointer ${role === 'admin'
                  ? 'border-orange-400 text-white shadow-md'
                  : 'hover:bg-gray-100 border-[#000000]'
                  }`}
              >
                <Image src="/icons/settings.png" alt="Icon Admin" width={'25'} height={'22'} />
              </button>
            </div>

            <div className="space-y-5">
              {/* Username */}
              <div>
                <label htmlFor="username" className="block text-md font-medium text-[#000000] mb-1">
                  {role === 'student' ? 'Mã sinh viên' : role === 'teacher' ? 'Mã giảng viên' : 'Tài khoản'}
                </label>
                <div className="relative">
                  <input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    required
                    className="w-full px-4 py-3 border-2 border-[#000000] rounded-full bg-gray-300"
                    placeholder={role === 'student' ? 'Mã sinh viên' : role === 'teacher' ? 'Mã giảng viên' : 'Nhập tài khoản'}
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <label htmlFor="password" className="block text-md font-medium text-[#000000] mb-1">
                  Mật khẩu
                </label>
                <div className="relative">
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    className="w-full px-4 py-3 border-2 border-[#000000] rounded-full bg-gray-300"
                    placeholder="Nhập mật khẩu"
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
                  className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded cursor-pointer"
                />
                <label
                  htmlFor="remember-me"
                  className="ml-2 block text-md text-[#000000] cursor-pointer"
                >
                  Ghi nhớ đăng nhập
                </label>
              </div>

              <div className="text-md">
                <a
                  href="#"
                  className="font-bold text-green-600 hover:text-green-500"
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
                className="bg-green-700 hover:bg-green-800 text-white font-bold py-3 px-12 rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition duration-300 shadow-lg hover:shadow-xl cursor-pointer text-lg"
              >
                {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}