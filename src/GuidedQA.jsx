import React, { useState, useEffect } from "react";

// Web Speech API Text-to-Speech Helper
const speakText = (text) => {
  if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
  try {
    window.speechSynthesis.cancel();
    if (text) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.95;
      window.speechSynthesis.speak(utterance);
    }
  } catch (err) {
    console.error("Speech synthesis error:", err);
  }
};

export default function GuidedQA({
  questions = [],
  onComplete,
  initialAnswers = {},
  initialIndex = 0,
}) {
  const [currentIndex, setCurrentIndex] = useState(initialIndex);
  const [answers, setAnswers] = useState(initialAnswers);
  const [otherText, setOtherText] = useState("");
  const [isSimplified, setIsSimplified] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setCurrentIndex(initialIndex);
  }, [initialIndex]);

  useEffect(() => {
    setAnswers(initialAnswers);
  }, [initialAnswers]);

  if (!questions || questions.length === 0) {
    return <div className="card floating-card">No questions available.</div>;
  }

  const currentQ = questions[currentIndex];
  const progressPercent = ((currentIndex + 1) / questions.length) * 100;
  const currentValue = answers[currentQ.fieldKey] || "";

  const validateInput = () => {
    if (currentQ.required && (!currentValue || currentValue.toString().trim() === "")) {
      setError("This field is required before moving forward.");
      return false;
    }

    if (currentQ.hasOtherInput && currentValue === "Other") {
      if (!otherText || otherText.trim() === "") {
        setError("Please specify details for 'Other'.");
        return false;
      }
    }

    if (currentQ.type === "number" && currentValue) {
      const num = Number(currentValue);
      if (currentQ.min !== undefined && num < currentQ.min) {
        setError(`Value must be at least ${currentQ.min}.`);
        return false;
      }
      if (currentQ.max !== undefined && num > currentQ.max) {
        setError(`Value cannot exceed ${currentQ.max}.`);
        return false;
      }
    }

    if (currentQ.pattern && currentValue) {
      const regex = new RegExp(currentQ.pattern);
      if (!regex.test(currentValue.toString().trim())) {
        setError(currentQ.errorMessage || "Invalid format entered.");
        return false;
      }
    }

    setError("");
    return true;
  };

  const handleInputChange = (value) => {
    setAnswers((prev) => ({ ...prev, [currentQ.fieldKey]: value }));
    if (error) setError("");
  };

  const handleOtherTextChange = (text) => {
    setOtherText(text);
    setAnswers((prev) => ({ ...prev, [`${currentQ.fieldKey}_other`]: text }));
    if (error) setError("");
  };

  const handleReadAloud = () => {
    const textToRead =
      isSimplified && currentQ.simplifiedText
        ? currentQ.simplifiedText
        : currentQ.questionText;
    const helpText = currentQ.helpText ? ` Hint: ${currentQ.helpText}` : "";
    speakText(`${textToRead}.${helpText}`);
  };

  const handleNext = () => {
    if (!validateInput()) return;

    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setIsSimplified(false);
      setError("");
    } else {
      onComplete(answers);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setError("");
      setCurrentIndex(currentIndex - 1);
      setIsSimplified(false);
    }
  };

  return (
    <div className="card floating-card">
      <style>{`
        /* Floating Card Box */
        .floating-card {
          border: 1.5px solid rgba(0, 0, 0, 0.12);
          box-shadow: 0 12px 30px -5px rgba(0, 0, 0, 0.12), 0 4px 12px -2px rgba(0, 0, 0, 0.05);
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .floating-card::before {
          content: "";
          position: absolute;
          top: -30px;
          right: -30px;
          width: 160px;
          height: 160px;
          border-radius: 50%;
          background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0) 70%);
          pointer-events: none;
          z-index: 0;
          
        }  
        /* Dedicated Typography for Form Inputs */
        .form-input-styled, .form-select-styled {
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
          font-size: 1rem;
          font-weight: 500;
          letter-spacing: 0.015em;
          color: #1e293b;
          line-height: 1.5;
        }

        /* Black Speaker Emoji Symbol */
        .black-speaker-icon {
          color: #000000;
          display: inline-block;
          margin-right: 0.25rem;
          filter: grayscale(100%) contrast(200%);
        }

        /* Button Hover and Shadows */
        .btn-hover-shadow {
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
          transition: transform 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease;
        }

        .btn-hover-shadow:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.15), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }

        .btn-hover-shadow:active:not(:disabled) {
          transform: translateY(0);
        }
      `}</style>

      {/* Progress Bar */}
      <div className="progress-container">
        <div className="progress-bar" style={{ width: `${progressPercent}%` }}></div>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <small style={{ color: "var(--text-color)" }}>
          Question {currentIndex + 1} of {questions.length}
        </small>
        <button
          type="button"
          className="btn btn-outline btn-hover-shadow"
          onClick={handleReadAloud}
          aria-label="Read question aloud"
          style={{ padding: "0.25rem 0.6rem", fontSize: "0.85rem" }}
        >
          <span className="black-speaker-icon">🔊</span> Read Aloud
        </button>
      </div>

      {/* Header with Original Question Typography */}
      <div
        style={{
          display: "flex",
          justify: "space-between",
          alignItems: "center",
          marginTop: "0.75rem",
          gap: "1rem",
        }}
      >
        <div style={{ flex: 1 }}>
          {isSimplified && (
            <span
              className="badge-simplified"
              style={{ display: "inline-block", marginBottom: "0.4rem" }}
            >
              💡 Easy Read Mode
            </span>
          )}
          <h2>
            {isSimplified && currentQ.simplifiedText
              ? currentQ.simplifiedText
              : currentQ.questionText}
          </h2>
        </div>
        {currentQ.simplifiedText && (
          <button
            type="button"
            className="btn btn-outline btn-hover-shadow"
            onClick={() => setIsSimplified(!isSimplified)}
            style={{ flexShrink: 0 }}
          >
            {isSimplified ? "Show Original" : "Simplify"}
          </button>
        )}
      </div>

      {currentQ.helpText && <div className="help-text">{currentQ.helpText}</div>}

      {currentQ.sourceExcerpt && (
        <div
          style={{
            marginTop: "0.9rem",
            padding: "0.85rem 1rem",
            borderRadius: "10px",
            border: "1px solid var(--border-color)",
            background: "rgba(0, 0, 0, 0.02)",
            fontSize: "0.92rem",
          }}
        >
          <strong>Source:</strong> {currentQ.sourceExcerpt}
        </div>
      )}

      {/* Form Inputs with Custom Typography */}
      <div className="form-group" style={{ marginTop: "1.25rem" }}>
        {["text", "date", "number", "email", "tel"].includes(currentQ.type) && (
          <input
            type={currentQ.type}
            className="form-input form-input-styled"
            value={currentValue}
            placeholder={currentQ.placeholder || ""}
            min={currentQ.min}
            max={currentQ.max}
            onChange={(e) => handleInputChange(e.target.value)}
          />
        )}

        {currentQ.type === "select" && (
          <select
            className="form-select form-select-styled"
            value={currentValue}
            onChange={(e) => handleInputChange(e.target.value)}
          >
            <option value="">-- Select an Option --</option>
            {currentQ.options &&
              currentQ.options.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
          </select>
        )}

        {currentQ.type === "radio" && (
          <div className="radio-group">
            {currentQ.options &&
              currentQ.options.map((opt) => (
                <label key={opt} className="radio-label form-input-styled">
                  <input
                    type="radio"
                    name={currentQ.fieldKey}
                    value={opt}
                    checked={currentValue === opt}
                    onChange={(e) => handleInputChange(e.target.value)}
                  />
                  {opt}
                </label>
              ))}
          </div>
        )}

        {/* Dynamic "Other" Field */}
        {currentQ.hasOtherInput && currentValue === "Other" && (
          <div style={{ marginTop: "1rem" }}>
            <label style={{ fontSize: "0.9rem", display: "block", marginBottom: "0.25rem" }}>
              Please specify details:
            </label>
            <input
              type="text"
              className="form-input form-input-styled"
              value={otherText}
              placeholder="Type your details here..."
              onChange={(e) => handleOtherTextChange(e.target.value)}
            />
          </div>
        )}
      </div>

      {error && <div className="error-message" role="alert">{error}</div>}

      {/* Button Group with Hover & Shadow */}
      <div className="button-group" style={{ marginTop: "1.5rem" }}>
        <button
          type="button"
          className="btn btn-secondary btn-hover-shadow"
          onClick={handlePrev}
          disabled={currentIndex === 0}
          style={{ opacity: currentIndex === 0 ? 0.5 : 1 }}
        >
          Previous
        </button>
        <button
          type="button"
          className="btn btn-primary btn-hover-shadow"
          onClick={handleNext}
        >
          Next
        </button>
      </div>
    </div>
  );
}