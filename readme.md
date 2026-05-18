# ザク・モーション制御システム (ZAKU Motion Control System)

スマートフォンを「コックピット端末」に見立て、Wi-Fi経由で模型のモノアイ点灯や武器（マシンガン）の音・光をリアルタイム制御するシステムです。

通常モードでは DFPlayer Mini と連携して音と光を同期させ、`DEBUG_LED_ONLY = True` の LED単体テストモードでは Wi-Fi / WebSocket を維持したまま音声処理だけを切り離して安全に段階検証できます。

利用者向けの基本手順はこの README にまとめ、詳細な動作確認チェックリスト・調整項目・開発メモは `DEVELOPMENT.md` に集約しています。

## 特徴

- 🎮 **WebベースUI** - アプリ不要、QRコードから即座に操作可能
- 🔌 **マルチデバイス対応** - ESP32およびRaspberry Pi Pico 2 W対応
- 🎵 **同期演出** - 通常モードではDFPlayer Miniを使用し、音と光を同期
- 🧪 **LED単体テストモード** - `DEBUG_LED_ONLY` で音声再生とBusy監視を一時的に無効化可能
- ⚙️ **汎用設計** - 様々な模型に流用可能

## システム構成

### ハードウェア

- **マイコン**: ESP32 DevKit V1 または Raspberry Pi Pico 2 W
- **サウンド**: DFPlayer Mini + MicroSDカード
- **LED**:
  - モノアイ: 高輝度ピンクLED (PWM制御)
  - マシンガン: 高輝度イエローLED (デジタル出力)

### ソフトウェア

- **言語**: MicroPython
- **非同期処理**: uasyncio
- **通信**: HTTP + WebSocket
- **UI**: HTML5 + Tailwind CSS

## ファイル構成


```

esp32-c3/
├── main.py          # エントリーポイント（起動用）
├── config.py        # 設定ファイル（ピンアサイン、Wi-Fi設定など）
├── index.html       # WebUI（スマホ操作画面）
├── readme.md        # このファイル
├── src/             # 分割されたモジュール
│   ├── dfplayer.py      # DFPlayer Mini制御クラス
│   ├── led_control.py   # LED制御クラス
│   ├── web_server.py    # WebSocket/HTTPサーバー
│   └── zaku_system.py   # システムコア（演出ロジック）
└── DEVELOPMENT.md   # 開発用タスクリスト（マイコンへの転送不要）

```

**マイコンへ転送が必要なファイル**: `main.py`, `config.py`, `index.html`, `src/` フォルダ全体

## セットアップと配線

`config.py` 内の `BOARD` 設定を切り替えることで、以下のピンアサインが自動的に適用されます。

あわせて、モノアイLEDのPWM制御方式も `config.py` 内で自動的に切り替わります。

- `BOARD = "esp32"` の場合: `MONOEYE_PWM_WRITE_METHOD = "duty"`
- `BOARD = "pico2w"` の場合: `MONOEYE_PWM_WRITE_METHOD = "duty_u16"`

通常はこれらを個別に変更する必要はなく、`BOARD` を選ぶだけで両対応できる想定です。

### 1. Raspberry Pi Pico 2 W を使用する場合 (`BOARD = "pico2w"`)


```

## Pico 2 W        DFPlayer Mini

GP0 (TX)    ->  RX
GP1 (RX)    ->  TX
GP2 (Input) <-  BUSY
GND         ->  GND
VBUS (5V)   ->  VCC

GP15        ->  モノアイLED (+)
GP14        ->  マシンガンLED (+)

※各LEDのマイナス側はGNDに抵抗(330Ω推奨)経由で接続

```

### 2. ESP32 DevKit V1 を使用する場合 (`BOARD = "esp32"`)


```

## ESP32           DFPlayer Mini

GPIO17 (TX) ->  RX
GPIO16 (RX) ->  TX
GPIO4 (Input)<- BUSY
GND         ->  GND
5V          ->  VCC

GPIO25      ->  モノアイLED (+)
GPIO26      ->  マシンガンLED (+)

※各LEDのマイナス側はGNDに抵抗(330Ω推奨)経由で接続

```

