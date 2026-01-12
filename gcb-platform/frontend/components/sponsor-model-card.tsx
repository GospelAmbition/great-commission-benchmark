"use client";

import { useEffect, useState, useRef } from "react";
import { loadStripe } from "@stripe/stripe-js";
import { Elements, CardElement, useStripe, useElements } from "@stripe/react-stripe-js";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";
import { trackSponsorshipRequest } from "@/lib/analytics";
import { 
  Sparkles, 
  MessageSquare, 
  ChevronDown, 
  ChevronUp, 
  DollarSign,
  Loader2,
  Search,
  Check,
  X
} from "lucide-react";

// Initialize Stripe only if key is provided
const stripeKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;
const stripePromise = stripeKey ? loadStripe(stripeKey) : null;

// Sponsorship fee
const SPONSORSHIP_FEE = 20.00;

interface Model {
  id: string;
  model_id: string;
  name?: string;
  provider?: string;
}

// Payment form component for sponsorships
function SponsorshipPaymentForm({
  modelId,
  modelName,
  clientSecret,
  onSuccess,
  onCancel,
}: {
  modelId: string;
  modelName: string;
  clientSecret: string;
  onSuccess: () => void;
  onCancel: () => void;
}) {
  const stripe = useStripe();
  const elements = useElements();
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [textColor, setTextColor] = useState("#fafafa"); // Default to white for dark mode
  const [placeholderColor, setPlaceholderColor] = useState("rgba(255, 255, 255, 0.5)");

  // Get the foreground color from CSS variables to support theme switching
  useEffect(() => {
    const rgbToHex = (rgb: string): string => {
      // Extract RGB values from "rgb(r, g, b)" or "rgba(r, g, b, a)"
      const match = rgb.match(/\d+/g);
      if (!match || match.length < 3) return "#fafafa";
      
      const r = parseInt(match[0], 10);
      const g = parseInt(match[1], 10);
      const b = parseInt(match[2], 10);
      
      return "#" + [r, g, b].map(x => {
        const hex = x.toString(16);
        return hex.length === 1 ? "0" + hex : hex;
      }).join("");
    };
    
    const getForegroundColor = (): string => {
      if (typeof window !== "undefined") {
        // Try to get the actual computed color by checking a test element
        const testEl = document.createElement("div");
        testEl.style.color = "var(--foreground)";
        testEl.style.position = "absolute";
        testEl.style.visibility = "hidden";
        document.body.appendChild(testEl);
        const computedColor = getComputedStyle(testEl).color;
        document.body.removeChild(testEl);
        
        // If we got a valid RGB/RGBA color, convert to hex
        if (computedColor && computedColor.startsWith("rgb")) {
          return rgbToHex(computedColor);
        }
        
        // Fallback: check if we're in dark mode
        const isDark = document.documentElement.classList.contains("dark") || 
                      !document.documentElement.classList.contains("light");
        return isDark ? "#fafafa" : "#09090b";
      }
      return "#fafafa";
    };
    
    const color = getForegroundColor();
    setTextColor(color);
    
    // Set placeholder color based on theme
    const isDark = typeof window !== "undefined" && 
                   (document.documentElement.classList.contains("dark") || 
                    !document.documentElement.classList.contains("light"));
    setPlaceholderColor(isDark ? "rgba(255, 255, 255, 0.5)" : "rgba(0, 0, 0, 0.5)");
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setProcessing(true);
    setError(null);

    try {
      const cardElement = elements.getElement(CardElement);
      if (!cardElement) {
        throw new Error("Card element not found");
      }

      const { error: confirmError, paymentIntent } = await stripe.confirmCardPayment(
        clientSecret,
        {
          payment_method: {
            card: cardElement,
          },
        }
      );

      if (confirmError) {
        setError(confirmError.message || "Payment failed");
        toast.error(confirmError.message || "Payment failed");
      } else if (paymentIntent && paymentIntent.status === "succeeded") {
        toast.success("Payment successful! Your sponsorship request has been submitted for review.");
        // Track successful sponsorship
        trackSponsorshipRequest("sponsorship", modelName);
        onSuccess();
      }
    } catch (err: any) {
      setError(err.message || "Payment failed");
      toast.error("Payment failed. Please try again.");
    } finally {
      setProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="p-3 bg-muted rounded-lg">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Model:</span>
          <span className="font-medium truncate ml-2">{modelName}</span>
        </div>
        <div className="flex justify-between text-sm mt-1">
          <span className="text-muted-foreground">Sponsorship Fee:</span>
          <span className="font-bold text-[--ga-red]">${SPONSORSHIP_FEE.toFixed(2)}</span>
        </div>
      </div>

      <div className="space-y-2">
        <Label>Card Information</Label>
        <div className="p-3 border rounded-lg bg-background">
          <CardElement
            options={{
              style: {
                base: {
                  fontSize: "14px",
                  color: textColor,
                  "::placeholder": {
                    color: placeholderColor,
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
          <AlertDescription className="text-sm">{error}</AlertDescription>
        </Alert>
      )}

      <div className="flex gap-2">
        <Button
          type="submit"
          variant="brand"
          disabled={!stripe || processing}
          className="flex-1"
          size="sm"
        >
          {processing ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <DollarSign className="h-4 w-4 mr-1" />
              Pay ${SPONSORSHIP_FEE.toFixed(2)}
            </>
          )}
        </Button>
        <Button type="button" variant="outline" size="sm" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
}

// Main component
export function SponsorModelCard() {
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [selectedModelName, setSelectedModelName] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [isListOpen, setIsListOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  
  // Custom request mode
  const [isCustomMode, setIsCustomMode] = useState(false);
  const [customModelName, setCustomModelName] = useState("");
  const [customMessage, setCustomMessage] = useState("");
  
  // Payment flow
  const [showPayment, setShowPayment] = useState(false);
  const [paymentData, setPaymentData] = useState<{
    clientSecret: string;
    sponsorshipId: string;
    modelName: string;
  } | null>(null);
  
  // User's sponsorships
  const [sponsorships, setSponsorships] = useState<any[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  // Close list when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (listRef.current && !listRef.current.contains(event.target as Node) &&
          inputRef.current && !inputRef.current.contains(event.target as Node)) {
        setIsListOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [modelsData, sponsorshipsData] = await Promise.all([
        apiClient.getAvailableModels({ limit: 500 }).catch(() => ({ items: [] })),
        apiClient.getUserSponsorships({ limit: 10 }).catch(() => ({ items: [], total: 0 })),
      ]);
      
      if (modelsData.items) {
        setModels(modelsData.items);
      }
      if (sponsorshipsData.items) {
        setSponsorships(sponsorshipsData.items);
      }
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setLoading(false);
    }
  }

  // Filter models based on search
  const filteredModels = models.filter((model) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    const name = (model.name || model.model_id || "").toLowerCase();
    const id = (model.model_id || model.id || "").toLowerCase();
    return name.includes(query) || id.includes(query);
  });

  function handleSelectModel(model: Model) {
    const modelId = model.model_id || model.id;
    const modelName = model.name || model.model_id || modelId;
    setSelectedModel(modelId);
    setSelectedModelName(modelName);
    setSearchQuery("");
    setIsListOpen(false);
  }

  function handleClearSelection() {
    setSelectedModel("");
    setSelectedModelName("");
    setSearchQuery("");
    inputRef.current?.focus();
  }

  async function handleSponsorSubmit() {
    if (!selectedModel) {
      toast.error("Please select a model");
      return;
    }

    setSubmitting(true);
    try {
      const response = await apiClient.createSponsorship({
        request_type: "sponsorship",
        openrouter_model_id: selectedModel,
      });

      if (response.payment_required && response.client_secret) {
        // Show payment form
        setPaymentData({
          clientSecret: response.client_secret,
          sponsorshipId: response.id,
          modelName: selectedModelName || selectedModel,
        });
        setShowPayment(true);
      } else {
        toast.success(response.message);
        loadData();
        setSelectedModel("");
        setSelectedModelName("");
      }
    } catch (error: any) {
      toast.error(error.message || "Failed to create sponsorship");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCustomRequestSubmit() {
    if (!customModelName.trim()) {
      toast.error("Please enter a model name");
      return;
    }
    if (!customMessage.trim()) {
      toast.error("Please enter a message");
      return;
    }

    setSubmitting(true);
    try {
      const response = await apiClient.createSponsorship({
        request_type: "request",
        custom_model_name: customModelName.trim(),
        message: customMessage.trim(),
      });

      toast.success(response.message);
      // Track custom request
      trackSponsorshipRequest("request", customModelName.trim());
      loadData();
      setCustomModelName("");
      setCustomMessage("");
      setIsCustomMode(false);
    } catch (error: any) {
      toast.error(error.message || "Failed to submit request");
    } finally {
      setSubmitting(false);
    }
  }

  function handlePaymentSuccess() {
    setShowPayment(false);
    setPaymentData(null);
    setSelectedModel("");
    setSelectedModelName("");
    loadData();
  }

  function handlePaymentCancel() {
    setShowPayment(false);
    setPaymentData(null);
  }

  function getStatusBadge(status: string, paymentStatus?: string) {
    if (status === "pending_payment" || paymentStatus === "pending") {
      return <Badge variant="outline" className="text-xs">Payment Pending</Badge>;
    }
    if (status === "pending") {
      return <Badge variant="outline" className="bg-yellow-50 dark:bg-yellow-900/60 text-yellow-700 dark:text-yellow-300 border-yellow-200 dark:border-yellow-700 text-xs">Pending Review</Badge>;
    }
    if (status === "approved") {
      return <Badge variant="default" className="bg-green-100 dark:bg-green-900/60 text-green-700 dark:text-green-300 border-green-200 dark:border-green-700 text-xs">Approved</Badge>;
    }
    if (status === "rejected") {
      return <Badge variant="destructive" className="text-xs">Rejected</Badge>;
    }
    if (status === "completed") {
      return <Badge variant="default" className="text-xs">Completed</Badge>;
    }
    return <Badge variant="outline" className="text-xs">{status}</Badge>;
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-64 mt-2" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full mt-4" />
        </CardContent>
      </Card>
    );
  }

  // Show payment form
  if (showPayment && paymentData) {
    return (
      <Card className="border-[--ga-red]/20">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-[--ga-red]" />
            <CardTitle className="text-lg">Complete Payment</CardTitle>
          </div>
          <CardDescription>
            Pay the sponsorship fee to submit your request
          </CardDescription>
        </CardHeader>
        <CardContent>
          {stripePromise ? (
            <Elements stripe={stripePromise}>
              <SponsorshipPaymentForm
                modelId={paymentData.sponsorshipId}
                modelName={paymentData.modelName}
                clientSecret={paymentData.clientSecret}
                onSuccess={handlePaymentSuccess}
                onCancel={handlePaymentCancel}
              />
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
    );
  }

  return (
    <div className="space-y-4">
      {/* Main Sponsorship Card */}
      <Card className="border-[--ga-red]/20">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-[--ga-red]" />
            <CardTitle className="text-lg">Sponsor a Model Test</CardTitle>
          </div>
          <CardDescription>
            Help test AI models for the Great Commission
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!isCustomMode ? (
            <>
              {/* Model Selection - Combobox Style */}
              <div className="space-y-2">
                <Label htmlFor="model-search">Select Model</Label>
                
                {/* Selected Model Display */}
                {selectedModel ? (
                  <div className="flex items-center gap-2 p-2 bg-muted rounded-lg border">
                    <Check className="h-4 w-4 text-green-600 flex-shrink-0" />
                    <span className="text-sm font-medium truncate flex-1">{selectedModelName}</span>
                    <button
                      type="button"
                      onClick={handleClearSelection}
                      className="p-1 hover:bg-background rounded text-muted-foreground hover:text-foreground"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ) : (
                  <div className="relative">
                    {/* Search Input */}
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        ref={inputRef}
                        id="model-search"
                        placeholder="Search models..."
                        value={searchQuery}
                        onChange={(e) => {
                          setSearchQuery(e.target.value);
                          setIsListOpen(true);
                        }}
                        onFocus={() => setIsListOpen(true)}
                        className="pl-9"
                      />
                    </div>
                    
                    {/* Filtered Model List */}
                    {isListOpen && (
                      <div
                        ref={listRef}
                        className="absolute z-50 w-full mt-1 bg-popover border rounded-lg shadow-lg overflow-hidden"
                      >
                        <div className="max-h-48 overflow-y-auto">
                          {filteredModels.length > 0 ? (
                            <>
                              {filteredModels.slice(0, 50).map((model) => (
                                <button
                                  key={model.model_id || model.id}
                                  type="button"
                                  onClick={() => handleSelectModel(model)}
                                  className="w-full px-3 py-2 text-left text-sm hover:bg-muted flex items-center justify-between gap-2 border-b last:border-0"
                                >
                                  <span className="truncate font-medium">
                                    {model.name || model.model_id}
                                  </span>
                                  {model.provider && (
                                    <span className="text-muted-foreground text-xs flex-shrink-0">
                                      {model.provider}
                                    </span>
                                  )}
                                </button>
                              ))}
                              {filteredModels.length > 50 && (
                                <div className="px-3 py-2 text-xs text-muted-foreground bg-muted/50">
                                  Showing 50 of {filteredModels.length} results. Type more to narrow down.
                                </div>
                              )}
                            </>
                          ) : (
                            <div className="px-3 py-4 text-sm text-center text-muted-foreground">
                              {searchQuery ? (
                                <>No models found matching &quot;{searchQuery}&quot;</>
                              ) : (
                                <>Type to search {models.length} available models</>
                              )}
                            </div>
                          )}
                        </div>
                        {!searchQuery && models.length > 0 && (
                          <div className="px-3 py-2 text-xs text-muted-foreground bg-muted/50 border-t">
                            {models.length} models available
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Sponsor Button */}
              <Button
                variant="brand"
                className="w-full"
                onClick={handleSponsorSubmit}
                disabled={!selectedModel || submitting}
              >
                {submitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <DollarSign className="h-4 w-4 mr-1" />
                    Sponsor Test (${SPONSORSHIP_FEE})
                  </>
                )}
              </Button>

              {/* Toggle to custom mode */}
              <button
                type="button"
                onClick={() => setIsCustomMode(true)}
                className="w-full text-sm text-muted-foreground hover:text-foreground flex items-center justify-center gap-1 py-2"
              >
                <MessageSquare className="h-4 w-4" />
                Can&apos;t find your model? Request it here (free)
              </button>
            </>
          ) : (
            <>
              {/* Custom Model Request Form */}
              <div className="space-y-3">
                <div className="space-y-2">
                  <Label htmlFor="custom-model">Model Name</Label>
                  <Input
                    id="custom-model"
                    placeholder="e.g., my-company/custom-model-v2"
                    value={customModelName}
                    onChange={(e) => setCustomModelName(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="custom-message">Message</Label>
                  <Textarea
                    id="custom-message"
                    placeholder="Tell us about this model and why you'd like it tested..."
                    value={customMessage}
                    onChange={(e) => setCustomMessage(e.target.value)}
                    rows={3}
                  />
                </div>
              </div>

              <div className="flex gap-2">
                <Button
                  variant="brand"
                  className="flex-1"
                  onClick={handleCustomRequestSubmit}
                  disabled={!customModelName.trim() || !customMessage.trim() || submitting}
                >
                  {submitting ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    "Submit Request (Free)"
                  )}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setIsCustomMode(false)}
                >
                  Back
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Sponsorship History */}
      {sponsorships.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <button
              type="button"
              onClick={() => setShowHistory(!showHistory)}
              className="flex items-center justify-between w-full text-left"
            >
              <CardTitle className="text-sm font-medium">
                Your Sponsorships ({sponsorships.length})
              </CardTitle>
              {showHistory ? (
                <ChevronUp className="h-4 w-4 text-muted-foreground" />
              ) : (
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              )}
            </button>
          </CardHeader>
          {showHistory && (
            <CardContent className="pt-0">
              <div className="space-y-2">
                {sponsorships.map((s) => (
                  <div
                    key={s.id}
                    className="flex items-center justify-between py-2 border-b last:border-0"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium truncate">{s.model_name}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(s.created_at).toLocaleDateString()}
                        {s.request_type === "request" && " • Request"}
                      </p>
                    </div>
                    <div className="ml-2 flex-shrink-0">
                      {getStatusBadge(s.status, s.payment_status)}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          )}
        </Card>
      )}
    </div>
  );
}
