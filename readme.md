
# ザク・モーション制御システム (ZAKU Motion Control System)

スマートフォンを「コックピット端末」に見立て、Wi-Fi経由で模型のモノアイ点灯や武器（マシンガン）の音・光をリアルタイム制御するシステムです。

## 特徴

- 🎮 **WebベースUI** - アプリ不要、QRコードから即座に操作可能
- 🔌 **マルチデバイス対応** - ESP32およびRaspberry Pi Pico 2 W対応
- 🎵 **同期演出** - DFPlayer Miniを使用し、音と光を完全同期
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

## セットアップ

### 1. ハードウェア接続 (ESP32の場合)

```
ESP32          DFPlayer Mini
GPIO17 (TX) -> RX
GPIO16 (RX) -> TX
GPIO4       -> BUSY
GND         -> GND
5V          -> VCC

GPIO25      -> モノアイLED+
GPIO26      -> マシンガンLED+

※各LEDはGNDに抵抗(330Ω推奨)経由で接続
```

### 2. MicroSDカード準備

DFPlayer Mini用のMicroSDカードをFAT32でフォーマットし、以下のいずれかの方式で音源ファイルを配置：

#### 方式1: simple モード（シンプル、デフォルト）

ルートディレクトリに連番ファイルを配置：

```
/
├── 0001.mp3 - モノアイ起動音
├── 0002.mp3 - マシンガン単発音
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
│   ├── 002.mp3 - マシンガン単発音
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
SOUND_GUN_SINGLE_FOLDER = (1, 2)   # /01/002.mp3
SOUND_GUN_BURST_FOLDER = (1, 3)    # /01/003.mp3
```

**注意**: 
- フォルダ名は01〜99の2桁数字
- ファイル名は001〜255の3桁数字
- 拡張子は.mp3

### 3. ファイル転送

以下のファイルをマイコンに転送してください：

#### 必須ファイル（7個）

```
esp32-c3/
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

[config.py](config.py) で以下を調整可能：

- ボード選択 (`BOARD`)
- ピンアサイン
- Wi-Fi SSID/パスワード
- 演出パラメータ（フェード時間、点滅間隔など）

### 5. 起動

```python
import main
```

または自動起動したい場合は `boot.py` に記述：

```python
import main
main.main()
```

## 使い方

### 1. Wi-Fi接続

1. マイコンを起動
2. スマートフォンのWi-Fi設定を開く
3. `ZAKU-COCKPIT` に接続（パスワード: `zaku0079`）

### 2. コックピットUI起動

ブラウザで `http://192.168.4.1/` にアクセス

### 3. 操作

- **POWER ON**: モノアイ起動（フェードイン + 起動音）
- **POWER OFF**: モノアイ消灯
- **MACHINE GUN**: 長押しで連射（音と光が同期）

## 制御コマンド

WebSocketで以下のコマンドを送信：

| コマンド | 動作 |
|----------|------|
| `monoeye_on` | モノアイ起動シーケンス |
| `monoeye_off` | モノアイ消灯 |
| `gun_press` | マシンガン発射開始 |
| `gun_release` | マシンガン発射終了 |

## 安全機能

- **自動タイムアウト**: 60秒間操作がないとモノアイを自動消灯
- **排他制御**: 演出実行中は他のコマンドをブロック

## トラブルシューティング

### WebSocketに接続できない

- Wi-Fi接続を確認
- ブラウザのキャッシュをクリア
- マイコンを再起動

### 音が鳴らない

- MicroSDカードのフォーマット確認（FAT32推奨）
- ファイル名が正確か確認（0001.mp3など）
- DFPlayerの配線を確認

### LEDが点灯しない

- ピンアサインを確認
- 抵抗値を確認（330Ω推奨）
- 電源供給を確認

## カスタマイズ

### ピンを変更する

[config.py](config.py) のピンアサイン設定を変更

### 演出を調整する

[config.py](config.py) の演出パラメータを変更：
- `MONOEYE_FADE_DURATION`: フェード時間（秒）
- `MACHINEGUN_BLINK_INTERVAL`: LED点滅間隔（ミリ秒）
- `MACHINEGUN_SINGLE_AUDIO_OFFSET`: 単発音の先頭無音補正（ミリ秒）
- `MACHINEGUN_BURST_AUDIO_OFFSET`: 連射音の先頭無音補正（ミリ秒）
- `DFPLAYER_VOLUME`: 音量（0-30）
- `SESSION_TIMEOUT`: 自動タイムアウト時間（秒、0で無効）

### LEDと音の同期タイミングを調整する

マシンガンのLED点滅と音がズレている場合は、以下で調整できます：

#### 1. LED点滅速度の調整

[config.py](config.py) の `MACHINEGUN_BLINK_INTERVAL` を変更：

```python
# マシンガンLED点滅間隔（ミリ秒）
MACHINEGUN_BLINK_INTERVAL = 100  # デフォルト値
```

