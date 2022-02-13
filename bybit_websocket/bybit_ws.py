import hmac
import json
import time
from typing import Tuple
import websockets
import asyncio


class BybitWebSocket:
    def __init__(self, api_key: str, api_secret: str) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.is_db_refreshed = False
    
    def __signature(self) -> Tuple:
        expires = int((time.time() + 5000) * 1000)
        signature = str(hmac.new(
            bytes(self.api_secret, "utf-8"),
            bytes(f"GET/realtime{expires}", "utf-8"), digestmod="sha256"
        ).hexdigest())

        return signature, expires

    def _ws_public_url(self):
        ws_url = "wss://stream.bybit.com/realtime_public"
        signature, expires = self.__signature()
        param = f"api_key={self.api_key}&expires={expires}&signature={signature}"
        return ws_url + "?" + param

    def _ws_private_url(self):
        ws_url = "wss://stream.bybit.com/realtime_private"
        signature, expires = self.__signature()
        param = f"api_key={self.api_key}&expires={expires}&signature={signature}"
        return ws_url + "?" + param

    # Send method
    def _ping(self) -> str:
        return '{"op": "ping"}'

    def _orderbookL2_25(self) -> str:
        return '{"op": "subscribe", "args": ["orderBookL2_25.BTCUSDT"]}'