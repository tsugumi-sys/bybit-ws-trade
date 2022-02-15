from pydantic import BaseModel

sides = ["Buy", "Sell"]


class BoardBase(BaseModel):
    id: str
    price: str
    symbol: str
    side: str
    size: float


class BoardCreate(BoardBase):
    pass

class Board(BoardBase):
    pass
    class Config:
        orm_mode = True


class TickBase(BaseModel):
    id: str
    symbol: str
    price: float
    timestamp: str
    size: float


class TickCreate(TickBase):
    pass


class Tick(TickBase):
    pass


class OHLCVBase(BaseModel):
    timestamp: str
    symbol: str
    open: float
    high: float
    low: float
    close: float


class OHLCVCreate(OHLCVBase):
    pass


class OHLCV(OHLCVBase):
    pass