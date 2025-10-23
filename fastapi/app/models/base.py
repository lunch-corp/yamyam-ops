from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

from app.utils.ulid_utils import generate_ulid

# 모든 모델의 기본 클래스
Base = declarative_base()


class ULIDMixin:
    """ULID를 프라이머리 키로 사용하는 Mixin 클래스"""

    id = Column(
        String(26),
        primary_key=True,
        default=generate_ulid,
        index=True,
        comment="ULID (Universally Lexicographically Sortable Identifier)",
    )
