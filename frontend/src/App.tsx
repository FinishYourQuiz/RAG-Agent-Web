import { useState } from "react";

export default function App() {
  const [file, setFile] = useState<File>();
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState("");

  const sendFile = async () => {
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file);
    await fetch(import.meta.env.VITE_API + "/upload", { method: "POST", body: fd });
    alert("Indexed!");
  };

  const ask = async () => {
    const fd = new FormData();
    fd.append("question", q);
    const res = await fetch(import.meta.env.VITE_API + "/chat", { method: "POST", body: fd });
    const data = await res.json();
    setAnswer(data.answer);
  };

  return (
    <main className="p-4 max-w-xl mx-auto space-y-4">
      <h1 className="text-2xl font-bold">My RAG Agent</h1>

      <input type="file" onChange={e => setFile(e.target.files?.[0])} />
      <button onClick={sendFile}>Upload &amp; Index</button>

      <textarea className="w-full border p-2" value={q} onChange={e => setQ(e.target.value)} />
      <button onClick={ask}>Ask</button>

      {answer && (
        <div className="mt-4 border p-4 rounded bg-gray-50 whitespace-pre-wrap">
          {answer}
        </div>
      )}
    </main>
  );
}
