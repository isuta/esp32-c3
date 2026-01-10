import json
import utime
from servo_controller import ServoController
from config import LOOP_INTERVAL_MS  # 設定をインポート

def run_scenario(controller, scenario_data):
    for step in scenario_data:
        # 待機コマンド
        if "wait_ms" in step:
            utime.sleep_ms(step["wait_ms"])
            continue

        # サーボ操作コマンド
        if step.get("type") == "servo":
            if step.get("command") == "set_angle":
                controller.set_angle(
                    step.get("servo_index"), 
                    step.get("angle"), 
                    step.get("duration_ms", 0)
                )

def main():
    controller = ServoController()
    
    # ファイル読み込み
    try:
        with open("scenarios.json", "r") as f:
            data = json.load(f)
        
        scenario_name = "servo_calibrate"
        if scenario_name not in data:
            print(f"Error: Scenario '{scenario_name}' not found.")
            return

        print(f"Starting loop for scenario: {scenario_name}")
        
        # --- 永久ループ開始 ---
        while True:
            # シナリオ実行
            run_scenario(controller, data[scenario_name])
            
            # ループ間の待機処理
            if LOOP_INTERVAL_MS > 0:
                print(f"Loop finished. Waiting {LOOP_INTERVAL_MS}ms...")
                utime.sleep_ms(LOOP_INTERVAL_MS)
            else:
                # 0の場合は表示なしで即ループ
                pass

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Ctrl+C などで停止した場合にPWMを解放
        controller.deinit()
        print("Program stopped.")

if __name__ == "__main__":
    main()