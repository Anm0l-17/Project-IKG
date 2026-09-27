import json
from typing import List, Optional, Any
from sqlalchemy import TypeDecorator, JSON


class VectorType(TypeDecorator):
    """
    SQLAlchemy TypeDecorator for storing dense float vector embeddings.
    Compatible with PostgreSQL and SQLite (using JSON serialization).
    Default dimension is 384 (all-MiniLM-L6-v2).
    """
    impl = JSON
    cache_ok = True

    def __init__(self, dimensions: int = 384, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.dimensions = dimensions

    def process_bind_param(self, value: Optional[List[float]], dialect: Any) -> Optional[Any]:
        if value is None:
            return None
        if isinstance(value, (list, tuple)):
            return [float(x) for x in value]
        return value

    def process_result_value(self, value: Any, dialect: Any) -> Optional[List[float]]:
        if value is None:
            return None
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return [float(x) for x in parsed]
            except Exception:
                return None
        if isinstance(value, (list, tuple)):
            return [float(x) for x in value]
        return value
