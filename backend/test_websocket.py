#!/usr/bin/env python3
"""Test WebSocket connection to camera stream"""
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/cameras/stream"
    print(f"Connecting to: {uri}")
    print("-" * 50)
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected!")
            print("Waiting for frames...")
            
            frame_count = 0
            async for message in websocket:
                data = json.loads(message)
                
                if data.get("type") == "frame":
                    frame_count += 1
                    if frame_count == 1:
                        print("✅ First frame received!")
                    if frame_count % 30 == 0:
                        print(f"Received {frame_count} frames...")
                
                elif data.get("type") == "error":
                    print(f"❌ Server error: {data.get('message')}")
                    break
                
                elif data.get("type") == "attendance_marked":
                    print(f"🎓 Attendance: {data.get('name')} ({data.get('student_id')})")
                
                # Stop after 100 frames for testing
                if frame_count >= 100:
                    print(f"\n✅ Test passed! Received {frame_count} frames")
                    break
                    
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Connection rejected: {e}")
        print("   Status code:", e.status_code)
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
    except ConnectionRefusedError:
        print("❌ Connection refused - is the backend running?")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("  WebSocket Camera Stream Test")
    print("=" * 50)
    print()
    asyncio.run(test_websocket())
