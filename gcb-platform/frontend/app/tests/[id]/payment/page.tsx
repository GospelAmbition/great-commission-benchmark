"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { loadStripe } from "@stripe/stripe-js";
import { Elements, CardElement, useStripe, useElements } from "@stripe/react-stripe-js";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { apiClient } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { Alert, AlertDescription } from "@/components/ui/alert";

// Initialize Stripe only if key is provided
const stripeKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;
const stripePromise = stripeKey ? loadStripe(stripeKey) : null;

// Dev Mode Payment Form - bypasses Stripe for local development
function DevModePaymentForm({ testId, test, onSuccess }: { testId: string; test: any; onSuccess: () => void }) {
  const [processing, setProcessing] = useState(false);
  const [costEstimate, setCostEstimate] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load cost estimate
    async function loadCost() {
      try {
        // We'll create a mock payment intent just to get the cost breakdown
        const intent = await apiClient.createPaymentIntent(testId).catch(() => null);
        if (intent) {
          setCostEstimate(intent.breakdown);
        }
      } catch (err) {
        // If payment intent creation fails in dev mode, show estimated cost from test
        setCostEstimate({
          api_cost: test.estimated_cost || test.cost_estimate || 0,
          processing_fee: 0,
          tip_amount: 0,
          total: test.estimated_cost || test.cost_estimate || 0
        });
      }
    }
    loadCost();
  }, [testId, test]);

  const handleDevComplete = async () => {
    setProcessing(true);
    setError(null);
    try {
      await apiClient.devCompletePayment(testId);
      toast.success("Payment bypassed (dev mode). Test starting...");
      onSuccess();
    } catch (err: any) {
      setError(err.detail || err.message || "Failed to complete dev payment");
      toast.error("Failed to complete dev payment");
    } finally {
      setProcessing(false);
    }
  };

  const baseCost = costEstimate?.total || test.estimated_cost || test.cost_estimate || 0;

  return (
    <div className="space-y-6">
      <Alert className="border-amber-500 bg-amber-50 dark:bg-amber-950">
        <AlertDescription className="text-amber-800 dark:text-amber-200">
          <strong>Development Mode:</strong> Payment processing is bypassed. 
          The cost shown below is what would be charged in production.
        </AlertDescription>
      </Alert>

      <div className="space-y-2">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Model:</span>
          <span className="font-medium">{test.model_name || test.model_id}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Version:</span>
          <span className="font-medium">{test.version || "Current"}</span>
        </div>
      </div>

      <div className="border-t pt-4 space-y-4">
        {costEstimate && (
          <>
            <div className="flex justify-between">
              <span className="text-muted-foreground">API Cost (estimated):</span>
              <span className="font-medium">${costEstimate.api_cost?.toFixed(2) || "0.00"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Processing Fee:</span>
              <span className="font-medium">${costEstimate.processing_fee?.toFixed(2) || "0.00"}</span>
            </div>
          </>
        )}
        <div className="border-t pt-4 flex justify-between text-lg font-bold">
          <span>Total:</span>
          <span>${baseCost.toFixed(2)}</span>
        </div>
      </div>

      <div className="p-4 border-2 border-dashed border-amber-500 rounded-lg bg-amber-50 dark:bg-amber-950">
        <div className="text-center text-amber-800 dark:text-amber-200">
          <p className="font-medium mb-2">💳 Card input disabled in dev mode</p>
          <p className="text-sm">Click below to accept the cost and start the test</p>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="flex gap-4">
        <Button
          type="button"
          variant="brand"
          onClick={handleDevComplete}
          disabled={processing}
          className="flex-1"
        >
          {processing ? "Processing..." : `Accept Cost & Start Test (Dev Mode)`}
        </Button>
        <Button type="button" variant="outline" asChild>
          <a href="/tests/new">Cancel</a>
        </Button>
      </div>
    </div>
  );
}

