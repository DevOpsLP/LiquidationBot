# Binance Futures Liquidation Bot

This bot connects to the Binance WebSocket API to listen for liquidation orders on all markets. When a liquidation order with a value greater than $50,000 is detected, the bot formats the message and sends it to a specified Telegram channel.

## Features

- Connects to the Binance WebSocket API to listen for all market liquidation orders.
- Filters and processes liquidation orders with a value greater than $50,000.
- Formats and sends liquidation notifications to a specified Telegram channel.

## Message Format

The liquidation messages are formatted as follows:

- For liquidated longs:

    - 🔴 #BTCUSDT Liquidated Long: $77.7K at $69177.53

- For liquidated shorts:
    - 🟢 #SOLUSDT Liquidated Short: $157K at $174.48


## Setup

### Prerequisites

- Python 3.x
- A Telegram bot token
- A Telegram channel where the bot has admin rights

### Installation

1. Clone the repository:
 ```bash
 git clone https://github.com/devopslp/liquidationbot.git
 cd binance-liquidation-bot
 ```

2. Install the dependencies:
 ```pip install -r requirements.txt```

3. Create a configuration file or set your environment variables with the following details:
 TELEGRAM_BOT_TOKEN: Your Telegram bot token
 TELEGRAM_CHANNEL_USERNAME: Your Telegram channel username (e.g., @BinancFuturesLiquidations)
 Make sure your bot is added as ADMIN to the channel

4. Run the bot script:
 ```python bot.py```

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss any changes.

## License

This project is licensed under the MIT License.


