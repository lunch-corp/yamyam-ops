"""
ULID (Universally Lexicographically Sortable Identifier) 유틸리티 함수들
"""

from ulid import ULID


def generate_ulid() -> str:
    """
    새로운 ULID 생성

    Returns:
        str: 생성된 ULID 문자열
    """
    return str(ULID())


def generate_ulid_from_timestamp(timestamp_ms: int) -> str:
    """
    특정 타임스탬프로부터 ULID 생성

    Args:
        timestamp_ms: 밀리초 단위 타임스탬프

    Returns:
        str: 생성된 ULID 문자열
    """
    return str(ULID.from_timestamp(timestamp_ms))


def is_valid_ulid(ulid_string: str) -> bool:
    """
    ULID 문자열이 유효한지 검증

    Args:
        ulid_string: 검증할 ULID 문자열

    Returns:
        bool: 유효한 ULID인지 여부
    """
    try:
        ULID.from_str(ulid_string)
        return True
    except (ValueError, TypeError):
        return False


def parse_ulid_timestamp(ulid_string: str) -> int:
    """
    ULID에서 타임스탬프 추출

    Args:
        ulid_string: ULID 문자열

    Returns:
        int: 밀리초 단위 타임스탬프
    """
    ulid = ULID.from_str(ulid_string)
    return ulid.timestamp
