export const mockQuestions = [
  {
    id: "q1",
    fieldKey: "fullName",
    questionText: "What is your full legal name?",
    simplifiedText: "What is your name?",
    helpText: "Please enter your first and last name as shown on official documents.",
    type: "text",
    placeholder: "e.g., John Doe",
    required: true,
    pattern: "^[A-Za-z\\s'-]{2,50}$",
    errorMessage: "Name must contain only letters, spaces, or hyphens (no numbers or special characters)."
  },
  {
    id: "q2",
    fieldKey: "phoneNumber",
    questionText: "What is your contact phone number?",
    simplifiedText: "What is your phone number?",
    helpText: "Enter a valid 10-digit phone number.",
    type: "tel",
    placeholder: "e.g., 9876543210",
    required: true,
    pattern: "^[0-9]{10}$",
    errorMessage: "Please enter a valid 10-digit phone number."
  },
  {
    id: "q3",
    fieldKey: "documentType",
    questionText: "What type of document are you submitting?",
    simplifiedText: "Which document do you have?",
    helpText: "Select the option that best describes your document.",
    type: "select",
    options: ["Identity Proof", "Address Proof", "Income Certificate", "Other"],
    hasOtherInput: true,
    required: true
  }
];