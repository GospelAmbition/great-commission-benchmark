"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { apiClient } from "@/lib/api";
import Link from "next/link";
import { AlertCircle } from "lucide-react";

interface TesterAgreementModalProps {
  open: boolean;
  onAccept: () => void;
}

export function TesterAgreementModal({ open, onAccept }: TesterAgreementModalProps) {
  const [accepted, setAccepted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAccept() {
    if (!accepted) {
      setError("You must accept the Tester Agreement to continue.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await apiClient.acceptTesterAgreement();
      onAccept();
    } catch (err: any) {
      setError(err.message || "Failed to accept agreement. Please try again.");
      setLoading(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={() => {}}>
      <DialogContent className="max-w-3xl max-h-[85vh] p-0 flex flex-col overflow-hidden [&>button]:hidden">
        <DialogHeader className="px-6 pt-6 pb-4 flex-shrink-0">
          <DialogTitle>Tester Agreement</DialogTitle>
          <DialogDescription>
            Before running benchmark tests, you must accept the Tester Agreement.
          </DialogDescription>
        </DialogHeader>

        <div className="overflow-y-auto px-6 flex-1 min-h-0">
          <div className="space-y-4 prose prose-sm max-w-none">
            <div className="p-4 bg-muted rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Confidentiality Obligations</h3>
              <p className="text-sm text-muted-foreground mb-4">
                The integrity of the Great Commission Benchmark depends on maintaining the 
                confidentiality of test questions. If questions become publicly available or 
                are shared with AI model providers, they may be incorporated into training 
                data, rendering our benchmark ineffective.
              </p>
              
              <h4 className="font-semibold mt-4 mb-2">You agree to:</h4>
              <ul className="list-disc pl-6 space-y-1 text-sm">
                <li><strong>Not share test questions publicly</strong> - Do not post questions online or in forums</li>
                <li><strong>Not share with model providers</strong> - Do not share questions with AI companies</li>
                <li><strong>Not use for training</strong> - Do not use questions to train or fine-tune models</li>
                <li><strong>Report leaks</strong> - Report any suspected breaches of confidentiality</li>
              </ul>

              <h4 className="font-semibold mt-4 mb-2">Consequences of Violation:</h4>
              <ul className="list-disc pl-6 space-y-1 text-sm">
                <li><strong>Minor violations:</strong> Warning and re-confirmation</li>
                <li><strong>Major violations:</strong> Access revocation</li>
                <li><strong>Severe violations:</strong> Permanent ban and possible legal action</li>
              </ul>
            </div>

            <p className="text-sm pb-2">
              By clicking "I Accept", you acknowledge that you have read and understood the{" "}
              <Link href="/tester-agreement" className="text-[--ga-red] hover:underline" target="_blank">
                full Tester Agreement
              </Link>{" "}
              and agree to be bound by all terms and conditions.
            </p>
          </div>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 mx-6 bg-destructive/10 text-destructive rounded-lg flex-shrink-0">
            <AlertCircle className="h-4 w-4" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        <DialogFooter className="flex-col sm:flex-row gap-2 flex-shrink-0 border-t px-6 py-4">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="accept"
              checked={accepted}
              onCheckedChange={(checked) => {
                setAccepted(checked === true);
                setError(null);
              }}
            />
            <label
              htmlFor="accept"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
            >
              I have read and accept the Tester Agreement
            </label>
          </div>
          <Button
            onClick={handleAccept}
            disabled={loading || !accepted}
            variant="destructive"
            className="bg-[--ga-red] hover:bg-[--ga-dark-red] text-white w-full sm:w-auto disabled:bg-[--ga-red]/50 disabled:text-white/70"
          >
            {loading ? "Accepting..." : "I Accept"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
