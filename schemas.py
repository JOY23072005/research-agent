from typing import Literal,Any
from pydantic import BaseModel, Field


# -------------------------
# Evidence
# -------------------------

class Evidence(BaseModel):
    url: str
    title: str | None = None
    source_type: str | None = None
    snippet: str | None = None


# -------------------------
# Generic researched value
# -------------------------

class Finding(BaseModel):
    value: str | None = None

    status: Literal[
        "verified",
        "not_found",
        "conflicting",
        "not_applicable"
    ]

    reason: str | None = None

    evidence: list[Evidence] = Field(default_factory=list)


# -------------------------
# Entity
# -------------------------

class EntityValidation(BaseModel):
    input_name: str

    status: Literal[
        "valid",
        "invalid",
        "uncertain"
    ]

    entity_type: Literal[
        "person",
        "business",
        "organization",
        "domain",
        "unknown"
    ]

    canonical_name: str | None = None

    reason: str | None = None

    evidence: list[Evidence] = Field(default_factory=list)


# -------------------------
# Research result
# -------------------------

class ResearchResult(BaseModel):
    entity_validation: EntityValidation

    website_description: Finding | None = None

    products: list[Finding] = Field(default_factory=list)

    product_type: Finding | None = None

    pricing: list[Finding] = Field(default_factory=list)

    shipping_policy: Finding | None = None

    terms_of_use: Finding | None = None

    social_media: list[Finding] = Field(default_factory=list)

    emails: list[Finding] = Field(default_factory=list)

    phone_numbers: list[Finding] = Field(default_factory=list)

    addresses: list[Finding] = Field(default_factory=list)

    leadership: list[Finding] = Field(default_factory=list)

    gst_numbers: list[Finding] = Field(default_factory=list)

    pan_numbers: list[Finding] = Field(default_factory=list)

    tan_numbers: list[Finding] = Field(default_factory=list)

    tin_numbers: list[Finding] = Field(default_factory=list)

    external_presence: list[Finding] = Field(default_factory=list)

    claims: list[Finding] = Field(default_factory=list)

    sources: list[Evidence] = Field(default_factory=list)

class ResearchStep(BaseModel):
    tool: str
    input: dict[str, Any]


class ResearchPlan(BaseModel):
    steps: list[ResearchStep]

class ResearchAnalysis(BaseModel):
    findings: list[Finding] = Field(default_factory=list)

    missing_fields: list[str] = Field(default_factory=list)

    contradictions: list[Finding] = Field(default_factory=list)

    next_research_required: bool