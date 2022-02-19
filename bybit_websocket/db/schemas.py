from pydantic import BaseModel

sides = ["Buy", "Sell"]

# timestamps are unix timestamp (ms).

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
    timestamp: int
    symbol: str
    price: float
    size: float


class TickCreate(TickBase):
    pass


class Tick(TickBase):
    pass
    class Config:
            orm_mode = True


class OHLCVBase(BaseModel):
    timestamp: int
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class OHLCVCreate(OHLCVBase):
    pass
    class Config:
        orm_mode = True


class OHLCV(OHLCVBase):
    pass
    class Config:
        orm_mode = True