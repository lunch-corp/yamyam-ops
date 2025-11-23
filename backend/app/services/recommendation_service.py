import logging
import os

from scipy.sparse import csr_matrix
from yamyam_lab.data.config import DataConfig
from yamyam_lab.data.csr import CsrDatasetLoader
from yamyam_lab.model.classic_cf.user_based import UserBasedCollaborativeFiltering
from yamyam_lab.tools.config import load_yaml

from app.core.config import Settings
from app.services.kakao_diner_service import KakaoDinerService
from app.services.kakao_review_service import KakaoReviewService
from app.services.kakao_reviewer_service import KakaoReviewerService


class RecommendationService:
    CATEGORY_COLUMNS = [
        "industry_category",
        "diner_category_large",
        "diner_category_middle",
        "diner_category_small",
        "diner_category_detail",
    ]
    DINER_IDX = "diner_idx"

    def __init__(self):
        self.settings = Settings()
        self.config = load_yaml(self.settings.node2vec_config_path)
        self.preprocess_config = load_yaml(
            os.path.join(self.settings.config_root_path, "./preprocess/preprocess.yaml")
        )
        self.csr_matrix: csr_matrix = None
        self.user_mapping: dict = None
        self.diner_mapping: dict = None

    def _init_models(self):
        self._load_dataset()
        self._prepare_user_cf()
        self._remove_dataset()
        logging.info("Successfully initialized user_cf model")

    def _load_dataset(self):
        # at first, load all of the dataset.
        # however, after creating csr_matrix, those data will be removed
        self.review = KakaoReviewService().get_list()
        self.diner = KakaoDinerService().get_list()
        self.reivewer = KakaoReviewerService().get_list()
        self.diner_category = self.diner[[self.DINER_IDX] + self.CATEGORY_COLUMNS]
        self.diner = self.diner[
            [col for col in self.diner.columns if col not in self.CATEGORY_COLUMNS]
        ]
        logging.info("Successfully loaded data from postgres db")

    def _remove_dataset(self):
        for attr in ["review", "diner", "reivewer", "diner_category"]:
            if hasattr(self, attr):
                delattr(self, attr)
        logging.info("Successfully deleted data")

    def _prepare_user_cf(self):
        fe = self.config.preprocess.feature_engineering

        data_loader = CsrDatasetLoader(
            data_config=DataConfig(
                X_columns=["diner_idx", "reviewer_id"],
                y_columns=["reviewer_review_score"],
                user_engineered_feature_names=fe.user_engineered_feature_names,
                diner_engineered_feature_names=fe.diner_engineered_feature_names,
                is_timeseries_by_time_point=self.config.preprocess.data.is_timeseries_by_time_point,
                train_time_point=self.config.preprocess.data.train_time_point,
                val_time_point=self.config.preprocess.data.val_time_point,
                test_time_point=self.config.preprocess.data.test_time_point,
                end_time_point=self.config.preprocess.data.end_time_point,
                test=False,
                config_root_path=self.settings.config_root_path,
                data_source="local",  # local loading, not from google drive
                review=self.review,
                reviewer=self.reivewer,
                diner=self.diner,
                category=self.diner_category,
            ),
        )
        data = data_loader.prepare_csr_dataset(
            is_csr=True,
            filter_config=self.preprocess_config.filter,
        )

        self.csr_matrix = data["X_train"]
        self.user_mapping = data["user_mapping"]
        self.diner_mapping = data["diner_mapping"]

        self.user_cf = UserBasedCollaborativeFiltering(
            user_item_matrix=self.csr_matrix,
            user_mapping=self.user_mapping,
            item_mapping=self.diner_mapping,
        )

    def get_most_similar_reviewer_with_user_cf(
        self, liked_diner_ids: list[int], scores_of_liked_diner_ids: list[int]
    ):
        # initialize dataset if yet initialized
        if self.csr_matrix is None:
            self._init_models()

        return self.user_cf.find_similar_users(
            liked_item_ids=liked_diner_ids,
            scores_of_liked_items=scores_of_liked_diner_ids,
        )
