import React, { useState } from "react";

export default function AccessibilityToolbar() {
  const [fontSize, setFontSize] = useState(16);
  const [isHighContrast, setIsHighContrast] = useState(false);

  const toggleHighContrast = () => {
    document.body.classList.toggle("high-contrast");
    setIsHighContrast(!isHighContrast);
  };

  const changeFontSize = (delta) => {
    const newSize = Math.min(Math.max(fontSize + delta, 12), 24);
    setFontSize(newSize);
    document.documentElement.style.setProperty("--font-size-base", `${newSize}px`);
  };

  return (
    <div className="accessibility-toolbar" role="region" aria-label="Accessibility Controls">
      <button 
        className="btn btn-outline" 
        onClick={() => changeFontSize(2)} 
        disabled={fontSize >= 24}
        aria-label="Increase text size"
      >
        A+
      </button>
      <button 
        className="btn btn-outline" 
        onClick={() => changeFontSize(-2)} 
        disabled={fontSize <= 12}
        aria-label="Decrease text size"
      >
        A-
      </button>
      <button 
        className="btn btn-outline" 
        onClick={toggleHighContrast} 
        aria-label="Toggle visual theme mode"
      >
        {isHighContrast ? "☀️ Light Mode" : "🌙 High Contrast"}
      </button>
    </div>
  );
}