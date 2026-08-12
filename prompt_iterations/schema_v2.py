from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class C4Element(BaseModel):
    id: str = Field(..., description="Unique snake_case identifier")
    name: str = Field(..., description="Human readable name")
    type: Literal["Person", "Software System"]
    boundary: Literal["Internal", "External"]
    description: str = Field(..., description="Brief description of responsibilities.")

    linked_work_items: List[str] = Field(
        default=[], 
        description="List of Work Item IDs (e.g., '1234', '567') that require this element."
    )

class C4Relationship(BaseModel):
    source: str
    target: str
    label: str = Field(..., description="Action performed (e.g., 'Sends data to').")
    technology: Optional[str] = Field(None, description="Protocol (e.g., 'HTTPS'), if known.")

class C4ContextArchitecture(BaseModel):
    architecture_reasoning: str = Field(..., description="Step-by-step reasoning. Identify the main system scope, list actors, and analyze relationships before generating the final list.")
    title: str
    elements: List[C4Element]
    relationships: List[C4Relationship]