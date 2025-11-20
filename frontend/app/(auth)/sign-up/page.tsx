'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { register } from '@/lib/actions';

export default function SignUpPage() {
  const [role, setRole] = useState<'student' | 'teacher'>('student');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const formData = new FormData(e.currentTarget);

    try {
      const result = await register(formData, role);
      
      if (result.success) {
        // Redirect to sign-in page with success message
        router.push('/sign-in?registered=true');
      } else {
        setError(result.error || 'Failed to register');
      }
    } catch (err) {
      setError((err as Error).message || 'Failed to register. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      {/* Left side - Green background with welcome text */}
      <div className="w-full md:w-[40%] bg-gradient-to-br from-green-800 to-green-400 p-10 flex flex-col justify-center text-white relative">
        <div className="max-w-md mx-auto text-center">
          <h1 className="text-3xl font-bold mb-4">Đăng ký ngay!</h1>
          <p className="text-gray-200 opacity-80 mb-12">
            Hãy đăng ký ngay để tận hưởng dịch vụ tốt nhất của chúng tôi hôm nay
          </p>
          <div className="font-bold text-lg py-3 px-6 rounded-lg inline-block">
            <span>Đã có tài khoản? </span>
            <Link href="/sign-in" className='text-orange-300'>Đăng nhập ngay</Link>
          </div>
        </div>
      </div>

      {/* Right side - Form section with light green background */}
      <div className="w-full md:w-[60%] bg-green-50 p-10 flex items-center">
        <div className="w-full max-w-md mx-auto bg-white p-8 rounded-xl shadow-lg">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-800">Đăng ký</h2>
            <p className="text-gray-600 opacity-80 mt-2">
              Nhập thông tin của bạn để đăng ký tài khoản.
            </p>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="rounded-md bg-red-50 p-4">
                <div className="text-sm text-red-700">{error}</div>
              </div>
            )}

            {/* Role Selection */}
            <div className="flex justify-center">
              <div className="bg-green-400 rounded-full px-6 py-3 flex items-center shadow-md">
                <span className="text-white font-medium">Chọn vai trò</span>
              </div>
            </div>

            {/* Role Toggle Buttons */}
            <div className="flex justify-center space-x-6 mt-4">
              <button
                type="button"
                onClick={() => setRole('student')}
                className={`px-6 py-3 rounded-full font-medium transition-all duration-200 ${
                  role === 'student'
                    ? 'bg-green-600 text-white shadow-md'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Sinh viên
              </button>
              <button
                type="button"
                onClick={() => setRole('teacher')}
                className={`px-6 py-3 rounded-full font-medium transition-all duration-200 ${
                  role === 'teacher'
                    ? 'bg-green-600 text-white shadow-md'
                    : 'bg-gray-20 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Giảng viên
              </button>
            </div>

            <div className="space-y-5 mt-8">
              {/* Student ID */}
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                  {role === 'student' ? 'Mã Sinh Viên' : 'Mã Giảng Viên'}
                </label>
                <div className="relative">
                  <input
                    id="username"
                    name="username"
                    type="text"
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-full focus:ring-2 focus:ring-green-500 focus:border-green-500 transition duration-20 shadow-sm"
                    placeholder={role === 'student' ? 'Mã Sinh Viên' : 'Mã Giảng Viên'}
                  />
                </div>
              </div>

              {/* Class/Department */}
              <div>
                <label htmlFor="classOrDepartment" className="block text-sm font-medium text-gray-700 mb-1">
                  {role === 'student' ? 'Lớp' : 'Khoa'}
                </label>
                <div className="relative">
                  <input
                    id="classOrDepartment"
                    name="classOrDepartment"
                    type="text"
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-full focus:ring-2 focus:ring-green-500 focus:border-green-50 transition duration-200 shadow-sm"
                    placeholder={role === 'student' ? 'Lớp' : 'Khoa'}
                  />
                </div>
              </div>

              {/* Full Name */}
              <div>
                <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-1">
                  Họ tên
                </label>
                <div className="relative">
                  <input
                    id="fullName"
                    name="fullName"
                    type="text"
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-full focus:ring-2 focus:ring-green-500 focus:border-green-500 transition duration-20 shadow-sm"
                    placeholder="Họ tên"
                  />
                </div>
              </div>

              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <div className="relative">
                  <input
                    id="email"
                    name="email"
                    type="email"
                    required
                    className="w-full px-4 py-3 border border-gray-30 rounded-full focus:ring-2 focus:ring-green-500 focus:border-green-500 transition duration-20 shadow-sm"
                    placeholder="Email"
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
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-full focus:ring-2 focus:ring-green-500 focus:border-green-500 transition duration-20 shadow-sm"
                    placeholder="Mật khẩu"
                  />
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex justify-center mt-10">
              <button
                type="submit"
                disabled={loading}
                className="bg-green-700 hover:bg-green-800 text-white font-bold py-3 px-12 rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition duration-300 shadow-lg hover:shadow-xl"
              >
                {loading ? 'Đang đăng ký...' : 'Đăng ký'}
              </button>
            </div>
          </form>

          <div className="text-center mt-8">
            <p className="text-sm text-gray-600">
              Đã có tài khoản?{' '}
              <Link href="/sign-in" className="font-medium text-green-600 hover:text-green-500">
                Đăng nhập ngay
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}