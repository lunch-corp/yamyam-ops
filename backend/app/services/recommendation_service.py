import logging
import os

from scipy.sparse import csr_matrix
from yamyam_lab.data.config import DataConfig
from yamyam_lab.data.csr import CsrDatasetLoader
from yamyam_lab.model.classic_cf.user_based import UserBasedCollaborativeFiltering
from yamyam_lab.tools.config import load_yaml

from app.api.v1.users import user_service
from app.api.v1.vector_db import vector_db_service
from app.core.config import Settings
from app.schemas.user import UserIdType
from app.schemas.vector_db import VectorType
from app.services.kakao_diner_service import KakaoDinerService
from app.services.kakao_review_service import KakaoReviewService
from app.services.kakao_reviewer_service import KakaoReviewerService


class RecommendationService:
    CATEGORY_COLUMNS = [
        "diner_category_large",
        "diner_category_middle",
        "diner_category_small",
        "diner_category_detail",
    ]
    DINER_IDX = "diner_idx"

    def __init__(self) -> None:
        self.settings = Settings()
        self.config = load_yaml(self.settings.node2vec_config_path)
        self.preprocess_config = load_yaml(
            os.path.join(self.settings.config_root_path, "./preprocess/preprocess.yaml")
        )
        self.csr_matrix: csr_matrix = None
        self.user_mapping: dict = None
        self.diner_mapping: dict = None

    def _init_models(self) -> None:
        self._load_dataset()
        self._prepare_user_cf()
        self._remove_dataset()
        logging.info("Successfully initialized user_cf model")

    def _load_dataset(self) -> None:
        # at first, load all of the dataset.
        # however, after creating csr_matrix, those data will be removed
        self.review = KakaoReviewService().get_list(use_dataframe=True)
        self.diner = KakaoDinerService().get_list(use_dataframe=True)
        self.reviewer = KakaoReviewerService().get_list(use_dataframe=True)

        # convert string type to integer because their data types are defined as String.
        # refer to app/models for more detail defined table schema
        self.review["reviewer_id"] = self.review["reviewer_id"].astype(int)
        self.review["review_id"] = self.review["review_id"].astype(int)
        self.reviewer["reviewer_id"] = self.reviewer["reviewer_id"].astype(int)

        self.diner_category = self.diner[[self.DINER_IDX] + self.CATEGORY_COLUMNS]
        self.diner = self.diner[
            [col for col in self.diner.columns if col not in self.CATEGORY_COLUMNS]
        ]
        logging.info("Successfully loaded data from postgres db")

    def _remove_dataset(self) -> None:
        for attr in ["review", "diner", "reivewer", "diner_category"]:
            if hasattr(self, attr):
                delattr(self, attr)
        logging.info("Successfully deleted data")

    def _prepare_user_cf(self) -> None:
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
                validate_data=False,  # do not validate data
                data_source="local",  # local loading, not from google drive
                review=self.review,
                reviewer=self.reviewer,
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
    ) -> int:
        """
        Get most similar one reviewer to what2eat user using user cf.

        Args:
            liked_diner_ids (List[int]): List of diner_ids which what2eat users gave ratings.
            scores_of_liked_diner_ids (List[int]): List of scores related with `liked_diner_ids`.

        Returns (int):
            Reviewer id using User Based CF.
        """
        # initialize dataset if yet initialized
        if self.csr_matrix is None:
            logging.info("Loading dataset and user_cf model for first time")
            self._init_models()
        else:
            logging.info("Using loaded user_cf model")

        return self.user_cf.find_similar_users(
            liked_item_ids=liked_diner_ids,
            scores_of_liked_items=scores_of_liked_diner_ids,
        )

    def get_personalized_ranked_diners(
        self, firebase_uid: str, diner_ids: list[int]
    ) -> list[int]:
        """
        Given firebase_uid, find matched kakao_reviewer_id and sort diner_ids with
        personalized ranking using embedding of searched kakao_reviewer_id and diner_ids.

        Args:
            firebase_uid (str): Unique value in firebase.
            diner_ids (list[int]): List of diner_ids to be ranked.

        Returns (list[int]):
            Personalized ranked diner_ids.
        """
        # get kakao_reviewer_id from `users` table
        kakao_reviewer_id = user_service.get_by_id(
            user_id=firebase_uid,
            user_id_type=UserIdType.FIREBASE_UID,
        ).kakao_reviewer_id

        logging.info(f"Get kakao_reviewer_id: {kakao_reviewer_id}")

        # if user does not have kakao_reviewer_id, raise error
        if kakao_reviewer_id is None:
            raise ValueError(
                "kakao_reviewer_id must be set for personal recommendation"
            )

        # get embedding for kakao_reviewer_id
        user_embedding = vector_db_service.search_vector(
            vector_type=VectorType.USER_N2V_VEC, id=kakao_reviewer_id
        ).embedding

        # sort diner_ids using score, i.e., dot product btw user and diner embeddings
        sorted_result = vector_db_service.get_similar(
            vector_type=VectorType.DINER_N2V_VEC,
            query_id=kakao_reviewer_id,
            query_vec=user_embedding,
            top_k=None,
            filtering_ids=diner_ids,
        ).neighbors

        logging.info("Sorted result")
        logging.info("\n".join([f"{res.id}: {res.score}" for res in sorted_result]))

        return [res.id for res in sorted_result], [res.score for res in sorted_result]
