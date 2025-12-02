'use client';

import { Topic } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Trash2, Edit, Users } from 'lucide-react';
import Link from 'next/link';

interface TopicCardProps {
  topic: Topic;
  onEdit: (topic: Topic) => void;
  onDelete: (topic: Topic) => void;
  onManageStudents: (topic: Topic) => void;
}

export function TopicCard({ topic, onEdit, onDelete, onManageStudents }: TopicCardProps) {
  // Function to get color based on topic title (matching Figma design)
  const getHeaderColor = () => {
    if (topic.title.includes('Kiểm thử')) return 'bg-green-200';
    if (topic.title.includes('Web')) return 'bg-pink-200';
    return 'bg-purple-200';
  };

  // Function to get instructor name from topic data
  const getInstructorName = () => {
    if (topic.teacher_info) {
      return topic.teacher_info.full_name || topic.teacher_info.username;
    }
    return `Teacher ${topic.teacher_id}`;
  };

  return (
    <Link href={`/manage-topics/${topic.id}`} className="block">
      <Card className="w-full max-w-sm overflow-hidden rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
        {/* Header with color based on topic */}
        <div className={`h-24 ${getHeaderColor()}`} />
        
        {/* Content */}
        <CardHeader className="pb-2 relative">
          {/* Edit/Delete buttons positioned in top-right corner */}
          <div className="absolute top-4 right-4 flex space-x-1">
            <Button 
              variant="ghost" 
              size="icon-sm" 
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onEdit(topic);
              }}
              aria-label="Edit topic"
              className="h-8 w-8 rounded-full bg-white shadow-sm hover:bg-gray-100"
            >
              <Edit className="h-4 w-4 text-gray-600" />
            </Button>
            <Button 
              variant="ghost" 
              size="icon-sm" 
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onDelete(topic);
              }}
              aria-label="Delete topic"
              className="h-8 w-8 rounded-full bg-white shadow-sm hover:bg-gray-100"
            >
              <Trash2 className="h-4 w-4 text-gray-600" />
            </Button>
          </div>
          
          {/* Topic title */}
          <CardTitle className="text-lg line-clamp-2 pr-16">{topic.title}</CardTitle>
          
          {/* Instructor name */}
          <p className="text-sm text-muted-foreground">Giảng viên: {getInstructorName()}</p>
        </CardHeader>
        
        <CardContent className="pt-2">
          {/* Code and Students button */}
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Code: {topic.code}</span>
            <Button 
              variant="outline" 
              size="sm" 
              className="rounded-full"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onManageStudents(topic);
              }}
            >
              <Users className="h-4 w-4 mr-1" />
              Quản lý sinh viên
            </Button>
          </div>
          
          {/* Deadline if exists */}
          {topic.deadline && (
            <p className="text-sm mt-3 pt-3 border-t border-gray-100">
              Hạn: {new Date(topic.deadline).toLocaleDateString('vi-VN')}
            </p>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}