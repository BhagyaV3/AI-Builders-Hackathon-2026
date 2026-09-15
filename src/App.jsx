import React, { useState } from "react";
import "./App.css";
import AccessibilityToolbar from "./AccessibilityToolbar";
import GuidedQA from "./GuidedQA";
import ReviewScreen from "./ReviewScreen";
import { mockQuestions } from "./mockFormData";

export default function App() {
  const [step, setStep] = useState("qa");
  const [userAnswers, setUserAnswers] = useState({});
  const [targetQuestionIndex, setTargetQuestionIndex] = useState(0);
  const [showSuccessModal, setShowSuccessModal] = useState(false);

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
      </header>

      <AccessibilityToolbar />

      {step === "qa" && (
        <GuidedQA
          questions={mockQuestions}
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
          questions={mockQuestions}
          answers={userAnswers}
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