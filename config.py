# サーボの設定をリストで管理 (インデックス1をGPIO5に割り当て)
# index 0は不使用とし、index 1にGPIO 5を設定
SERVO_CONFIG = {
    1: {"pin": 5, "min_duty": 26, "max_duty": 123}
}

# シナリオ間の待機時間 (ミリ秒)
# 0 の場合は待ち時間なしで即座にループします
LOOP_INTERVAL_MS = 2000  # 例：2秒待機