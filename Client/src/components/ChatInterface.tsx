import React, { useState, useRef, useEffect } from "react";
import { Send, Bot, User, CheckCircle, File, Menu } from "lucide-react";
import type { FileObjectType } from "@/types/fileType";
import { usePostQuery } from "@/hooks/useUpload";

interface ChatMessage {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: string;
}

export default function ChatInterface({ file }: { file: FileObjectType }) {
  const queryMutation = usePostQuery();

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState<string>("");
  const [isBotTyping, setIsBotTyping] = useState<boolean>(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      text: inputMessage,
      sender: "user",
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsBotTyping(true);

    queryMutation.mutate(
      { question: inputMessage, fileId: file?.id },
      {
        onSuccess: (data) => {
          setIsBotTyping(false);
          const botMessage: ChatMessage = {
            id: crypto.randomUUID(),
            text: data.answer,
            sender: "bot",
            timestamp: new Date().toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            }),
          };
          setMessages((prev) => [...prev, botMessage]);
        },
        onError: () => setIsBotTyping(false),
      }
    );
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen flex bg-neutral-950 text-neutral-50">
      {/* Sidebar */}
      <aside
        className={`$ {
          isSidebarOpen ? "w-64" : "w-16"
        } bg-neutral-900 border-r border-neutral-800 transition-all duration-300 flex flex-col`}
      >
        <div className="flex items-center justify-between p-4 border-b border-neutral-800">
          <h2 className="text-xl font-bold">{isSidebarOpen && "PDF Chat"}</h2>
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="text-neutral-400 hover:text-neutral-200"
          >
            <Menu size={20} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-2 text-sm">
          <button className="w-full text-left px-3 py-2 rounded bg-neutral-800 hover:bg-neutral-700 transition">New Chat</button>
          <button className="w-full text-left px-3 py-2 rounded bg-neutral-800 hover:bg-neutral-700 transition">History 1</button>
          <button className="w-full text-left px-3 py-2 rounded bg-neutral-800 hover:bg-neutral-700 transition">History 2</button>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col h-screen">
        {/* Header */}
        <div className="border-b border-neutral-800 p-4 flex items-center justify-between bg-neutral-900">
          <div>
            <h2 className="text-xl font-semibold">Chat Assistant</h2>
            <p className="text-sm text-neutral-400">Ask me anything</p>
          </div>
          {file?.uploaded && (
            <div className="flex items-center gap-3">
              {file.uploaded ? (
                <CheckCircle className="text-green-500" size={20} />
              ) : (
                <File className="text-neutral-400" size={20} />
              )}
              <div className="flex flex-col">
                <p className="text-sm font-medium truncate">{file.name}</p>
                <p className="text-xs text-neutral-400">{file.size}</p>
              </div>
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-track]:bg-neutral-900 [&::-webkit-scrollbar-thumb]:bg-neutral-700 [&::-webkit-scrollbar-thumb:hover]:bg-neutral-600">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Bot className="mx-auto mb-4 text-neutral-600" size={48} />
                <p className="text-neutral-400">Start a conversation...</p>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.sender === "user" ? "flex-row-reverse" : ""}`}
              >
                <div
                  className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${message.sender === "user" ? "bg-neutral-50" : "bg-neutral-700"}`}
                >
                  {message.sender === "user" ? (
                    <User className="text-neutral-950" size={18} />
                  ) : (
                    <Bot className="text-neutral-50" size={18} />
                  )}
                </div>
                <div className="flex-1 max-w-[70%]">
                  <div
                    className={`rounded-lg p-3 ${message.sender === "user" ? "bg-neutral-50 text-neutral-950" : "bg-neutral-800 text-neutral-50"}`}
                  >
                    <p className="text-sm leading-relaxed">{message.text}</p>
                  </div>
                  <p className="text-xs text-neutral-500 mt-1 px-1">{message.timestamp}</p>
                </div>
              </div>
            ))
          )}

          {/* Typing indicator */}
          {isBotTyping && (
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-neutral-700 flex items-center justify-center">
                <Bot className="text-neutral-50" size={18} />
              </div>
              <div className="flex items-center gap-2 bg-neutral-800 text-neutral-50 w-fit px-4 py-2 rounded-lg">
                <span className="w-2 h-2 rounded-full bg-neutral-500 animate-bounce"></span>
                <span className="w-2 h-2 rounded-full bg-neutral-500 animate-bounce delay-150"></span>
                <span className="w-2 h-2 rounded-full bg-neutral-500 animate-bounce delay-300"></span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-neutral-800 p-4 bg-neutral-900">
          <div className="flex gap-3">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type your message..."
              className="flex-1 bg-neutral-800 border border-neutral-700 text-neutral-50 placeholder-neutral-500 rounded-lg px-4 py-3 focus:outline-none focus:border-neutral-600 transition-colors"
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim()}
              className={`px-6 py-3 rounded-lg font-semibold transition-colors duration-200 ${
                inputMessage.trim()
                  ? "bg-neutral-50 hover:bg-neutral-200 text-neutral-950"
                  : "bg-neutral-700 text-neutral-500 cursor-not-allowed"
              }`}
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}