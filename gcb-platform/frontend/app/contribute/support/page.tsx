"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import Link from "next/link";
import { Heart, Server, Users, Shield, ChevronLeft, Check, Lock } from "lucide-react";
import { useState, useEffect } from "react";
import { loadStripe } from "@stripe/stripe-js";
import { Elements, CardElement, useStripe, useElements } from "@stripe/react-stripe-js";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";
import { trackDonationInitiated, trackDonationCompleted } from "@/lib/analytics";

// Stripe will be initialized dynamically with key from API

// Preset donation amounts
const PRESET_AMOUNTS = [10, 25, 50, 100];
const MIN_AMOUNT = 5;

// Donation form component (needs to be inside Elements provider)
function DonationForm({ onSuccess }: { onSuccess: () => void }) {
  const stripe = useStripe();
  const elements = useElements();
  
  const [selectedAmount, setSelectedAmount] = useState<number | null>(25);
  const [customAmount, setCustomAmount] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const actualAmount = selectedAmount ?? (parseFloat(customAmount) || 0);
  const isValidAmount = actualAmount >= MIN_AMOUNT;

  const handlePresetClick = (amount: number) => {
    setSelectedAmount(amount);
    setCustomAmount("");
  };

  const handleCustomAmountChange = (value: string) => {
    setCustomAmount(value);
    setSelectedAmount(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!stripe || !elements || !isValidAmount) {
      return;
    }

    setProcessing(true);
    setError(null);

    try {
      // Track donation initiation
      trackDonationInitiated(actualAmount);
      
      // Create payment intent on backend
      const { client_secret } = await apiClient.createDonationIntent(
        actualAmount,
        email || undefined
      );

      // Get card element
      const cardElement = elements.getElement(CardElement);
      if (!cardElement) {
        throw new Error("Card element not found");
      }

      // Confirm payment with Stripe
      const { error: confirmError, paymentIntent } = await stripe.confirmCardPayment(
        client_secret,
        {
          payment_method: {
            card: cardElement,
            billing_details: email ? { email } : undefined,
          },
        }
      );

      if (confirmError) {
        setError(confirmError.message || "Payment failed");
        toast.error(confirmError.message || "Payment failed");
      } else if (paymentIntent && paymentIntent.status === "succeeded") {
        toast.success("Thank you for your donation!");
        // Track successful donation
        trackDonationCompleted(actualAmount);
        onSuccess();
      }
    } catch (err: any) {
      setError(err.message || err.detail || "Payment failed");
      toast.error("Payment failed. Please try again.");
    } finally {
      setProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Preset Amount Buttons */}
      <div className="space-y-2">
        <Label>Select Amount</Label>
        <div className="grid grid-cols-4 gap-2">
          {PRESET_AMOUNTS.map((amount) => (
            <Button
              key={amount}
              type="button"
              variant={selectedAmount === amount ? "brand" : "outline"}
              className="h-12 text-lg font-semibold"
              onClick={() => handlePresetClick(amount)}
            >
              ${amount}
            </Button>
          ))}
        </div>
      </div>

      {/* Custom Amount */}
      <div className="space-y-2">
        <Label htmlFor="custom-amount">Or enter a custom amount</Label>
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
          <Input
            id="custom-amount"
            type="number"
            min={MIN_AMOUNT}
            step="1"
            placeholder={`${MIN_AMOUNT} minimum`}
            value={customAmount}
            onChange={(e) => handleCustomAmountChange(e.target.value)}
            className="pl-7"
          />
        </div>
      </div>

      {/* Email for Receipt */}
      <div className="space-y-2">
        <Label htmlFor="email">Email for receipt (optional)</Label>
        <Input
          id="email"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
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
                  color: "#fafafa",
                  fontFamily: "inherit",
                  "::placeholder": {
                    color: "rgba(255, 255, 255, 0.5)",
                  },
                },
                invalid: {
                  color: "#ef4444",
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

      {/* Submit Button */}
      <Button
        type="submit"
        variant="brand"
        size="lg"
        disabled={!stripe || processing || !isValidAmount}
        className="w-full"
      >
        {processing ? (
          "Processing..."
        ) : (
          <>
            <Heart className="h-4 w-4 mr-2" />
            Donate ${actualAmount.toFixed(2)}
          </>
        )}
      </Button>

      {/* Security Note */}
      <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
        <Lock className="h-3 w-3" />
        <span>Secure payment via Stripe</span>
      </div>
    </form>
  );
}

