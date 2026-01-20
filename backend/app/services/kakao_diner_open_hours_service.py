"""
카카오 음식점 영업시간 서비스
"""

import logging
from datetime import datetime

from fastapi import HTTPException, status

from app.core.db import db
from app.database.kakao_queries import (
    DELETE_KAKAO_DINER_OPEN_HOURS_BY_ID,
    GET_KAKAO_DINER_OPEN_HOURS_BY_DINER_AND_DAY,
    GET_KAKAO_DINER_OPEN_HOURS_BY_DINER_IDX,
    GET_KAKAO_DINER_OPEN_HOURS_BY_ID,
    INSERT_KAKAO_DINER_OPEN_HOURS,
    UPDATE_KAKAO_DINER_OPEN_HOURS_BY_ID,
)
from app.schemas.kakao_diner_open_hours import (
    KakaoDinerOpenHoursCreate,
    KakaoDinerOpenHoursResponse,
    KakaoDinerOpenHoursUpdate,
)
from app.services.base_service import BaseService
from app.utils.ulid_utils import generate_ulid

logger = logging.getLogger(__name__)


class KakaoDinerOpenHoursService(
    BaseService[
        KakaoDinerOpenHoursCreate,
        KakaoDinerOpenHoursUpdate,
        KakaoDinerOpenHoursResponse,
    ]
):
    """카카오 음식점 영업시간 서비스"""

    def __init__(self):
        super().__init__("kakao_diner_open_hours", "id")

    def _convert_to_response(self, row) -> KakaoDinerOpenHoursResponse:
        """DB row를 Response 모델로 변환"""
        if not row:
            return None

        return KakaoDinerOpenHoursResponse(
            id=row[0],
            diner_idx=row[1],
            day_of_week=row[2],
            is_open=row[3],
            start_time=row[4],
            end_time=row[5],
            description=row[6],
            created_at=row[7],
            updated_at=row[8],
        )

    def get_by_diner_idx(self, diner_idx: int) -> list[KakaoDinerOpenHoursResponse]:
        """
        특정 음식점의 영업시간 조회 (모든 요일)

        Args:
            diner_idx: 음식점 인덱스

        Returns:
            영업시간 목록 (요일별)
        """
        try:
            with db.get_cursor() as (cursor, conn):
                cursor.execute(GET_KAKAO_DINER_OPEN_HOURS_BY_DINER_IDX, (diner_idx,))
                results = cursor.fetchall()
                return [self._convert_to_response(row) for row in results]
        except Exception as e:
            logger.warning(f"영업시간 조회 실패 (diner_idx={diner_idx}): {e}")
            return []

    def get_by_diner_and_day(
        self, diner_idx: int, day_of_week: int
    ) -> KakaoDinerOpenHoursResponse | None:
        """
        특정 음식점의 특정 요일 영업시간 조회

        Args:
            diner_idx: 음식점 인덱스
            day_of_week: 요일 (0=월요일, 6=일요일)

        Returns:
            영업시간 정보 (없으면 None, 조회 실패 시에도 None 반환)
        """
        try:
            with db.get_cursor() as (cursor, conn):
                cursor.execute(
                    GET_KAKAO_DINER_OPEN_HOURS_BY_DINER_AND_DAY,
                    (diner_idx, day_of_week),
                )
                result = cursor.fetchone()
                return self._convert_to_response(result) if result else None
        except Exception as e:
            # 영업시간 체크에서는 조회 실패 시 None 반환 (영업 중으로 간주)
            # DB 연결 오류나 데이터 없음 등은 정상적인 경우일 수 있으므로 DEBUG 레벨로만 로깅
            logger.debug(
                f"영업시간 조회 실패 (diner_idx={diner_idx}, day={day_of_week}): {str(e)[:100]}"
            )
            return None

    def is_open_at(self, diner_idx: int, check_datetime: datetime) -> bool:
        """
        특정 시간에 영업 중인지 판단

        Args:
            diner_idx: 음식점 인덱스
            check_datetime: 확인할 날짜시간

        Returns:
            영업 중이면 True, 아니면 False
            영업시간 데이터가 없으면 True (영업 중으로 간주)
        """
        try:
            # 요일과 시간 추출 (0=월요일, 6=일요일)
            day_of_week = check_datetime.weekday()
            check_time = check_datetime.time()

            # 영업시간 조회
            open_hours = self.get_by_diner_and_day(diner_idx, day_of_week)

            # 영업시간 데이터가 없으면 영업 중으로 간주
            if not open_hours:
                return True

            # is_open이 False면 휴무일
            if not open_hours.is_open:
                return False

            # start_time, end_time이 None이면 24시간 영업으로 간주
            if open_hours.start_time is None or open_hours.end_time is None:
                return True

            # 영업시간 체크
            # 자정을 넘어가는 경우 처리 (예: 23:00 ~ 02:00)
            if open_hours.start_time <= open_hours.end_time:
                # 일반적인 경우 (예: 09:00 ~ 18:00)
                return open_hours.start_time <= check_time <= open_hours.end_time
            else:
                # 자정을 넘어가는 경우 (예: 23:00 ~ 02:00)
                return (
                    check_time >= open_hours.start_time
                    or check_time <= open_hours.end_time
                )

        except Exception as e:
            logger.warning(
                f"영업시간 체크 중 오류 발생 (diner_idx={diner_idx}): {e}, 영업 중으로 간주"
            )
            # 오류 발생 시 영업 중으로 간주
            return True

    def filter_open_diners(
        self, diner_idx_list: list[int], check_datetime: datetime
    ) -> list[int]:
        """
        영업 중인 음식점만 필터링 (배치 쿼리 최적화)

        Args:
            diner_idx_list: 음식점 인덱스 리스트
            check_datetime: 확인할 날짜시간

        Returns:
            영업 중인 음식점 인덱스 리스트
        """
        if not diner_idx_list:
            return []

        try:
            # 요일과 시간 추출 (0=월요일, 6=일요일)
            day_of_week = check_datetime.weekday()
            check_time = check_datetime.time()

            # 배치 쿼리로 모든 영업시간을 한 번에 조회
            placeholders = ",".join(["%s"] * len(diner_idx_list))
            query = f"""
                SELECT diner_idx, is_open, start_time, end_time
                FROM kakao_diner_open_hours
                WHERE diner_idx IN ({placeholders}) AND day_of_week = %s
            """

            open_diners = []
            with db.get_cursor() as (cursor, conn):
                params = list(diner_idx_list) + [day_of_week]
                cursor.execute(query, params)
                results = cursor.fetchall()

                # 결과를 딕셔너리로 변환 (diner_idx -> 영업시간 정보)
                # RealDictCursor를 사용하므로 딕셔너리 접근 가능
                open_hours_map = {}
                for row in results:
                    diner_idx = row["diner_idx"]
                    open_hours_map[diner_idx] = {
                        "is_open": row["is_open"],
                        "start_time": row["start_time"],
                        "end_time": row["end_time"],
                    }

                # 각 음식점의 영업시간 체크
                for diner_idx in diner_idx_list:
                    if diner_idx not in open_hours_map:
                        # 영업시간 데이터가 없으면 영업 중으로 간주
                        open_diners.append(diner_idx)
                        continue

                    hours = open_hours_map[diner_idx]

                    # is_open이 False면 휴무일
                    if not hours["is_open"]:
                        continue

                    # start_time, end_time이 None이면 24시간 영업으로 간주
                    if hours["start_time"] is None or hours["end_time"] is None:
                        open_diners.append(diner_idx)
                        continue

                    # 영업시간 체크
                    # 자정을 넘어가는 경우 처리 (예: 23:00 ~ 02:00)
                    if hours["start_time"] <= hours["end_time"]:
                        # 일반적인 경우 (예: 09:00 ~ 18:00)
                        if hours["start_time"] <= check_time <= hours["end_time"]:
                            open_diners.append(diner_idx)
                    else:
                        # 자정을 넘어가는 경우 (예: 23:00 ~ 02:00)
                        if (
                            check_time >= hours["start_time"]
                            or check_time <= hours["end_time"]
                        ):
                            open_diners.append(diner_idx)

            logger.info(
                f"영업시간 필터링: {len(diner_idx_list)}개 중 {len(open_diners)}개 영업 중"
            )
            return open_diners

        except Exception as e:
            logger.error(f"영업시간 필터링 중 오류 발생: {e}, 전체 반환")
            # 오류 발생 시 전체 반환
            return diner_idx_list

    def create(
        self, data: KakaoDinerOpenHoursCreate, dry_run: bool = False
    ) -> KakaoDinerOpenHoursResponse:
        """영업시간 생성"""
        try:
            if dry_run:
                logger.info(
                    f"[DRY RUN] Creating open hours for diner_idx {data.diner_idx}"
                )
                return KakaoDinerOpenHoursResponse(
                    id="dry_run_id",
                    diner_idx=data.diner_idx,
                    day_of_week=data.day_of_week,
                    is_open=data.is_open,
                    start_time=data.start_time,
                    end_time=data.end_time,
                    description=data.description,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )

            with db.get_cursor() as (cursor, conn):
                ulid = generate_ulid()
                cursor.execute(
                    INSERT_KAKAO_DINER_OPEN_HOURS,
                    (
                        ulid,
                        data.diner_idx,
                        data.day_of_week,
                        data.is_open,
                        data.start_time,
                        data.end_time,
                        data.description,
                    ),
                )

                # 생성된 데이터 조회
                cursor.execute(GET_KAKAO_DINER_OPEN_HOURS_BY_ID, (ulid,))
                result = cursor.fetchone()
                conn.commit()

                return self._convert_to_response(result)

        except Exception as e:
            self._handle_exception("creating kakao diner open hours", e)

    def get_by_id(
        self, open_hours_id: str, dry_run: bool = False
    ) -> KakaoDinerOpenHoursResponse:
        """영업시간 ID로 조회"""
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Getting open hours by id: {open_hours_id}")
                return None

            with db.get_cursor() as (cursor, conn):
                cursor.execute(GET_KAKAO_DINER_OPEN_HOURS_BY_ID, (open_hours_id,))
                result = cursor.fetchone()

                if not result:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Open hours with id {open_hours_id} not found",
                    )

                return self._convert_to_response(result)

        except HTTPException:
            raise
        except Exception as e:
            self._handle_exception("getting kakao diner open hours by id", e)

    def get_list(
        self, skip: int = 0, limit: int = 100, dry_run: bool = False, **filters
    ) -> list[KakaoDinerOpenHoursResponse]:
        """영업시간 목록 조회"""
        try:
            if dry_run:
                logger.info("[DRY RUN] Getting open hours list")
                return []

            # 기본 쿼리 (필터링 미지원, 필요시 확장 가능)
            query = """
                SELECT id, diner_idx, day_of_week, is_open, start_time, end_time, description,
                       created_at, updated_at
                FROM kakao_diner_open_hours
                ORDER BY diner_idx, day_of_week
                LIMIT %s OFFSET %s
            """

            with db.get_cursor() as (cursor, conn):
                cursor.execute(query, (limit, skip))
                results = cursor.fetchall()
                return [self._convert_to_response(row) for row in results]

        except Exception as e:
            self._handle_exception("getting kakao diner open hours list", e)

    def update(
        self,
        open_hours_id: str,
        data: KakaoDinerOpenHoursUpdate,
        dry_run: bool = False,
    ) -> KakaoDinerOpenHoursResponse:
        """영업시간 업데이트"""
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Updating open hours: {open_hours_id}")
                # 기존 데이터 조회
                existing = self.get_by_id(open_hours_id, dry_run=True)
                if not existing:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Open hours with id {open_hours_id} not found",
                    )
                return existing

            # 기존 데이터 조회
            existing = self.get_by_id(open_hours_id)

            # 업데이트할 값 결정 (None이면 기존 값 유지)
            diner_idx = (
                data.diner_idx if data.diner_idx is not None else existing.diner_idx
            )
            day_of_week = (
                data.day_of_week
                if data.day_of_week is not None
                else existing.day_of_week
            )
            is_open = data.is_open if data.is_open is not None else existing.is_open
            start_time = (
                data.start_time if data.start_time is not None else existing.start_time
            )
            end_time = data.end_time if data.end_time is not None else existing.end_time
            description = (
                data.description
                if data.description is not None
                else existing.description
            )

            with db.get_cursor() as (cursor, conn):
                cursor.execute(
                    UPDATE_KAKAO_DINER_OPEN_HOURS_BY_ID,
                    (
                        diner_idx,
                        day_of_week,
                        is_open,
                        start_time,
                        end_time,
                        description,
                        open_hours_id,
                    ),
                )
                result = cursor.fetchone()
                conn.commit()

                if not result:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Open hours with id {open_hours_id} not found",
                    )

                return self._convert_to_response(result)

        except HTTPException:
            raise
        except Exception as e:
            self._handle_exception("updating kakao diner open hours", e)

    def delete(self, open_hours_id: str, dry_run: bool = False) -> dict[str, str]:
        """영업시간 삭제"""
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Deleting open hours: {open_hours_id}")
                return {"id": open_hours_id, "status": "deleted (dry run)"}

            with db.get_cursor() as (cursor, conn):
                cursor.execute(DELETE_KAKAO_DINER_OPEN_HOURS_BY_ID, (open_hours_id,))
                result = cursor.fetchone()
                conn.commit()

                if not result:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Open hours with id {open_hours_id} not found",
                    )

                return {"id": result[0], "status": "deleted"}

        except HTTPException:
            raise
        except Exception as e:
            self._handle_exception("deleting kakao diner open hours", e)
