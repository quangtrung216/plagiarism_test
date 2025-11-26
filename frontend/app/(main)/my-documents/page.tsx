"use client";

import React, { useEffect, useState, ChangeEvent } from "react";
import documentService from "../../../services/documentService";
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Document } from "@/types";

export default function MyDocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [fileToUpload, setFileToUpload] = useState<File | null>(null);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const data = await documentService.listDocuments();
      setDocuments(data as Document[]);
      setError(null);
    } catch {
      setError("Failed to fetch documents");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const onSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const onSearchSubmit = async () => {
    setLoading(true);
    try {
      const data = await documentService.searchDocuments(searchQuery);
      setDocuments(data as Document[]);
      setError(null);
    } catch {
      setError("Failed to search documents");
    }
    setLoading(false);
  };

  const onFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFileToUpload(e.target.files[0]);
    }
  };

  const onUpload = async () => {
    if (!fileToUpload) return;
    setLoading(true);
    try {
      await documentService.uploadDocument(fileToUpload);
      setFileToUpload(null);
      fetchDocuments();
      setError(null);
    } catch {
      setError("Failed to upload document");
    }
    setLoading(false);
  };

  const onDelete = async (objectName: string) => {
    if (!confirm(`Are you sure you want to delete document ${objectName}?`)) return;
    setLoading(true);
    try {
      await documentService.deleteDocument(objectName);
      fetchDocuments();
      setError(null);
    } catch {
      setError("Failed to delete document");
    }
    setLoading(false);
  };

  if (loading)
    return (
      <div className="min-h-screen flex items-center justify-center">Loading documents...</div>
    );
  if (error)
    return (
      <div className="min-h-screen flex items-center justify-center text-red-600">{error}</div>
    );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Tài liệu của tôi</h1>
        <p className="text-muted-foreground">Quản lý tài liệu đã tải lên</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Danh sách Tài liệu</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-8 max-w-md mx-auto px-4 py-2 bg-gray-100 rounded-full flex items-center gap-2">
            <input
              type="text"
              placeholder="Enter document name"
              className="flex-grow bg-gray-200 rounded-full px-4 py-2 focus:outline-none"
              value={searchQuery}
              onChange={onSearchChange}
            />
            <button
              type="button"
              className="bg-green-800 hover:bg-green-900 text-white px-4 py-2 rounded-full flex items-center gap-2"
              onClick={onSearchSubmit}
              aria-label="Search"
            >
              Search
            </button>
          </div>

          <div className="mb-8 max-w-md mx-auto px-4 py-2 flex items-center gap-2">
            <input type="file" onChange={onFileChange} />
            <button
              type="button"
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
              onClick={onUpload}
              disabled={!fileToUpload}
            >
              Upload
            </button>
          </div>

          <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
            {documents.length === 0 && (
              <p className="text-center col-span-full">No documents found.</p>
            )}
            {documents.map((doc) => (
              <div key={doc.object_name} className="relative rounded-xl shadow-md overflow-hidden flex flex-col h-48 p-4">
                <div className="flex flex-col justify-center">
                  <h2 className="font-bold text-lg truncate">{doc.object_name}</h2>
                  <p className="text-sm text-gray-500">{doc.content_type || "Unknown type"}</p>
                  <p className="text-sm text-gray-600">Size: {doc.size} bytes</p>
                  <p className="text-xs text-gray-400">Last Modified: {new Date(doc.last_modified).toLocaleString()}</p>
                </div>
                <div className="mt-auto flex justify-end gap-2">
                  <button
                    className="text-red-600 hover:text-red-800"
                    onClick={() => onDelete(doc.object_name)}
                    aria-label={`Delete document ${doc.object_name}`}
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
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
