import threading
import time
from rich.live import Live
from rich.text import Text
import uvicorn
import capture_server


W, H = capture_server.W, capture_server.H

def render():
    t = Text()
    x = round(capture_server.position.x, ndigits=0)
    y = round(capture_server.position.y, ndigits=0)
    if x > W or y>H or x < 0 or y<0:
        t.append(f"x or y out of range: ({x}, {y})")
        return t
    for j in range(H):
        for i in range(W):
            t.append("●" if (i, j) == (x, y) else "·")
        t.append("\n")
    t.append("\n")
    t.append(f"Last Update{capture_server.last_pos_update.now.isoformat()} ({capture_server.position.x}, {capture_server.position.y})\n")
    return t

def run_server():
    uvicorn.run(
        "capture_server:app",
        host="0.0.0.0",
        port=8000,
        workers=1,  # WICHTIG
        log_level="warning"
    )

# Webserver im Hintergrund
threading.Thread(target=run_server, daemon=True).start()

# Live Display
with Live(render(), refresh_per_second=2) as live:
    while True:
        live.update(render())
        time.sleep(1)
