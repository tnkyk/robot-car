"""
音声合成インフラ
テキストを音声に変換してスピーカーから出力する
"""
import pyttsx3
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class VoiceSynthesizer:
    """音声合成クラス"""

    def __init__(self, rate: int = 150, volume: float = 1.0):
        """
        音声合成を初期化する

        Args:
            rate: 話速（デフォルト: 150）
            volume: 音量（0.0～1.0、デフォルト: 1.0）
        """
        self.rate = rate
        self.volume = volume
        self.engine: Optional[pyttsx3.Engine] = None
        self._is_initialized = False

    def initialize(self) -> bool:
        """
        音声合成エンジンを初期化する

        Returns:
            bool: 初期化成功時True
        """
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)

            # 日本語音声の設定（利用可能な場合）
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'japanese' in voice.name.lower() or 'ja' in voice.languages:
                    self.engine.setProperty('voice', voice.id)
                    break

            self._is_initialized = True
            logger.info(f"音声合成初期化成功 (速度: {self.rate}, 音量: {self.volume})")
            return True

        except Exception as e:
            logger.error(f"音声合成初期化エラー: {e}")
            return False

    def speak(self, text: str, blocking: bool = True) -> bool:
        """
        テキストを音声で発話する

        Args:
            text: 発話するテキスト
            blocking: ブロッキング動作（True: 発話完了まで待機、False: 非同期）

        Returns:
            bool: 発話成功時True
        """
        if not self._is_initialized or self.engine is None:
            logger.warning("音声合成エンジンが初期化されていません")
            return False

        try:
            logger.info(f"発話: {text}")
            self.engine.say(text)

            if blocking:
                self.engine.runAndWait()

            return True

        except Exception as e:
            logger.error(f"音声合成エラー: {e}")
            return False

    def stop(self) -> None:
        """現在の発話を停止する"""
        if self.engine is not None:
            try:
                self.engine.stop()
                logger.info("発話停止")
            except Exception as e:
                logger.error(f"発話停止エラー: {e}")

    def shutdown(self) -> None:
        """音声合成エンジンをシャットダウンする"""
        if self.engine is not None:
            try:
                self.engine.stop()
                self._is_initialized = False
                logger.info("音声合成リソース解放完了")
            except Exception as e:
                logger.error(f"音声合成シャットダウンエラー: {e}")

    def __enter__(self):
        """コンテキストマネージャー: with文でのエントリー"""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー: with文での終了時"""
        self.shutdown()
