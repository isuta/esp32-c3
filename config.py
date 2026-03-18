# ============================
# ZAKU Motion Control System
# Configuration File
# ============================

# ==================
# 1. ボード選択
# ==================
# "esp32" または "pico2w" を選択
BOARD = "esp32"  # "esp32" または "pico2w"

# ==================
# 2. Wi-Fi設定
# ==================
AP_SSID = "ZAKU-COCKPIT"
AP_PASSWORD = "zaku0079"  # 8文字以上必要
AP_IP = "192.168.4.1"

# ==================
# 3. ピンアサイン (ESP32)
# ==================
if BOARD == "esp32":
    # モノアイLED (PWM対応ピン)
    PIN_MONOEYE = 25
    
    # マシンガンLED (デジタル出力)
    PIN_MACHINEGUN = 26
    
    # DFPlayer Mini (UART)
    PIN_DFPLAYER_TX = 17  # ESP32 TX -> DFPlayer RX
    PIN_DFPLAYER_RX = 16  # ESP32 RX -> DFPlayer TX
    DFPLAYER_UART_ID = 2
    
    # DFPlayer Busy Pin (入力)
    PIN_DFPLAYER_BUSY = 4

# ==================
# 3. ピンアサイン (Raspberry Pi Pico 2 W)
# ==================
elif BOARD == "pico2w":
    # モノアイLED (PWM対応ピン)
    PIN_MONOEYE = 15
    
    # マシンガンLED (デジタル出力)
    PIN_MACHINEGUN = 14
    
    # DFPlayer Mini (UART)
    PIN_DFPLAYER_TX = 0   # Pico TX -> DFPlayer RX
    PIN_DFPLAYER_RX = 1   # Pico RX -> DFPlayer TX
    DFPLAYER_UART_ID = 0
    
    # DFPlayer Busy Pin (入力)
    PIN_DFPLAYER_BUSY = 2

# ==================
# 4. 演出パラメータ
# ==================
# モノアイフェードイン時間（秒）
MONOEYE_FADE_DURATION = 2.0

# モノアイPWM周波数
MONOEYE_PWM_FREQ = 1000

# モノアイ音源の先頭無音時間補正（ミリ秒）
# 音源ファイルの先頭に無音部分がある場合、その分フェードインを遅らせる
MONOEYE_AUDIO_OFFSET = 0  # 0001.mp3: モノアイ起動音の先頭無音補正

# マシンガンLED点滅間隔（ミリ秒）
MACHINEGUN_BLINK_INTERVAL = 100

# マシンガン音源の先頭無音時間補正（ミリ秒）
# 音源ファイルの先頭に無音部分がある場合、その分LEDの点滅を遅らせる
MACHINEGUN_SINGLE_AUDIO_OFFSET = 0  # 0002.mp3: 単発音の先頭無音補正
MACHINEGUN_BURST_AUDIO_OFFSET = 0   # 0003.mp3: 連射音の先頭無音補正

# セッション自動タイムアウト（秒、0で無効）
SESSION_TIMEOUT = 60

# ==================
# 5. DFPlayer設定
# ==================
# ボーレート
DFPLAYER_BAUDRATE = 9600

# 音量 (0-30)
DFPLAYER_VOLUME = 25

# 音源ファイル指定方式
# "simple": ルートディレクトリの連番ファイル (0001.mp3, 0002.mp3, ...)
# "folder": フォルダ/ファイル指定 (/01/001.mp3, /02/005.mp3, ...)
SOUND_MODE = "simple"  # "simple" または "folder"

# === simple モード: ルート直下の連番ファイル ===
# 音源ファイル番号 (SOUND_MODE = "simple" の場合に使用)
SOUND_MONOEYE_ON = 1   # 0001.mp3: モノアイ起動音
SOUND_GUN_SINGLE = 2   # 0002.mp3: マシンガン単発音
SOUND_GUN_BURST = 3    # 0003.mp3: マシンガン連射音

# === folder モード: フォルダ/ファイル指定 ===
# (folder, file) のタプル形式で指定 (SOUND_MODE = "folder" の場合に使用)
# 例: (1, 1) = /01/001.mp3, (2, 5) = /02/005.mp3
SOUND_MONOEYE_ON_FOLDER = (1, 1)   # /01/001.mp3: モノアイ起動音
SOUND_GUN_SINGLE_FOLDER = (1, 2)   # /01/002.mp3: マシンガン単発音
SOUND_GUN_BURST_FOLDER = (1, 3)    # /01/003.mp3: マシンガン連射音

# ==================
# 6. WebSocket設定
# ==================
WEBSOCKET_PORT = 80
