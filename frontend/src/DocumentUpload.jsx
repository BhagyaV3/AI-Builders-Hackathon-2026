import React, { useState } from "react";
import { extractFormAI, fetchGuidedQuestions } from "./api";

const SAMPLE_DOCUMENTS = [
  {
    name: "State Assistance & Benefit Application",
    text: `STATE HOUSING AND NUTRITION ASSISTANCE APPLICATION

Section 1: Applicant Details
Full legal name is required for all applicants.
Date of birth must be provided.
Email address is required for digital notifications.
Contact phone number is required.
Mailing address must be provided.
Monthly gross income must be stated under penalty of perjury.
Applicant signature is required to certify statements.

Section 2: Conditional Requirements & Exceptions
If the applicant is under 18 years of age, a parent or guardian signature is required.
Applicants with monthly income exceeding $5,000 must attach federal tax return schedule C.
Fee waiver is available for households with zero income.

Section 3: Deadlines & Attachments
All application materials must be submitted by March 31, 2026.
Applicants must attach recent pay stubs verifying income.
A valid government photo ID is required.`,
  },
  {
    name: "Youth Academic Scholarship Form",
    text: `FOUNDATION MERIT SCHOLARSHIP APPLICATION

Applicant legal name is required.
Date of birth must be provided.
Email address is required.
Cumulative GPA or academic score must be entered.
Mailing address is mandatory.
If the applicant is under 18, parent or guardian signature is mandatory.
Submit all records before April 15, 2026.
Official academic transcript must be attached.`,
  },
];

