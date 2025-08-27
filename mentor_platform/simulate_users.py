
# import asyncio
# import websockets
# import json
# import random
# import string
# import time

# WS_URL = "ws://127.0.0.1:8000/ws/chat/group/279/"  # your group WebSocket URL



import asyncio
import websockets
import json
import random
import string
import time

# WebSocket endpoint
WS_URL = "ws://127.0.0.1:8000/ws/chat/group/279/"  # your group WebSocket URL

# Number of simulated users
NUM_USERS = 500
# How long the test should run (seconds)
DURATION = 300  # 5 minutes


async def simulate_user(user_id: int):
    try:
        async with websockets.connect(WS_URL) as ws:
            print(f"[User {user_id}] Connected")

            start_time = time.time()

            while time.time() - start_time < DURATION:
                # Weighted random choice: mostly messages
                action = random.choices(
                    ["message", "typing", "idle"],
                    weights=[0.7, 0.2, 0.1],  # 70% message, 20% typing, 10% idle
                    k=1
                )[0]

                if action == "message":
                    msg = ''.join(random.choices(string.ascii_letters, k=random.randint(10, 30)))
                    payload = {
                        "message": msg,
                        "sender": f"user_{user_id}",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "profile_picture": f"http://localhost:8000/media/profile_pictures/user_{user_id}.jpg"
                    }
                    {"message":"hiiiiiii","sender":"harshitkh9","timestamp":"2025-08-25T05:21:19.376Z","profile_picture":"http://localhost:8000/media/profile_pictures/photo_7dgvNq4.jpg"}
                    await ws.send(json.dumps(payload))
                    print(f"[User {user_id}] Sent message: {msg}")

                elif action == "typing":
                    payload = {
                        "type": "typing",
                        "sender": f"user_{user_id}"
                    }
                    await ws.send(json.dumps(payload))
                    print(f"[User {user_id}] Typing...")

                # Delay between actions
                await asyncio.sleep(random.uniform(0.5, 2.0))

    except Exception as e:
        print(f"[User {user_id}] Error: {e}")


async def main():
    tasks = [simulate_user(i) for i in range(NUM_USERS)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
