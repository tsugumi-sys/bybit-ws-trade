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