import React, { useState, useRef, useEffect } from "react";
import { Send, Bot, User, CheckCircle, File } from "lucide-react";
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
          console.log("Received response:", data);
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
        onError: () => {
          setIsBotTyping(false);
        },
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
    <div className="min-h-screen bg-neutral-950 flex items-center justify-center">
      <div className="w-full max-w-4xl h-[calc(100vh-2rem)]">
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg shadow-xl flex flex-col h-full">
          {/* Chat Header */}
          <div className="flex items-center place-content-between border-b border-neutral-800 p-6">
            <div>
              <h2 className="text-2xl font-semibold text-neutral-50">
                Chat Assistant
              </h2>
              <p className="text-neutral-400 text-sm mt-1">Ask me anything</p>
            </div>

            {file?.uploaded && (
              <div className="flex items-center gap-3  ">
                <div className="">
                  {file.uploaded ? (
                    <CheckCircle className="text-green-500" size={24} />
                  ) : (
                    <File className="text-neutral-400" size={24} />
                  )}
                </div>
                <div className="flex-1">
                  <p className="text-neutral-50 font-medium truncate">
                    {file.name}
                  </p>
                  <p className="text-neutral-400 text-sm">{file.size}</p>
                </div>
              </div>
            )}
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-track]:bg-neutral-900 [&::-webkit-scrollbar-track]:rounded-full [&::-webkit-scrollbar-thumb]:bg-neutral-700 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb:hover]:bg-neutral-600 dark:[&::-webkit-scrollbar-track]:bg-neutral-900 dark:[&::-webkit-scrollbar-thumb]:bg-neutral-700 dark:[&::-webkit-scrollbar-thumb:hover]:bg-neutral-600">
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
                  className={`flex gap-3 ${
                    message.sender === "user" ? "flex-row-reverse" : ""
                  }`}
                >
                  {/* Avatar */}
                  <div
                    className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      message.sender === "user"
                        ? "bg-neutral-50"
                        : "bg-neutral-700"
                    }`}
                  >
                    {message.sender === "user" ? (
                      <User className="text-neutral-950" size={18} />
                    ) : (
                      <Bot className="text-neutral-50" size={18} />
                    )}
                  </div>

                  {/* Bubble */}
                  <div
                    className={`flex-1 max-w-[70%] ${
                      message.sender === "user" ? "items-end" : ""
                    }`}
                  >
                    <div
                      className={`rounded-lg p-3 ${
                        message.sender === "user"
                          ? "bg-neutral-50 text-neutral-950"
                          : "bg-neutral-800 text-neutral-50"
                      }`}
                    >
                      <p className="text-sm leading-relaxed">{message.text}</p>
                    </div>
                    <p className="text-xs text-neutral-500 mt-1 px-1">
                      {message.timestamp}
                    </p>
                  </div>
                </div>
              ))
            )}

            {isBotTyping && (
              <div className="flex gap-3">
                {/* Bot avatar */}
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-neutral-700 flex items-center justify-center">
                  <Bot className="text-neutral-50" size={18} />
                </div>

                {/* Typing dots */}
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
          <div className="border-t border-neutral-800 p-6">
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
        </div>
      </div>
    </div>
  );
}
