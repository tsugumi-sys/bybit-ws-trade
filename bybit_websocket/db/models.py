from turtle import Turtle
from sqlalchemy import Boolean, Column, ForeignKey, Integer, DateTime, Float, String

from db.database import Base


class Board(Base):
    __tablename__ = "board"

    id = Column(String(10), primary_key=True, index=True)
    price = Column(Float, index=True)
    symbol = Column(String(10), index=True)
    side = Column(String(10), index=True)
    size = Column(Float)

    def __repr__(self) -> str:
        return f"Board(id={self.id}, price={self.price}, symbol={self.symbol}, side={self.side}, size={self.size})"