// Success state component
function DonationSuccess({ amount }: { amount?: number }) {
  return (
    <div className="text-center py-8 space-y-4">
      <div className="mx-auto w-16 h-16 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
        <Check className="h-8 w-8 text-green-600 dark:text-green-400" />
      </div>
      <div>
        <h3 className="text-xl font-semibold mb-2">Thank You!</h3>
        <p className="text-muted-foreground">
          Your generous donation helps keep the Great Commission Benchmark 
          running and accessible to missionaries and ministry workers worldwide.
        </p>
      </div>
      <Button asChild variant="outline" className="mt-4">
        <Link href="/contribute">Back to Contribute</Link>
      </Button>
    </div>
  );
}

export default function SupportPage() {
  const [donationComplete, setDonationComplete] = useState(false);
  const [stripePromise, setStripePromise] = useState<Promise<any> | null>(null);

  // Fetch Stripe publishable key from API
  useEffect(() => {
    async function initializeStripe() {
      try {
        const response = await apiClient.getStripePublishableKey();
        if (response.publishable_key && response.is_configured) {
          setStripePromise(loadStripe(response.publishable_key));
        } else {
          console.warn("Stripe is not configured");
        }
      } catch (error) {
        console.error("Failed to load Stripe publishable key:", error);
      }
    }
    initializeStripe();
  }, []);

  return (
    <div className="container py-8 max-w-4xl">
      {/* Back link */}
      <Link 
        href="/contribute" 
        className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-6"
      >
        <ChevronLeft className="h-4 w-4 mr-1" />
        Back to Contribute
      </Link>

      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Heart className="h-8 w-8 text-[--ga-red]" />
          <h1 className="text-4xl font-bold">Support the Project</h1>
        </div>
        <p className="mt-2 text-muted-foreground text-lg">
          Help keep the Great Commission Benchmark running and growing
        </p>
      </div>

      {/* Main content grid */}
      <div className="grid gap-8 lg:grid-cols-5">
        {/* Left column - Why donate */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Why Your Support Matters</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-muted-foreground">
              <p>
                The Great Commission Benchmark is a community project that operates on a 
                cost-neutral, not-for-profit basis. We don&apos;t charge more than necessary, 
                but we do need to cover our costs.
              </p>
              <p>
                Your donation helps ensure this tool remains available to missionaries, 
                evangelists, and ministry workers around the world.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">What Your Donation Supports</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start gap-3">
                <Server className="h-5 w-5 text-[--ga-red] mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-sm">Infrastructure</p>
                  <p className="text-xs text-muted-foreground">
                    Hosting, databases, and platform services
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Users className="h-5 w-5 text-[--ga-red] mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-sm">Accessibility</p>
                  <p className="text-xs text-muted-foreground">
                    Sponsoring tests for those who cannot afford them
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Shield className="h-5 w-5 text-[--ga-red] mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-sm">Development</p>
                  <p className="text-xs text-muted-foreground">
                    Continued improvements and new features
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Financial Stewardship</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <p>
                All donations are received and managed by the{" "}
                <strong className="text-foreground">Digital Disciple Makers Network</strong>, 
                a ministry committed to supporting digital discipleship tools and collaboration.
              </p>
              <p>
                Donations may be tax-deductible. You will receive a receipt for your records.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Right column - Donation form */}
        <div className="lg:col-span-3">
          <Card className="border-[--ga-red]/20">
            <CardHeader>
              <CardTitle>Make a Donation</CardTitle>
              <CardDescription>
                Choose an amount to support the Great Commission Benchmark
              </CardDescription>
            </CardHeader>
            <CardContent>
              {donationComplete ? (
                <DonationSuccess />
              ) : stripePromise ? (
                <Elements stripe={stripePromise}>
                  <DonationForm onSuccess={() => setDonationComplete(true)} />
                </Elements>
              ) : (
                <div className="text-center py-8 space-y-4">
                  <p className="text-muted-foreground">
                    Payment processing is not configured.
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Please configure Stripe in the admin panel to enable donations.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Other ways to support */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Other Ways to Support</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">
            Financial donations aren&apos;t the only way to support the Great Commission Benchmark.
            You can also contribute by:
          </p>
          <div className="flex flex-wrap gap-3">
            <Button asChild variant="outline">
              <Link href="/contribute">Become a Tester</Link>
            </Button>
            <Button asChild variant="outline">
              <a href="https://discord.com" target="_blank" rel="noopener noreferrer">
                Volunteer Your Time
              </a>
            </Button>
            <Button asChild variant="outline">
              <a href="https://github.com" target="_blank" rel="noopener noreferrer">
                Contribute Code
              </a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
