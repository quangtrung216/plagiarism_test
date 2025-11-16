'use client';

import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import Image from 'next/image';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="flex justify-between items-center px-8 py-6">
        <Image src={"/images/logo.png"} alt="Logo" width={100} height={100}/>
        <nav className="hidden md:flex space-x-8">
          <a href="#features" className="text-[#4F5665] hover:text-[#0B132A]">Tính năng</a>
          <a href="#process" className="text-[#4F5665] hover:text-[#0B132A]">Quy trình</a>
          <a href="#support" className="text-[#4F5665] hover:text-[#0B132A]">Hỗ trợ</a>
          <a href="#contact" className="text-[#4F5665] hover:text-[#0B132A]">Liên hệ</a>
        </nav>
        <div className="flex space-x-4">
          <Link href="/sign-in">
            <Button variant="outline" className="border-[#F53855] text-[#F53855] hover:bg-[#F53855] hover:text-white">
              Đăng nhập
            </Button>
          </Link>
          <Link href="/sign-in">
            <Button className="bg-[#F53838] hover:bg-[#F53838]/90 text-white">
              Đăng ký
            </Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="px-8 py-16 md:py-24">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold text-[#0B132A] mb-6">
              So từng chữ – Giữ niềm tin
            </h1>
            <p className="text-xl text-[#4F5665] mb-8">
              Giải pháp AI phát hiện sao chép nhanh, giúp bạn viết đúng và tự tin hơn mỗi ngày.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/sign-in">
                <Button className="bg-[#F53838] hover:bg-[#F53838]/90 text-white px-8 py-6 text-lg">
                  Bắt đầu
                </Button>
              </Link>
              <Button variant="outline" className="border-[#0B132A] text-[#0B132A] hover:bg-[#0B132A] hover:text-white px-8 py-6 text-lg">
                Giới thiệu
              </Button>
            </div>
            
            {/* Stats */}
            <div className="mt-12 grid grid-cols-3 gap-8">
              <div>
                <p className="text-2xl font-bold text-[#0B132A]">99%</p>
                <p className="text-[#4F5665]">Độ chính xác</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-[#0B132A]">1500+</p>
                <p className="text-[#4F5665]">Người dùng</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-[#0B132A]">2000+</p>
                <p className="text-[#4F5665]">Tài liệu tham chiếu</p>
              </div>
            </div>
          </div>
          <Image src={"/images/landing1.png"} alt="Landing Illustration" width={500} height={300}/>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="px-8 py-16 bg-[#F8F8F8]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-[#0B132A] mb-4">
              Những Tính Năng Nổi Bật Của Hệ Thống
            </h2>
            <p className="text-xl text-[#4F5665] max-w-3xl mx-auto">
              Hệ thống giúp sinh viên và giảng viên kiểm tra trùng lặp nội dung, đảm bảo tính trung thực học thuật trong mọi bài viết.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <Image src={"/images/landing2.png"} alt="Feature Illustration" width={500} height={300}/>
            
            <div className="space-y-6">
              <div className="flex items-start">
                <div className="bg-white p-2 rounded-full mr-4">
                  <div className="w-6 h-6 text-[#2FAB73]">✓</div>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-[#0B132A] mb-2">Kiểm tra trùng lặp chính xác</h3>
                  <p className="text-[#4F5665]">Hệ thống sử dụng công nghệ AI tiên tiến để phát hiện đạo văn với độ chính xác cao.</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="bg-white p-2 rounded-full mr-4">
                  <div className="w-6 h-6 text-[#2FAB73]">✓</div>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-[#0B132A] mb-2">Đối chiếu với cơ sở dữ liệu lớn</h3>
                  <p className="text-[#4F5665]">So sánh với hàng triệu tài liệu tham khảo để đảm bảo kết quả kiểm tra toàn diện.</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="bg-white p-2 rounded-full mr-4">
                  <div className="w-6 h-6 text-[#2FAB73]">✓</div>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-[#0B132A] mb-2">Phân tích mức độ tương đồng</h3>
                  <p className="text-[#4F5665]">Cung cấp phân tích chi tiết về mức độ tương đồng giữa các tài liệu.</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="bg-white p-2 rounded-full mr-4">
                  <div className="w-6 h-6 text-[#2FAB73]">✓</div>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-[#0B132A] mb-2">Báo cáo chi tiết, dễ hiểu</h3>
                  <p className="text-[#4F5665]">Tạo báo cáo trực quan giúp người dùng dễ dàng hiểu và xử lý kết quả.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section id="process" className="px-8 py-16">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-[#0B132A] mb-4">
              Các bước sử dụng thật đơn giản
            </h2>
            <p className="text-xl text-[#4F5665] max-w-3xl mx-auto">
              Chỉ cần vài thao tác là bạn đã có thể đảm bảo chất lượng bài viết của mình
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="border border-gray-200 rounded-lg p-8 text-center">
              <div className="w-[100px] h-[100px] mx-auto mb-6 rounded-lg bg-white border border-gray-200 flex items-center justify-center text-2xl font-bold text-[#0B132A]">
                <div className='flex flex-col items-center'>
                  <Image src={"/images/browsing.png"} alt="Browsing" width={50} height={50} />
                  <span>Bước 1</span>
                </div>
              </div>
              <h3 className="text-xl font-semibold text-[#0B132A] mb-4">Đăng nhập tài khoản</h3>
            </div>
            
            {/* Step 2 */}
            <div className="border border-gray-200 rounded-lg p-8 text-center">
              <div className="w-[100px] h-[100px] mx-auto mb-6 rounded-lg bg-white border border-gray-200 flex items-center justify-center text-2xl font-bold text-[#0B132A]">
                <div className='flex flex-col items-center'>
                  <Image src={"/images/browsing.png"} alt="Upload" width={50} height={50} />
                  <span>Bước 2</span>
                </div>
              </div>
              <h3 className="text-xl font-semibold text-[#0B132A] mb-4">Tải lên bài viết cần kiểm tra</h3>
            </div>
            
            {/* Step 3 */}
            <div className="border border-gray-200 rounded-lg p-8 text-center">
              <div className="w-[100px] h-[100px] mx-auto mb-6 rounded-lg bg-white border border-gray-200 flex items-center justify-center text-2xl font-bold text-[#0B132A]">
                <div className='flex flex-col items-center'>
                  <Image src={"/images/browsing.png"} alt="Result" width={50} height={50} />
                  <span>Bước 3</span>
                </div>
              </div>
              <h3 className="text-xl font-semibold text-[#0B132A] mb-4">Nhận kết quả chính xác</h3>
            </div>
          </div>
          
          <div className="text-center mt-12">
            <Link href="/sign-in">
              <Button className="bg-[#F53838] hover:bg-[#F53838]/90 text-white px-8 py-6 text-lg">
                Bắt đầu ngay
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-8 py-16 bg-[#0D1025] text-white">
        <div className="max-w-7xl mx-auto rounded-2xl p-12 text-center" style={{ opacity: 0.06, filter: 'blur(114px)' }}></div>
        <div className="max-w-4xl mx-auto text-center relative -mt-32">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Cải thiện tính chính xác bài viết của bạn!
          </h2>
          <p className="text-xl mb-8">
            Kiểm tra đạo văn và cho ra bài viết tốt nhất.
          </p>
          <Link href="/sign-in">
            <Button className="bg-[#F53838] hover:bg-[#F53838]/90 text-white px-8 py-6 text-lg">
              Trải nghiệm ngay
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer id="contact" className="px-8 py-16 bg-[#F8F8F8]">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-xl font-semibold text-[#0B132A] mb-4">Hệ thống</h3>
              <p className="text-[#4F5665]">
                Hệ thống được xây dựng bởi trường Đại học SPKT Hưng Yên
              </p>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-[#0B132A] mb-4">Giới thiệu</h4>
              <ul className="space-y-2 text-[#4F5665]">
                <li><a href="#" className="hover:text-[#0B132A]">Tính năng</a></li>
                <li><a href="#" className="hover:text-[#0B132A]">Quy trình</a></li>
                <li><a href="#" className="hover:text-[#0B132A]">Tin tức & Cập nhật</a></li>
              </ul>
            </div>
            
            <div id="support">
              <h4 className="text-lg font-semibold text-[#0B132A] mb-4">Hỗ trợ</h4>
              <ul className="space-y-2 text-[#4F5665]">
                <li><a href="#" className="hover:text-[#0B132A]">Hướng dẫn sử dụng</a></li>
                <li><a href="#" className="hover:text-[#0B132A]">Câu hỏi thường gặp FAQ</a></li>
                <li><a href="#" className="hover:text-[#0B132A]">Chính sách bảo mật</a></li>
                <li><a href="#" className="hover:text-[#0B132A]">Điều khoản sử dụng</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-[#0B132A] mb-4">Liên hệ</h4>
              <ul className="space-y-2 text-[#4F5665]">
                <li>Email: dhspkt@utehy.edu.vn</li>
                <li>Điện thoại: 0321.3713081</li>
                <li>Địa chỉ: Xã Dân Tiến, huyện Khoái Châu, tỉnh Hưng Yên</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-200 mt-12 pt-8 text-center text-[#4F5665]">
            <p>&copy; {new Date().getFullYear()} Hệ thống. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}