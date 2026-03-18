# ============================
# ZAKU Motion Control System Core
# ============================

import uasyncio as asyncio
from src.dfplayer import DFPlayer
from src.led_control import MonoeyeLED, MachinegunLED
from config import *


class ZakuMotionSystem:
    """ザク・モーション制御システムのコアクラス"""
    
    def __init__(self):
        """システム初期化"""
        # ハードウェア初期化
        self.monoeye = MonoeyeLED(PIN_MONOEYE, MONOEYE_PWM_FREQ)
        self.machinegun = MachinegunLED(PIN_MACHINEGUN)
        self.dfplayer = DFPlayer(
            DFPLAYER_UART_ID,
            PIN_DFPLAYER_TX,
            PIN_DFPLAYER_RX,
            DFPLAYER_BAUDRATE,
            PIN_DFPLAYER_BUSY
        )
        
        # 状態管理
        self.is_executing = False
        self.gun_firing = False
        self.session_active = False
        self.last_activity = 0
        
        # DFPlayer初期化
        asyncio.create_task(self.init_dfplayer())
    
    async def init_dfplayer(self):
        """DFPlayer初期化（起動待ちと音量設定）"""
        await asyncio.sleep(1)  # DFPlayer起動待ち
        self.dfplayer.set_volume(DFPLAYER_VOLUME)
        print("[DFPlayer] Initialized with volume:", DFPLAYER_VOLUME)
    
    async def monoeye_on_sequence(self):
        """モノアイ起動シーケンス"""
        if self.is_executing:
            return
        
        self.is_executing = True
        self.session_active = True
        self.last_activity = asyncio.ticks_ms() // 1000
        
        try:
            print("[MONOEYE] ON sequence started")
            
            # 起動音再生
            if SOUND_MODE == "folder":
                folder, track = SOUND_MONOEYE_ON_FOLDER
                self.dfplayer.play_folder_track(folder, track)
            else:
                self.dfplayer.play_track(SOUND_MONOEYE_ON)
            
            # 音源の先頭無音時間補正
            if MONOEYE_AUDIO_OFFSET > 0:
                await asyncio.sleep_ms(MONOEYE_AUDIO_OFFSET)
            
            # フェードイン
            await self.monoeye.fade_in(MONOEYE_FADE_DURATION)
            
            print("[MONOEYE] ON sequence completed")
        finally:
            self.is_executing = False
    
    async def monoeye_off_sequence(self):
        """モノアイ消灯シーケンス"""
        if self.is_executing:
            return
        
        self.is_executing = True
        
        try:
            print("[MONOEYE] OFF sequence started")
            
            # 消灯
            self.monoeye.off()
            
            # サウンド停止
            self.dfplayer.stop()
            
            # セッション終了
            self.session_active = False
            
            print("[MONOEYE] OFF sequence completed")
        finally:
            self.is_executing = False
    
    async def gun_press_sequence(self):
        """マシンガン発射開始"""
        if self.is_executing or self.gun_firing:
            return
        
        self.is_executing = True
        self.gun_firing = True
        self.last_activity = asyncio.ticks_ms() // 1000
        
        try:
            print("[GUN] Press - burst fire started")
            
            # 連射音再生
            if SOUND_MODE == "folder":
                folder, track = SOUND_GUN_BURST_FOLDER
                self.dfplayer.play_folder_track(folder, track)
            else:
                self.dfplayer.play_track(SOUND_GUN_BURST)
            
            # Busyピンが再生中になるまで待機
            for _ in range(50):  # 最大500ms待機
                if self.dfplayer.is_busy():
                    break
                await asyncio.sleep(0.01)
            
            # 音源ファイルの先頭無音部分の補正
            if MACHINEGUN_BURST_AUDIO_OFFSET > 0:
                await asyncio.sleep_ms(MACHINEGUN_BURST_AUDIO_OFFSET)
            
            # LED点滅タスク開始
            asyncio.create_task(self.gun_blink_task())
            
        finally:
            self.is_executing = False
    
    async def gun_release_sequence(self):
        """マシンガン発射終了"""
        if not self.gun_firing:
            return
        
        print("[GUN] Release - waiting for sound to finish")
        self.gun_firing = False
        self.last_activity = asyncio.ticks_ms() // 1000
    
    async def gun_blink_task(self):
        """マシンガンLED点滅タスク"""
        while self.gun_firing or self.dfplayer.is_busy():
            self.machinegun.on()
            await asyncio.sleep_ms(MACHINEGUN_BLINK_INTERVAL // 2)
            self.machinegun.off()
            await asyncio.sleep_ms(MACHINEGUN_BLINK_INTERVAL // 2)
        
        # 確実に消灯
        self.machinegun.off()
        print("[GUN] Blink task stopped")
    
    async def session_timeout_task(self):
        """セッション自動タイムアウト監視"""
        if SESSION_TIMEOUT <= 0:
            return
        
        while True:
            await asyncio.sleep(5)  # 5秒ごとにチェック
            
            if self.session_active:
                current_time = asyncio.ticks_ms() // 1000
                elapsed = current_time - self.last_activity
                
                if elapsed >= SESSION_TIMEOUT:
                    print(f"[SESSION] Timeout after {SESSION_TIMEOUT}s")
                    await self.monoeye_off_sequence()
