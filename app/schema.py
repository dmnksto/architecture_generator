from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# ==========================================
# SYSTEM CONTEXT LEVEL (Level 1)
# ==========================================
class C4Element(BaseModel):
    """
    Represents an Actor (Person) or a Software System in the C4 Context diagram.
    """
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
    """
    Represents a directional interaction between two C4 elements.
    """
    source: str
    target: str
    label: str = Field(..., description="Action performed (e.g., 'Sends data to').")
    technology: Optional[str] = Field(None, description="Protocol (e.g., 'HTTPS'), if known.")

class C4ContextArchitecture(BaseModel):
    """
    Top-level schema for the C4 System Context.
    Note: 'architecture_reasoning' is intentionally placed first to force the LLM 
    to generate its Chain of Thought (CoT) prior to instantiating the elements array.
    """
    architecture_reasoning: str = Field(..., description="Step-by-step reasoning. " \
        "1. SCOPE: Explicitly name the single 'Internal' system under design. " \
        "2. BOUNDARIES: Classify all other systems and actors as 'External'. " \
        "3. RELATIONS: Analyze interactions. " \
        "Identify the main system scope, list actors, and analyze relationships before generating the final list.")
    title: str
    elements: List[C4Element]
    relationships: List[C4Relationship]

# ==========================================
# CONTAINER LEVEL Extension (Level 2)
# ==========================================
class C4Container(BaseModel):
    """
    Represents a deployable Container (e.g., Web App, Database) within the internal system boundary.
    """
    id: str = Field(..., description="Unique snake_case identifier (e.g., 'web_app', 'db').")
    name: str = Field(..., description="Name of the container (e.g., 'Web Application').")

    # 'Database' maps to ContainerDb(), others to Container()
    type: Literal["WebApp", "MobileApp", "Api", "Database", "Service", "FileSystem"] 
    description: str = Field(..., description="Brief description of responsibilities.")
    technology: str = Field(..., description="Technology stack (e.g., 'Java, Spring MVC', 'PostgreSQL').")
    linked_work_items: List[str] = Field(default=[], description="Work Item IDs.")

class C4ContainerArchitecture(BaseModel):
    """
    Top-level schema for the C4 Container architecture.
    Utilizes initial CoT reasoning to map out internal components before generation.
    """
    architecture_reasoning: str = Field(..., description="Reasoning: " \
        "1. Identify containers inside the system boundary. " \
        "2. Assign technologies. " \
        "3. Map interactions.")
    title: str
    containers: List[C4Container]
    relationships: List[C4Relationship]