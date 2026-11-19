"""Pydantic models used for structured LLM output and validation."""

from typing import Literal

from pydantic import BaseModel, Field

EntityType = Literal[
    "Attraction", "Person", "HistoricalEvent", "District",
    "Route", "Institution", "Concept",
]

RelationType = Literal[
    "located_in", "created_by", "associated_with", "part_of",
    "included_in_route", "connected_to", "has_function", "has_feature",
]


class Fact(BaseModel):
    """One directed relation extracted from a source document."""

    id: str
    subject: str
    subject_id: str | None = None
    subject_type: EntityType
    relation: RelationType
    object: str
    object_id: str | None = None
    object_type: EntityType
    source_doc: str
    evidence: str = Field(min_length=10)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class FactCollection(BaseModel):
    facts: list[Fact]


class SearchResult(BaseModel):
    chunk_id: str
    document: str
    text: str
    score: float

