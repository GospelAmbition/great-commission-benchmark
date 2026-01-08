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
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { apiClient } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { TestProgressIndicator } from "@/components/test-flow";
import { 
  AlertTriangle, 
  Clock, 
  FileQuestion, 
  Layers, 
  Trophy, 
  CreditCard,
  Pencil
} from "lucide-react";
import Link from "next/link";

// Initialize Stripe only if key is provided
const stripeKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;
const stripePromise = stripeKey ? loadStripe(stripeKey) : null;

// Test Configuration Card
function TestConfigurationCard({ 
  test, 
  onEdit 
}: { 
  test: any; 
  onEdit?: () => void;
}) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Test Configuration</CardTitle>
          {onEdit && (
            <Button variant="ghost" size="sm" onClick={onEdit}>
              <Pencil className="h-4 w-4 mr-1" />
              Edit
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Provider</span>
          <span className="font-medium">{test.provider || "OpenRouter"}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Model</span>
          <span className="font-medium">{test.model_name || test.model_id}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Version</span>
          <span className="font-medium">{test.version || "Current"}</span>
        </div>
      </CardContent>
    </Card>
  );
}

// Test Details Card
function TestDetailsCard() {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">Test Details</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center gap-3">
          <FileQuestion className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm">300 benchmark questions</span>
        </div>
        <div className="flex items-center gap-3">
          <Layers className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm">3 evaluation tiers</span>
        </div>
        <div className="flex items-center gap-3">
          <Trophy className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm">19 categories total</span>
        </div>
        <div className="flex items-center gap-3">
          <Clock className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm">Estimated time: 5-10 minutes</span>
        </div>
        
        <Separator className="my-3" />
        
        <div className="text-xs text-muted-foreground space-y-1">
          <div>• Task Capability (Tier 1): 70% weight</div>
          <div>• Gospel Core (Tier 2): 20% weight</div>
          <div>• Worldview Confession (Tier 3): 10% weight</div>
        </div>
      </CardContent>
    </Card>
  );
}

// Important Notes Card
function ImportantNotesCard() {
  return (
    <Card className="border-amber-200 dark:border-amber-800 bg-amber-50/50 dark:bg-amber-950/20">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-amber-600" />
          Important Notes
        </CardTitle>
      </CardHeader>
      <CardContent className="text-sm space-y-2 text-amber-900 dark:text-amber-100">
        <p>• Test runs cannot be cancelled once started</p>
        <p>• Results typically ready in 5-10 minutes</p>
        <p>• You can leave this page and return when ready</p>
        <p>• Results published to the leaderboard automatically</p>
        <p>• Auto-retry on errors; refund option if unrecoverable</p>
      </CardContent>
    </Card>
  );
}

// Sponsor Credit Card
function SponsorCreditCard({ 
  value, 
  onChange 
}: { 
  value: string; 
  onChange: (value: string) => void;
}) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <Trophy className="h-5 w-5" />
          Sponsor Credit (Optional)
        </CardTitle>
        <CardDescription>
          Display a name with this test to show you sponsored it
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Input
          placeholder="Your name, organization, or alias"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          maxLength={100}
        />
        <p className="text-xs text-muted-foreground mt-2">
          This will appear on the results page and share previews
        </p>
      </CardContent>
    </Card>
  );
}

// Order Summary Card
function OrderSummaryCard({ 
  breakdown,
  isDevMode 
}: { 
  breakdown: any;
  isDevMode: boolean;
}) {
  return (
    <Card className="sticky top-4">
      <CardHeader>
        <CardTitle className="text-lg">Order Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {breakdown && (
          <>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">API Cost (estimated)</span>
                <span>${breakdown.api_cost?.toFixed(2) || "0.00"}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Platform Fee</span>
                <span>${breakdown.processing_fee?.toFixed(2) || "20.00"}</span>
              </div>
              {breakdown.tip_amount > 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Tip</span>
                  <span>${breakdown.tip_amount.toFixed(2)}</span>
                </div>
              )}
            </div>
            
            <Separator />
            
            <div className="flex justify-between font-bold text-lg">
              <span>Total</span>
              <span>${breakdown.total?.toFixed(2) || "0.00"}</span>
            </div>
          </>
        )}
        
        <Separator />
        
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <CreditCard className="h-4 w-4" />
          <span>Secure checkout via {isDevMode ? "Dev Mode" : "Stripe"}</span>
        </div>
      </CardContent>
    </Card>
  );
}

