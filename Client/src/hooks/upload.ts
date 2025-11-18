import { useMutation } from "@tanstack/react-query";
import axios from "axios";

// ------------------ Upload PDF ------------------
const useUploadFile = () => {
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);

      const res = await axios.post(
        "http://localhost:8000/upload",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      return res.data;
    },
    onSuccess: () => {
      console.log("PDF uploaded successfully.");
    },
    onError: (error: any) => {
      console.error(error.response?.data || error.message);
    },
  });
};

const usePostQuery = () => {
  return useMutation({
    mutationFn: async ({question, fileId}: {question: string, fileId: string}) => {
      const res = await axios.post(
        "http://localhost:8000/query",
        {  file_id: fileId, question },
        { headers: { "Content-Type": "application/json" } }
      );
      return res.data;
    },
    onSuccess: () => {
      console.log("Query posted successfully.");
    },
    onError: (error: any) => {
      console.error(error.response?.data || error.message);
    },
  });
};

export { useUploadFile, usePostQuery };
