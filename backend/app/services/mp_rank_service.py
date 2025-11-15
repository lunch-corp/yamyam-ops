import logging
from datetime import datetime
from typing import List, Optional, Union

from fastapi import HTTPException, status

from app.schemas.mp_rank import MostPopularRankRequest, MostPopularRankResponse

try:
    from yamyam_lab.data.config import DataConfig
    from yamyam_lab.data.mp_rank import MostPopularRankDataLoader
except ImportError as e:
    raise ImportError(f"yamyam-lab 패키지를 찾을 수 없습니다: {e}")

logger = logging.getLogger(__name__)


class MostPopularRankService:
    def __init__(self):
        self.base_data_config = DataConfig(config_root_path="/app")

    def get_top_diners(
        self, request: MostPopularRankRequest
    ) -> MostPopularRankResponse:
        validation_errors = self._validate_request(request)
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=validation_errors
            )

        reference_date = self._parse_reference_date(request.reference_date)

        dataloader = MostPopularRankDataLoader(
            data_config=self.base_data_config,
            diner_category_large=request.diner_category_large,
            diner_category_middle=request.diner_category_middle,
            rank_method=request.rank_method,
            lat=request.lat,
            lon=request.lon,
            period=request.period,
            reference_date=reference_date,
            topk=request.topk,
            min_review_count=request.min_review_count,
        )

        diner_ids = dataloader.load_topk_diners_rank()
        logger.info(f"Loaded {len(diner_ids)} diners")

        filters = {
            "diner_category_large": request.diner_category_large,
            "diner_category_middle": request.diner_category_middle,
            "lat": request.lat,
            "lon": request.lon,
            "reference_date": str(reference_date) if reference_date else None,
            "topk": request.topk,
            "min_review_count": request.min_review_count,
        }

        return MostPopularRankResponse(
            diner_ids=diner_ids,
            count=len(diner_ids),
            rank_method=request.rank_method,
            period=request.period,
            filters=filters,
        )

    def _parse_reference_date(
        self, reference_date: Optional[Union[str, datetime]]
    ) -> Optional[datetime]:
        if reference_date is None:
            return None
        if isinstance(reference_date, datetime):
            return reference_date
        if isinstance(reference_date, str):
            try:
                return datetime.strptime(reference_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Invalid date format: {reference_date}")
        raise ValueError(f"Unsupported type: {type(reference_date)}")

    def _validate_request(self, request: MostPopularRankRequest) -> List[str]:
        errors = []

        if request.rank_method == "distance":
            if request.lat is None:
                errors.append("lat required for distance ranking")
            if request.lon is None:
                errors.append("lon required for distance ranking")

        if request.lat is not None and not (-90 <= request.lat <= 90):
            errors.append("lat must be between -90 and 90")
        if request.lon is not None and not (-180 <= request.lon <= 180):
            errors.append("lon must be between -180 and 180")

        if not (1 <= request.topk <= 100):
            errors.append("topk must be between 1 and 100")

        if request.min_review_count < 0:
            errors.append("min_review_count must be non-negative")

        if isinstance(request.reference_date, str):
            try:
                datetime.strptime(request.reference_date, "%Y-%m-%d")
            except ValueError:
                errors.append("reference_date must be YYYY-MM-DD")

        return errors
