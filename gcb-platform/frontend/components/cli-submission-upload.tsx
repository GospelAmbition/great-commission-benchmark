"use client";

import { useState, useRef } from "react";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert } from "@/components/ui/alert";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";
import { Upload, FileText, X } from "lucide-react";

interface CliSubmissionUploadProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function CliSubmissionUpload({ open, onOpenChange, onSuccess }: CliSubmissionUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [jsonText, setJsonText] = useState("");
  const [uploadMode, setUploadMode] = useState<"file" | "paste">("file");
  const [loading, setLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [preview, setPreview] = useState<{
    model: string;
    version: string;
    score: number;
  } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    if (!selectedFile.name.endsWith(".json")) {
      toast.error("Please select a JSON file");
      return;
    }

    setFile(selectedFile);
    setValidationErrors([]);
    setPreview(null);

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const content = event.target?.result as string;
        const data = JSON.parse(content);
        validateAndPreview(data);
      } catch (error) {
        toast.error("Invalid JSON file");
        setFile(null);
      }
    };
    reader.readAsText(selectedFile);
  };

  const handlePasteChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value;
    setJsonText(text);
    setValidationErrors([]);
    setPreview(null);

    if (text.trim()) {
      try {
        const data = JSON.parse(text);
        validateAndPreview(data);
      } catch (error) {
        // Invalid JSON, but don't show error until submit
      }
    }
  };

  const validateAndPreview = (data: any) => {
    const errors: string[] = [];

    // Basic structure validation
    if (!data.format_version) {
      errors.push("Missing format_version field");
    }
    if (!data.test_run) {
      errors.push("Missing test_run field");
    }
    if (!data.summary) {
      errors.push("Missing summary field");
    }
    if (!data.responses) {
      errors.push("Missing responses field");
    }
    if (!data.metadata) {
      errors.push("Missing metadata field");
    }

    if (errors.length > 0) {
      setValidationErrors(errors);
      setPreview(null);
      return;
    }

    // Extract preview info
    const testRun = data.test_run || {};
    const summary = data.summary || {};
    const model = testRun.model || "Unknown";
    const version = testRun.benchmark_version || "Unknown";
    const score = summary.score || 0;

    setPreview({ model, version, score });
    setValidationErrors([]);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setValidationErrors([]);

    try {
      let exportData: any;

      if (uploadMode === "file" && file) {
        const text = await file.text();
        exportData = JSON.parse(text);
      } else if (uploadMode === "paste" && jsonText.trim()) {
        exportData = JSON.parse(jsonText);
      } else {
        toast.error("Please provide a file or paste JSON data");
        setLoading(false);
        return;
      }

      // Final validation
      validateAndPreview(exportData);
      if (validationErrors.length > 0) {
        toast.error("Please fix validation errors before submitting");
        setLoading(false);
        return;
      }

      // Submit to API
      const response = await apiClient.uploadCliSubmission(exportData);

      if (response.validation_errors && response.validation_errors.length > 0) {
        setValidationErrors(response.validation_errors);
        toast.error("Validation failed. Please check the errors.");
        setLoading(false);
        return;
      }

      // Success
      toast.success(response.message || "Submission uploaded successfully");

      if (response.payment_required && response.payment_intent_id) {
        toast.info("Payment required to complete submission");
        // TODO: Navigate to payment page if needed
      }

      // Reset form
      setFile(null);
      setJsonText("");
      setPreview(null);
      setValidationErrors([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      onOpenChange(false);
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      const errorMessage = error.message || "Failed to upload submission";
      toast.error(errorMessage);
      if (error.response?.data?.validation_errors) {
        setValidationErrors(error.response.data.validation_errors);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setFile(null);
      setJsonText("");
      setPreview(null);
      setValidationErrors([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Upload GCB Runner Test Results</DialogTitle>
          <DialogDescription>
            Upload test results exported from gcb-runner. Export your results using{" "}
            <code className="text-xs bg-muted px-1 py-0.5 rounded">gcb-runner export --run N</code>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Upload mode toggle */}
          <div className="flex gap-2">
            <Button
              type="button"
              variant={uploadMode === "file" ? "default" : "outline"}
              size="sm"
              onClick={() => setUploadMode("file")}
              className="flex-1"
            >
              <Upload className="mr-2 h-4 w-4" />
              Upload File
            </Button>
            <Button
              type="button"
              variant={uploadMode === "paste" ? "default" : "outline"}
              size="sm"
              onClick={() => setUploadMode("paste")}
              className="flex-1"
            >
              <FileText className="mr-2 h-4 w-4" />
              Paste JSON
            </Button>
          </div>

          {/* File upload */}
          {uploadMode === "file" && (
            <div className="space-y-2">
              <Label htmlFor="file-upload">Select JSON file</Label>
              <Input
                id="file-upload"
                type="file"
                accept=".json"
                ref={fileInputRef}
                onChange={handleFileSelect}
                disabled={loading}
              />
              {file && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <FileText className="h-4 w-4" />
                  <span>{file.name}</span>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setFile(null);
                      setPreview(null);
                      if (fileInputRef.current) {
                        fileInputRef.current.value = "";
                      }
                    }}
                    className="h-6 w-6 p-0"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </div>
          )}

          {/* JSON paste */}
          {uploadMode === "paste" && (
            <div className="space-y-2">
              <Label htmlFor="json-paste">Paste JSON export</Label>
              <textarea
                id="json-paste"
                className="flex min-h-[200px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 font-mono"
                value={jsonText}
                onChange={handlePasteChange}
                disabled={loading}
                placeholder='{"format_version": "1.0", "test_run": {...}, ...}'
              />
            </div>
          )}

          {/* Preview */}
          {preview && (
            <div className="rounded-lg border bg-muted/50 p-4 space-y-2">
              <h4 className="text-sm font-semibold">Preview</h4>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <div className="text-muted-foreground">Model</div>
                  <div className="font-medium">{preview.model}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">Version</div>
                  <div className="font-medium">{preview.version}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">Score</div>
                  <div className="font-medium">{preview.score.toFixed(1)}</div>
                </div>
              </div>
            </div>
          )}

          {/* Validation errors */}
          {validationErrors.length > 0 && (
            <Alert variant="destructive">
              <div className="space-y-1">
                <div className="font-semibold">Validation Errors:</div>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  {validationErrors.map((error, idx) => (
                    <li key={idx}>{error}</li>
                  ))}
                </ul>
              </div>
            </Alert>
          )}
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button type="button" onClick={handleSubmit} disabled={loading || (!file && !jsonText.trim())}>
            {loading ? "Uploading..." : "Upload"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
