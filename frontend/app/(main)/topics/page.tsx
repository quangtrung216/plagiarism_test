"use client";

import React, { useEffect, useState, ChangeEvent } from "react";
import { getMyTopics, createTopic, updateTopic, deleteTopic } from "../../../services/topicService";
import { Topic } from "@/types";
import { useAuthorization } from "@/providers/AuthorizationProvider";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "../../../components/ui/dialog";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";

type TopicFormData = {
  title: string;
  code: string;
  description?: string;
  public: boolean;
};

const pastelColors = [
  "bg-purple-200 text-purple-800",
  "bg-green-200 text-green-800",
  "bg-orange-200 text-orange-800",
  "bg-pink-200 text-pink-800",
  "bg-purple-100 text-purple-700",
];

const TopicsPage: React.FC = () => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const { user } = useAuthorization();
  
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TopicFormData>();

  const fetchTopics = async () => {
    setLoading(true);
    try {
      const data = await getMyTopics();
      setTopics(data);
      setError(null);
    } catch {
      setError("Lỗi khi tải dữ liệu. Vui lòng thử lại.");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchTopics();
  }, []);

  const openCreateDialog = () => {
    setSelectedTopic(null);
    reset();
    setDialogOpen(true);
  };

  const openEditDialog = (topic: Topic) => {
    setSelectedTopic(topic);
    reset({
      title: topic.title,
      code: topic.code,
      description: topic.description,
      public: topic.public,
    });
    setDialogOpen(true);
  };

  const onSubmit = async (data: TopicFormData) => {
    try {
      if (selectedTopic) {
        await updateTopic(selectedTopic.id, data);
      } else {
        await createTopic(data);
      }
      setDialogOpen(false);
      fetchTopics();
    } catch {
      setError("Lỗi khi lưu chủ đề");
    }
  };

  const deleteTopicHandler = async (topicId: number) => {
    if (!confirm("Bạn có chắc chắn muốn xóa chủ đề này không??")) {
      return;
    }
    try {
      await deleteTopic(topicId);
      fetchTopics();
    } catch {
      setError("Lỗi khi xóa chủ đề");
    }
  };

  const onSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const handleSearch = () => {
    fetchTopics();
  };

  const filteredTopics = topics.filter((topic) =>
    topic.code.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading)
    return (
      <div className="min-h-screen flex items-center justify-center">
        Đang tải dữ liệu...
      </div>
    );
  if (error)
    return (
      <div className="min-h-screen flex items-center justify-center text-red-600">
        {error}
      </div>
    );

  // If user is a student, show a simpler view
  if (user?.role === "student") {
    return (
      <div className="bg-white min-h-screen p-6">
        <h1 className="text-3xl font-bold mb-6">Chủ đề tham gia của tôi</h1>

        {/* Search Bar */}
        <div className="mb-8 max-w-md mx-auto px-4 py-2 bg-gray-100 rounded-full flex items-center gap-2">
          <Input
            type="text"
            placeholder="Tìm kiếm chủ đề của tôi..."
            className="flex-grow bg-gray-200 rounded-full px-4 py-2 focus:outline-none"
            value={searchQuery}
            onChange={onSearchChange}
          />
          <Button
            type="button"
            className="bg-green-800 hover:bg-green-900 text-white px-4 py-2 rounded-full flex items-center gap-2"
            onClick={handleSearch}
            aria-label="Search"
          >
            <svg
              className="w-5 h-5 fill-current"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
            >
              <path d="M21 20l-5.59-5.59A7.92 7.92 0 0016 10a8 8 0 10-8 8 7.92 7.92 0 004.41-1.59L20 21zM10 16a6 6 0 110-12 6 6 0 010 12z" />
            </svg>
            Search
          </Button>
        </div>

        {/* Grid topic cards */}
        <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
          {filteredTopics.length === 0 && (
            <p className="text-center col-span-full">Bạn chưa tham gia bất kỳ chủ đề nào.</p>
          )}
          {filteredTopics.map((topic, index) => {
            const color = pastelColors[index % pastelColors.length];
            const avatarLetter = topic.title.charAt(0).toUpperCase();

            return (
              <div
                key={topic.id}
                className="relative rounded-xl shadow-md overflow-hidden flex flex-col h-64"
              >
                {/* Header with pastel background */}
                <div
                  className={`relative flex flex-col justify-center px-6 h-1/3 ${color}`}
                >
                  <h2 className="font-bold text-lg">{topic.title}</h2>
                  <span className="text-sm">{`Người tạo: ${topic.teacher_info?.full_name || topic.teacher_info?.username || `Teacher ${topic.teacher_id}`}`}</span>
                  {/* Avatar */}
                  <div className="absolute top-full right-6 transform -translate-y-1/2">
                    <div className="w-16 h-16 rounded-full bg-white border border-gray-300 flex items-center justify-center text-2xl font-bold text-gray-700 shadow">
                      {avatarLetter}
                    </div>
                  </div>
                </div>
                {/* Body */}
                <div className="bg-white flex-grow px-6 py-4">
                  {/* Display description as deadline substitute or other info */}
                  <p className="text-gray-700">{topic.description || ""}</p>
                </div>
                {/* Footer */}
                <div className="border-t border-gray-200 px-6 py-3 flex justify-end gap-2 bg-white">
                  <Button
                    variant="outline"
                    className="text-green-600 hover:text-green-800"
                    onClick={() => openEditDialog(topic)}
                  >
                    Đi đến chủ đề
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // Teacher view (existing functionality) - updated to match Figma design
  return (
    <div className="bg-white min-h-screen p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Quản lý chủ đề</h1>
      </div>

      {/* Search Bar - matching Figma design */}
      <div className="mb-8 px-4 py-2 bg-gray-100 rounded-full flex items-center gap-2">
        <Input
          type="text"
          placeholder="Nhập mã chủ đề"
          className="flex-grow bg-gray-200 rounded-full px-4 py-2 focus:outline-none"
          value={searchQuery}
          onChange={onSearchChange}
        />
        <Button
          type="button"
          className="bg-green-800 hover:bg-green-900 text-white px-4 py-2 rounded-full flex items-center gap-2"
          onClick={handleSearch}
          aria-label="Tìm kiếm"
        >
          <svg
            className="w-5 h-5 fill-current"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
          >
            <path d="M21 20l-5.59-5.59A7.92 7.92 0 0016 10a8 8 0 10-8 8 7.92 7.92 0 004.41-1.59L20 21zM10 16a6 6 0 110-12 6 6 0 010 12z" />
          </svg>
          Tìm kiếm
        </Button>
        <Button
          onClick={openCreateDialog}
          className="bg-green-800 hover:bg-green-900 text-white px-4 py-2 rounded-full flex items-center gap-2"
          aria-label="Tạo mới"
        >
          <svg
            className="w-5 h-5 fill-current"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
          >
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
          </svg>
          Tạo mới
        </Button>
      </div>

      {/* Grid topic cards */}
      <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
        {filteredTopics.length === 0 && (
          <p className="text-center col-span-full">Không tìm thấy chủ đề nào.</p>
        )}
        {filteredTopics.map((topic, index) => {
          const color = pastelColors[index % pastelColors.length];
          const avatarLetter = topic.title.charAt(0).toUpperCase();

          return (
            <div
              key={topic.id}
              className="relative rounded-xl shadow-md overflow-hidden flex flex-col h-64"
            >
              {/* Header with pastel background */}
              <div
                className={`relative flex flex-col justify-center px-6 h-1/3 ${color}`}
              >
                <h2 className="font-bold text-lg">{topic.title}</h2>
                <span className="text-sm">{`Giảng viên: ${topic.teacher_id}`}</span>
                {/* Avatar */}
                <div className="absolute top-full right-6 transform -translate-y-1/2">
                  <div className="w-16 h-16 rounded-full bg-white border border-gray-300 flex items-center justify-center text-2xl font-bold text-gray-700 shadow">
                    {avatarLetter}
                  </div>
                </div>
              </div>
              {/* Body */}
              <div className="bg-white flex-grow px-6 py-4">
                {/* Display description as deadline substitute or other info */}
                <p className="text-gray-700">{topic.description || ""}</p>
              </div>
              {/* Footer */}
              <div className="border-t border-gray-200 px-6 py-3 flex justify-end gap-2 bg-white">
                <Button
                  variant="outline"
                  className="text-red-600 hover:text-red-800"
                  onClick={() => deleteTopicHandler(topic.id)}
                  aria-label={`Delete ${topic.title}`}
                  title="Delete"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-6 w-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </Button>
                <Button
                  variant="outline"
                  className="text-green-600 hover:text-green-800"
                  onClick={() => openEditDialog(topic)}
                  aria-label={`Edit ${topic.title}`}
                  title="Edit"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-6 w-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                </Button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Dialog for create/edit */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogTrigger asChild></DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{selectedTopic ? "Cập nhật chủ đề" : "Tạo chủ đề"}</DialogTitle>
            <DialogDescription>
              {selectedTopic
                ? "Update the topic details and save."
                : "Fill the form to create a new topic."}
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 mt-4">
            <div>
              <label className="block mb-1 font-semibold" htmlFor="title">
                Title
              </label>
              <Input
                id="title"
                {...register("title", { required: true })}
              />
              {errors.title && (
                <span className="text-red-600">Tên không được để trống</span>
              )}
            </div>
            <div>
              <label className="block mb-1 font-semibold" htmlFor="description">
                Description
              </label>
              <Textarea
                id="description"
                {...register("description")}
              />
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox id="public" {...register("public")} />
              <label
                htmlFor="public"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Public
              </label>
            </div>

            <DialogFooter>
              <Button type="submit">
                Save
              </Button>
              <DialogClose asChild>
                <Button variant="outline">
                  Cancel
                </Button>
              </DialogClose>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default TopicsPage;