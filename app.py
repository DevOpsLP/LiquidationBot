import websocket
import json
import requests

# Telegram Bot details
TELEGRAM_BOT_TOKEN = '6606304009:AAH06LpGvbU73HHZfhOnwh0qJ8Wfj__1lFA'
TELEGRAM_CHANNEL_USERNAME = '@BinancFuturesLiquidations'  # Channel username

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

def on_message(ws, message):
    data = json.loads(message)
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

        formatted_message = f"{emoji} #{symbol} Liquidated {side_text}: ${value/1000:.1f}K at ${price}"
        print(f"Formatted message: {formatted_message}")

        # Send the message to the Telegram channel
        send_telegram_message(formatted_message)
    else:
        print(f"Ignored message with value: ${value:,.1f}")

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("### WebSocket closed ###")
    print(f"Close status code: {close_status_code}, close message: {close_msg}")

def on_open(ws):
    print("### WebSocket opened ###")

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://fstream.binance.com/ws/!forceOrder@arr",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
