# ============================
# LED Control Classes
# ============================

import uasyncio as asyncio
from machine import Pin, PWM
from config import MONOEYE_PWM_LOGICAL_MAX, MONOEYE_PWM_MAX_DUTY, MONOEYE_PWM_WRITE_METHOD


class MonoeyeLED:
    """モノアイLED制御クラス (PWM制御)"""
    
    def __init__(self, pin_num, pwm_freq=1000):
        """
        Args:
            pin_num: GPIO ピン番号
            pwm_freq: PWM周波数 (デフォルト: 1000Hz)
        """
        self.pwm = PWM(Pin(pin_num))
        self.pwm.freq(pwm_freq)
        self._pwm_write = getattr(self.pwm, MONOEYE_PWM_WRITE_METHOD, None)
        if self._pwm_write is None:
            raise AttributeError(
                "PWM write method '{}' is not supported on this board".format(MONOEYE_PWM_WRITE_METHOD)
            )
        self.current_duty = 0
        self._write_duty(0)

    def _write_duty(self, logical_duty):
        """論理Duty値(0-1023)をボード別PWM値へ変換して出力"""
        logical_duty = max(0, min(MONOEYE_PWM_LOGICAL_MAX, int(logical_duty)))
        self.current_duty = logical_duty
        board_duty = (logical_duty * MONOEYE_PWM_MAX_DUTY) // MONOEYE_PWM_LOGICAL_MAX
        self._pwm_write(board_duty)
        
    async def fade_in(self, duration):
        """
        フェードイン
        Args:
            duration: フェード時間（秒）
        """
        steps = 50
        step_delay = duration / steps
        for i in range(steps + 1):
            logical_duty = int((i / steps) * MONOEYE_PWM_LOGICAL_MAX)
            self._write_duty(logical_duty)
            await asyncio.sleep(step_delay)
    
    def on(self):
        """即座に点灯"""
        self._write_duty(MONOEYE_PWM_LOGICAL_MAX)
    
    def off(self):
        """消灯"""
        self._write_duty(0)


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
