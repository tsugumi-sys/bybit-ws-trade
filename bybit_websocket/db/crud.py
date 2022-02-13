from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from . import schemas, models


def get_whole_board(db: Session) -> List[schemas.Board]:
    """[Get all board]

    Args:
        db (Session): [Session of sqlalchemy.]
    """
    return db.query(models.Board).all()


def get_board(db: Session, symbol: str, side: str) -> List[schemas.Board]:
    """[Get current board. return with ascending order of price.]

    Args:
        db (Session): [Session of sqlalchemy.]
        symbol (str): [target symbol.]
        side (str): [target side (Buy or Sell)]

    Raises:
        ValueError: [raise error if `side` is invalid]

    Returns:
        [type]: [description]
    """
    if side not in schemas.sides:
        raise ValueError(f"Invalid side {side}. side should be in {schemas.sides}")

    return db.query(models.Board).filter(and_(models.Board.symbol == symbol, models.Board.side == side)).order_by(models.Board.price).all()


def insert_board_items(db: Session, insert_items: List[Dict]) -> None:
    """[Insert Board items from delta or snapshot responce of bybit websocket.]

    Args:
        db (Session): [Session of sqlalchemy]
        snapshot_items (List[schemas.BoardCreate.dict): [items of snapshot]
    """
    board_items = [models.Board(**item) for item in insert_items]
    db.add_all(board_items)
    db.commit()


def update_board_items(db: Session, update_items: List[Dict]) -> None:
    """[Update Board items from delta format responce of bybit websocket.]

    Args:
        db (Session): [Session of sqlalchemy]
        update_items (List[schemas.Board]): [items to update.]
    """
    for item in update_items:
        update_values = item.copy()
        update_values.pop("id")
        db.query(models.Board).filter(models.Board.id == item["id"]).update(update_values, synchronize_session="fetch")

    db.commit()


def delete_board_items(db: Session, delete_items: List[Dict]) -> None:
    """[Delete Board items from delta format respone of bybit websocket.]

    Args:
        db (Session): [Session of sqlalchemy]
        delete_items (List[schemas.Board]): [items to be deleted.]
    """
    for item in delete_items:
        db.query(models.Board).filter(models.Board.id == item["id"]).delete(synchronize_session="fetch")

    db.commit()


def delete_all_board_items(db: Session) -> int:
    """[delete all board items]

    Args:
        db (Session): [Session of sqlalchemy]

    Returns:
        int: [Deleted items count]
    """
    remove_items_count: int = db.query(models.Board).delete()
    return remove_items_count