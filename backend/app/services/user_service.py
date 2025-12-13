"""
사용자 서비스
"""

from fastapi import HTTPException, status

from app.core.db import db
from app.core.firebase_auth import firebase_auth
from app.database.user_queries import (
    CHECK_USER_EXISTS,
    CHECK_USER_EXISTS_BY_ID,
    DELETE_USER_BY_ID,
    GET_ALL_USERS,
    GET_USER_BY_FIREBASE_UID,
    GET_USER_BY_ID,
    GET_USER_ID_BY_FIREBASE_UID,
    INSERT_USER,
    INSERT_USER_FOR_SYNC,
    INSERT_USER_FROM_FIREBASE,
    UPDATE_USER_BY_FIREBASE_UID,
    UPDATE_USER_BY_ID,
    UPDATE_USER_ONBOARDING,
)
from app.schemas.user import (
    OnboardingDataCreate,
    UserCreate,
    UserIdType,
    UserResponse,
    UserUpdate,
)
from app.services.base_service import BaseService


class UserService(BaseService[UserCreate, UserUpdate, UserResponse]):
    """사용자 서비스"""

    def __init__(self):
        super().__init__("users", "id")

    def create(self, data: UserCreate) -> UserResponse:
        """사용자 생성 (PostgreSQL DB에 직접 생성)"""
        try:
            with db.get_cursor() as (cursor, conn):
                # 중복 사용자 확인 (firebase_uid 기준)
                if self._check_exists(CHECK_USER_EXISTS, (data.firebase_uid,)):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="이미 등록된 사용자입니다.",
                    )

                # ULID 생성
                user_id = self._generate_ulid()

                cursor.execute(
                    INSERT_USER,
                    (
                        user_id,
                        data.firebase_uid,
                        data.name,
                        data.email,
                        data.display_name,
                        data.photo_url,
                        None,  # kakao_reviewer_id not yet set
                    ),
                )

                result = cursor.fetchone()
                conn.commit()

                return self._convert_to_response(result)

        except Exception as e:
            self._handle_exception("creating user", e)

    def get_by_id(self, user_id: str, user_id_type: UserIdType) -> UserResponse:
        """ID(ULID) 또는 FIREBASE_UID로 사용자 조회"""

        # Choose the correct query based on user_id_type
        if user_id_type == UserIdType.ID:
            result = self._execute_query(GET_USER_BY_ID, (user_id,))
        else:  # firebase_uid
            result = self._execute_query(GET_USER_BY_FIREBASE_UID, (user_id,))

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다.",
            )

        return self._convert_to_response(result)

    def get_by_firebase_uid(self, firebase_uid: str) -> UserResponse:
        """Firebase UID로 사용자 조회"""

        result = self._execute_query(GET_USER_BY_FIREBASE_UID, (firebase_uid,))
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다.",
            )

        return self._convert_to_response(result)

    def get_list(
        self, skip: int = 0, limit: int = 100, **filters
    ) -> list[UserResponse]:
        """사용자 목록 조회"""
        results = self._execute_query_all(GET_ALL_USERS, (limit, skip))
        return [self._convert_to_response(row) for row in results]

    def update(
        self, user_id: str, data: UserUpdate, user_id_type: UserIdType = UserIdType.ID
    ) -> UserResponse:
        """사용자 정보 업데이트 (PostgreSQL DB에서 직접 업데이트)"""
        # Choose the correct existence check and update query based on user_id_type
        if user_id_type == UserIdType.ID:
            exists_query = CHECK_USER_EXISTS_BY_ID
            update_query_template = UPDATE_USER_BY_ID
        else:  # firebase_uid
            exists_query = CHECK_USER_EXISTS
            update_query_template = UPDATE_USER_BY_FIREBASE_UID

        # 사용자 존재 확인
        if not self._check_exists(exists_query, (user_id,)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다.",
            )

        # 업데이트할 필드와 값 구성 (None이 아닌 값만)
        update_fields = []
        update_values = []

        for field, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = %s")
                update_values.append(value)

        # 업데이트할 필드가 없으면 에러
        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="업데이트할 필드가 없습니다.",
            )

        # 동적으로 쿼리 생성
        fields_str = ", ".join(update_fields) + ","
        update_query = update_query_template.format(fields=fields_str)

        # user_id를 마지막에 추가
        update_values.append(user_id)

        result = self._execute_query(update_query, tuple(update_values))
        return self._convert_to_response(result)

    def delete(self, user_id: str) -> dict:
        """사용자 삭제 (PostgreSQL DB에서 직접 삭제)"""
        result = self._execute_query(DELETE_USER_BY_ID, (user_id,))
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다.",
            )

        return {"message": "사용자가 성공적으로 삭제되었습니다."}

    def sync_with_firebase(self, firebase_uid: str) -> UserResponse:
        """Firebase Auth 정보를 기반으로 단일 사용자 동기화"""
        try:
            # Firebase에서 최신 사용자 정보 가져오기
            firebase_user = firebase_auth.get_user_by_uid(firebase_uid)
            if not firebase_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Firebase 사용자를 찾을 수 없습니다.",
                )

            # DB에서 기존 사용자 조회
            result = self._execute_query(GET_USER_ID_BY_FIREBASE_UID, (firebase_uid,))

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="DB에 등록된 사용자를 찾을 수 없습니다.",
                )

            user_id = result["id"]

            # Firebase 정보로 업데이트
            update_data = UserUpdate(
                name=firebase_user.get("display_name")
                or firebase_user.get("email", "").split("@")[0],
                email=firebase_user.get("email"),
                display_name=firebase_user.get("display_name"),
                photo_url=firebase_user.get("photo_url"),
            )

            return self.update(user_id, update_data)

        except Exception as e:
            self._handle_exception("syncing with firebase", e)

    def sync_all_from_firebase(self) -> dict:
        """Firebase Auth의 모든 사용자를 DB에 동기화 (전체 동기화)"""
        try:
            from firebase_admin import auth

            # Firebase에서 모든 사용자 가져오기
            page = auth.list_users()
            users = page.users

            created_count = 0
            updated_count = 0
            error_count = 0
            errors = []

            with db.get_cursor() as (cursor, conn):
                for user in users:
                    try:
                        firebase_uid = user.uid
                        email = user.email
                        display_name = user.display_name
                        photo_url = user.photo_url
                        name = display_name or (
                            email.split("@")[0] if email else firebase_uid
                        )

                        # 사용자가 이미 존재하는지 확인
                        cursor.execute(
                            GET_USER_ID_BY_FIREBASE_UID,
                            (firebase_uid,),
                        )
                        existing_user = cursor.fetchone()

                        if existing_user:
                            # Firebase 정보로 업데이트
                            cursor.execute(
                                UPDATE_USER_BY_FIREBASE_UID,
                                (name, email, display_name, photo_url, firebase_uid),
                            )
                            updated_count += 1
                        else:
                            # 새로운 사용자 생성 (ULID 생성)
                            user_id = self._generate_ulid()
                            cursor.execute(
                                INSERT_USER_FOR_SYNC,
                                (
                                    user_id,
                                    firebase_uid,
                                    name,
                                    email,
                                    display_name,
                                    photo_url,
                                    None,  # kakao_reviewer_id not yet set
                                ),
                            )
                            created_count += 1

                    except Exception as e:
                        error_count += 1
                        errors.append(f"{firebase_uid}: {str(e)}")

                conn.commit()

            return {
                "message": "Firebase 사용자 동기화 완료",
                "total_users": len(users),
                "created": created_count,
                "updated": updated_count,
                "errors": error_count,
                "error_details": errors[:10]
                if errors
                else [],  # 최대 10개의 오류만 반환
            }

        except Exception as e:
            self._handle_exception("syncing all users from firebase", e)

    def create_from_firebase(
        self, firebase_uid: str, email: str | None, name: str
    ) -> UserResponse:
        """Firebase 회원가입 직후 사용자 생성"""
        try:
            with db.get_cursor() as (cursor, conn):
                # 중복 사용자 확인
                if self._check_exists(CHECK_USER_EXISTS, (firebase_uid,)):
                    # 이미 존재하는 경우 기존 사용자 반환
                    result = self._execute_query(
                        GET_USER_BY_FIREBASE_UID, (firebase_uid,)
                    )
                    return self._convert_to_response(result)

                # ULID 생성
                user_id = self._generate_ulid()

                cursor.execute(
                    INSERT_USER_FROM_FIREBASE,
                    (
                        user_id,
                        firebase_uid,
                        name,
                        email,
                        name,  # display_name = name
                        None,  # photo_url
                    ),
                )

                result = cursor.fetchone()
                conn.commit()

                return self._convert_to_response(result)

        except Exception as e:
            self._handle_exception("creating user from firebase", e)

    def update_onboarding(
        self, firebase_uid: str, onboarding_data: OnboardingDataCreate
    ) -> UserResponse:
        """온보딩 완료 시 사용자 프로필 업데이트"""
        try:
            import logging
            from datetime import datetime

            from psycopg2.extras import Json

            logger = logging.getLogger(__name__)

            with db.get_cursor() as (cursor, conn):
                # 사용자 존재 확인
                if not self._check_exists(CHECK_USER_EXISTS, (firebase_uid,)):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="사용자를 찾을 수 없습니다.",
                    )

                # 온보딩 완료 시각
                onboarding_completed_at = datetime.now()

                # 디버깅: 원본 데이터 타입 및 값 로깅
                logger.info("=== 온보딩 데이터 디버깅 시작 ===")
                logger.info(
                    f"dining_companions: type={type(onboarding_data.dining_companions)}, value={onboarding_data.dining_companions}"
                )
                logger.info(
                    f"food_preferences_large: type={type(onboarding_data.food_preferences_large)}, value={onboarding_data.food_preferences_large}"
                )
                logger.info(
                    f"food_preferences_middle: type={type(onboarding_data.food_preferences_middle)}, value={onboarding_data.food_preferences_middle}"
                )
                logger.info(
                    f"restaurant_ratings: type={type(onboarding_data.restaurant_ratings)}, value={onboarding_data.restaurant_ratings}"
                )

                # 리스트 타입 처리 (psycopg2가 자동으로 ARRAY로 변환)
                # None이면 None, 빈 리스트면 빈 리스트 그대로 전달
                dining_companions_array = (
                    onboarding_data.dining_companions
                    if onboarding_data.dining_companions is not None
                    else None
                )
                food_preferences_large_array = (
                    onboarding_data.food_preferences_large
                    if onboarding_data.food_preferences_large is not None
                    else None
                )

                # dict 타입을 psycopg2.extras.Json으로 변환 (JSONB 타입에 적합)
                # 빈 dict도 Json({})로 변환
                if onboarding_data.food_preferences_middle is not None:
                    food_preferences_middle_json = Json(
                        onboarding_data.food_preferences_middle
                    )
                    logger.info(
                        f"food_preferences_middle_json: type={type(food_preferences_middle_json)}, value={food_preferences_middle_json}"
                    )
                else:
                    food_preferences_middle_json = None
                    logger.info("food_preferences_middle_json: None")

                if onboarding_data.restaurant_ratings is not None:
                    restaurant_ratings_json = Json(onboarding_data.restaurant_ratings)
                    logger.info(
                        f"restaurant_ratings_json: type={type(restaurant_ratings_json)}, value={restaurant_ratings_json}"
                    )
                else:
                    restaurant_ratings_json = None
                    logger.info("restaurant_ratings_json: None")

                # 디버깅: 변환된 데이터 타입 로깅
                logger.info("=== 변환된 데이터 타입 ===")
                logger.info(
                    f"dining_companions_array: type={type(dining_companions_array)}, value={dining_companions_array}"
                )
                logger.info(
                    f"food_preferences_large_array: type={type(food_preferences_large_array)}, value={food_preferences_large_array}"
                )

                # 모든 파라미터를 튜플로 구성
                params = (
                    True,  # is_personalization_enabled
                    True,  # has_completed_onboarding
                    onboarding_completed_at,
                    onboarding_data.location,
                    onboarding_data.location_method,
                    onboarding_data.user_lat,
                    onboarding_data.user_lon,
                    onboarding_data.birth_year,
                    onboarding_data.gender,
                    dining_companions_array,
                    onboarding_data.regular_budget,
                    onboarding_data.special_budget,
                    onboarding_data.spice_level,
                    onboarding_data.allergies,
                    onboarding_data.dislikes,
                    food_preferences_large_array,
                    food_preferences_middle_json,
                    restaurant_ratings_json,
                    firebase_uid,
                )

                # 디버깅: 모든 파라미터 타입 검증
                logger.info("=== 파라미터 타입 검증 ===")
                param_names = [
                    "is_personalization_enabled",
                    "has_completed_onboarding",
                    "onboarding_completed_at",
                    "location",
                    "location_method",
                    "user_lat",
                    "user_lon",
                    "birth_year",
                    "gender",
                    "dining_companions",
                    "regular_budget",
                    "special_budget",
                    "spice_level",
                    "allergies",
                    "dislikes",
                    "food_preferences_large",
                    "food_preferences_middle",
                    "restaurant_ratings",
                    "firebase_uid",
                ]

                for i, (name, value) in enumerate(zip(param_names, params)):
                    logger.info(f"param[{i}] {name}: type={type(value)}, value={value}")
                    # dict 타입이 Json으로 변환되지 않은 경우 감지
                    if isinstance(value, dict) and name not in [
                        "food_preferences_middle",
                        "restaurant_ratings",
                    ]:
                        logger.error(
                            f"ERROR: {name} is dict type but not converted to Json!"
                        )

                logger.info("=== SQL 실행 시작 ===")
                cursor.execute(UPDATE_USER_ONBOARDING, params)
                logger.info("=== SQL 실행 완료 ===")

                result = cursor.fetchone()
                conn.commit()

                return self._convert_to_response(result)

        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(
                f"온보딩 데이터 업데이트 중 오류 발생: {type(e).__name__}: {str(e)}"
            )
            logger.exception("상세 오류 정보:")
            self._handle_exception("updating onboarding data", e)

    def _convert_to_response(self, row: dict) -> UserResponse:
        """데이터베이스 행을 응답 모델로 변환"""
        return UserResponse(
            id=row["id"],
            firebase_uid=row["firebase_uid"],
            kakao_reviewer_id=row.get("kakao_reviewer_id"),
            name=row["name"],
            email=row["email"],
            display_name=row["display_name"],
            photo_url=row["photo_url"],
            created_at=row["created_at"].isoformat(),
            updated_at=row["updated_at"].isoformat(),
            is_personalization_enabled=row.get("is_personalization_enabled"),
            has_completed_onboarding=row.get("has_completed_onboarding"),
            onboarding_completed_at=row["onboarding_completed_at"].isoformat()
            if row.get("onboarding_completed_at")
            else None,
            location=row.get("location"),
            location_method=row.get("location_method"),
            user_lat=row.get("user_lat"),
            user_lon=row.get("user_lon"),
            birth_year=row.get("birth_year"),
            gender=row.get("gender"),
            dining_companions=row.get("dining_companions"),
            regular_budget=row.get("regular_budget"),
            special_budget=row.get("special_budget"),
            spice_level=row.get("spice_level"),
            allergies=row.get("allergies"),
            dislikes=row.get("dislikes"),
            food_preferences_large=row.get("food_preferences_large"),
            food_preferences_middle=row.get("food_preferences_middle"),
            restaurant_ratings=row.get("restaurant_ratings"),
        )
