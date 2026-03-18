# ============================
# LED Control Classes
# ============================

import uasyncio as asyncio
from machine import Pin, PWM


class MonoeyeLED:
    """モノアイLED制御クラス (PWM制御)"""
    
    def __init__(self, pin_num, pwm_freq=1000):
        """
        Args:
            pin_num: GPIO ピン番号
            pwm_freq: PWM周波数 (デフォルト: 1000Hz)
        """
        self.pwm = PWM(Pin(pin_num), freq=pwm_freq, duty=0)
        self.current_duty = 0
        
    async def fade_in(self, duration):
        """
        フェードイン
        Args:
            duration: フェード時間（秒）
        """
        steps = 50
        step_delay = duration / steps
        for i in range(steps + 1):
            self.current_duty = int((i / steps) * 1023)
            self.pwm.duty(self.current_duty)
            await asyncio.sleep(step_delay)
    
    def on(self):
        """即座に点灯"""
        self.current_duty = 1023
        self.pwm.duty(self.current_duty)
    
    def off(self):
        """消灯"""
        self.current_duty = 0
        self.pwm.duty(0)


class MachinegunLED:
    """マシンガンLED制御クラス (デジタル出力)"""
    
    def __init__(self, pin_num):
        """
        Args:
            pin_num: GPIO ピン番号
        """
        self.pin = Pin(pin_num, Pin.OUT)
        self.pin.off()
    
    def on(self):
        """点灯"""
        self.pin.on()
    
    def off(self):
        """消灯"""
        self.pin.off()
