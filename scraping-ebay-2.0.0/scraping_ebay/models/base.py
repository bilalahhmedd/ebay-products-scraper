from datetime import datetime
from pydantic import BaseModel, ConfigDict

class BaseEntity(BaseModel):
    """
    Base class for every domain model
    """
    model_config = ConfigDict(
        extra="ignore",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()