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
  expected_refusal_type?: string;
  tests_capability?: boolean;
  tests_willingness?: boolean;
  use_case_tags?: string[];
  audience_context?: string;
  ministry_type?: string;
  reasoning?: string;
}

interface QuestionsFile {
  tier1_questions?: QuestionFromFile[];
  tier2_questions?: QuestionFromFile[];
  tier3_questions?: QuestionFromFile[];
}

export async function POST(request: Request) {
  const token = await getBackendToken();
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  try {
    const formData = await request.formData();
    const file = formData.get("file") as File;

    if (!file) {
      return NextResponse.json({ error: "No file provided" }, { status: 400 });
    }

    // Read and parse the file
    const fileContent = await file.text();
    let questionsData: QuestionsFile;

    try {
      questionsData = JSON.parse(fileContent);
    } catch {
      return NextResponse.json(
        { error: "Invalid JSON file" },
        { status: 400 }
      );
    }

    // First, check if a question set exists or create one
    let questionSetId: string;

    // Try to get existing question sets
    const setsResponse = await fetch(`${API_URL}/api/admin/question-sets`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (setsResponse.ok) {
      const setsData = await setsResponse.json();
      if (setsData.items && setsData.items.length > 0) {
        // Use the first draft version, or the first version
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

    // Transform questions to backend format
    const questions: Array<{
      question_set_id: string;
      tier: number;
      category: string;
      content: string;
      metadata?: Record<string, unknown>;
    }> = [];

    // Process tier1 questions
    if (questionsData.tier1_questions) {
      for (const q of questionsData.tier1_questions) {
        questions.push({
          question_set_id: questionSetId,
          tier: 1,
          category: q.category,
          content: q.content,
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
          },
        });
      }
    }

    // Process tier2 questions
    if (questionsData.tier2_questions) {
      for (const q of questionsData.tier2_questions) {
        questions.push({
          question_set_id: questionSetId,
          tier: 2,
          category: q.category,
          content: q.content,
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
          },
        });
      }
    }

    // Process tier3 questions
    if (questionsData.tier3_questions) {
      for (const q of questionsData.tier3_questions) {
        questions.push({
          question_set_id: questionSetId,
          tier: 3,
          category: q.category,
          content: q.content,
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
          },
        });
      }
    }

    if (questions.length === 0) {
      return NextResponse.json(
        { error: "No questions found in file" },
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
      question_set_id: questionSetId,
      message: `Successfully imported ${result.imported} questions`,
    });
  } catch (error) {
    console.error("Failed to import questions:", error);
    return NextResponse.json(
      { error: "Failed to import questions" },
      { status: 500 }
    );
  }
}