export default function DocumentUpload({ onExtractionComplete }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [pastedText, setPastedText] = useState(SAMPLE_DOCUMENTS[0].text);
  const [selectedMode, setSelectedMode] = useState("simple_language");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [extractedData, setExtractedData] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setPastedText("");
      setError("");
    }
  };

  const handleSelectSample = (sample) => {
    setSelectedFile(null);
    setPastedText(sample.text);
    setExtractedData(null);
    setError("");
  };

  const handleExtract = async () => {
    if (!selectedFile && !pastedText.trim()) {
      setError("Please select a file or paste document text to analyze.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const data = await extractFormAI({
        file: selectedFile,
        documentText: pastedText.trim() || undefined,
      });
      setExtractedData(data);
    } catch (err) {
      console.error(err);
      setError("Failed to extract form with AI. Please ensure the backend server is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleStartGuidedQA = async () => {
    if (!extractedData) return;

    setLoading(true);
    try {
      const qaResponse = await fetchGuidedQuestions({
        fields: extractedData.fields,
        rules: extractedData.rules,
        mode: selectedMode,
      });

      // Map generated questions to the GuidedQA format
      const formattedQuestions = qaResponse.questions.map((q) => ({
        id: `q_${q.step_number}`,
        fieldKey: q.field_name,
        questionText: q.question_text,
        simplifiedText: q.question_text,
        helpText: q.explanation,
        type: q.input_type === "number" ? "number" : q.input_type === "tel" ? "tel" : "text",
        required: q.required,
        citation: q.citation,
        label: q.label,
        accessibilityMode: q.accessibility_mode,
      }));

      onExtractionComplete({
        sourceText: pastedText || selectedFile?.name || "Uploaded Document",
        extractionData: extractedData,
        questions: formattedQuestions,
        mode: selectedMode,
      });
    } catch (err) {
      console.error(err);
      setError("Failed to generate guided questions. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card floating-card">
      <h2>Transform a Dense Form into Guided Assistance</h2>
      <p style={{ opacity: 0.8, marginBottom: "1.5rem" }}>
        Upload an official form (PDF / TXT) or choose a sample document. AccessBridge extracts requirements, deadlines, and conditions into an accessible, citation-backed workflow.
      </p>

      {/* Preset Buttons */}
      <div style={{ marginBottom: "1rem" }}>
        <span style={{ fontSize: "0.9rem", fontWeight: "bold", marginRight: "0.5rem" }}>Sample Forms:</span>
        {SAMPLE_DOCUMENTS.map((sample, idx) => (
          <button
            key={idx}
            className="btn btn-outline"
            style={{ marginRight: "0.5rem", marginBottom: "0.5rem", fontSize: "0.85rem", padding: "0.35rem 0.75rem" }}
            onClick={() => handleSelectSample(sample)}
          >
            📄 {sample.name}
          </button>
        ))}
      </div>

      {/* File Upload & Text Area */}
      <div style={{ marginBottom: "1.5rem" }}>
        <label style={{ display: "block", fontWeight: "bold", marginBottom: "0.5rem" }}>
          Upload PDF or Text Document
        </label>
        <input
          type="file"
          accept=".pdf,.txt"
          onChange={handleFileChange}
          style={{ marginBottom: "1rem", display: "block" }}
        />

        <label style={{ display: "block", fontWeight: "bold", marginBottom: "0.5rem" }}>
          Or Paste Form Text Directly
        </label>
        <textarea
          rows={7}
          value={pastedText}
          onChange={(e) => {
            setPastedText(e.target.value);
            setSelectedFile(null);
          }}
          placeholder="Paste dense form instructions, rules, or requirements here..."
          style={{
            width: "100%",
            padding: "0.75rem",
            borderRadius: "8px",
            border: "1px solid var(--border-color, #ccc)",
            fontFamily: "inherit",
            fontSize: "0.9rem",
            resize: "vertical",
          }}
        />
      </div>

      {/* Error Message */}
      {error && (
        <div style={{ color: "#d9534f", marginBottom: "1rem", padding: "0.5rem", background: "#fdf2f2", borderRadius: "4px" }}>
          ⚠️ {error}
        </div>
      )}

      {/* Extract Button */}
      {!extractedData && (
        <button
          className="btn btn-primary"
          onClick={handleExtract}
          disabled={loading}
          style={{ width: "100%", padding: "0.75rem", fontSize: "1rem" }}
        >
          {loading ? "Analyzing Document with AI..." : "🔍 Analyze Form with AI"}
        </button>
      )}

      {/* Extraction Results Breakdown */}
      {extractedData && (
        <div style={{ marginTop: "1.5rem", borderTop: "2px dashed var(--border-color, #eee)", paddingTop: "1rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h3 style={{ margin: 0 }}>✨ AI Extraction Breakdown</h3>
            <span style={{ background: "#e8f5e9", color: "#2e7d32", padding: "0.25rem 0.75rem", borderRadius: "12px", fontSize: "0.85rem", fontWeight: "bold" }}>
              {(extractedData.confidence * 100).toFixed(0)}% Confidence
            </span>
          </div>

          <p style={{ fontStyle: "italic", opacity: 0.85, margin: "0.5rem 0" }}>
            {extractedData.summary}
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", margin: "1rem 0" }}>
            <div style={{ background: "rgba(0,0,0,0.03)", padding: "0.75rem", borderRadius: "6px" }}>
              <strong>📋 Detected Fields ({extractedData.fields.length})</strong>
              <ul style={{ paddingLeft: "1.2rem", margin: "0.5rem 0 0", fontSize: "0.85rem" }}>
                {extractedData.fields.slice(0, 4).map((f, i) => (
                  <li key={i}>{f.label} {f.required && <span style={{ color: "#d9534f" }}>*</span>}</li>
                ))}
                {extractedData.fields.length > 4 && <li>+{extractedData.fields.length - 4} more...</li>}
              </ul>
            </div>

            <div style={{ background: "rgba(0,0,0,0.03)", padding: "0.75rem", borderRadius: "6px" }}>
              <strong>⚖️ Rules & Conditions ({extractedData.rules.length})</strong>
              <ul style={{ paddingLeft: "1.2rem", margin: "0.5rem 0 0", fontSize: "0.85rem" }}>
                {extractedData.rules.slice(0, 2).map((r, i) => (
                  <li key={i}>{r.text.slice(0, 60)}...</li>
                ))}
              </ul>
            </div>

            <div style={{ background: "rgba(0,0,0,0.03)", padding: "0.75rem", borderRadius: "6px" }}>
              <strong>⏰ Deadlines & Proofs</strong>
              <div style={{ fontSize: "0.85rem", marginTop: "0.5rem" }}>
                {extractedData.deadlines.length > 0 && (
                  <div>Due: <strong>{extractedData.deadlines[0].due_date || extractedData.deadlines[0].text.slice(0, 40)}</strong></div>
                )}
                {extractedData.required_attachments.length > 0 && (
                  <div style={{ marginTop: "0.25rem" }}>
                    Required Proofs: {extractedData.required_attachments.map((a) => a.name).join(", ")}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Accessibility Mode Selector */}
          <div style={{ margin: "1.5rem 0", background: "#f0f7ff", padding: "1rem", borderRadius: "8px", border: "1px solid #cce5ff" }}>
            <label style={{ display: "block", fontWeight: "bold", marginBottom: "0.5rem", color: "#004085" }}>
              Choose Accessibility Preset:
            </label>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "0.5rem" }}>
              {[
                { key: "simple_language", label: "🌟 Simple Language", desc: "Everyday words, 5th-grade level" },
                { key: "reduced_cognitive_load", label: "🎯 Low Cognitive Load", desc: "Minimalist, bite-sized steps" },
                { key: "screen_reader", label: "🔊 Screen Reader", desc: "Explicit semantic descriptions" },
                { key: "standard", label: "📜 Standard Legal", desc: "Official legal wording" },
              ].map((preset) => (
                <button
                  key={preset.key}
                  type="button"
                  onClick={() => setSelectedMode(preset.key)}
                  style={{
                    padding: "0.5rem",
                    borderRadius: "6px",
                    border: selectedMode === preset.key ? "2px solid #0056b3" : "1px solid #b8daff",
                    background: selectedMode === preset.key ? "#0056b3" : "#ffffff",
                    color: selectedMode === preset.key ? "#ffffff" : "#004085",
                    cursor: "pointer",
                    textAlign: "left",
                    fontSize: "0.85rem",
                  }}
                >
                  <div style={{ fontWeight: "bold" }}>{preset.label}</div>
                  <div style={{ fontSize: "0.75rem", opacity: 0.9 }}>{preset.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Button to proceed to guided questionnaire */}
          <button
            className="btn btn-primary"
            onClick={handleStartGuidedQA}
            disabled={loading}
            style={{ width: "100%", padding: "0.75rem", fontSize: "1.05rem" }}
          >
            {loading ? "Generating Guided Flow..." : "🚀 Begin Guided Form Assistant"}
          </button>
        </div>
      )}
    </div>
  );
}
