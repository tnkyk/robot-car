"""
行動計画サービス
ユーザーの依頼から行動計画を立案・実行する
"""
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import time

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """タスクステータス"""
    PENDING = "pending"          # 未実行
    IN_PROGRESS = "in_progress"  # 実行中
    COMPLETED = "completed"      # 完了
    FAILED = "failed"            # 失敗
    TIMEOUT = "timeout"          # タイムアウト


@dataclass
class Task:
    """タスククラス"""
    description: str              # タスクの説明
    action: str                   # 実行するアクション
    status: TaskStatus = TaskStatus.PENDING
    timeout: float = 60.0         # タイムアウト時間（秒）
    start_time: Optional[float] = None


class TaskPlanner:
    """行動計画サービス"""

    def __init__(self, default_timeout: float = 300.0):
        """
        行動計画を初期化する

        Args:
            default_timeout: デフォルトタイムアウト時間（秒）
        """
        self.default_timeout = default_timeout
        self.current_plan: List[Task] = []
        self.current_task_index: int = 0

    def create_plan(self, user_request: str) -> List[Task]:
        """
        ユーザーの依頼から行動計画を作成する

        Args:
            user_request: ユーザーの依頼内容

        Returns:
            List[Task]: 作成された行動計画
        """
        logger.info(f"行動計画作成中: {user_request}")

        # 簡易的なキーワードマッチングで計画を立てる
        tasks = []

        # 探し物系のタスク
        if "探して" in user_request or "見つけて" in user_request:
            target = self._extract_target_object(user_request)
            tasks.append(Task(
                description=f"{target}を探索する",
                action="search",
                timeout=120.0
            ))
            tasks.append(Task(
                description=f"{target}に近づく",
                action="approach",
                timeout=60.0
            ))
            tasks.append(Task(
                description="発見を報告する",
                action="report",
                timeout=10.0
            ))

        # 移動系のタスク
        elif "行って" in user_request or "移動" in user_request:
            destination = self._extract_destination(user_request)
            tasks.append(Task(
                description=f"{destination}へ移動する",
                action="navigate",
                timeout=180.0
            ))
            tasks.append(Task(
                description="到着を報告する",
                action="report",
                timeout=10.0
            ))

        # 確認系のタスク
        elif "確認" in user_request or "チェック" in user_request:
            target = self._extract_target_object(user_request)
            tasks.append(Task(
                description=f"{target}を確認する",
                action="check",
                timeout=60.0
            ))
            tasks.append(Task(
                description="確認結果を報告する",
                action="report",
                timeout=10.0
            ))

        # デフォルトタスク
        else:
            tasks.append(Task(
                description="依頼内容を理解する",
                action="understand",
                timeout=30.0
            ))
            tasks.append(Task(
                description="適切なアクションを実行する",
                action="execute",
                timeout=120.0
            ))

        self.current_plan = tasks
        self.current_task_index = 0

        logger.info(f"行動計画作成完了: {len(tasks)}個のタスク")
        return tasks

    def _extract_target_object(self, text: str) -> str:
        """テキストから対象物を抽出する（簡易実装）"""
        # キーワードの後の名詞を抽出（簡易）
        keywords = ["探して", "見つけて", "確認"]
        for keyword in keywords:
            if keyword in text:
                parts = text.split(keyword)
                if len(parts) > 1:
                    target = parts[1].strip().split()[0] if parts[1].strip() else "対象物"
                    return target
        return "対象物"

    def _extract_destination(self, text: str) -> str:
        """テキストから目的地を抽出する（簡易実装）"""
        keywords = ["行って", "移動"]
        for keyword in keywords:
            if keyword in text:
                parts = text.split(keyword)
                if len(parts) > 0:
                    dest = parts[0].strip().split()[-1] if parts[0].strip() else "目的地"
                    return dest
        return "目的地"

    def get_plan_description(self) -> str:
        """
        現在の行動計画の説明を取得する

        Returns:
            str: 行動計画の説明
        """
        if not self.current_plan:
            return "行動計画がありません"

        description = "以下の行動計画を実行します:\n"
        for i, task in enumerate(self.current_plan, 1):
            description += f"{i}. {task.description}\n"

        return description

    def start_current_task(self) -> Optional[Task]:
        """
        現在のタスクを開始する

        Returns:
            Optional[Task]: 開始したタスク、計画完了時None
        """
        if self.current_task_index >= len(self.current_plan):
            logger.info("すべてのタスクが完了しました")
            return None

        task = self.current_plan[self.current_task_index]
        task.status = TaskStatus.IN_PROGRESS
        task.start_time = time.time()

        logger.info(f"タスク開始: {task.description}")
        return task

    def complete_current_task(self, success: bool = True) -> None:
        """
        現在のタスクを完了する

        Args:
            success: 成功した場合True、失敗した場合False
        """
        if self.current_task_index >= len(self.current_plan):
            return

        task = self.current_plan[self.current_task_index]
        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED

        logger.info(f"タスク完了: {task.description} (ステータス: {task.status.value})")

        self.current_task_index += 1

    def check_timeout(self) -> bool:
        """
        現在のタスクがタイムアウトしたかチェックする

        Returns:
            bool: タイムアウトした場合True
        """
        if self.current_task_index >= len(self.current_plan):
            return False

        task = self.current_plan[self.current_task_index]

        if task.status == TaskStatus.IN_PROGRESS and task.start_time is not None:
            elapsed_time = time.time() - task.start_time
            if elapsed_time > task.timeout:
                task.status = TaskStatus.TIMEOUT
                logger.warning(f"タスクタイムアウト: {task.description}")
                return True

        return False

    def is_plan_completed(self) -> bool:
        """
        行動計画が完了したかチェックする

        Returns:
            bool: 完了した場合True
        """
        return self.current_task_index >= len(self.current_plan)

    def reset(self) -> None:
        """行動計画をリセットする"""
        self.current_plan = []
        self.current_task_index = 0
        logger.info("行動計画リセット")
