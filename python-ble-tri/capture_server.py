import logging
from sqlmodel import Session
from models import BLEcapture, engine
from fastapi import FastAPI
from statistics import mean, median
from itertools import combinations
from datetime import datetime

###################
##### LOGGING #####
###################

class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m"
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(ColorFormatter("%(levelname)-8s [%(name)s:%(threadName)s:%(lineno)d] %(message)s"))
logger.addHandler(stdout_handler)

class Update():
    def __init__(self) -> None:
        self.now = datetime.now()
    
    def update(self):
        self.now = datetime.now()
    

class Measurement:
    def __init__(self, keep=5, prefill=-65) -> None:
        self.keep = 5
        self.data = [prefill for _ in range(keep)]
        #print(self.data)
        self.mean = mean(self.data)
        self.median = median(self.data)

    
    def push(self, data:int):
        self.data.pop(0)
        self.data.append(data)
        #print(self.data)
        self.mean = mean(self.data)
        self.median = median(self.data)


class Position:
    def __init__(self, x,y) -> None:
        self.x = x
        self.y = y
    def update(self, x,y):
        print(f"update: {x}, {y}")
        self.x = x
        self.y = y

def distance_from_rssi(rssi, TXower, n=2):
    # from https://davidgyoungtech.com/2020/05/15/how-far-can-you-go
    return(10**((TXower-rssi)/(10*n)))


def update_position():
    pos = list()
    for comb in reciver_combs:
        x1 = reciver_positions[comb[0]].x
        y1 = reciver_positions[comb[0]].y

        x2 = reciver_positions[comb[1]].x
        y2 = reciver_positions[comb[1]].y

        x3 = reciver_positions[comb[2]].x
        y3 = reciver_positions[comb[2]].y

        r1 = distance_from_rssi(measurements[comb[0]].mean, TXower=TX_POWER, n=N)
        r2 = distance_from_rssi(measurements[comb[0]].mean, TXower=TX_POWER, n=N)
        r3 = distance_from_rssi(measurements[comb[0]].mean, TXower=TX_POWER, n=N)
        pos.append(locate_trilateration(x1,y1,r1,x2,y2,r2,x3,y3,r3))
        #print("appended pos")
        print(f"distances: {r1}, {r2}, {r3}")
    
    position.update(mean([i[0] for i in pos]), mean([i[1] for i in pos]))



# from: https://www.101computing.net/cell-phone-trilateration-algorithm/
def locate_trilateration(x1,y1,r1,x2,y2,r2,x3,y3,r3):
  A = 2*x2 - 2*x1
  B = 2*y2 - 2*y1
  C = r1**2 - r2**2 - x1**2 + x2**2 - y1**2 + y2**2
  D = 2*x3 - 2*x2
  E = 2*y3 - 2*y2
  F = r2**2 - r3**2 - x2**2 + x3**2 - y2**2 + y3**2
  x = (C*E - F*B) / (E*A - B*D)
  y = (C*D - A*F) / (B*D - A*E)
  return x,y


###############################
#######     GLOBALS     #######
###############################


W = 20
H = 10

MEASSURMENTS_TO_KEEP = 5

RECIVERS = ["pi01ble", "pible02", "pible03", "pible04"] # list of the reciver hostnames, clockwise starting at the top left
# 1   2
# 3   4
POSITIONS = [Position(0,H), Position(W,H), Position(W,0), Position(0,0)]
TX_POWER = -50 # measured at 1 meeter
N = 3 # should be between 2 and 4, for me 4 got the best results

reciver_combs = tuple(combinations(RECIVERS, 3))
#print(reciver_combs)
measurements = {r:Measurement() for r in RECIVERS}
position = Position(x=W//2, y=H//2) # set initial pos to middle
reciver_positions = {RECIVERS[i]: POSITIONS[i] for i in range(len(RECIVERS))}
last_pos_update = Update()
app = FastAPI()

@app.post("/push_data")
async def insert_data_to_db(data:BLEcapture):
    data = BLEcapture.model_validate(data)
    if data.capture_host:
        measurements[data.capture_host].push(data.rssi)
        print(measurements[data.capture_host].data)
        update_position()
        last_pos_update.update()
        print("update from", data.capture_host)

    with Session(engine) as session:
        session.add(data)
        session.commit()
        #logger.info(f"Added data from {data.capture_host}: {data.device_name if data.device_name else data.device_address} : {data.rssi}")
    return "ok"

@app.get("/")
def root():
    logger.info("Hello")
    return {"ok":True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("capture_server:app", host="0.0.0.0",
)
    