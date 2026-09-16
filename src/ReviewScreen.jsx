import React from "react";

export default function ReviewScreen({ questions = [], answers = {}, analysis = null, onEdit, onSubmit }) {
  const renderList = (items, emptyText) => {
    if (!items || items.length === 0) {
      return <p style={{ margin: 0, opacity: 0.7 }}>{emptyText}</p>;
    }

    return (
      <ul style={{ margin: "0.5rem 0 0", paddingLeft: "1.2rem" }}>
        {items.map((item, index) => (
          <li key={`${index}-${typeof item === "string" ? item : item.text}`} style={{ marginBottom: "0.65rem" }}>
            <div>{typeof item === "string" ? item : item.text}</div>
            {typeof item === "object" && item && item.source_excerpt && (
              <div style={{ fontSize: "0.86rem", opacity: 0.78, marginTop: "0.2rem" }}>
                Source: {item.source_excerpt}
              </div>
            )}
          </li>
        ))}
      </ul>
    );
  };

  return (
    <div className="card">
      <h2>Review Your Responses</h2>
      <p style={{ opacity: 0.8 }}>Please verify your details before final submission.</p>

      {analysis && (
        <div
          style={{
            margin: "1rem 0 1.5rem",
            padding: "1rem 1.1rem",
            borderRadius: "12px",
            background: "var(--help-bg)",
            border: "1px solid var(--border-color)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap" }}>
            <div>
              <strong>{analysis.title}</strong>
              <div style={{ marginTop: "0.35rem", opacity: 0.85 }}>{analysis.summary}</div>
            </div>
            <div style={{ minWidth: "160px", textAlign: "right" }}>
              <div style={{ fontWeight: 600 }}>Confidence</div>
              <div>{Math.round((analysis.confidence || 0) * 100)}%</div>
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              gap: "1rem",
              marginTop: "1rem",
            }}
          >
            <div>
              <strong>Deadlines</strong>
              {renderList(analysis.deadlines || [], "No deadlines detected.")}
            </div>
            <div>
              <strong>Warnings</strong>
              {renderList(analysis.warnings || [], "No warnings flagged.")}
            </div>
            <div>
              <strong>Next steps</strong>
              {renderList(analysis.next_steps, "No next steps available.")}
            </div>
          </div>

          {analysis.rules && analysis.rules.length > 0 && (
            <div style={{ marginTop: "1rem" }}>
              <strong>Rules and checks</strong>
              {renderList(analysis.rules, "No extra rules detected.")}
            </div>
          )}
        </div>
      )}

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
              {q.sourceExcerpt && (
                <div style={{ marginTop: "0.5rem", fontSize: "0.9rem", opacity: 0.85 }}>
                  <span style={{ fontWeight: 600 }}>Source:</span> {q.sourceExcerpt}
                </div>
              )}
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