"""
衝突回避サービス
カメラ画像から障害物を検出し、衝突を回避する
"""
import cv2
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CollisionAvoidance:
    """衝突回避サービス"""

    def __init__(self, safety_distance_threshold: float = 0.3):
        """
        衝突回避を初期化する

        Args:
            safety_distance_threshold: 安全距離の閾値（画像幅に対する比率）
        """
        self.safety_distance_threshold = safety_distance_threshold
        self._is_initialized = True

    def detect_obstacles(self, image: np.ndarray) -> bool:
        """
        障害物を検出する

        Args:
            image: 検出対象の画像

        Returns:
            bool: 障害物が検出された場合True
        """
        if not self._is_initialized:
            return False

        try:
            # グレースケール変換
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # エッジ検出
            edges = cv2.Canny(gray, 50, 150)

            # 画像の下部領域（ロボットの進行方向）を分析
            height, width = edges.shape
            roi_height = int(height * 0.6)  # 下60%を確認
            roi = edges[roi_height:, :]

            # エッジの密度を計算
            edge_density = np.sum(roi > 0) / roi.size

            # 密度が高い場合は障害物あり
            obstacle_detected = edge_density > 0.2

            if obstacle_detected:
                logger.warning(f"障害物検出（エッジ密度: {edge_density:.3f}）")

            return obstacle_detected

        except Exception as e:
            logger.error(f"障害物検出エラー: {e}")
            return False

    def is_safe_to_move(self, image: np.ndarray, direction: str) -> bool:
        """
        指定方向への移動が安全かを判定する

        Args:
            image: 現在の画像
            direction: 移動方向 ("forward", "backward", "left", "right")

        Returns:
            bool: 移動が安全な場合True
        """
        if direction in ["left", "right", "backward"]:
            # 旋回や後退は比較的安全
            return True

        # 前進の場合は障害物チェック
        if direction == "forward":
            return not self.detect_obstacles(image)

        return True

    def calculate_safe_direction(self, image: np.ndarray) -> Optional[str]:
        """
        安全な移動方向を計算する

        Args:
            image: 現在の画像

        Returns:
            Optional[str]: 安全な方向、見つからない場合None
        """
        try:
            # 画像を左・中央・右に分割して分析
            height, width = image.shape[:2]
            roi_height = int(height * 0.6)

            left_region = image[roi_height:, :width//3]
            center_region = image[roi_height:, width//3:2*width//3]
            right_region = image[roi_height:, 2*width//3:]

            # 各領域のエッジ密度を計算
            def get_edge_density(region):
                gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                return np.sum(edges > 0) / edges.size

            left_density = get_edge_density(left_region)
            center_density = get_edge_density(center_region)
            right_density = get_edge_density(right_region)

            logger.info(f"エッジ密度 - 左: {left_density:.3f}, 中央: {center_density:.3f}, 右: {right_density:.3f}")

            # 最もエッジ密度が低い（障害物が少ない）方向を選択
            min_density = min(left_density, center_density, right_density)

            if min_density > 0.3:
                # すべての方向が混雑している場合
                logger.warning("すべての方向に障害物あり")
                return None

            if center_density == min_density:
                return "forward"
            elif left_density == min_density:
                return "left"
            else:
                return "right"

        except Exception as e:
            logger.error(f"安全方向計算エラー: {e}")
            return None
