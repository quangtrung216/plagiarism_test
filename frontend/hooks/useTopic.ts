'use client';

import { useState, useEffect } from 'react';
import { Topic } from '@/types';
import { getTopicById } from '@/services/topicService';
import { useAuthorization } from '@/providers/AuthorizationProvider';

export function useTopic(id: number) {
  const [topic, setTopic] = useState<Topic | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuthorization();

  const fetchTopic = async () => {
    try {
      setLoading(true);
      const data = await getTopicById(id);
      setTopic(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch topic');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id && user) {
      fetchTopic();
    }
}, [id, user]);

  return {
    topic,
    loading,
    error,
    fetchTopic
  };
}