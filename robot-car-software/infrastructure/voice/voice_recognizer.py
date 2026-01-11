"""
音声認識インフラ
マイクから音声を取得し、テキストに変換する
"""
import speech_recognition as sr
from typing import Optional
import logging
import re

logger = logging.getLogger(__name__)


class VoiceRecognizer:
    """音声認識クラス"""

    WAKE_WORD = "hey tom"  # ウェイクワード

    def __init__(self, language: str = "ja-JP", energy_threshold: int = 4000):
        """
        音声認識を初期化する

        Args:
            language: 認識言語（デフォルト: 日本語）
            energy_threshold: 音声検出の閾値（デフォルト: 4000）
        """
        self.language = language
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.microphone: Optional[sr.Microphone] = None
        self._is_initialized = False

    def initialize(self) -> bool:
        """
        マイクを初期化する

        Returns:
            bool: 初期化成功時True
        """
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                logger.info("マイク調整中...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

            self._is_initialized = True
            logger.info(f"マイク初期化成功 (閾値: {self.recognizer.energy_threshold})")
            return True

        except Exception as e:
            logger.error(f"マイク初期化エラー: {e}")
            return False

    def listen(self, timeout: Optional[float] = None, phrase_time_limit: Optional[float] = None) -> Optional[str]:
        """
        音声を聞き取り、テキストに変換する

        Args:
            timeout: リスニングのタイムアウト（秒）
            phrase_time_limit: フレーズの最大長（秒）

        Returns:
            Optional[str]: 認識されたテキスト、失敗時None
        """
        if not self._is_initialized or self.microphone is None:
            logger.warning("マイクが初期化されていません")
            return None

        try:
            with self.microphone as source:
                logger.info("音声入力待機中...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            logger.info("音声認識中...")
            text = self.recognizer.recognize_google(audio, language=self.language)
            logger.info(f"認識結果: {text}")
            return text

        except sr.WaitTimeoutError:
            logger.warning("音声入力タイムアウト")
            return None
        except sr.UnknownValueError:
            logger.warning("音声を認識できませんでした")
            return None
        except sr.RequestError as e:
            logger.error(f"音声認識サービスエラー: {e}")
            return None
        except Exception as e:
            logger.error(f"音声認識エラー: {e}")
            return None

    def detect_wake_word(self, timeout: Optional[float] = None) -> bool:
        """
        ウェイクワード（"Hey, Tom"）を検出する

        Args:
            timeout: リスニングのタイムアウト（秒）

        Returns:
            bool: ウェイクワードが検出された場合True
        """
        text = self.listen(timeout=timeout, phrase_time_limit=5)
        if text is None:
            return False

        # テキストを正規化（小文字化、記号削除）
        normalized_text = re.sub(r'[^\w\s]', '', text.lower())
        wake_word_normalized = re.sub(r'[^\w\s]', '', self.WAKE_WORD.lower())

        detected = wake_word_normalized in normalized_text
        if detected:
            logger.info(f"ウェイクワード検出: {text}")

        return detected

    def listen_command(self, timeout: float = 10.0) -> Optional[str]:
        """
        ユーザーコマンドを聞き取る

        Args:
            timeout: リスニングのタイムアウト（秒）

        Returns:
            Optional[str]: 認識されたコマンド、失敗時None
        """
        return self.listen(timeout=timeout, phrase_time_limit=10)

    def __enter__(self):
        """コンテキストマネージャー: with文でのエントリー"""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー: with文での終了時"""
        self._is_initialized = False
        logger.info("音声認識リソース解放完了")
