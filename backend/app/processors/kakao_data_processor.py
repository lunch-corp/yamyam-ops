"""
Kakao 데이터 처리 전용 클래스 - 설정 기반 처리
"""

import ast
import json
from collections.abc import Callable

import pandas as pd

from app.utils.ulid_utils import generate_ulid


class KakaoDataProcessor:
    """Kakao 데이터 처리 전용 클래스 - 설정 기반 처리"""

    # 각 파일별 처리 설정 (필수 컬럼 + 변환 함수 + SQL 쿼리 정보)
    PROCESSING_CONFIG = {
        "diner_basic": {
            "required_columns": [
                "diner_idx",
                "diner_name",
                "diner_review_cnt",
                "diner_review_avg",
                "diner_road_address",
                "diner_num_address",
                "diner_phone",
                "diner_lat",
                "diner_lon",
            ],
            "field_mappings": [
                ("id", "ulid"),
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
                ("diner_grade", "int_nullable"),
                ("hidden_score", "float_nullable"),
                ("bayesian_score", "float_nullable"),
            ],
            "sql_fields": [
                "id",
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
                "diner_grade",
                "hidden_score",
                "bayesian_score",
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
                ("id", "ulid"),
                ("reviewer_id", "int"),
                ("reviewer_user_name", "str"),
                ("reviewer_review_cnt", "int"),
                ("reviewer_avg", "float"),
                ("badge_grade", "str"),
                ("badge_level", "int"),
            ],
            "sql_fields": [
                "id",
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
                ("id", "ulid"),
                ("diner_idx", "int"),
                ("reviewer_id", "int"),
                ("review_id", "int"),
                ("reviewer_review", "str_optional"),
                ("reviewer_review_date", "date_str"),
                ("reviewer_review_score", "float"),
            ],
            "sql_fields": [
                "id",
                "diner_idx",
                "reviewer_id",
                "review_id",
                "reviewer_review",
                "reviewer_review_date",
                "reviewer_review_score",
            ],
            "query_name": "INSERT_KAKAO_REVIEW",
        },
        "review_photos": {
            "required_columns": [
                "review_id",
                "photo_url",
            ],
            "field_mappings": [
                ("id", "ulid"),
                ("review_id", "str"),
                ("photo_url", "str"),
                ("original_photo_id", "int_nullable"),
                ("media_type", "str_default_photo"),
                ("status", "str_optional"),
                ("display_order", "int_default_zero"),
                ("view_count", "int_default_zero"),
            ],
            "sql_fields": [
                "id",
                "review_id",
                "photo_url",
                "original_photo_id",
                "media_type",
                "status",
                "display_order",
                "view_count",
            ],
            "query_name": "INSERT_REVIEW_PHOTO",
        },
        "diner_grade_bayesian": {
            "required_columns": [
                "diner_idx",
                "diner_grade",
                "bayesian_score",
            ],
            "field_mappings": [
                ("diner_grade", "int"),
                ("bayesian_score", "float"),
                ("diner_idx", "int"),
            ],
            "sql_fields": [
                "diner_grade",
                "bayesian_score",
                "diner_idx",
            ],
            "query_name": "UPDATE_KAKAO_DINER_GRADE_BAYESIAN",
        },
        "diner_hidden_score": {
            "required_columns": [
                "diner_idx",
                "hidden_score",
            ],
            "field_mappings": [
                ("hidden_score", "float"),
                ("diner_idx", "int"),
            ],
            "sql_fields": [
                "hidden_score",
                "diner_idx",
            ],
            "query_name": "UPDATE_KAKAO_DINER_HIDDEN_SCORE",
        },
        "diner_open_hours": {
            "required_columns": [
                "diner_idx",
                "day_of_week",
                "is_open",
            ],
            "field_mappings": [
                ("id", "ulid"),
                ("diner_idx", "int"),
                ("day_of_week", "int"),
                ("is_open", "bool"),
                ("start_time", "time_str"),
                ("end_time", "time_str"),
                ("description", "str_optional"),
            ],
            "sql_fields": [
                "id",
                "diner_idx",
                "day_of_week",
                "is_open",
                "start_time",
                "end_time",
                "description",
            ],
            "query_name": "INSERT_KAKAO_DINER_OPEN_HOURS",
        },
        "diner_menus_new": {
            "required_columns": [
                "diner_idx",
                "name",
                "product_id",
            ],
            "field_mappings": [
                ("id", "ulid"),
                ("diner_idx", "int"),
                ("name", "str"),
                ("product_id", "str"),
                ("price", "float_nullable"),
                ("is_ai_mate", "bool_nullable"),
                ("photo_url", "str_optional"),
                ("is_recommend", "bool_nullable"),
                ("desc", "str_optional"),
                ("mod_at", "datetime_str"),
            ],
            "sql_fields": [
                "id",
                "diner_idx",
                "name",
                "product_id",
                "price",
                "is_ai_mate",
                "photo_url",
                "is_recommend",
                "desc",
                "mod_at",
            ],
            "query_name": "INSERT_KAKAO_DINER_MENU",
        },
        "diner_ai_data": {
            "required_columns": [
                "diner_idx",
            ],
            "field_mappings": [
                ("id", "ulid"),
                ("diner_idx", "int"),
                ("ai_bottom_sheet_title", "str_optional"),
                ("ai_bottom_sheet_summary", "str_optional"),
                ("ai_bottom_sheet_sheets", "json_str"),
                ("ai_bottom_sheet_landing_url", "str_optional"),
                ("blog_summaries", "json_str"),
                # all_keywords는 서비스 레이어에서 자동 생성되므로 CSV에서 받지 않음
            ],
            "sql_fields": [
                "id",
                "diner_idx",
                "ai_bottom_sheet_title",
                "ai_bottom_sheet_summary",
                "ai_bottom_sheet_sheets",
                "ai_bottom_sheet_landing_url",
                "blog_summaries",
            ],
            "query_name": "INSERT_KAKAO_DINER_AI_DATA_CSV",
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

    @staticmethod
    def convert_json_string(x):
        """
        CSV에서 읽힌 문자열을 파싱하여 dict/list로 변환한 후 JSON 문자열로 반환
        - 작은따옴표/큰따옴표로 감싸진 JSON 문자열도 처리
        - JSON 파싱 실패 시 ast.literal_eval 시도 (Python 리터럴 형식)
        - 파싱된 dict/list를 JSON 문자열로 변환하여 반환
        - 실패 시 None 반환

        예:
        - '{"title": "test"}' -> '{"title": "test"}' (JSON 문자열)
        - "[{'title': '제공 서비스'}]" -> '[{"title": "제공 서비스"}]' (JSON 문자열)

        주의: PostgreSQL JSONB 타입에 저장하기 위해 JSON 문자열로 반환합니다.
        psycopg2가 자동으로 변환하지만, 명시적으로 JSON 문자열로 변환하는 것이 더 안전합니다.
        """
        # 결측치 처리
        if pd.isnull(x) or x is None:
            return None

        if not isinstance(x, str):
            # 이미 dict/list인 경우 JSON 문자열로 변환
            if isinstance(x, (dict, list)):
                try:
                    return json.dumps(x, ensure_ascii=False)
                except (TypeError, ValueError):
                    return None
            return None

        x_strip = x.strip()

        if x_strip == "" or x_strip == "nan":
            return None

        # 작은따옴표나 큰따옴표로 감싸진 경우 처리
        if (x_strip.startswith("'") and x_strip.endswith("'")) or (
            x_strip.startswith('"') and x_strip.endswith('"')
        ):
            x_strip = x_strip[1:-1]  # 따옴표 제거

        # list / dict 형태만 시도
        if (x_strip.startswith("{") and x_strip.endswith("}")) or (
            x_strip.startswith("[") and x_strip.endswith("]")
        ):
            parsed = None
            # 먼저 JSON 파싱 시도 (JSON 형식인 경우)
            try:
                parsed = json.loads(x_strip)
            except (ValueError, json.JSONDecodeError):
                # JSON 파싱 실패 시 ast.literal_eval 시도 (Python 리터럴 형식인 경우)
                try:
                    parsed = ast.literal_eval(x_strip)
                except (ValueError, SyntaxError):
                    # 파싱 실패 시 None 반환
                    return None

            # 파싱된 dict/list를 JSON 문자열로 변환
            if parsed is not None:
                try:
                    return json.dumps(parsed, ensure_ascii=False)
                except (TypeError, ValueError):
                    return None

        return None

    TYPE_CONVERTERS = {
        "str": lambda x: str(x) if pd.notnull(x) else None,
        "str_optional": lambda x: str(x) if pd.notnull(x) and str(x).strip() else None,
        "int": lambda x: int(x) if pd.notnull(x) else None,
        "int_nullable": lambda x: int(x) if pd.notnull(x) else None,
        "float": lambda x: float(x) if pd.notnull(x) else None,
        "float_nullable": lambda x: float(x) if pd.notnull(x) else None,
        "int_default_zero": lambda x: int(x) if pd.notnull(x) else 0,
        "float_default_zero": lambda x: float(x) if pd.notnull(x) else 0.0,
        "str_default_photo": lambda x: str(x).strip()
        if pd.notnull(x) and str(x).strip()
        else "PHOTO",
        "bool": lambda x: bool(x) if pd.notnull(x) else False,
        "bool_nullable": lambda x: bool(x) if pd.notnull(x) else None,
        "date_str": lambda x: str(x).strip()
        if pd.notnull(x) and str(x).strip()
        else None,
        "datetime_str": lambda x: str(x).strip()
        if pd.notnull(x) and str(x).strip() and str(x).lower() != "nan"
        else None,
        "time_str": lambda x: str(x).strip()
        if pd.notnull(x) and str(x).strip() and str(x).lower() != "nan"
        else None,
        "list_to_comma": lambda x: KakaoDataProcessor.convert_list_string_to_comma_separated(
            x
        ),
        "json_str": lambda x: KakaoDataProcessor.convert_json_string(x),
        "ulid": lambda x: generate_ulid(),  # ULID는 항상 새로 생성 (입력값 무시)
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
        required_columns = config.get("required_columns", [])

        data = []
        for row_idx, (_, row) in enumerate(df.iterrows()):
            processed_row = []

            for field_name, data_type in field_mappings:
                converter = cls.TYPE_CONVERTERS.get(data_type)
                if not converter:
                    raise ValueError(f"지원하지 않는 데이터 타입: {data_type}")

                # ulid 타입은 필드가 없어도 변환기 호출 (항상 새로 생성)
                if data_type == "ulid":
                    try:
                        processed_value = converter(None)  # ulid는 입력값 무시
                        processed_row.append(processed_value)
                        continue
                    except Exception as e:
                        original_row_idx = (
                            df.index[row_idx]
                            if hasattr(df.index, "__getitem__")
                            else row_idx
                        )
                        raise ValueError(
                            f"행 {original_row_idx}, 필드 '{field_name}' (ULID 생성) 처리 실패: {str(e)}"
                        ) from e

                # 필수 컬럼이 아닌 경우, CSV에 없으면 None 반환
                if field_name not in row:
                    if field_name in required_columns:
                        raise ValueError(
                            f"필수 컬럼 '{field_name}'이 DataFrame에 없습니다"
                        )
                    else:
                        # 선택 필드인 경우 None 반환
                        processed_row.append(None)
                        continue

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
