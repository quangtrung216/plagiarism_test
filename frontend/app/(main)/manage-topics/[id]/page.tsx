'use client';

import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { Topic, TopicMember } from '@/types';
import { useTopic } from '@/hooks/useTopic';
import { useTopicMembers } from '@/hooks/useTopicMembers';
import { Download, Eye, FileText, MoreHorizontal } from 'lucide-react';

export default function ManageTopicDetailPage() {
  const params = useParams();
  const topicId = Number(params.id);
  
  const { topic, loading: topicLoading, error: topicError } = useTopic(topicId);
  const { members, loading: membersLoading, error: membersError } = useTopicMembers(topicId);
  
  const [activeTab, setActiveTab] = useState<'members' | 'reports'>('members');

  if (topicLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">Đang tải...</h1>
        </div>
        <div className="flex justify-center items-center h-64">
          <p>Đang tải thông tin chủ đề...</p>
        </div>
      </div>
    );
  }

  if (topicError || !topic) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">Lỗi</h1>
        </div>
        <div className="flex justify-center items-center h-64">
          <p className="text-red-500">Không thể tải thông tin chủ đề: {topicError}</p>
        </div>
      </div>
    );
  }

  // Filter accepted members
  const acceptedMembers = members.filter(member => member.status === 'accepted');

  // Calculate similarity rate (mock data for now)
  const getSimilarityRate = (studentId: number) => {
    // This would be replaced with actual data from the backend
    const rates = [21, 32, 25, 11, 38, 19];
    return rates[studentId % rates.length] || 25;
  };

  // Get similarity color based on rate
  const getSimilarityColor = (rate: number) => {
    if (rate > 30) return 'bg-red-200 text-red-800';
    return 'bg-green-200 text-green-800';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">{topic.title}</h1>
        <div className="mt-2 flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
          <span>Gv: {topic.teacher_info?.full_name || 'N/A'}</span>
          <span>Mã chủ đề: {topic.code}</span>
          <span>Tỉ lệ: 30%</span>
        </div>
      </div>

      {/* Main Content */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <CardTitle>Chi tiết chủ đề</CardTitle>
            <Button className="bg-green-700 hover:bg-green-800 rounded-lg">
              <Download className="mr-2 h-4 w-4" />
              Tải lên
            </Button>
          </div>
          
          {/* Tabs */}
          <div className="flex border-b">
            <button
              className={`py-2 px-4 font-medium text-sm ${
                activeTab === 'members'
                  ? 'border-b-2 border-green-700 text-green-700'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
              onClick={() => setActiveTab('members')}
            >
              Thành viên
            </button>
            <button
              className={`py-2 px-4 font-medium text-sm ${
                activeTab === 'reports'
                  ? 'border-b-2 border-green-700 text-green-700'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
              onClick={() => setActiveTab('reports')}
            >
              Báo cáo
            </button>
          </div>
        </CardHeader>
        
        <CardContent>
          {membersLoading ? (
            <div className="flex justify-center items-center h-64">
              <p>Đang tải danh sách thành viên...</p>
            </div>
          ) : membersError ? (
            <div className="flex justify-center items-center h-64">
              <p className="text-red-500">Lỗi khi tải danh sách thành viên: {membersError}</p>
            </div>
          ) : activeTab === 'members' ? (
            // Members Table
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[100px]">STT</TableHead>
                    <TableHead>Lớp</TableHead>
                    <TableHead>Mã sinh viên</TableHead>
                    <TableHead>Họ tên</TableHead>
                    <TableHead>Email</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {acceptedMembers.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                        Không có thành viên nào
                      </TableCell>
                    </TableRow>
                  ) : (
                    acceptedMembers.map((member, index) => (
                      <TableRow key={member.id}>
                        <TableCell className="font-medium">{index + 1}</TableCell>
                        <TableCell>12523W1</TableCell>
                        <TableCell>{member.student.student_profile?.student_id || 'N/A'}</TableCell>
                        <TableCell>{member.student.full_name || member.student.username}</TableCell>
                        <TableCell>{member.student.email}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          ) : (
            // Reports Table
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[100px]">STT</TableHead>
                    <TableHead>Mã sinh viên</TableHead>
                    <TableHead>Họ tên</TableHead>
                    <TableHead>Tên báo cáo</TableHead>
                    <TableHead>Lần nộp gần nhất</TableHead>
                    <TableHead>Tỉ lệ</TableHead>
                    <TableHead>Thao tác</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {acceptedMembers.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                        Không có báo cáo nào
                      </TableCell>
                    </TableRow>
                  ) : (
                    acceptedMembers.map((member, index) => {
                      const rate = getSimilarityRate(index);
                      return (
                        <TableRow key={member.id}>
                          <TableCell className="font-medium">{index + 1}</TableCell>
                          <TableCell>{member.student.student_profile?.student_id || 'N/A'}</TableCell>
                          <TableCell>{member.student.full_name || member.student.username}</TableCell>
                          <TableCell className="max-w-xs truncate">
                            Baocaowebbandodien...
                          </TableCell>
                          <TableCell>12/08/2025</TableCell>
                          <TableCell>
                            <Badge className={getSimilarityColor(rate)}>
                              {rate}%
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex space-x-2">
                              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                <Eye className="h-4 w-4" />
                              </Button>
                              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                <FileText className="h-4 w-4" />
                              </Button>
                              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
              
              {/* Download Report Button */}
              <div className="mt-6 flex justify-end">
                <Button className="bg-green-700 hover:bg-green-800 rounded-lg">
                  <Download className="mr-2 h-4 w-4" />
                  Tải báo cáo chung
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}