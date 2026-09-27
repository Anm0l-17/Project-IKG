from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class GraphNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    label: str
    type: str  # "EVENT" | "ENTITY"
    category: Optional[str] = None
    status: Optional[str] = None
    importance: float = 1.0
    is_central: bool = False


class GraphEdge(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source: str
    target: str
    type: str  # "PRECEDES" | "CAUSES" | "RELATED_TO" | "MENTIONS" | etc.
    confidence: float = 1.0
    reasoning: Optional[str] = None


class GraphResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    central_event_id: Optional[str] = None
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    node_count: int
    edge_count: int
