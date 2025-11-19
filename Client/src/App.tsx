import { useState } from "react";
import ChatInterface from "./components/ChatInterface";
import FileUpload from "./components/FileForm";
import type { FileObjectType } from "./types/fileType";

export default function App() {
  const [file, setFile] = useState<FileObjectType | null>(null);

  return (
    <>
      {!file?.uploaded ? (
        <FileUpload file={file} setFile={setFile} />
      ) : (
        <ChatInterface file={file} />
      )}
    </>
  );
}
