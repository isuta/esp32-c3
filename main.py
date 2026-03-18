# ============================
# ZAKU Motion Control System
# Main Entry Point
# ============================

import network
import uasyncio as asyncio
from config import AP_SSID, AP_PASSWORD, AP_IP
from src.zaku_system import ZakuMotionSystem
from src.web_server import start_server


def start_wifi_ap():
    """Wi-Fi Access Point起動"""
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=AP_SSID, password=AP_PASSWORD)
    ap.ifconfig((AP_IP, '255.255.255.0', AP_IP, AP_IP))
    
    print("=" * 40)
    print("ZAKU Motion Control System")
    print("=" * 40)
    print(f"Wi-Fi AP: {AP_SSID}")
    print(f"Password: {AP_PASSWORD}")
    print(f"Access: http://{AP_IP}/")
    print("=" * 40)
    
    return ap


def main():
    """メインエントリーポイント"""
    # Wi-Fi AP起動
    start_wifi_ap()
    
    # システム初期化
    system = ZakuMotionSystem()
    
    # サーバー起動
    try:
        asyncio.run(start_server(system))
    except KeyboardInterrupt:
        print("\n[System] Shutting down...")
        system.monoeye.off()
        system.machinegun.off()


if __name__ == "__main__":
    main()

