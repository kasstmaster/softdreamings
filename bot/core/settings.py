import os

# Required
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
DATABASE_URL  = os.getenv("DATABASE_URL")

# Optional Railway/Postgres TLS toggle
# Set DATABASE_SSL=require on Railway if you run into TLS/handshake issues.
DATABASE_SSL = os.getenv("DATABASE_SSL", "").strip().lower()  # "", "require"

# Optional: dev helpers
_raw = (os.getenv("DEV_GUILD_ID") or "").strip()
DEV_GUILD_IDS = [int(x.strip()) for x in _raw.split(",") if x.strip().isdigit()]

# Default templates/messages (override per-guild in DB where applicable)
MSG = {
    "deadchat_award": "💬 **Dead Chat Revived!** {user_mention} brought the chat back to life!",
    "plague_award": "🦠 **The Plague Spreads...** {user_mention} has been infected!",
    "prize_drop": "🎁 **Prize Drop!** Click the button to claim: **{prize_name}**",
    "prize_claimed_channel": "🏆 {user_mention} claimed **{prize_name}**!",
    "birthday_announce": "🎉 Happy Birthday {user_mention}! 🎂",
    "welcome": "👋 Welcome {user_mention}!",
    "qotd_prefix": "❓ **QOTD:**",
}
