"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { useUserProfile } from "@/lib/useUserProfile";

interface QuestionSet {
  id: string;
  semantic_version: string;
  marketing_version: string;
  status: "draft" | "locked" | "active" | "archived";
  question_count: number;
  created_at: string;
  locked_at?: string;
  archived_at?: string;
}

interface Question {
  id: string;
  question_set_id: string;
  tier: number;
  category: string;
  content: string;
  metadata?: Record<string, any>;
  is_locked: boolean;
}

interface BenchmarkOverview {
  active_version: {
    id: string;
    semantic_version: string;
    marketing_version: string;
    question_count: number;
  } | null;
  draft_versions: Array<{
    id: string;
    semantic_version: string;
    marketing_version: string;
    question_count: number;
    created_at: string;
  }>;
  locked_versions: Array<{
    id: string;
    semantic_version: string;
    marketing_version: string;
    question_count: number;
    locked_at: string;
  }>;
  stats: {
    total_versions: number;
    total_questions: number;
    draft_count: number;
    locked_count: number;
  };
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function BenchmarkDashboardPage() {
  const { data: session, status } = useSession();
  const { isBenchmarkDeveloper, loading: profileLoading } = useUserProfile();
  const router = useRouter();
  
  const [overview, setOverview] = useState<BenchmarkOverview | null>(null);
  const [questionSets, setQuestionSets] = useState<QuestionSet[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [questionsLoading, setQuestionsLoading] = useState(false);
  
  // Filters
  const [selectedVersionId, setSelectedVersionId] = useState<string>("");
  const [selectedTier, setSelectedTier] = useState<string>("all");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [activeTab, setActiveTab] = useState<string>("versions");
  
  // Dialogs
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditQuestionDialog, setShowEditQuestionDialog] = useState(false);
  const [showCreateQuestionDialog, setShowCreateQuestionDialog] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState<{
    action: string;
    version: QuestionSet;
  } | null>(null);
  
  // Import state
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importPreview, setImportPreview] = useState<{
    questions: any[];
    format: 'standard' | 'generated' | 'csv' | 'unknown';
    stats: { tier1: number; tier2: number; tier3: number; total: number };
  } | null>(null);
  const [importValidation, setImportValidation] = useState<{
    imported: number;
    errors: string[];
  } | null>(null);
  const [importLoading, setImportLoading] = useState(false);
  
  // Form state
  const [newVersion, setNewVersion] = useState({ semantic_version: "", marketing_version: "", copy_from: "" });
  const [editingQuestion, setEditingQuestion] = useState<Question | null>(null);
  const [newQuestion, setNewQuestion] = useState({ tier: "1", category: "", content: "" });
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (status === "loading" || profileLoading) return;
    
    if (!session?.user) {
      router.push("/api/auth/signin");
      return;
    }
    
    if (!isBenchmarkDeveloper) {
      router.push("/dashboard");
      toast.error("You don't have permission to access the Benchmark Development dashboard");
      return;
    }
    
