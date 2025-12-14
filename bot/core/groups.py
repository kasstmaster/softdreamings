from discord import app_commands

# Central place to define shared slash-command groups so modules don't create duplicates.
config_group   = app_commands.Group(name="config", description="Server configuration")
messages_group = app_commands.Group(name="messages", description="Message utilities")
schedule_group = app_commands.Group(name="schedule", description="Scheduled features")
movies_group   = app_commands.Group(name="movies", description="Movie night tools")
status_group   = app_commands.Group(name="status", description="Status and diagnostics")

ALL_GROUPS = (config_group, messages_group, schedule_group, movies_group, status_group)
