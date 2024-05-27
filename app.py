import websocket
import json
import requests
import time
import threading

# Telegram Bot details
TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN' # Change your TOKEN here, make sure the bot is added with ADMIN permissions
TELEGRAM_CHANNEL_USERNAME = 'CHANNEL_ID/USERNAME'  # Channel username

# Track WebSocket instances and their states
ws_instances = {}
reconnecting = False

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        "chat_id": TELEGRAM_CHANNEL_USERNAME,
        "text": message,
        "parse_mode": "HTML"
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.request("POST", url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"Message sent: {message}")
        print(response.text)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message: {e}")

def format_value(value):
    if value >= 1000000:
        return f"<b>{value/1000000:,.1f}M</b>"  # Use "M" suffix and bold for millions
    elif value > 100000:
        return f"{value/1000:,.0f}K"  # Use "K" suffix and bold for thousands (no decimal places)
    else:
        return f"{value/1000:,.1f}K"  # Use "K" suffix and bold for thousands (one decimal place)

def on_message(ws, message):
    print(f"Received message: {message}")  # Log the raw message received
    combined_data = json.loads(message)
    
    if 'stream' in combined_data:
        data = combined_data['data']
    else:
        data = combined_data

    order = data['o']
    symbol = order['s']
    side = order['S']
    quantity = float(order['q'])
    price = float(order['ap'])
    value = quantity * price

    # Check if the liquidated amount is greater than $50,000
    if value > 50000:
        if side == "BUY":
            emoji = "🟢"
            side_text = "Short"
        else:
            emoji = "🔴"
            side_text = "Long"

        formatted_value = format_value(value)
        formatted_message = f"{emoji} #{symbol} Liquidated {side_text}: {formatted_value} at <b>${price:,.2f}</b>"
        print(f"Formatted message: {formatted_message}")

        # Send the message to the Telegram channel
        send_telegram_message(formatted_message)
    else:
        print(f"Ignored message with value: ${value:,.1f}")

def on_error(ws, error):
    print(f"WebSocket error: {error}")
    attempt_reconnect(ws.url)

def on_close(ws, close_status_code, close_msg):
    print("### WebSocket closed ###")
    print(f"Close status code: {close_status_code}, close message: {close_msg}")
    attempt_reconnect(ws.url)

def on_open(ws):
    global reconnecting
    print("### WebSocket opened ###")
    reconnecting = False  # Reset the reconnecting flag

def attempt_reconnect(url):
    global reconnecting
    if reconnecting:
        return
    reconnecting = True
    max_retries = 5
    for attempt in range(max_retries):
        try:
            print(f"Attempting to reconnect... (Attempt {attempt + 1}/{max_retries})")
            ws = websocket.WebSocketApp(url,
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close)
            ws.on_open = on_open
            ws_thread = threading.Thread(target=ws.run_forever)
            ws_thread.start()
            reconnecting = False
            break
        except Exception as e:
            print(f"Reconnection attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    else:
        print("Max reconnection attempts reached. Exiting.")
        reconnecting = False

def get_binance_coin_futures_symbols():
    url = "https://dapi.binance.com/dapi/v1/exchangeInfo"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        symbols = [symbol['symbol'] for symbol in data['symbols'] if symbol['symbol'].endswith('_PERP')]
        return symbols
    else:
        print(f"Error: Unable to fetch data (status code: {response.status_code})")
        return []

def run_ws(url):
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.url = url  # Store the URL in the WebSocketApp instance
    ws.on_open = on_open
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.start()
    return ws

if __name__ == "__main__":
    # Get COIN-M market symbols
    symbols = get_binance_coin_futures_symbols()
    print("Symbols ending with _PERP:")
    for symbol in symbols:
        print(symbol)

    # Create combined WebSocket stream for COIN-M market
    base_endpoint_coin_m = "wss://dstream.binance.com/stream?streams="
    stream_names_coin_m = [f"{symbol.lower()}@forceOrder" for symbol in symbols]
    combined_stream_url_coin_m = base_endpoint_coin_m + "/".join(stream_names_coin_m)

    # Create combined WebSocket stream for USDT-M market
    combined_stream_url_usdt_m = "wss://fstream.binance.com/ws/!forceOrder@arr"

    print(f"Combined stream URL (COIN-M): {combined_stream_url_coin_m}")
    print(f"Combined stream URL (USDT-M): {combined_stream_url_usdt_m}")

    # Run both WebSocket connections
    ws_coin_m = run_ws(combined_stream_url_coin_m)
    ws_usdt_m = run_ws(combined_stream_url_usdt_m)

    # Keep the main thread alive
    while True:
        time.sleep(1)
