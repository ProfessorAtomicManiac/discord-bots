import asyncio
import datetime
import time

import discord
from discord.ext import commands
from discord_components import Button, ButtonStyle, InteractionType
from discord_slash import SlashContext, cog_ext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option

from bot.helpers import tools


class Embeds(commands.Cog, name="embeds"):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="sendembed",
        description="Send an embed message from the bot. This launches the embeditorificatorinator.",
        options=[
            create_option(
                name="channel",
                description="The channel the embed is in.",
                option_type=SlashCommandOptionType.CHANNEL,
                required=True,
            ),
        ],
    )
    async def sendembed(self, ctx: SlashContext, channel: discord.TextChannel) -> None:
        embedcreator = EmbedCreator(self.bot, ctx, channel.id)
        await embedcreator.run()

    @cog_ext.cog_slash(
        name="editembed",
        description="Edit an embed message sent by the bot. This launches the embeditorificatorinator.",
        options=[
            create_option(
                name="channel",
                description="The channel the embed is in.",
                option_type=SlashCommandOptionType.CHANNEL,
                required=True,
            ),
            create_option(
                name="message_id",
                description="The ID of the message that contains the embed.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
        ],
    )
    async def editembed(
        self, ctx: SlashContext, channel: discord.TextChannel, message_id: str
    ) -> None:
        embedcreator = EmbedCreator(self.bot, ctx, channel.id, int(message_id))
        await embedcreator.run()


def setup(bot: commands.Bot):
    bot.add_cog(Embeds(bot))


class EmbedCreator:
    def __init__(
        self,
        bot: commands.Bot,
        ctx: SlashContext,
        channel_id: int,
        message_id: int = None,
    ):
        self.bot = bot
        self.ctx = ctx
        self.channel_id = channel_id
        self.message_id = message_id

    REACTIONS_CONVERTER = {
        "👁": "view",
        "📜": "title",
        "📄": "description",
        "📑": "footer",
        "🟩": "color",
        "🌠": "image",
        "📎": "thumbnail",
        "👤": "author",
        "🖊️": "add_field",
        "✅": "finish",
    }

    REACTIONS_CONVERTER_VIEW = {
        "⤴️": "menu",
        "✅": "finish",
    }

    def create_menu(self) -> discord.Embed:
        desc = [
            "View Embed - 👁",
            "Title - 📜",
            "Description - 📄",
            "Footer - 📑",
            "Color - 🟩",
            "Image - 🌠",
            "Thumbnail - 📎",
            "Author - 👤",
            "Add Field - 🖊️",
            "Fields - 1️⃣-9️⃣",
            "",
            "Finish Setup - ✅",
        ]
        return discord.Embed(
            title="Embeditorificatorinator | Menu", description="\n".join(desc)
        )

    async def run(self) -> None:
        if self.message_id:
            channel = self.ctx.guild.get_channel(self.channel_id)
            message = await channel.fetch_message(self.message_id)
            self.embed_viewer = message.embeds[0]
        else:
            self.embed_viewer = discord.Embed()

        self.embed_creator = self.create_menu()
        self.bot_message = await self.ctx.send(embed=self.embed_creator)

        def rcheck(reaction: discord.Reaction, user: discord.User) -> bool:
            return (
                user.id == self.ctx.author_id
                and reaction.message.id == self.bot_message.id
            )

        def tcheck(message: discord.Message) -> bool:
            return (
                message.author.id == self.ctx.author_id
                and message.channel == self.ctx.channel
            )

        running = True
        self.setup_status = "menu"

        self.field_count = 0
        for reaction in self.REACTIONS_CONVERTER.keys():
            await self.bot_message.add_reaction(reaction)
        while running:
            self.embed_creator = self.create_menu()
            await self.bot_message.edit(embed=self.embed_creator)

            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", check=rcheck, timeout=45
                )
            except asyncio.TimeoutError:
                return

            self.setup_status = self.REACTIONS_CONVERTER.get(reaction.emoji)
            if self.setup_status == "view":
                await self.bot_message.clear_reactions()
                await self.bot_message.edit(embed=self.embed_viewer)
                for reaction in self.REACTIONS_CONVERTER_VIEW.keys():
                    await self.bot_message.add_reaction(reaction)
                try:
                    reaction, user = await self.bot.wait_for(
                        "reaction_add", check=rcheck, timeout=45
                    )
                except asyncio.TimeoutError:
                    return
                self.setup_status = self.REACTIONS_CONVERTER_VIEW.get(reaction.emoji)
                if self.setup_status == "menu":
                    await self.bot_message.edit(embed=self.embed_creator)
                    await self.bot_message.clear_reactions()
                    for reaction in self.REACTIONS_CONVERTER.keys():
                        await self.bot_message.add_reaction(reaction)
            if self.setup_status == "title":
                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator | Title",
                    description="Send the title you want for the embed.",
                )
                await self.bot_message.edit(embed=self.embed_creator)
                try:
                    msg = await self.bot.wait_for("message", check=tcheck, timeout=300)
                except asyncio.TimeoutError:
                    return
                self.embed_viewer.title = (
                    msg.content
                    if msg.content.lower() != "none"
                    else discord.Embed.Empty
                )
                await msg.delete()
            elif self.setup_status == "description":
                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator | Description",
                    description="Send the description you want for the embed.",
                )
                await self.bot_message.edit(embed=self.embed_creator)
                try:
                    msg = await self.bot.wait_for("message", check=tcheck, timeout=300)
                except asyncio.TimeoutError:
                    return
                self.embed_viewer.description = (
                    msg.content
                    if msg.content.lower() != "none"
                    else discord.Embed.Empty
                )
                await msg.delete()
            elif self.setup_status == "footer":
                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator | Footer",
                    description="Send the footer you want for the embed.",
                )
                await self.bot_message.edit(embed=self.embed_creator)
                try:
                    msg = await self.bot.wait_for("message", check=tcheck, timeout=300)
                except asyncio.TimeoutError:
                    return
                self.embed_viewer.set_footer(
                    text=msg.content
                    if msg.content.lower() != "none"
                    else discord.Embed.Empty
                )
                await msg.delete()
            elif self.setup_status == "color":
                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator | Color",
                    description='Send the color you want for the embed. This must be in hexadecimal, preceded by a "#".\nExample: #FFFFFF',
                )
                await self.bot_message.edit(embed=self.embed_creator)
                try:
                    msg = await self.bot.wait_for("message", check=tcheck, timeout=300)
                except asyncio.TimeoutError:
                    return

                if msg.content.lower() == "none":
                    self.embed_viewer.color = discord.Embed.Empty
                else:
                    r, g, b = [
                        int(msg.content.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)
                    ]
                    self.embed_viewer.color = discord.Color.from_rgb(r, g, b)
                await msg.delete()
            elif self.setup_status == "image":
                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator | Image",
                    description="Send the image you want for the embed.\nThis can be either a URL or an image upload.",
                )
                await self.bot_message.edit(embed=self.embed_creator)
                try:
                    msg = await self.bot.wait_for("message", check=tcheck, timeout=300)
                except asyncio.TimeoutError:
                    return
                if msg.content.startswith("http"):
                    image_url = (
                        msg.content
                        if msg.content.lower() != "none"
                        else discord.Embed.Empty
                    )
                else:
                    image_url = msg.attachments[0].proxy_url
                self.embed_viewer.set_image(url=image_url)
                await msg.delete()
            elif self.setup_status == "thumbnail":
                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator | Thumbnail",
                    description="Send the thumbnail you want for the embed.\nThis can be either a URL or an image upload.",
                )
                await self.bot_message.edit(embed=self.embed_creator)
                try:
                    msg = await self.bot.wait_for("message", check=tcheck, timeout=300)
                except asyncio.TimeoutError:
                    return
                if msg.content.startswith("http"):
                    thumbnail_url = (
                        msg.content
                        if msg.content.lower() != "none"
                        else discord.Embed.Empty
                    )
                else:
                    thumbnail_url = msg.attachments[0].proxy_url
                self.embed_viewer.set_thumbnail(url=thumbnail_url)
                await msg.delete()
            elif self.setup_status == "author":
                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator | Author",
                    description="Send the author you want for the embed.",
                )
                await self.bot_message.edit(embed=self.embed_creator)
                try:
                    msg = await self.bot.wait_for("message", check=tcheck, timeout=300)
                except asyncio.TimeoutError:
                    return
                author = (
                    msg.content
                    if msg.content.lower() != "none"
                    else discord.Embed.Empty
                )
                await msg.delete()

                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator | Author Image URL",
                    description="Send the author image URL you want for the embed.",
                )
                await self.bot_message.edit(embed=self.embed_creator)
                try:
                    msg = await self.bot.wait_for("message", check=tcheck, timeout=300)
                except asyncio.TimeoutError:
                    return
                if msg.content.startswith("http"):
                    author_icon_url = msg.content
                if msg.content.lower() == "none":
                    author_icon_url = discord.Embed.Empty
                else:
                    author_icon_url = msg.attachments[0].proxy_url
                self.embed_viewer.set_author(name=author, icon_url=author_icon_url)
                await msg.delete()
            elif self.setup_status == "finish":
                channel = self.ctx.guild.get_channel(self.channel_id)
                if self.message_id:
                    message = await channel.fetch_message(self.message_id)
                    await message.edit(embed=self.embed_viewer)
                else:
                    await channel.send(embed=self.embed_viewer)
                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator",
                    description="Embed has been created and sent succesfully!",
                )
                await self.bot_message.edit(embed=self.embed_creator)
                await self.bot_message.clear_reactions()
                running = False
            self.setup_status = "menu"


