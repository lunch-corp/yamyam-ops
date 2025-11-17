import logging

from fastapi import HTTPException, status

from app.schemas.mp_rank import MostPopularRankRequest, MostPopularRankResponse

from yamyam_lab.data.config import DataConfig
from yamyam_lab.data.mp_rank import MostPopularRankDataLoader

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

        reference_date = request.reference_date

        dataloader = MostPopularRankDataLoader(
            data_config=self.base_data_config,
            diner_category_large=request.diner_category_large,
            diner_category_middle=request.diner_category_middle,
            rank_method=request.rank_method.value,  # Enum to str
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
            rank_method=request.rank_method,  # Enum
            period=request.period,
            filters=filters,
        )
