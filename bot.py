import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === BOT CONFIG ===
BOT_TOKEN = "YOUR_BOT_TOKEN"

# === CZKK CONTRACT ADDRESSES ===
CZKK_CONTRACT_BSC = "0xd5defcb306d93d4cd5dd59e66c8d4dc3b74ef096"
CZKK_CONTRACT_ETH = "0x5dBbD676f70cF9Aac23b25A28e841239fa8d2685"
CZKK_CONTRACT_ARB = "0x1c8053E1cFc0a494814c4B0b619D68b48d88c1Ec"

# === GeckoTerminal API Pool URLs ===
BTCB_CZKK_URL = "https://api.geckoterminal.com/api/v2/networks/bsc/pools/0x3458ae2d9409f138a879fca6ff59cb0d397769bb"
USD_CZKK_URL  = "https://api.geckoterminal.com/api/v2/networks/bsc/pools/0x48b5fc41889fc5a739b2a4fa9dc1f06d60c63a3c"
BNB_CZKK_URL  = "https://api.geckoterminal.com/api/v2/networks/bsc/pools/0x862c173c27cbe6a29ec495f4a2cba4fe21da9689"

# === PRICE UTILITIES ===

def get_inverted_price(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        base_usd = float(data['data']['attributes']['base_token_price_usd'])
        quote_usd = float(data['data']['attributes']['quote_token_price_usd'])

        price_czkk = base_usd / quote_usd
        inverted_price = 1 / price_czkk if price_czkk != 0 else None
        return inverted_price
    except Exception as e:
        print(f"Error fetching inverted price: {e}")
        return None

def get_direct_price(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # We assume this pool is already showing CZKK per USD
        price = float(data['data']['attributes']['base_token_price_usd']) / float(data['data']['attributes']['quote_token_price_usd'])
        return price
    except Exception as e:
        print(f"Error fetching direct price: {e}")
        return None

def format_price(price):
    if price is None:
        return "N/A"
    if price >= 1_000_000:
        return f"{price / 1_000_000:.2f}M"
    elif price >= 1_000:
        return f"{price:,.0f}"
    else:
        return f"{price:.4f}"

# === COMMAND HANDLERS ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💱 Welcome to the CZKK info Bot\n\n"
        "Use the following commands:\n"
        "/btc - BTCB price in CZKK\n"
        "/usd - USD price in CZKK\n"
        "/bnb - WBNB price in CZKK\n"
        "/czkk - CZKK token contract addresses"
    )

async def btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_inverted_price(BTCB_CZKK_URL)
    formatted = format_price(price)
    await update.message.reply_text(f"₿ BTCB price: {formatted} CZKK")

async def usd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_direct_price(USD_CZKK_URL)
    formatted = format_price(price)
    await update.message.reply_text(f"💵 USD price: {formatted} CZKK")

async def bnb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_inverted_price(BNB_CZKK_URL)
    formatted = format_price(price)
    await update.message.reply_text(f"⚡ WBNB price: {formatted} CZKK")

async def czkk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🦁 *CZKK Contract Addresses:*\n\n"
        f"*Binance Smart Chain (BSC)*:\n`{CZKK_CONTRACT_BSC}`\n\n"
        f"*Ethereum*:\n`{CZKK_CONTRACT_ETH}`\n\n"
        f"*Arbitrum*:\n`{CZKK_CONTRACT_ARB}`",
        parse_mode="Markdown"
    )

# === MAIN ===

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("btc", btc))
    app.add_handler(CommandHandler("usd", usd))
    app.add_handler(CommandHandler("bnb", bnb))
    app.add_handler(CommandHandler("czkk", czkk))

    print("✅ CZKK Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if str(e).startswith("Cannot close a running event loop"):
            import nest_asyncio
            nest_asyncio.apply()
            asyncio.get_event_loop().run_until_complete(main())
        else:
            raise