---

## MicroSDカード準備

DFPlayer Mini用のMicroSDカードをFAT32でフォーマットし、以下のいずれかの方式で音源ファイルを配置：

#### 方式1: simple モード（シンプル、デフォルト）

ルートディレクトリに連番ファイルを配置：


```

/
├── 0001.mp3 - モノアイ起動音
├── 0002.mp3 - 将来の単発演出用（現状未使用・任意）
└── 0003.mp3 - マシンガン連射音

```

**config.pyの設定**:
```python
SOUND_MODE = "simple"  # デフォルト

```

#### 方式2: folder モード（整理しやすい）

フォルダで音源を分類して配置：

```
/
├── 01/
│   ├── 001.mp3 - モノアイ起動音
│   ├── 002.mp3 - 将来の単発演出用（現状未使用・任意）
│   └── 003.mp3 - マシンガン連射音
├── 02/
│   ├── 001.mp3 - その他の効果音
│   └── 002.mp3 - その他の効果音
└── ...

```

**config.pyの設定**:

```python
SOUND_MODE = "folder"
# フォルダとファイル番号で指定
SOUND_MONOEYE_ON_FOLDER = (1, 1)   # /01/001.mp3
# SOUND_GUN_SINGLE_FOLDER = (1, 2)  # /01/002.mp3: 将来の単発演出用（現状未使用）
SOUND_GUN_BURST_FOLDER = (1, 3)    # /01/003.mp3

```

**現時点の実装では、マシンガン演出で使用する音源は `0003.mp3`（連射音）のみです。**
`0002.mp3` と `SOUND_GUN_SINGLE*` / `MACHINEGUN_SINGLE_AUDIO_OFFSET` は将来拡張用の予約設定として残しています。

**注意**:

* フォルダ名は01〜99の2桁数字
* ファイル名は001〜255の3桁数字
* 拡張子は.mp3

---

## ファイル転送

以下のファイルをマイコンに転送してください：

#### 必須ファイル（7個）

```
├── main.py          # エントリーポイント
├── config.py        # 設定ファイル（要編集）
├── index.html       # WebUI（コックピット画面）
└── src/             # モジュールフォルダ（フォルダごと転送）
    ├── dfplayer.py      # DFPlayer Mini制御
    ├── led_control.py   # LED制御
    ├── web_server.py    # WebSocket/HTTPサーバー
    └── zaku_system.py   # システムコア

```

**重要**: `src` フォルダごと転送してください。フォルダ構造を保つ必要があります。

#### 転送方法の例

**Thonny IDEの場合:**

1. Thonny IDEでマイコンに接続
2. 各ファイルを右クリック → "Upload to /" で転送
3. `src` フォルダも右クリック → "Upload to /" で転送

**rshellの場合:**

```bash
rshell --port COM[X]
> cp config.py /pyboard/
> cp main.py /pyboard/
> cp index.html /pyboard/
> cp -r src /pyboard/

```

### 4. 設定調整

`config.py` で以下を調整可能：

* ボード選択 (`BOARD`)
* ピンアサイン
* ボード別PWM設定（`MONOEYE_PWM_WRITE_METHOD`, `MONOEYE_PWM_MAX_DUTY`）
* Wi-Fi SSID/パスワード
* 演出パラメータ（フェード時間、点滅間隔など）

#### LED単体テストモード

DFPlayer Mini をまだ接続していない段階でも、Wi-Fi通信とLED演出だけを安全に確認できます。

```python
DEBUG_LED_ONLY = True
```

* `True`: LED単体テストモード（音声再生・Busy監視・DFPlayer初期化/停止をスキップ）
* `False`: 通常動作モード（音声とLEDを同期して動作）

**この設定はWi-Fi接続、AP起動、WebSocket通信には影響しません。**

### 5. 起動

```python
import main
main.main()

```

または自動起動したい場合は `boot.py` に記述：

