'use client';

import { useState, useEffect } from 'react';
import { TopicMember } from '@/types';
import { getTopicStudents, updateTopicMemberStatus } from '@/services/topicService';

export function useTopicMembers(topicId: number | null) {
  const [members, setMembers] = useState<TopicMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMembers = async () => {
    if (!topicId) return;
    
    try {
      setLoading(true);
      const data = await getTopicStudents(topicId);
      console.log(data);
      setMembers(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch topic members');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const updateMemberStatus = async (memberId: number, status: 'accepted' | 'rejected', note?: string) => {
    if (!topicId) return;
    
    try {
      const updatedMember = await updateTopicMemberStatus(topicId, memberId, status, note);
      setMembers(prev => prev.map(member => member.id === memberId ? updatedMember : member));
      return updatedMember;
    } catch (err) {
      setError('Failed to update member status');
      console.error(err);
      throw err;
    }
  };

  useEffect(() => {
    fetchMembers();
  }, [topicId,fetchMembers]);

  return {
    members,
    loading,
    error,
    fetchMembers,
    updateMemberStatus
  };
}