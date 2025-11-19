import discord
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = discord.Bot(intents=intents)

# ────────────────────────── CONFIG ──────────────────────────
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", "1207917070684004452"))
ROLE_TO_WATCH      = int(os.getenv("ROLE_TO_WATCH", "1217937235840598026"))
BIRTHDAY_FORM_LINK = os.getenv("BIRTHDAY_FORM_LINK", "https://discord.com/channels/1205041211610501120/1435375785220243598")

# Customizable text & appearance (change these in Railway → Variables)
WELCOME_TITLE      = os.getenv("WELCOME_TITLE", "Welcome to the server!")
WELCOME_TEXT       = os.getenv("WELCOME_TEXT", "Hey {mention}, we're so happy you're here!")
BOOST_TITLE        = os.getenv("BOOST_TITLE", "NEW BOOST!")
BOOST_TEXT         = os.getenv("BOOST_TEXT", "Huge thank you {mention} for boosting us!")
VIP_TITLE          = os.getenv("VIP_TITLE", "VIP Unlocked!")
VIP_TEXT           = os.getenv("VIP_TEXT", "{mention} just got **{role}**!\nPlease add your birthday below so we can celebrate with you")
BUTTON_LABEL       = os.getenv("BUTTON_LABEL", "Add Your Birthday")
BUTTON_EMOJI       = os.getenv("BUTTON_EMOJI", "cake")
EMBED_COLOR        = int(os.getenv("EMBED_COLOR", "0x8b5cf6").replace("#", "0x"), 16)  # default nice purple
# ───────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready!")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title=WELCOME_TITLE,
                              description=WELCOME_TEXT.replace("{mention}", member.mention),
                              color=EMBED_COLOR)
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

@bot.event
async def on_member_update(before, after):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return

    # Boost detection
    if before.premium_since is None and after.premium_since is not None:
        embed = discord.Embed(title=BOOST_TITLE,
                              description=BOOST_TEXT.replace("{mention}", after.mention),
                              color=EMBED_COLOR)
        embed.set_thumbnail(url=after.display_avatar.url)
        await channel.send(embed=embed)

    # Role + button
    new_roles = set(after.roles) - set(before.roles)
    for role in new_roles:
        if role.id == ROLE_TO_WATCH:
            embed = discord.Embed(title=VIP_TITLE,
                                  description=VIP_TEXT.replace("{mention}", after.mention).replace("{role}", role.name),
                                  color=role.color or EMBED_COLOR)
            embed.set_thumbnail(url=after.display_avatar.url)

            view = discord.ui.View(timeout=None)
            view.add_item(discord.ui.Button(
                label=BUTTON_LABEL,
                style=discord.ButtonStyle.secondary,
                url=BIRTHDAY_FORM_LINK,
                emoji=BUTTON_EMOJI
            ))
            await channel.send(embed=embed, view=view)

bot.run(os.getenv("TOKEN"))
