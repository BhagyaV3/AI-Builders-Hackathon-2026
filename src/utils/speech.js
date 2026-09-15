export const speakText = (text) => {
  if (!("speechSynthesis" in window)) {
    alert("Text-to-speech is not supported in this browser.");
    return;
  }
  
  // Stop any ongoing speech
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.95; // Slightly slower speed for high clarity
  utterance.pitch = 1.0;
  
  window.speechSynthesis.speak(utterance);
};