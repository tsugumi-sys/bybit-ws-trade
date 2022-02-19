.PHONY: run_websocket
run_websocket:
	poetry run python -m websockets ws://localhost:8765/

.PHONY: run_bybit_ws
run_bybit_ws:
	poetry run python ./bybit_websocket/connect.py

.PHONY: visualize
visualize:
	poetry run python ./visualize/candle.py