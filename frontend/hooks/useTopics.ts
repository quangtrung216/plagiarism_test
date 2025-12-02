'use client';

import { useState, useEffect } from 'react';
import { Topic } from '@/types';
import { getMyTopics, createTopic, updateTopic, deleteTopic, TopicFormData } from '@/services/topicService';
import { useAuthorization } from '@/providers/AuthorizationProvider';

export function useTopics() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuthorization();

  const fetchTopics = async () => {
    try {
      setLoading(true);
      const data = await getMyTopics();
      setTopics(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch topics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const createNewTopic = async (data: TopicFormData) => {
    try {
      const newTopic = await createTopic(data);
      setTopics(prev => [...prev, newTopic]);
      return newTopic;
    } catch (err) {
      setError('Failed to create topic');
      console.error(err);
      throw err;
    }
  };

  const updateExistingTopic = async (id: number, data: TopicFormData) => {
    try {
      const updatedTopic = await updateTopic(id, data);
      setTopics(prev => prev.map(topic => topic.id === id ? updatedTopic : topic));
      return updatedTopic;
    } catch (err) {
      setError('Failed to update topic');
      console.error(err);
      throw err;
    }
  };

  const deleteExistingTopic = async (id: number) => {
    try {
      await deleteTopic(id);
      setTopics(prev => prev.filter(topic => topic.id !== id));
    } catch (err) {
      setError('Failed to delete topic');
      console.error(err);
      throw err;
    }
  };

  useEffect(() => {
    if (user?.role === 'teacher') {
      fetchTopics();
    }
  }, [user]);

  return {
    topics,
    loading,
    error,
    fetchTopics,
    createNewTopic,
    updateExistingTopic,
    deleteExistingTopic
  };
}