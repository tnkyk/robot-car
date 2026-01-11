"""
アシスタントロボットカー メインプログラム

要件定義: robot-car-software/required.md
"""
import logging
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from application.usecase import RobotController


def setup_logging():
    """ロギングを設定する"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('robot_car.log')
        ]
    )


def main():
    """メイン関数"""
    # ロギング設定
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 50)
    logger.info("アシスタントロボットカー起動")
    logger.info("=" * 50)

    # ロボットコントローラーを初期化
    robot = RobotController()

    if not robot.initialize():
        logger.error("ロボット初期化に失敗しました")
        return 1

    try:
        # ロボット動作開始
        robot.run()

    except KeyboardInterrupt:
        logger.info("ユーザーによる終了")

    except Exception as e:
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        return 1

    finally:
        robot.shutdown()
        logger.info("プログラム終了")

    return 0


if __name__ == "__main__":
    sys.exit(main())
