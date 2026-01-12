"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import { toast } from "sonner";

// Types
interface StripeConfig {
  is_configured: boolean;
  source: "database" | "environment";
  is_live_mode: boolean;
  config_name: string | null;
  config_id: string | null;
  secret_key_masked: string | null;
  publishable_key_masked: string | null;
  webhook_secret_masked: string | null;
  updated_at: string | null;
  updated_by_email: string | null;
}

interface StripeBalance {
  available: { amount: number; currency: string }[];
  pending: { amount: number; currency: string }[];
  livemode: boolean;
}

interface StripeCharge {
  id: string;
  amount: number;
  amount_refunded: number;
  currency: string;
  status: string;
  paid: boolean;
  refunded: boolean;
  disputed: boolean;
  description: string | null;
  receipt_email: string | null;
  receipt_url: string | null;
  payment_intent: string | null;
  metadata: Record<string, string>;
  created: string;
  failure_code: string | null;
  failure_message: string | null;
}

interface StripeRefund {
  id: string;
  amount: number;
  currency: string;
  status: string;
  reason: string | null;
  payment_intent: string | null;
  charge: string | null;
  created: string;
  metadata: Record<string, string>;
}

interface StripeTransaction {
  id: string;
  amount: number;
  currency: string;
  net: number;
  fee: number;
  type: string;
  status: string;
  description: string | null;
  created: string;
  available_on: string | null;
  source: string | null;
}

