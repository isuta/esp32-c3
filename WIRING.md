# 配線ガイド

このドキュメントは、実機テスト前に必要な配線情報だけをまとめたクイックリファレンスです。

実装上の正しいピン定義は `config.py` にあります。配線を変更した場合は、必ず `config.py` の `BOARD` とピン設定も合わせて確認してください。

## 先に決めること

- ESP32 DevKit V1 を使う → `BOARD = "esp32"`
- Raspberry Pi Pico 2 W を使う → `BOARD = "pico2w"`

`BOARD` の設定によって、LED と DFPlayer の使用 GPIO が切り替わります。

## まずはこの順で配線するのがおすすめ

1. モノアイLED
2. マシンガンLED
3. `DEBUG_LED_ONLY = True` で LED 単体確認
4. DFPlayer Mini
5. `DEBUG_LED_ONLY = False` で音声込み確認

最初から DFPlayer まで全部つなぐより、LED だけ先に確認した方が切り分けしやすいです。

## ブレッドボード前提の組み方

このシステムは、ブレッドボードでの仮組みで十分再現できます。
はんだ付け前の確認や、展示前の切り分け用途としても向いています。

### まず押さえるポイント

- **GND は共通にする**
	- マイコンの `GND`
	- DFPlayer Mini の `GND`
	- LED のカソード(-)
	- これらを同じ GND ラインにまとめる
- **LED には必ず抵抗を入れる**
	- 推奨は `330Ω`
- **TX / RX は交差接続**
	- マイコン `TX -> DFPlayer RX`
	- マイコン `RX -> DFPlayer TX`
- **最初は LED だけで確認する**
	- `DEBUG_LED_ONLY = True` にして Wi-Fi / Web UI / LED のみ先に確認

### ブレッドボード上のおすすめ配置

1. マイコンを中央の溝をまたぐように載せる
2. 電源レールの片側を `GND` 用に決める
3. もう片側を DFPlayer 用電源として使う
	 - ESP32 の場合: `5V`
	 - Pico 2 W の場合: `VBUS`
4. モノアイLEDとマシンガンLEDをブレッドボード端側に置く
5. LED の直列に抵抗を入れる
6. DFPlayer Mini は LED 配線確認後に追加する

### LED だけ先に組む場合の最小構成

- マイコン
- モノアイLED + 抵抗
- マシンガンLED + 抵抗
- 共通 GND

この状態で `DEBUG_LED_ONLY = True` にすれば、音声系をつながずに以下だけ確認できます。

- Wi-Fi AP が立ち上がるか
- `http://192.168.4.1/` が開くか
- `POWER ON` でモノアイLEDが点灯するか
- `MACHINE GUN` 長押しでマシンガンLEDが点滅するか

### DFPlayer を後から追加する場合

LED 単体確認ができたら、次を追加します。

- DFPlayer `VCC`
- DFPlayer `GND`
- DFPlayer `RX` / `TX`
- DFPlayer `BUSY`
- スピーカー (`SPK_1`, `SPK_2`)

その後、`DEBUG_LED_ONLY = False` に戻して音声込み確認を行います。

### ESP32 をブレッドボードで使うときの注意

- ESP32 DevKit V1 は横幅が広めなので、ブレッドボードの行をかなり使います
- 小さいブレッドボードだと配線スペースが足りなくなりやすいです
- 余裕のあるブレッドボードか、電源レール付きのものが扱いやすいです

### Pico 2 W をブレッドボードで使うときの注意

- Pico 2 W は細長いので、仮組みは比較的やりやすいです
- ただし `VBUS` を DFPlayer の電源に使う場合は、電源ラインの取り回しを先に決めておくと混乱しにくいです

### よくあるハマりどころ

- LED の向きが逆
- GND が共通になっていない
- TX / RX を同じ名前同士でつないでいる
- DFPlayer の BUSY を未接続のまま同期確認しようとしている
- ジャンパーが半刺さりで接触していない

---

## ESP32 DevKit V1 配線

### GPIO 割り当て