- **値を小さく** (例: 50) → LED点滅が速くなる
- **値を大きく** (例: 150) → LED点滅が遅くなる
- 音源ファイル（0003.mp3）のリズムに合わせて調整

#### 2. 音源ファイルの先頭無音補正

音源ファイルの先頭に無音部分がある場合、LEDが音より先に点滅してしまいます。
[config.py](config.py) で各音源の無音時間を個別に補正できます：

```python
# マシンガン音源の先頭無音時間補正（ミリ秒）
MACHINEGUN_SINGLE_AUDIO_OFFSET = 0  # 0002.mp3: 単発音用
MACHINEGUN_BURST_AUDIO_OFFSET = 0   # 0003.mp3: 連射音用
```

**使い方**:
- 連射音（0003.mp3）の先頭に50msの無音がある → `MACHINEGUN_BURST_AUDIO_OFFSET = 50`
- 単発音（0002.mp3）の先頭に30msの無音がある → `MACHINEGUN_SINGLE_AUDIO_OFFSET = 30`
- 各音源ファイルごとに個別に設定できるため、異なる音源でも柔軟に対応可能

**現在の実装**: 連射音（`MACHINEGUN_BURST_AUDIO_OFFSET`）のみ使用。将来的に単発音を実装する際は`MACHINEGUN_SINGLE_AUDIO_OFFSET`を使用します。

#### 3. LEDが音より遅れる場合（上級者向け）

[src/zaku_system.py](src/zaku_system.py) の `gun_press_sequence()` 関数で、Busy待機をスキップまたは調整：

```py4. LEDが音より早い場合（上級者向け）
# 連射音再生
self.dfplayer.play_track(SOUND_GUN_BURST)

# この待機処理をコメントアウトすると即座にLED点滅開始
# for _ in range(50):
#     if self.dfplayer.is_busy():
#         break
#     await asyncio.sleep(0.01)

# LED点滅タスク開始
asyncio.create_task(self.gun_blink_task())
```

#### 3. LEDが音より早い場合

待機時間を増やして遅延を追加：

```python
# 連射音再生
self.dfplayer.play_track(SOUND_GUN_BURST)

# 固定遅延を追加（例: 50ms〜200ms）
await asyncio.sleep(0.1)  # 100ms待機

# LED点滅タスク開始
asyncio.create_task(self.gun_blink_task())
```BURST_AUDIO_OFFSET` (連射音) や `MACHINEGUN_SINGLE_AUDIO_OFFSET` (単発音)

**推奨調整手順**: 
1. まず `MACHINEGUN_BLINK_INTERVAL` で点滅速度を調整
2. 音源に先頭無音がある場合は `MACHINEGUN_AUDIO_OFFSET` で補正
3. それでもズレる場合のみコードを修正

### 音源を変更する

MicroSDカード内のmp3ファイルを差し替え

### 音量を調整する

[config.py](config.py) の `DFPLAYER_VOLUME` で音量を変更：

```python
# 音量 (0-30)
DFPLAYER_VOLUME = 25  # デフォルト値
```

- **範囲**: 0（無音）〜 30（最大音量）
- **推奨値**: 20〜25
- 値を変更してマイコンに再転送すると、起動時に自動的に設定されます
- 音が小さすぎる/大きすぎる場合はこの値で調整してください

## 開発について

### モジュール構成

コードは機能ごとにモジュール分割されています：

- **`src/dfplayer.py`**: DFPlayer Mini制御（サウンド再生）
- **`src/led_control.py`**: LED制御（モノアイ、マシンガン）
- **`src/zaku_system.py`**: システムコア（演出ロジック、状態管理）
- **`src/web_server.py`**: WebSocket/HTTPサーバー（通信処理）
- **`main.py`**: エントリーポイント（起動とWi-Fi AP設定）
- **`config.py`**: 設定ファイル（ピンアサイン、パラメータ）

### コードを編集する場合

1. **設定の変更**: `config.py` を編集してマイコンに再転送
2. **機能の追加/修正**: 該当する `src/` 内のファイルを編集
3. **新しいLED追加**: `src/led_control.py` にクラスを追加
4. **新しい演出追加**: `src/zaku_system.py` にシーケンス関数を追加
5. **新しいコマンド追加**: `src/web_server.py` のコマンド処理とUIの両方を更新

### 詳細な開発ガイド

詳細なセットアップ手順、トラブルシューティング、拡張アイデアは [DEVELOPMENT.md](DEVELOPMENT.md) を参照してください。

## ライセンス

本プロジェクトはファンメイドの展示支援ツールです。

## 詳細仕様

詳細な動作仕様は [ザク・モーション制御システム (ZAKU Motion Control Sy.md)](ザク・モーション制御システム%20(ZAKU%20Motion%20Control%20Sy.md) を参照してください。

