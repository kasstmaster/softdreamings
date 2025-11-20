import discord
import os
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True

bot = discord.Bot(intents=intents)

# ────────────────────── YOUR CONFIG (emojis preserved) ──────────────────────
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", "1207917070684004452"))
ROLE_TO_WATCH = int(os.getenv("ROLE_TO_WATCH", "1217937235840598026"))
BIRTHDAY_FORM_LINK = os.getenv("BIRTHDAY_FORM_LINK", "https://discord.com/channels/1205041211610501120/1435375785220243598")

WELCOME_TEXT = os.getenv("WELCOME_TEXT", "<:welcome:1435084504950640690> @{mention} just joined the server!")
BOOST_TEXT   = os.getenv("BOOST_TEXT", "<:boost:1435140623714877460> @{mention} just boosted the server!")
VIP_TEXT     = os.getenv("VIP_TEXT", "<a:pepebirthday:1296553298895310971> It's @{mention}'s birthday! @everyone")
BUTTON_LABEL = os.getenv("BUTTON_LABEL", "Add Your Birthday")

# CHANNEL STATUS CONFIG — THESE MUST BE SET IN RAILWAY VARIABLES
STATUS_VC_ID_          = int(os.getenv("STATUS_VC_ID_", "0"))           # ← voice channel ID
STATUS_LOG_CHANNEL_ID = int(os.getenv("STATUS_LOG_CHANNEL_ID", "0"))  # ← text channel for embed
STATUS_MESSAGE_ID     = int(os.getenv("STATUS_MESSAGE_ID", "0"))     # ← leave 0, bot fills it

BUTTON_1_LABEL = os.getenv("BUTTON_1_LABEL", "Showtimes")
BUTTON_1_URL   = os.getenv("BUTTON_1_URL", "https://example.com")
BUTTON_2_LABEL = os.getenv("BUTTON_2_LABEL", "Other Movies/Shows")
BUTTON_2_URL   = os.getenv("BUTTON_2_URL", "https://example.com")

# ────────────────────── /say COMMAND ──────────────────────
@bot.slash_command(name="say", description="Make the bot send a message to any channel")
async def say(ctx, channel: discord.Option(discord.TextChannel), message: str):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.respond("No permission.", ephemeral=True)
    await channel.send(message)
    await ctx.respond(f"Sent to {channel.mention}", ephemeral=True)

# ────────────────────── BASIC EVENTS ──────────────────────
@bot.event
async def status_updater():
    await bot.wait_until_ready()
    print("Status updater loop started!")          # ← YOU WILL SEE THIS IN LOGS

    last_topic = None

    while not bot.is_closed():
        await asyncio.sleep(8)

        # DEBUG LINES — these will show up in Railway logs
        print(f"Checking VC ID: {STATUS_VC_ID_}")
        print(f"Log channel ID: {STATUS_LOG_CHANNEL_ID}")

        if STATUS_VC_ID_ == 0 or STATUS_LOG_CHANNEL_ID == 0:
            print("One of the IDs is 0 → skipping")
            continue

        vc = bot.get_channel(STATUS_VC_ID_)
        log_ch = bot.get_channel(STATUS_LOG_CHANNEL_ID)

        print(f"VC object: {vc}")                     # ← should show the voice channel name
        print(f"Log channel object: {log_ch}")        # ← should show the text channel name

        if not vc or not log_ch:
            print("Could not fetch one of the channels → skipping")
            continue

        current_topic = (vc.topic or "").strip() or "*No status set*"
        print(f"Current topic: '{current_topic}' | Last topic: '{last_topic}'")

        if current_topic == last_topic:
            print("No change → sleeping")
            continue

        # If we get here → topic changed → create/update embed
        print("TOPIC CHANGED → UPDATING EMBED NOW!")
        embed = discord.Embed(title="Channel Status", description=current_topic, color=0x00ffae)
        embed.set_footer(text=f"Updated • {discord.utils.utcnow().strftime('%b %d • %I:%M %p UTC')}")

        view = discord.ui.View(timeout=None)
        view.add_item(discord.ui.Button(label=BUTTON_1_LABEL, url=BUTTON_1_URL, style=discord.ButtonStyle.link))
        view.add_item(discord.ui.Button(label=BUTTON_2_LABEL, url=BUTTON_2_URL, style=discord.ButtonStyle.link))

        try:
            msg = await log_ch.send(embed=embed, view=view)
            print(f"SUCCESS → New message sent! ID: {msg.id}")
        except Exception as e:
            print(f"FAILED TO SEND → {e}")

        last_topic = current_topic

# ────────────────────── START BOT ──────────────────────
bot.run(os.getenv("TOKEN"))