| 用途 | ESP32 側 | 接続先 |
| --- | --- | --- |
| モノアイLED | GPIO25 | 330Ω抵抗経由で LEDアノード(+) |
| マシンガンLED | GPIO26 | 330Ω抵抗経由で LEDアノード(+) |
| DFPlayer TX | GPIO17 | DFPlayer RX |
| DFPlayer RX | GPIO16 | DFPlayer TX |
| DFPlayer Busy | GPIO4 | DFPlayer BUSY |
| 電源 | 5V | DFPlayer VCC |
| GND | GND | DFPlayer GND / LEDカソード(-)側 |

### LED 配線

#### モノアイLED

- `GPIO25` → `330Ω抵抗` → モノアイLEDのアノード(+)
- モノアイLEDのカソード(-) → `GND`

#### マシンガンLED

- `GPIO26` → `330Ω抵抗` → マシンガンLEDのアノード(+)
- マシンガンLEDのカソード(-) → `GND`

### DFPlayer Mini 配線

| ESP32 | DFPlayer Mini |
| --- | --- |
| GPIO17 (TX) | RX |
| GPIO16 (RX) | TX |
| GPIO4 | BUSY |
| 5V | VCC |
| GND | GND |

### スピーカー

- DFPlayer Mini の `SPK_1` / `SPK_2` にスピーカーを接続

### 配線後の最小確認

- `BOARD = "esp32"` を確認
- LED だけ先に試すなら `DEBUG_LED_ONLY = True`
- LED確認後に DFPlayer をつないで `DEBUG_LED_ONLY = False`

---

## Raspberry Pi Pico 2 W 配線

### GPIO 割り当て

| 用途 | Pico 2 W 側 | 接続先 |
| --- | --- | --- |
| モノアイLED | GPIO15 | 330Ω抵抗経由で LEDアノード(+) |
| マシンガンLED | GPIO14 | 330Ω抵抗経由で LEDアノード(+) |
| DFPlayer TX | GPIO0 | DFPlayer RX |
| DFPlayer RX | GPIO1 | DFPlayer TX |
| DFPlayer Busy | GPIO2 | DFPlayer BUSY |
| 電源 | VBUS | DFPlayer VCC |
| GND | GND | DFPlayer GND / LEDカソード(-)側 |

### LED 配線

#### モノアイLED

- `GPIO15` → `330Ω抵抗` → モノアイLEDのアノード(+)
- モノアイLEDのカソード(-) → `GND`

#### マシンガンLED

- `GPIO14` → `330Ω抵抗` → マシンガンLEDのアノード(+)
- マシンガンLEDのカソード(-) → `GND`

### DFPlayer Mini 配線

| Pico 2 W | DFPlayer Mini |
| --- | --- |
| GPIO0 (TX) | RX |
| GPIO1 (RX) | TX |
| GPIO2 | BUSY |
| VBUS | VCC |
| GND | GND |

### スピーカー

- DFPlayer Mini の `SPK_1` / `SPK_2` にスピーカーを接続

### 配線後の最小確認

- `BOARD = "pico2w"` を確認
- LED だけ先に試すなら `DEBUG_LED_ONLY = True`
- LED確認後に DFPlayer をつないで `DEBUG_LED_ONLY = False`

---

## 共通の注意点

### LED の向き

- アノード(+) → GPIO 側
- カソード(-) → GND 側

逆につなぐと光りません。LED 側の定番トラブル王です。

### 抵抗

- 推奨: `330Ω`
- 目安: `100Ω〜470Ω` でも可

### UART の TX / RX

- **TX と RX は交差接続**です
- つまり、マイコンの `TX → DFPlayer RX`、マイコンの `RX → DFPlayer TX`

ここを同じ名前同士でつなぐと通信できません。UART あるあるです。

### BUSY ピン

- LED と音の同期確認では `BUSY` 配線が重要です
- BUSY 未接続だと、音声連動の確認が不完全になります

### 電源

- ESP32 は `5V → DFPlayer VCC`
- Pico 2 W は `VBUS → DFPlayer VCC`
- GND は必ず共通にする

### 実装上の前提

現時点で使用している音源は以下です。

- `0001.mp3`: モノアイ起動音
- `0003.mp3`: マシンガン連射音

`0002.mp3` は将来の単発演出用で、現状の実装では未使用です。

## 次に見る場所

- 実機の確認手順: `DEVELOPMENT.md`
- 利用者向けの全体説明: `readme.md`
- 実際のピン定義と設定値: `config.py`
