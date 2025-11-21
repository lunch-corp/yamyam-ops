"""
Kakao 데이터 처리 전용 클래스 - 설정 기반 처리
"""

import ast
from collections.abc import Callable

import pandas as pd


class KakaoDataProcessor:
    """Kakao 데이터 처리 전용 클래스 - 설정 기반 처리"""

    # 각 파일별 처리 설정 (필수 컬럼 + 변환 함수 + SQL 쿼리 정보)
    PROCESSING_CONFIG = {
        "diner_basic": {
            "required_columns": [
                "diner_idx",
                "diner_name",
                "diner_tag",
                "diner_menu_name",
                "diner_menu_price",
                "diner_review_cnt",
                "diner_review_avg",
                "diner_blog_review_cnt",
                "diner_review_tags",
                "diner_road_address",
                "diner_num_address",
                "diner_phone",
                "diner_lat",
                "diner_lon",
                "diner_open_time",
            ],
            "field_mappings": [
                ("diner_idx", "int"),
                ("diner_name", "str"),
                ("diner_tag", "list_to_comma"),
                ("diner_menu_name", "list_to_comma"),
                ("diner_menu_price", "list_to_comma"),
                ("diner_review_cnt", "str"),
                ("diner_review_avg", "float_nullable"),
                ("diner_blog_review_cnt", "float_nullable"),
                ("diner_review_tags", "list_to_comma"),
                ("diner_road_address", "str"),
                ("diner_num_address", "str"),
                ("diner_phone", "str"),
                ("diner_lat", "float"),
                ("diner_lon", "float"),
                ("diner_open_time", "str"),
            ],
            "sql_fields": [
                "diner_idx",
                "diner_name",
                "diner_tag",
                "diner_menu_name",
                "diner_menu_price",
                "diner_review_cnt",
                "diner_review_avg",
                "diner_blog_review_cnt",
                "diner_review_tags",
                "diner_road_address",
                "diner_num_address",
                "diner_phone",
                "diner_lat",
                "diner_lon",
                "diner_open_time",
            ],
            "query_name": "INSERT_KAKAO_DINER_BASIC",
        },
        "diner_categories": {
            "required_columns": [
                "diner_idx",
                "diner_category_large",
                "diner_category_middle",
                "diner_category_small",
                "diner_category_detail",
            ],
            "field_mappings": [
                ("diner_category_large", "str"),
                ("diner_category_middle", "str"),
                ("diner_category_small", "str"),
                ("diner_category_detail", "str"),
                ("diner_idx", "int"),
            ],
            "sql_fields": [
                "diner_category_large",
                "diner_category_middle",
                "diner_category_small",
                "diner_category_detail",
                "diner_idx",
            ],
            "query_name": "UPDATE_KAKAO_DINER_CATEGORY",
        },
        "diner_menus": {
            "required_columns": ["diner_idx", "diner_menu_name", "diner_menu_price"],
            "field_mappings": [
                ("diner_menu_name", "str"),
                ("diner_idx", "int"),
                ("diner_menu_price", "str"),
            ],
            "sql_fields": ["diner_menu_name", "diner_idx", "diner_menu_price"],
            "query_name": "UPDATE_KAKAO_DINER_MENU",
        },
        "diner_reviews": {
            "required_columns": [
                "diner_idx",
                "diner_review_cnt",
                "diner_review_avg",
                "diner_blog_review_cnt",
            ],
            "field_mappings": [
                ("diner_review_cnt", "int_default_zero"),
                ("diner_review_avg", "float_default_zero"),
                ("diner_blog_review_cnt", "float_default_zero"),
                ("diner_idx", "int"),
            ],
            "sql_fields": [
                "diner_review_cnt",
                "diner_review_avg",
                "diner_blog_review_cnt",
                "diner_idx",
            ],
            "query_name": "UPDATE_KAKAO_DINER_REVIEW",
        },
        "diner_tags": {
            "required_columns": ["diner_idx", "diner_tag", "diner_review_tags"],
            "field_mappings": [
                ("diner_tag", "str"),
                ("diner_review_tags", "str"),
                ("diner_idx", "int"),
            ],
            "sql_fields": ["diner_tag", "diner_review_tags", "diner_idx"],
            "query_name": "UPDATE_KAKAO_DINER_TAGS",
        },
        "reviewers": {
            "required_columns": [
                "reviewer_id",
                "reviewer_review_cnt",
                "reviewer_avg",
                "badge_grade",
                "badge_level",
            ],
            "field_mappings": [
                ("reviewer_id", "int"),
                ("reviewer_user_name", "str"),
                ("reviewer_review_cnt", "int"),
                ("reviewer_avg", "float"),
                ("badge_grade", "str"),
                ("badge_level", "int"),
            ],
            "sql_fields": [
                "reviewer_id",
                "reviewer_user_name",
                "reviewer_review_cnt",
                "reviewer_avg",
                "badge_grade",
                "badge_level",
            ],
            "query_name": "INSERT_KAKAO_REVIEWER",
        },
        "reviews": {
            "required_columns": [
                "diner_idx",
                "reviewer_id",
                "review_id",
                "reviewer_review_score",
            ],
            "field_mappings": [
                ("diner_idx", "int"),
                ("reviewer_id", "int"),
                ("review_id", "int"),
                ("reviewer_review", "str_optional"),
                ("reviewer_review_date", "date_str"),
                ("reviewer_review_score", "float"),
            ],
            "sql_fields": [
                "diner_idx",
                "reviewer_id",
                "review_id",
                "reviewer_review",
                "reviewer_review_date",
                "reviewer_review_score",
            ],
            "query_name": "INSERT_KAKAO_REVIEW",
        },
    }

    # 데이터 타입 변환 함수들
    @staticmethod
    def convert_list_string_to_comma_separated(x):
        """
        리스트 형식의 문자열을 쉼표로 구분된 문자열로 변환

        예: "['제로페이', '모임,회식']" -> "제로페이,모임,회식"
        """
        if pd.isnull(x) or x is None:
            return None

        # 문자열 정제
        x_str = str(x).strip()

        if not x_str or x_str == "" or x_str == "nan":
            return None

        try:
            # Python 리스트로 파싱 시도
            if x_str.startswith("[") and x_str.endswith("]"):
                parsed = ast.literal_eval(x_str)
                if isinstance(parsed, list):
                    return ",".join([str(item).strip() for item in parsed if item])

            # 이미 쉼표로 구분된 문자열인 경우
            return x_str

        except (ValueError, SyntaxError):
            # 파싱 실패 시 원본 반환
            return x_str

    # PostgreSQL INTEGER 범위: -2,147,483,648 ~ 2,147,483,647
    INTEGER_MIN = -2147483648
    INTEGER_MAX = 2147483647

    @staticmethod
    def _validate_integer_range(value, field_name: str = None):
        """정수 값이 PostgreSQL INTEGER 범위 내인지 검증"""
        if value is None:
            return value

        if (
            value < KakaoDataProcessor.INTEGER_MIN
            or value > KakaoDataProcessor.INTEGER_MAX
        ):
            field_info = f" ({field_name})" if field_name else ""
            raise ValueError(
                f"정수 값이 INTEGER 범위를 초과합니다{field_info}: "
                f"{value} (범위: {KakaoDataProcessor.INTEGER_MIN} ~ {KakaoDataProcessor.INTEGER_MAX})"
            )
        return value

    TYPE_CONVERTERS = {
        "str": lambda x: str(x) if pd.notnull(x) else None,
        "str_optional": lambda x: str(x) if pd.notnull(x) and str(x).strip() else None,
        "int": lambda x: int(x) if pd.notnull(x) else None,
        "float": lambda x: float(x) if pd.notnull(x) else None,
        "float_nullable": lambda x: float(x) if pd.notnull(x) else None,
        "int_default_zero": lambda x: int(x) if pd.notnull(x) else 0,
        "float_default_zero": lambda x: float(x) if pd.notnull(x) else 0.0,
        "date_str": lambda x: str(x).strip()
        if pd.notnull(x) and str(x).strip()
        else None,
        "list_to_comma": lambda x: KakaoDataProcessor.convert_list_string_to_comma_separated(
            x
        ),
    }

    @classmethod
    def get_required_columns(cls, file_type: str) -> list[str]:
        """파일 타입별 필수 컬럼 반환"""
        if file_type not in cls.PROCESSING_CONFIG:
            raise ValueError(f"지원하지 않는 파일 타입: {file_type}")
        return cls.PROCESSING_CONFIG[file_type]["required_columns"]

    @classmethod
    def get_sql_fields(cls, file_type: str) -> list[str]:
        """파일 타입별 SQL 필드 반환"""
        if file_type not in cls.PROCESSING_CONFIG:
            raise ValueError(f"지원하지 않는 파일 타입: {file_type}")
        return cls.PROCESSING_CONFIG[file_type]["sql_fields"]

    @classmethod
    def get_query_name(cls, file_type: str) -> str:
        """파일 타입별 쿼리 이름 반환"""
        if file_type not in cls.PROCESSING_CONFIG:
            raise ValueError(f"지원하지 않는 파일 타입: {file_type}")
        return cls.PROCESSING_CONFIG[file_type]["query_name"]

    @classmethod
    def generate_sql_query(cls, file_type: str, operation: str = "INSERT") -> str:
        """
        설정에 따라 SQL 쿼리 자동 생성

        Args:
            file_type: 파일 타입
            operation: SQL 작업 타입 (INSERT, UPDATE)
        """
        if file_type not in cls.PROCESSING_CONFIG:
            raise ValueError(f"지원하지 않는 파일 타입: {file_type}")

        config = cls.PROCESSING_CONFIG[file_type]
        sql_fields = config["sql_fields"]

        if operation == "INSERT":
            # INSERT 쿼리 생성
            fields_str = ", ".join(sql_fields)
            placeholders = ", ".join(["%s"] * len(sql_fields))

            if file_type == "diner_basic":
                table_name = "kakao_diner"
                conflict_field = "diner_idx"
                update_fields = [f for f in sql_fields if f != conflict_field]
                update_clause = ", ".join(
                    [f"{field} = EXCLUDED.{field}" for field in update_fields]
                )

                return f"""
                INSERT INTO {table_name} ({fields_str})
                VALUES ({placeholders})
                ON CONFLICT ({conflict_field}) DO UPDATE SET
                    {update_clause},
                    updated_at = CURRENT_TIMESTAMP
                """
            else:
                # 다른 타입들은 UPDATE 쿼리 사용
                return cls.generate_sql_query(file_type, "UPDATE")

        elif operation == "UPDATE":
            # UPDATE 쿼리 생성
            if file_type == "diner_categories":
                update_fields = [
                    "diner_category_large",
                    "diner_category_middle",
                    "diner_category_small",
                    "diner_category_detail",
                ]
                where_field = "diner_idx"
            elif file_type == "diner_menus":
                update_fields = ["diner_menu_name", "diner_menu_price"]
                where_field = "diner_idx"
            elif file_type == "diner_reviews":
                update_fields = [
                    "diner_review_cnt",
                    "diner_review_avg",
                    "diner_blog_review_cnt",
                ]
                where_field = "diner_idx"
            elif file_type == "diner_tags":
                update_fields = ["diner_tag", "diner_review_tags"]
                where_field = "diner_idx"
            else:
                raise ValueError(f"지원하지 않는 UPDATE 타입: {file_type}")

            set_clause = ", ".join([f"{field} = %s" for field in update_fields])

            return f"""
            UPDATE kakao_diner SET
                {set_clause},
                updated_at = CURRENT_TIMESTAMP
            WHERE {where_field} = %s
            """

        else:
            raise ValueError(f"지원하지 않는 작업 타입: {operation}")

    @classmethod
    def validate_config_consistency(cls, file_type: str) -> dict[str, bool]:
        """
        설정의 일관성 검증

        Args:
            file_type: 파일 타입

        Returns:
            검증 결과 딕셔너리
        """
        if file_type not in cls.PROCESSING_CONFIG:
            return {"valid": False, "error": "지원하지 않는 파일 타입"}

        config = cls.PROCESSING_CONFIG[file_type]

        # 필수 키 존재 확인
        required_keys = [
            "required_columns",
            "field_mappings",
            "sql_fields",
            "query_name",
        ]
        for key in required_keys:
            if key not in config:
                return {"valid": False, "error": f"누락된 설정 키: {key}"}

        # 필드 매핑과 SQL 필드 일치 확인
        field_mapping_fields = [field for field, _ in config["field_mappings"]]
        sql_fields = config["sql_fields"]

        if field_mapping_fields != sql_fields:
            return {
                "valid": False,
                "error": f"필드 매핑과 SQL 필드 불일치: {field_mapping_fields} vs {sql_fields}",
            }

        return {"valid": True, "message": "설정이 일관성 있게 구성됨"}

    @classmethod
    def process_file(cls, file_type: str, df: pd.DataFrame) -> list[tuple]:
        """
        설정 기반 파일 처리

        Args:
            file_type: 파일 타입 (diner_basic, diner_categories 등)
            df: 처리할 DataFrame

        Returns:
            처리된 데이터 튜플 리스트
        """
        if file_type not in cls.PROCESSING_CONFIG:
            raise ValueError(f"지원하지 않는 파일 타입: {file_type}")

        config = cls.PROCESSING_CONFIG[file_type]
        field_mappings = config["field_mappings"]

        data = []
        for row_idx, (_, row) in enumerate(df.iterrows()):
            processed_row = []

            for field_name, data_type in field_mappings:
                if field_name not in row:
                    raise ValueError(f"컬럼 '{field_name}'이 DataFrame에 없습니다")

                converter = cls.TYPE_CONVERTERS.get(data_type)
                if not converter:
                    raise ValueError(f"지원하지 않는 데이터 타입: {data_type}")

                try:
                    processed_value = converter(row[field_name])
                    # INTEGER 타입인 경우 범위 검증 (BigInteger로 변경했지만 혹시 모를 경우 대비)
                    # 실제로는 모델이 BigInteger이므로 검증은 선택사항
                    processed_row.append(processed_value)
                except (ValueError, OverflowError) as e:
                    # 원본 행 인덱스 포함하여 오류 메시지 개선
                    original_row_idx = (
                        df.index[row_idx]
                        if hasattr(df.index, "__getitem__")
                        else row_idx
                    )
                    raise ValueError(
                        f"행 {original_row_idx}, 필드 '{field_name}' 처리 실패: {str(e)}\n"
                        f"원본 값: {row[field_name]}"
                    ) from e

            data.append(tuple(processed_row))

        return data

    # 기존 메서드들을 새로운 구조로 래핑 (하위 호환성 유지)
    @classmethod
    def process_diner_basic(cls, df: pd.DataFrame) -> list[tuple]:
        """diner_basic.csv 데이터 처리"""
        return cls.process_file("diner_basic", df)

    @classmethod
    def process_diner_categories(cls, df: pd.DataFrame) -> list[tuple]:
        """diner_categories.csv 데이터 처리"""
        return cls.process_file("diner_categories", df)

    @classmethod
    def process_diner_menus(cls, df: pd.DataFrame) -> list[tuple]:
        """diner_menus.csv 데이터 처리"""
        return cls.process_file("diner_menus", df)

    @classmethod
    def process_diner_reviews(cls, df: pd.DataFrame) -> list[tuple]:
        """diner_reviews.csv 데이터 처리"""
        return cls.process_file("diner_reviews", df)

    @classmethod
    def process_diner_tags(cls, df: pd.DataFrame) -> list[tuple]:
        """diner_tags.csv 데이터 처리"""
        return cls.process_file("diner_tags", df)

    @classmethod
    def add_new_file_type(
        cls,
        file_type: str,
        required_columns: list[str],
        field_mappings: list[tuple[str, str]],
    ) -> None:
        """
        새로운 파일 타입 추가

        Args:
            file_type: 파일 타입명
            required_columns: 필수 컬럼 리스트
            field_mappings: 필드명과 데이터 타입 매핑 리스트
        """
        cls.PROCESSING_CONFIG[file_type] = {
            "required_columns": required_columns,
            "field_mappings": field_mappings,
        }

    @classmethod
    def add_custom_converter(cls, type_name: str, converter_func: Callable) -> None:
        """
        커스텀 데이터 타입 변환기 추가

        Args:
            type_name: 타입명
            converter_func: 변환 함수
        """
        cls.TYPE_CONVERTERS[type_name] = converter_func
