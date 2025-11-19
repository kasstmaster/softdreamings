import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
# CHANGE ONLY THESE THREE LINES WITH YOUR REAL VALUES
WELCOME_CHANNEL_ID = 1207917070684004452                         # ← your welcome channel ID
ROLE_TO_WATCH = 1217937235840598026                              # ← the role that triggers the button
BIRTHDAY_FORM_LINK = "https://discord.com/channels/1205041211610501120/1435375785220243598"  # ← your birthday link
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready!")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="Welcome to the server!",
            description=f"Hey {member.mention}! We're thrilled to have you here!",
            color=0x00ff88
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

@bot.event
async def on_member_update(before, after):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return

    # Boost detection
    if before.premium_since is None and after.premium_since is not None:
        embed = discord.Embed(
            title="Server Boost!",
            description=f"Big thank you to {after.mention} for boosting the server!",
            color=0xff73fa
        )
        embed.set_thumbnail(url=after.display_avatar.url)
        await channel.send(embed=embed)

    # Role + button detection
    roles_added = set(after.roles) - set(before.roles)
    for role in roles_added:
        if role.id == ROLE_TO_WATCH:
            embed = discord.Embed(
                title="New VIP Alert!",
                description=f"{after.mention} just unlocked **{role.name}**!\nPlease add your birthday below so we can celebrate with you",
                color=role.color or 0x2b2d31
            )
            embed.set_thumbnail(url=after.display_avatar.url)

            view = discord.ui.View(timeout=None)
            button = discord.ui.Button(
                label="Add Your Birthday",
                style=discord.ButtonStyle.secondary,
                url=BIRTHDAY_FORM_LINK,
                emoji="cake"
            )
            view.add_item(button)
            await channel.send(embed=embed, view=view)

bot.run(os.getenv("TOKEN"))