// Dev Mode Payment Form
function DevModePaymentForm({ 
  testId, 
  test, 
  sponsorName,
  confirmed,
  onSuccess 
}: { 
  testId: string; 
  test: any; 
  sponsorName: string;
  confirmed: boolean;
  onSuccess: () => void;
}) {
  const [processing, setProcessing] = useState(false);
  const [costEstimate, setCostEstimate] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadCost() {
      try {
        const intent = await apiClient.createPaymentIntent(testId).catch(() => null);
        if (intent) {
          setCostEstimate(intent.breakdown);
        }
      } catch {
        setCostEstimate({
          api_cost: test.estimated_cost || test.cost_estimate || 0,
          processing_fee: 20,
          tip_amount: 0,
          total: (test.estimated_cost || test.cost_estimate || 0) + 20
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

  return (
    <div className="space-y-6">
      <Alert className="border-amber-500 bg-amber-50 dark:bg-amber-950">
        <AlertDescription className="text-amber-800 dark:text-amber-200">
          <strong>Development Mode:</strong> Payment processing is bypassed. 
          The cost shown is what would be charged in production.
        </AlertDescription>
      </Alert>

      <div className="p-4 border-2 border-dashed border-amber-500 rounded-lg bg-amber-50/50 dark:bg-amber-950/50">
        <div className="text-center text-amber-800 dark:text-amber-200">
          <CreditCard className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p className="font-medium">Card input disabled in dev mode</p>
          <p className="text-sm mt-1">Click below to accept the cost and start the test</p>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Button
        type="button"
        variant="brand"
        size="lg"
        onClick={handleDevComplete}
        disabled={processing || !confirmed}
        className="w-full"
      >
        {processing ? "Processing..." : `Accept Cost & Start Test (Dev Mode)`}
      </Button>
    </div>
  );
}

// Stripe Payment Form
function StripePaymentForm({ 
  testId, 
  test, 
  sponsorName,
  confirmed,
  onSuccess,
  onBreakdownChange 
}: { 
  testId: string; 
  test: any; 
  sponsorName: string;
  confirmed: boolean;
  onSuccess: () => void;
  onBreakdownChange: (breakdown: any) => void;
}) {
  const stripe = useStripe();
  const elements = useElements();
  const [tip, setTip] = useState<number>(0);
  const [processing, setProcessing] = useState(false);
  const [paymentIntent, setPaymentIntent] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function createIntent() {
      try {
        const baseCost = test.estimated_cost || test.cost_estimate || 0;
        const tipPercentage = tip > 0 ? Math.round((tip / baseCost) * 100) : 0;
        const intent = await apiClient.createPaymentIntent(testId, tipPercentage || undefined);
        setPaymentIntent(intent);
        onBreakdownChange(intent.breakdown);
      } catch (err: any) {
        setError(err.detail || "Failed to create payment intent");
        toast.error("Failed to initialize payment");
      }
    }
    createIntent();
  }, [testId, tip, test]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements || !confirmed) {
      return;
    }

    setProcessing(true);
    setError(null);

    try {
      const cardElement = elements.getElement(CardElement);
      if (!cardElement) {
        throw new Error("Card element not found");
      }

      const { error: confirmError, paymentIntent: confirmedIntent } = await stripe.confirmCardPayment(
        paymentIntent.client_secret,
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

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Tip Selection */}
      <div>
        <Label className="mb-3 block">Add a Tip (Optional)</Label>
        <div className="flex gap-2 flex-wrap">
          {[0, 1, 5, 10].map((amount) => (
            <Button
              key={amount}
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setTip(amount)}
              className={tip === amount ? "bg-[var(--ga-accent-red)] border-[var(--ga-red)]" : ""}
            >
              {amount === 0 ? "No tip" : `$${amount}`}
            </Button>
          ))}
          <Input
            type="number"
            placeholder="Custom"
            value={tip > 10 ? tip : ""}
            onChange={(e) => setTip(parseFloat(e.target.value) || 0)}
            className="w-24"
            min="0"
            step="0.01"
          />
        </div>
      </div>

      {/* Card Element */}
      <div className="space-y-2">
        <Label>Card Information</Label>
        <div className="p-4 border rounded-lg bg-background">
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

      <Button
        type="submit"
        variant="brand"
        size="lg"
        disabled={!stripe || processing || !paymentIntent || !confirmed}
        className="w-full"
      >
        {processing ? "Processing..." : `Pay $${paymentIntent?.breakdown?.total?.toFixed(2) || "0.00"} & Start Test`}
      </Button>
    </form>
  );
}

// Main Payment Page
export default function PaymentPage() {
  const params = useParams();
  const router = useRouter();
  const testId = params.id as string;
  const [test, setTest] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [devMode, setDevMode] = useState<boolean | null>(null);
  const [sponsorName, setSponsorName] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [breakdown, setBreakdown] = useState<any>(null);

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
      
      // Initialize breakdown - cast to any to access dynamic properties
      const data = testData as any;
      const apiCost = data.estimated_cost || data.cost_estimate || 0;
      setBreakdown({
        api_cost: apiCost,
        processing_fee: 20,
        tip_amount: 0,
        total: apiCost + 20
      });
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
      setDevMode(dev_mode || !stripe_configured);
    } catch {
      setDevMode(!process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY);
    }
  }

  function handleSuccess() {
    router.push(`/tests/${testId}/processing`);
  }

  function handleEdit() {
    router.push("/tests/new");
  }

  if (loading || devMode === null) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <div className="grid lg:grid-cols-[1fr_320px] gap-8">
          <Skeleton className="h-[600px]" />
          <Skeleton className="h-[400px]" />
        </div>
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
              <Link href="/tests/new">Back to Test Creation</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const useDevMode = devMode || !process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || !stripePromise;

  return (
    <div className="container py-8">
      {/* Header */}
      <div className="mb-8 max-w-4xl">
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-4xl font-bold">Confirm Your Test</h1>
          {useDevMode && (
            <Badge variant="outline" className="bg-amber-100 text-amber-800 border-amber-300">
              Dev Mode
            </Badge>
          )}
        </div>
        <p className="text-muted-foreground">
          Review your selection and confirm payment to start the benchmark.
        </p>
      </div>

      {/* Progress Indicator */}
      <div className="max-w-4xl">
        <TestProgressIndicator currentStep="payment" />
      </div>

      {/* Two-column layout */}
      <div className="grid lg:grid-cols-[1fr_320px] gap-8">
        {/* Left column */}
        <div className="space-y-6">
          <TestConfigurationCard test={test} onEdit={handleEdit} />
          <TestDetailsCard />
          <ImportantNotesCard />
          <SponsorCreditCard value={sponsorName} onChange={setSponsorName} />

          {/* Confirmation Checkbox */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <Checkbox
                  id="confirm"
                  checked={confirmed}
                  onCheckedChange={(checked) => setConfirmed(checked === true)}
                />
                <Label htmlFor="confirm" className="text-sm leading-relaxed cursor-pointer">
                  I understand this test cannot be cancelled once started and agree to the{" "}
                  <Link href="/tester-agreement" className="text-[var(--ga-red)] hover:underline">
                    Tester Agreement
                  </Link>
                </Label>
              </div>
            </CardContent>
          </Card>

          {/* Payment Form */}
          <Card>
            <CardHeader>
              <CardTitle>Payment</CardTitle>
              <CardDescription>
                {useDevMode ? "Payment is bypassed in development mode" : "Enter your payment details"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {useDevMode ? (
                <DevModePaymentForm 
                  testId={testId} 
                  test={test} 
                  sponsorName={sponsorName}
                  confirmed={confirmed}
                  onSuccess={handleSuccess} 
                />
              ) : stripePromise ? (
                <Elements stripe={stripePromise}>
                  <StripePaymentForm 
                    testId={testId} 
                    test={test} 
                    sponsorName={sponsorName}
                    confirmed={confirmed}
                    onSuccess={handleSuccess}
                    onBreakdownChange={setBreakdown}
                  />
                </Elements>
              ) : (
                <Alert variant="destructive">
                  <AlertDescription>
                    Stripe is not configured. Please set NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY.
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Back button */}
          <Button asChild variant="outline">
            <Link href="/tests/new">← Back to Selection</Link>
          </Button>
        </div>

        {/* Right column - Order Summary */}
        <div>
          <OrderSummaryCard breakdown={breakdown} isDevMode={useDevMode} />
        </div>
      </div>
    </div>
  );
}
