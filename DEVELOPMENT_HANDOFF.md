# OW_tool — Codex開発引き継ぎ資料

更新日: 2026-11-22

> **重要**: この文書はChatGPTでの開発会話とユーザー提供の検証ログに基づく。現在の作業ツリーを直接監査したものではない。Codexは最初に実際のコードを読み、実装状況を確認すること。

## 1. 目的とスコープ

Overwatchの試合中、TABで表示されるスコアボードを自動取得し、**各マッチの最後に取得した有効なスコアボード画像だけを残す**Pythonデスクトップツールを開発中。

将来はマップ名、勝敗（低優先度／手動も可）、指定したフレンドのロール（タンク／ダメージ／サポート）、特定ヒーロー組み合わせの同時選択履歴などのログ化も構想している。ただし**直近の優先順位は既存の画像保存機能の安定化と設定の整理**。ヒーローの継続追跡は不要。プレイヤー名には日本語等が含まれる可能性があり、将来のOCR基盤は多言語対応を検討する。

## 2. 動作環境と既知の構造

- Windows、Python 3系。Overwatchは1920×1080フルスクリーン、UIスケール固定。画面全体キャプチャを前提とし、アクティブウィンドウ領域だけに絞る変更は不要。
- 既存の主なファイル／クラス（実ファイルを確認すること）:
  - `main.py`: 依存関係の組み立て、TAB入力ループ、終了処理。
  - `capture/keyboard_listener.py` — `KeyboardListener`。
  - `capture/game_capture.py` — `GameCapture`。
  - `capture/capture_manager.py` — `CaptureManager`。Overwatchアクティブ判定、複数フレームのキャプチャ、スコアボード検出、品質判定、バッファへの受け渡し、保存。
  - `detector/scoreboard_locator.py` — `ScoreboardLocator("template/header.png", threshold=0.90)` のテンプレートマッチング。
  - `detector/map_comparator.py` — `MapComparator`。画像ベースのマップ領域比較（SSIM＋位置ずれへの対応を検討）。
  - `MatchBuffer` — 最後の画像を保持。ファイル配置は実コードで確認。
  - `logger/logger.py` — ロギング。過去の設計では `logs/ow_logger.log`、コンソールINFO／ファイルDEBUG。
  - OCR比較用のテストスクリプト（過去に `test_ocr_compare.py` として扱われた）。
- 現状の設定ファイル `config/settings.py`, `config/maps.py` は**提案段階**。既にあるかはリポジトリで確認。

## 3. これまでに動作確認された重要な仕様

### TABトリガー

`listener.wait_for_tab()` → **押した直後** `manager.process_tab_press()` → `listener.wait_for_tab_release()`。TABを押し続けても1回しか処理しない。離した時点で処理するとスコアボードが消える問題があったため、この順番は変更しない。

### キャプチャとスコアボード判定

- `CaptureManager.is_overwatch_active()` が対象ゲームのフォアグラウンド状態を確認する設計。
- TAB押下後に約0.10秒待ち、複数（過去の実装は3）フレームを取得し、`ScoreboardLocator` のスコアが最も高いものを選ぶ。
- `template/header.png` に対するテンプレートマッチング閾値の例は `0.90`。複数テンプレート対応は将来のToDoであり、今の優先事項ではない。
- 一部スクリーンショットが視覚効果等で暗くなる問題があり、暗い／不適切なフレームをバッファに入れない品質チェックを追加した経緯がある。過去のコード説明ではマップROIの平均輝度 `20〜200`、標準偏差 `>=30` を使用。**現行コードの値・判定順は要確認**。

### MatchBufferの意図

1. 最初の有効なスコアボードAを保持。
2. 次の有効な画像Bを取得。
3. A/Bのマップが同じマッチと判定できれば、AをBで置き換える。
4. 別マッチなら、Aを前マッチの最終画像として保存し、Bを保持。
5. 正常終了時には最後の保持画像を `flush()` して保存。

`main.py` の `try/finally` で `manager.flush()` を呼ぶ構成が提案・実装された。通常の終了は **Ctrl+C**。強制終了やコンソールを閉じる操作では `finally` が実行されない場合がある。

