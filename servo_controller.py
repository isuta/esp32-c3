import machine
import utime
from config import SERVO_CONFIG

class ServoController:
    def __init__(self):
        self.servos = {}
        self.step_interval_ms = 20  # 動作がスムーズになるよう20msに戻しました
        
        for idx, conf in SERVO_CONFIG.items():
            pin = machine.Pin(conf["pin"])
            pwm = machine.PWM(pin, freq=50)
            self.servos[idx] = {
                "pwm": pwm,
                "min": conf["min_duty"],
                "max": conf["max_duty"],
                "current_angle": 0
            }
            # 起動時の位置を0度に固定
            self._write_duty(idx, 0)
            utime.sleep_ms(200)

    def _write_duty(self, index, angle):
        """Duty比を計算して書き込む"""
        s = self.servos[index]
        duty = int(s["min"] + (angle / 180) * (s["max"] - s["min"]))
        s["pwm"].duty(duty)
        s["current_angle"] = angle

    def set_angle(self, index, target_angle, duration_ms=0):
        if index not in self.servos:
            return

        start_angle = self.servos[index]["current_angle"]
        angle_diff = target_angle - start_angle
        
        # 移動不要、または即時移動の場合
        if duration_ms <= self.step_interval_ms or angle_diff == 0:
            self._write_duty(index, target_angle)
            return

        # ステップ数の計算
        steps = int(duration_ms / self.step_interval_ms)
        
        for i in range(1, steps + 1):
            next_angle = start_angle + (angle_diff * (i / steps))
            self._write_duty(index, next_angle)
            utime.sleep_ms(self.step_interval_ms)
        
        # 最後に目標角度に補正
        self._write_duty(index, target_angle)

    def deinit(self):
        for s in self.servos.values():
            s["pwm"].deinit()