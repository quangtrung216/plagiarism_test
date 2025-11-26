"use client";

import React, { useEffect, useState, ChangeEvent } from "react";
import topicService from "../../../services/topicService";
import { Topic } from "@/types";
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
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TopicFormData>();

  const fetchTopics = async () => {
    setLoading(true);
    try {
      const data = await topicService.getMyTopics();
      setTopics(data);
      setError(null);
    } catch {
      setError("Failed to fetch topics");
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
        await topicService.updateTopic(selectedTopic.id, data);
      } else {
        await topicService.createTopic(data);
      }
      setDialogOpen(false);
      fetchTopics();
    } catch {
      setError("Failed to save topic");
    }
  };

  const deleteTopic = async (topicId: number) => {
    if (!confirm("Are you sure you want to delete this topic?")) {
      return;
    }
    try {
      await topicService.deleteTopic(topicId);
      fetchTopics();
    } catch {
      setError("Failed to delete topic");
    }
  };

  const onSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const filteredTopics = topics.filter((topic) =>
    topic.code.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading)
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading topics...
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
      <h1 className="text-3xl font-bold mb-6">Topics Management</h1>

      {/* Search Bar */}
      <div className="mb-8 max-w-md mx-auto px-4 py-2 bg-gray-100 rounded-full flex items-center gap-2">
        <input
          type="text"
          placeholder="Enter topic code"
          className="flex-grow bg-gray-200 rounded-full px-4 py-2 focus:outline-none"
          value={searchQuery}
          onChange={onSearchChange}
        />
        <button
          type="button"
          className="bg-green-800 hover:bg-green-900 text-white px-4 py-2 rounded-full flex items-center gap-2"
          onClick={() => { }}
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
        </button>
      </div>

      {/* Grid topic cards */}
      <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
        {filteredTopics.length === 0 && (
          <p className="text-center col-span-full">No topics found.</p>
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
                <span className="text-sm">{`Lecturer: ${topic.teacher_id}`}</span>
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
                <p className="text-gray-700">{topic.description || "No description"}</p>
              </div>
              {/* Footer */}
              <div className="border-t border-gray-200 px-6 py-3 flex justify-end gap-2 bg-white">
                <button
                  className="text-red-600 hover:text-red-800"
                  onClick={() => deleteTopic(topic.id)}
                  aria-label={`Leave or logout ${topic.title}`}
                  title="Leave"
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
                      d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1m0-12v1"
                    />
                  </svg>
                </button>
                <button
                  className="text-green-600 hover:text-green-800"
                  onClick={() => openEditDialog(topic)}
                  aria-label={`View detail for ${topic.title}`}
                  title="View Detail"
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
                      d="M15 10l4.553-2.276A2 2 0 0122 9.618v4.764a2 2 0 01-2.447 1.894L15 14M9 21H6a2 2 0 01-2-2v-3m0-4v-3a2 2 0 012-2h3m3-2h0a4 4 0 014 4v1.5"
                    />
                  </svg>
                </button>
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
            <DialogTitle>{selectedTopic ? "Edit Topic" : "Create Topic"}</DialogTitle>
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
              <input
                id="title"
                {...register("title", { required: true })}
                className="w-full rounded border px-3 py-2"
              />
              {errors.title && (
                <span className="text-red-600">Title is required</span>
              )}
            </div>
            <div>
              <label className="block mb-1 font-semibold" htmlFor="code">
                Code
              </label>
              <input
                id="code"
                {...register("code", { required: true })}
                className="w-full rounded border px-3 py-2"
              />
              {errors.code && (
                <span className="text-red-600">Code is required</span>
              )}
            </div>
            <div>
              <label className="block mb-1 font-semibold" htmlFor="description">
                Description
              </label>
              <textarea
                id="description"
                {...register("description")}
                className="w-full rounded border px-3 py-2"
              />
            </div>
            <div>
              <label className="inline-flex items-center gap-2">
                <input type="checkbox" {...register("public")} />
                Public
              </label>
            </div>

            <DialogFooter>
              <button
                type="submit"
                className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
              >
                Save
              </button>
              <DialogClose asChild>
                <button
                  type="button"
                  className="ml-2 rounded border border-gray-300 px-4 py-2 hover:bg-gray-100"
                >
                  Cancel
                </button>
              </DialogClose>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default TopicsPage;
