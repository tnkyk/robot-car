# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Raspberry Pi 4を使用したアシスタントロボットカーの開発プロジェクト。特定の登録ユーザーを追跡し、音声コマンド（"Hey, Tom"）に応答し、カメラビジョン、音声入出力、ディスプレイフィードバックを使用してタスクを実行する設計。

## 開発コマンド

### ロボットの実行
```bash
# キーボード制御テストプログラムの実行（開発・テスト用）
cd robot-car-software
python robotCarMain.py
```

**操作方法**:
- `w`: 前進
- `s`: 後退
- `a`: 左旋回
- `d`: 右旋回
- `e`: 停止
- `q`: プログラム終了

## アーキテクチャ

### ディレクトリ構造（DDD / レイヤードアーキテクチャ）
```
robot-car/
├── robot-car-software/          # Pythonソフトウェア（開発のルートディレクトリ）
│   ├── domain/                 # ドメイン層
│   │   ├── model/             # ドメインモデル（エンティティ、値オブジェクト）
│   │   └── service/           # ドメインサービス
│   │       ├── person_tracker.py       # 人物追跡サービス
│   │       ├── collision_avoidance.py  # 衝突回避サービス
│   │       └── task_planner.py         # 行動計画サービス
│   ├── infrastructure/        # インフラ層（外部システム・ハードウェア）
│   │   ├── camera/           # カメラ入力
│   │   │   └── camera_input.py
│   │   ├── voice/            # 音声入出力
│   │   │   ├── voice_recognizer.py    # 音声認識
│   │   │   └── voice_synthesizer.py   # 音声合成
│   │   ├── display/          # ディスプレイ表示
│   │   │   └── display_controller.py  # 表情表示
│   │   └── motor/            # モーター制御
│   │       ├── dcMortorL298N.py        # DCモーター制御クラス
│   │       └── pimygpio.py             # GPIO ピンマッピング
│   ├── application/          # アプリケーション層（ユースケース）
│   │   └── usecase/
│   │       └── robot_controller.py     # ロボット統合コントローラー
│   ├── resources/            # リソースファイル
│   │   └── expressions/      # 表情画像
│   ├── main.py              # エントリーポイント
│   ├── requirements.txt     # 依存パッケージ
│   ├── README.md           # ドキュメント
│   ├── dcMortorL298N.py    # （レガシー・下位互換用）
│   ├── pimygpio.py         # （レガシー・下位互換用）
│   ├── robotCarMain.py     # （テスト用キーボード制御）
│   └── required.md         # ソフトウェア要件定義（日本語）
└── robot-car-chassis/          # ハードウェア設計
    ├── parts-Information.md    # ハードウェア部品リスト
    ├── layer1/                 # 1層目設計（モーター・バッテリー層）
    │   ├── required-layer1.md  # 1層目要件定義
    │   └── RobotCarArmor_Layer1.FCStd
    └── layer2/                 # 2層目設計（Raspberry Pi層）
        ├── required-layer2.md  # 2層目要件定義
        └── RobotCarArmor_Layer2.FCStd
```

### ハードウェア構成

#### 3層構造の物理レイアウト
- **1層目（底面）**: DCモーター×4、L298Nドライバー、5V/20Ahバッテリー、スピーカー
- **2層目（中間）**: Raspberry Pi 4 Model B 8GB
- **3層目（上面）**: Webカメラ、ディスプレイ、マイク（未実装）

#### 主要コンポーネント
- **制御基板**: Raspberry Pi 4 Model B 8GB
- **モータードライバー**: L298N デュアルHブリッジ
- **センサー**: Webカメラ、マイク
- **出力**: スピーカー、ディスプレイ
- **電源**: 5V/20Ahバッテリー
- **GPIOライブラリ**: pigpio（ハードウェアPWM制御）

詳細は `robot-car-chassis/parts-Information.md` 参照。

### ソフトウェアアーキテクチャ（レイヤードアーキテクチャ）

#### レイヤー構成

**ドメイン層** (`domain/`):
- **ビジネスロジック**: ロボットの中核機能
- **ドメインサービス**:
  - `PersonTracker`: 顔検出、人物登録、追跡方向計算
  - `CollisionAvoidance`: 障害物検出、安全方向計算
  - `TaskPlanner`: 行動計画立案、タスク管理、タイムアウト処理

**インフラ層** (`infrastructure/`):
- **ハードウェア・外部システムとの接続**
- `CameraInput`: OpenCVによるカメラ制御
- `VoiceRecognizer`: speech_recognitionによる音声認識、ウェイクワード検出
- `VoiceSynthesizer`: pyttsx3による音声合成
- `DisplayController`: OpenCVによる表情表示
- `Motor`: pigpioによるL298N制御

**アプリケーション層** (`application/`):
- **ユースケースの実装**
- `RobotController`: 全コンポーネントの統合、動作モード管理

#### 動作モード

```python
class RobotMode(Enum):
    IDLE = "idle"                      # 待機中（ウェイクワード待ち）
    FOLLOWING = "following"            # 人物追跡中
    LISTENING = "listening"            # 音声コマンド入力待ち
    TASK_PLANNING = "task_planning"    # 行動計画立案中
    TASK_EXECUTING = "task_executing"  # タスク実行中
```

