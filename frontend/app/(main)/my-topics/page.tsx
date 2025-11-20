'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function MyTopicsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Chủ đề của tôi</h1>
        <p className="text-muted-foreground">Quản lý chủ đề đã tạo</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Chủ đề</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Chức năng quản lý chủ đề sẽ được triển khai ở đây.</p>
        </CardContent>
      </Card>
    </div>
  );
}