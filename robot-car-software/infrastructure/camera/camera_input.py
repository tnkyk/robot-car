"""
カメラ入力インフラ
Webカメラから画像を取得する
"""
import cv2
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CameraInput:
    """カメラ入力クラス"""

    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        """
        カメラを初期化する

        Args:
            camera_index: カメラのインデックス（デフォルト: 0）
            width: 画像の幅（デフォルト: 640）
            height: 画像の高さ（デフォルト: 480）
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.capture: Optional[cv2.VideoCapture] = None
        self._is_initialized = False

    def initialize(self) -> bool:
        """
        カメラを初期化する

        Returns:
            bool: 初期化成功時True
        """
        try:
            self.capture = cv2.VideoCapture(self.camera_index)
            if not self.capture.isOpened():
                logger.error(f"カメラ {self.camera_index} を開けませんでした")
                return False

            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

            self._is_initialized = True
            logger.info(f"カメラ初期化成功: {self.width}x{self.height}")
            return True

        except Exception as e:
            logger.error(f"カメラ初期化エラー: {e}")
            return False

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        フレームを取得する

        Returns:
            Optional[np.ndarray]: 取得した画像（BGRフォーマット）、失敗時None
        """
        if not self._is_initialized or self.capture is None:
            logger.warning("カメラが初期化されていません")
            return None

        try:
            ret, frame = self.capture.read()
            if not ret:
                logger.warning("フレーム取得失敗")
                return None
            return frame

        except Exception as e:
            logger.error(f"フレーム取得エラー: {e}")
            return None

    def release(self) -> None:
        """カメラリソースを解放する"""
        if self.capture is not None:
            self.capture.release()
            self._is_initialized = False
            logger.info("カメラリソース解放完了")

    def __enter__(self):
        """コンテキストマネージャー: with文でのエントリー"""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー: with文での終了時"""
        self.release()