class ButtonEmbedCreator:
    def __init__(
        self,
        bot: commands.Bot,
        ctx: SlashContext,
        channel_id: int,
        message_id: int = None,
    ):
        self.bot = bot
        self.ctx = ctx
        self.channel_id = channel_id
        self.message_id = message_id

    def create_menu(self) -> discord.Embed:
        return discord.Embed(
            title="Embeditorificatorinator | Menu",
            description="Please select an option below.",
        )

    def create_buttons(self, disabled: bool = False) -> list[list[Button]]:
        return [
            [
                Button(
                    label="View Embed",
                    style=ButtonStyle.blue,
                    id="viewembed",
                    disabled=disabled,
                ),
                Button(
                    label="Title",
                    style=ButtonStyle.gray,
                    id="title",
                    disabled=disabled,
                ),
                Button(
                    label="Description",
                    style=ButtonStyle.gray,
                    id="description",
                    disabled=disabled,
                ),
                Button(
                    label="Footer",
                    style=ButtonStyle.gray,
                    id="footer",
                    disabled=disabled,
                ),
                Button(
                    label="Color",
                    style=ButtonStyle.gray,
                    id="color",
                    disabled=disabled,
                ),
            ],
            [
                Button(
                    label="Image",
                    style=ButtonStyle.gray,
                    id="image",
                    disabled=disabled,
                ),
                Button(
                    label="Thumbnail",
                    style=ButtonStyle.gray,
                    id="thumbnail",
                    disabled=disabled,
                ),
                Button(
                    label="Author",
                    style=ButtonStyle.gray,
                    id="author",
                    disabled=disabled,
                ),
                Button(
                    label="Add Field",
                    style=ButtonStyle.gray,
                    id="addfield",
                    disabled=disabled,
                ),
            ],
            [
                Button(
                    label="Field 1",
                    style=ButtonStyle.gray,
                    id="field1",
                    disabled=True if self.field_count >= 1 else False,
                ),
                Button(
                    label="Field 2",
                    style=ButtonStyle.gray,
                    id="field2",
                    disabled=True if self.field_count >= 2 else False,
                ),
                Button(
                    label="Field 3",
                    style=ButtonStyle.gray,
                    id="field3",
                    disabled=True if self.field_count >= 3 else False,
                ),
                Button(
                    label="Field 4",
                    style=ButtonStyle.gray,
                    id="field4",
                    disabled=True if self.field_count >= 4 else False,
                ),
                Button(
                    label="Field 5",
                    style=ButtonStyle.gray,
                    id="field5",
                    disabled=True if self.field_count >= 5 else False,
                ),
            ],
            [
                Button(
                    label="Field 6",
                    style=ButtonStyle.gray,
                    id="field6",
                    disabled=True if self.field_count >= 6 else False,
                ),
                Button(
                    label="Field 7",
                    style=ButtonStyle.gray,
                    id="field7",
                    disabled=True if self.field_count >= 7 else False,
                ),
                Button(
                    label="Field 8",
                    style=ButtonStyle.gray,
                    id="field8",
                    disabled=True if self.field_count >= 8 else False,
                ),
                Button(
                    label="Field 9",
                    style=ButtonStyle.gray,
                    id="field9",
                    disabled=True if self.field_count >= 9 else False,
                ),
                Button(
                    label="Field 10",
                    style=ButtonStyle.gray,
                    id="field10",
                    disabled=True if self.field_count >= 10 else False,
                ),
            ],
        ]

    async def run(self) -> None:
        if self.message_id:
            channel = self.ctx.guild.get_channel(self.channel_id)
            message = await channel.fetch_message(self.message_id)
            self.embed_viewer = message.embeds[0]
        else:
            self.embed_viewer = discord.Embed()

        self.embed_creator = self.create_menu()
        self.bot_message = await self.ctx.send(embed=self.embed_creator)

        def rcheck(reaction: discord.Reaction, user: discord.User) -> bool:
            return (
                user.id == self.ctx.author_id
                and reaction.message.id == self.bot_message.id
            )

        self.setup_status = "menu"

        while True:
            self.embed_creator = self.create_menu()
            await self.bot_message.edit(embed=self.embed_creator)

            # try:
            #     interaction = await self.bot.wait_for(
            #         "button_click", check=lambda i:  , timeout=45
            #     )
            # except asyncio.TimeoutError:
            #     return

            self.setup_status = self.REACTIONS_CONVERTER.get(reaction.emoji)
            if self.setup_status == "view":
                await self.bot_message.clear_reactions()
                await self.bot_message.edit(embed=self.embed_viewer)
                for reaction in self.REACTIONS_CONVERTER_VIEW.keys():
                    await self.bot_message.add_reaction(reaction)
                try:
                    reaction, user = await self.bot.wait_for(
                        "reaction_add", check=rcheck, timeout=45
                    )
                except asyncio.TimeoutError:
                    return
                self.setup_status = self.REACTIONS_CONVERTER_VIEW.get(reaction.emoji)
                if self.setup_status == "menu":
                    await self.bot_message.edit(embed=self.embed_creator)
                    await self.bot_message.clear_reactions()
                    for reaction in self.REACTIONS_CONVERTER.keys():
                        await self.bot_message.add_reaction(reaction)
            if self.setup_status == "title":
                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator | Title",
                    description="Send the title you want for the embed.",
                )
                await self.bot_message.edit(embed=self.embed_creator)
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author.id == self.ctx.author_id
                        and m.channel == self.ctx.channel,
                        timeout=300,
                    )
                except asyncio.TimeoutError:
                    return
                self.embed_viewer.title = (
                    msg.content
                    if msg.content.lower() != "none"
                    else discord.Embed.Empty
                )
                await msg.delete()
            elif self.setup_status == "description":
                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator | Description",
                    description="Send the description you want for the embed.",
                )
                await self.bot_message.edit(embed=self.embed_creator)
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author.id == self.ctx.author_id
                        and m.channel == self.ctx.channel,
                        timeout=300,
                    )
                except asyncio.TimeoutError:
                    return
                self.embed_viewer.description = (
                    msg.content
                    if msg.content.lower() != "none"
                    else discord.Embed.Empty
                )
                await msg.delete()
            elif self.setup_status == "footer":
                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator | Footer",
                    description="Send the footer you want for the embed.",
                )
                await self.bot_message.edit(embed=self.embed_creator)
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author.id == self.ctx.author_id
                        and m.channel == self.ctx.channel,
                        timeout=300,
                    )
                except asyncio.TimeoutError:
                    return
                self.embed_viewer.set_footer(
                    text=msg.content
                    if msg.content.lower() != "none"
                    else discord.Embed.Empty
                )
                await msg.delete()
            elif self.setup_status == "color":
                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator | Color",
                    description='Send the color you want for the embed. This must be in hexadecimal, preceded by a "#".\nExample: #FFFFFF',
                )
                await self.bot_message.edit(embed=self.embed_creator)
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author.id == self.ctx.author_id
                        and m.channel == self.ctx.channel,
                        timeout=300,
                    )
                except asyncio.TimeoutError:
                    return

                if msg.content.lower() == "none":
                    self.embed_viewer.color = discord.Embed.Empty
                else:
                    r, g, b = [
                        int(msg.content.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)
                    ]
                    self.embed_viewer.color = discord.Color.from_rgb(r, g, b)
                await msg.delete()
            elif self.setup_status == "image":
                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator | Image",
                    description="Send the image you want for the embed.\nThis can be either a URL or an image upload.",
                )
                await self.bot_message.edit(embed=self.embed_creator)
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author.id == self.ctx.author_id
                        and m.channel == self.ctx.channel,
                        timeout=300,
                    )
                except asyncio.TimeoutError:
                    return
                if msg.content.startswith("http"):
                    image_url = (
                        msg.content
                        if msg.content.lower() != "none"
                        else discord.Embed.Empty
                    )
                else:
                    image_url = msg.attachments[0].proxy_url
                self.embed_viewer.set_image(url=image_url)
                await msg.delete()
            elif self.setup_status == "thumbnail":
                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator | Thumbnail",
                    description="Send the thumbnail you want for the embed.\nThis can be either a URL or an image upload.",
                )
                await self.bot_message.edit(embed=self.embed_creator)
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author.id == self.ctx.author_id
                        and m.channel == self.ctx.channel,
                        timeout=300,
                    )
                except asyncio.TimeoutError:
                    return
                if msg.content.startswith("http"):
                    thumbnail_url = (
                        msg.content
                        if msg.content.lower() != "none"
                        else discord.Embed.Empty
                    )
                else:
                    thumbnail_url = msg.attachments[0].proxy_url
                self.embed_viewer.set_thumbnail(url=thumbnail_url)
                await msg.delete()
            elif self.setup_status == "author":
                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator | Author",
                    description="Send the author you want for the embed.",
                )
                await self.bot_message.edit(embed=self.embed_creator)
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author.id == self.ctx.author_id
                        and m.channel == self.ctx.channel,
                        timeout=300,
                    )
                except asyncio.TimeoutError:
                    return
                author = (
                    msg.content
                    if msg.content.lower() != "none"
                    else discord.Embed.Empty
                )
                await msg.delete()

                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator | Author Image URL",
                    description="Send the author image URL you want for the embed.",
                )
                await self.bot_message.edit(embed=self.embed_creator)
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author.id == self.ctx.author_id
                        and m.channel == self.ctx.channel,
                        timeout=300,
                    )
                except asyncio.TimeoutError:
                    return
                if msg.content.startswith("http"):
                    author_icon_url = msg.content
                if msg.content.lower() == "none":
                    author_icon_url = discord.Embed.Empty
                else:
                    author_icon_url = msg.attachments[0].proxy_url
                self.embed_viewer.set_author(name=author, icon_url=author_icon_url)
                await msg.delete()
            elif self.setup_status == "finish":
                channel = self.ctx.guild.get_channel(self.channel_id)
                if self.message_id:
                    message = await channel.fetch_message(self.message_id)
                    await message.edit(embed=self.embed_viewer)
                else:
                    await channel.send(embed=self.embed_viewer)
                self.embed_creator = discord.Embed(
                    title="Embeditorificatorinator",
                    description="Embed has been created and sent succesfully!",
                )
                await self.bot_message.edit(embed=self.embed_creator)
                await self.bot_message.clear_reactions()
                running = False
            self.setup_status = "menu"
