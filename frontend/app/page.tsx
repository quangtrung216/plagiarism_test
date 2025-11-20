'use client';

import Image from "next/image";
import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white text-gray-800 font-sans">
      {/* Header */}
      <header className="container mx-auto px-10 py-4 flex justify-between items-center">
        <Image src="/images/logo.png" alt="Logo App" width={160} height={145} />
        <nav className="hidden md:flex items-center space-x-8 text-gray-600 font-medium">
          <a href="#" className="hover:text-primary transition-colors">Giới thiệu</a>
          <a href="#" className="hover:text-primary transition-colors">Kiểm tra đạo văn</a>
          <a href="#" className="hover:text-primary transition-colors">Quản lý chủ đề</a>
          <a href="#" className="hover:text-primary transition-colors">Giúp đỡ</a>
        </nav>
        <div className="flex items-center space-x-4">
          <Link href="/sign-up" className="text-gray-600 font-medium hover:text-primary transition-colors">Đăng ký</Link>
          <Link href="/sign-in" className="border border-primary text-primary px-6 py-2 rounded-full font-semibold hover:bg-primary hover:text-white transition-colors">
            Đăng nhập
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-10 py-16 md:py-24">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-6 max-w-160">
            <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 leading-tight">
              So từng chữ – Giữ niềm tin
            </h1>
            <p className="text-lg text-gray-600">
              Giải pháp AI phát hiện sao chép nhanh, giúp bạn viết đúng và tự tin hơn mỗi ngày.
            </p>
            <button className="bg-primary text-white font-bold py-4 px-8 w-55 rounded-lg shadow-lg hover:bg-red-600 transition-all transform hover:scale-105 flex items-center justify-center space-x-2">
              <span>Bắt đầu</span>
              <svg className="h-6 w-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z" />
              </svg>
            </button>
          </div>
          <div>
            <Image src="/images/hero.png" alt="Student using laptop" className="rounded-sm" width={600} height={540} />
          </div>
        </div>
      </main>

      {/* Stats Section */}
      <section className="bg-gray-50 py-16">
        <div className="container mx-auto px-10">
          <div className="grid md:grid-cols-3 text-center shadow-lg">
            <div className="flex items-center justify-around p-6 bg-white border-r">
              <div className="bg-primary/10 p-4 rounded-full">
                <svg className="h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                </svg>
              </div>
              <div className="flex flex-col">
                <p className="text-3xl font-bold text-gray-900">1500+</p>
                <p className="text-gray-500">Người dùng</p>
              </div>
            </div>
            <div className="flex items-center justify-around p-6 bg-white border-r">
              <div className="bg-primary/10 p-4 rounded-full mb-4">
                <svg className="h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M9 21.035V19.035H5V5H19V11H21V5C21 3.895 20.105 3 19 3H5C3.895 3 3 3.895 3 5V19C3 20.105 3.895 21 5 21H9.035V21.035ZM14 21.035V19.035H11V21.035H14ZM7 17H17V15H7V17ZM17 13H7V11H17V13ZM17 9H7V7H17V9Z" />
                  <path d="M20.707 15.293L16.414 19.586L14.707 17.879L13.293 19.293L16.414 22.414L22.121 16.707L20.707 15.293Z" />
                </svg>
              </div>
              <div className="flex flex-col">
                <p className="text-3xl font-bold text-gray-900">99%</p>
                <p className="text-gray-500">Độ chính xác</p>
              </div>
            </div>
            <div className="flex items-center justify-around p-6 bg-white">
              <div className="bg-primary/10 p-4 rounded-full mb-4">
                <svg className="h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M6 2c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6H6zm8 7V3.5L18.5 9H14z" />
                </svg>
              </div>
              <div className="flex flex-col">
                <p className="text-3xl font-bold text-gray-900">2000+</p>
                <p className="text-gray-500">Tài liệu tham chiếu</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-10 py-24">
        <div className="grid md:grid-cols-2 gap-16 items-center">
          <div>
            <Image src="/images/feature.png" alt="Person with laptop presenting" className="rounded-sm" width={580} height={500} />
          </div>
          <div className="space-y-6">
            <h2 className="text-3xl md:text-4xl font-extrabold text-gray-900">
              Những Tính Năng Nổi Bật Của Hệ Thống
            </h2>
            <p className="text-gray-600">
              Hệ thống giúp sinh viên và giảng viên kiểm tra trùng lặp nội dung, đảm bảo tính trung thực học thuật trong mọi bài viết.
            </p>
            <ul className="space-y-4">
              <li className="flex items-center space-x-3">
                <svg className="h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                </svg>
                <span className="text-gray-700">Kiểm tra trùng lặp chính xác</span>
              </li>
              <li className="flex items-center space-x-3">
                <svg className="h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                </svg>
                <span className="text-gray-700">Đối chiếu với cơ sở dữ liệu lớn</span>
              </li>
              <li className="flex items-center space-x-3">
                <svg className="h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                </svg>
                <span className="text-gray-700">Phân tích mức độ tương đồng</span>
              </li>
              <li className="flex items-center space-x-3">
                <svg className="h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                </svg>
                <span className="text-gray-700">Báo cáo chi tiết, dễ hiểu</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="bg-slate-50 py-24">
        <div className="container mx-auto px-10 text-center">
          <h2 className="text-3xl md:text-4xl font-extrabold text-gray-900 mb-4">Các bước sử dụng thật đơn giản</h2>
          <p className="text-gray-600 mb-12 max-w-2xl mx-auto">Chỉ cần vài thao tác là bạn đã có thể đảm bảo chất lượng bài viết của mình</p>
          <div className="grid md:grid-cols-3 gap-12">
            {/* Step 1 */}
            <div className="bg-white px-8 py-22 rounded-md shadow-lg flex flex-col items-center border">
              <Image src="/images/browsing.png" alt="Step 1 icon" className="rounded-sm mb-6" width={170} height={150} />
              <h3 className="text-xl font-bold mb-2">Bước 1</h3>
              <div className="flex items-center text-green-600 space-x-2 my-4 h-64">
                <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                </svg>
                <span>Đăng nhập tài khoản</span>
              </div>
              <button className="mt-auto bg-primary text-white font-semibold py-3 px-8 rounded-full shadow-md hover:bg-red-600 transition-all">
                Bắt đầu ngay
              </button>
            </div>
            {/* Step 2 */}
            <div className="bg-white px-8 py-22 rounded-md shadow-lg flex flex-col items-center border">
              <Image src="/images/browsing.png" alt="Step 2 icon" className="rounded-sm mb-6" width={170} height={150} />
              <h3 className="text-xl font-bold mb-2">Bước 2</h3>
              <div className="flex items-center text-green-600 space-x-2 my-4 h-64">
                <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                </svg>
                <span>Tải lên bài viết cần kiểm tra</span>
              </div>
              <button className="mt-auto bg-primary text-white font-semibold py-3 px-8 rounded-full shadow-md hover:bg-red-600 transition-all">
                Bắt đầu ngay
              </button>
            </div>
            {/* Step 3 */}
            <div className="bg-white px-8 py-22 rounded-md shadow-lg flex flex-col items-center border">
              <Image src="/images/browsing.png" alt="Step 3 icon" className="rounded-sm mb-6" width={170} height={150} />
              <h3 className="text-xl font-bold mb-2">Bước 3</h3>
              <div className="flex items-center text-green-600 space-x-2 my-4 h-64">
                <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                </svg>
                <span>Nhận kết quả chính xác</span>
              </div>
              <button className="mt-auto bg-primary text-white font-semibold py-3 px-8 rounded-full shadow-md hover:bg-red-600 transition-all">
                Bắt đầu ngay
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Connection Diagram Section */}
      <section>
        <div className="container mx-auto px-10 text-center">
          <h2 className="text-3xl md:text-4xl font-extrabold text-gray-900 mb-4">Cầu nối học thuật giữa <br /> giảng viên và sinh viên</h2>
          <p className="text-gray-600 mb-16 max-w-3xl mx-auto">
            Plagiarism Detector là hệ thống cho phép kết nối giảng viên và sinh viên thông qua việc kiểm tra đạo văn và cho phép nộp bài, một ứng dụng chưa từng có.
          </p>
          <Image src="/images/diagram.png" alt="Diagram Image" width={1000} height={800} className="mx-auto mt-16" />
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="bg-white pt-24">
        <div className="container mx-auto px-8 text-center py-16 flex justify-between items-center">
          <div className="text-start">
            <h2 className="text-3xl md:text-4xl font-extrabold text-gray-900 mb-4 max-w-100">Cải thiện tính chính xác bài viết của bạn!</h2>
            <p className="text-gray-600">Kiểm tra đạo văn và cho ra bài viết tốt nhất.</p>
          </div>
          <button className="bg-primary text-white text-[#ffffff] font-bold py-3 px-8 w-60 h-16 rounded-md shadow-2xl hover:bg-red-600 transition-all transform hover:scale-105">
            Trải nghiệm ngay
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-100 pt-16 pb-8">
        <div className="container mx-auto px-6 grid md:grid-cols-4 gap-8 text-gray-600">
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Image src="/images/logo.png" alt="Logo App" width={160} height={145} className="bg-gray-100" />
            </div>
            <p className="text-sm">Hệ thống được xây dựng bởi trường Đại học SPKT Hưng Yên</p>
            <div className="flex space-x-3">
              <a href="#" className="bg-primary p-2 rounded-full text-[#ffffff] shadow-md">
                <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878V14.89H8.018v-2.89h2.42V9.59c0-2.399 1.433-3.725 3.623-3.725 1.032 0 2.16.184 2.16.184v2.443h-1.22c-1.18 0-1.56.73-1.56 1.505v1.787h2.72l-.438 2.89h-2.282v7.028C18.343 21.128 22 16.991 22 12z" /></svg>
              </a>
              <a href="#" className="bg-primary p-2 rounded-full text-[#ffffff] shadow-md">
                <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V8l8 5 8-5v10zm-8-7L4 6h16l-8 5z" /></svg>
              </a>
              <a href="#" className="bg-primary p-2 rounded-full text-[#ffffff] shadow-md">
                <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" /></svg>
              </a>
            </div>
          </div>
          <div>
            <h4 className="font-bold text-gray-800 mb-4">Hệ thống</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="hover:text-primary">Giới thiệu</a></li>
              <li><a href="#" className="hover:text-primary">Tính năng</a></li>
              <li><a href="#" className="hover:text-primary">Quy trình</a></li>
              <li><a href="#" className="hover:text-primary">Tin tức & Cập nhật</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold text-gray-800 mb-4">Hỗ trợ</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="hover:text-primary">Hướng dẫn sử dụng</a></li>
              <li><a href="#" className="hover:text-primary">Câu hỏi thường gặp FAQ</a></li>
              <li><a href="#" className="hover:text-primary">Chính sách bảo mật</a></li>
              <li><a href="#" className="hover:text-primary">Điều khoản sử dụng</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold text-gray-800 mb-4">Liên hệ</h4>
            <ul className="space-y-2 text-sm">
              <li>Email: dhspkt@utehy.edu.vn</li>
              <li>Điện thoại: 0321.3713081</li>
              <li>Địa chỉ: Xã Dân Tiến, huyện Khoái Châu, tỉnh Hưng Yên</li>
            </ul>
          </div>
        </div>
      </footer>
    </div>
  )
}