'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { 
  Home, 
  LogOut, 
  BookOpen, 
  FileText 
} from 'lucide-react';

interface MenuItem {
  title: string;
  href: string;
  icon?: React.ReactNode;
}

interface SidebarProps {
  role: string;
}

const Sidebar: React.FC<SidebarProps> = ({ role }) => {
  const pathname = usePathname();

  // Define menu items based on user role
  const getMenuItems = (): MenuItem[] => {
    const commonItems: MenuItem[] = [
      { title: 'Trang chủ', href: '/dashboard', icon: <Home className="h-4 w-4" /> },
      { title: 'Đăng xuất', href: '/sign-in', icon: <LogOut className="h-4 w-4" /> },
    ];

    if (role === 'student') {
      return [
        { title: 'Chủ đề', href: '/topics', icon: <BookOpen className="h-4 w-4" /> },
        { title: 'Tài liệu của tôi', href: '/my-documents', icon: <FileText className="h-4 w-4" /> },
        ...commonItems,
      ];
    } else if (role === 'lecturer') {
      return [
        { title: 'Chủ đề', href: '/topics', icon: <BookOpen className="h-4 w-4" /> },
        ...commonItems,
      ];
    }

    return commonItems;
  };

  const menuItems = getMenuItems();

  return (
    <div className="flex flex-col h-full bg-gray-50 border-r w-64">
      {/* Logo */}
      <div className='p-4'>
        <Image src="/images/logo.png" alt="Logo App" width={160} height={145} />
      </div>

      {/* Menu Items */}
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-1 px-2">
          {menuItems.map((item) => (
            <li key={item.href}>
              <Button
                asChild
                variant={pathname === item.href ? 'default' : 'ghost'}
                className={cn(
                  'w-full justify-start',
                  pathname === item.href ? 'bg-primary text-primary-foreground' : ''
                )}
              >
                <Link href={item.href}>
                  {item.icon && <span className="mr-2">{item.icon}</span>}
                  {item.title}
                </Link>
              </Button>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar;