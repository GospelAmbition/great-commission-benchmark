"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiClient } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";

export default function PaymentPage() {
  const params = useParams();
  const router = useRouter();
  const testId = params.id as string;
  const [test, setTest] = useState<any>(null);
  const [tip, setTip] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    if (testId) {
      loadTest();
    }
  }, [testId]);

  async function loadTest() {
    setLoading(true);
    try {
      const testData = await apiClient.getTest(testId);
      setTest(testData);
    } catch (error) {
      console.error("Failed to load test:", error);
      toast.error("Failed to load test details");
    } finally {
      setLoading(false);
    }
  }

  async function handlePayment() {
    // In Phase D, this will integrate with Stripe
    // For now, we'll simulate payment and start the test
    setProcessing(true);
    try {
      await apiClient.startTest(testId);
      toast.success("Payment successful! Test started.");
      router.push(`/tests/${testId}/processing`);
    } catch (error) {
      console.error("Failed to process payment:", error);
      toast.error("Payment failed. Please try again.");
    } finally {
      setProcessing(false);
    }
  }

  if (loading) {
    return (
      <div className="container py-8 max-w-3xl">
        <Skeleton className="h-12 w-64 mb-8" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!test) {
    return (
      <div className="container py-8 max-w-3xl">
        <Card>
          <CardHeader>
            <CardTitle>Test Not Found</CardTitle>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <a href="/tests/new">Back to Test Creation</a>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const baseCost = test.estimated_cost || 5.0;
  const totalCost = baseCost + tip;

  return (
    <div className="container py-8 max-w-3xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Payment</h1>
        <p className="mt-2 text-muted-foreground">
          Confirm your payment to start the test
        </p>
      </div>

      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[--ga-red] text-white flex items-center justify-center font-bold">
              ✓
            </div>
            <span className="text-muted-foreground">Select Model</span>
          </div>
          <div className="flex-1 h-1 bg-[--ga-red] mx-4" />
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[--ga-red] text-white flex items-center justify-center font-bold">
              2
            </div>
            <span className="font-medium">Payment</span>
          </div>
          <div className="flex-1 h-1 bg-muted mx-4" />
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-muted text-muted-foreground flex items-center justify-center font-bold">
              3
            </div>
            <span className="text-muted-foreground">Processing</span>
          </div>
          <div className="flex-1 h-1 bg-muted mx-4" />
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-muted text-muted-foreground flex items-center justify-center font-bold">
              4
            </div>
            <span className="text-muted-foreground">Results</span>
          </div>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Payment Summary</CardTitle>
          <CardDescription>
            Review your test details and payment amount
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Model:</span>
              <span className="font-medium">{test.model_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Version:</span>
              <span className="font-medium">{test.version}</span>
            </div>
          </div>

          <div className="border-t pt-4 space-y-4">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Test Cost:</span>
              <span className="font-medium">${baseCost.toFixed(2)}</span>
            </div>
            <div>
              <Label htmlFor="tip">Tip (Optional)</Label>
              <div className="flex gap-2 mt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setTip(1)}
                  className={tip === 1 ? "bg-[--ga-accent-red]" : ""}
                >
                  $1
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setTip(5)}
                  className={tip === 5 ? "bg-[--ga-accent-red]" : ""}
                >
                  $5
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setTip(10)}
                  className={tip === 10 ? "bg-[--ga-accent-red]" : ""}
                >
                  $10
                </Button>
                <Input
                  id="tip"
                  type="number"
                  placeholder="Custom"
                  value={tip || ""}
                  onChange={(e) => setTip(parseFloat(e.target.value) || 0)}
                  className="w-24"
                  min="0"
                  step="0.01"
                />
              </div>
            </div>
            <div className="border-t pt-4 flex justify-between text-lg font-bold">
              <span>Total:</span>
              <span>${totalCost.toFixed(2)}</span>
            </div>
          </div>

          <div className="bg-muted p-4 rounded-lg">
            <p className="text-sm text-muted-foreground">
              <strong>Note:</strong> Payment processing will be integrated with Stripe in Phase D.
              For now, clicking "Pay Now" will simulate payment and start your test.
            </p>
          </div>

          <div className="flex gap-4">
            <Button
              onClick={handlePayment}
              disabled={processing}
              className="bg-[--ga-red] hover:bg-[--ga-dark-red] flex-1"
            >
              {processing ? "Processing..." : `Pay $${totalCost.toFixed(2)} Now`}
            </Button>
            <Button asChild variant="outline">
              <a href="/tests/new">Cancel</a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
