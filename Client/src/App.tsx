// PaperBrainApp.tsx
import React, { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, Send, FileText } from "lucide-react";
import { useUploadFile, usePostQuery } from "./hooks/upload"; // your hooks

type Message = { role: "user" | "assistant"; content: string; id?: string };

export default function PaperBrainApp() {
  // mutations (assumed provided by your project)
  const uploadMutation = useUploadFile();
  const queryMutation = usePostQuery();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileId, setFileId] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Welcome — upload a file to get started!" },
  ]);
  const [question, setQuestion] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const chatRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  // placeholder branding / mascot (change later)
  const BRAND_NAME = "PaperBrain";
  const MASCOT = "🧠📄"; // <-- Replace this emoji later as you like

  // scroll chat to bottom when messages change
  useEffect(() => {
    chatRef.current?.scrollTo({
      top: chatRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  // file select handler
  const handleFileSelect = (file?: File) => {
    if (!file) return;
    // accept pdf/docx/txt
    const allowed = [
      "application/pdf",
      "text/plain",
      "application/msword",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];
    if (!allowed.includes(file.type)) {
      alert("Please upload PDF, DOCX or TXT file.");
      return;
    }
    setSelectedFile(file);
  };

  // drag handlers
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) handleFileSelect(f);
  };

  // upload action
  const handleUpload = () => {
    if (!selectedFile) return;
    uploadMutation.mutate(selectedFile, {
      onSuccess: (res) => {
        // store returned file id for queries
        if (res?.file_id) setFileId(res.file_id);
        // fun success message + confetti is optional client-side; keep simple here
        setMessages((m) => [
          ...m,
          {
            role: "assistant",
            content: `Uploaded: <b>${selectedFile.name}</b>. Ask anything about it.`,
          },
        ]);
        setSelectedFile(null);
      },
      onError: () => {
        alert("Upload failed. Try again.");
      },
    });
  };

  // send question
  const handleSend = () => {
    if (!question.trim()) return;
    const q = question.trim();
    setMessages((m) => [...m, { role: "user", content: q }]);
    setQuestion("");

    // show thinking bubble
    const typingMessageId = `t_${Date.now()}`;
    setMessages((m) => [
      ...m,
      { role: "assistant", content: "Thinking...", id: typingMessageId },
    ]);

    queryMutation.mutate(
      { question: q, fileId },
      {
        onSuccess: (res) => {
          // remove typing and append real answer
          setMessages((prev) =>
            prev.filter((msg) => msg.id !== typingMessageId)
          );
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: res?.answer || "Couldn't find an answer in the file.",
            },
          ]);
        },
        onError: () => {
          setMessages((prev) =>
            prev.filter((msg) => msg.id !== typingMessageId)
          );
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: "Error while querying. Please try again.",
            },
          ]);
        },
      }
    );
  };

  // Enter to send
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // quick suggestion chips
  const suggestions = [
    "Summarize this document",
    "List key takeaways",
    "Find dates and deadlines",
    "Extract contact info",
  ];

  return (
    <div className="min-h-screen bg-[#fff7ec] flex items-start justify-center p-6">
      {/* Canvas background accent */}
      <div className="absolute inset-0 pointer-events-none"></div>

      <div className="w-full max-w-4xl">
        {/* Header / Branding */}
        <div className="flex flex-col items-center gap-3 mb-6">
          <div className="inline-flex items-center gap-3 bg-yellow-300 rounded-full px-5 py-3 border-2 border-black shadow-[6px_6px_0_0_rgba(0,0,0,1)]">
            <div className="text-3xl">{MASCOT}</div>
            <div className="text-2xl font-extrabold tracking-wide">
              {BRAND_NAME}
            </div>
          </div>

          <h2 className="text-center text-2xl font-semibold text-[#1f2937]">
            Upload your PDF & Ask Anything Instantly
          </h2>
          <p className="text-center text-sm text-[#374151]">
            AI-powered PDF Q&A • Summaries • Smart search
          </p>
        </div>

        {/* Upload card + Chat area */}
        <div className="bg-transparent">
          {/* Upload Section */}
          <div
            onDragEnter={() => setIsDragging(true)}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={`relative rounded-3xl p-10 mb-8 transition-transform ${
              isDragging ? "scale-[1.01]" : ""
            }`}
          >
            <div
              className="w-full bg-white rounded-3xl p-10 flex flex-col items-center gap-6
               border-4 border-dashed border-black shadow-[10px_10px_0_#000000]"
            >
              {/* Hidden File Input */}
              <input
                id="fileInput"
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                className="hidden"
                onChange={(e) => handleFileSelect(e.target.files?.[0])}
              />

              {/* CLICKABLE UPLOAD ICON */}
              <div
                onClick={() => document.getElementById("fileInput")?.click()}
                className="w-32 h-32 bg-yellow-300 rounded-full border-4 border-black shadow-[6px_6px_0_#000] 
                 flex items-center justify-center cursor-pointer hover:scale-105 transition"
              >
                <Upload size={48} className="text-black" />
              </div>

              {/* Title */}
              <h2 className="text-2xl font-bold text-center text-black">
                Upload Your File
              </h2>
              <p className="text-center text-gray-600 text-sm">
                PDF, DOCX, TXT
              </p>

              {/* FILE PREVIEW (LIGHT GREEN BOX) */}
              {selectedFile && (
                <div
                  className="w-full bg-green-100 border border-black/20 rounded-2xl px-5 py-3 
                      flex items-center gap-3 shadow-sm"
                >
                  <FileText size={20} className="text-black" />
                  <span className="font-medium text-black">
                    {selectedFile.name}
                  </span>
                </div>
              )}
            </div>
            {/* Upload Button */}
            <button
              onClick={handleUpload}
              disabled={!selectedFile || uploadMutation.isPending}
              className={`flex mx-auto mt-4 px-6 py-3 rounded-2xl text-lg font-bold border-2 border-black 
                  shadow-[6px_6px_0_#000] transition
                  ${
                    uploadMutation.isPending || !selectedFile
                      ? "bg-gray-300 cursor-not-allowed"
                      : "bg-yellow-300 hover:brightness-105"
                  }`}
            >
              {uploadMutation.isPending ? "Uploading..." : "Start Chating"}
            </button>
          </div>

          {/* CHAT SECTION — Cartoon Bubble Style */}
          <div className="rounded-2xl p-5 bg-[#fffefa] border border-black/10 shadow-[6px_6px_0_rgba(0,0,0,0.15)]">
            <div
              ref={chatRef}
              className="max-h-[55vh] overflow-y-auto p-4 space-y-5"
            >
              <AnimatePresence>
                {messages.map((msg, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ duration: 0.25 }}
                    className={`flex w-full ${
                      msg.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`px-4 py-3 max-w-[78%] leading-relaxed rounded-3xl shadow-md border ${
                        msg.role === "user"
                          ? "bg-yellow-300 border-black/20 text-black shadow-[4px_4px_0_rgba(0,0,0,0.35)]"
                          : "bg-white border-black/10 text-gray-900 shadow-[4px_4px_0_rgba(0,0,0,0.2)]"
                      }`}
                      style={{ borderRadius: "20px 20px 20px 20px" }}
                      dangerouslySetInnerHTML={{ __html: msg.content }}
                    ></div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* Typing bubble */}
              {queryMutation.isPending && (
                <div className="flex items-center gap-2">
                  <div className="bg-white border border-black/10 px-4 py-3 rounded-3xl shadow">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-150"></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-300"></div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="mt-4 flex items-center gap-3">
              <input
                ref={inputRef}
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask your question…"
                className="flex-1 px-4 py-3 rounded-full border border-black/20 bg-white shadow-[4px_4px_0_rgba(0,0,0,0.15)] focus:ring-2 focus:ring-yellow-300 outline-none"
              />

              <button
                onClick={handleSend}
                className="px-4 py-3 rounded-full bg-yellow-300 border border-black shadow-[4px_4px_0_rgba(0,0,0,0.4)] hover:brightness-105"
              >
                <Send size={18} className="text-black" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
