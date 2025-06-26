import React, { useState } from "react";
import { QueryClient, QueryClientProvider, useMutation } from "@tanstack/react-query";

const queryClient = new QueryClient();
const API = import.meta.env.VITE_API as string;

type HistoryItem = { question: string; answer: string; mode: string };

function Spinner() {
  return <div className="animate-spin h-5 w-5 border-4 border-t-transparent border-white rounded-full mr-2" />;
}

function App() {
  const [mode, setMode] = useState<"doc" | "web" | "general">("doc");
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error("Please select a .txt file.");
      const fd = new FormData(); fd.append("file", file);
      const res = await fetch(`${API}/upload`, { method: "POST", body: fd });
      if (!res.ok) throw new Error("Upload failed.");
    },
    onError: err => setError((err as Error).message),
    onSuccess: () => {
      setError(null);
      alert("Document indexed successfully!");
    }
  });

  const chatMutation = useMutation({
    mutationFn: async () => {
      if (!question.trim()) throw new Error("Please type a question.");
      setError(null);
      setLoading(true);
      const fd = new FormData();
      fd.append("question", question);
      fd.append("mode", mode);
      const res = await fetch(`${API}/chat`, { method: "POST", body: fd });
      setLoading(false);
      if (!res.ok) {
        const { detail } = await res.json();
        throw new Error(detail || "Chat error.");
      }
      return res.json();
    },
    onError: err => {
      setLoading(false);
      setError((err as Error).message);
    },
    onSuccess: data => {
      const newAnswer = data.answer as string;
      setHistory([...history, { question, answer: newAnswer, mode }]);
      setQuestion("");
    }
  });

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      <header className="bg-indigo-600 p-4 text-white text-2xl text-center">RAG Agent Playground</header>
      <main className="flex-1 overflow-y-auto p-4 space-y-6">
        {error && <div className="text-red-600">⚠️ {error}</div>}
        {history.map((item, idx) => (
          <div key={idx} className="max-w-lg mx-auto flex flex-col space-y-2">
            <div className="self-end text-gray-700">Q: {item.question}</div>
            <div className="self-center bg-indigo-50 p-4 rounded-lg text-left max-w-full">A: {item.answer}</div>
          </div>
        ))}
      </main>
      <footer className="p-4 bg-white shadow-md">
        {mode === "doc" && (
          <div className="flex items-center mb-4">
            <input
              type="file"
              accept=".txt"
              onChange={e => setFile(e.target.files?.[0] ?? null)}
              className="flex-1"
            />
            <button
              onClick={() => uploadMutation.mutate()}
              disabled={!file || uploadMutation.isPending}
              className="ml-2 px-4 py-2 bg-green-500 text-white rounded-full"
            >{uploadMutation.isPending ? 'Uploading...' : 'Upload'}</button>
          </div>
        )}
        <div className="flex space-x-2 items-center">
          {/* Mode selector on left of input */}
          <select
            value={mode}
            onChange={e => setMode(e.target.value as any)}
            className="border border-gray-300 rounded-full px-4 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-400"
          >
            <option value="doc">Document RAG</option>
            <option value="web">Web RAG</option>
            <option value="general">General Chat</option>
          </select>
          {/* Flexible input field */}
          <textarea
            rows={2}
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="Ask a question... Press Enter to send"
            className="flex-1 border border-gray-300 rounded-xl px-4 py-2 resize-y focus:outline-none focus:ring-2 focus:ring-indigo-400"
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); chatMutation.mutate(); } }}
          />
          <button
            onClick={() => chatMutation.mutate()}
            disabled={loading}
            className="inline-flex items-center px-6 py-2 bg-indigo-600 text-white rounded-full transition disabled:opacity-50"
          >{loading ? <Spinner /> : 'Ask'}</button>
        </div>
      </footer>
    </div>
  );
}

export default function Wrapped() {
  return (
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  );
}