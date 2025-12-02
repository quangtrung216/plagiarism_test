'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Topic } from '@/types';
import { useTopics } from '@/hooks/useTopics';
import { TopicForm } from '@/components/TopicForm';
import { TopicCard } from '@/components/TopicCard';
import { TopicMembersDialog } from '@/components/TopicMembersDialog';
import { Plus, Search } from 'lucide-react';
import { TopicFormData } from '@/services/topicService';

export default function MyTopicsPage() {
  const { topics, loading, error, createNewTopic, updateExistingTopic, deleteExistingTopic } = useTopics();
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingTopic, setEditingTopic] = useState<Topic | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isMembersDialogOpen, setIsMembersDialogOpen] = useState(false);
  const [selectedTopicId, setSelectedTopicId] = useState<number | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [topicToDelete, setTopicToDelete] = useState<Topic | null>(null);

  const handleCreateTopic = async (data: TopicFormData) => {
    await createNewTopic(data);
    handleCloseForm();
  };

  const handleUpdateTopic = async (data: TopicFormData) => {
    if (editingTopic) {
      await updateExistingTopic(editingTopic.id, data);
    }
    handleCloseForm();
  };

  const handleDeleteTopic = (topic: Topic) => {
    setTopicToDelete(topic);
    setIsDeleteDialogOpen(true);
  };

  const confirmDeleteTopic = async () => {
    if (topicToDelete) {
      await deleteExistingTopic(topicToDelete.id);
      setIsDeleteDialogOpen(false);
      setTopicToDelete(null);
    }
  };

  const cancelDeleteTopic = () => {
    setIsDeleteDialogOpen(false);
    setTopicToDelete(null);
  };

  const handleEditTopic = (topic: Topic) => {
    setEditingTopic(topic);
    setIsFormOpen(true);
  };

  const handleCreateNewTopic = () => {
    setEditingTopic(null);
    setIsFormOpen(true);
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setEditingTopic(null);
  };

  const handleManageStudents = (topic: Topic) => {
    setSelectedTopicId(topic.id);
    setIsMembersDialogOpen(true);
  };

  const filteredTopics = topics.filter(topic => 
    topic.title.toLowerCase().includes(searchTerm.toLowerCase())
    // Removed code search since codes are auto-generated
  );

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Chủ đề của tôi</h1>
          <p className="text-muted-foreground">Quản lý chủ đề đã tạo</p>
        </div>
        <div className="flex justify-center items-center h-64">
          <p>Đang tải dữ liệu...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Chủ đề của tôi</h1>
        <p className="text-muted-foreground">Quản lý chủ đề đã tạo</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <CardTitle>Chủ đề</CardTitle>
            <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
              <div className="relative w-full sm:w-64">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Tìm kiếm theo tiêu đề"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 rounded-lg"
                />
              </div>
              <Button className="bg-green-700 hover:bg-green-800 rounded-lg">
                <Search className="mr-2 h-4 w-4" />
                Tìm kiếm
              </Button>
              <Button onClick={handleCreateNewTopic} className="bg-green-700 hover:bg-green-800 rounded-lg">
                <Plus className="mr-2 h-4 w-4" />
                Tạo mới
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-4 p-4 bg-red-50 text-red-700 rounded-md">
              {error}
            </div>
          )}
          
          {filteredTopics.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground mb-4">
                {searchTerm ? 'Không tìm thấy chủ đề phù hợp.' : 'Bạn chưa tạo chủ đề nào.'}
              </p>
              {!searchTerm && (
                <Button onClick={handleCreateNewTopic} className="bg-green-700 hover:bg-green-800 rounded-lg">
                  <Plus className="mr-2 h-4 w-4" />
                  Tạo chủ đề đầu tiên
                </Button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredTopics.map((topic) => (
                <TopicCard
                  key={topic.id}
                  topic={topic}
                  onEdit={handleEditTopic}
                  onDelete={handleDeleteTopic}
                  onManageStudents={handleManageStudents}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <TopicForm
        open={isFormOpen}
        onOpenChange={handleCloseForm}
        onSubmit={editingTopic ? handleUpdateTopic : handleCreateTopic}
        initialData={editingTopic}
      />
      <TopicMembersDialog
        topicId={selectedTopicId}
        open={isMembersDialogOpen}
        onOpenChange={setIsMembersDialogOpen}
      />
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Xác nhận xóa chủ đề</AlertDialogTitle>
            <AlertDialogDescription>
              Bạn có chắc chắn muốn xóa chủ đề "{topicToDelete?.title}" không? Hành động này không thể hoàn tác.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={cancelDeleteTopic}>Hủy</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDeleteTopic} className="bg-red-600 hover:bg-red-700">
              Xóa
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}