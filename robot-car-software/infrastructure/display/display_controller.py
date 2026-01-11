"""
ディスプレイ表示インフラ
表情画像（GIFアニメーション対応）をディスプレイに表示する
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List
from enum import Enum
import logging
from PIL import Image
import time

logger = logging.getLogger(__name__)


class Expression(Enum):
    """表情の種類"""
    NEUTRAL = "neutral"      # 通常
    HAPPY = "happy"          # 笑顔
    SAD = "sad"              # 悲しい
    SURPRISED = "surprised"  # 驚き
    THINKING = "thinking"    # 考え中
    SLEEPY = "sleepy"        # 眠い


class DisplayController:
    """ディスプレイ表示コントローラー"""

    def __init__(self, expression_dir: str = "resources/expressions", fullscreen: bool = True):
        """
        ディスプレイコントローラーを初期化する

        Args:
            expression_dir: 表情画像が格納されているディレクトリ
            fullscreen: フルスクリーン表示（デフォルト: True）
        """
        self.expression_dir = Path(expression_dir)
        self.fullscreen = fullscreen
        self.window_name = "Robot Face"
        self.current_expression: Optional[Expression] = None
        # 表情データ: {Expression: {'frames': [frame1, frame2, ...], 'delays': [ms, ms, ...], 'is_animated': bool}}
        self.expressions: Dict[Expression, Dict] = {}
        self._is_initialized = False
        self._animation_thread = None
        self._stop_animation = False

    def initialize(self) -> bool:
        """
        ディスプレイを初期化する

        Returns:
            bool: 初期化成功時True
        """
        try:
            # ウィンドウを作成
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            if self.fullscreen:
                cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

            # 表情画像を読み込む
            self._load_expressions()

            self._is_initialized = True
            logger.info("ディスプレイ初期化成功")
            return True

        except Exception as e:
            logger.error(f"ディスプレイ初期化エラー: {e}")
            return False

    def _load_expressions(self) -> None:
        """表情画像（GIF）を読み込む"""
        if not self.expression_dir.exists():
            logger.warning(f"表情画像ディレクトリが存在しません: {self.expression_dir}")
            # デフォルト画像を生成
            self._create_default_expressions()
            return

        for expression in Expression:
            image_path = self.expression_dir / f"{expression.value}.gif"
            if image_path.exists():
                gif_data = self._load_gif(image_path)
                if gif_data is not None:
                    self.expressions[expression] = gif_data
                    logger.info(f"表情GIF読み込み: {expression.value} ({len(gif_data['frames'])}フレーム)")
                else:
                    logger.warning(f"表情GIF読み込み失敗: {image_path}")
            else:
                logger.warning(f"表情GIFが見つかりません: {image_path}")

        # 読み込めなかった表情はデフォルト画像を生成
        if len(self.expressions) == 0:
            self._create_default_expressions()

    def _load_gif(self, gif_path: Path) -> Optional[Dict]:
        """
        GIFファイルを読み込み、全フレームと遅延時間を取得する

        Args:
            gif_path: GIFファイルのパス

        Returns:
            Optional[Dict]: {'frames': [frame1, ...], 'delays': [ms, ...], 'is_animated': bool}
        """
        try:
            gif = Image.open(gif_path)
            frames = []
            delays = []

            # 全フレームを読み込む
            frame_index = 0
            while True:
                try:
                    gif.seek(frame_index)

                    # RGBに変換（透明度チャンネルを削除）
                    frame_rgb = gif.convert('RGB')

                    # numpy配列に変換してBGRに変換（OpenCV用）
                    frame_np = np.array(frame_rgb)
                    frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
                    frames.append(frame_bgr)

                    # フレーム遅延時間を取得（ミリ秒）
                    delay = gif.info.get('duration', 100)  # デフォルト100ms
                    delays.append(delay)

                    frame_index += 1

                except EOFError:
                    # 全フレーム読み込み完了
                    break

            if len(frames) == 0:
                logger.error(f"GIFフレームが読み込めませんでした: {gif_path}")
                return None

            return {
                'frames': frames,
                'delays': delays,
                'is_animated': len(frames) > 1
            }

        except Exception as e:
            logger.error(f"GIF読み込みエラー: {e}")
            return None

    def _create_default_expressions(self) -> None:
        """デフォルトの表情画像を生成する"""
        logger.info("デフォルト表情画像を生成中...")

        # 640x480の黒背景
        base_image = np.zeros((480, 640, 3), dtype=np.uint8)

        for expression in Expression:
            image = base_image.copy()

            # 白い円（顔）
            cv2.circle(image, (320, 240), 150, (255, 255, 255), -1)

            # 表情に応じた目と口を描画
            if expression == Expression.HAPPY:
                # 笑顔の目（^_^）
                cv2.ellipse(image, (270, 220), (30, 20), 0, 0, 180, (0, 0, 0), 3)
                cv2.ellipse(image, (370, 220), (30, 20), 0, 0, 180, (0, 0, 0), 3)
                # 笑顔の口
                cv2.ellipse(image, (320, 260), (60, 40), 0, 0, 180, (0, 0, 0), 3)
            elif expression == Expression.SAD:
                # 悲しい目
                cv2.circle(image, (270, 220), 10, (0, 0, 0), -1)
                cv2.circle(image, (370, 220), 10, (0, 0, 0), -1)
                # 悲しい口
                cv2.ellipse(image, (320, 300), (60, 40), 0, 180, 360, (0, 0, 0), 3)
            elif expression == Expression.SURPRISED:
                # 驚きの目（大きい円）
                cv2.circle(image, (270, 220), 20, (0, 0, 0), 3)
                cv2.circle(image, (370, 220), 20, (0, 0, 0), 3)
                # 驚きの口（O）
                cv2.circle(image, (320, 280), 30, (0, 0, 0), 3)
            else:  # NEUTRAL, THINKING, SLEEPY
                # 通常の目
                cv2.circle(image, (270, 220), 10, (0, 0, 0), -1)
                cv2.circle(image, (370, 220), 10, (0, 0, 0), -1)
                # 通常の口
                cv2.line(image, (280, 280), (360, 280), (0, 0, 0), 3)

            self.expressions[expression] = image

    def show_expression(self, expression: Expression) -> bool:
        """
        表情を表示する

        Args:
            expression: 表示する表情

        Returns:
            bool: 表示成功時True
        """
        if not self._is_initialized:
            logger.warning("ディスプレイが初期化されていません")
            return False

        if expression not in self.expressions:
            logger.warning(f"表情が読み込まれていません: {expression}")
            return False

        try:
            cv2.imshow(self.window_name, self.expressions[expression])
            cv2.waitKey(1)  # 画面更新
            self.current_expression = expression
            logger.info(f"表情表示: {expression.value}")
            return True

        except Exception as e:
            logger.error(f"表情表示エラー: {e}")
            return False

    def close(self) -> None:
        """ディスプレイを閉じる"""
        if self._is_initialized:
            cv2.destroyWindow(self.window_name)
            self._is_initialized = False
            logger.info("ディスプレイリソース解放完了")

    def __enter__(self):
        """コンテキストマネージャー: with文でのエントリー"""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー: with文での終了時"""
        self.close()
