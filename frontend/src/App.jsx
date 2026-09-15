import React, { useState } from "react";
import "./App.css";
import AccessibilityToolbar from "./AccessibilityToolbar";
import DocumentUpload from "./DocumentUpload";
import GuidedQA from "./GuidedQA";
import ReviewScreen from "./ReviewScreen";
import { mockQuestions } from "./mockFormData";

export default function App() {
  const [step, setStep] = useState("upload"); // 'upload' | 'qa' | 'review'
  const [questions, setQuestions] = useState(mockQuestions);
  const [extractionData, setExtractionData] = useState(null);
  const [sourceText, setSourceText] = useState("");
  const [userAnswers, setUserAnswers] = useState({});
  const [targetQuestionIndex, setTargetQuestionIndex] = useState(0);
  const [showSuccessModal, setShowSuccessModal] = useState(false);

  const handleExtractionComplete = ({ sourceText, extractionData, questions: generatedQuestions }) => {
    setSourceText(sourceText);
    setExtractionData(extractionData);
    setQuestions(generatedQuestions && generatedQuestions.length > 0 ? generatedQuestions : mockQuestions);
    setUserAnswers({});
    setTargetQuestionIndex(0);
    setStep("qa");
  };

  const handleEditQuestion = (index) => {
    setTargetQuestionIndex(index);
    setStep("qa");
  };

  const handleFinalSubmit = () => {
    setShowSuccessModal(true);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>AccessBridge Form Assistant</h1>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          {step !== "upload" && (
            <button
              className="btn btn-outline"
              style={{ fontSize: "0.85rem", padding: "0.4rem 0.8rem" }}
              onClick={() => setStep("upload")}
            >
              📄 Upload / Select Form
            </button>
          )}
          {step === "review" && (
            <button
              className="btn btn-outline"
              style={{ fontSize: "0.85rem", padding: "0.4rem 0.8rem" }}
              onClick={() => setStep("qa")}
            >
              ✏️ Back to Questions
            </button>
          )}
        </div>
      </header>

      <AccessibilityToolbar />

      {step === "upload" && (
        <DocumentUpload onExtractionComplete={handleExtractionComplete} />
      )}

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
          extractionData={extractionData}
          sourceText={sourceText}
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
            <p>Your responses have been validated and sent to the application pipeline.</p>
            <button 
              className="btn btn-primary" 
              style={{ marginTop: "1rem" }}
              onClick={() => {
                setShowSuccessModal(false);
                setStep("upload");
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