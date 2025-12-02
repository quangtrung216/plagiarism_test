'use client';

import { useState, useEffect } from 'react';
import { Topic } from '@/types';
import { TopicFormData } from '@/services/topicService';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogFooter,
  DialogDescription
} from '@/components/ui/dialog';
import { 
  Form, 
  FormControl, 
  FormField, 
  FormItem, 
  FormLabel, 
  FormMessage 
} from '@/components/ui/form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import * as z from 'zod';

const topicFormSchema = z.object({
  title: z.string().min(1, 'Tiêu đề là bắt buộc'),
  code: z.string().optional(),
  description: z.string().optional(),
  public: z.boolean(),
  require_approval: z.boolean(),
  deadline: z.string().optional(),
  max_file_size: z.number().optional(),
  allowed_extensions: z.array(z.string()).optional(),
  max_uploads: z.number().optional(),
  threshold: z.number().optional()
});

interface TopicFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: TopicFormData) => Promise<void>;
  initialData?: Topic | null;
}

export function TopicForm({ open, onOpenChange, onSubmit, initialData }: TopicFormProps) {
  const [loading, setLoading] = useState(false);
  
  const form = useForm<z.infer<typeof topicFormSchema>>({
    resolver: zodResolver(topicFormSchema),
    defaultValues: {
      title: '',
      code: '',
      description: '',
      public: false,
      require_approval: true,
      deadline: '',
      max_file_size: 10485760, // 10MB default
      allowed_extensions: ['pdf', 'doc', 'docx', 'txt'],
      max_uploads: 1,
      threshold: 80 // Convert to percentage for display
    }
  });

  // Reset form when initialData changes or when dialog opens
  useEffect(() => {
    if (open) {
      form.reset({
        title: initialData?.title || '',
        code: initialData?.code || '',
        description: initialData?.description || '',
        public: initialData?.public || false,
        require_approval: initialData?.require_approval !== undefined ? initialData.require_approval : true,
        deadline: initialData?.deadline || '',
        max_file_size: initialData?.max_file_size || 10485760, // 10MB default
        allowed_extensions: initialData?.allowed_extensions || ['pdf', 'doc', 'docx', 'txt'],
        max_uploads: initialData?.max_uploads || 1,
        threshold: initialData?.threshold ? initialData.threshold * 100 : 80 // Convert to percentage for display
      });
    }
  }, [initialData, open, form]);

  const handleSubmit = async (values: z.infer<typeof topicFormSchema>) => {
    setLoading(true);
    try {
      // Remove code field if it's empty for new topics
      const formData: TopicFormData = {
        ...values,
        code: values.code || undefined,
        threshold: values.threshold ? values.threshold / 100 : undefined // Convert back to decimal
      } as TopicFormData;
      
      await onSubmit(formData);
      form.reset();
      onOpenChange(false);
    } catch (error) {
      console.error('Failed to save topic:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px] rounded-lg">
        <DialogHeader>
          <DialogTitle>{initialData ? 'Chỉnh sửa chủ đề' : 'Tạo chủ đề mới'}</DialogTitle>
          <DialogDescription>
            {initialData ? 'Chỉnh sửa thông tin chủ đề bên dưới' : 'Nhập thông tin cho chủ đề mới của bạn'}
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Tiêu đề</FormLabel>
                  <FormControl>
                    <Input placeholder="Nhập tiêu đề chủ đề" {...field} className="rounded-lg" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            {initialData ? (
              <FormField
                control={form.control}
                name="code"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Mã chủ đề</FormLabel>
                    <FormControl>
                      <Input {...field} className="rounded-lg" readOnly />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            ) : null}
            
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Mô tả</FormLabel>
                  <FormControl>
                    <Textarea 
                      placeholder="Nhập mô tả chủ đề" 
                      className="resize-none rounded-lg" 
                      {...field} 
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="max_uploads"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Số lần tải lên tối đa</FormLabel>
                  <FormControl>
                    <Input 
                      type="number" 
                      min="1" 
                      {...field} 
                      value={field.value || ''} 
                      onChange={e => field.onChange(e.target.value ? parseInt(e.target.value) : '')}
                      className="rounded-lg" 
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="threshold"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Ngưỡng kiểm tra đạo văn (%)</FormLabel>
                  <FormControl>
                    <Input 
                      type="number" 
                      min="0" 
                      max="100" 
                      {...field} 
                      value={field.value || ''} 
                      onChange={e => field.onChange(e.target.value ? parseInt(e.target.value) : '')}
                      className="rounded-lg" 
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="public"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">Công khai</FormLabel>
                    <DialogDescription>
                      Cho phép chủ đề này được truy cập công khai
                    </DialogDescription>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="require_approval"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">Yêu cầu phê duyệt</FormLabel>
                    <DialogDescription>
                      Yêu cầu giảng viên phê duyệt trước khi công bố
                    </DialogDescription>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="deadline"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Hạn chót</FormLabel>
                  <FormControl>
                    <Input type="date" {...field} className="rounded-lg" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <DialogFooter>
              <Button 
                type="submit" 
                disabled={loading}
                className="bg-green-700 hover:bg-green-800 rounded-lg"
              >
                {loading ? 'Đang lưu...' : (initialData ? 'Cập nhật' : 'Tạo')}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}