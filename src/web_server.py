# ============================
# Web Server (HTTP + WebSocket)
# ============================

import uasyncio as asyncio
import struct
import gc
from config import WEBSOCKET_PORT


async def _read_exact(reader, size):
    """指定サイズ分を確実に読み込む"""
    data = bytearray()
    while len(data) < size:
        chunk = await reader.read(size - len(data))
        if not chunk:
            return None
        data.extend(chunk)
    return bytes(data)


async def handle_websocket(reader, writer, system, headers):
    """WebSocket接続ハンドラ"""
    print("[WebSocket] Client connected")
    
    try:
        # Sec-WebSocket-Key抽出
        key = headers.get('Sec-WebSocket-Key')
        
        if key:
            # ハンドシェイク応答
            import uhashlib
            import ubinascii
            accept_key = ubinascii.b2a_base64(
                uhashlib.sha1(key.encode() + b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest()
            ).decode().strip()
            
            response = (
                'HTTP/1.1 101 Switching Protocols\r\n'
                'Upgrade: websocket\r\n'
                'Connection: Upgrade\r\n'
                f'Sec-WebSocket-Accept: {accept_key}\r\n'
                '\r\n'
            )
            writer.write(response.encode())
            await writer.drain()
            
            # メッセージ受信ループ
            while True:
                frame_header = await _read_exact(reader, 2)
                if not frame_header:
                    break
                
                # フレーム解析
                payload_len = frame_header[1] & 0x7F
                
                if payload_len == 126:
                    payload_len_bytes = await _read_exact(reader, 2)
                    if not payload_len_bytes:
                        break
                    payload_len = struct.unpack('>H', payload_len_bytes)[0]
                elif payload_len == 127:
                    payload_len_bytes = await _read_exact(reader, 8)
                    if not payload_len_bytes:
                        break
                    payload_len = struct.unpack('>Q', payload_len_bytes)[0]
                
                # マスクキー読み込み
                mask = await _read_exact(reader, 4)
                if not mask:
                    break
                
                # ペイロード読み込み
                masked_payload = await _read_exact(reader, payload_len)
                if masked_payload is None:
                    break
                
                # マスク解除
                payload = bytearray(masked_payload)
                for i in range(len(payload)):
                    payload[i] ^= mask[i % 4]
                
                message = payload.decode('utf-8')
                print(f"[WebSocket] Received: {message}")
                
                # コマンド処理
                if message == "monoeye_on":
                    asyncio.create_task(system.monoeye_on_sequence())
                elif message == "monoeye_off":
                    asyncio.create_task(system.monoeye_off_sequence())
                elif message == "gun_press":
                    asyncio.create_task(system.gun_press_sequence())
                elif message == "gun_release":
                    asyncio.create_task(system.gun_release_sequence())
                
                gc.collect()
        else:
            response = (
                'HTTP/1.1 400 Bad Request\r\n'
                'Content-Type: text/plain\r\n'
                'Connection: close\r\n'
                '\r\n'
                'Missing Sec-WebSocket-Key'
            )
            writer.write(response.encode())
            await writer.drain()
    
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
        print("[WebSocket] Client disconnected")


async def handle_http(reader, writer, system):
    """HTTP リクエストハンドラ"""
    upgraded_to_websocket = False

    try:
        request_line = await reader.readline()
        request_str = request_line.decode('utf-8')
        
        # ヘッダー読み込み
        headers = {}
        while True:
            line = await reader.readline()
            if line == b'\r\n':
                break
            line_str = line.decode('utf-8').strip()
            if ':' in line_str:
                key, value = line_str.split(':', 1)
                headers[key.strip()] = value.strip()
        
        # WebSocketアップグレード判定
        if headers.get('Upgrade', '').lower() == 'websocket':
            upgraded_to_websocket = True
            await handle_websocket(reader, writer, system, headers)
            return
        
        # 通常のHTTPリクエスト
        if 'GET / ' in request_str or 'GET /index.html' in request_str:
            try:
                with open('index.html', 'r') as f:
                    content = f.read()
                
                response = (
                    'HTTP/1.1 200 OK\r\n'
                    'Content-Type: text/html; charset=utf-8\r\n'
                    f'Content-Length: {len(content)}\r\n'
                    'Connection: close\r\n'
                    '\r\n'
                )
                writer.write(response.encode())
                writer.write(content.encode())
            except OSError:
                response = (
                    'HTTP/1.1 404 Not Found\r\n'
                    'Content-Type: text/plain\r\n'
                    'Connection: close\r\n'
                    '\r\n'
                    'index.html not found'
                )
                writer.write(response.encode())
        else:
            response = (
                'HTTP/1.1 404 Not Found\r\n'
                'Content-Type: text/plain\r\n'
                'Connection: close\r\n'
                '\r\n'
                '404 Not Found'
            )
            writer.write(response.encode())
        
        await writer.drain()
    
    except Exception as e:
        print(f"[HTTP] Error: {e}")
    finally:
        if not upgraded_to_websocket:
            writer.close()
            await writer.wait_closed()


async def start_server(system):
    """Webサーバー起動"""
    server = await asyncio.start_server(
        lambda r, w: handle_http(r, w, system),
        "0.0.0.0",
        WEBSOCKET_PORT
    )
    
    print(f"[Server] Listening on port {WEBSOCKET_PORT}")
    
    # セッションタイムアウト監視開始
    asyncio.create_task(system.session_timeout_task())
    
    async with server:
        await server.wait_closed()
