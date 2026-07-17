"""Pydantic models for Email Campaign API"""
from typing import Optional
from pydantic import BaseModel, Field


class SendResponse(BaseModel):
    success: bool
    message: str
    sent_count: int = 0
    fail_count: int = 0
    errors: list = []


class ManualContact(BaseModel):
    name: str
    email: str
    phone: str = ""
    job_title: str = ""
    company: str = ""


class ContactEdit(BaseModel):
    index: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    company: Optional[str] = None


class SendSelectedRequest(BaseModel):
    indices: list[int]


class CheckDuplicateRequest(BaseModel):
    indices: list[int]
    template_id: str = ""


class SectionFields(BaseModel):
    """Per-section editable fields for the full email template."""
    header: str = ""
    greeting: str = ""
    intro: str = ""
    closing: str = ""
    signature: str = ""
    footer: str = ""


class TemplateModel(BaseModel):
    id: str = ""
    title: str = Field(default="")
    subject: str = Field(default="")
    body_html: str = ""
    body_text: str = ""
    logo_b64: str = ""
    cc_email: str = ""
    sections: Optional[SectionFields] = None


class TemplateUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    logo_b64: Optional[str] = None
    cc_email: Optional[str] = None
    sections: Optional[SectionFields] = None