**残課題**: 画像が途中経過のものになり、必ずしもマッチ最終盤の画像にならないことがある。過去に「暗転対策を先に、途中画像問題は後で検証」と優先順位を決定した。最新コードで解消済みかは未確認。

## 4. マップ識別方式の経緯

- 最初の簡易版はマップ名の画像領域のSSIM比較。マッチ時間の数字が等幅ではなく、表示の横幅が変わることでマップ名のX位置がずれるため、単純なSSIMでは不安定。
- **SSIM＋横方向のスライド**を候補として検討したが、会話の進展により**マップ名をOCRして辞書照合する方式**を優先して検証。
- マップ名の左側にあるモード名との区切り `|` の画像検出を試したが、`L` / `R` の縦線を誤検出する問題があり、この方式は採用しない。ROIを狭めず全領域をOCRする。
- OCRの実験には **Tesseract + pytesseract + RapidFuzz** を採用。将来の日本語プレイヤー名OCRでは別エンジン（PaddleOCR等）の採用・共通`OCREngine`化も過去に提案されたが、**現行のマップOCRをPaddleOCRに置き換える決定ではない**。
- 現在の画像比較ベースの `MapComparator` とOCRの本番統合状況は、コード確認が必要。OCRテストの成功だけで本番統合済みと判断しない。

## 5. マップOCR検証の固定条件

- 入力: `captures/ok/*.png`
- 正解ファイル: `captures/ok/map_name.txt`（1行 `ファイル名<TAB>正しいマップ名`）
- ROI: `x=1323`, `y=13`, `width=420`, `height=42`
- Tesseract: 過去のテストファイルでは `lang='eng'`, `--oem 3 --psm 7`
- 辞書照合: RapidFuzz、過去のテストでは `fuzz.WRatio`。表示スコアはOCR確率ではない。
- 比較した前処理: `gray`, `gray_x4`, `clahe`, `clahe_x4`, `otsu`, `adaptive`, `lanczos`

### 2026-11-15時点の再検証（ユーザー実測）

| 前処理 | 正解 / 40枚 | 正答率 |
|---|---:|---:|
| gray | 40/40 | 100.0% |
| gray_x4 | 40/40 | 100.0% |
| clahe | 40/40 | 100.0% |
| clahe_x4 | 40/40 | 100.0% |
| otsu | 40/40 | 100.0% |
| adaptive | 37/40 | 92.5% |
| lanczos | 40/40 | 100.0% |

辞書に `NEW QUEEN STREET` を追加したことで、それまで他のマップへ誤分類していた画像も6方式で正解となった。`adaptive` の誤りは以下の3件:

- `20261115_002410_231.png`: 正解 `WATCHPOINT:GRIMSVÖTON` → `RIALTO`
- `20261115_015032_253.png`: 正解 `NEW QUEEN STREET` → `NEW JUNK CITY`
- `20261115_021454_381.png`: 正解 `OASIS` → `AATLIS`

`gray` だけで40/40正解だったため、本番の第一候補は単純グレースケール。CLAHEフォールバックは提案段階。40枚以外の環境での精度は未確認。例えば `PARAÍSO` の照合スコアは64.3でも正解だったため、**閾値80を無検証で採用すると正常画像を捨てる**。閾値を決める場合は正解・不正解のスコア分布を評価すること。

### 最新のマップ辞書（32件、NEW QUEEN STREETを含む）

```python
MAP_NAMES = [
    "AATLIS",
    "ANTARCTIC PENINSULA",
    "BUSAN",
    "CIRCUIT ROYAL",
    "COLOSSEO",
    "DORADO",
    "ESPERANÇA",
    "EICHENWALDE",
    "WATCHPOINT:GRIMSVÖTON",
    "HAVANA",
    "HOLLYWOOD",
    "ILIOS",
    "JUNKERTOWN",
    "KING'S ROW",
    "LIJIANG TOWER",
    "MIDTOWN",
    "NEPAL",
    "NEON JUNCTION",
    "NEW JUNK CITY",
    "NEW QUEEN STREET",
    "NUMBANI",
    "OASIS",
    "PARAÍSO",
    "RIALTO",
    "ROUTE 66",
    "RUNASAPI",
    "SAMOA",
    "SHAMBALI MONASTERY",
    "SURAVASA",
    "TEMPLE OF ANUBIS",
    "THRONE OF ANUBIS",
    "WATCHPOINT:GIBRALTAR",
]
```

