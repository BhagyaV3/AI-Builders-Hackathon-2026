import React, { useMemo, useState } from "react";
import "./App.css";
import AccessibilityToolbar from "./AccessibilityToolbar";
import GuidedQA from "./GuidedQA";
import ReviewScreen from "./ReviewScreen";
import { mockQuestions } from "./mockFormData";

const DEFAULT_SOURCE_TEXT = `Application Form
Applicant name is required.
Monthly income must be provided.
Submit by March 15.
If the applicant is under 18, a parent signature is required.`;

function inferQuestionType(field) {
  const label = `${field.label || ""} ${field.name || ""}`.toLowerCase();

  if (label.includes("email")) return "email";
  if (label.includes("phone") || label.includes("contact")) return "tel";
  if (label.includes("date") || label.includes("deadline") || label.includes("dob")) return "date";
  if (label.includes("income") || label.includes("score") || label.includes("amount") || label.includes("age")) {
    return "number";
  }

  return "text";
}

function fieldLabelToQuestion(field) {
  const label = (field.label || field.name || "this field").trim();
  return field.required ? `Please provide ${label.toLowerCase()}.` : `Enter ${label.toLowerCase()}.`;
}

function buildQuestionsFromExtraction(extraction) {
  if (!extraction || !Array.isArray(extraction.fields) || extraction.fields.length === 0) {
    return mockQuestions;
  }

  return extraction.fields.map((field, index) => ({
    id: field.name || `field-${index}`,
    fieldKey: field.name || `field_${index}`,
    questionText: fieldLabelToQuestion(field),
    simplifiedText: field.label || field.name || "Field",
    helpText: field.required ? "This field is required." : "This field is optional.",
    sourceExcerpt: field.source_excerpt || extraction.summary || "Extracted from the source document.",
    type: inferQuestionType(field),
    placeholder: field.value || "",
    required: Boolean(field.required),
  }));
}

export default function App() {
  const [step, setStep] = useState("qa");
  const [userAnswers, setUserAnswers] = useState({});
  const [targetQuestionIndex, setTargetQuestionIndex] = useState(0);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [sourceText, setSourceText] = useState(DEFAULT_SOURCE_TEXT);
  const [analysis, setAnalysis] = useState(null);
  const [analysisError, setAnalysisError] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileInputKey, setFileInputKey] = useState(0);

  const questions = useMemo(() => buildQuestionsFromExtraction(analysis), [analysis]);

  const handleEditQuestion = (index) => {
    setTargetQuestionIndex(index);
    setStep("qa");
  };

  const handleFinalSubmit = () => {
    setShowSuccessModal(true);
  };

  const handleAnalyzeSource = async () => {
    const trimmedText = sourceText.trim();
    if (!selectedFile && !trimmedText) {
      setAnalysisError("Paste or type some form text before analyzing.");
      return;
    }

    setIsAnalyzing(true);
    setAnalysisError("");

    try {
      const formData = new FormData();
      if (selectedFile) {
        formData.append("file", selectedFile);
      } else {
        formData.append("document_text", trimmedText);
      }

      const response = await fetch("/api/forms/process", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const payload = await response.json();
      setAnalysis(payload);
      setUserAnswers({});
      setTargetQuestionIndex(0);
      setStep("qa");
    } catch (error) {
      setAnalysis(null);
      setAnalysisError(
        error instanceof Error
          ? error.message
          : "Unable to analyze the document right now. Using the demo questions instead."
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>AccessBridge Form Assistant</h1>
      </header>

      <AccessibilityToolbar />

      <div className="card" style={{ marginBottom: "1rem" }}>
        <h2 style={{ marginTop: 0 }}>Source document</h2>
        <p style={{ opacity: 0.8, marginTop: 0 }}>
          Paste a form or policy excerpt, analyze it, and the app will turn the extracted fields into guided questions.
        </p>
        <textarea
          value={sourceText}
          onChange={(event) => setSourceText(event.target.value)}
          rows={7}
          className="form-input"
          style={{ resize: "vertical", minHeight: "150px" }}
          aria-label="Source form text"
        />
        <div style={{ marginTop: "0.85rem" }}>
          <label style={{ display: "block", marginBottom: "0.4rem", fontWeight: 600 }}>
            Or upload a file
          </label>
          <input
            key={fileInputKey}
            type="file"
            accept=".pdf,.txt,.html,.htm,.docx"
            onChange={(event) => setSelectedFile(event.target.files && event.target.files[0] ? event.target.files[0] : null)}
          />
          {selectedFile && (
            <div style={{ marginTop: "0.45rem", fontSize: "0.92rem", opacity: 0.85 }}>
              Selected file: {selectedFile.name}
            </div>
          )}
        </div>
        <div className="button-group" style={{ marginTop: "1rem", alignItems: "center" }}>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleAnalyzeSource}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? "Analyzing..." : "Analyze form"}
          </button>
          <button
            type="button"
            className="btn btn-outline"
            onClick={() => {
              setSourceText(DEFAULT_SOURCE_TEXT);
              setSelectedFile(null);
              setFileInputKey((value) => value + 1);
              setAnalysis(null);
              setAnalysisError("");
              setUserAnswers({});
              setTargetQuestionIndex(0);
              setStep("qa");
            }}
          >
            Reset sample
          </button>
        </div>
        {analysisError && <div className="error-message" role="alert">{analysisError}</div>}
        {analysis && (
          <div style={{ marginTop: "1rem", display: "grid", gap: "0.75rem" }}>
            <div><strong>Title:</strong> {analysis.title}</div>
            <div><strong>Summary:</strong> {analysis.summary}</div>
            <div><strong>Confidence:</strong> {Math.round((analysis.confidence || 0) * 100)}%</div>
            {analysis.file_name && <div><strong>File:</strong> {analysis.file_name}</div>}
          </div>
        )}
      </div>

      {step === "qa" && (
        <GuidedQA
          questions={questions}
          initialAnswers={userAnswers}
          initialIndex={targetQuestionIndex}
          onComplete={(answers) => {
            setUserAnswers(answers);
            setStep("review");
          }}
        />
      )}

      {step === "review" && (
        <ReviewScreen
          questions={questions}
          answers={userAnswers}
          analysis={analysis}
          onEdit={handleEditQuestion}
          onSubmit={handleFinalSubmit}
        />
      )}

      {/* Styled Large Submission Modal */}
      {showSuccessModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <span style={{ fontSize: "3rem" }}>✅</span>
            <h2>Form Submitted Successfully!</h2>
            <p>Your responses have been saved and sent to the application pipeline.</p>
            <button 
              className="btn btn-primary" 
              style={{ marginTop: "1rem" }}
              onClick={() => {
                setShowSuccessModal(false);
                setStep("qa");
                setTargetQuestionIndex(0);
                setUserAnswers({});
              }}
            >
              Start New Form
            </button>
          </div>
        </div>
      )}
    </div>
  );
}