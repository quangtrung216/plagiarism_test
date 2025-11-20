'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function MyDocumentsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Tài liệu của tôi</h1>
        <p className="text-muted-foreground">Quản lý tài liệu đã tải lên</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Danh sách Tài liệu</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Chức năng quản lý tài liệu sẽ được triển khai ở đây.</p>
        </CardContent>
      </Card>
    </div>
  );
}