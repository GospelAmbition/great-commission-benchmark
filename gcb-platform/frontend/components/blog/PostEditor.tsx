"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import "@uiw/react-md-editor/markdown-editor.css";
import "@uiw/react-markdown-preview/markdown.css";

// MDEditor uses browser APIs — load client-side only to avoid SSR hydration issues
const MDEditor = dynamic(() => import("@uiw/react-md-editor"), { ssr: false });

interface PostEditorProps {
  value: string;
  onChange: (content: string) => void;
  onImageUpload?: (file: File) => Promise<string>;
}

export function PostEditor({ value, onChange, onImageUpload }: PostEditorProps) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return (
      <div className="h-[500px] border rounded-md flex items-center justify-center bg-muted">
        <p className="text-muted-foreground">Loading editor...</p>
      </div>
    );
  }

  // Build an extra toolbar command for image upload when a handler is provided
  const extraCommands = onImageUpload
    ? [
        {
          name: "upload-image",
          keyCommand: "upload-image",
          buttonProps: { "aria-label": "Upload image", title: "Upload image" },
          icon: (
            <svg viewBox="0 0 16 16" width="12px" height="12px">
              <path
                fill="currentColor"
                d="M14 9a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1v-4a1 1 0 0 1 2 0v3h10v-3a1 1 0 0 1 1-1zM8 1a1 1 0 0 1 .707.293l3 3a1 1 0 0 1-1.414 1.414L9 4.414V9a1 1 0 0 1-2 0V4.414L5.707 5.707A1 1 0 0 1 4.293 4.293l3-3A1 1 0 0 1 8 1z"
              />
            </svg>
          ),
          execute: (_state: unknown, _api: unknown) => {
            const input = document.createElement("input");
            input.type = "file";
            input.accept = "image/*,.svg";
            input.onchange = async () => {
              const file = input.files?.[0];
              if (!file || !onImageUpload) return;
              try {
                const url = await onImageUpload(file);
                const api = _api as { replaceSelection: (text: string) => void };
                api.replaceSelection(`![${file.name}](${url})`);
              } catch {
                // upload failed — do nothing, let the caller surface the error
              }
            };
            input.click();
          },
        },
      ]
    : [];

  return (
    <div data-color-mode="dark">
      <MDEditor
        value={value}
        onChange={(val) => onChange(val ?? "")}
        height={500}
        visibleDragbar={false}
        extraCommands={extraCommands}
      />
    </div>
  );
}
