import React from "react";

export default function ReviewScreen({ questions = [], answers = {}, onEdit, onSubmit }) {
  return (
    <div className="card">
      <h2>Review Your Responses</h2>
      <p style={{ opacity: 0.8 }}>Please verify your details before final submission.</p>

      <div style={{ margin: "1.5rem 0" }}>
        {questions.map((q, idx) => (
          <div
            key={q.fieldKey}
            style={{
              padding: "1rem 0",
              borderBottom: "1px solid var(--border-color)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center"
            }}
          >
            <div>
              <strong>{q.questionText}</strong>
              <div style={{ marginTop: "0.25rem" }}>
                {answers[q.fieldKey] || <em style={{ opacity: 0.6 }}>Not answered</em>}
              </div>
            </div>
            {onEdit && (
              <button className="btn btn-outline" onClick={() => onEdit(idx)}>
                Edit
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="button-group">
        {onEdit && (
          <button className="btn btn-secondary" onClick={() => onEdit(0)}>
            Back to Form
          </button>
        )}
        <button className="btn btn-primary" onClick={onSubmit}>
          Submit Application
        </button>
      </div>
    </div>
  );
}