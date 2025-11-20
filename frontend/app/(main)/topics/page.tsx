'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function TopicsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Quản lý Chủ đề</h1>
        <p className="text-muted-foreground">Quản lý các chủ đề đồ án</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Danh sách Chủ đề</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Chức năng quản lý chủ đề sẽ được triển khai ở đây.</p>
        </CardContent>
      </Card>
    </div>
  );
}