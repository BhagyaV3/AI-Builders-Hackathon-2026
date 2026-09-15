from __future__ import annotations

from pydantic import BaseModel, Field


class FormField(BaseModel):
    name: str
    label: str
    value: str | None = None
    required: bool = False
    source_excerpt: str | None = None


class FormRule(BaseModel):
    kind: str = Field(description="rule, validation, condition, or instruction")
    text: str
    source_excerpt: str | None = None


class FormDeadline(BaseModel):
    text: str
    due_date: str | None = None
    source_excerpt: str | None = None


class FormWarning(BaseModel):
    text: str
    severity: str = "medium"
    source_excerpt: str | None = None


class FormExtractionResponse(BaseModel):
    file_name: str
    title: str
    summary: str
    fields: list[FormField]
    rules: list[FormRule]
    deadlines: list[FormDeadline]
    exceptions: list[str]
    warnings: list[FormWarning]
    next_steps: list[str]
    confidence: float