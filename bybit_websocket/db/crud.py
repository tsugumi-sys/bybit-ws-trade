from typing import Dict, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_

from . import schemas, models

# Board methods
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


def get_board_item(db: Session, id: str) -> schemas.Board:
    """get board item (row) by id

    Args:
        db (Session): [Session of sqlalchemy.]
        id (str): [id]

    Returns:
        schemas.Board: Board item.
    """
    return db.query(models.Board).filter(models.Board.id == id).first()


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
        db.query(models.Board).filter(models.Board.id == item["id"]).update(item)

    db.commit()


def delete_board_items(db: Session, delete_items: List[Dict]) -> None:
    """[Delete Board items from delta format respone of bybit websocket.]

    Args:
        db (Session): [Session of sqlalchemy]
        delete_items (List[schemas.Board]): [items to be deleted.]
    """
    for item in delete_items:
        db.query(models.Board).filter(models.Board.id == item["id"]).delete()

    db.commit()


# Tick methods
def get_ticks(db: Session, symbol: str) -> List[schemas.Tick]:
    """get all tick data

    Args:
        db (Session): Session of sqlalchemy

    Returns:
        List[schemas.Tick]: list of ticks.
    """
    return db.query(models.Tick).filter(models.Tick.symbol == symbol).all()


def _count_ticks(db: Session) -> int:
    """Get count of rows in `tick` table

    Args:
        db (Session): Session of sqlalchemy

    Returns:
        int: counts of rows
    """
    return db.query(models.Tick).count()


def get_older_ticks(db: Session, limit: int = 1) -> List[schemas.Tick]:
    """Get older tick data.

    Args:
        db (Session): Session of sqlalchemy
        limit (int, optional): the number of ticks to get. Defaults to 1 (oldest ticks).

    Returns:
        List[schemas.Tick]: list of older ticks
    """
    return db.query(models.Tick).order_by(models.Tick.timestamp).limit(limit).all()


def delete_tick_items(db: Session, delete_items: List[Union[Dict, schemas.Tick]]) -> None:
    """Delete tick items

    Args:
        db (Session): Session of sqlalchemy
        delete_items (List[Dict]): the list of delete items
    """
    for item in delete_items:
        if isinstance(item, schemas.Tick):
            db.query(models.Tick).filter(models.Tick.id == item.id).delete()
        else:
            db.query(models.Tick).filter(models.Tick.id == item["id"]).delete()

    db.commit()


def insert_tick_items(db: Session, insert_items: List[Dict], max_rows: int = 100):
    # Delete older items
    count_ticks = _count_ticks(db)
    if count_ticks + len(insert_items) - 1 > max_rows:
        delete_items_count = count_ticks + len(insert_items) - max_rows
        delete_items = get_older_ticks(db=db, limit=delete_items_count)
        delete_tick_items(db=db, delete_items=delete_items)
    
    # insert new tick data
    tick_items = [models.Tick(id=item["id"], symbol=item["symbol"], price=item["price"], timestamp=item["trade_time_ms"], size=item["size"]) for item in insert_items]
    db.add_all(tick_items)
    db.commit()


# OHLCV methods
def _count_ohlcv(db: Session):
    return db.query(models.OHLCV).count()


def get_ohlcv_with_symbol(db: Session, symbol: Optional[str] = None, limit: Optional[int] = None, ascending: bool = True) -> List[schemas.OHLCV]:
    """get all ohlcv of a symbol

    Args:
        db (Session): Session of sqlalchemy
        symbol (str): Name of symbol
        limit (Optional[int], optional): limit. Defaults to None.
        ascending (bool, optional): ascending order. Defaults to True.

    Returns:
        List[schemas.OHLCV]: list of ohlcv
    """
    if limit is not None and limit < 1:
        raise ValueError(f"`limit` should be more than 1.")

    if ascending:
        if limit is None:
            return db.query(models.OHLCV).filter(models.OHLCV.symbol == symbol).order_by(models.OHLCV.timestamp).all()
        else:
            return db.query(models.OHLCV).filter(models.OHLCV.symbol == symbol).order_by(models.OHLCV.timestamp).limit(limit).all()
    else:
        if limit is None:
            return db.query(models.OHLCV).filter(models.OHLCV.symbol == symbol).order_by(models.OHLCV.timestamp.desc()).all()
        else:
            return db.query(models.OHLCV).filter(models.OHLCV.symbol == symbol).order_by(models.OHLCV.timestamp.desc()).limit(limit).all()


def get_ohlcv(db: Session, limit: Optional[int] = None, ascending: bool = True) -> List[schemas.OHLCV]:
    """get all ohlcv

    Args:
        db (Session): Session of sqlalchemy
        limit (Optional[int], optional): limit. Defaults to None.
        ascending (bool, optional): ascending order. Defaults to True.

    Returns:
        List[schemas.OHLCV]: Session of sqlalchemy
    """
    if limit is not None and limit < 1:
        raise ValueError(f"`limit` should be more than 1.")

    if ascending:
        if limit is None:
            return db.query(models.OHLCV).order_by(models.OHLCV.timestamp).all()
        else:
            return db.query(models.OHLCV).order_by(models.OHLCV.timestamp).limit(limit).all()
    else:
        if limit is None:
            return db.query(models.OHLCV).order_by(models.OHLCV.timestamp.desc()).all()
        else:
            return db.query(models.OHLCV).order_by(models.OHLCV.timestamp.desc()).limit(limit).all()


def insert_ohlcv_items(db: Session, insert_items: List[Union[Dict, schemas.OHLCV]], max_rows: int = 100) -> None:
    """Insert ohlcv items

    Args:
        db (Session): Session of sqlalchemy
        insert_items (List[Union[Dict, schemas.OHLCV]]): List of ohlcv items.
    """
    # Delete older rows
    count_ohlcv = _count_ohlcv(db=db)
    if count_ohlcv + len(insert_items) - 1 > max_rows:
        query_limit = count_ohlcv + len(insert_items) - max_rows
        delete_items = get_ohlcv(db=db, limit=query_limit)
        delete_ohlcv_items(db=db, delete_items=delete_items)

    ohlcv_items = []
    for item in insert_items:
        if isinstance(item, Dict):
            item = models.OHLCV(timestamp=item["timestamp"], symbol=item["symbol"], open=item["open"], high=item["high"], low=item["low"], close=item["close"])
            ohlcv_items.append(item)

    ohlcv_items = insert_items if len(ohlcv_items) == 0 else ohlcv_items

    db.add_all(ohlcv_items)
    db.commit()


def delete_ohlcv_items(db: Session, delete_items: List[Union[Dict, schemas.OHLCV]]) -> None:
    for item in delete_items:
        if isinstance(item, Dict):
            db.query(models.OHLCV).filter(models.OHLCV.timestamp == item["timestamp"]).delete()
        else:
            db.query(models.OHLCV).filter(models.OHLCV.timestamp == item.timestamp).delete()

    db.commit()


