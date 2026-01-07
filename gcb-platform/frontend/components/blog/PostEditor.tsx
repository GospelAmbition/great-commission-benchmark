"use client";

import { useRef, useState, useEffect } from "react";
import { Editor } from "@tinymce/tinymce-react";

interface PostEditorProps {
  value: string;
  onChange: (content: string) => void;
  onImageUpload?: (file: File) => Promise<string>;
}

export function PostEditor({ value, onChange, onImageUpload }: PostEditorProps) {
  const editorRef = useRef<any>(null);
  const [isMounted, setIsMounted] = useState(false);

  const apiKey = process.env.NEXT_PUBLIC_TINYMCE_API_KEY;

  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Custom image upload handler
  const handleImageUpload = async (
    blobInfo: any,
    progress: (percent: number) => void
  ): Promise<string> => {
    if (onImageUpload) {
      const file = blobInfo.blob();
      progress(50);
      const url = await onImageUpload(file);
      progress(100);
      return url;
    }
    throw new Error("Image upload handler not provided");
  };

  return (
    <Editor
      apiKey={apiKey}
      onInit={(evt, editor) => {
        editorRef.current = editor;
      }}
      value={value}
      onEditorChange={(content) => onChange(content)}
      init={{
        height: 500,
        menubar: true,
        plugins: [
          "advlist",
          "autolink",
          "lists",
          "link",
          "image",
          "charmap",
          "preview",
          "anchor",
          "searchreplace",
          "visualblocks",
          "code",
          "fullscreen",
          "insertdatetime",
          "media",
          "table",
          "help",
          "wordcount",
        ],
        toolbar:
          "undo redo | blocks | " +
          "bold italic forecolor | alignleft aligncenter " +
          "alignright alignjustify | bullist numlist outdent indent | " +
          "link image | removeformat | code fullscreen | help",
        content_style: `
          body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            font-size: 16px;
            line-height: 1.6;
            max-width: 100%;
            padding: 1rem;
          }
          img { max-width: 100%; height: auto; }
          h1, h2, h3, h4, h5, h6 { margin-top: 1.5em; margin-bottom: 0.5em; }
          p { margin-bottom: 1em; }
          blockquote { 
            border-left: 4px solid #dc2626; 
            padding-left: 1rem; 
            margin-left: 0;
            font-style: italic;
          }
          pre { 
            background: #f4f4f5; 
            padding: 1rem; 
            border-radius: 0.5rem;
            overflow-x: auto;
          }
          code { 
            background: #f4f4f5; 
            padding: 0.125rem 0.25rem; 
            border-radius: 0.25rem;
          }
        `,
        images_upload_handler: onImageUpload ? handleImageUpload : undefined,
        automatic_uploads: !!onImageUpload,
        file_picker_types: "image",
        image_advtab: true,
        image_caption: true,
        link_default_target: "_blank",
        link_assume_external_targets: true,
        paste_data_images: true,
        // Dark mode support
        skin: typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches 
          ? "oxide-dark" 
          : "oxide",
        content_css: typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches 
          ? "dark" 
          : "default",
      }}
    />
  );
}

