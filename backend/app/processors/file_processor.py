"""
범용 파일 처리 클래스 - CSV, JSON, Excel 등 지원
"""

import json
import logging
from io import BytesIO, StringIO
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class FileProcessor:
    """범용 파일 처리 클래스 - 다양한 포맷 지원"""

    @staticmethod
    def read_file(
        file_content: bytes, file_format: str = "csv", encoding: str = "utf-8"
    ) -> pd.DataFrame | dict[str, Any] | list[dict[str, Any]]:
        """
        파일 내용을 적절한 포맷으로 읽기

        Args:
            file_content: 파일의 바이트 내용
            file_format: 파일 포맷 ("csv", "json", "excel")
            encoding: 파일 인코딩 (기본값: utf-8)

        Returns:
            pandas DataFrame 또는 JSON 데이터
        """
        try:
            if file_format.lower() == "csv":
                return FileProcessor.read_csv(file_content, encoding)
            elif file_format.lower() == "json":
                return FileProcessor.read_json(file_content, encoding)
            elif file_format.lower() in ["excel", "xlsx", "xls"]:
                return FileProcessor.read_excel(file_content)
            else:
                raise ValueError(f"지원하지 않는 파일 포맷: {file_format}")
        except Exception as e:
            logger.error(f"파일 읽기 실패 ({file_format}): {str(e)}")
            raise

    @staticmethod
    def read_csv(file_content: bytes, encoding: str = "utf-8") -> pd.DataFrame:
        """
        CSV 파일 내용을 DataFrame으로 읽기

        Args:
            file_content: CSV 파일의 바이트 내용
            encoding: 파일 인코딩 (기본값: utf-8)

        Returns:
            pandas DataFrame
        """
        try:
            # 바이트를 문자열로 디코딩
            text = file_content.decode(encoding)
            # DataFrame으로 변환
            df = pd.read_csv(StringIO(text))
            df.reset_index(drop=True, inplace=True)
            logger.info(f"CSV 파일 읽기 성공: {len(df)} 행")
            return df
        except UnicodeDecodeError:
            # UTF-8 실패 시 다른 인코딩 시도
            logger.warning(f"{encoding} 디코딩 실패, cp949로 재시도")
            text = file_content.decode("cp949")
            df = pd.read_csv(StringIO(text))
            logger.info(f"CSV 파일 읽기 성공 (cp949): {len(df)} 행")
            return df

    @staticmethod
    def read_json(
        file_content: bytes, encoding: str = "utf-8"
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """
        JSON 파일 내용을 읽기

        Args:
            file_content: JSON 파일의 바이트 내용
            encoding: 파일 인코딩 (기본값: utf-8)

        Returns:
            JSON 데이터 (딕셔너리 또는 리스트)
        """
        try:
            text = file_content.decode(encoding)
            data = json.loads(text)
            logger.info(f"JSON 파일 읽기 성공: {type(data).__name__}")
            return data
        except UnicodeDecodeError:
            logger.warning(f"{encoding} 디코딩 실패, cp949로 재시도")
            text = file_content.decode("cp949")
            data = json.loads(text)
            logger.info(f"JSON 파일 읽기 성공 (cp949): {type(data).__name__}")
            return data

    @staticmethod
    def read_excel(file_content: bytes) -> pd.DataFrame:
        """
        Excel 파일 내용을 DataFrame으로 읽기

        Args:
            file_content: Excel 파일의 바이트 내용

        Returns:
            pandas DataFrame
        """
        try:
            df = pd.read_excel(BytesIO(file_content))
            logger.info(f"Excel 파일 읽기 성공: {len(df)} 행")
            return df
        except Exception as e:
            logger.error(f"Excel 파일 읽기 실패: {str(e)}")
            raise

    @staticmethod
    def validate_columns(
        df: pd.DataFrame, required_columns: list[str]
    ) -> tuple[bool, str]:
        """
        DataFrame의 컬럼 유효성 검사

        Args:
            df: 검사할 DataFrame
            required_columns: 필수 컬럼 리스트

        Returns:
            (성공 여부, 에러 메시지)
        """
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            return False, f"필수 컬럼 누락: {', '.join(missing_columns)}"
        return True, ""

    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        데이터 정제

        Args:
            df: 정제할 DataFrame

        Returns:
            정제된 DataFrame
        """
        # NaN을 None으로 변환
        df = df.where(pd.notnull(df), None)
        return df

    @staticmethod
    def batch_data(df: pd.DataFrame, batch_size: int = 1000) -> list[pd.DataFrame]:
        """
        DataFrame을 배치로 분할

        Args:
            df: 분할할 DataFrame
            batch_size: 배치 크기

        Returns:
            DataFrame 배치 리스트
        """
        batches = []
        for i in range(0, len(df), batch_size):
            batches.append(df.iloc[i : i + batch_size])
        return batches

    @staticmethod
    def detect_file_format(filename: str) -> str:
        """
        파일명으로부터 파일 포맷 감지

        Args:
            filename: 파일명

        Returns:
            감지된 파일 포맷
        """
        extension = filename.lower().split(".")[-1]

        format_mapping = {"csv": "csv", "json": "json", "xlsx": "excel", "xls": "excel"}

        return format_mapping.get(extension, "csv")
