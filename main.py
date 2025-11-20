async def status_updater():
    await bot.wait_until_ready()
    print("Channel Status updater STARTED — new message on every new status")
    last_status = None   # only tracks what was actually sent

    while not bot.is_closed():
        await asyncio.sleep(10)

        if STATUS_VC_ID_ == 0 or STATUS_LOG_CHANNEL_ID == 0:
            continue

        vc = bot.get_channel(STATUS_VC_ID_)
        log_ch = bot.get_channel(STATUS_LOG_CHANNEL_ID)
        if not vc or not log_ch or not isinstance(vc, discord.VoiceChannel):
            continue

        raw_status = str(vc.status or "").strip()
        
        # ←←← YOUR EXACT RULES ←←←
        if not raw_status:                    # status is empty → do NOTHING
            if last_status is not None:       # (optional: clear tracking when emptied)
                print("Status cleared → staying silent")
                last_status = None
            continue

        if raw_status == last_status:         # same status as before → stay silent
            continue

        # ←←← New non-empty status → send a fresh message ←←←
        embed = discord.Embed(color=0x00ffae)
        embed.title = raw_status
        embed.description = "Playing all day. Feel free to coordinate with others in chat if you want to plan a group watch later in the day."
        embed.set_footer(text=f"Updated • {discord.utils.utcnow().strftime('%b %d • %I:%M %p UTC')}")

        view = discord.ui.View(timeout=None)
        view.add_item(discord.ui.Button(label=BUTTON_1_LABEL, url=BUTTON_1_URL, style=discord.ButtonStyle.link))
        view.add_item(discord.ui.Button(label=BUTTON_2_LABEL, url=BUTTON_2_URL, style=discord.ButtonStyle.link))

        await log_ch.send(embed=embed, view=view)
        print(f"New status → '{raw_status}' → fresh message sent")

        last_status = raw_status   # remember this one was already announced
