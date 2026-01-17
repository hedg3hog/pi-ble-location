from rich.live import Live
from rich.text import Text
import time
import random

W, H = 20, 10

def render(x, y):
    t = Text()
    

    for j in range(H):
        for i in range(W):
            t.append("●" if (i, j) == (x, y) else "·")
        t.append("\n")
    return t

x = y = 0

with Live(render(x, y), refresh_per_second=20) as live:
    while True:
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        live.update(render(x, y))
        time.sleep(0.1)


