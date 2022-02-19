from typing import List
import websockets
import asyncio
import os
import json
import logging
import time
from dotenv import load_dotenv
import matplotlib.pyplot as plt

from bybit_ws import BybitWebSocket
from db import crud, models
from db.database import SessionLocal, engine
from utils.cusmom_exceptions import ConnectionFailedError

# Load .env file
load_dotenv()

# Set logging.basicConfig
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


bybit_ws = BybitWebSocket(api_key=os.environ["BYBIT_API_KEY"], api_secret=os.environ["BYBIT_SECRET_KEY"])


async def orderbook_ws(ws_url :str, symbol: str):
    async with websockets.connect(ws_url, logger=logger, ping_timeout=1.0) as ws:
        # Subscribe board topic
        board_topic = bybit_ws._orderbookL2_25(symbol)
        subscribe_message = bybit_ws.subscribe_topic(board_topic)
        await asyncio.wait_for(ws.send(subscribe_message), timeout=1.0)

        while True:
            try:
                # Get data
                res = await ws.recv()
                res = json.loads(res)
                if "type" in list(res.keys()):
                    with SessionLocal() as db:
                        # ws.logger.info(res)

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
                            ws.logger.info("Something wrong with responce.")
                            await asyncio.sleep(0.0)
                            raise ConnectionFailedError

                    bybit_ws.is_db_refreshed = True
                    await asyncio.sleep(0.0)

                elif "success" in list(res.keys()):
                    # Subscribe responce is randomly comming from bybit
                    ws.logger.info("success subscribe!!")
                    await asyncio.sleep(0.0)
                    continue
                else:
                    ws.logger.error("responce dont have any key of [`success`, `type`]")
                    print(res)
                    await asyncio.sleep(5)
                    raise ConnectionFailedError
            
            except websockets.exceptions.ConnectionClosed:
                ws.logger.error("Public websocket connection has been closed.")
                await asyncio.sleep(0.0)
                raise ConnectionFailedError

            except asyncio.TimeoutError:
                ws.logger.error("Time out for sending to pubic websocket api.")
                await asyncio.sleep(0.0)
                raise ConnectionFailedError


async def ticks_ws(ws_url :str, symbol: str):
    async with websockets.connect(ws_url, logger=logger, ping_timeout=1.0) as ws:
        # Subscribe board topic
        ticks_topic = bybit_ws._ticks(symbol)
        subscribe_message = bybit_ws.subscribe_topic(ticks_topic)
        await asyncio.wait_for(ws.send(subscribe_message), timeout=1.0)

        while True:
            try:
                # Get data
                res = await ws.recv()
                res = json.loads(res)
                if "data" in list(res.keys()):
                    ticks_data = res["data"]
                    if len(ticks_data) > 0:
                        with SessionLocal() as db:
                            # Check
                            print("Number of ticks:", crud._count_ticks(db=db))
                            print("Number of ohlcv:", crud._count_ohlcv(db=db))
                            print(len(crud.get_ohlcv(db=db)))

                            # Insert tick data
                            crud.insert_tick_items(db=db, insert_items=ticks_data, max_rows=1000)

                            # Create and storeohlcv data
                            crud.create_ohlcv_from_ticks(db, symbol=symbol, max_rows=1000)
                        
                    bybit_ws.is_db_refreshed = True
                    await asyncio.sleep(0.0)

                elif "success" in list(res.keys()):
                    # Subscribe responce
                    ws.logger.info(res)
                    await asyncio.sleep(0.0)
                    continue
                else:
                    ws.logger.error("responce dont have any key of [`success`, `data`]")
                    ws.logger.error(res)
                    await asyncio.sleep(0.0)
                    raise ConnectionFailedError
            
            except websockets.exceptions.ConnectionClosed:
                ws.logger.error("Public websocket connection has been closed.")
                await asyncio.sleep(0.0)
                raise ConnectionFailedError

            except asyncio.TimeoutError:
                ws.logger.error("Time out for sending to pubic websocket api.")
                await asyncio.sleep(0.0)
                raise ConnectionFailedError


async def trading_ws(ws_url: str):
    async with websockets.connect(ws_url, logger=logger, ping_timeout=1.0) as ws:
        while True:
            try:
                if bybit_ws.is_db_refreshed:
                    bybit_ws.is_db_refreshed = False

                    start = time.time()
                    with SessionLocal() as db:
                        buy_borad = crud.get_board(db=db, symbol="BTCUSDT", side="Buy")
                        sell_board = crud.get_board(db, symbol="BTCUSDT", side="Sell")
                        best_bid, best_ask = buy_borad[-1], sell_board[0]
                        
                        ws.logger.info(f"Best Ask (price, size): ({best_ask.price}, {best_ask.size})")
                        ws.logger.info(f"Best Bid (price, size): ({best_bid.price}, {best_bid.size})")


                    ws.logger.info(f"Trade execution time: {time.time() - start}s")
                
                await asyncio.sleep(3)
            except websockets.exceptions.ConnectionClosed:
                ws.logger.error("Private websocket connection has been Closed.")
                await asyncio.sleep(0.0)
                raise ConnectionFailedError


async def run_multiple_websockets():
    symbol = "BTCUSDT"
    await asyncio.gather(
        ticks_ws(ws_url=bybit_ws._ws_public_url(), symbol=symbol),
    )


def main():
    try:
        # Initialize sqlite3 in-memory database
        models.Base.metadata.create_all(engine)
        asyncio.run(run_multiple_websockets())
    except ConnectionFailedError:
        bybit_ws.is_db_refreshed = False
        # Clear in-memory DB
        models.Base.metadata.drop_all(engine)

        # Initialize sqlite3 in-memory DB
        models.Base.metadata.create_all(engine)
        
        logger.info("Reconnect websockets")
        asyncio.run(main())

    # Clear in-memory DB again for next try
    models.Base.metadata.drop_all(engine)
    bybit_ws.is_db_refreshed = False

if __name__ == "__main__":
    while True:
        main()
    