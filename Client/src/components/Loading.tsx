import React, { useEffect, useState } from "react";

const loadingMessages = [
  "Processing your file...",
  "Extracting content...",
  "Indexing sections...",
  "Analyzing structure...",
  "Preparing context...",
  "Almost ready..."
];

export default function Loading() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % loadingMessages.length);
    }, 1500); // Change message every 1.5s

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center py-12 gap-4">
      {/* Spinner */}
      <div className="w-8 h-8 border-4 border-neutral-800 border-t-neutral-300 rounded-full animate-spin" />

      {/* Message */}
      <p className="text-neutral-300 text-sm font-medium transition-opacity duration-500">
        {loadingMessages[index]}
      </p>
    </div>
  );
}
