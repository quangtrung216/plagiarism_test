"use client";

import React, { useEffect, useState, ChangeEvent } from "react";
import { Topic } from "@/types";
import { searchPublicTopics, requestJoinTopicByCode, getMyJoinedTopics } from "@/services/topicService";
import { useAuthorization } from "@/providers/AuthorizationProvider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const pastelColors = [
  "bg-purple-200 text-purple-800",
  "bg-green-200 text-green-800",
  "bg-orange-200 text-orange-800",
  "bg-pink-200 text-pink-800",
  "bg-purple-100 text-purple-700",
];

const StudentTopicsPage: React.FC = () => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [joiningTopic, setJoiningTopic] = useState<number | null>(null);
  // Track which topics the user has already joined
  const [joinedTopics, setJoinedTopics] = useState<Set<number>>(new Set());
  const { user } = useAuthorization();

  // Fetch public topics and user's joined topics
  const fetchTopics = async () => {
    setLoading(true);
    try {
      // Fetch public topics
      const publicTopics = await searchPublicTopics();
      setTopics(publicTopics);
      
      // Fetch user's joined topics
      const userJoinedTopics = await getMyJoinedTopics();
      setJoinedTopics(new Set(userJoinedTopics.map(topic => topic.id)));
      
      setError(null);
    } catch (err) {
      setError("Lỗi khi tải dữ liệu. Vui lòng thử lại.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTopics();
  }, []);

  const onSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const handleSearch = async () => {
    setLoading(true);
    try {
      const data = await searchPublicTopics(searchQuery);
      setTopics(data);
      setError(null);
    } catch (err) {
      setError("Lỗi khi tải dữ liệu. Vui lòng thử lại.");
      console.error(err);
    }
    setLoading(false);
  };

  const handleJoinTopic = async (topicCode: string, topicId: number) => {
    try {
      setJoiningTopic(topicId);
      await requestJoinTopicByCode(topicCode);
      toast.success("Yêu cầu tham gia chủ đề đã được gửi!");
      // Add the topic to joined topics
      setJoinedTopics(prev => new Set(prev).add(topicId));
    } catch (err: any) {
      // Check if the error is the specific "already requested" message
      if (err.message && err.message.includes("You have already requested to join this topic")) {
        toast.error("Bạn đã yêu cầu tham gia chủ đề này");
        // Add the topic to joined topics to prevent future attempts
        setJoinedTopics(prev => new Set(prev).add(topicId));
      } else {
        toast.error("Thất bại khi tham gia chủ đề");
      }
      console.error(err);
    } finally {
      setJoiningTopic(null);
    }
  };

  const filteredTopics = topics.filter((topic) =>
    topic.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
    topic.title.toLowerCase().includes(searchQuery.toLowerCase())
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

  return (
    <div className="bg-white min-h-screen p-6">
      <h1 className="text-3xl font-bold mb-6">Các chủ đề khả dụng</h1>

      {/* Search Bar - matching Figma design */}
      <div className="mb-8 max-w-md mx-auto px-4 py-2 bg-gray-100 rounded-full flex items-center gap-2">
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
            <Card key={topic.id} className="rounded-xl shadow-md overflow-hidden flex flex-col h-[350px]">
              {/* Header with pastel background */}
              <CardHeader className={`relative flex flex-col justify-center px-6 h-1/3 ${color}`}>
                <CardTitle className="font-bold text-lg">{topic.title}</CardTitle>
                <CardDescription className="text-sm">{`Giảng viên: ${topic.teacher_info?.full_name || topic.teacher_info?.username || `Teacher ${topic.teacher_id}`}`}</CardDescription>
                {/* Avatar */}
                <div className="absolute top-full right-6 transform -translate-y-1/2">
                  <div className="w-16 h-16 rounded-full bg-white border border-gray-300 flex items-center justify-center text-2xl font-bold text-gray-700 shadow">
                    {avatarLetter}
                  </div>
                </div>
              </CardHeader>
              
              {/* Body */}
              <CardContent className="bg-white flex-grow px-6 py-4">
                <p className="text-gray-700">{topic.description || "No description"}</p>
                <div className="mt-2">
                  <span className="inline-block bg-gray-200 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 mr-2">
                    {topic.code}
                  </span>
                </div>
              </CardContent>
              
              {/* Footer */}
              <CardFooter className="border-t border-gray-200 px-6 py-3 flex justify-end gap-2 bg-white">
                {joinedTopics.has(topic.id) ? (
                  <Button
                    className="bg-gray-500 text-white cursor-not-allowed"
                    disabled={true}
                  >
                    Đã tham gia
                  </Button>
                ) : (
                  <Button
                    onClick={() => handleJoinTopic(topic.code, topic.id)}
                    className="bg-green-600 hover:bg-green-700 text-white"
                    disabled={joiningTopic === topic.id}
                  >
                    {joiningTopic === topic.id ? "Đang tham gia..." : "Tham gia chủ đề"}
                  </Button>
                )}
              </CardFooter>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

export default StudentTopicsPage;