#### モーター制御（インフラ層）

**Motor クラス** (`infrastructure/motor/dcMortorL298N.py`):
- 方向定数: `FORWARD`, `BACKWARD`, `LEFT`, `RIGHT`, `STOP`
- `move(direction, speed)`: 移動の主要インターフェース
  - `direction`: 方向定数のいずれか
  - `speed`: スピード（0-100%）
  - 実装: pigpioライブラリを使用してGPIOピン13と19でハードウェアPWM制御
  - スピードをPWMデューティサイクルに変換（`speed * 1000000 / 100`）

**GPIO設定** (`infrastructure/motor/pimygpio.py`):
```python
L298N_IN_1 = 22  # モーター1/2の回転方向制御
L298N_IN_2 = 23  # モーター1/2の回転方向制御
L298N_IN_3 = 20  # モーター3/4の回転方向制御
L298N_IN_4 = 26  # モーター3/4の回転方向制御
PWM_PIN_1 = 13   # モーター1/2のPWM速度制御
PWM_PIN_2 = 19   # モーター3/4のPWM速度制御
```

#### モーター動作特性
- **シャーシの重量配分により、旋回時は前後移動より高いスピード値が必要**:
  - 前進/後退: 20%
  - 左/右旋回: 70%
- **旋回の実装**:
  - 左旋回: 左モーター逆転、右モーター正転
  - 右旋回: 左モーター正転、右モーター逆転

#### 主要な処理フロー

1. **起動**: `main.py` → `RobotController.initialize()` → 全コンポーネント初期化
2. **人物追跡**: カメラ取得 → `PersonTracker.detect_registered_person()` → `Motor.move()`
3. **ウェイクワード**: `VoiceRecognizer.detect_wake_word()` → 停止 → リスニングモード
4. **コマンド処理**: `VoiceRecognizer.listen_command()` → `TaskPlanner.create_plan()` → 計画説明 → 実行

### 設計原則

#### ドメイン駆動設計（DDD）
- ユビキタス言語でクラス名・変数名を定義
- `robot-car-software/` を開発ルートとして使用
- Python言語を使用

#### ドキュメント
- 要件定義と設計ドキュメントは日本語で記述
- ソフトウェア要件: `robot-car-software/required.md`
- ハードウェア要件: `robot-car-chassis/layer*/required-layer*.md`

## 今後の実装要件

`robot-car-software/required.md` に定義された要件:

### 移動（Output: 移動）
- **Input**: DCモーターの状況、カメラ画像、音声入力
- **基本動作**: 特定の登録ユーザーを追跡
  - ユーザー識別: 画像・音声情報による
- **衝突回避**: 常に物や人にぶつからないこと
- **停止**: "Hey, Tom" 発話で停止
- **タスク実行**: 停止後の依頼に基づき行動計画を立案・実行
  - 短期間のゴール設定、状況に応じた計画更新
  - タイムアウト時は音声通知して基本動作に戻る
- **制約**: 移動は `Motor.move()` を使用すること

### 音声出力（Output: 音声出力）
- "Hey, Tom" に音声で返事
- 行動計画の説明と目標確認
- "ok" 発話で行動計画実行

### 画面出力（Output: 画面出力）
- 表情画像の表示
- 状況に応じた動的な表情切り替え（例: 笑顔を見たら笑顔になる）

## 3Dプリント情報

### 制約
- 最大造形体積: 180×180×180 mm³
- 1層目の板は制約により2分割して造形後に結合

### Layer 1（240×175×6mm）
- 右側板（Layer1_Right）: 120×175×6mm
- 左側板（Layer1_Left）: 120×175×6mm
- コネクタ×3: 19.8×29.8×3.8mm（板結合用）

### Layer 2（167×175×6mm）
- 一体成形（分割不要）

設計ファイルはFreeCAD形式（.FCStd）で保存。

## 開発ルールと規約

### コーディング規約

#### Pythonスタイルガイド
- **PEP 8準拠**: Pythonコーディング標準に従う
- **命名規則**:
  - クラス名: PascalCase（例: `Motor`, `RobotCarController`）
  - 関数名・変数名: snake_case（例: `move()`, `setup_l298n()`）
  - 定数: UPPER_CASE（例: `FORWARD`, `PWM_PIN_1`）
  - ユビキタス言語に基づく命名（DDDの原則）
- **インデント**: スペース4つ
- **行の長さ**: 最大120文字を推奨

#### 型ヒントの使用
```python
def move(self, direction: int, speed: int) -> None:
    """
    モーターを指定した方向とスピードで動かす

    Args:
        direction: 方向定数（FORWARD, BACKWARD, LEFT, RIGHT, STOP）
        speed: スピード（0-100の範囲）
    """
```

#### コメントとドキュメント
- **クラス・関数のdocstring**: 必須（日本語で記述）
- **複雑なロジック**: インラインコメントで説明
- **ハードウェア関連**: GPIO番号や物理的な接続情報をコメントで明記

### Git運用ルール

