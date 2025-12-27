import { auth } from "@/auth";
import { NextResponse } from "next/server";
import * as jose from "jose";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getBackendToken() {
  const session = await auth();
  if (!session) return null;

  const secret = new TextEncoder().encode(process.env.NEXTAUTH_SECRET!);
  const token = await new jose.SignJWT({
    sub: session.user?.id,
    email: session.user?.email,
    name: session.user?.name,
  })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("1h")
    .sign(secret);

  return token;
}

interface QuestionFromFile {
  content: string;
  category: string;
  tier: number;
  difficulty?: string;
  expected_verdict?: string;
}

interface QuestionsFile {
  tier1_questions?: QuestionFromFile[];
  tier2_questions?: QuestionFromFile[];
  tier3_questions?: QuestionFromFile[];
}

interface ParsedQuestion {
  question_set_id: string;
  tier: number;
  category: string;
  content: string;
  metadata?: Record<string, unknown>;
}

interface ValidationError {
  row: number;
  field: string;
  message: string;
}

/**
 * Parse CSV content into rows and columns
 * Handles quoted fields, commas within quotes, and escaped quotes
 */
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
        // Escaped quote
        currentLine += '"';
        i++; // Skip next quote
      } else {
        inQuotes = !inQuotes;
        currentLine += char;
      }
    } else if ((char === "\n" || (char === "\r" && nextChar === "\n")) && !inQuotes) {
      if (currentLine.trim()) {
        lines.push(currentLine);
      }
      currentLine = "";
      if (char === "\r") i++; // Skip \n in \r\n
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

  // Parse each line into fields
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

/**
 * Infer tier from category code
 * 3.x -> Tier 1, 4.x -> Tier 2, 5.x -> Tier 3
 */
function inferTierFromCategory(category: string): number | null {
  const majorCategory = category.split(".")[0];
  switch (majorCategory) {
    case "3":
      return 1;
    case "4":
      return 2;
    case "5":
      return 3;
    default:
      return null;
  }
}


/**
 * Parse CSV rows into questions
 */
function parseCSVQuestions(
  headers: string[],
  rows: string[][],
  questionSetId: string
): { questions: ParsedQuestion[]; errors: ValidationError[] } {
  const questions: ParsedQuestion[] = [];
  const errors: ValidationError[] = [];

  // Map header names to indices
  const headerIndex: Record<string, number> = {};
  headers.forEach((header, index) => {
    headerIndex[header] = index;
  });

  // Required field check
  if (!("content" in headerIndex)) {
    errors.push({ row: 0, field: "content", message: "Missing required 'content' column" });
    return { questions, errors };
  }

  for (let rowIndex = 0; rowIndex < rows.length; rowIndex++) {
    const row = rows[rowIndex];
    const rowNum = rowIndex + 2; // +2 for 1-indexed and header row

    // Skip empty rows
    if (row.every((cell) => !cell || cell.trim() === "")) {
      continue;
    }

    const getValue = (field: string): string | undefined => {
      const idx = headerIndex[field];
      return idx !== undefined ? row[idx]?.trim() : undefined;
    };

    // Get content (required)
    const content = getValue("content");
    if (!content) {
      errors.push({ row: rowNum, field: "content", message: "Missing content" });
      continue;
    }

    // Get category (required)
    const category = getValue("category");
    if (!category) {
      errors.push({ row: rowNum, field: "category", message: "Missing category" });
      continue;
    }

    // Get tier (from column or infer from category)
    let tier: number;
    const tierValue = getValue("tier");
    if (tierValue) {
      tier = parseInt(tierValue, 10);
      if (isNaN(tier) || tier < 1 || tier > 3) {
        errors.push({ row: rowNum, field: "tier", message: `Invalid tier value: ${tierValue}` });
        continue;
      }
    } else {
      const inferredTier = inferTierFromCategory(category);
      if (inferredTier === null) {
        errors.push({
          row: rowNum,
          field: "tier",
          message: `Cannot infer tier from category: ${category}`,
        });
        continue;
      }
      tier = inferredTier;
    }

    // Build metadata from optional fields
    const metadata: Record<string, unknown> = {};

    const difficulty = getValue("difficulty");
    if (difficulty) metadata.difficulty = difficulty.toLowerCase();

    const expectedVerdict = getValue("expected_verdict");
    if (expectedVerdict) metadata.expected_verdict = expectedVerdict.toUpperCase();

    questions.push({
      question_set_id: questionSetId,
      tier,
      category,
      content,
      metadata: Object.keys(metadata).length > 0 ? metadata : undefined,
    });
  }

  return { questions, errors };
}

/**
 * Parse JSON questions (existing format)
 */
function parseJSONQuestions(
  data: QuestionsFile,
  questionSetId: string
): { questions: ParsedQuestion[]; errors: ValidationError[] } {
  const questions: ParsedQuestion[] = [];
  const errors: ValidationError[] = [];

  const processQuestions = (items: QuestionFromFile[] | undefined, tier: number) => {
    if (!items) return;
    for (let i = 0; i < items.length; i++) {
      const q = items[i];
      if (!q.content) {
        errors.push({ row: i + 1, field: "content", message: `Tier ${tier}: Missing content` });
        continue;
      }
      if (!q.category) {
        errors.push({ row: i + 1, field: "category", message: `Tier ${tier}: Missing category` });
        continue;
      }

      questions.push({
        question_set_id: questionSetId,
        tier,
        category: q.category,
        content: q.content,
        metadata: {
          difficulty: q.difficulty,
          expected_verdict: q.expected_verdict,
        },
      });
    }
  };

  processQuestions(data.tier1_questions, 1);
  processQuestions(data.tier2_questions, 2);
  processQuestions(data.tier3_questions, 3);

  return { questions, errors };
}

/**
 * Detect file type from filename or content
 */
function detectFileType(filename: string, content: string): "csv" | "json" {
  // Check extension first
  if (filename.toLowerCase().endsWith(".csv")) return "csv";
  if (filename.toLowerCase().endsWith(".json")) return "json";

  // Try to detect from content
  const trimmed = content.trim();
  if (trimmed.startsWith("{") || trimmed.startsWith("[")) return "json";

  return "csv"; // Default to CSV
}

export async function POST(request: Request) {
  const token = await getBackendToken();
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  try {
    const formData = await request.formData();
    const file = formData.get("file") as File;
    const questionSetIdParam = formData.get("question_set_id") as string | null;
    const dryRunParam = formData.get("dry_run") as string | null;
    const dryRun = dryRunParam === "true";

    if (!file) {
      return NextResponse.json({ error: "No file provided" }, { status: 400 });
    }

    // Read file content
    const fileContent = await file.text();
    const fileType = detectFileType(file.name, fileContent);

    // Determine question set ID
    let questionSetId: string;

    if (questionSetIdParam) {
      // Use provided question set ID
      questionSetId = questionSetIdParam;

      // Verify the question set exists
      const verifyResponse = await fetch(`${API_URL}/api/admin/question-sets`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (verifyResponse.ok) {
        const setsData = await verifyResponse.json();
        const exists = setsData.items?.some(
          (v: { id: string }) => v.id === questionSetId
        );
        if (!exists) {
          return NextResponse.json(
            { error: "Question set not found" },
            { status: 404 }
          );
        }
      }
    } else {
      // Auto-select or create question set (existing behavior)
      const setsResponse = await fetch(`${API_URL}/api/admin/question-sets`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (setsResponse.ok) {
        const setsData = await setsResponse.json();
        if (setsData.items && setsData.items.length > 0) {
          const draftSet = setsData.items.find(
            (v: { status: string }) => v.status === "draft"
          );
          questionSetId = draftSet?.id || setsData.items[0].id;
        } else {
          // Create a new question set
          const createResponse = await fetch(`${API_URL}/api/admin/question-sets`, {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              semantic_version: "1.0",
              marketing_version: "Version 1",
              notes: "Initial question set import",
            }),
          });

          if (!createResponse.ok) {
            const error = await createResponse.json().catch(() => ({
              detail: "Failed to create question set",
            }));
            return NextResponse.json(
              { error: error.detail || "Failed to create question set" },
              { status: createResponse.status }
            );
          }

          const newSet = await createResponse.json();
          questionSetId = newSet.id;
        }
      } else {
        // Create a new question set
        const createResponse = await fetch(`${API_URL}/api/admin/question-sets`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            semantic_version: "1.0",
            marketing_version: "Version 1",
            notes: "Initial question set import",
          }),
        });

        if (!createResponse.ok) {
          const error = await createResponse.json().catch(() => ({
            detail: "Failed to create question set",
          }));
          return NextResponse.json(
            { error: error.detail || "Failed to create question set" },
            { status: createResponse.status }
          );
        }

        const newSet = await createResponse.json();
        questionSetId = newSet.id;
      }
    }

    // Parse file based on type
    let questions: ParsedQuestion[];
    let parseErrors: ValidationError[];

    if (fileType === "csv") {
      const { headers, rows } = parseCSV(fileContent);

      if (headers.length === 0) {
        return NextResponse.json(
          { error: "CSV file is empty or has no headers" },
          { status: 400 }
        );
      }

      const result = parseCSVQuestions(headers, rows, questionSetId);
      questions = result.questions;
      parseErrors = result.errors;
    } else {
      // JSON parsing
      let questionsData: QuestionsFile;
      try {
        questionsData = JSON.parse(fileContent);
      } catch {
        return NextResponse.json(
          { error: "Invalid JSON file" },
          { status: 400 }
        );
      }

      const result = parseJSONQuestions(questionsData, questionSetId);
      questions = result.questions;
      parseErrors = result.errors;
    }

    // If dry run, return preview without importing
    if (dryRun) {
      // Count by tier and category
      const tierCounts: Record<number, number> = { 1: 0, 2: 0, 3: 0 };
      const categoryCounts: Record<string, number> = {};
      const difficultyCounts: Record<string, number> = {};

      for (const q of questions) {
        tierCounts[q.tier] = (tierCounts[q.tier] || 0) + 1;
        categoryCounts[q.category] = (categoryCounts[q.category] || 0) + 1;
        const difficulty = (q.metadata?.difficulty as string) || "unspecified";
        difficultyCounts[difficulty] = (difficultyCounts[difficulty] || 0) + 1;
      }

      return NextResponse.json({
        dry_run: true,
        file_type: fileType,
        total_questions: questions.length,
        tier_counts: tierCounts,
        category_counts: categoryCounts,
        difficulty_counts: difficultyCounts,
        parse_errors: parseErrors,
        question_set_id: questionSetId,
        sample_questions: questions.slice(0, 3).map((q) => ({
          content: q.content.substring(0, 100) + (q.content.length > 100 ? "..." : ""),
          tier: q.tier,
          category: q.category,
          difficulty: q.metadata?.difficulty,
        })),
      });
    }

    if (questions.length === 0) {
      return NextResponse.json(
        {
          error: "No valid questions found in file",
          parse_errors: parseErrors,
        },
        { status: 400 }
      );
    }

    // Import questions to backend
    const importResponse = await fetch(
      `${API_URL}/api/admin/questions/import`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          questions,
          dry_run: false,
        }),
      }
    );

    if (!importResponse.ok) {
      const error = await importResponse.json().catch(() => ({
        detail: "Import failed",
      }));
      return NextResponse.json(
        { error: error.detail || "Import failed", ...error },
        { status: importResponse.status }
      );
    }

    const result = await importResponse.json();
    return NextResponse.json({
      imported: result.imported,
      errors: result.errors,
      parse_errors: parseErrors,
      question_set_id: questionSetId,
      file_type: fileType,
      message: `Successfully imported ${result.imported} questions from ${fileType.toUpperCase()} file`,
    });
  } catch (error) {
    console.error("Failed to import questions:", error);
    return NextResponse.json(
      { error: "Failed to import questions" },
      { status: 500 }
    );
  }
}
