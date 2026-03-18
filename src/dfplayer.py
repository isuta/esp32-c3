# ============================
# DFPlayer Mini Controller
# ============================

from machine import Pin, UART


class DFPlayer:
    """DFPlayer Mini サウンドモジュール制御クラス"""
    
    def __init__(self, uart_id, tx_pin, rx_pin, baudrate=9600, busy_pin=None):
        """
        Args:
            uart_id: UART ID
            tx_pin: TX ピン番号
            rx_pin: RX ピン番号
            baudrate: ボーレート (デフォルト: 9600)
            busy_pin: Busy ピン番号
        """
        self.uart = UART(uart_id, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin))
        self.busy_pin = Pin(busy_pin, Pin.IN) if busy_pin else None
        
    def send_command(self, cmd, param=0):
        """DFPlayerにコマンドを送信"""
        buf = bytearray(10)
        buf[0] = 0x7E  # Start
        buf[1] = 0xFF  # Version
        buf[2] = 0x06  # Length
        buf[3] = cmd   # Command
        buf[4] = 0x00  # Feedback (no feedback)
        buf[5] = (param >> 8) & 0xFF  # Param high byte
        buf[6] = param & 0xFF           # Param low byte
        
        # Checksum calculation
        checksum = -(buf[1] + buf[2] + buf[3] + buf[4] + buf[5] + buf[6])
        buf[7] = (checksum >> 8) & 0xFF
        buf[8] = checksum & 0xFF
        buf[9] = 0xEF  # End
        
        self.uart.write(buf)
    
    def set_volume(self, volume):
        """音量設定 (0-30)"""
        self.send_command(0x06, volume)
    
    def play_track(self, track_num):
        """トラック再生（ルートディレクトリの連番ファイル）"""
        self.send_command(0x03, track_num)
    
    def play_folder_track(self, folder, track_num):
        """
        フォルダとファイルを指定して再生
        Args:
            folder: フォルダ番号 (1-99)
            track_num: ファイル番号 (1-255)
        
        SDカード構成例:
            /01/001.mp3
            /01/002.mp3
            /02/001.mp3
        """
        # パラメータ: 上位バイト=フォルダ、下位バイト=ファイル
        param = (folder << 8) | track_num
        self.send_command(0x0F, param)
    
    def stop(self):
        """再生停止"""
        self.send_command(0x16)
    
    def is_busy(self):
        """再生中か確認 (Busyピン: LOW=再生中, HIGH=停止中)"""
        if self.busy_pin:
            return self.busy_pin.value() == 0
        return False
