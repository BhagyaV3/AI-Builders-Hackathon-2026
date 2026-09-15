/**
 * API client for AccessBridge backend and AI endpoints
 */

const API_BASE = "/api";

export async function extractFormAI({ file, documentText }) {
  const formData = new FormData();
  if (file) {
    formData.append("file", file);
  }
  if (documentText) {
    formData.append("document_text", documentText);
  }

  const response = await fetch(`${API_BASE}/ai/extract`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`AI Extraction failed (${response.status})`);
  }
  return response.json();
}

export async function fetchGuidedQuestions({ fields, rules, mode = "simple_language" }) {
  const response = await fetch(`${API_BASE}/ai/guided-questions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fields, rules, mode }),
  });

  if (!response.ok) {
    throw new Error(`Guided questions generation failed (${response.status})`);
  }
  return response.json();
}

export async function validateAnswersAI({ fields, rules, deadlines, userAnswers, userContext = {} }) {
  const response = await fetch(`${API_BASE}/ai/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      fields,
      rules: rules || [],
      deadlines: deadlines || [],
      user_answers: userAnswers,
      user_context: userContext,
    }),
  });

  if (!response.ok) {
    throw new Error(`Validation failed (${response.status})`);
  }
  return response.json();
}

export async function verifyFidelityAI({
  sourceText,
  extractedFields,
  extractedRules,
  extractedDeadlines,
  extractedExceptions,
}) {
  const response = await fetch(`${API_BASE}/ai/verify-fidelity`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      source_text: sourceText,
      extracted_fields: extractedFields || [],
      extracted_rules: extractedRules || [],
      extracted_deadlines: extractedDeadlines || [],
      extracted_exceptions: extractedExceptions || [],
    }),
  });

  if (!response.ok) {
    throw new Error(`Fidelity verification failed (${response.status})`);
  }
  return response.json();
}
