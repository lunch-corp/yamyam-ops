from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

from ..utils.ulid_utils import generate_ulid
from .item import Item
from .item_kakao_mapping import ItemKakaoMapping
from .kakao_diner import KakaoDiner
from .kakao_review import KakaoReview
from .kakao_reviewer import KakaoReviewer
from .preference import EmbeddingMetadata, UserPreference
from .review import Review
from .user import User

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


# 모든 모델을 import하여 SQLAlchemy가 인식할 수 있도록 함

__all__ = [
    "Base",
    "ULIDMixin",
    "User",
    "Item",
    "Review",
    "UserPreference",
    "EmbeddingMetadata",
    "KakaoDiner",
    "KakaoReviewer",
    "KakaoReview",
    "ItemKakaoMapping",
]
