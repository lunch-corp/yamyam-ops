import logging

from fastapi import APIRouter, Body, HTTPException, status

from app.schemas.redis_schemas import (
    RedisCreateRequest,
    RedisDeleteRequest,
    RedisReadRequest,
    RedisReadResponse,
    RedisResponse,
    RedisUpdateRequest,
)
from app.services.redis_service import redis_service

router = APIRouter()


@router.post(
    "/",
    response_model=RedisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Redis Keys",
    description="Create one or more key-value pairs in Redis. For a single key, just include 1 item in items dict.",
)
async def create_redis_keys(request: RedisCreateRequest):
    """
    Redis CREATE operation

    - **items**: {key: value} dictionary (single or multiple)
    - **expire**: Expiration time in seconds for all keys

    Single key example: `{"items": {"1783192": {"diner_ids": ["57812123"]}}, "expire": 3600}`
    """
    try:
        results = await redis_service.create(items=request.items, expire=request.expire)

        succeeded = sum(1 for v in results.values() if v)
        failed = len(results) - succeeded

        return RedisResponse(
            success=failed == 0,
            message=f"Created {succeeded} key(s)"
            if failed == 0
            else f"Created {succeeded}/{len(results)} key(s)",
            data=results,
            stats={"total": len(results), "succeeded": succeeded, "failed": failed},
        )
    except Exception as e:
        logging.error(f"Redis create endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post(
    "/read",
    response_model=RedisReadResponse,
    summary="Read Redis Keys",
    description="Read one or more key values from Redis.",
)
async def read_redis_keys(request: RedisReadRequest = Body(...)):
    """
    Redis READ operation

    - **keys**: List of keys to read (single or multiple)

    Single key example: `{"keys": ["1783192"]}`
    """
    try:
        results = await redis_service.read(keys=request.keys)

        found = sum(1 for v in results.values() if v is not None)
        not_found = len(results) - found

        return RedisReadResponse(
            success=True,
            message=f"Read {found} key(s)"
            if not_found == 0
            else f"Read {found}/{len(results)} key(s)",
            data=results,
            stats={"total": len(results), "found": found, "not_found": not_found},
        )
    except Exception as e:
        logging.error(f"Redis read endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put(
    "/",
    response_model=RedisResponse,
    summary="Update Redis Keys",
    description="Update one or more key values in Redis.",
)
async def update_redis_keys(request: RedisUpdateRequest):
    """
    Redis UPDATE operation

    - **items**: {key: value} dictionary (single or multiple)
    - **expire**: Expiration time in seconds for all keys

    Single key example: `{"items": {"1783192": {"diner_ids": ["57812123"]}}, "expire": 7200}`
    """
    try:
        results = await redis_service.update(items=request.items, expire=request.expire)

        succeeded = sum(1 for v in results.values() if v)
        failed = len(results) - succeeded

        return RedisResponse(
            success=failed == 0,
            message=f"Updated {succeeded} key(s)"
            if failed == 0
            else f"Updated {succeeded}/{len(results)} key(s)",
            data=results,
            stats={"total": len(results), "succeeded": succeeded, "failed": failed},
        )
    except Exception as e:
        logging.error(f"Redis update endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete(
    "/",
    response_model=RedisResponse,
    summary="Delete Redis Keys",
    description="Delete one or more keys from Redis.",
)
async def delete_redis_keys(request: RedisDeleteRequest = Body(...)):
    """
    Redis DELETE operation

    - **keys**: List of keys to delete (single or multiple)

    Single key example: `{"keys": ["1783192"]}`
    """
    try:
        results = await redis_service.delete(keys=request.keys)

        succeeded = sum(1 for v in results.values() if v)
        failed = len(results) - succeeded

        return RedisResponse(
            success=failed == 0,
            message=f"Deleted {succeeded} key(s)"
            if failed == 0
            else f"Deleted {succeeded}/{len(results)} key(s)",
            data=results,
            stats={"total": len(results), "succeeded": succeeded, "failed": failed},
        )
    except Exception as e:
        logging.error(f"Redis delete endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete(
    "/",
    response_model=RedisResponse,
    summary="Delete Redis Key(s)",
    description="Redis에서 단일 또는 여러 키를 삭제합니다.",
)
async def delete_redis_key(request: RedisDeleteRequest = Body(...)):
    """
    Redis DELETE 작업 (단일/벌크 지원)

    **단일 작업:**
    - **key**: 삭제할 Redis 키

    **벌크 작업:**
    - **keys**: 삭제할 키 리스트
    """
    try:
        # 벌크 작업
        if request.keys is not None:
            results = await redis_service.bulk_delete(keys=request.keys)
            succeeded = sum(1 for v in results.values() if v)
            failed = len(results) - succeeded

            return RedisResponse(
                success=failed == 0,
                message="Bulk delete completed",
                data=results,
                is_bulk=True,
                stats={"total": len(results), "succeeded": succeeded, "failed": failed},
            )

        # 단일 작업
        elif request.key is not None:
            if not await redis_service.exists(request.key):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Key '{request.key}' not found",
                )

            success = await redis_service.delete(request.key)

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete key",
                )

            return RedisResponse(
                success=True,
                message=f"Key '{request.key}' deleted successfully",
                data={"key": request.key},
                is_bulk=False,
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either 'key' OR 'keys' must be provided",
            )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Redis delete endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get(
    "/health/ping",
    response_model=RedisResponse,
    summary="Redis Health Check",
    description="Check Redis connection status",
)
async def redis_health_check():
    """Check Redis connection status"""
    try:
        from app.core.redis_db import redis_db

        is_connected = await redis_db.ping()

        if not is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis is not available",
            )

        return RedisResponse(
            success=True,
            message="Redis is healthy",
            data={"status": "connected"},
            is_bulk=False,
        )
    except Exception as e:
        logging.error(f"Redis health check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )
    except Exception as e:
        logging.error(f"Redis bulk update endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
