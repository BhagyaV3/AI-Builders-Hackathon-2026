import React, { useState, useEffect } from "react";
import { verifyFidelityAI, validateAnswersAI } from "./api";

export default function ReviewScreen({
  questions = [],
  answers = {},
  extractionData = null,
  sourceText = "",
  onEdit,
  onSubmit,
}) {
  const [fidelityReport, setFidelityReport] = useState(null);
  const [validationReport, setValidationReport] = useState(null);
  const [loadingFidelity, setLoadingFidelity] = useState(false);
  const [showFidelityDetails, setShowFidelityDetails] = useState(false);

  useEffect(() => {
    // Run AI Fidelity Verification & Answer Validation if extractionData exists
    async function runVerification() {
      if (!extractionData) return;

      setLoadingFidelity(true);
      try {
        const [fidelity, validation] = await Promise.all([
          verifyFidelityAI({
            sourceText: sourceText || "Sample Document Text",
            extractedFields: extractionData.fields || [],
            extractedRules: extractionData.rules || [],
            extractedDeadlines: extractionData.deadlines || [],
            extractedExceptions: extractionData.exceptions || [],
          }),
          validateAnswersAI({
            fields: extractionData.fields || [],
            rules: extractionData.rules || [],
            deadlines: extractionData.deadlines || [],
            userAnswers: answers,
          }),
        ]);
        setFidelityReport(fidelity);
        setValidationReport(validation);
      } catch (err) {
        console.error("AI Verification check failed:", err);
      } finally {
        setLoadingFidelity(false);
      }
    }

    runVerification();
  }, [extractionData, sourceText, answers]);

  const canSubmit = validationReport ? validationReport.can_submit : true;

  return (
    <div className="card floating-card">
      <h2>Review Your Responses</h2>
      <p style={{ opacity: 0.8 }}>
        Please verify your details and review the automated fidelity check before final submission.
      </p>

      {/* AI Fidelity & Source Citations Panel (Issue 6) */}
      <div
        style={{
          margin: "1.5rem 0",
          padding: "1rem",
          borderRadius: "8px",
          border: "1px solid var(--border-color, #e2e8f0)",
          background: "rgba(99, 102, 241, 0.04)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h3 style={{ margin: 0, display: "flex", alignItems: "center", gap: "0.5rem" }}>
              🛡️ AI Fidelity & Trust Score
            </h3>
            <span style={{ fontSize: "0.85rem", opacity: 0.8 }}>
              Automated verifier pass comparing draft requirements against source document
            </span>
          </div>

          {loadingFidelity ? (
            <span style={{ fontSize: "0.85rem", color: "#6366f1" }}>Verifying source text...</span>
          ) : fidelityReport ? (
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "0.4rem",
                padding: "0.35rem 0.75rem",
                borderRadius: "20px",
                background: fidelityReport.overall_fidelity_score >= 0.8 ? "#e8f5e9" : "#fff3e0",
                color: fidelityReport.overall_fidelity_score >= 0.8 ? "#2e7d32" : "#e65100",
                fontWeight: "bold",
                fontSize: "0.95rem",
              }}
            >
              <span>{(fidelityReport.overall_fidelity_score * 100).toFixed(0)}% Fidelity</span>
            </div>
          ) : null}
        </div>

        {/* Fidelity Warnings */}
        {fidelityReport && fidelityReport.fidelity_warnings && fidelityReport.fidelity_warnings.length > 0 && (
          <div style={{ marginTop: "0.75rem", padding: "0.5rem", background: "#fff8e1", borderRadius: "6px", fontSize: "0.85rem", color: "#8d6e63" }}>
            <strong>Notice: </strong> {fidelityReport.fidelity_warnings.join(" ")}
          </div>
        )}

        {/* Toggle Detailed Checks */}
        {fidelityReport && (
          <div style={{ marginTop: "0.75rem" }}>
            <button
              type="button"
              className="btn btn-outline"
              style={{ fontSize: "0.8rem", padding: "0.25rem 0.5rem" }}
              onClick={() => setShowFidelityDetails(!showFidelityDetails)}
            >
              {showFidelityDetails ? "Hide Source Citations" : `View ${fidelityReport.total_checks} Source Citations & Checks`}
            </button>

            {showFidelityDetails && (
              <div style={{ marginTop: "0.75rem", maxHeight: "250px", overflowY: "auto", fontSize: "0.82rem" }}>
                {fidelityReport.checks.map((check, i) => (
                  <div
                    key={i}
                    style={{
                      padding: "0.4rem 0",
                      borderBottom: "1px solid rgba(0,0,0,0.06)",
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.2rem",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <strong>{check.claim_text}</strong>
                      <span
                        style={{
                          textTransform: "uppercase",
                          fontSize: "0.7rem",
                          fontWeight: "bold",
                          color: check.status === "verified" ? "#2e7d32" : "#d9534f",
                        }}
                      >
                        {check.status}
                      </span>
                    </div>
                    {check.source_citation && (
                      <em style={{ color: "#64748b" }}>Source: "{check.source_citation.quote}"</em>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* AI Validation Status (Issue 4) */}
      {validationReport && (
        <div
          style={{
            marginBottom: "1.5rem",
            padding: "0.75rem",
            borderRadius: "6px",
            background: validationReport.can_submit ? "#f0fdf4" : "#fef2f2",
            border: validationReport.can_submit ? "1px solid #bbf7d0" : "1px solid #fecaca",
          }}
        >
          <strong>{validationReport.can_submit ? "✅ Ready for Submission" : "⚠️ Attention Required"}</strong>
          <div style={{ fontSize: "0.85rem", marginTop: "0.25rem" }}>{validationReport.summary_message}</div>

          {validationReport.issues && validationReport.issues.length > 0 && (
            <ul style={{ margin: "0.5rem 0 0", paddingLeft: "1.2rem", fontSize: "0.85rem" }}>
              {validationReport.issues.map((iss, idx) => (
                <li key={idx} style={{ color: iss.severity === "error" ? "#dc2626" : "#d97706" }}>
                  <strong>{iss.message}</strong> — {iss.correction_prompt}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Answers List */}
      <div style={{ margin: "1.5rem 0" }}>
        <h3>Your Recorded Responses</h3>
        {questions.map((q, idx) => (
          <div
            key={q.fieldKey || idx}
            style={{
              padding: "0.75rem 0",
              borderBottom: "1px solid var(--border-color, #eee)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <div>
              <strong>{q.questionText}</strong>
              <div style={{ marginTop: "0.25rem", color: answers[q.fieldKey] ? "inherit" : "#94a3b8" }}>
                {answers[q.fieldKey] || <em>Not provided</em>}
              </div>
              {q.citation && q.citation.quote && (
                <div style={{ fontSize: "0.75rem", color: "#6366f1", marginTop: "0.2rem" }}>
                  📌 Source: <em>"{q.citation.quote.slice(0, 80)}..."</em>
                </div>
              )}
            </div>
            {onEdit && (
              <button className="btn btn-outline" style={{ fontSize: "0.85rem" }} onClick={() => onEdit(idx)}>
                Edit
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="button-group">
        {onEdit && (
          <button className="btn btn-secondary" onClick={() => onEdit(0)}>
            Back to Questions
          </button>
        )}
        <button
          className="btn btn-primary"
          onClick={onSubmit}
          disabled={!canSubmit}
          style={{ opacity: canSubmit ? 1 : 0.6 }}
        >
          Confirm & Submit Application
        </button>
      </div>
    </div>
  );
}