import hmac
import time
import json
from typing import Tuple, Union, List


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

    def subscribe_topic(self, topics: Union[str, List[str]]) -> str:
        if isinstance(topics, str):
            topics = [topics]

        return json.dumps({"op": "subscribe", "args": topics})

    def unsubscribe_topic(self, topics: Union[str, List[str]]) -> str:
        if isinstance(topics, str):
            topics = [topics]

        return json.dumps({"op": "unsubscribe", "args": topics})

    def _orderbookL2_25(self, symbol: str) -> str:
        return f"orderBookL2_25.{symbol}"

    def _klines(self, symbol: str, interval: Union[str, int]) -> str:
        return f"candle.{interval}.{symbol}"

    def _ticks(self, symbol: str) -> str:
        return f"trade.{symbol}"