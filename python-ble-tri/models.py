from sqlmodel import Field, SQLModel, create_engine
from socket import gethostname
from uuid import uuid4,UUID
from datetime import datetime, UTC



def get_curr_datetime():
    return datetime.now(UTC).astimezone()

class BLEcapture(SQLModel, table=True):
    id: UUID | None = Field(primary_key=True, default_factory=uuid4)
    device_name: str|None
    device_address: str|None
    rssi: int
    tx_power:int|None
    capture_host:str|None = Field(default_factory=gethostname)
    capture_time: datetime|None = Field(default_factory=get_curr_datetime)




sqlite_file_name = "distance_test_5m.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False)

SQLModel.metadata.create_all(engine)