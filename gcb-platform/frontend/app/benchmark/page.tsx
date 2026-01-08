"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
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
import { 
  TIER_CATEGORIES, 
  CATEGORY_NAMES, 
  TIER_NAMES,
  getCategoryName 
} from "@/lib/benchmark-definitions";

// =============================================================================
// Types
// =============================================================================

interface QuestionSet {
  id: string;
  semantic_version: string;
  marketing_version: string;
  status: "draft" | "locked" | "active" | "archived";
  is_publicly_visible: boolean;
  question_count: number;
  target_question_count: number | null;
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
  expected_verdict?: string;
  is_locked: boolean;
  notes?: string;
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

interface CategoryDifficultyBreakdown {
  easy: number;
  medium: number;
  hard: number;
}

interface CategoryStats {
  count: number;
  target: number;
  difficulty: CategoryDifficultyBreakdown;
}

interface TierStats {
  count: number;
  target: number;
  categories: Record<string, CategoryStats>;
}

interface DifficultyCount {
  count: number;
  percentage: number;
}

interface DifficultyStats {
  easy: DifficultyCount;
  medium: DifficultyCount;
  hard: DifficultyCount;
}

interface VersionStats {
  question_set_id: string;
  semantic_version: string;
  marketing_version: string;
  total_questions: number;
  target_total: number;
  tier_stats: Record<number, TierStats>;
  difficulty_stats: DifficultyStats;
  category_difficulty_matrix: Record<string, CategoryDifficultyBreakdown>;
}

interface Alert {
  type: "error" | "warning" | "info";
  message: string;
  category?: string;
  tier?: number;
}

// =============================================================================
// Constants
// =============================================================================

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// TIER_CATEGORIES, CATEGORY_NAMES, and TIER_NAMES are imported from @/lib/benchmark-definitions
// Alias for backward compatibility with the component code
const CATEGORIES = TIER_CATEGORIES;

// Target distribution: 15% easy, 70% medium, 15% hard
const DIFFICULTY_TARGETS = {
  easy: 15,
  medium: 70,
  hard: 15,
};

// =============================================================================
// Main Component
// =============================================================================

export default function BenchmarkDashboardPage() {
  const { data: session, status } = useSession();
  const { isBenchmarkDeveloper, loading: profileLoading } = useUserProfile();
  const router = useRouter();
  
  // Data state
  const [overview, setOverview] = useState<BenchmarkOverview | null>(null);
  const [questionSets, setQuestionSets] = useState<QuestionSet[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [versionStats, setVersionStats] = useState<VersionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [statsLoading, setStatsLoading] = useState(false);
  const [questionsLoading, setQuestionsLoading] = useState(false);
  
  // Selection state
  const [selectedVersionId, setSelectedVersionId] = useState<string>("");
  const [selectedTier, setSelectedTier] = useState<string>("all");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>("all");
  const [hideLocked, setHideLocked] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>("statistics");
  
  // Dialog state
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditQuestionDialog, setShowEditQuestionDialog] = useState(false);
  const [showCreateQuestionDialog, setShowCreateQuestionDialog] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState<{
    action: string;
    version: QuestionSet;
  } | null>(null);
  const [archiveKeepVisible, setArchiveKeepVisible] = useState(false);
  const [showTargetDialog, setShowTargetDialog] = useState(false);
  const [targetVersion, setTargetVersion] = useState<QuestionSet | null>(null);
  const [editTargetValue, setEditTargetValue] = useState("");
  const [targetLoading, setTargetLoading] = useState(false);
  
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
  const [newQuestion, setNewQuestion] = useState({ tier: "1", category: "", content: "", difficulty: "medium", notes: "", expected_verdict: "" });
  const [actionLoading, setActionLoading] = useState(false);

  // =============================================================================
  // Auth & API Helpers
  // =============================================================================

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

  // =============================================================================
  // Data Loading
  // =============================================================================

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [overviewData, questionSetsData] = await Promise.all([
        apiRequest<BenchmarkOverview>('/api/benchmark/overview'),
        apiRequest<{ items: QuestionSet[]; total: number }>('/api/benchmark/question-sets'),
      ]);
      
      setOverview(overviewData);
      setQuestionSets(questionSetsData.items || []);
      
      // Auto-select a version
      if (!selectedVersionId) {
        if (overviewData.draft_versions.length > 0) {
          setSelectedVersionId(overviewData.draft_versions[0].id);
        } else if (overviewData.active_version) {
          setSelectedVersionId(overviewData.active_version.id);
        } else if (questionSetsData.items?.length > 0) {
          setSelectedVersionId(questionSetsData.items[0].id);
        }
      }
    } catch (error) {
      console.error("Failed to load benchmark data:", error);
      toast.error("Failed to load benchmark data");
    } finally {
      setLoading(false);
    }
  }, [selectedVersionId]);

  const loadVersionStats = useCallback(async () => {
    if (!selectedVersionId) return;
    
    setStatsLoading(true);
    try {
      const stats = await apiRequest<VersionStats>(
        `/api/benchmark/question-sets/${selectedVersionId}/stats`
      );
      setVersionStats(stats);
    } catch (error) {
      console.error("Failed to load version stats:", error);
      toast.error("Failed to load version statistics");
    } finally {
      setStatsLoading(false);
    }
  }, [selectedVersionId]);

  const loadQuestions = useCallback(async () => {
    if (!selectedVersionId) return;
    
    setQuestionsLoading(true);
    try {
      const params = new URLSearchParams();
      params.append("question_set_id", selectedVersionId);
      if (selectedTier !== "all") params.append("tier", selectedTier);
      if (selectedCategory !== "all") params.append("category", selectedCategory);
      params.append("limit", "200");
      
      const data = await apiRequest<{ items: Question[]; total: number }>(
        `/api/benchmark/questions?${params.toString()}`
      );
      
      // Filter by difficulty if selected (client-side since backend doesn't support it)
      let filteredQuestions = data.items || [];
      if (selectedDifficulty !== "all") {
        filteredQuestions = filteredQuestions.filter(q => 
          q.metadata?.difficulty?.toLowerCase() === selectedDifficulty
        );
      }
      
      setQuestions(filteredQuestions);
    } catch (error) {
      console.error("Failed to load questions:", error);
      toast.error("Failed to load questions");
    } finally {
      setQuestionsLoading(false);
    }
  }, [selectedVersionId, selectedTier, selectedCategory, selectedDifficulty]);

  // =============================================================================
  // Effects
  // =============================================================================

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
  }, [session, status, profileLoading, isBenchmarkDeveloper, router, loadData]);

  useEffect(() => {
    if (selectedVersionId) {
      loadVersionStats();
      loadQuestions();
    }
  }, [selectedVersionId, loadVersionStats, loadQuestions]);

  // =============================================================================
  // Version Actions
  // =============================================================================

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
          await apiRequest(`/api/benchmark/question-sets/${version.id}/archive?is_publicly_visible=${archiveKeepVisible}`, { method: "POST" });
          toast.success(`Version ${version.semantic_version} archived${archiveKeepVisible ? " (publicly visible)" : ""}`);
          setArchiveKeepVisible(false);
          break;
        case "toggle_visibility":
          const newVisibility = !version.is_publicly_visible;
          await apiRequest(`/api/benchmark/question-sets/${version.id}/visibility?is_publicly_visible=${newVisibility}`, { method: "PATCH" });
          toast.success(`Version ${version.semantic_version} is now ${newVisibility ? "publicly visible" : "hidden"}`);
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

  async function handleUpdateTarget() {
    if (!targetVersion) return;
    setTargetLoading(true);
    try {
      const targetValue = editTargetValue.trim() === "" ? null : parseInt(editTargetValue, 10);
      await apiRequest(`/api/benchmark/question-sets/${targetVersion.id}/target`, {
        method: "PATCH",
        body: JSON.stringify({ target_question_count: targetValue }),
      });

      const targetDisplay = targetValue ? `${targetValue} questions` : "auto-calculated";
      toast.success(`Target updated to ${targetDisplay}`);
      setShowTargetDialog(false);
      setTargetVersion(null);
      setEditTargetValue("");
      loadData();
      // Reload stats if we updated the currently selected version
      if (targetVersion.id === selectedVersionId) {
        loadVersionStats();
      }
    } catch (error: any) {
      toast.error(error.message || "Failed to update target");
    } finally {
      setTargetLoading(false);
    }
  }

  // =============================================================================
  // Question Actions
  // =============================================================================

  async function handleCreateQuestion() {
    if (!newQuestion.category || !newQuestion.content) {
      toast.error("Please fill in all required fields");
      return;
    }
    
    setActionLoading(true);
    try {
      await apiRequest('/api/benchmark/questions', {
        method: "POST",
        body: JSON.stringify({
          question_set_id: selectedVersionId,
          tier: parseInt(newQuestion.tier),
          category: newQuestion.category,
          content: newQuestion.content,
          metadata: {
            difficulty: newQuestion.difficulty,
            expected_verdict: newQuestion.expected_verdict || undefined,
          },
          notes: newQuestion.notes || undefined,
        }),
      });
      
      toast.success("Question created");
      setShowCreateQuestionDialog(false);
      setNewQuestion({ tier: "1", category: "", content: "", difficulty: "medium", notes: "", expected_verdict: "" });
      loadQuestions();
      loadVersionStats();
      loadData();
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
          metadata: editingQuestion.metadata,
          expected_verdict: editingQuestion.expected_verdict || undefined,
          is_locked: editingQuestion.is_locked,
          notes: editingQuestion.notes,
        }),
      });
      
      toast.success("Question updated");
      setShowEditQuestionDialog(false);
      setEditingQuestion(null);
      loadQuestions();
      loadVersionStats();
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
      loadVersionStats();
      loadData();
    } catch (error: any) {
      toast.error(error.message || "Failed to delete question");
    }
  }

  // =============================================================================
  // Import Functions
  // =============================================================================

  function parseCSV(content: string): { headers: string[]; rows: string[][] } {
    const rows: string[][] = [];
    let currentRow: string[] = [];
    let currentField = "";
    let inQuotes = false;

    // Parse CSV character by character, handling quoted fields that span multiple lines
    for (let i = 0; i < content.length; i++) {
      const char = content[i];
      const nextChar = content[i + 1];

      if (char === '"') {
        if (inQuotes && nextChar === '"') {
          // Escaped quote ("" represents a single quote in CSV)
          currentField += '"';
          i++; // Skip next quote
        } else {
          // Toggle quote state
          inQuotes = !inQuotes;
          // Don't include the quote character in the field value
        }
      } else if (char === "," && !inQuotes) {
        // Field separator (only outside quotes)
        currentRow.push(currentField.trim());
        currentField = "";
      } else if ((char === "\n" || (char === "\r" && nextChar === "\n")) && !inQuotes) {
        // Row separator (only outside quotes)
        // Finish current field
        currentRow.push(currentField.trim());
        currentField = "";
        // Add row if it has content
        if (currentRow.some((field) => field.length > 0)) {
          rows.push(currentRow);
        }
        currentRow = [];
        if (char === "\r") i++; // Skip \n in \r\n
      } else if (char !== "\r") {
        // Regular character (or newline inside quotes)
        currentField += char;
      }
    }

    // Handle last field and row
    if (currentField.trim() || currentRow.length > 0) {
      currentRow.push(currentField.trim());
    }
    if (currentRow.some((field) => field.length > 0)) {
      rows.push(currentRow);
    }

    if (rows.length === 0) {
      return { headers: [], rows: [] };
    }

    // First row is headers
    const headers = rows[0].map((h) => h.toLowerCase().trim());
    const dataRows = rows.slice(1);

    return { headers, rows: dataRows };
  }

  function inferTierFromCategory(category: string): number | null {
    const majorCategory = category.split(".")[0];
    switch (majorCategory) {
      case "3": return 1;
      case "4": return 2;
      case "5": return 3;
      default: return null;
    }
  }

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
      const notes = getValue("notes");

      questions.push({
        content,
        category,
        tier,
        metadata: {
          difficulty: difficulty?.toLowerCase(),
          expected_verdict: expectedVerdict?.toUpperCase(),
        },
        notes: notes || undefined,
      });
    }

    return questions;
  }

  function detectFileType(filename: string, content: string): "csv" | "json" {
    if (filename.toLowerCase().endsWith(".csv")) return "csv";
    if (filename.toLowerCase().endsWith(".json")) return "json";
    const trimmed = content.trim();
    if (trimmed.startsWith("{") || trimmed.startsWith("[")) return "json";
    return "csv";
  }

  function parseImportFile(fileContent: string, filename: string = ""): { questions: any[]; format: 'standard' | 'generated' | 'csv' | 'unknown' } {
    const fileType = detectFileType(filename, fileContent);

    if (fileType === "csv") {
      const { headers, rows } = parseCSV(fileContent);
      if (headers.length === 0) {
        return { questions: [], format: 'unknown' };
      }
      const questions = parseCSVQuestions(headers, rows);
      return { questions, format: questions.length > 0 ? 'csv' : 'unknown' };
    }

    try {
      const data = JSON.parse(fileContent);
      
      if (data.tier1_questions || data.tier2_questions || data.tier3_questions) {
        const allQuestions: any[] = [];
        
        [1, 2, 3].forEach((tier) => {
          const key = `tier${tier}_questions`;
          if (Array.isArray(data[key])) {
            data[key].forEach((q: any) => {
              allQuestions.push({
                ...q,
                tier,
                metadata: {
                  difficulty: q.difficulty,
                  expected_verdict: q.expected_verdict,
                }
              });
            });
          }
        });
        
        return { questions: allQuestions, format: 'generated' };
      }
      
      if (Array.isArray(data)) {
        return { questions: data, format: 'standard' };
      }
      
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
      const questionsToImport = importPreview.questions.map(q => ({
        question_set_id: selectedVersionId,
        tier: q.tier,
        category: q.category,
        content: q.content,
        metadata: q.metadata,
        notes: q.notes,
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
      const questionsToImport = importPreview.questions.map(q => ({
        question_set_id: selectedVersionId,
        tier: q.tier,
        category: q.category,
        content: q.content,
        metadata: q.metadata,
        notes: q.notes,
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
      
      resetImportDialog();
      loadQuestions();
      loadVersionStats();
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

  // =============================================================================
  // Export Functions
  // =============================================================================

  function exportQuestionsToCSV() {
    if (questions.length === 0) {
      toast.error("No questions to export");
      return;
    }

    // Helper to format UUID in truncated format (first 8 chars only)
    function formatTruncatedId(uuid: string): string {
      if (!uuid) return "";
      // Remove hyphens if present
      const cleanId = uuid.replace(/-/g, "");
      if (cleanId.length < 8) return uuid;
      // Return first 8 characters only for most compact format
      return cleanId.substring(0, 8);
    }

    // CSV header - only essential fields
    const headers = [
      "id",
      "content",
      "category",
      "tier",
      "difficulty",
      "expected_verdict",
      "notes"
    ];

    // Helper to escape CSV fields
    function escapeCSV(value: any): string {
      if (value === null || value === undefined) return "";
      const str = String(value);
      // If contains comma, newline, or quote, wrap in quotes and escape quotes
      if (str.includes(",") || str.includes("\n") || str.includes('"')) {
        return '"' + str.replace(/"/g, '""') + '"';
      }
      return str;
    }

    // Build CSV rows
    const rows = questions.map(q => {
      const meta = q.metadata || {};
      return [
        escapeCSV(formatTruncatedId(q.id)),
        escapeCSV(q.content),
        escapeCSV(q.category),
        escapeCSV(q.tier),
        escapeCSV(meta.difficulty),
        escapeCSV(q.expected_verdict),
        escapeCSV(q.notes)
      ].join(",");
    });

    // Combine header and rows
    const csvContent = [headers.join(","), ...rows].join("\n");

    // Create blob and download
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    
    // Generate filename with version and filters
    const version = selectedVersion?.semantic_version || "unknown";
    const filterParts = [];
    if (selectedTier !== "all") filterParts.push(`tier${selectedTier}`);
    if (selectedCategory !== "all") filterParts.push(selectedCategory.replace(".", "-"));
    if (selectedDifficulty !== "all") filterParts.push(selectedDifficulty);
    const filterSuffix = filterParts.length > 0 ? `_${filterParts.join("_")}` : "";
    const filename = `gcb_questions_v${version}${filterSuffix}.csv`;
    
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    toast.success(`Exported ${questions.length} questions to ${filename}`);
  }

  // =============================================================================
  // Computed Values & Alerts
  // =============================================================================

  const selectedVersion = questionSets.find(qs => qs.id === selectedVersionId);
  const canEditQuestions = selectedVersion?.status === "draft";

  function generateAlerts(): Alert[] {
    if (!versionStats) return [];
    
    const alerts: Alert[] = [];
    const total = versionStats.total_questions;
    
    // Check tier distribution
    if (total > 0) {
      const tier1Pct = (versionStats.tier_stats[1]?.count || 0) / total * 100;
      const tier2Pct = (versionStats.tier_stats[2]?.count || 0) / total * 100;
      const tier3Pct = (versionStats.tier_stats[3]?.count || 0) / total * 100;
      
      if (tier1Pct < 65) {
        alerts.push({
          type: "warning",
          message: `Tier 1 is at ${tier1Pct.toFixed(0)}% - needs to be at least 65%`,
          tier: 1,
        });
      } else if (tier1Pct > 75) {
        alerts.push({
          type: "warning",
          message: `Tier 1 is at ${tier1Pct.toFixed(0)}% - should be at most 75%`,
          tier: 1,
        });
      }
      
      if (tier2Pct < 15) {
        alerts.push({
          type: "warning",
          message: `Tier 2 is at ${tier2Pct.toFixed(0)}% - needs to be at least 15%`,
          tier: 2,
        });
      } else if (tier2Pct > 25) {
        alerts.push({
          type: "warning",
          message: `Tier 2 is at ${tier2Pct.toFixed(0)}% - should be at most 25%`,
          tier: 2,
        });
      }
      
      if (tier3Pct < 5) {
        alerts.push({
          type: "warning",
          message: `Tier 3 is at ${tier3Pct.toFixed(0)}% - needs to be at least 5%`,
          tier: 3,
        });
      } else if (tier3Pct > 15) {
        alerts.push({
          type: "warning",
          message: `Tier 3 is at ${tier3Pct.toFixed(0)}% - should be at most 15%`,
          tier: 3,
        });
      }
    }
    
    // Check categories missing questions
    [1, 2, 3].forEach((tier) => {
      const tierStats = versionStats.tier_stats[tier];
      if (!tierStats) return;
      
      Object.entries(tierStats.categories).forEach(([category, stats]) => {
        const missing = stats.target - stats.count;
        if (missing > 0) {
          alerts.push({
            type: "info",
            message: `${category} ${CATEGORY_NAMES[category]} needs ${missing} more question${missing > 1 ? 's' : ''}`,
            category,
            tier,
          });
        }
      });
    });
    
    // Check difficulty distribution (targets: 15% easy, 70% medium, 15% hard)
    if (total > 0) {
      const easyPct = versionStats.difficulty_stats.easy.percentage;
      const mediumPct = versionStats.difficulty_stats.medium.percentage;
      const hardPct = versionStats.difficulty_stats.hard.percentage;
      
      if (easyPct < 10 || easyPct > 20) {
        alerts.push({
          type: "warning",
          message: `Easy questions at ${easyPct.toFixed(0)}% - aim for ~15%`,
        });
      }
      if (mediumPct < 60 || mediumPct > 80) {
        alerts.push({
          type: "warning",
          message: `Medium questions at ${mediumPct.toFixed(0)}% - aim for ~70%`,
        });
      }
      if (hardPct < 10 || hardPct > 20) {
        alerts.push({
          type: "warning",
          message: `Hard questions at ${hardPct.toFixed(0)}% - aim for ~15%`,
        });
      }
    }
    
    return alerts;
  }

  const alerts = generateAlerts();

  function getStatusBadgeVariant(status: string): "default" | "secondary" | "outline" | "destructive" {
    switch (status) {
      case "active": return "default";
      case "locked": return "secondary";
      case "draft": return "outline";
      case "archived": return "outline";
      default: return "outline";
    }
  }

  // =============================================================================
  // Render Loading State
  // =============================================================================

  if (status === "loading" || profileLoading || loading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-12 w-64 mb-8" />
        <div className="grid gap-6 md:grid-cols-4 mb-8">
          {[1, 2, 3, 4].map((i) => (
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

  // =============================================================================
  // Main Render
  // =============================================================================

  return (
    <div className="container py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Benchmark Development</h1>
        <p className="mt-2 text-muted-foreground">
          Develop and manage benchmark versions and questions
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-6 md:grid-cols-4 mb-8">
        <Card className={overview?.active_version ? "border-green-500" : ""}>
          <CardHeader className="pb-2">
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
          <CardHeader className="pb-2">
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
          <CardHeader className="pb-2">
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
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Versions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overview?.stats.total_versions || 0}</div>
            <p className="text-sm text-muted-foreground">
              {overview?.stats.total_questions || 0} total questions
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Version Selector */}
      <Card className="mb-8">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <CardTitle>Working Version</CardTitle>
              <CardDescription>Select a version to view statistics and manage questions</CardDescription>
            </div>
            <div className="flex gap-2 flex-wrap">
              <Select value={selectedVersionId} onValueChange={setSelectedVersionId}>
                <SelectTrigger className="w-[220px]">
                  <SelectValue placeholder="Select version" />
                </SelectTrigger>
                <SelectContent>
                  {questionSets.map((qs) => (
                    <SelectItem key={qs.id} value={qs.id}>
                      {qs.semantic_version} ({qs.status}) - {qs.question_count} qs
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button onClick={() => setShowCreateDialog(true)}>
                Create New Version
              </Button>
            </div>
          </div>
        </CardHeader>
        {selectedVersion && (
          <CardContent className="pt-0">
            <div className="flex items-center gap-4 flex-wrap">
              <Badge variant={getStatusBadgeVariant(selectedVersion.status)} className="text-sm">
                {selectedVersion.status}
              </Badge>
              <span className="text-sm text-muted-foreground">
                {selectedVersion.marketing_version}
              </span>
              <span className="text-sm text-muted-foreground">
                Created {new Date(selectedVersion.created_at).toLocaleDateString()}
              </span>
              {selectedVersion.status === "draft" && (
                <div className="flex gap-2 ml-auto">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowConfirmDialog({ action: "lock", version: selectedVersion })}
                  >
                    Lock for Review
                  </Button>
                </div>
              )}
              {selectedVersion.status === "locked" && (
                <div className="flex gap-2 ml-auto">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowConfirmDialog({ action: "unlock", version: selectedVersion })}
                  >
                    Unlock
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => setShowConfirmDialog({ action: "publish", version: selectedVersion })}
                  >
                    Publish
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        )}
      </Card>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="statistics">Statistics</TabsTrigger>
          <TabsTrigger value="categories">Category Breakdown</TabsTrigger>
          <TabsTrigger value="questions">Questions</TabsTrigger>
          <TabsTrigger value="versions">All Versions</TabsTrigger>
        </TabsList>

        {/* Statistics Tab */}
        <TabsContent value="statistics" className="space-y-6">
          {statsLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-32" />
              <Skeleton className="h-48" />
            </div>
          ) : versionStats ? (
            <>
              {/* Progress Overview */}
              <Card>
                <CardHeader>
                  <CardTitle>Progress Overview</CardTitle>
                  <CardDescription>
                    {versionStats.total_questions} of {versionStats.target_total} questions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span>Overall Completion</span>
                        <span className="font-medium">
                          {Math.round((versionStats.total_questions / versionStats.target_total) * 100)}%
                        </span>
                      </div>
                      <Progress 
                        value={(versionStats.total_questions / versionStats.target_total) * 100} 
                        className="h-3"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Tier Distribution */}
              <div className="grid gap-6 md:grid-cols-3">
                {[1, 2, 3].map((tier) => {
                  const stats = versionStats.tier_stats[tier];
                  const pct = stats ? Math.round((stats.count / stats.target) * 100) : 0;
                  const weight = tier === 1 ? "70%" : tier === 2 ? "20%" : "10%";
                  return (
                    <Card key={tier}>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">
                          Tier {tier} ({weight} weight)
                        </CardTitle>
                        <CardDescription>{TIER_NAMES[tier]}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="text-3xl font-bold mb-2">
                          {stats?.count || 0} / {stats?.target || 0}
                        </div>
                        <Progress value={pct} className="h-2 mb-1" />
                        <div className="text-xs text-muted-foreground">{pct}% complete</div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>

              {/* Difficulty Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle>Difficulty Distribution</CardTitle>
                  <CardDescription>Target: 15% Easy, 70% Medium, 15% Hard</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-3">
                    {(["easy", "medium", "hard"] as const).map((difficulty) => {
                      const stats = versionStats.difficulty_stats[difficulty];
                      const target = DIFFICULTY_TARGETS[difficulty];
                      const isOnTarget = Math.abs(stats.percentage - target) <= 10;
                      return (
                        <div
                          key={difficulty}
                          className={`p-4 rounded-lg border ${
                            isOnTarget 
                              ? "bg-green-500/10 border-green-500/20" 
                              : "bg-orange-500/10 border-orange-500/20"
                          }`}
                        >
                          <div className="flex justify-between items-center mb-2">
                            <span className="font-medium capitalize text-foreground">{difficulty}</span>
                            <span className="text-sm text-muted-foreground">Target: {target}%</span>
                          </div>
                          <div className="text-2xl font-bold text-foreground">{stats.count}</div>
                          <div className={`text-sm ${isOnTarget ? "text-green-400" : "text-orange-400"}`}>
                            {stats.percentage.toFixed(1)}%
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              {/* Alerts */}
              {alerts.length > 0 && (
                <Card className="border-orange-500">
                  <CardHeader>
                    <CardTitle>Development Alerts</CardTitle>
                    <CardDescription>Issues to address before publishing</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {alerts.map((alert, idx) => (
                        <div
                          key={idx}
                          className={`p-3 rounded-lg text-sm flex items-center gap-2 ${
                            alert.type === "error"
                              ? "bg-red-50 text-red-700 dark:bg-red-950/20 dark:text-red-400"
                              : alert.type === "warning"
                              ? "bg-orange-50 text-orange-700 dark:bg-orange-950/20 dark:text-orange-400"
                              : "bg-blue-50 text-blue-700 dark:bg-blue-950/20 dark:text-blue-400"
                          }`}
                        >
                          <span className="flex-shrink-0">
                            {alert.type === "error" ? "✕" : alert.type === "warning" ? "⚠" : "ℹ"}
                          </span>
                          <span>{alert.message}</span>
                          {alert.category && canEditQuestions && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="ml-auto h-6 text-xs"
                              onClick={() => {
                                setSelectedCategory(alert.category!);
                                setSelectedTier(String(alert.tier));
                                setActiveTab("questions");
                              }}
                            >
                              Add Questions
                            </Button>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                Select a version to view statistics
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Categories Tab */}
        <TabsContent value="categories" className="space-y-6">
          {statsLoading ? (
            <Skeleton className="h-96" />
          ) : versionStats ? (
            <>
              {[1, 2, 3].map((tier) => {
                const tierStats = versionStats.tier_stats[tier];
                if (!tierStats) return null;
                
                return (
                  <Card key={tier}>
                    <CardHeader>
                      <CardTitle>Tier {tier}: {TIER_NAMES[tier]}</CardTitle>
                      <CardDescription>
                        {tierStats.count} / {tierStats.target} questions
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Category</TableHead>
                            <TableHead>Count</TableHead>
                            <TableHead>Target</TableHead>
                            <TableHead>Easy</TableHead>
                            <TableHead>Medium</TableHead>
                            <TableHead>Hard</TableHead>
                            <TableHead>Status</TableHead>
                            {canEditQuestions && <TableHead></TableHead>}
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {CATEGORIES[tier].map((category) => {
                            const catStats = tierStats.categories[category] || { count: 0, target: 0, difficulty: { easy: 0, medium: 0, hard: 0 } };
                            const missing = catStats.target - catStats.count;
                            const pct = catStats.target > 0 ? (catStats.count / catStats.target) * 100 : 0;
                            
                            return (
                              <TableRow key={category}>
                                <TableCell>
                                  <div className="font-medium">{category}</div>
                                  <div className="text-xs text-muted-foreground">
                                    {CATEGORY_NAMES[category]}
                                  </div>
                                </TableCell>
                                <TableCell className="font-medium">{catStats.count}</TableCell>
                                <TableCell className="text-muted-foreground">{catStats.target}</TableCell>
                                <TableCell>
                                  <Badge variant="outline" className="bg-green-50 dark:bg-green-950/20">
                                    {catStats.difficulty?.easy || 0}
                                  </Badge>
                                </TableCell>
                                <TableCell>
                                  <Badge variant="outline" className="bg-yellow-50 dark:bg-yellow-950/20">
                                    {catStats.difficulty?.medium || 0}
                                  </Badge>
                                </TableCell>
                                <TableCell>
                                  <Badge variant="outline" className="bg-red-50 dark:bg-red-950/20">
                                    {catStats.difficulty?.hard || 0}
                                  </Badge>
                                </TableCell>
                                <TableCell>
                                  {pct >= 100 ? (
                                    <Badge className="bg-green-600">Complete</Badge>
                                  ) : pct >= 50 ? (
                                    <Badge variant="secondary">{Math.round(pct)}%</Badge>
                                  ) : (
                                    <Badge variant="destructive">
                                      {missing > 0 ? `Need ${missing}` : `${Math.round(pct)}%`}
                                    </Badge>
                                  )}
                                </TableCell>
                                {canEditQuestions && (
                                  <TableCell>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => {
                                        setSelectedCategory(category);
                                        setSelectedTier(String(tier));
                                        setActiveTab("questions");
                                      }}
                                    >
                                      View
                                    </Button>
                                  </TableCell>
                                )}
                              </TableRow>
                            );
                          })}
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                );
              })}
            </>
          ) : (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                Select a version to view category breakdown
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Questions Tab */}
        <TabsContent value="questions">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                  <CardTitle>Question Management</CardTitle>
                  <CardDescription>
                    Browse and edit questions
                    {questions.length > 0 && (
                      <span className="ml-2">
                        ({hideLocked ? `${questions.filter(q => !q.is_locked).length} shown, ${questions.filter(q => q.is_locked).length} locked hidden` : `${questions.length} questions`})
                      </span>
                    )}
                    {!canEditQuestions && selectedVersion && (
                      <span className="text-orange-500 ml-2">
                        (Read-only - version is {selectedVersion.status})
                      </span>
                    )}
                  </CardDescription>
                </div>
                <div className="flex gap-2 flex-wrap">
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
                        CATEGORIES[parseInt(selectedTier) as 1 | 2 | 3]?.map((cat) => (
                          <SelectItem key={cat} value={cat}>
                            {cat} - {CATEGORY_NAMES[cat]}
                          </SelectItem>
                        ))
                      ) : (
                        Object.entries(CATEGORIES).flatMap(([tier, cats]) =>
                          cats.map((cat) => (
                            <SelectItem key={cat} value={cat}>
                              T{tier}: {cat}
                            </SelectItem>
                          ))
                        )
                      )}
                    </SelectContent>
                  </Select>
                  <Select value={selectedDifficulty} onValueChange={setSelectedDifficulty}>
                    <SelectTrigger className="w-[130px]">
                      <SelectValue placeholder="Difficulty" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Levels</SelectItem>
                      <SelectItem value="easy">Easy</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="hard">Hard</SelectItem>
                    </SelectContent>
                  </Select>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="hide-locked"
                      checked={hideLocked}
                      onChange={(e) => setHideLocked(e.target.checked)}
                      className="h-4 w-4 rounded border-gray-300"
                    />
                    <Label htmlFor="hide-locked" className="font-normal cursor-pointer text-sm">
                      Hide locked
                    </Label>
                  </div>
                  <Button 
                    variant="outline" 
                    onClick={exportQuestionsToCSV}
                    disabled={questions.length === 0}
                  >
                    Export CSV
                  </Button>
                  {canEditQuestions && (
                    <>
                      <Button variant="outline" onClick={() => setShowImportDialog(true)}>
                        Import
                      </Button>
                      <Button onClick={() => {
                        if (selectedCategory !== "all") {
                          setNewQuestion(prev => ({ ...prev, category: selectedCategory }));
                        }
                        if (selectedTier !== "all") {
                          setNewQuestion(prev => ({ ...prev, tier: selectedTier }));
                        }
                        setShowCreateQuestionDialog(true);
                      }}>
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
                  {selectedVersionId ? "No questions found matching filters" : "Select a version to view questions"}
                </div>
              ) : hideLocked && questions.every(q => q.is_locked) ? (
                <div className="text-center py-8 text-muted-foreground">
                  All {questions.length} questions are locked. Uncheck &quot;Hide locked&quot; to view them.
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[80px]">ID</TableHead>
                      <TableHead className="w-[180px]">Meta</TableHead>
                      <TableHead>Content</TableHead>
                      <TableHead>Notes</TableHead>
                      {canEditQuestions && <TableHead className="w-[120px]">Actions</TableHead>}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {questions.filter(q => !hideLocked || !q.is_locked).map((q) => {
                      // Format ID as truncated (first 8 chars)
                      const truncatedId = q.id ? q.id.replace(/-/g, "").substring(0, 8) : "";
                      return (
                      <TableRow key={q.id}>
                        <TableCell>
                          <code className="text-xs font-mono text-muted-foreground">{truncatedId}</code>
                        </TableCell>
                        <TableCell>
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <Badge variant="outline">T{q.tier}</Badge>
                              <span className="font-medium text-sm">{q.category}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Badge 
                                variant="outline"
                                className={
                                  q.metadata?.difficulty === "easy" 
                                    ? "bg-green-50 dark:bg-green-950/20" 
                                    : q.metadata?.difficulty === "hard"
                                    ? "bg-red-50 dark:bg-red-950/20"
                                    : "bg-yellow-50 dark:bg-yellow-950/20"
                                }
                              >
                                {q.metadata?.difficulty || "?"}
                              </Badge>
                              {q.is_locked && (
                                <Badge variant="default" className="bg-green-600 hover:bg-green-600 text-xs">
                                  Locked
                                </Badge>
                              )}
                            </div>
                            {q.expected_verdict && (
                              <div>
                                <Badge 
                                  variant="outline"
                                  className={
                                    q.expected_verdict === "ACCEPTED"
                                      ? "bg-blue-50 dark:bg-blue-950/20 text-blue-700 dark:text-blue-400"
                                      : q.expected_verdict === "COMPROMISED"
                                      ? "bg-orange-50 dark:bg-orange-950/20 text-orange-700 dark:text-orange-400"
                                      : "bg-red-50 dark:bg-red-950/20 text-red-700 dark:text-red-400"
                                  }
                                >
                                  {q.expected_verdict}
                                </Badge>
                              </div>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="whitespace-normal break-words">{q.content}</div>
                        </TableCell>
                        <TableCell>
                          {q.notes ? (
                            <div className="text-sm text-muted-foreground whitespace-normal break-words">
                              {q.notes}
                            </div>
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )}
                        </TableCell>
                        {canEditQuestions && (
                          <TableCell>
                            <div className="flex gap-1">
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
                    );
                    })}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Versions Tab */}
        <TabsContent value="versions">
          <Card>
            <CardHeader>
              <div>
                <CardTitle>All Versions</CardTitle>
                <CardDescription>Manage all benchmark versions</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Version</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Questions</TableHead>
                    <TableHead>Target</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {questionSets.map((qs) => (
                    <TableRow key={qs.id} className={qs.id === selectedVersionId ? "bg-muted/50" : ""}>
                      <TableCell>
                        <div className="font-medium">{qs.semantic_version}</div>
                        <div className="text-sm text-muted-foreground">{qs.marketing_version}</div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Badge variant={getStatusBadgeVariant(qs.status)}>
                            {qs.status}
                          </Badge>
                          {qs.status === "archived" && (
                            <Badge variant={qs.is_publicly_visible ? "outline" : "secondary"} className="text-xs">
                              {qs.is_publicly_visible ? "Public" : "Hidden"}
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{qs.question_count}</TableCell>
                      <TableCell>
                        {qs.target_question_count ? (
                          <span>{qs.target_question_count}</span>
                        ) : (
                          <span className="text-muted-foreground text-xs">Auto</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {new Date(qs.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2 flex-wrap">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSelectedVersionId(qs.id)}
                          >
                            Select
                          </Button>
                          {qs.status === "draft" && (
                            <>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  setTargetVersion(qs);
                                  setEditTargetValue(qs.target_question_count?.toString() || "");
                                  setShowTargetDialog(true);
                                }}
                              >
                                Set Target
                              </Button>
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
                            </>
                          )}
                          {(qs.status === "active" || qs.status === "locked") && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setShowConfirmDialog({ action: "archive", version: qs })}
                            >
                              Archive
                            </Button>
                          )}
                          {qs.status === "archived" && (
                            <>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setShowConfirmDialog({ action: "toggle_visibility", version: qs })}
                              >
                                {qs.is_publicly_visible ? "Hide" : "Show"}
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
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
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
        <DialogContent className="max-w-4xl">
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
                <Label htmlFor="new_difficulty">Difficulty</Label>
                <Select
                  value={newQuestion.difficulty}
                  onValueChange={(value) => setNewQuestion({ ...newQuestion, difficulty: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="easy">Easy</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="hard">Hard</SelectItem>
                  </SelectContent>
                </Select>
              </div>
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
                  {CATEGORIES[parseInt(newQuestion.tier) as 1 | 2 | 3]?.map((cat) => (
                    <SelectItem key={cat} value={cat}>
                      {cat} - {CATEGORY_NAMES[cat]}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="new_expected_verdict">Expected Verdict</Label>
              <Select
                value={newQuestion.expected_verdict}
                onValueChange={(value) => setNewQuestion({ ...newQuestion, expected_verdict: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select expected verdict" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ACCEPTED">ACCEPTED</SelectItem>
                  <SelectItem value="COMPROMISED">COMPROMISED</SelectItem>
                  <SelectItem value="REFUSED">REFUSED</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="new_content">Question Content</Label>
              <textarea
                id="new_content"
                className="w-full min-h-[200px] p-3 border rounded-md bg-background"
                placeholder="Enter the question content..."
                value={newQuestion.content}
                onChange={(e) => setNewQuestion({ ...newQuestion, content: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="new_notes">Notes</Label>
              <textarea
                id="new_notes"
                className="w-full min-h-[100px] p-3 border rounded-md bg-background text-sm"
                placeholder="Add notes about this question's framing, history, or reasoning..."
                value={newQuestion.notes}
                onChange={(e) => setNewQuestion({ ...newQuestion, notes: e.target.value })}
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
                  <Label htmlFor="edit_difficulty">Difficulty</Label>
                  <Select
                    value={editingQuestion.metadata?.difficulty || "medium"}
                    onValueChange={(value) => setEditingQuestion({ 
                      ...editingQuestion, 
                      metadata: { ...editingQuestion.metadata, difficulty: value } 
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="easy">Easy</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="hard">Hard</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
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
                    {CATEGORIES[editingQuestion.tier as 1 | 2 | 3]?.map((cat) => (
                      <SelectItem key={cat} value={cat}>
                        {cat} - {CATEGORY_NAMES[cat]}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="edit_expected_verdict">Expected Verdict</Label>
                <Select
                  value={editingQuestion.expected_verdict || ""}
                  onValueChange={(value) => setEditingQuestion({ 
                    ...editingQuestion, 
                    expected_verdict: value || undefined 
                  })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select expected verdict" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ACCEPTED">ACCEPTED</SelectItem>
                    <SelectItem value="COMPROMISED">COMPROMISED</SelectItem>
                    <SelectItem value="REFUSED">REFUSED</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="edit_content">Question Content</Label>
                <textarea
                  id="edit_content"
                  className="w-full min-h-[200px] p-3 border rounded-md bg-background"
                  value={editingQuestion.content}
                  onChange={(e) => setEditingQuestion({ ...editingQuestion, content: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="edit_notes">Notes</Label>
                <textarea
                  id="edit_notes"
                  className="w-full min-h-[100px] p-3 border rounded-md bg-background text-sm"
                  placeholder="Add notes about this question's framing, history, or reasoning..."
                  value={editingQuestion.notes || ""}
                  onChange={(e) => setEditingQuestion({ ...editingQuestion, notes: e.target.value })}
                />
              </div>
              <div className="flex items-center gap-3 pt-2">
                <input
                  type="checkbox"
                  id="edit_locked"
                  checked={editingQuestion.is_locked}
                  onChange={(e) => setEditingQuestion({ ...editingQuestion, is_locked: e.target.checked })}
                  className="h-4 w-4 rounded border-gray-300"
                />
                <Label htmlFor="edit_locked" className="font-normal cursor-pointer">
                  Mark as locked/accepted
                </Label>
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
      <Dialog open={!!showConfirmDialog} onOpenChange={() => { setShowConfirmDialog(null); setArchiveKeepVisible(false); }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {showConfirmDialog?.action === "delete" ? "Delete Version" :
               showConfirmDialog?.action === "publish" ? "Publish Version" :
               showConfirmDialog?.action === "lock" ? "Lock Version" :
               showConfirmDialog?.action === "unlock" ? "Unlock Version" :
               showConfirmDialog?.action === "archive" ? "Archive Version" :
               showConfirmDialog?.action === "toggle_visibility" ? "Change Visibility" : "Confirm Action"}
            </DialogTitle>
            <DialogDescription>
              {showConfirmDialog?.action === "delete" && (
                <>Are you sure you want to delete version {showConfirmDialog.version.semantic_version}? This cannot be undone. Note: Deletion will fail if test runs exist for this version.</>
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
                <div className="space-y-4">
                  <p>Are you sure you want to archive version {showConfirmDialog.version.semantic_version}?</p>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="keep_visible"
                      checked={archiveKeepVisible}
                      onCheckedChange={(checked) => setArchiveKeepVisible(checked === true)}
                    />
                    <label
                      htmlFor="keep_visible"
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      Keep publicly visible after archiving
                    </label>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {archiveKeepVisible
                      ? "The version will still appear in the public API."
                      : "The version will be hidden from the public API."}
                  </p>
                </div>
              )}
              {showConfirmDialog?.action === "toggle_visibility" && (
                showConfirmDialog.version.is_publicly_visible
                  ? <>Are you sure you want to hide version {showConfirmDialog.version.semantic_version}? It will no longer appear in the public API.</>
                  : <>Are you sure you want to make version {showConfirmDialog.version.semantic_version} publicly visible? It will appear in the public API alongside the active version.</>
              )}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setShowConfirmDialog(null); setArchiveKeepVisible(false); }}>
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
        <DialogContent className="sm:max-w-3xl">
          <DialogHeader>
            <DialogTitle>Import Questions</DialogTitle>
            <DialogDescription>
              Import questions from a CSV or JSON file into {selectedVersion?.semantic_version || 'the selected version'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
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
            </div>

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
                      Unable to parse file.
                    </p>
                  ) : (
                    <>
                      <div className="grid grid-cols-4 gap-3 text-sm">
                        <div className="text-center p-3 bg-muted rounded">
                          <div className="text-2xl font-bold">{importPreview.stats.total}</div>
                          <div className="text-muted-foreground text-xs">Total</div>
                        </div>
                        <div className="text-center p-3 bg-muted rounded">
                          <div className="text-2xl font-bold">{importPreview.stats.tier1}</div>
                          <div className="text-muted-foreground text-xs">Tier 1</div>
                        </div>
                        <div className="text-center p-3 bg-muted rounded">
                          <div className="text-2xl font-bold">{importPreview.stats.tier2}</div>
                          <div className="text-muted-foreground text-xs">Tier 2</div>
                        </div>
                        <div className="text-center p-3 bg-muted rounded">
                          <div className="text-2xl font-bold">{importPreview.stats.tier3}</div>
                          <div className="text-muted-foreground text-xs">Tier 3</div>
                        </div>
                      </div>
                    </>
                  )}
                </div>

                {importValidation && (
                  <div className={`p-4 border rounded-lg ${importValidation.errors.length > 0 ? 'border-orange-500' : 'border-green-500'}`}>
                    <h4 className="font-medium mb-2">
                      {importValidation.errors.length === 0 ? 'Validation Passed' : 'Validation Issues'}
                    </h4>
                    <p className="text-sm">
                      {importValidation.imported} questions ready to import
                    </p>
                    {importValidation.errors.length > 0 && (
                      <div className="mt-2 max-h-24 overflow-y-auto">
                        {importValidation.errors.slice(0, 5).map((err, idx) => (
                          <p key={idx} className="text-xs text-destructive">{err}</p>
                        ))}
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

      {/* Set Target Dialog */}
      <Dialog open={showTargetDialog} onOpenChange={setShowTargetDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Set Question Target</DialogTitle>
            <DialogDescription>
              Set a target question count for version {targetVersion?.semantic_version}.
              Leave blank for automatic calculation based on current questions.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <div>
              <Label htmlFor="target-count">Target Question Count</Label>
              <Input
                id="target-count"
                type="number"
                placeholder="e.g., 200 or 300"
                value={editTargetValue}
                onChange={(e) => setEditTargetValue(e.target.value)}
                className="mt-1"
              />
              <p className="text-xs text-muted-foreground mt-2">
                Leave blank to calculate targets from actual question count
              </p>
            </div>
            <div className="bg-muted p-4 rounded-lg space-y-2">
              <div className="flex justify-between">
                <span>Current Questions:</span>
                <span className="font-medium">{targetVersion?.question_count || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Current Target:</span>
                <span className="font-medium">
                  {targetVersion?.target_question_count ? targetVersion.target_question_count : "Auto"}
                </span>
              </div>
              {editTargetValue && parseInt(editTargetValue) > 0 && (
                <>
                  <hr className="my-2 border-muted-foreground/20" />
                  <div className="flex justify-between text-sm">
                    <span>Tier 1 target (70%):</span>
                    <span>{Math.round(parseInt(editTargetValue) * 0.7)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Tier 2 target (20%):</span>
                    <span>{Math.round(parseInt(editTargetValue) * 0.2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Tier 3 target (10%):</span>
                    <span>{Math.round(parseInt(editTargetValue) * 0.1)}</span>
                  </div>
                </>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setShowTargetDialog(false);
              setEditTargetValue("");
            }} disabled={targetLoading}>
              Cancel
            </Button>
            <Button
              onClick={handleUpdateTarget}
              disabled={targetLoading}
            >
              {targetLoading ? "Updating..." : "Update Target"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
