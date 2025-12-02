'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useAuthorization } from '@/providers/AuthorizationProvider';
import { signOut } from '@/lib/actions';

const UserMenu: React.FC = () => {
  const { user } = useAuthorization();
  const router = useRouter();

  const handleLogout = async () => {
    // Use server action to clear token
    await signOut();
    
    // Redirect to sign-in page regardless of result
    router.push('/sign-in');
  };

  const getUserInitials = () => {
    if (user.full_name) {
      return user.full_name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase();
    }
    return user.username.substring(0, 2).toUpperCase();
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="relative p-0 cursor-pointer">
          <Avatar className="h-12 w-12">
            <AvatarImage src="/icons/avata.png" alt={user.full_name} />
            <AvatarFallback>{getUserInitials()}</AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56" align="end" forceMount>
        <div className="flex items-center justify-start gap-2 p-2">
          <div className="flex flex-col space-y-1 leading-none">
            <p className="font-medium">{user.full_name}</p>
            <p className="text-muted-foreground text-xs">{user.email}</p>
          </div>
        </div>
        <DropdownMenuItem onClick={handleLogout}>
          Đăng xuất
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default UserMenu;