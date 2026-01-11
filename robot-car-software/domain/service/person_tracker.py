"""
人物追跡サービス
カメラ画像から特定の登録された人物を検出・追跡する
"""
import cv2
import numpy as np
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PersonTracker:
    """人物追跡サービス"""

    def __init__(self):
        """人物追跡を初期化する"""
        self.face_cascade: Optional[cv2.CascadeClassifier] = None
        self.registered_person_features: Optional[np.ndarray] = None
        self._is_initialized = False

    def initialize(self) -> bool:
        """
        人物追跡を初期化する（顔検出器の読み込み）

        Returns:
            bool: 初期化成功時True
        """
        try:
            # Haar Cascade分類器を読み込む
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)

            if self.face_cascade.empty():
                logger.error("顔検出器の読み込みに失敗しました")
                return False

            self._is_initialized = True
            logger.info("人物追跡初期化成功")
            return True

        except Exception as e:
            logger.error(f"人物追跡初期化エラー: {e}")
            return False

    def register_person(self, image: np.ndarray) -> bool:
        """
        特定の人物を登録する

        Args:
            image: 登録する人物の画像

        Returns:
            bool: 登録成功時True
        """
        if not self._is_initialized or self.face_cascade is None:
            logger.warning("人物追跡が初期化されていません")
            return False

        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) == 0:
                logger.warning("登録画像から顔が検出されませんでした")
                return False

            # 最初に検出された顔を登録
            x, y, w, h = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (100, 100))  # サイズ正規化

            # 特徴量として保存（簡易実装）
            self.registered_person_features = face_roi.flatten()

            logger.info("人物登録成功")
            return True

        except Exception as e:
            logger.error(f"人物登録エラー: {e}")
            return False

    def detect_registered_person(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        登録された人物を検出する

        Args:
            image: 検出対象の画像

        Returns:
            Optional[Tuple[int, int, int, int]]: 検出された人物の位置(x, y, width, height)、検出失敗時None
        """
        if not self._is_initialized or self.face_cascade is None:
            return None

        if self.registered_person_features is None:
            logger.warning("人物が登録されていません")
            return None

        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) == 0:
                return None

            # 各顔と登録された人物の類似度を計算
            best_match = None
            best_similarity = float('inf')

            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                face_roi = cv2.resize(face_roi, (100, 100))
                face_features = face_roi.flatten()

                # ユークリッド距離で類似度を計算（簡易実装）
                similarity = np.linalg.norm(face_features - self.registered_person_features)

                if similarity < best_similarity:
                    best_similarity = similarity
                    best_match = (x, y, w, h)

            # 類似度の閾値を設定（調整が必要）
            threshold = 50000
            if best_similarity < threshold:
                return best_match

            return None

        except Exception as e:
            logger.error(f"人物検出エラー: {e}")
            return None

    def calculate_direction_to_person(self, person_bbox: Tuple[int, int, int, int],
                                       image_width: int) -> str:
        """
        検出された人物への移動方向を計算する

        Args:
            person_bbox: 人物のバウンディングボックス (x, y, width, height)
            image_width: 画像の幅

        Returns:
            str: 移動方向 ("left", "right", "forward", "stop")
        """
        x, y, w, h = person_bbox
        person_center_x = x + w // 2
        image_center_x = image_width // 2

        # 中心からのずれを計算
        offset = person_center_x - image_center_x
        offset_threshold = image_width * 0.1  # 10%の誤差を許容

        if abs(offset) < offset_threshold:
            # 人物が画面中央にいる場合
            # サイズで距離を推定
            person_size_ratio = w / image_width
            if person_size_ratio > 0.4:  # 十分近い
                return "stop"
            else:
                return "forward"
        elif offset < 0:
            # 人物が左側にいる
            return "left"
        else:
            # 人物が右側にいる
            return "right"
