'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
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
      <div className="w-full md:w-[40%] bg-gradient-to-br bg-[#2E7D32BF] p-10 flex flex-col justify-center text-white relative space-y-90">
        <div className="max-w-md mx-auto text-center flex flex-col justify-center">
          <h1 className="text-3xl font-bold mb-3">Đăng ký ngay!</h1>
          <p className="text-gray-200 opacity-80">
            Hãy đăng ký ngay để tận hưởng dịch vụ tốt nhất của chúng tôi hôm nay
          </p>
        </div>
        <div className="max-w-md mx-auto text-center">
          <div className="font-bold text-lg py-3 px-6 rounded-lg inline-block">
            <span>Đã có tài khoản? </span>
            <Link href="/sign-in" className='text-orange-300'>Đăng nhập ngay</Link>
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

          <form className="space-y-6" onSubmit={handleSubmit}>
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
            </div>

            <div className="space-y-5">
              {/* Student ID */}
              <div>
                <label htmlFor="username" className="block text-md font-medium text-[#000000] mb-1">
                  {role === 'student' ? 'Mã sinh viên' : 'Mã giảng viên'}
                </label>
                <div className="relative">
                  <input
                    id="username"
                    name="username"
                    type="text"
                    required
                    className="w-full px-4 py-3 border-2 border-[#000000] rounded-full bg-gray-300"
                    placeholder={role === 'student' ? 'Mã sinh viên' : 'Mã giảng viên'}
                  />
                </div>
              </div>

              {/* Full Name */}
              <div>
                <label htmlFor="fullName" className="block text-md font-medium text-[#000000] mb-1">
                  Họ tên
                </label>
                <div className="relative">
                  <input
                    id="fullName"
                    name="fullName"
                    type="text"
                    required
                    className="w-full px-4 py-3 border-2 border-[#000000] rounded-full bg-gray-300"
                    placeholder="Họ tên"
                  />
                </div>
              </div>

              {/* Class/Department */}
              <div>
                <label htmlFor="classOrDepartment" className="block text-md font-medium text-[#000000] mb-1">
                  {role === 'student' ? 'Lớp' : 'Khoa'}
                </label>
                <div className="relative">
                  <input
                    id="classOrDepartment"
                    name="classOrDepartment"
                    type="text"
                    required
                    className="w-full px-4 py-3 border-2 border-[#000000] rounded-full bg-gray-300"
                    placeholder={role === 'student' ? 'Lớp' : 'Khoa'}
                  />
                </div>
              </div>

              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-md font-medium text-[#000000] mb-1">
                  Email
                </label>
                <div className="relative">
                  <input
                    id="email"
                    name="email"
                    type="email"
                    required
                    className="w-full px-4 py-3 border-2 border-[#000000] rounded-full bg-gray-300"
                    placeholder="Email"
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
                    required
                    className="w-full px-4 py-3 border-2 border-[#000000] rounded-full bg-gray-300"
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
                className="bg-green-700 hover:bg-green-800 text-white font-bold py-3 px-12 rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition duration-300 shadow-lg hover:shadow-xl text-lg cursor-pointer"
              >
                {loading ? 'Đang đăng ký...' : 'Đăng ký'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}