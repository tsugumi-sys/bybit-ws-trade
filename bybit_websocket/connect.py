import traceback
from typing import List
import websockets
import asyncio
import os
import json
import logging
import time
from dotenv import load_dotenv

from bybit_ws import BybitWebSocket
from db import crud, models
from db.database import SessionLocal, engine

# Load .env file
load_dotenv()

# Initialize sqlite3 in-memory database
models.Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Set logging.basicConfig
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)


bybit_ws = BybitWebSocket(api_key=os.environ["BYBIT_API_KEY"], api_secret=os.environ["BYBIT_SECRET_KEY"])


async def connect_public_ws(ws_url :str):
    print("public start")
    async with websockets.connect(ws_url) as ws:
        while True:
            try:
                start = time.time()
                # Load board
                await ws.send(bybit_ws._orderbookL2_25())
                res = await ws.recv()
                res = json.loads(res)
                if "type" in list(res.keys()):
                    with SessionLocal() as db:
                        if res["type"] == "snapshot":
                            crud.insert_board_items(db=db, insert_items=res["data"]["order_book"])
                        elif res["type"] == "delta":
                            delete_items: List = res["data"]["delete"]
                            if len(delete_items) > 0:
                                crud.delete_board_items(db=db, delete_items=delete_items)
                            
                            update_items: List = res["data"]["update"]
                            if len(update_items) > 0:
                                crud.update_board_items(db=db, update_items=update_items)
                            
                            insert_items: List = res["data"]["insert"]
                            if len(insert_items) > 0:
                                crud.insert_board_items(db=db, insert_items=insert_items)
                        else:
                            ws.logger.error(res)
                else:
                    ws.logger.error(res)
                
                print(f"Execution time {time.time() - start}s")
                bybit_ws.is_db_refreshed = True
                await asyncio.sleep(3 - (time.time() - start))
            except websockets.exceptions.ConnectionClosed:
                ws.logger.error("Public connection has closed. Try to connect again ...")
                # Delete all items in Board
                with SessionLocal() as db:
                    _ = crud.delete_all_board_items(db=db)

                raise ValueError("Poop")


async def connect_private_ws(ws_url: str):
    async with websockets.connect(ws_url) as ws:
        while True:
            try:
                if bybit_ws.is_db_refreshed:
                    print("Lets Trade!!")

                    start = time.time()
                    with SessionLocal() as db:
                        buy_borad = crud.get_board(db=db, symbol="BTCUSDT", side="Buy")
                        sell_board = crud.get_board(db, symbol="BTCUSDT", side="Sell")
                        best_bid, best_ask = buy_borad[-1], sell_board[0]
                        print(best_bid, best_ask)

                    bybit_ws.is_db_refreshed = False
                    print(f"Trade execution time: {time.time() - start}s")
                
                await asyncio.sleep(0.01)
            except websockets.exceptions.ConnectionClosed:
                ws.logger.error("Private connection has closed. Try to connect again ...")
                raise ValueError("Unko")


async def main():
    await asyncio.gather(
        connect_private_ws(bybit_ws._ws_private_url()),
        connect_public_ws(bybit_ws._ws_public_url()),
    )


if __name__ == "__main__":
    asyncio.run(main())
    