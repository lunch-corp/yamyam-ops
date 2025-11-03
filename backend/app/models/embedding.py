from sqlalchemy import Column, DateTime, Integer, LargeBinary, String
from sqlalchemy.sql import func

from .base import Base, ULIDMixin


class EmbeddingVector(Base, ULIDMixin):
    """임베딩 벡터를 저장하는 테이블"""

    __tablename__ = "embedding_vectors"

    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(26), nullable=False, index=True)
    embedding_type = Column(String(50), nullable=False, index=True)
    dimension = Column(Integer, nullable=False)
    vector_data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 복합 인덱스: entity_type과 entity_id로 빠르게 조회
    __table_args__ = ({"comment": "임베딩 벡터 데이터를 저장하는 테이블"},)