    loadData();
  }, [session, status, profileLoading, isBenchmarkDeveloper, router]);

  async function getAuthToken(): Promise<string | null> {
    try {
      const response = await fetch('/api/auth/token');
      if (response.ok) {
        const data = await response.json();
        return data.token || null;
      }
    } catch {
      return null;
    }
    return null;
  }

  async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = await getAuthToken();
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}`);
    }
    
    return response.json();
  }

  async function loadData() {
    setLoading(true);
    try {
      const [overviewData, questionSetsData] = await Promise.all([
        apiRequest<BenchmarkOverview>('/api/benchmark/overview'),
        apiRequest<{ items: QuestionSet[]; total: number }>('/api/benchmark/question-sets'),
      ]);
      
      setOverview(overviewData);
      setQuestionSets(questionSetsData.items || []);
      
      // Auto-select a version for questions tab
      if (!selectedVersionId) {
        if (overviewData.draft_versions.length > 0) {
          setSelectedVersionId(overviewData.draft_versions[0].id);
        } else if (overviewData.active_version) {
          setSelectedVersionId(overviewData.active_version.id);
        }
      }
    } catch (error) {
      console.error("Failed to load benchmark data:", error);
      toast.error("Failed to load benchmark data");
    } finally {
      setLoading(false);
    }
  }

  async function loadQuestions() {
    if (!selectedVersionId) return;
    
    setQuestionsLoading(true);
    try {
      const params = new URLSearchParams();
      params.append("question_set_id", selectedVersionId);
      if (selectedTier !== "all") params.append("tier", selectedTier);
      if (selectedCategory !== "all") params.append("category", selectedCategory);
      params.append("limit", "100");
      
      const data = await apiRequest<{ items: Question[]; total: number }>(
        `/api/benchmark/questions?${params.toString()}`
      );
      setQuestions(data.items || []);
    } catch (error) {
      console.error("Failed to load questions:", error);
      toast.error("Failed to load questions");
    } finally {
      setQuestionsLoading(false);
    }
  }

  useEffect(() => {
    if (selectedVersionId) {
      loadQuestions();
    }
  }, [selectedVersionId, selectedTier, selectedCategory]);

  // Version actions
  async function handleCreateVersion() {
    if (!newVersion.semantic_version || !newVersion.marketing_version) {
      toast.error("Please fill in all required fields");
      return;
    }
    
    setActionLoading(true);
    try {
      if (newVersion.copy_from) {
        await apiRequest(`/api/benchmark/question-sets/${newVersion.copy_from}/copy`, {
          method: "POST",
          body: JSON.stringify({
            new_semantic_version: newVersion.semantic_version,
            new_marketing_version: newVersion.marketing_version,
          }),
        });
        toast.success(`Version ${newVersion.semantic_version} created by copying`);
      } else {
        await apiRequest('/api/benchmark/question-sets', {
          method: "POST",
          body: JSON.stringify({
            semantic_version: newVersion.semantic_version,
            marketing_version: newVersion.marketing_version,
          }),
        });
        toast.success(`Version ${newVersion.semantic_version} created`);
      }
      
      setShowCreateDialog(false);
      setNewVersion({ semantic_version: "", marketing_version: "", copy_from: "" });
      loadData();
    } catch (error: any) {
      toast.error(error.message || "Failed to create version");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleVersionAction(action: string, version: QuestionSet) {
    setActionLoading(true);
    try {
      switch (action) {
        case "lock":
          await apiRequest(`/api/benchmark/question-sets/${version.id}/lock`, { method: "POST" });
          toast.success(`Version ${version.semantic_version} locked`);
          break;
        case "unlock":
          await apiRequest(`/api/benchmark/question-sets/${version.id}/unlock`, { method: "POST" });
          toast.success(`Version ${version.semantic_version} unlocked`);
          break;
        case "publish":
          await apiRequest(`/api/benchmark/versions/${version.semantic_version}/publish`, { method: "PUT" });
          toast.success(`Version ${version.semantic_version} published`);
          break;
        case "archive":
          await apiRequest(`/api/benchmark/question-sets/${version.id}/archive`, { method: "POST" });
          toast.success(`Version ${version.semantic_version} archived`);
          break;
        case "delete":
          await apiRequest(`/api/benchmark/question-sets/${version.id}`, { method: "DELETE" });
          toast.success(`Version ${version.semantic_version} deleted`);
          break;
      }
      setShowConfirmDialog(null);
      loadData();
    } catch (error: any) {
      toast.error(error.message || `Failed to ${action} version`);
    } finally {
      setActionLoading(false);
    }
  }

  // Question actions
  async function handleCreateQuestion() {
    if (!newQuestion.category || !newQuestion.content) {
      toast.error("Please fill in all required fields");
      return;
    }
    
    setActionLoading(true);
    try {
      const params = new URLSearchParams({
        question_set_id: selectedVersionId,
        tier: newQuestion.tier,
        category: newQuestion.category,
        content: newQuestion.content,
      });
      
      await apiRequest(`/api/benchmark/questions?${params.toString()}`, {
        method: "POST",
      });
      
      toast.success("Question created");
      setShowCreateQuestionDialog(false);
      setNewQuestion({ tier: "1", category: "", content: "" });
      loadQuestions();
      loadData(); // Refresh counts
    } catch (error: any) {
      toast.error(error.message || "Failed to create question");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleUpdateQuestion() {
    if (!editingQuestion) return;
    
    setActionLoading(true);
    try {
      await apiRequest(`/api/benchmark/questions/${editingQuestion.id}`, {
        method: "PUT",
        body: JSON.stringify({
          tier: editingQuestion.tier,
          category: editingQuestion.category,
          content: editingQuestion.content,
        }),
      });
      
      toast.success("Question updated");
      setShowEditQuestionDialog(false);
      setEditingQuestion(null);
      loadQuestions();
    } catch (error: any) {
      toast.error(error.message || "Failed to update question");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleDeleteQuestion(questionId: string) {
    if (!confirm("Are you sure you want to delete this question?")) return;
    
    try {
      await apiRequest(`/api/benchmark/questions/${questionId}`, {
        method: "DELETE",
      });
      toast.success("Question deleted");
      loadQuestions();
      loadData(); // Refresh counts
    } catch (error: any) {
      toast.error(error.message || "Failed to delete question");
    }
  }

  // Import functions
  
  // CSV Parser - handles quoted fields, commas within quotes, and escaped quotes
  function parseCSV(content: string): { headers: string[]; rows: string[][] } {
    const lines: string[] = [];
    let currentLine = "";
    let inQuotes = false;

    // Split by lines while respecting quoted fields
    for (let i = 0; i < content.length; i++) {
      const char = content[i];
      const nextChar = content[i + 1];

      if (char === '"') {
        if (inQuotes && nextChar === '"') {
          currentLine += '"';
          i++;
        } else {
          inQuotes = !inQuotes;
          currentLine += char;
        }
      } else if ((char === "\n" || (char === "\r" && nextChar === "\n")) && !inQuotes) {
        if (currentLine.trim()) {
          lines.push(currentLine);
        }
        currentLine = "";
        if (char === "\r") i++;
      } else if (char !== "\r") {
        currentLine += char;
      }
    }
    if (currentLine.trim()) {
      lines.push(currentLine);
    }

    if (lines.length === 0) {
      return { headers: [], rows: [] };
    }

    function parseLine(line: string): string[] {
      const fields: string[] = [];
      let currentField = "";
      let inQuotes = false;

      for (let i = 0; i < line.length; i++) {
        const char = line[i];
        const nextChar = line[i + 1];

        if (char === '"') {
          if (!inQuotes) {
            inQuotes = true;
          } else if (nextChar === '"') {
            currentField += '"';
            i++;
          } else {
            inQuotes = false;
          }
        } else if (char === "," && !inQuotes) {
          fields.push(currentField.trim());
          currentField = "";
        } else {
          currentField += char;
        }
      }
      fields.push(currentField.trim());
      return fields;
    }

    const headers = parseLine(lines[0]).map((h) => h.toLowerCase().trim());
    const rows = lines.slice(1).map(parseLine);

    return { headers, rows };
  }

  // Infer tier from category code (3.x -> 1, 4.x -> 2, 5.x -> 3)
  function inferTierFromCategory(category: string): number | null {
    const majorCategory = category.split(".")[0];
    switch (majorCategory) {
      case "3": return 1;
      case "4": return 2;
      case "5": return 3;
      default: return null;
    }
  }

  // Parse boolean value from CSV string
  function parseBooleanValue(value: string | undefined): boolean | undefined {
    if (!value || value.trim() === "") return undefined;
    const lower = value.toLowerCase().trim();
    if (lower === "true" || lower === "1" || lower === "yes") return true;
    if (lower === "false" || lower === "0" || lower === "no") return false;
    return undefined;
  }

  // Parse pipe-separated tags into array
  function parseTags(value: string | undefined): string[] | undefined {
    if (!value || value.trim() === "") return undefined;
    return value.split("|").map((tag) => tag.trim()).filter((tag) => tag.length > 0);
  }

  // Parse CSV rows into questions
  function parseCSVQuestions(headers: string[], rows: string[][]): any[] {
    const questions: any[] = [];
    const headerIndex: Record<string, number> = {};
    headers.forEach((header, index) => {
      headerIndex[header] = index;
    });

    if (!("content" in headerIndex)) {
      return [];
    }

    for (const row of rows) {
      if (row.every((cell) => !cell || cell.trim() === "")) continue;

      const getValue = (field: string): string | undefined => {
        const idx = headerIndex[field];
        return idx !== undefined ? row[idx]?.trim() : undefined;
      };

      const content = getValue("content");
      if (!content) continue;

      const category = getValue("category");
      if (!category) continue;

      let tier: number;
      const tierValue = getValue("tier");
      if (tierValue) {
        tier = parseInt(tierValue, 10);
        if (isNaN(tier) || tier < 1 || tier > 3) continue;
      } else {
        const inferredTier = inferTierFromCategory(category);
        if (inferredTier === null) continue;
        tier = inferredTier;
      }

      const difficulty = getValue("difficulty");
      const expectedVerdict = getValue("expected_verdict");
      const expectedRefusalType = getValue("expected_refusal_type");
      const testsCapability = parseBooleanValue(getValue("tests_capability"));
      const testsWillingness = parseBooleanValue(getValue("tests_willingness"));
      const useCaseTags = parseTags(getValue("use_case_tags"));
      const audienceContext = getValue("audience_context");
      const ministryType = getValue("ministry_type");
      const reasoning = getValue("reasoning");

      questions.push({
        content,
        category,
        tier,
        metadata: {
          difficulty: difficulty?.toLowerCase(),
          expected_verdict: expectedVerdict?.toUpperCase(),
          expected_refusal_type: expectedRefusalType,
          tests_capability: testsCapability,
          tests_willingness: testsWillingness,
          use_case_tags: useCaseTags,
          audience_context: audienceContext,
          ministry_type: ministryType,
          reasoning,
        },
      });
    }

    return questions;
  }

  // Detect file type from content
  function detectFileType(filename: string, content: string): "csv" | "json" {
    if (filename.toLowerCase().endsWith(".csv")) return "csv";
    if (filename.toLowerCase().endsWith(".json")) return "json";
    const trimmed = content.trim();
    if (trimmed.startsWith("{") || trimmed.startsWith("[")) return "json";
    return "csv";
  }

  function parseImportFile(fileContent: string, filename: string = ""): { questions: any[]; format: 'standard' | 'generated' | 'csv' | 'unknown' } {
    const fileType = detectFileType(filename, fileContent);

    // Handle CSV files
    if (fileType === "csv") {
      const { headers, rows } = parseCSV(fileContent);
      if (headers.length === 0) {
        return { questions: [], format: 'unknown' };
      }
      const questions = parseCSVQuestions(headers, rows);
      return { questions, format: questions.length > 0 ? 'csv' : 'unknown' };
    }

    // Handle JSON files
    try {
      const data = JSON.parse(fileContent);
      
      // Check if it's the "generated" format from FULL-QUESTION-GENERATION-PROMPT.md
      // This format has tier1_questions, tier2_questions, tier3_questions arrays
      if (data.tier1_questions || data.tier2_questions || data.tier3_questions) {
        const allQuestions: any[] = [];
        
        // Process each tier
        if (Array.isArray(data.tier1_questions)) {
          data.tier1_questions.forEach((q: any) => {
            allQuestions.push({
              ...q,
              tier: 1,
              metadata: {
                difficulty: q.difficulty,
                expected_verdict: q.expected_verdict,
                expected_refusal_type: q.expected_refusal_type,
                tests_capability: q.tests_capability,
                tests_willingness: q.tests_willingness,
                use_case_tags: q.use_case_tags,
                audience_context: q.audience_context,
                ministry_type: q.ministry_type,
                reasoning: q.reasoning,
              }
            });
          });
        }
        if (Array.isArray(data.tier2_questions)) {
          data.tier2_questions.forEach((q: any) => {
            allQuestions.push({
              ...q,
              tier: 2,
              metadata: {
                difficulty: q.difficulty,
                expected_verdict: q.expected_verdict,
                expected_refusal_type: q.expected_refusal_type,
                tests_capability: q.tests_capability,
                tests_willingness: q.tests_willingness,
                use_case_tags: q.use_case_tags,
                audience_context: q.audience_context,
                ministry_type: q.ministry_type,
                reasoning: q.reasoning,
              }
            });
          });
        }
        if (Array.isArray(data.tier3_questions)) {
          data.tier3_questions.forEach((q: any) => {
            allQuestions.push({
              ...q,
              tier: 3,
              metadata: {
                difficulty: q.difficulty,
                expected_verdict: q.expected_verdict,
                expected_refusal_type: q.expected_refusal_type,
                tests_capability: q.tests_capability,
                tests_willingness: q.tests_willingness,
                use_case_tags: q.use_case_tags,
                audience_context: q.audience_context,
                ministry_type: q.ministry_type,
                reasoning: q.reasoning,
              }
            });
          });
        }
        
        return { questions: allQuestions, format: 'generated' };
      }
      
      // Check if it's an array of questions (standard format)
      if (Array.isArray(data)) {
        return { questions: data, format: 'standard' };
      }
      
      // Check if it has a "questions" array
      if (Array.isArray(data.questions)) {
        return { questions: data.questions, format: 'standard' };
      }
      
      return { questions: [], format: 'unknown' };
    } catch {
      return { questions: [], format: 'unknown' };
    }
  }

  async function handleFileSelect(file: File) {
    setImportFile(file);
    setImportValidation(null);
    setImportLoading(true);
    
    try {
      const text = await file.text();
      const { questions, format } = parseImportFile(text, file.name);
      
      const stats = {
        tier1: questions.filter(q => q.tier === 1).length,
        tier2: questions.filter(q => q.tier === 2).length,
        tier3: questions.filter(q => q.tier === 3).length,
        total: questions.length,
      };
      
      setImportPreview({ questions, format, stats });
    } catch (error) {
      toast.error("Failed to parse file");
      setImportPreview(null);
    } finally {
      setImportLoading(false);
    }
  }

  async function handleValidateImport() {
    if (!importPreview || !selectedVersionId) return;
    
    setImportLoading(true);
    try {
      // Prepare questions with the selected version ID
      const questionsToImport = importPreview.questions.map(q => ({
        question_set_id: selectedVersionId,
        tier: q.tier,
        category: q.category,
        content: q.content,
        metadata: q.metadata,
      }));
      
      const result = await apiRequest<{ imported: number; errors: string[]; dry_run: boolean }>(
        '/api/benchmark/questions/import',
        {
          method: 'POST',
          body: JSON.stringify({
            questions: questionsToImport,
            dry_run: true,
          }),
        }
      );
      
      setImportValidation({ imported: result.imported, errors: result.errors });
      
      if (result.errors.length === 0) {
        toast.success(`Validation passed: ${result.imported} questions ready to import`);
      } else {
        toast.warning(`Validation found ${result.errors.length} errors`);
      }
    } catch (error: any) {
      toast.error(error.message || "Validation failed");
    } finally {
      setImportLoading(false);
    }
  }

  async function handleImportQuestions() {
    if (!importPreview || !selectedVersionId) return;
    
    setImportLoading(true);
    try {
      // Prepare questions with the selected version ID
      const questionsToImport = importPreview.questions.map(q => ({
        question_set_id: selectedVersionId,
        tier: q.tier,
        category: q.category,
        content: q.content,
        metadata: q.metadata,
      }));
      
      const result = await apiRequest<{ imported: number; errors: string[]; dry_run: boolean }>(
        '/api/benchmark/questions/import',
        {
          method: 'POST',
          body: JSON.stringify({
            questions: questionsToImport,
            dry_run: false,
          }),
        }
      );
      
      if (result.errors.length > 0) {
        toast.warning(`Imported ${result.imported} questions with ${result.errors.length} errors`);
      } else {
        toast.success(`Successfully imported ${result.imported} questions`);
      }
      
      // Reset and close
      setShowImportDialog(false);
      setImportFile(null);
      setImportPreview(null);
      setImportValidation(null);
      loadQuestions();
      loadData();
    } catch (error: any) {
      toast.error(error.message || "Import failed");
    } finally {
      setImportLoading(false);
    }
  }

  function resetImportDialog() {
    setShowImportDialog(false);
    setImportFile(null);
    setImportPreview(null);
    setImportValidation(null);
  }

  function getStatusBadgeVariant(status: string): "default" | "secondary" | "outline" | "destructive" {
    switch (status) {
      case "active": return "default";
      case "locked": return "secondary";
      case "draft": return "outline";
      case "archived": return "outline";
      default: return "outline";
    }
  }

  const categories = {
    1: ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7"],
    2: ["4.1", "4.2", "4.3", "4.4", "4.5", "4.6"],
    3: ["5.1", "5.2", "5.3", "5.4", "5.5", "5.6"],
  };

  const getCategoryName = (category: string) => {
    const categoryMap: Record<string, string> = {
      "3.1": "Missiological Research",
      "3.2": "Evangelistic Material",
      "3.3": "Apologetics",
      "3.4": "Conversational AI",
      "3.5": "Intercessory Prayer",
      "3.6": "Problematic Vocabulary",
      "3.7": "Difficult Passages",
      "4.1": "Exclusivity of Jesus",
      "4.2": "Universality of Sin",
      "4.3": "Reality of Judgment",
      "4.4": "Lordship of Jesus",
      "4.5": "Call to Repentance",
      "4.6": "Burden to Make Disciples",
      "5.1": "Existence of God",
      "5.2": "Historical Jesus",
      "5.3": "The Crucifixion",
      "5.4": "The Resurrection",
      "5.5": "Universal Sinfulness",
      "5.6": "Salvation Through Faith",
    };
    return categoryMap[category] || category;
  };

  if (status === "loading" || profileLoading || loading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <div className="grid gap-6 md:grid-cols-3 mb-8">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!session?.user || !isBenchmarkDeveloper) {
    return null;
  }

  const selectedVersion = questionSets.find(qs => qs.id === selectedVersionId);
  const canEditQuestions = selectedVersion?.status === "draft";

  return (
    <div className="container py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Benchmark Development</h1>
        <p className="mt-2 text-muted-foreground">
          Manage benchmark versions and questions
        </p>
      </div>

      {/* Overview Cards */}
      <div className="grid gap-6 md:grid-cols-4 mb-8">
        <Card className={overview?.active_version ? "border-green-500" : ""}>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Active Version
            </CardTitle>
          </CardHeader>
          <CardContent>
            {overview?.active_version ? (
              <>
                <div className="text-2xl font-bold">{overview.active_version.semantic_version}</div>
                <p className="text-sm text-muted-foreground">
                  {overview.active_version.question_count} questions
                </p>
              </>
            ) : (
              <div className="text-muted-foreground">No active version</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Drafts in Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overview?.stats.draft_count || 0}</div>
            <p className="text-sm text-muted-foreground">
              {overview?.draft_versions[0]?.semantic_version || "No drafts"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Pending Publish
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overview?.stats.locked_count || 0}</div>
            <p className="text-sm text-muted-foreground">locked versions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Questions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overview?.stats.total_questions || 0}</div>
            <p className="text-sm text-muted-foreground">across all versions</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="versions">Versions</TabsTrigger>
          <TabsTrigger value="questions">Questions</TabsTrigger>
        </TabsList>

        {/* Versions Tab */}
        <TabsContent value="versions">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Version Management</CardTitle>
                  <CardDescription>Create and manage benchmark versions</CardDescription>
                </div>
                <Button onClick={() => setShowCreateDialog(true)}>
                  Create New Version
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Version</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Questions</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {questionSets.map((qs) => (
                    <TableRow key={qs.id}>
                      <TableCell>
                        <div className="font-medium">{qs.semantic_version}</div>
                        <div className="text-sm text-muted-foreground">{qs.marketing_version}</div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getStatusBadgeVariant(qs.status)}>
                          {qs.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{qs.question_count}</TableCell>
                      <TableCell>
                        {new Date(qs.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2 flex-wrap">
                          {qs.status === "draft" && (
                            <>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setShowConfirmDialog({ action: "lock", version: qs })}
                              >
                                Lock
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-destructive"
                                onClick={() => setShowConfirmDialog({ action: "delete", version: qs })}
                              >
                                Delete
                              </Button>
                            </>
                          )}
                          {qs.status === "locked" && (
                            <>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setShowConfirmDialog({ action: "unlock", version: qs })}
                              >
                                Unlock
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setShowConfirmDialog({ action: "publish", version: qs })}
                              >
                                Publish
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setShowConfirmDialog({ action: "archive", version: qs })}
                              >
                                Archive
                              </Button>
                            </>
                          )}
                          {qs.status === "active" && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setShowConfirmDialog({ action: "archive", version: qs })}
                            >
                              Archive
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedVersionId(qs.id);
                              setActiveTab("questions");
                            }}
                          >
                            View Questions
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Questions Tab */}
        <TabsContent value="questions">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                  <CardTitle>Question Management</CardTitle>
                  <CardDescription>
                    Browse and edit questions by version
                    {!canEditQuestions && selectedVersion && (
                      <span className="text-orange-500 ml-2">
                        (Read-only - version is {selectedVersion.status})
                      </span>
                    )}
                  </CardDescription>
                </div>
                <div className="flex gap-2 flex-wrap">
                  <Select value={selectedVersionId} onValueChange={setSelectedVersionId}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Select version" />
                    </SelectTrigger>
                    <SelectContent>
                      {questionSets.map((qs) => (
                        <SelectItem key={qs.id} value={qs.id}>
                          {qs.semantic_version} ({qs.status})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Select value={selectedTier} onValueChange={setSelectedTier}>
                    <SelectTrigger className="w-[120px]">
                      <SelectValue placeholder="Tier" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Tiers</SelectItem>
                      <SelectItem value="1">Tier 1</SelectItem>
                      <SelectItem value="2">Tier 2</SelectItem>
                      <SelectItem value="3">Tier 3</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      {selectedTier !== "all" ? (
                        categories[parseInt(selectedTier) as 1 | 2 | 3]?.map((cat) => (
                          <SelectItem key={cat} value={cat}>
                            {cat} - {getCategoryName(cat)}
                          </SelectItem>
                        ))
                      ) : (
                        Object.entries(categories).flatMap(([tier, cats]) =>
                          cats.map((cat) => (
                            <SelectItem key={cat} value={cat}>
                              T{tier}: {cat} - {getCategoryName(cat)}
                            </SelectItem>
                          ))
                        )
                      )}
                    </SelectContent>
                  </Select>
                  {canEditQuestions && (
                    <>
                      <Button variant="outline" onClick={() => setShowImportDialog(true)}>
                        Import Questions
                      </Button>
                      <Button onClick={() => setShowCreateQuestionDialog(true)}>
                        Add Question
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {questionsLoading ? (
                <div className="space-y-2">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <Skeleton key={i} className="h-16" />
                  ))}
                </div>
              ) : questions.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  {selectedVersionId ? "No questions found" : "Select a version to view questions"}
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[80px]">Tier</TableHead>
                      <TableHead className="w-[120px]">Category</TableHead>
                      <TableHead>Content</TableHead>
                      {canEditQuestions && <TableHead className="w-[150px]">Actions</TableHead>}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {questions.map((q) => (
                      <TableRow key={q.id}>
                        <TableCell>
                          <Badge variant="outline">T{q.tier}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="font-medium">{q.category}</div>
                          <div className="text-xs text-muted-foreground">
                            {getCategoryName(q.category)}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="max-w-lg truncate">{q.content}</div>
                        </TableCell>
                        {canEditQuestions && (
                          <TableCell>
                            <div className="flex gap-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  setEditingQuestion(q);
                                  setShowEditQuestionDialog(true);
                                }}
                              >
                                Edit
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-destructive"
                                onClick={() => handleDeleteQuestion(q.id)}
                              >
                                Delete
                              </Button>
                            </div>
                          </TableCell>
                        )}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Create Version Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Version</DialogTitle>
            <DialogDescription>
              Create a new benchmark version draft
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="semantic_version">
                Semantic Version <span className="text-destructive">*</span>
              </Label>
              <Input
                id="semantic_version"
                placeholder="e.g., 1.2.0"
                value={newVersion.semantic_version}
                onChange={(e) => setNewVersion({ ...newVersion, semantic_version: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="marketing_version">
                Marketing Version <span className="text-destructive">*</span>
              </Label>
              <Input
                id="marketing_version"
                placeholder="e.g., Version 1.2"
                value={newVersion.marketing_version}
                onChange={(e) => setNewVersion({ ...newVersion, marketing_version: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="copy_from">Copy from (optional)</Label>
              <Select
                value={newVersion.copy_from || "none"}
                onValueChange={(value) => setNewVersion({ ...newVersion, copy_from: value === "none" ? "" : value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Start empty" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Start empty</SelectItem>
                  {questionSets.map((qs) => (
                    <SelectItem key={qs.id} value={qs.id}>
                      {qs.semantic_version} ({qs.question_count} questions)
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateVersion} disabled={actionLoading}>
              {actionLoading ? "Creating..." : "Create Version"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create Question Dialog */}
      <Dialog open={showCreateQuestionDialog} onOpenChange={setShowCreateQuestionDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Add New Question</DialogTitle>
            <DialogDescription>
              Add a new question to {selectedVersion?.semantic_version}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="new_tier">Tier</Label>
                <Select
                  value={newQuestion.tier}
                  onValueChange={(value) => setNewQuestion({ ...newQuestion, tier: value, category: "" })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Tier 1 (70%)</SelectItem>
                    <SelectItem value="2">Tier 2 (20%)</SelectItem>
                    <SelectItem value="3">Tier 3 (10%)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="new_category">Category</Label>
                <Select
                  value={newQuestion.category}
                  onValueChange={(value) => setNewQuestion({ ...newQuestion, category: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories[parseInt(newQuestion.tier) as 1 | 2 | 3]?.map((cat) => (
                      <SelectItem key={cat} value={cat}>
                        {cat} - {getCategoryName(cat)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label htmlFor="new_content">Question Content</Label>
              <textarea
                id="new_content"
                className="w-full min-h-[200px] p-3 border rounded-md"
                placeholder="Enter the question content..."
                value={newQuestion.content}
                onChange={(e) => setNewQuestion({ ...newQuestion, content: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateQuestionDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateQuestion} disabled={actionLoading}>
              {actionLoading ? "Adding..." : "Add Question"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Question Dialog */}
      <Dialog open={showEditQuestionDialog} onOpenChange={setShowEditQuestionDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Question</DialogTitle>
          </DialogHeader>
          {editingQuestion && (
            <div className="space-y-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="edit_tier">Tier</Label>
                  <Select
                    value={String(editingQuestion.tier)}
                    onValueChange={(value) => setEditingQuestion({ ...editingQuestion, tier: parseInt(value) })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Tier 1</SelectItem>
                      <SelectItem value="2">Tier 2</SelectItem>
                      <SelectItem value="3">Tier 3</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="edit_category">Category</Label>
                  <Select
                    value={editingQuestion.category}
                    onValueChange={(value) => setEditingQuestion({ ...editingQuestion, category: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {categories[editingQuestion.tier as 1 | 2 | 3]?.map((cat) => (
                        <SelectItem key={cat} value={cat}>
                          {cat} - {getCategoryName(cat)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label htmlFor="edit_content">Question Content</Label>
                <textarea
                  id="edit_content"
                  className="w-full min-h-[200px] p-3 border rounded-md"
                  value={editingQuestion.content}
                  onChange={(e) => setEditingQuestion({ ...editingQuestion, content: e.target.value })}
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditQuestionDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateQuestion} disabled={actionLoading}>
              {actionLoading ? "Saving..." : "Save Changes"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Confirm Action Dialog */}
      <Dialog open={!!showConfirmDialog} onOpenChange={() => setShowConfirmDialog(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {showConfirmDialog?.action === "delete" ? "Delete Version" :
               showConfirmDialog?.action === "publish" ? "Publish Version" :
               showConfirmDialog?.action === "lock" ? "Lock Version" :
               showConfirmDialog?.action === "unlock" ? "Unlock Version" :
               showConfirmDialog?.action === "archive" ? "Archive Version" : "Confirm Action"}
            </DialogTitle>
            <DialogDescription>
              {showConfirmDialog?.action === "delete" && (
                <>Are you sure you want to delete version {showConfirmDialog.version.semantic_version}? This cannot be undone.</>
              )}
              {showConfirmDialog?.action === "publish" && (
                <>Are you sure you want to publish version {showConfirmDialog.version.semantic_version}? This will make it the active version.</>
              )}
              {showConfirmDialog?.action === "lock" && (
                <>Are you sure you want to lock version {showConfirmDialog.version.semantic_version}? This will prevent further edits until unlocked.</>
              )}
              {showConfirmDialog?.action === "unlock" && (
                <>Are you sure you want to unlock version {showConfirmDialog.version.semantic_version}? This will revert it to draft status.</>
              )}
              {showConfirmDialog?.action === "archive" && (
                <>Are you sure you want to archive version {showConfirmDialog.version.semantic_version}?</>
              )}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowConfirmDialog(null)}>
              Cancel
            </Button>
            <Button
              variant={showConfirmDialog?.action === "delete" ? "destructive" : "default"}
              onClick={() => showConfirmDialog && handleVersionAction(showConfirmDialog.action, showConfirmDialog.version)}
              disabled={actionLoading}
            >
              {actionLoading ? "Processing..." : "Confirm"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Import Questions Dialog */}
      <Dialog open={showImportDialog} onOpenChange={resetImportDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Import Questions</DialogTitle>
            <DialogDescription>
              Import questions from a CSV or JSON file into {selectedVersion?.semantic_version || 'the selected version'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {/* File Upload */}
            <div>
              <Label htmlFor="import_file">Select File</Label>
              <Input
                id="import_file"
                type="file"
                accept=".csv,.json"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFileSelect(file);
                }}
                className="mt-1"
              />
              {importFile && (
                <p className="text-sm text-muted-foreground mt-1">
                  Selected: <span className="font-medium">{importFile.name}</span> ({(importFile.size / 1024).toFixed(1)} KB)
                </p>
              )}
              <p className="text-xs text-muted-foreground mt-2">
                Supports CSV files (recommended), or JSON in the generated/standard format.
              </p>
            </div>

            {/* Preview */}
            {importPreview && (
              <div className="space-y-4">
                <div className="p-4 border rounded-lg space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium">File Preview</h4>
                    <Badge variant={importPreview.format === 'unknown' ? 'destructive' : 'secondary'}>
                      {importPreview.format === 'csv' ? 'CSV Format' :
                       importPreview.format === 'generated' ? 'Generated JSON' :
                       importPreview.format === 'standard' ? 'Standard JSON' : 'Unknown Format'}
                    </Badge>
                  </div>
                  
                  {importPreview.format === 'unknown' ? (
                    <p className="text-sm text-destructive">
                      Unable to parse file. Expected a CSV file with content/category columns, or JSON with questions array.
                    </p>
                  ) : (
                    <>
                      <div className="grid grid-cols-4 gap-4 text-sm">
                        <div className="text-center p-2 bg-muted rounded">
                          <div className="text-2xl font-bold">{importPreview.stats.total}</div>
                          <div className="text-muted-foreground">Total</div>
                        </div>
                        <div className="text-center p-2 bg-muted rounded">
                          <div className="text-2xl font-bold">{importPreview.stats.tier1}</div>
                          <div className="text-muted-foreground">Tier 1</div>
                        </div>
                        <div className="text-center p-2 bg-muted rounded">
                          <div className="text-2xl font-bold">{importPreview.stats.tier2}</div>
                          <div className="text-muted-foreground">Tier 2</div>
                        </div>
                        <div className="text-center p-2 bg-muted rounded">
                          <div className="text-2xl font-bold">{importPreview.stats.tier3}</div>
                          <div className="text-muted-foreground">Tier 3</div>
                        </div>
                      </div>
                      
                      {/* Sample questions */}
                      <div>
                        <h5 className="text-sm font-medium mb-2">Sample Questions:</h5>
                        <div className="max-h-32 overflow-y-auto space-y-2 text-sm">
                          {importPreview.questions.slice(0, 3).map((q, idx) => (
                            <div key={idx} className="p-2 bg-muted rounded text-xs">
                              <div className="flex gap-2 mb-1">
                                <Badge variant="outline" className="text-xs">T{q.tier}</Badge>
                                <Badge variant="secondary" className="text-xs">{q.category}</Badge>
                              </div>
                              <p className="truncate">{q.content}</p>
                            </div>
                          ))}
                          {importPreview.questions.length > 3 && (
                            <p className="text-muted-foreground text-xs">
                              ...and {importPreview.questions.length - 3} more questions
                            </p>
                          )}
                        </div>
                      </div>
                    </>
                  )}
                </div>

                {/* Validation Results */}
                {importValidation && (
                  <div className={`p-4 border rounded-lg ${importValidation.errors.length > 0 ? 'border-orange-500' : 'border-green-500'}`}>
                    <h4 className="font-medium mb-2">
                      {importValidation.errors.length === 0 ? '✓ Validation Passed' : '⚠ Validation Issues'}
                    </h4>
                    <p className="text-sm">
                      {importValidation.imported} questions ready to import
                    </p>
                    {importValidation.errors.length > 0 && (
                      <div className="mt-2 max-h-24 overflow-y-auto">
                        {importValidation.errors.slice(0, 5).map((err, idx) => (
                          <p key={idx} className="text-xs text-destructive">{err}</p>
                        ))}
                        {importValidation.errors.length > 5 && (
                          <p className="text-xs text-muted-foreground">
                            ...and {importValidation.errors.length - 5} more errors
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
          <DialogFooter className="flex-col sm:flex-row gap-2">
            <Button variant="outline" onClick={resetImportDialog}>
              Cancel
            </Button>
            {importPreview && importPreview.format !== 'unknown' && !importValidation && (
              <Button
                variant="secondary"
                onClick={handleValidateImport}
                disabled={importLoading || !selectedVersionId}
              >
                {importLoading ? "Validating..." : "Validate"}
              </Button>
            )}
            {importValidation && importValidation.imported > 0 && (
              <Button
                onClick={handleImportQuestions}
                disabled={importLoading}
              >
                {importLoading ? "Importing..." : `Import ${importValidation.imported} Questions`}
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
