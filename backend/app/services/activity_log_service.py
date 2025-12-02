"""
활동 로그 서비스
"""

import csv
import io
from datetime import datetime
from typing import Any, Optional

from fastapi import HTTPException, status

from app.core.db import db
from app.database.activity_log_queries import (
    COUNT_LOGS_BY_EVENT_TYPE,
    GET_ACTIVITY_LOGS_BY_FIREBASE_UID,
    GET_ACTIVITY_LOGS_BY_SESSION,
    GET_ACTIVITY_LOGS_BY_TYPE,
    GET_ACTIVITY_LOGS_WITH_FILTER,
    GET_LOGS_FOR_ML,
    GET_TOP_CLICKED_DINERS,
    GET_USER_PREFERRED_CATEGORIES,
    INSERT_ACTIVITY_LOG,
)
from app.database.user_queries import GET_USER_ID_BY_FIREBASE_UID
from app.schemas.activity_log import (
    ActivityLogCreate,
    ActivityLogExport,
    ActivityLogFilter,
    ActivityLogResponse,
)
from app.services.base_service import BaseService


class ActivityLogService(
    BaseService[ActivityLogCreate, dict[str, Any], ActivityLogResponse]
):
    """활동 로그 서비스"""

    def __init__(self):
        super().__init__("user_activity_logs", "id")

    # BaseService의 추상 메서드 구현
    def create(
        self, data: ActivityLogCreate, dry_run: bool = False
    ) -> ActivityLogResponse:
        """레코드 생성 (BaseService 추상 메서드)"""
        if dry_run:
            log_id = self._generate_ulid()
            return ActivityLogResponse(
                id=log_id,
                user_id="",
                firebase_uid=data.firebase_uid,
                session_id=data.session_id,
                event_type=data.event_type,
                event_timestamp=datetime.now().isoformat(),
                page=data.page,
                location_query=data.location_query,
                location_address=data.location_address,
                location_lat=data.location_lat,
                location_lon=data.location_lon,
                location_method=data.location_method,
                search_radius_km=data.search_radius_km,
                selected_large_categories=data.selected_large_categories,
                selected_middle_categories=data.selected_middle_categories,
                sort_by=data.sort_by,
                period=data.period,
                selected_city=data.selected_city,
                selected_region=data.selected_region,
                selected_grades=data.selected_grades,
                clicked_diner_idx=data.clicked_diner_idx,
                clicked_diner_name=data.clicked_diner_name,
                display_position=data.display_position,
                additional_data=data.additional_data,
                user_agent=data.user_agent,
                ip_address=data.ip_address,
            )
        return self.create_log(data)

    def get_by_id(self, id_value: str, dry_run: bool = False) -> ActivityLogResponse:
        """ID로 레코드 조회 (BaseService 추상 메서드)"""
        try:
            query = (
                f"SELECT * FROM {self.table_name} WHERE {self.primary_key_field} = %s"
            )
            result = self._execute_query(query, (id_value,), dry_run)

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="활동 로그를 찾을 수 없습니다.",
                )

            return self._convert_to_response(result)
        except HTTPException:
            raise
        except Exception as e:
            self._handle_exception("getting activity log by id", e)

    def get_list(
        self, skip: int = 0, limit: int = 100, dry_run: bool = False, **filters
    ) -> list[ActivityLogResponse]:
        """레코드 목록 조회 (BaseService 추상 메서드)"""
        try:
            query = f"SELECT * FROM {self.table_name}"
            params = []
            conditions = []

            # 필터 적용
            if filters.get("firebase_uid"):
                conditions.append("firebase_uid = %s")
                params.append(filters["firebase_uid"])

            if filters.get("event_type"):
                conditions.append("event_type = %s")
                params.append(filters["event_type"])

            if filters.get("session_id"):
                conditions.append("session_id = %s")
                params.append(filters["session_id"])

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY event_timestamp DESC"
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, skip])

            results = self._execute_query_all(query, tuple(params), dry_run)
            return [self._convert_to_response(row) for row in results]
        except Exception as e:
            self._handle_exception("getting activity log list", e)

    def update(
        self, id_value: str, data: dict[str, Any], dry_run: bool = False
    ) -> ActivityLogResponse:
        """레코드 업데이트 (BaseService 추상 메서드)"""
        try:
            # 업데이트 가능한 필드 목록
            updateable_fields = [
                "page",
                "location_query",
                "location_address",
                "location_lat",
                "location_lon",
                "location_method",
                "search_radius_km",
                "selected_large_categories",
                "selected_middle_categories",
                "sort_by",
                "period",
                "selected_city",
                "selected_region",
                "selected_grades",
                "clicked_diner_idx",
                "clicked_diner_name",
                "display_position",
                "additional_data",
                "user_agent",
                "ip_address",
            ]

            update_fields = []
            update_values = []

            for field in updateable_fields:
                if field in data and data[field] is not None:
                    update_fields.append(f"{field} = %s")
                    update_values.append(data[field])

            if not update_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="업데이트할 필드가 없습니다.",
                )

            # user_activity_logs 테이블에는 updated_at 컬럼이 없으므로 직접 쿼리 작성
            query = f"""
                UPDATE {self.table_name}
                SET {", ".join(update_fields)}
                WHERE {self.primary_key_field} = %s
                RETURNING *
            """
            update_values.append(id_value)

            result = self._execute_query(query, tuple(update_values), dry_run)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="활동 로그를 찾을 수 없습니다.",
                )

            return self._convert_to_response(result)
        except HTTPException:
            raise
        except Exception as e:
            self._handle_exception("updating activity log", e)

    def delete(self, id_value: str, dry_run: bool = False) -> dict[str, str]:
        """레코드 삭제 (BaseService 추상 메서드)"""
        try:
            # 먼저 존재 여부 확인
            check_query = (
                f"SELECT 1 FROM {self.table_name} WHERE {self.primary_key_field} = %s"
            )
            if not self._check_exists(check_query, (id_value,), dry_run):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="활동 로그를 찾을 수 없습니다.",
                )

            # 삭제 실행
            delete_query = f"DELETE FROM {self.table_name} WHERE {self.primary_key_field} = %s RETURNING {self.primary_key_field}"
            self._execute_query(delete_query, (id_value,), dry_run)

            if dry_run:
                return {"message": "Dry run: would delete activity log", "id": id_value}

            return {"message": "활동 로그가 삭제되었습니다.", "id": id_value}
        except HTTPException:
            raise
        except Exception as e:
            self._handle_exception("deleting activity log", e)

    def create_log(self, data: ActivityLogCreate) -> ActivityLogResponse:
        """활동 로그 생성"""
        try:
            with db.get_cursor() as (cursor, conn):
                # Firebase UID로 user_id 조회
                cursor.execute(GET_USER_ID_BY_FIREBASE_UID, (data.firebase_uid,))
                user_result = cursor.fetchone()

                if not user_result:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="사용자를 찾을 수 없습니다.",
                    )

                user_id = user_result["id"]

                # ULID 생성
                log_id = self._generate_ulid()

                # 로그 삽입
                cursor.execute(
                    INSERT_ACTIVITY_LOG,
                    (
                        log_id,
                        user_id,
                        data.firebase_uid,
                        data.session_id,
                        data.event_type,
                        data.page,
                        data.location_query,
                        data.location_address,
                        data.location_lat,
                        data.location_lon,
                        data.location_method,
                        data.search_radius_km,
                        data.selected_large_categories,
                        data.selected_middle_categories,
                        data.sort_by,
                        data.period,
                        data.selected_city,
                        data.selected_region,
                        data.selected_grades,
                        data.clicked_diner_idx,
                        data.clicked_diner_name,
                        data.display_position,
                        data.additional_data,
                        data.user_agent,
                        data.ip_address,
                    ),
                )

                result = cursor.fetchone()
                conn.commit()

                return self._convert_to_response(result)

        except Exception as e:
            self._handle_exception("creating activity log", e)

    def get_user_logs(
        self, firebase_uid: str, limit: int = 100, offset: int = 0
    ) -> list[ActivityLogResponse]:
        """사용자별 로그 조회"""
        results = self._execute_query_all(
            GET_ACTIVITY_LOGS_BY_FIREBASE_UID, (firebase_uid, limit, offset)
        )
        return [self._convert_to_response(row) for row in results]

    def get_session_logs(self, session_id: str) -> list[ActivityLogResponse]:
        """세션별 로그 조회"""
        results = self._execute_query_all(GET_ACTIVITY_LOGS_BY_SESSION, (session_id,))
        return [self._convert_to_response(row) for row in results]

    def get_logs_by_type(
        self, event_type: str, limit: int = 100, offset: int = 0
    ) -> list[ActivityLogResponse]:
        """이벤트 타입별 로그 조회"""
        results = self._execute_query_all(
            GET_ACTIVITY_LOGS_BY_TYPE, (event_type, limit, offset)
        )
        return [self._convert_to_response(row) for row in results]

    def get_logs_with_filter(
        self, firebase_uid: str, filter_params: ActivityLogFilter
    ) -> list[ActivityLogResponse]:
        """필터를 적용한 로그 조회"""
        results = self._execute_query_all(
            GET_ACTIVITY_LOGS_WITH_FILTER,
            (
                firebase_uid,
                filter_params.event_type,
                filter_params.event_type,
                filter_params.page,
                filter_params.page,
                filter_params.start_date,
                filter_params.start_date,
                filter_params.end_date,
                filter_params.end_date,
                filter_params.limit,
                filter_params.offset,
            ),
        )
        return [self._convert_to_response(row) for row in results]

    def export_logs_for_ml(self, export_params: ActivityLogExport) -> dict[str, Any]:
        """ML 학습용 데이터 추출"""
        try:
            results = self._execute_query_all(
                GET_LOGS_FOR_ML,
                (
                    export_params.start_date,
                    export_params.start_date,
                    export_params.end_date,
                    export_params.end_date,
                    export_params.event_types,
                    export_params.event_types,
                ),
            )

            if export_params.format == "csv":
                return self._convert_to_csv(results)
            else:
                return {"data": [dict(row) for row in results], "count": len(results)}

        except Exception as e:
            self._handle_exception("exporting logs for ML", e)

    def get_statistics(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> dict[str, Any]:
        """로그 통계 조회"""
        try:
            # 기본 날짜 설정
            if not start_date:
                start_date = (datetime.now().replace(day=1)).isoformat()
            if not end_date:
                end_date = datetime.now().isoformat()

            # 이벤트 타입별 카운트
            event_counts = self._execute_query_all(
                COUNT_LOGS_BY_EVENT_TYPE, (start_date, end_date)
            )

            # 인기 음식점
            top_diners = self._execute_query_all(
                GET_TOP_CLICKED_DINERS, (start_date, end_date, 20)
            )

            return {
                "period": {"start": start_date, "end": end_date},
                "event_counts": [dict(row) for row in event_counts],
                "top_clicked_diners": [dict(row) for row in top_diners],
            }

        except Exception as e:
            self._handle_exception("getting statistics", e)

    def get_user_preferences(self, firebase_uid: str) -> dict[str, Any]:
        """사용자 선호도 분석"""
        try:
            categories = self._execute_query_all(
                GET_USER_PREFERRED_CATEGORIES, (firebase_uid,)
            )

            return {
                "firebase_uid": firebase_uid,
                "preferred_categories": [dict(row) for row in categories],
            }

        except Exception as e:
            self._handle_exception("getting user preferences", e)

    def _convert_to_response(self, row: dict) -> ActivityLogResponse:
        """데이터베이스 행을 응답 모델로 변환"""
        return ActivityLogResponse(
            id=row["id"],
            user_id=row["user_id"],
            firebase_uid=row["firebase_uid"],
            session_id=row["session_id"],
            event_type=row["event_type"],
            event_timestamp=row["event_timestamp"].isoformat(),
            page=row.get("page"),
            location_query=row.get("location_query"),
            location_address=row.get("location_address"),
            location_lat=row.get("location_lat"),
            location_lon=row.get("location_lon"),
            location_method=row.get("location_method"),
            search_radius_km=row.get("search_radius_km"),
            selected_large_categories=row.get("selected_large_categories"),
            selected_middle_categories=row.get("selected_middle_categories"),
            sort_by=row.get("sort_by"),
            period=row.get("period"),
            selected_city=row.get("selected_city"),
            selected_region=row.get("selected_region"),
            selected_grades=row.get("selected_grades"),
            clicked_diner_idx=row.get("clicked_diner_idx"),
            clicked_diner_name=row.get("clicked_diner_name"),
            display_position=row.get("display_position"),
            additional_data=row.get("additional_data"),
            user_agent=row.get("user_agent"),
            ip_address=row.get("ip_address"),
        )

    def _convert_to_csv(self, results: list[dict]) -> dict[str, Any]:
        """결과를 CSV 형식으로 변환"""
        if not results:
            return {"data": "", "count": 0}

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows([dict(row) for row in results])

        return {"data": output.getvalue(), "count": len(results), "format": "csv"}


# 서비스 인스턴스
activity_log_service = ActivityLogService()