function PaymentForm({ testId, test, onSuccess }: { testId: string; test: any; onSuccess: () => void }) {
  const stripe = useStripe();
  const elements = useElements();
  const [tip, setTip] = useState<number>(0);
  const [tipPercentage, setTipPercentage] = useState<number>(0);
  const [processing, setProcessing] = useState(false);
  const [paymentIntent, setPaymentIntent] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Create payment intent when component mounts
    async function createIntent() {
      try {
        const intent = await apiClient.createPaymentIntent(testId, tipPercentage || undefined);
        setPaymentIntent(intent);
      } catch (err: any) {
        setError(err.detail || "Failed to create payment intent");
        toast.error("Failed to initialize payment");
      }
    }
    createIntent();
  }, [testId, tipPercentage]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setProcessing(true);
    setError(null);

    try {
      // Create payment intent with tip if tip changed
      let intent = paymentIntent;
      if (tipPercentage > 0 && (!intent || intent.breakdown.tip_amount !== tip)) {
        // Recalculate tip percentage from dollar amount
        const baseCost = test.estimated_cost || test.cost_estimate || 0;
        const calculatedTipPercentage = Math.round((tip / baseCost) * 100);
        intent = await apiClient.createPaymentIntent(testId, calculatedTipPercentage);
        setPaymentIntent(intent);
      }

      const cardElement = elements.getElement(CardElement);
      if (!cardElement) {
        throw new Error("Card element not found");
      }

      // Confirm payment
      const { error: confirmError, paymentIntent: confirmedIntent } = await stripe.confirmCardPayment(
        intent.client_secret,
        {
          payment_method: {
            card: cardElement,
            billing_details: {
              email: test.user_email,
            },
          },
        }
      );

      if (confirmError) {
        setError(confirmError.message || "Payment failed");
        toast.error(confirmError.message || "Payment failed");
      } else if (confirmedIntent && confirmedIntent.status === "succeeded") {
        toast.success("Payment successful! Test starting...");
        // Wait a moment for webhook to process, then redirect
        setTimeout(() => {
          onSuccess();
        }, 1000);
      }
    } catch (err: any) {
      setError(err.message || "Payment failed");
      toast.error("Payment failed. Please try again.");
    } finally {
      setProcessing(false);
    }
  };

  const baseCost = test.estimated_cost || test.cost_estimate || 0;
  const totalCost = paymentIntent ? paymentIntent.breakdown.total : baseCost + tip;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Model:</span>
          <span className="font-medium">{test.model_name}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Version:</span>
          <span className="font-medium">{test.version || "Current"}</span>
        </div>
      </div>

      <div className="border-t pt-4 space-y-4">
        {paymentIntent && (
          <>
            <div className="flex justify-between">
              <span className="text-muted-foreground">API Cost:</span>
              <span className="font-medium">${paymentIntent.breakdown.api_cost.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Processing Fee:</span>
              <span className="font-medium">${paymentIntent.breakdown.processing_fee.toFixed(2)}</span>
            </div>
          </>
        )}
        <div>
          <Label htmlFor="tip">Tip (Optional)</Label>
          <div className="flex gap-2 mt-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => {
                setTip(1);
                setTipPercentage(0); // Will recalculate
              }}
              className={tip === 1 ? "bg-[--ga-accent-red]" : ""}
            >
              $1
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => {
                setTip(5);
                setTipPercentage(0);
              }}
              className={tip === 5 ? "bg-[--ga-accent-red]" : ""}
            >
              $5
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => {
                setTip(10);
                setTipPercentage(0);
              }}
              className={tip === 10 ? "bg-[--ga-accent-red]" : ""}
            >
              $10
            </Button>
            <Input
              id="tip"
              type="number"
              placeholder="Custom"
              value={tip || ""}
              onChange={(e) => {
                const value = parseFloat(e.target.value) || 0;
                setTip(value);
                setTipPercentage(0);
              }}
              className="w-24"
              min="0"
              step="0.01"
            />
          </div>
        </div>
        {paymentIntent && (
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>Tip:</span>
            <span>${paymentIntent.breakdown.tip_amount.toFixed(2)}</span>
          </div>
        )}
        <div className="border-t pt-4 flex justify-between text-lg font-bold">
          <span>Total:</span>
          <span>${totalCost.toFixed(2)}</span>
        </div>
      </div>

      <div className="space-y-4">
        <Label>Card Information</Label>
        <div className="p-4 border rounded-lg">
          <CardElement
            options={{
              style: {
                base: {
                  fontSize: "16px",
                  color: "#424770",
                  "::placeholder": {
                    color: "#aab7c4",
                  },
                },
                invalid: {
                  color: "#9e2146",
                },
              },
            }}
          />
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="flex gap-4">
        <Button
          type="submit"
          variant="brand"
          disabled={!stripe || processing || !paymentIntent}
          className="flex-1"
        >
          {processing ? "Processing..." : `Pay $${totalCost.toFixed(2)} Now`}
        </Button>
        <Button type="button" variant="outline" asChild>
          <a href="/tests/new">Cancel</a>
        </Button>
      </div>
    </form>
  );
}

export default function PaymentPage() {
  const params = useParams();
  const router = useRouter();
  const testId = params.id as string;
  const [test, setTest] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [devMode, setDevMode] = useState<boolean | null>(null);

  useEffect(() => {
    if (testId) {
      loadTest();
      checkDevMode();
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

  async function checkDevMode() {
    try {
      const { dev_mode, stripe_configured } = await apiClient.checkPaymentDevMode();
      // Use dev mode if explicitly enabled OR if Stripe is not configured
      setDevMode(dev_mode || !stripe_configured);
    } catch (error) {
      // If we can't check, fall back to checking if Stripe key is present
      setDevMode(!process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY);
    }
  }

  function handleSuccess() {
    router.push(`/tests/${testId}/processing`);
  }

  if (loading || devMode === null) {
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

  // Check if we should use dev mode or real Stripe
  const useDevMode = devMode || !process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || !stripePromise;

  return (
    <div className="container py-8 max-w-3xl">
      <div className="mb-8">
        <div className="flex items-center gap-3">
          <h1 className="text-4xl font-bold">Payment</h1>
          {useDevMode && (
            <Badge variant="outline" className="bg-amber-100 text-amber-800 border-amber-300">
              Dev Mode
            </Badge>
          )}
        </div>
        <p className="mt-2 text-muted-foreground">
          {useDevMode 
            ? "Review the estimated cost and start your test (development mode)"
            : "Confirm your payment to start the test"
          }
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
            Review your test details and {useDevMode ? "estimated cost" : "payment amount"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {useDevMode ? (
            <DevModePaymentForm testId={testId} test={test} onSuccess={handleSuccess} />
          ) : stripePromise ? (
            <Elements stripe={stripePromise}>
              <PaymentForm testId={testId} test={test} onSuccess={handleSuccess} />
            </Elements>
          ) : (
            <Alert variant="destructive">
              <AlertDescription>
                Stripe is not configured. Please set NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY environment variable.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
