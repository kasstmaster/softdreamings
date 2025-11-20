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

# Channel Status feature
STATUS_VC_ID           = int(os.getenv("STATUS_VC_ID", "0"))
STATUS_LOG_CHANNEL_ID  = int(os.getenv("STATUS_LOG_CHANNEL_ID", "0"))
STATUS_MESSAGE_ID      = int(os.getenv("STATUS_MESSAGE_ID", "0"))  # auto-filled

BUTTON_1_LABEL = os.getenv("BUTTON_1_LABEL", "Showtimes")
BUTTON_1_URL   = os.getenv("BUTTON_1_URL", "https://example.com")
BUTTON_2_LABEL = os.getenv("BUTTON_2_LABEL", "Other Movies/Shows")
BUTTON_2_URL   = os.getenv("BUTTON_2_URL", "https://example.com")

# ────────────────────── COMMANDS & EVENTS ──────────────────────
@bot.slash_command(name="say", description="Make the bot send a message to any channel")
async def say(ctx,
              channel: discord.Option(discord.TextChannel, "Channel to send to", required=True),
              message: discord.Option(str, "Message to send", required=True)):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("You need Administrator to use this.", ephemeral=True)
        return
    await channel.send(message)
    await ctx.respond(f"Sent to {channel.mention}", ephemeral=True)

@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready!")
    bot.loop.create_task(channel_status_loop())   # ← start the loop

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        msg = WELCOME_TEXT.replace("{mention}", member.mention)
        view = discord.ui.View(timeout=None)
        view.add_item(discord.ui.Button(label=BUTTON_LABEL, style=discord.ButtonStyle.secondary, url=BIRTHDAY_FORM_LINK))
        await channel.send(msg, view=view)

@bot.event
async def on_member_update(before, after):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return
    if before.premium_since is None and after.premium_since is not None:
        await channel.send(BOOST_TEXT.replace("{mention}", after.mention))
    new_roles = set(after.roles) - set(before.roles)
    for role in new_roles:
        if role.id == ROLE_TO_WATCH:
            await channel.send(VIP_TEXT.replace("{mention}", after.mention))

# ────────────────────── CHANNEL STATUS LOOP (actually works!) ──────────────────────
async def channel_status_loop():
    await bot.wait_until_ready()
    last_topic = None

    while not bot.is_closed():
        if STATUS_VC_ID == 0 or STATUS_LOG_CHANNEL_ID == 0:
            await asyncio.sleep(15)
            continue

        vc = bot.get_channel(STATUS_VC_ID)
        log_channel = bot.get_channel(STATUS_LOG_CHANNEL_ID)
        if not vc or not log_channel:
            await asyncio.sleep(15)
            continue

        current_topic = (vc.topic or "").strip() or "*No status set yet*"

        if current_topic == last_topic:
            await asyncio.sleep(15)
            continue

        # Topic changed → update embed
        embed = discord.Embed(
            title="Channel Status",
            description=current_topic,
            color=0x00ffae
        )
        embed.set_footer(text=f"Last updated • {discord.utils.utcnow().strftime('%b %d, %Y • %I:%M %p UTC')}")

        view = discord.ui.View(timeout=None)
        view.add_item(discord.ui.Button(label=BUTTON_1_LABEL, url=BUTTON_1_URL, style=discord.ButtonStyle.link))
        view.add_item(discord.ui.Button(label=BUTTON_2_LABEL, url=BUTTON_2_URL, style=discord.ButtonStyle.link))

        global STATUS_MESSAGE_ID
        try:
            if STATUS_MESSAGE_ID == 0:
                msg = await log_channel.send(embed=embed, view=view)
                STATUS_MESSAGE_ID = msg.id
                print(f"Channel Status message created: {msg.id}")
            else:
                msg = await log_channel.fetch_message(STATUS_MESSAGE_ID)
                await msg.edit(embed=embed, view=view)
        except:
            msg = await log_channel.send(embed=embed, view=view)
            STATUS_MESSAGE_ID = msg.id

        last_topic = current_topic
        await asyncio.sleep(15)  # checks every 15 seconds

# ────────────────────── START BOT ──────────────────────
bot.run(os.getenv("TOKEN"))
