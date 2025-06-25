import { useState } from "react";

export default function App() {
  // ── Local UI state ───────────────────────────────────────────
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // ── Upload & index handler ──────────────────────────────────
  const sendFile = async () => {
    if (!file) return alert("Select a file first!");
    setLoading(true);
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch(`${import.meta.env.VITE_API}/upload`, {
        method: "POST",
        body: form,
      });
      if (!res.ok) throw new Error(await res.text());
      alert("✅ Document indexed");
    } catch (e: any) {
      alert("Upload error: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  // ── Ask question handler ─────────────────────────────────────
  const ask = async () => {
    if (!question.trim()) return alert("Type a question!");
    setLoading(true);
    const form = new FormData();
    form.append("question", question);
    try {
      const res = await fetch(`${import.meta.env.VITE_API}/chat`, {
        method: "POST",
        body: form,
      });
      if (!res.ok) throw new Error(await res.text());
      const { answer } = await res.json();
      setAnswer(answer);
    } catch (e: any) {
      alert("Chat error: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="p-6 max-w-lg mx-auto space-y-6">
      <h1 className="text-3xl font-bold">Simple RAG Agent</h1>

      {/* File picker */}
      <div className="flex items-center space-x-2">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="border p-2 rounded"
        />
        <button
          onClick={sendFile}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
        >
          {loading ? "Working…" : "Upload & Index"}
        </button>
      </div>

      {/* Question input */}
      <div className="space-y-2">
        <textarea
          rows={3}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about the uploaded document…"
          className="w-full border p-2 rounded"
        />
        <button
          onClick={ask}
          disabled={loading}
          className="px-4 py-2 bg-green-600 text-white rounded disabled:opacity-50"
        >
          {loading ? "Waiting…" : "Ask"}
        </button>
      </div>

      {/* Answer display */}
      {answer && (
        <div className="border p-4 bg-gray-50 rounded whitespace-pre-wrap">
          <h2 className="font-semibold mb-2">Answer:</h2>
          <p>{answer}</p>
        </div>
      )}
    </main>
  );
}
