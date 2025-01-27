"""Cog that automatically manages voice channels."""
import discord
from discord.ext import commands
from typing import Optional


class AutoVoice(commands.Cog):

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
        self.channel_id = get_auto_voice_master_id()
        self.channel_list = []

    # clear empty voice channels that were genereted before this session started
    # TODO TEST IF THIS EVEN WORKS!!!
    @commands.Cog.listener()
    async def on_ready(self) -> None:

        # try to get the channel category of the automatic voice channel
        try:
            auto_voice_category = self.bot.get_channel(self.channel_id).category

        except AttributeError:
            return

        # get every voice channel in the auto_voice_category
        for each in auto_voice_category.voice_channels:
            channel = self.bot.get_channel(each)

            is_auto_voice_master = channel.id == self.channel_id

            # if channel doesnt have any members connected
            # and if it isn't the auto voice creator it self, delete it
            if not channel.members and not is_auto_voice_master:
                await each.channel.delete()

    @commands.Cog.listener()
    async def on_voice_state_update(self,
                                    member: discord.Member,
                                    before: discord.VoiceState,
                                    after: discord.VoiceState) -> None:
        # check if a automatic voice channel is set, if not dont do anything
        if self.channel_id is None:
            return

        # check if the voice channel joined is the automatic voice creator
        try:
            joined_auto_voice_master = after.channel.id == self.channel_id

            if joined_auto_voice_master:
                new_channel = await create_new_channel(member, after.channel.category)
                self.channel_list.append(new_channel)

        except AttributeError:
            pass

        try:
            # get the category of automatic voice channels
            auto_voice_category = self.bot.get_channel(self.channel_id).category

            is_automatic_voice_channel = before.channel in auto_voice_category.voice_channels
            is_auto_voice_master = before.channel.id == self.channel_id

            # check if the channel the user left is from the automatic voice category
            # and if it isnt the channel from which the voice channels are created
            can_be_deleted = is_automatic_voice_channel and not is_auto_voice_master

        except AttributeError:
            can_be_deleted = False

        # check if a channel the member left can be deleted
        # and if the channel doesn't have any members connected, delete it
        if can_be_deleted and not before.channel.members:
            await before.channel.delete()

    # set the automatic voice master ID to the one specified by the user
    @commands.slash_command(name="setautovoicechannel")
    @commands.has_permissions(administrator=True)
    async def set_auto_voice(self, ctx: commands.Context, auto_channel_id: str, storage: str) -> None:
        # check if the id should be stored localy
        if storage == "local":
            self.channel_id = int(auto_channel_id)
            await ctx.respond("Automatic voice channel set locally!")
            return

        # TODO implement ID storing to database
        elif storage == "db":
            await ctx.respond("Automatic voice channel set in the database!")
            return

        await ctx.respond("Invalid storage!")

    # handle command errors
    @set_auto_voice.error
    async def admin_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("You do not have the required permissions to run this command.")


def setup(bot: discord.Bot) -> None:
    bot.add_cog(AutoVoice(bot))


async def create_new_channel(
    user: discord.Member,
    category: discord.CategoryChannel,
) -> int:

    discord_server = user.guild

    # create the voice channel name from username or nickname
    new_channel_name = user.name
    if user.nick is not None:
        new_channel_name = user.nick
    new_channel_name += "'s channel"

    # create the new channel
    created_channel = await discord_server.create_voice_channel(name=new_channel_name, category=category)

    # move the user to the newly created channel
    await user.move_to(created_channel)

    # return the created channel
    return created_channel.id

# TODO implement the retrieval of voice master ID from the database
def get_auto_voice_master_id() -> Optional[int]:

    return None
