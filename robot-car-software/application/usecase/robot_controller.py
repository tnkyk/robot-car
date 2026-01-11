"""
ロボット統合コントローラー
すべてのコンポーネントを統合し、ロボットの動作を制御する
"""
from typing import Optional
from enum import Enum
import logging
import time

from infrastructure.motor import Motor
from infrastructure.camera import CameraInput
from infrastructure.voice import VoiceRecognizer, VoiceSynthesizer
from infrastructure.display import DisplayController, Expression
from domain.service import PersonTracker, CollisionAvoidance, TaskPlanner

logger = logging.getLogger(__name__)


class RobotMode(Enum):
    """ロボットの動作モード"""
    IDLE = "idle"                      # 待機中
    FOLLOWING = "following"            # 人物追跡中
    LISTENING = "listening"            # 音声入力待機中
    TASK_PLANNING = "task_planning"    # タスク計画中
    TASK_EXECUTING = "task_executing"  # タスク実行中


class RobotController:
    """ロボット統合コントローラー"""

    def __init__(self):
        """ロボットコントローラーを初期化する"""
        # インフラ層
        self.motor = Motor()
        self.camera = CameraInput()
        self.voice_recognizer = VoiceRecognizer()
        self.voice_synthesizer = VoiceSynthesizer()
        self.display = DisplayController()

        # ドメインサービス層
        self.person_tracker = PersonTracker()
        self.collision_avoidance = CollisionAvoidance()
        self.task_planner = TaskPlanner()

        # 状態管理
        self.current_mode = RobotMode.IDLE
        self.is_running = False
        self._is_initialized = False

    def initialize(self) -> bool:
        """
        すべてのコンポーネントを初期化する

        Returns:
            bool: 初期化成功時True
        """
        logger.info("ロボット初期化開始...")

        try:
            # カメラ初期化
            if not self.camera.initialize():
                logger.error("カメラ初期化失敗")
                return False

            # 音声認識初期化
            if not self.voice_recognizer.initialize():
                logger.error("音声認識初期化失敗")
                return False

            # 音声合成初期化
            if not self.voice_synthesizer.initialize():
                logger.error("音声合成初期化失敗")
                return False

            # ディスプレイ初期化
            if not self.display.initialize():
                logger.error("ディスプレイ初期化失敗")
                return False

            # 人物追跡初期化
            if not self.person_tracker.initialize():
                logger.error("人物追跡初期化失敗")
                return False

            self._is_initialized = True
            self.display.show_expression(Expression.HAPPY)
            logger.info("ロボット初期化完了")
            return True

        except Exception as e:
            logger.error(f"ロボット初期化エラー: {e}")
            return False

    def run(self) -> None:
        """ロボットのメインループを開始する"""
        if not self._is_initialized:
            logger.error("ロボットが初期化されていません")
            return

        self.is_running = True
        logger.info("ロボット動作開始")

        try:
            while self.is_running:
                if self.current_mode == RobotMode.IDLE:
                    self._idle_mode()
                elif self.current_mode == RobotMode.FOLLOWING:
                    self._following_mode()
                elif self.current_mode == RobotMode.LISTENING:
                    self._listening_mode()
                elif self.current_mode == RobotMode.TASK_PLANNING:
                    self._task_planning_mode()
                elif self.current_mode == RobotMode.TASK_EXECUTING:
                    self._task_executing_mode()

                time.sleep(0.1)  # CPUの負荷を軽減

        except KeyboardInterrupt:
            logger.info("ユーザーによる中断")
        except Exception as e:
            logger.error(f"ロボット動作エラー: {e}")
        finally:
            self.shutdown()

    def _idle_mode(self) -> None:
        """待機モード: ウェイクワードを待つ"""
        self.display.show_expression(Expression.NEUTRAL)

        # ウェイクワード検出
        if self.voice_recognizer.detect_wake_word(timeout=1.0):
            logger.info("ウェイクワード検出")
            self.voice_synthesizer.speak("はい、何でしょうか?")
            self.display.show_expression(Expression.HAPPY)
            self.current_mode = RobotMode.LISTENING
        else:
            # ウェイクワードがない場合は人物追跡モードへ
            self.current_mode = RobotMode.FOLLOWING

    def _following_mode(self) -> None:
        """人物追跡モード: 登録された人物を追跡する"""
        self.display.show_expression(Expression.NEUTRAL)

        # カメラから画像取得
        frame = self.camera.capture_frame()
        if frame is None:
            return

        # 衝突回避チェック
        if self.collision_avoidance.detect_obstacles(frame):
            logger.warning("障害物検出、停止")
            self.motor.move(Motor.STOP, 0)
            safe_direction = self.collision_avoidance.calculate_safe_direction(frame)
            if safe_direction:
                logger.info(f"安全な方向: {safe_direction}")
            return

        # 登録された人物を検出
        person_bbox = self.person_tracker.detect_registered_person(frame)

        if person_bbox:
            # 人物への移動方向を計算
            direction = self.person_tracker.calculate_direction_to_person(
                person_bbox, frame.shape[1]
            )

            if direction == "forward":
                self.motor.move(Motor.FORWARD, 20)
            elif direction == "left":
                self.motor.move(Motor.LEFT, 70)
            elif direction == "right":
                self.motor.move(Motor.RIGHT, 70)
            elif direction == "stop":
                self.motor.move(Motor.STOP, 0)
        else:
            # 人物が見つからない場合は停止
            self.motor.move(Motor.STOP, 0)

        # ウェイクワード検出をチェック（非ブロッキング）
        if self.voice_recognizer.detect_wake_word(timeout=0.1):
            self.motor.move(Motor.STOP, 0)
            self.voice_synthesizer.speak("はい、何でしょうか?")
            self.display.show_expression(Expression.HAPPY)
            self.current_mode = RobotMode.LISTENING

    def _listening_mode(self) -> None:
        """音声入力待機モード: ユーザーのコマンドを聞く"""
        self.display.show_expression(Expression.THINKING)

        # ユーザーコマンドを聞き取る
        command = self.voice_recognizer.listen_command(timeout=10.0)

        if command is None:
            self.voice_synthesizer.speak("もう一度お願いします")
            return

        logger.info(f"受信コマンド: {command}")

        # タスク計画モードへ移行
        self.current_mode = RobotMode.TASK_PLANNING
        self.user_command = command

    def _task_planning_mode(self) -> None:
        """タスク計画モード: 行動計画を立てる"""
        self.display.show_expression(Expression.THINKING)

        # 行動計画を作成
        tasks = self.task_planner.create_plan(self.user_command)

        if not tasks:
            self.voice_synthesizer.speak("すみません、理解できませんでした")
            self.current_mode = RobotMode.FOLLOWING
            return

        # 計画を説明
        plan_description = self.task_planner.get_plan_description()
        logger.info(plan_description)
        self.voice_synthesizer.speak(plan_description)
        self.voice_synthesizer.speak("よろしいですか?")

        # "ok"の確認を待つ
        confirmation = self.voice_recognizer.listen_command(timeout=10.0)

        if confirmation and ("ok" in confirmation.lower() or "はい" in confirmation):
            self.voice_synthesizer.speak("了解しました。実行します")
            self.current_mode = RobotMode.TASK_EXECUTING
        else:
            self.voice_synthesizer.speak("キャンセルしました")
            self.task_planner.reset()
            self.current_mode = RobotMode.FOLLOWING

    def _task_executing_mode(self) -> None:
        """タスク実行モード: 行動計画を実行する"""
        self.display.show_expression(Expression.NEUTRAL)

        # 現在のタスクを取得
        current_task = self.task_planner.start_current_task()

        if current_task is None:
            # すべてのタスクが完了
            self.voice_synthesizer.speak("タスクが完了しました")
            self.display.show_expression(Expression.HAPPY)
            self.task_planner.reset()
            self.current_mode = RobotMode.FOLLOWING
            return

        # タイムアウトチェック
        if self.task_planner.check_timeout():
            self.voice_synthesizer.speak("タスクを完了できませんでした。人を探します")
            self.task_planner.reset()
            self.current_mode = RobotMode.FOLLOWING
            return

        # タスクの種類に応じた実行（簡易実装）
        logger.info(f"タスク実行中: {current_task.description}")

        # 簡易実装: 一定時間後にタスク完了とする
        time.sleep(2.0)
        self.task_planner.complete_current_task(success=True)

        # 次のタスクへ
        if self.task_planner.is_plan_completed():
            self.voice_synthesizer.speak("すべてのタスクが完了しました")
            self.display.show_expression(Expression.HAPPY)
            self.task_planner.reset()
            self.current_mode = RobotMode.FOLLOWING

    def shutdown(self) -> None:
        """ロボットをシャットダウンする"""
        logger.info("ロボットシャットダウン開始...")

        try:
            # モーター停止
            self.motor.move(Motor.STOP, 0)

            # リソース解放
            self.camera.release()
            self.voice_synthesizer.shutdown()
            self.display.close()

            self.is_running = False
            logger.info("ロボットシャットダウン完了")

        except Exception as e:
            logger.error(f"シャットダウンエラー: {e}")
