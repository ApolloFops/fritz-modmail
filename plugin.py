from discord.ext import commands

from resources.shared import CONTEXTS, INTEGRATION_TYPES
from scripts.tools import journal

LOG_COMPONENT = "Modmail"

# Test command
@commands.slash_command(name="modmail", description="Say hi to the bot!", contexts=CONTEXTS, integration_types=INTEGRATION_TYPES)
async def modmail(ctx):
	journal.log(f"User {ctx.user} said MODMAIL TIMEEE!", 6, component=LOG_COMPONENT)

	await ctx.respond(f"HIIIII {ctx.author.display_name.upper()}")

def setup(bot):
    bot.add_application_command(modmail)

def teardown(bot):
	journal.log("BYEEEEE!!!", 5, component=LOG_COMPONENT)
