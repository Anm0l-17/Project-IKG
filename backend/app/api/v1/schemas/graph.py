from pydantic import BaseModel, ConfigDict


class GraphNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    label: str
    type: str  # "EVENT" | "ENTITY"
    category: str | None = None
    status: str | None = None
    importance: float = 1.0
    is_central: bool = False


class GraphEdge(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source: str
    target: str
    type: str  # "PRECEDES" | "CAUSES" | "RELATED_TO" | "MENTIONS" | etc.
    confidence: float = 1.0
    reasoning: str | None = None


class GraphResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    central_event_id: str | None = None
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    node_count: int
    edge_count: int