#### ブランチ戦略
- `main`: 安定版（動作確認済みのコード）
- `feature/*`: 機能開発用ブランチ（例: `feature/voice-recognition`, `feature/camera-tracking`）
- `fix/*`: バグ修正用ブランチ

#### コミットメッセージ
```
[type] 簡潔な変更内容の要約（50文字以内）

詳細な説明（必要に応じて）
- 変更の理由
- 影響範囲
- 注意事項
```

**type の種類**:
- `feat`: 新機能追加
- `fix`: バグ修正
- `refactor`: リファクタリング
- `docs`: ドキュメント更新
- `test`: テストコード追加・修正
- `hw`: ハードウェア設定変更

例:
```
feat: DCモーターのキーボード制御機能を追加

robotCarMain.pyに以下を実装:
- w/s/a/dキーによる前後左右の制御
- eキーによる停止
- qキーによるプログラム終了
```

### テストと品質保証

#### ハードウェアテスト
- **モーター動作テスト**: 各方向（前進・後退・左旋回・右旋回・停止）を個別に検証
- **速度検証**: 設定したスピード値が適切に反映されることを確認
- **安全性確認**:
  - 物理的な動作範囲の確認
  - 緊急停止機能の動作確認
  - バッテリー電圧の監視

#### ソフトウェアテスト
- **単体テスト**: ビジネスロジックの関数・クラスに対してテストを作成
- **統合テスト**: ハードウェアとソフトウェアの連携動作を確認
- **エッジケースの考慮**:
  - 範囲外のスピード値（負の値、100超）
  - 未定義の方向定数
  - GPIO初期化失敗時の挙動

### エラーハンドリング

#### ハードウェア制御での例外処理
```python
try:
    self.myPi = pigpio.pi()
    if not self.myPi.connected:
        raise RuntimeError("pigpioデーモンに接続できません")
    setupL298N(self.myPi)
except Exception as e:
    print(f"モーター初期化エラー: {e}")
    # 適切なクリーンアップ処理
    raise
```

#### ロギング
- **重要な状態変化**: モーター始動・停止、エラー発生をログに記録
- **デバッグ情報**: 開発時はGPIO状態、PWM値などを出力
- **ログレベル**: ERROR, WARNING, INFO, DEBUGを適切に使い分け

### セキュリティとプライバシー

#### 認証情報の管理
- **環境変数の使用**: APIキー、トークンは環境変数またはconfigファイルで管理
- **Gitignore**: `.env`, `config.json`, `credentials/*` をリポジトリから除外
- `.gitignore` に以下を追加:
  ```
  .env
  *.config
  credentials/
  __pycache__/
  *.pyc
  ```

#### カメラ・マイクのプライバシー
- **データ保存**: 録画・録音データは明示的な許可なしに保存しない
- **ユーザー登録情報**: 顔画像・音声データは暗号化して保存
- **アクセス制御**: センサーデータへのアクセスは最小権限の原則

### ハードウェア操作の安全性

#### GPIO操作の原則
- **初期化確認**: GPIOを使用する前に必ず初期化状態を確認
- **クリーンアップ**: プログラム終了時は必ずGPIOをクリーンアップ
  ```python
  try:
      # GPIO操作
  finally:
      self.myPi.stop()  # pigpioデーモンとの接続を切断
  ```
- **ハードウェア保護**:
  - PWMデューティサイクルの上限設定（100%以下）
  - モーター過負荷の検出と自動停止

#### 安全な動作フロー
1. **起動時チェック**: バッテリー電圧、GPIO接続状態の確認
2. **段階的な動作**: いきなり高速ではなく、低速から徐々に加速
3. **異常検知**: センサー値の異常、予期しない動作を検出したら即座に停止
4. **フェイルセーフ**: エラー発生時は安全な状態（モーター停止）に遷移

### コードレビュー

#### レビュー観点
- **DDDの原則遵守**: ユビキタス言語に基づく命名、ドメインモデルの適切な表現
- **ハードウェア整合性**: GPIO番号、電気的特性が仕様と一致しているか
- **安全性**: 緊急停止、エラーハンドリング、リソース解放が適切か
- **可読性**: 日本語コメント、分かりやすい変数名、適切な関数分割

#### マージ前の確認事項
- [ ] 実機での動作確認完了
- [ ] コーディング規約に準拠
- [ ] 必要なドキュメント更新（required.md、CLAUDE.md等）
- [ ] テストコード作成（該当する場合）
- [ ] エラーハンドリングの実装
- [ ] GPIOクリーンアップ処理の実装

### ドキュメンテーション

#### 更新が必要なタイミング
- **新機能追加時**: `robot-car-software/required.md` に要件を追記
- **ハードウェア変更時**: `parts-Information.md` およびレイヤー要件定義を更新
- **API変更時**: 関数のdocstringとCLAUDE.mdを更新
- **設計変更時**: アーキテクチャセクションを更新

#### 図表の活用
- **システム構成図**: ハードウェアとソフトウェアの関係を図示
- **状態遷移図**: ロボットの動作モード、状態遷移を明確化
- **シーケンス図**: 複雑な処理フロー（音声認識→行動計画→実行）を記述
