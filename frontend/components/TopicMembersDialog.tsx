'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useTopicMembers } from '@/hooks/useTopicMembers';
import { Check, X, Loader2 } from 'lucide-react';

interface TopicMembersDialogProps {
  topicId: number | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function TopicMembersDialog({ topicId, open, onOpenChange }: TopicMembersDialogProps) {
  const { members, loading, error, updateMemberStatus } = useTopicMembers(topicId);
  const [processingMember, setProcessingMember] = useState<number | null>(null);

  const handleUpdateStatus = async (memberId: number, status: 'accepted' | 'rejected') => {
    try {
      setProcessingMember(memberId);
      await updateMemberStatus(memberId, status);
    } finally {
      setProcessingMember(null);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge variant="secondary">Chờ duyệt</Badge>;
      case 'accepted':
        return <Badge variant="default">Đã chấp nhận</Badge>;
      case 'rejected':
        return <Badge variant="destructive">Đã từ chối</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Quản lý sinh viên</DialogTitle>
        </DialogHeader>
        
        {loading ? (
          <div className="flex justify-center items-center py-8">
            <Loader2 className="h-6 w-6 animate-spin" />
          </div>
        ) : error ? (
          <div className="text-red-500 py-4">{error}</div>
        ) : (
          <div className="space-y-4">
            {members.length === 0 ? (
              <p className="text-center py-4 text-muted-foreground">Không tìm thấy sinh viên nào.</p>
            ) : (
              <div className="space-y-3">
                {members.map((member) => (
                  <div key={member.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="font-medium">
                        {member.student?.full_name || member.student?.username || 'Unknown'}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {member.student?.email || 'No email'}
                      </div>
                      <div className="text-sm">
                        {member.student?.student_profile 
                          ? `${member.student.student_profile.student_id || 'No ID'} - ${member.student.student_profile.major || 'No major'}`
                          : 'No profile data'
                        }
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {getStatusBadge(member.status)}
                      
                      {member.status === 'pending' && (
                        <div className="flex gap-1">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleUpdateStatus(member.id, 'accepted')}
                            disabled={processingMember === member.id}
                          >
                            {processingMember === member.id ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <Check className="h-4 w-4" />
                            )}
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleUpdateStatus(member.id, 'rejected')}
                            disabled={processingMember === member.id}
                          >
                            {processingMember === member.id ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <X className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}