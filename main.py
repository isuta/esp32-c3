import machine
import time
import ssd1306

# --- ピン設定 ---
OLED_SDA = 5
OLED_SCL = 6
MIST_PIN_NUM = 1

# --- 表示位置（Mが切れない位置） ---
OFFSET_X = 28
OFFSET_Y = 14

# --- 待機時間の定数 ---
SEC_ON  = 2
SEC_OFF = 2

def setup_hardware():
    i2c = machine.I2C(0, sda=machine.Pin(OLED_SDA), scl=machine.Pin(OLED_SCL))
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)
    mist = machine.Pin(MIST_PIN_NUM, machine.Pin.OUT)
    return oled, mist

def update_oled(oled, status, mode_num):
    if oled:
        oled.fill(0)
        oled.text("MIST SYSTEM", OFFSET_X, OFFSET_Y)
        
        # モード4をOFFとして表示
        mode_label = "OFF" if mode_num == 4 else str(mode_num)
        
        oled.text("MODE:" + mode_label, OFFSET_X, OFFSET_Y + 15)
        oled.text("SIG :" + status, OFFSET_X, OFFSET_Y + 30)
        oled.show()

def main():
    oled, mist = setup_hardware()
    
    # --- 修正の要：カウントの初期値 ---
    # count=6 から始めると、最初の count+=1 で 7 (奇数＝OFF) になります。
    # (7 // 2) % 4 + 1 = 4 (つまり MODE: OFF)
    count = 6
    
    print("--- SYSTEM START (INITIAL: OFF) ---")
    
    while True:
        count += 1
        is_on = (count % 2 == 0)
        status = "ON" if is_on else "OFF"
        
        # 制御用モード計算（動いていたロジックそのまま）
        current_mode = (count // 2) % 4 + 1
        
        # 表示用モードの同期
        # OFFになった瞬間に、ミスト器が切り替わる「次のモード」を画面に出す
        if is_on:
            display_mode = current_mode
        else:
            display_mode = (current_mode % 4) + 1
            
        # ミスト制御
        mist.value(1 if is_on else 0)
        
        # 表示更新
        update_oled(oled, status, display_mode)
        print("Status: " + status + " | DisplayMode: " + str(display_mode))
        
        time.sleep(SEC_ON if is_on else SEC_OFF)

if __name__ == "__main__":
    main()
