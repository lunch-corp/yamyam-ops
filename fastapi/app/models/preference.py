from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func

from .base import Base, ULIDMixin


class UserPreference(Base, ULIDMixin):
    __tablename__ = "user_preferences"

    firebase_uid = Column(
        String(128), ForeignKey("users.firebase_uid"), nullable=False, index=True
    )
    category = Column(String(100), nullable=False)
    preference_score = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class EmbeddingMetadata(Base, ULIDMixin):
    __tablename__ = "embeddings_metadata"

    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(26), nullable=False)
    embedding_type = Column(String(50), nullable=False)
    dimension = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