```python
import main
main.main()

```

---

## 使い方

### 1. Wi-Fi接続

1. マイコンを起動
2. スマートフォンのWi-Fi設定を開く
3. `config.py` で設定したSSIDに接続（デフォルト: `ZAKU-COCKPIT` / パスワード: `zaku0079`）

### 2. コックピットUI起動

ブラウザで `http://192.168.4.1/` にアクセス

### 3. 操作

* **POWER ON**: モノアイ起動（通常: フェードイン + 起動音 / LED単体テスト時: フェードインのみ）
* **POWER OFF**: モノアイ消灯
* **MACHINE GUN**: 長押しで連射（通常: 音と光が同期 / LED単体テスト時: LED点滅のみ）

※ 現時点では単発専用ボタン・単発専用コマンドは未実装です。

### 4. 最短の確認手順

1. `DEBUG_LED_ONLY = True` に設定して書き込み
2. Wi-Fi接続、Web UI、モノアイLED、マシンガンLEDの動作を確認
3. DFPlayer Mini と MicroSD の配線・音源を準備
4. `DEBUG_LED_ONLY = False` に戻して音声同期を確認

※ 詳細なチェック項目は `DEVELOPMENT.md` の「動作確認」を参照してください。

---

## 制御コマンド

WebSocketで以下のコマンドを送信：

| コマンド | 動作 |
| --- | --- |
| `monoeye_on` | モノアイ起動シーケンス |
| `monoeye_off` | モノアイ消灯 |
| `gun_press` | マシンガン発射開始 |
| `gun_release` | マシンガン発射終了 |

## 安全機能

* **自動タイムアウト**: 60秒間操作がないとモノアイを自動消灯
* **排他制御**: 演出実行中は他のコマンドをブロック

---

## トラブルシューティング

### WebSocketに接続できない

* Wi-Fi接続を確認
* ブラウザのキャッシュをクリア
* マイコンを再起動

### 音が鳴らない

* MicroSDカードのフォーマット確認（FAT32推奨）
* ファイル名が正確か確認（0001.mp3など）
* DFPlayerの配線を確認

### LEDが点灯しない

* ピンアサインを確認
* 抵抗値を確認（330Ω推奨）
* 電源供給を確認

### LEDだけ先に確認したい

* `config.py` の `DEBUG_LED_ONLY = True` を確認
* このモードでは Wi-Fi / WebSocket は通常どおり動作
* DFPlayer の音声再生、Busyピン監視、停止処理はスキップ
* LED動作確認後に `False` へ戻して通常モードを試す

---

## カスタマイズ

### ピンを変更する

`config.py` のピンアサイン設定を変更

### 演出を調整する

`config.py` の演出パラメータを変更：

* `MONOEYE_FADE_DURATION`: フェード時間（秒）
* `MONOEYE_PWM_LOGICAL_MAX`: フェード制御の内部上限値（通常は変更不要）
* `MACHINEGUN_BLINK_INTERVAL`: LED点滅間隔（ミリ秒）
* `DEBUG_LED_ONLY`: LED単体テストモード切り替え（`True` で音声処理をスキップ）
* `DFPLAYER_VOLUME`: 音量（0-30）
* `SESSION_TIMEOUT`: 自動タイムアウト時間（秒、0で無効）

※ `MONOEYE_PWM_WRITE_METHOD` と `MONOEYE_PWM_MAX_DUTY` は `BOARD` に応じて自動設定されるため、通常は変更不要です。

### LEDと音の同期調整

通常利用では、まず `MACHINEGUN_BLINK_INTERVAL` と `*_AUDIO_OFFSET` を `config.py` で微調整してください。

より詳しい確認手順やコードレベルの調整ポイントは `DEVELOPMENT.md` にまとめています。

---

## 開発について

実装メモ、詳細な動作確認チェックリスト、トラブルシューティングの深掘り、拡張アイデアは `DEVELOPMENT.md` を参照してください。

## ライセンス

本プロジェクトはファンメイドの展示支援ツールです。

```

```
