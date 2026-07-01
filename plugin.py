import discord
from discord.channel import TextChannel
from discord.ext import commands
from discord.commands import SlashCommandGroup

from resources.shared import CONTEXTS, INTEGRATION_TYPES
from scripts.tools import journal

from .config import LOG_COMPONENT
from .database import ModmailDatabase

database = ModmailDatabase()


class ModmailButtonView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@discord.ui.button(label="Create thread", custom_id="create-thread", style=discord.ButtonStyle.primary, emoji="📬")
	async def create_thread(self, button, interaction):
		modal = ModmailCreateModal()
		await interaction.response.send_modal(modal)


class ModmailCreateModal(discord.ui.DesignerModal):
	def __init__(self):
		super().__init__(title="Create thread")

		subject_input = discord.ui.Label(label="Subject")
		subject_input.set_input_text(custom_id="subject")
		super().add_item(subject_input)

	async def callback(self, interaction: discord.Interaction):
		if interaction.guild is None:
			await interaction.response.send_message("Failed to create modmail thread: Couldn't find guild", ephemeral=True)
			return

		channel_id = database.get_channel(interaction.guild.id)
		if channel_id is None:
			await interaction.response.send_message("No modmail channel set for this server", ephemeral=True)
			return

		channel = interaction.guild.get_channel(channel_id)

		# If channel isn't already cached, fetch it from Discord
		if channel is None:
			journal.log(f"Couldn't find channel {channel_id} in cache, fetching from Discord", 7, component=LOG_COMPONENT)
			channel = await interaction.guild.fetch_channel(channel_id)

		await interaction.response.send_message("Creating private modmail thread!", ephemeral=True)

		subject = self.children[0].get_item("subject").value

		thread = await channel.create_thread(name=subject)
		await thread.add_user(interaction.user)


class Modmail(commands.Cog):
	command_group = SlashCommandGroup("modmail", "Modmail functions", contexts=CONTEXTS, integration_types=INTEGRATION_TYPES)

	def __init__(self, bot: discord.Bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		self.bot.add_view(ModmailButtonView())

	@command_group.command(name="button", description="Create a modmail button", contexts=CONTEXTS, integration_types=INTEGRATION_TYPES)
	async def create_button(self, ctx):
		await ctx.send("Press this button to create a modmail thread", view=ModmailButtonView())

		await ctx.respond("Modmail button created!", ephemeral=True)

	@command_group.command(name="set_channel", description="Set what channel modmail threads should be created in for this server", contexts=CONTEXTS, integration_types=INTEGRATION_TYPES)
	async def set_channel(self, ctx, channel: TextChannel):
		database.set_channel(ctx.guild_id, channel.id)

		await ctx.respond(f"Set the modmail channel to {channel.jump_url}")

	@command_group.command(name="remove_channel", description="Removes the modmail channel for this server. This disables modmail.", contexts=CONTEXTS, integration_types=INTEGRATION_TYPES)
	async def remove_channel(self, ctx):
		database.remove_channel(ctx.guild_id)

		await ctx.respond("Modmail removed")


def setup(bot):
	bot.add_cog(Modmail(bot))


def teardown(bot):
	bot.remove_cog("Modmail")
