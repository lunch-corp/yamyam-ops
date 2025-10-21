"""
사용자 서비스
"""

from typing import List

from fastapi import HTTPException, status

from ..core.db import db
from ..core.firebase_auth import firebase_auth
from ..schemas.user import UserCreate, UserResponse, UserUpdate
from .base_service import BaseService


class UserService(BaseService[UserCreate, UserUpdate, UserResponse]):
    """사용자 서비스"""

    def __init__(self):
        super().__init__("users", "id")

    def create(self, data: UserCreate) -> UserResponse:
        """사용자 생성 (PostgreSQL DB에 직접 생성)"""
        try:
            with db.get_cursor() as (cursor, conn):
                # 중복 사용자 확인 (firebase_uid 기준)
                if self._check_exists(
                    "SELECT 1 FROM users WHERE firebase_uid = %s", (data.firebase_uid,)
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="이미 등록된 사용자입니다.",
                    )

                # ULID 생성
                user_id = self._generate_ulid()

                cursor.execute(
                    """
                    INSERT INTO users (id, firebase_uid, name, email, display_name, photo_url)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, firebase_uid, name, email, display_name, photo_url,
                              created_at, updated_at
                    """,
                    (
                        user_id,
                        data.firebase_uid,
                        data.name,
                        data.email,
                        data.display_name,
                        data.photo_url,
                    ),
                )

                result = cursor.fetchone()
                conn.commit()

                return self._convert_to_response(result)

        except Exception as e:
            self._handle_exception("creating user", e)

    def get_by_id(self, user_id: str) -> UserResponse:
        """ID(ULID)로 사용자 조회"""
        query = """
            SELECT id, firebase_uid, name, email, display_name, photo_url,
                   created_at, updated_at
            FROM users WHERE id = %s
        """

        result = self._execute_query(query, (user_id,))
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다.",
            )

        return self._convert_to_response(result)

    def get_by_firebase_uid(self, firebase_uid: str) -> UserResponse:
        """Firebase UID로 사용자 조회"""
        query = """
            SELECT id, firebase_uid, name, email, display_name, photo_url,
                   created_at, updated_at
            FROM users WHERE firebase_uid = %s
        """

        result = self._execute_query(query, (firebase_uid,))
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다.",
            )

        return self._convert_to_response(result)

    def get_list(
        self, skip: int = 0, limit: int = 100, **filters
    ) -> List[UserResponse]:
        """사용자 목록 조회"""
        fields = [
            "id",
            "firebase_uid",
            "name",
            "email",
            "display_name",
            "photo_url",
            "created_at",
            "updated_at",
        ]

        query, params = self._build_select_query(
            fields, order_by="created_at DESC", limit=limit, offset=skip
        )

        results = self._execute_query_all(query, params)
        return [self._convert_to_response(row) for row in results]

    def update(self, user_id: str, data: UserUpdate) -> UserResponse:
        """사용자 정보 업데이트 (PostgreSQL DB에서 직접 업데이트)"""
        # 사용자 존재 확인
        if not self._check_exists("SELECT 1 FROM users WHERE id = %s", (user_id,)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다.",
            )

        # 업데이트할 필드 구성
        update_fields = []
        update_values = []

        field_mapping = {
            "name": data.name,
            "email": data.email,
            "display_name": data.display_name,
            "photo_url": data.photo_url,
        }

        for field, value in field_mapping.items():
            if value is not None:
                update_fields.append(f"{field} = %s")
                update_values.append(value)

        query, params = self._build_update_query(
            update_fields, update_values, "id", user_id
        )

        result = self._execute_query(query, params)
        return self._convert_to_response(result)

    def delete(self, user_id: str) -> dict:
        """사용자 삭제 (PostgreSQL DB에서 직접 삭제)"""
        query = f"DELETE FROM {self.table_name} WHERE {self.primary_key_field} = %s RETURNING id"

        result = self._execute_query(query, (user_id,))
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
            query = "SELECT id FROM users WHERE firebase_uid = %s"
            result = self._execute_query(query, (firebase_uid,))

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
                            "SELECT id FROM users WHERE firebase_uid = %s",
                            (firebase_uid,),
                        )
                        existing_user = cursor.fetchone()

                        if existing_user:
                            # Firebase 정보로 업데이트
                            cursor.execute(
                                """
                                UPDATE users 
                                SET name = %s, email = %s, display_name = %s, 
                                    photo_url = %s, updated_at = CURRENT_TIMESTAMP
                                WHERE firebase_uid = %s
                                """,
                                (name, email, display_name, photo_url, firebase_uid),
                            )
                            updated_count += 1
                        else:
                            # 새로운 사용자 생성 (ULID 생성)
                            user_id = self._generate_ulid()
                            cursor.execute(
                                """
                                INSERT INTO users (id, firebase_uid, name, email, display_name, photo_url)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                """,
                                (
                                    user_id,
                                    firebase_uid,
                                    name,
                                    email,
                                    display_name,
                                    photo_url,
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

    def _convert_to_response(self, row: dict) -> UserResponse:
        """데이터베이스 행을 응답 모델로 변환"""
        return UserResponse(
            id=row["id"],
            firebase_uid=row["firebase_uid"],
            name=row["name"],
            email=row["email"],
            display_name=row["display_name"],
            photo_url=row["photo_url"],
            created_at=row["created_at"].isoformat(),
            updated_at=row["updated_at"].isoformat(),
        )