export default function AdminPaymentsPage() {
  const { data: session, status } = useSession();
  const user = session?.user;
  const userLoading = status === "loading";
  const router = useRouter();

  // Config state
  const [config, setConfig] = useState<StripeConfig | null>(null);
  const [configLoading, setConfigLoading] = useState(true);
  const [balance, setBalance] = useState<StripeBalance | null>(null);
  const [balanceLoading, setBalanceLoading] = useState(false);

  // Config form state
  const [showConfigForm, setShowConfigForm] = useState(false);
  const [configFormData, setConfigFormData] = useState({
    secret_key: "",
    publishable_key: "",
    webhook_secret: "",
    name: "",
  });
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionTestResult, setConnectionTestResult] = useState<{
    success: boolean;
    error?: string;
    account_id?: string;
    business_name?: string;
  } | null>(null);
  const [savingConfig, setSavingConfig] = useState(false);

  // Charges state
  const [charges, setCharges] = useState<StripeCharge[]>([]);
  const [chargesLoading, setChargesLoading] = useState(true);
  const [chargesHasMore, setChargesHasMore] = useState(false);
  const [chargesCursor, setChargesCursor] = useState<string | null>(null);

  // Transactions state
  const [transactions, setTransactions] = useState<StripeTransaction[]>([]);
  const [transactionsLoading, setTransactionsLoading] = useState(true);
  const [transactionsHasMore, setTransactionsHasMore] = useState(false);
  const [transactionsCursor, setTransactionsCursor] = useState<string | null>(null);

  // Refunds state
  const [refunds, setRefunds] = useState<StripeRefund[]>([]);
  const [refundsLoading, setRefundsLoading] = useState(true);
  const [refundsHasMore, setRefundsHasMore] = useState(false);
  const [refundsCursor, setRefundsCursor] = useState<string | null>(null);

  // Delete config dialog
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [deletingConfig, setDeletingConfig] = useState(false);

  // Test current config state
  const [testingCurrentConfig, setTestingCurrentConfig] = useState(false);
  const [currentConfigTestResult, setCurrentConfigTestResult] = useState<{
    success: boolean;
    error?: string;
    message?: string;
    config_source?: string;
    is_restricted_key?: boolean;
    account_id?: string;
    business_name?: string;
  } | null>(null);

  // Load config on mount
  useEffect(() => {
    if (!userLoading && !user) {
      router.push("/api/auth/signin");
      return;
    }
    if (user) {
      loadConfig();
    }
  }, [user, userLoading, router]);

  // Load data when config is loaded and configured
  useEffect(() => {
    if (config?.is_configured) {
      loadBalance();
      loadCharges();
      loadTransactions();
      loadRefunds();
    }
  }, [config?.is_configured]);

  async function loadConfig() {
    setConfigLoading(true);
    try {
      const response = await fetch("/api/admin/stripe/config");
      if (response.ok) {
        const data = await response.json();
        setConfig(data);
      } else {
        toast.error("Failed to load Stripe configuration");
      }
    } catch (error) {
      console.error("Failed to load config:", error);
      toast.error("Failed to load Stripe configuration");
    } finally {
      setConfigLoading(false);
    }
  }

  async function loadBalance() {
    setBalanceLoading(true);
    try {
      const response = await fetch("/api/admin/stripe/balance");
      if (response.ok) {
        const data = await response.json();
        setBalance(data);
      } else {
        const error = await response.json().catch(() => ({ detail: "Failed to load balance" }));
        console.error("Failed to load balance:", error);
        toast.error(error.detail || "Failed to load balance");
      }
    } catch (error) {
      console.error("Failed to load balance:", error);
      toast.error("Failed to load balance");
    } finally {
      setBalanceLoading(false);
    }
  }

  async function loadCharges(cursor?: string | null) {
    setChargesLoading(true);
    try {
      const params = new URLSearchParams({ limit: "25" });
      if (cursor) params.set("starting_after", cursor);
      
      const response = await fetch(`/api/admin/stripe/charges?${params}`);
      if (response.ok) {
        const data = await response.json();
        if (cursor) {
          setCharges(prev => [...prev, ...data.data]);
        } else {
          setCharges(data.data);
        }
        setChargesHasMore(data.has_more);
        if (data.data.length > 0) {
          setChargesCursor(data.data[data.data.length - 1].id);
        }
      } else {
        const error = await response.json().catch(() => ({ detail: "Failed to load charges" }));
        console.error("Failed to load charges:", error);
        if (!cursor) {
          toast.error(error.detail || "Failed to load charges");
        }
      }
    } catch (error) {
      console.error("Failed to load charges:", error);
      if (!cursor) {
        toast.error("Failed to load charges");
      }
    } finally {
      setChargesLoading(false);
    }
  }

  async function loadTransactions(cursor?: string | null) {
    setTransactionsLoading(true);
    try {
      const params = new URLSearchParams({ limit: "25" });
      if (cursor) params.set("starting_after", cursor);
      
      const response = await fetch(`/api/admin/stripe/transactions?${params}`);
      if (response.ok) {
        const data = await response.json();
        if (cursor) {
          setTransactions(prev => [...prev, ...data.data]);
        } else {
          setTransactions(data.data);
        }
        setTransactionsHasMore(data.has_more);
        if (data.data.length > 0) {
          setTransactionsCursor(data.data[data.data.length - 1].id);
        }
      } else {
        const error = await response.json().catch(() => ({ detail: "Failed to load transactions" }));
        console.error("Failed to load transactions:", error);
        if (!cursor) {
          toast.error(error.detail || "Failed to load transactions");
        }
      }
    } catch (error) {
      console.error("Failed to load transactions:", error);
      if (!cursor) {
        toast.error("Failed to load transactions");
      }
    } finally {
      setTransactionsLoading(false);
    }
  }

  async function loadRefunds(cursor?: string | null) {
    setRefundsLoading(true);
    try {
      const params = new URLSearchParams({ limit: "25" });
      if (cursor) params.set("starting_after", cursor);
      
      const response = await fetch(`/api/admin/stripe/refunds?${params}`);
      if (response.ok) {
        const data = await response.json();
        if (cursor) {
          setRefunds(prev => [...prev, ...data.data]);
        } else {
          setRefunds(data.data);
        }
        setRefundsHasMore(data.has_more);
        if (data.data.length > 0) {
          setRefundsCursor(data.data[data.data.length - 1].id);
        }
      } else {
        const error = await response.json().catch(() => ({ detail: "Failed to load refunds" }));
        console.error("Failed to load refunds:", error);
        if (!cursor) {
          toast.error(error.detail || "Failed to load refunds");
        }
      }
    } catch (error) {
      console.error("Failed to load refunds:", error);
      if (!cursor) {
        toast.error("Failed to load refunds");
      }
    } finally {
      setRefundsLoading(false);
    }
  }

  async function testConnection() {
    if (!configFormData.secret_key) {
      toast.error("Please enter a secret key");
      return;
    }
    setTestingConnection(true);
    setConnectionTestResult(null);
    try {
      const response = await fetch("/api/admin/stripe/config/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ secret_key: configFormData.secret_key }),
      });
      const data = await response.json();
      setConnectionTestResult(data);
      if (data.success) {
        toast.success("Connection successful!");
      } else {
        toast.error(data.error || "Connection failed");
      }
    } catch (error) {
      console.error("Connection test failed:", error);
      toast.error("Failed to test connection");
    } finally {
      setTestingConnection(false);
    }
  }

  async function saveConfig() {
    if (!configFormData.secret_key || !configFormData.publishable_key) {
      toast.error("Secret key and publishable key are required");
      return;
    }
    setSavingConfig(true);
    try {
      const response = await fetch("/api/admin/stripe/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          secret_key: configFormData.secret_key,
          publishable_key: configFormData.publishable_key,
          webhook_secret: configFormData.webhook_secret || undefined,
          name: configFormData.name || undefined,
        }),
      });
      if (response.ok) {
        toast.success("Stripe configuration saved");
        setShowConfigForm(false);
        setConfigFormData({ secret_key: "", publishable_key: "", webhook_secret: "", name: "" });
        setConnectionTestResult(null);
        loadConfig();
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to save configuration");
      }
    } catch (error) {
      console.error("Failed to save config:", error);
      toast.error("Failed to save configuration");
    } finally {
      setSavingConfig(false);
    }
  }

  async function deleteConfig() {
    setDeletingConfig(true);
    try {
      const response = await fetch("/api/admin/stripe/config", {
        method: "DELETE",
      });
      if (response.ok) {
        toast.success("Configuration deleted. Using environment variables now.");
        setShowDeleteDialog(false);
        loadConfig();
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to delete configuration");
      }
    } catch (error) {
      console.error("Failed to delete config:", error);
      toast.error("Failed to delete configuration");
    } finally {
      setDeletingConfig(false);
    }
  }

  async function testCurrentConfig() {
    setTestingCurrentConfig(true);
    setCurrentConfigTestResult(null);
    try {
      const response = await fetch("/api/admin/stripe/config/test-current");
      const data = await response.json();
      setCurrentConfigTestResult(data);
      if (data.success) {
        toast.success(data.message || "Configuration test successful!");
      } else {
        toast.error(data.error || "Configuration test failed");
      }
    } catch (error) {
      console.error("Configuration test failed:", error);
      toast.error("Failed to test configuration");
    } finally {
      setTestingCurrentConfig(false);
    }
  }

  function formatCurrency(amount: number, currency: string) {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency.toUpperCase(),
    }).format(amount);
  }

  function formatDate(dateString: string) {
    return new Date(dateString).toLocaleString();
  }

  function getStatusBadgeVariant(status: string): "default" | "secondary" | "destructive" | "outline" {
    switch (status) {
      case "succeeded":
      case "available":
      case "paid":
        return "default";
      case "pending":
      case "processing":
        return "secondary";
      case "failed":
      case "canceled":
      case "disputed":
        return "destructive";
      default:
        return "outline";
    }
  }

  if (userLoading || configLoading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="container py-8">
      <div className="mb-8">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/admin">← Back to Admin Dashboard</Link>
        </Button>
        <h1 className="text-4xl font-bold">Payments & Stripe</h1>
        <p className="mt-2 text-muted-foreground">
          Manage Stripe configuration and view transaction history
        </p>
      </div>

      {/* Stripe Configuration Section */}
      <Card className="mb-8">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                Stripe Configuration
                {config?.is_configured && (
                  <Badge variant={config.is_live_mode ? "default" : "secondary"}>
                    {config.is_live_mode ? "Live Mode" : "Test Mode"}
                  </Badge>
                )}
              </CardTitle>
              <CardDescription>
                Configure Stripe API credentials for payment processing
              </CardDescription>
            </div>
            <div className="flex gap-2">
              {config?.is_configured && (
                <Button
                  variant="outline"
                  onClick={testCurrentConfig}
                  disabled={testingCurrentConfig}
                >
                  {testingCurrentConfig ? "Testing..." : "Test Configuration"}
                </Button>
              )}
              {config?.source === "database" && (
                <Button
                  variant="outline"
                  className="text-destructive"
                  onClick={() => setShowDeleteDialog(true)}
                >
                  Remove Config
                </Button>
              )}
              <Button onClick={() => setShowConfigForm(true)}>
                {config?.is_configured ? "Update Configuration" : "Configure Stripe"}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {config?.is_configured ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <Label className="text-muted-foreground">Source</Label>
                  <p className="font-medium capitalize">{config.source}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Config Name</Label>
                  <p className="font-medium">{config.config_name || "—"}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Last Updated</Label>
                  <p className="font-medium">
                    {config.updated_at ? formatDate(config.updated_at) : "—"}
                  </p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Updated By</Label>
                  <p className="font-medium">{config.updated_by_email || "—"}</p>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t">
                <div>
                  <Label className="text-muted-foreground">Secret Key</Label>
                  <p className="font-mono text-sm">{config.secret_key_masked || "—"}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Publishable Key</Label>
                  <p className="font-mono text-sm">{config.publishable_key_masked || "—"}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Webhook Secret</Label>
                  <p className="font-mono text-sm">{config.webhook_secret_masked || "Not configured"}</p>
                </div>
              </div>

              {/* Balance Display */}
              {balance && (
                <div className="pt-4 border-t">
                  <Label className="text-muted-foreground mb-2 block">Account Balance</Label>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-green-50 dark:bg-green-900/40 border border-green-200 dark:border-green-700 rounded-lg">
                      <p className="text-sm text-green-700 dark:text-green-300">Available</p>
                      <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                        {balance.available.map(b => formatCurrency(b.amount, b.currency)).join(", ") || "$0.00"}
                      </p>
                    </div>
                    <div className="p-4 bg-yellow-50 dark:bg-yellow-900/40 border border-yellow-200 dark:border-yellow-700 rounded-lg">
                      <p className="text-sm text-yellow-700 dark:text-yellow-300">Pending</p>
                      <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                        {balance.pending.map(b => formatCurrency(b.amount, b.currency)).join(", ") || "$0.00"}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Configuration Test Result */}
              {currentConfigTestResult && (
                <div className="pt-4 border-t">
                  <Alert variant={currentConfigTestResult.success ? "default" : "destructive"}>
                    <AlertTitle>
                      {currentConfigTestResult.success ? "✓ Configuration Valid" : "✗ Configuration Error"}
                    </AlertTitle>
                    <AlertDescription>
                      {currentConfigTestResult.success ? (
                        <div className="space-y-1 mt-2">
                          <p>{currentConfigTestResult.message || "Connection to Stripe successful."}</p>
                          {currentConfigTestResult.config_source && (
                            <p className="text-sm text-muted-foreground">
                              Source: <span className="capitalize">{currentConfigTestResult.config_source}</span>
                            </p>
                          )}
                          {currentConfigTestResult.business_name && (
                            <p className="text-sm text-muted-foreground">
                              Business: {currentConfigTestResult.business_name}
                            </p>
                          )}
                          {currentConfigTestResult.is_restricted_key && (
                            <p className="text-sm text-muted-foreground">
                              Using restricted API key (limited account details)
                            </p>
                          )}
                        </div>
                      ) : (
                        <p>{currentConfigTestResult.error}</p>
                      )}
                    </AlertDescription>
                  </Alert>
                </div>
              )}
            </div>
          ) : (
            <Alert>
              <AlertTitle>Stripe Not Configured</AlertTitle>
              <AlertDescription>
                {config?.source === "environment" 
                  ? "No Stripe API keys found in environment variables. Click 'Configure Stripe' to add credentials."
                  : "Click 'Configure Stripe' to set up payment processing."}
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Transaction History Tabs */}
      {config?.is_configured && (
        <Tabs defaultValue="charges" className="space-y-6">
          <TabsList>
            <TabsTrigger value="charges">Charges</TabsTrigger>
            <TabsTrigger value="transactions">Balance Transactions</TabsTrigger>
            <TabsTrigger value="refunds">Refunds</TabsTrigger>
          </TabsList>

          {/* Charges Tab */}
          <TabsContent value="charges">
            <Card>
              <CardHeader>
                <CardTitle>Charges</CardTitle>
                <CardDescription>
                  All charges processed through Stripe
                </CardDescription>
              </CardHeader>
              <CardContent>
                {chargesLoading && charges.length === 0 ? (
                  <Skeleton className="h-64" />
                ) : (
                  <>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Date</TableHead>
                          <TableHead>Amount</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Email</TableHead>
                          <TableHead>Type</TableHead>
                          <TableHead>Receipt</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {charges.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={6} className="text-center text-muted-foreground">
                              No charges found
                            </TableCell>
                          </TableRow>
                        ) : (
                          charges.map((charge) => (
                            <TableRow key={charge.id}>
                              <TableCell>{formatDate(charge.created)}</TableCell>
                              <TableCell className="font-medium">
                                {formatCurrency(charge.amount, charge.currency)}
                                {charge.refunded && (
                                  <span className="text-xs text-muted-foreground ml-1">
                                    (refunded: {formatCurrency(charge.amount_refunded, charge.currency)})
                                  </span>
                                )}
                              </TableCell>
                              <TableCell>
                                <Badge variant={getStatusBadgeVariant(charge.status)}>
                                  {charge.status}
                                </Badge>
                                {charge.disputed && (
                                  <Badge variant="destructive" className="ml-1">
                                    Disputed
                                  </Badge>
                                )}
                              </TableCell>
                              <TableCell>{charge.receipt_email || "—"}</TableCell>
                              <TableCell>
                                <span className="text-xs font-mono">
                                  {charge.metadata?.type || "payment"}
                                </span>
                              </TableCell>
                              <TableCell>
                                {charge.receipt_url ? (
                                  <a
                                    href={charge.receipt_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-primary hover:underline text-sm"
                                  >
                                    View
                                  </a>
                                ) : (
                                  "—"
                                )}
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                    {chargesHasMore && (
                      <div className="mt-4 flex justify-center">
                        <Button
                          variant="outline"
                          onClick={() => loadCharges(chargesCursor)}
                          disabled={chargesLoading}
                        >
                          {chargesLoading ? "Loading..." : "Load More"}
                        </Button>
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Balance Transactions Tab */}
          <TabsContent value="transactions">
            <Card>
              <CardHeader>
                <CardTitle>Balance Transactions</CardTitle>
                <CardDescription>
                  All balance changes including fees and payouts
                </CardDescription>
              </CardHeader>
              <CardContent>
                {transactionsLoading && transactions.length === 0 ? (
                  <Skeleton className="h-64" />
                ) : (
                  <>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Date</TableHead>
                          <TableHead>Type</TableHead>
                          <TableHead>Gross</TableHead>
                          <TableHead>Fee</TableHead>
                          <TableHead>Net</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Description</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {transactions.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={7} className="text-center text-muted-foreground">
                              No transactions found
                            </TableCell>
                          </TableRow>
                        ) : (
                          transactions.map((tx) => (
                            <TableRow key={tx.id}>
                              <TableCell>{formatDate(tx.created)}</TableCell>
                              <TableCell>
                                <Badge variant="outline">{tx.type}</Badge>
                              </TableCell>
                              <TableCell className={tx.amount >= 0 ? "text-green-600" : "text-red-600"}>
                                {formatCurrency(tx.amount, tx.currency)}
                              </TableCell>
                              <TableCell className="text-muted-foreground">
                                {tx.fee > 0 ? `-${formatCurrency(tx.fee, tx.currency)}` : "—"}
                              </TableCell>
                              <TableCell className="font-medium">
                                {formatCurrency(tx.net, tx.currency)}
                              </TableCell>
                              <TableCell>
                                <Badge variant={getStatusBadgeVariant(tx.status)}>
                                  {tx.status}
                                </Badge>
                              </TableCell>
                              <TableCell className="text-sm text-muted-foreground max-w-xs truncate">
                                {tx.description || "—"}
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                    {transactionsHasMore && (
                      <div className="mt-4 flex justify-center">
                        <Button
                          variant="outline"
                          onClick={() => loadTransactions(transactionsCursor)}
                          disabled={transactionsLoading}
                        >
                          {transactionsLoading ? "Loading..." : "Load More"}
                        </Button>
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Refunds Tab */}
          <TabsContent value="refunds">
            <Card>
              <CardHeader>
                <CardTitle>Refunds</CardTitle>
                <CardDescription>
                  All refunds issued through Stripe
                </CardDescription>
              </CardHeader>
              <CardContent>
                {refundsLoading && refunds.length === 0 ? (
                  <Skeleton className="h-64" />
                ) : (
                  <>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Date</TableHead>
                          <TableHead>Amount</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Reason</TableHead>
                          <TableHead>Payment Intent</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {refunds.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={5} className="text-center text-muted-foreground">
                              No refunds found
                            </TableCell>
                          </TableRow>
                        ) : (
                          refunds.map((refund) => (
                            <TableRow key={refund.id}>
                              <TableCell>{formatDate(refund.created)}</TableCell>
                              <TableCell className="font-medium">
                                {formatCurrency(refund.amount, refund.currency)}
                              </TableCell>
                              <TableCell>
                                <Badge variant={getStatusBadgeVariant(refund.status)}>
                                  {refund.status}
                                </Badge>
                              </TableCell>
                              <TableCell>{refund.reason || "—"}</TableCell>
                              <TableCell className="font-mono text-xs">
                                {refund.payment_intent?.slice(0, 20)}...
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                    {refundsHasMore && (
                      <div className="mt-4 flex justify-center">
                        <Button
                          variant="outline"
                          onClick={() => loadRefunds(refundsCursor)}
                          disabled={refundsLoading}
                        >
                          {refundsLoading ? "Loading..." : "Load More"}
                        </Button>
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {/* Configure Stripe Dialog */}
      <Dialog open={showConfigForm} onOpenChange={setShowConfigForm}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Configure Stripe</DialogTitle>
            <DialogDescription>
              Enter your Stripe API credentials. These will be encrypted and stored securely.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="config-name">Configuration Name (Optional)</Label>
              <Input
                id="config-name"
                placeholder="e.g., Production - Ministry Name"
                value={configFormData.name}
                onChange={(e) => setConfigFormData({ ...configFormData, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="secret-key">Secret Key *</Label>
              <Input
                id="secret-key"
                type="password"
                placeholder="sk_test_... or sk_live_..."
                value={configFormData.secret_key}
                onChange={(e) => setConfigFormData({ ...configFormData, secret_key: e.target.value })}
              />
              <p className="text-xs text-muted-foreground">
                Find this in your Stripe Dashboard under Developers → API keys
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="publishable-key">Publishable Key *</Label>
              <Input
                id="publishable-key"
                placeholder="pk_test_... or pk_live_..."
                value={configFormData.publishable_key}
                onChange={(e) => setConfigFormData({ ...configFormData, publishable_key: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="webhook-secret">Webhook Secret (Optional)</Label>
              <Input
                id="webhook-secret"
                type="password"
                placeholder="whsec_..."
                value={configFormData.webhook_secret}
                onChange={(e) => setConfigFormData({ ...configFormData, webhook_secret: e.target.value })}
              />
              <p className="text-xs text-muted-foreground">
                Required for processing payment webhooks. Find this in Stripe Dashboard → Webhooks
              </p>
            </div>

            {/* Test Connection */}
            <div className="pt-4 border-t">
              <Button
                variant="outline"
                onClick={testConnection}
                disabled={testingConnection || !configFormData.secret_key}
              >
                {testingConnection ? "Testing..." : "Test Connection"}
              </Button>
              {connectionTestResult && (
                <div className={`mt-2 p-3 rounded-md ${connectionTestResult.success ? "bg-green-50 dark:bg-green-950" : "bg-red-50 dark:bg-red-950"}`}>
                  {connectionTestResult.success ? (
                    <div className="text-green-700 dark:text-green-300">
                      <p className="font-medium">Connection successful!</p>
                      {connectionTestResult.account_id && (
                        <p className="text-sm">Account: {connectionTestResult.account_id}</p>
                      )}
                      {connectionTestResult.business_name && (
                        <p className="text-sm">Business: {connectionTestResult.business_name}</p>
                      )}
                    </div>
                  ) : (
                    <p className="text-red-700 dark:text-red-300">
                      {connectionTestResult.error || "Connection failed"}
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setShowConfigForm(false);
              setConfigFormData({ secret_key: "", publishable_key: "", webhook_secret: "", name: "" });
              setConnectionTestResult(null);
            }}>
              Cancel
            </Button>
            <Button onClick={saveConfig} disabled={savingConfig}>
              {savingConfig ? "Saving..." : "Save Configuration"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Config Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Remove Stripe Configuration</DialogTitle>
            <DialogDescription>
              Are you sure you want to remove the stored Stripe configuration? 
              The system will fall back to environment variables if configured.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={deleteConfig}
              disabled={deletingConfig}
            >
              {deletingConfig ? "Removing..." : "Remove Configuration"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