マップ辞書は将来追加されるため、テストの正解ラベルが辞書に存在するかを検証すること。

## 6. 次の作業（ユーザーと直近合意）

**設定値のコード分離・リファクタリング**。今は変更案の議論までであり、実コードへの適用はCodexが確認・実施する。

推奨ディレクトリ:

```text
OW_tool/
├── AGENTS.md
├── docs/
│   └── DEVELOPMENT_HANDOFF.md
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── maps.py
├── main.py
├── capture/
├── detector/
├── logger/
├── template/
└── captures/
```

提案された`config/settings.py`の例（**現行値と照合してから移すこと**）:

```python
class OCRConfig:
    SCALE = 4
    PSM = 7
    OEM = 3
    MATCH_THRESHOLD = 80  # 提案値のみ。PARAÍSO 64.3で正解のため要再検討

class ROIConfig:
    MAP_X = 1323
    MAP_Y = 13
    MAP_WIDTH = 420
    MAP_HEIGHT = 42

class ScoreboardConfig:
    HEADER_THRESHOLD = 0.90

class MatchConfig:
    SSIM_THRESHOLD = 0.98  # 過去に0.985案もあり。現行コード優先
```

使用例:

```python
from config.settings import OCRConfig, ROIConfig
from config.maps import MAP_NAMES

x, y = ROIConfig.MAP_X, ROIConfig.MAP_Y
w, h = ROIConfig.MAP_WIDTH, ROIConfig.MAP_HEIGHT
map_roi = frame[y:y + h, x:x + w]
```

`dataclass` / JSON / YAML への変更は必須ではない。現段階では**インスタンス不要のクラス属性**が推奨。辞書は `config/maps.py` に分離する。

### Codexに最初に依頼する作業手順

1. リポジトリを調査し、主要クラス、実装済み機能、既存設定値、テスト・依存関係を一覧化。
2. この資料とコードの不一致（特にSSIM閾値、品質フィルタ、OCRの本番統合状況）を報告。
3. 既存の挙動を変えずに `config/settings.py` と `config/maps.py` を作成し、参照箇所を置き換える。
4. 既存OCRの40枚ベンチマークを再実行して、少なくとも従来の正答率を維持しているか検証。画像・Tesseractがない場合は未実施と明記。
5. TAB押下／解放、最終画像の保持、暗転除外、Ctrl+C時のflushについて、実行可能な範囲で回帰確認。
6. **追加の機能変更（SSIM→OCR判定への移行、スコア閾値の新設、PaddleOCR採用など）は別提案**としてユーザーの判断を待つ。

## 7. 将来の検討事項（今すぐ実装しない）

- 画像ベースの同一マッチ判定をOCRのマップ名判定に置き換えるか。連続試合のマップ名が同じ場合の例外処理も必要。
- 試合途中の画像を最終画像として誤って残すケースの検証。
- マップ辞書更新、OCR不確実時のフォールバックとスコアリングの比較（`ratio`, `partial_ratio`, `token_sort_ratio`, `token_set_ratio`, `WRatio` の比較案あり）。
- 多言語のプレイヤー名認識、ロール判定、勝敗判定、指定ヒーロー組み合わせの検出。
- 複数スコアボードテンプレート対応。

## 8. 注意点

- 過去の会話には採用していない案や後から変わった設計が混在する。直近のユーザーの明示的な決定を優先する。
- ログの40/40は辞書の網羅性が前提。辞書外のマップはRapidFuzzでは正しく分類できない。
- 実測スコアが低い正解例があるため、**単純な一律80点足切りは避ける**。
- Codexに必要な実ソース、画像、`map_name.txt` は本引き継ぎ文書には含まれない。**ローカルのプロジェクトフォルダを開いて作業すること**。
