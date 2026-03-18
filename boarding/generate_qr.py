"""
QRコード生成スクリプト
boarding.html用のWi-Fi接続QRコードと操作画面URLのQRコードを生成します。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import qrcode
from config import AP_SSID, AP_PASSWORD, AP_IP

def generate_wifi_qr():
    """Wi-Fi接続用QRコード生成"""
    # Wi-Fi QRコードフォーマット: WIFI:T:WPA;S:ssid;P:password;;
    wifi_data = f"WIFI:T:WPA;S:{AP_SSID};P:{AP_PASSWORD};;"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(wifi_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("wifi_qr.png")
    print(f"✓ Wi-Fi QRコード生成完了: wifi_qr.png")
    print(f"  SSID: {AP_SSID}")
    print(f"  Password: {AP_PASSWORD}")

def generate_url_qr():
    """操作画面URL用QRコード生成"""
    url = f"http://{AP_IP}/"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("url_qr.png")
    print(f"✓ 操作画面URL QRコード生成完了: url_qr.png")
    print(f"  URL: {url}")

def main():
    print("=" * 50)
    print("QRコード生成ツール - ZAKU搭乗手続き用")
    print("=" * 50)
    print()
    
    try:
        generate_wifi_qr()
        print()
        generate_url_qr()
        print()
        print("=" * 50)
        print("生成完了！boarding.htmlと同じフォルダに保存されました。")
        print("ブラウザでboarding.htmlを開いて印刷してください。")
        print("=" * 50)
        
    except ImportError as e:
        print(f"❌ エラー: {e}")
        print()
        print("qrcodeライブラリがインストールされていません。")
        print("以下のコマンドでインストールしてください：")
        print()
        print("  pip install qrcode[pil]")
        print()
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
