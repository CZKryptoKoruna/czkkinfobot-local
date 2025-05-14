import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === BOT CONFIG ===
BOT_TOKEN = ""

# === CZKK CONTRACT ADDRESSES ===
CZKK_CONTRACT_BSC = "0xd5defcb306d93d4cd5dd59e66c8d4dc3b74ef096"
CZKK_CONTRACT_ETH = "0x5dBbD676f70cF9Aac23b25A28e841239fa8d2685"

# === GeckoTerminal API Pool URLs ===
# GeckoTerminal API endpoint format:
# https://api.geckoterminal.com/api/v2/networks/<network>/pools/<pool_address>
BTCB_CZKK_URL = "https://api.geckoterminal.com/api/v2/networks/bsc/pools/0x3458ae2d9409f138a879fca6ff59cb0d397769bb"
USDT_CZKK_URL = "https://api.geckoterminal.com/api/v2/networks/bsc/pools/0x06313b57eac23e0c005a76f81972175c7e8f42ef"
BNB_CZKK_URL  = "https://api.geckoterminal.com/api/v2/networks/bsc/pools/0x862c173c27cbe6a29ec495f4a2cba4fe21da9689"

# === PRICE UTILITIES ===

def get_inverted_price(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Get CZKK per token
        price_czkk = float(data['data']['attributes']['base_token_price_usd']) / float(data['data']['attributes']['quote_token_price_usd'])

        # Invert to get token per CZKK
        inverted_price = 1 / price_czkk if price_czkk != 0 else None
        return inverted_price
    except Exception as e:
        print(f"Error fetching price: {e}")
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
        "/usdt - USDT price in CZKK\n"
        "/bnb - WBNB price in CZKK\n"
        "/czkk - CZKK token contract addresses"
    )

async def btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_inverted_price(BTCB_CZKK_URL)
    formatted = format_price(price)
    await update.message.reply_text(f"₿ BTCB price: {formatted} CZKK")

async def usdt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_inverted_price(USDT_CZKK_URL)
    formatted = format_price(price)
    await update.message.reply_text(f"💵 USDT price: {formatted} CZKK")

async def bnb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_inverted_price(BNB_CZKK_URL)
    formatted = format_price(price)
    await update.message.reply_text(f"⚡ WBNB price: {formatted} CZKK")

async def czkk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🦁 *CZKK Contract Addresses:*\n\n"
        f"*Binance Smart Chain (BSC)*:\n`{CZKK_CONTRACT_BSC}`\n\n"
        f"*Ethereum*:\n`{CZKK_CONTRACT_ETH}`",
        parse_mode="Markdown"
    )


# === MAIN ===

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("btc", btc))
    app.add_handler(CommandHandler("usdt", usdt))
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

