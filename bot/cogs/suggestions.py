import asyncio
import json

import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option

import bot.cogs.core.settings
from bot.helpers import tools


class Suggestions(
    commands.Cog,
    name="suggestions",
    description="A group of commands related to suggesting improvements for a server.",
):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_subcommand(
        base="suggest",
        base_desc="Create a suggestion.",
        name="server",
        description="Create a server suggestion.",
        options=[
            create_option(
                name="suggestion",
                description="The suggestion you want to make.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
            create_option(
                name="reason",
                description="The reason for your suggestion.",
                option_type=SlashCommandOptionType.STRING,
                required=False,
            ),
            create_option(
                name="notes",
                description="The notes you want to add to the suggestion.",
                option_type=SlashCommandOptionType.STRING,
                required=False,
            ),
            create_option(
                name="image_url",
                description="The URL of the image to attach to the suggestion.",
                option_type=SlashCommandOptionType.STRING,
                required=False,
            ),
        ],
    )
    async def suggest_server(
        self,
        ctx: SlashContext,
        suggestion: str,
        reason: str = None,
        notes: str = None,
        image_url: str = None,
    ) -> None:
        await self.create_suggestion_slash(
            ctx,
            suggestion,
            reason,
            notes,
            image_url,
            "Server Suggestion",
            color=discord.Color.gold(),
        )

    @cog_ext.cog_subcommand(
        base="suggest",
        base_desc="Create a suggestion.",
        name="movie",
        description="Create a movie suggestion.",
        options=[
            create_option(
                name="suggestion",
                description="The suggestion you want to make.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
            create_option(
                name="reason",
                description="The reason for your suggestion.",
                option_type=SlashCommandOptionType.STRING,
                required=False,
            ),
            create_option(
                name="notes",
                description="The notes you want to add to the suggestion.",
                option_type=SlashCommandOptionType.STRING,
                required=False,
            ),
            create_option(
                name="image_url",
                description="The URL of the image to attach to the suggestion.",
                option_type=SlashCommandOptionType.STRING,
                required=False,
            ),
        ],
    )
    async def suggest_movie(
        self,
        ctx: SlashContext,
        suggestion: str,
        reason: str = None,
        notes: str = None,
        image_url: str = None,
    ) -> None:
        await self.create_suggestion_slash(
            ctx,
            suggestion,
            reason,
            notes,
            image_url,
            "Movie Suggestion",
            color=discord.Color.green(),
        )

    @cog_ext.cog_subcommand(
        base="suggest",
        base_desc="Create a suggestion.",
        name="bot",
        description="Create a bot suggestion.",
        options=[
            create_option(
                name="suggestion",
                description="The suggestion you want to make.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
            create_option(
                name="reason",
                description="The reason for your suggestion.",
                option_type=SlashCommandOptionType.STRING,
                required=False,
            ),
            create_option(
                name="notes",
                description="The notes you want to add to the suggestion.",
                option_type=SlashCommandOptionType.STRING,
                required=False,
            ),
            create_option(
                name="image_url",
                description="The URL of the image to attach to the suggestion.",
                option_type=SlashCommandOptionType.STRING,
                required=False,
            ),
        ],
    )
    async def suggest_bot(
        self,
        ctx: SlashContext,
        suggestion: str,
        reason: str = None,
        notes: str = None,
        image_url: str = None,
    ) -> None:
        await self.create_suggestion_slash(
            ctx,
            suggestion,
            reason,
            notes,
            image_url,
            "Bot Suggestion",
            color=discord.Color.purple(),
        )

    @cog_ext.cog_subcommand(
        base="suggest",
        base_desc="Create a suggestion.",
        name="rule",
        description="Create a rule suggestion.",
        options=[
            create_option(
                name="suggestion",
                description="The suggestion you want to make.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
            create_option(
                name="reason",
                description="The reason for your suggestion.",
                option_type=SlashCommandOptionType.STRING,
                required=False,
            ),
            create_option(
                name="notes",
                description="The notes you want to add to the suggestion.",
                option_type=SlashCommandOptionType.STRING,
                required=False,
            ),
            create_option(
                name="image_url",
                description="The URL of the image to attach to the suggestion.",
                option_type=SlashCommandOptionType.STRING,
                required=False,
            ),
        ],
    )
    async def suggest_rule(
        self,
        ctx: SlashContext,
        suggestion: str,
        reason: str = None,
        notes: str = None,
        image_url: str = None,
    ) -> None:
        await self.create_suggestion_slash(
            ctx,
            suggestion,
            reason,
            notes,
            image_url,
            "Rule Suggestion",
            color=discord.Color.blue(),
        )

    async def create_suggestion_slash(
        self,
        ctx: SlashContext,
        suggestion: str,
        reason: str,
        notes: str,
        image_url: str,
        title: str,
        color: discord.Colour,
        downvote: bool = True,
    ) -> None:
        settings_cog = self.bot.get_cog("settings")
        settings = await settings_cog.get_guild_settings(ctx.guild.id)
        suggestions_channel = ctx.guild.get_channel(settings["suggestions"]["channel"])
        embed = tools.create_embed(
            ctx, title, desc=suggestion, footer_enabled=False, color=color
        )
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        if notes:
            embed.add_field(name="Notes", value=notes, inline=False)
        if image_url:
            embed.set_image(url=image_url)
        msg = await suggestions_channel.send(embed=embed)
        await msg.add_reaction(settings["suggestions"]["up_emoji"])
        if downvote:
            await msg.add_reaction(settings["suggestions"]["down_emoji"])

        embed = tools.create_embed(
            ctx,
            title,
            desc="Your suggestion has been submitted successfully!",
            color=color,
        )
        await ctx.send(embed=embed)

    # --------------------------------------------
    # LEGACY COMMANDS
    # --------------------------------------------

    @commands.group(name="suggest")
    @commands.cooldown(1, 900, type=commands.BucketType.user)
    async def suggest_legacy(self, ctx: commands.Context) -> None:
        """Suggest something for the server.
        Suggestions will go into #suggestions.
        The bot will prompt for the reason for the suggestion, then any notes.
        You may specify "none" for either the reason or the notes.
        """
        if ctx.invoked_subcommand is None:
            embed = tools.create_embed(
                ctx,
                "Suggestion",
                desc=f"Please specify a category for your suggestion.\nThe available categories are `server`, `bot`, `movie`, and `rule`.\nThe command's usage is `{ctx.prefix}suggest <category> <suggestion>`",
            )
            await ctx.send(embed=embed)
            ctx.command.reset_cooldown(ctx)

    @suggest_legacy.command(name="server")
    async def suggest_server_legacy(
        self, ctx: commands.Context, *, suggestion: str
    ) -> None:
        await self.create_suggestion(
            ctx, suggestion, "Server Suggestion", color=discord.Color.gold()
        )

    @suggest_legacy.command(name="movie")
    async def suggest_movie_legacy(
        self, ctx: commands.Context, *, suggestion: str
    ) -> None:
        await self.create_suggestion(
            ctx,
            suggestion,
            "Movie Suggestion",
            color=discord.Color.green(),
            downvote=False,
        )

    @suggest_legacy.command(name="bot")
    async def suggest_bot_legacy(
        self, ctx: commands.Context, *, suggestion: str
    ) -> None:
        await self.create_suggestion(
            ctx, suggestion, "Bot Suggestion", color=discord.Color.purple()
        )

    @suggest_legacy.command(name="rule")
    async def suggest_rule_legacy(
        self, ctx: commands.Context, *, suggestion: str
    ) -> None:
        await self.create_suggestion(
            ctx, suggestion, "Rule Suggestion", color=discord.Color.blue()
        )

    async def create_suggestion(
        self,
        ctx: commands.Context,
        suggestion: str,
        title: str,
        color: discord.Color,
        downvote: bool = True,
    ) -> None:
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        embed = tools.create_embed(
            ctx, "Suggestion Reason", "What is the reason for your suggestion?"
        )
        await ctx.send(embed=embed)
        msg = await self.bot.wait_for("message", check=check, timeout=180)
        if msg.content.lower() == "none":
            reason = None
        elif msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Suggestion has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            reason = msg.content

        embed = tools.create_embed(
            ctx,
            "Suggestion Notes",
            'What else you would like to add? Type "none" if you don\'t have anything else.',
        )
        await ctx.send(embed=embed)
        msg = await self.bot.wait_for("message", check=check, timeout=180)
        if msg.content.lower() == "none":
            notes = None
        elif msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Suggestion has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            notes = msg.content

        embed = tools.create_embed(
            ctx,
            "Suggestion Image",
            'Do you have an image to attach to the suggestion? Reply with "none" if you don\'t.',
        )
        await ctx.send(embed=embed)
        msg = await self.bot.wait_for("message", check=check, timeout=180)
        if msg.content.lower() == "none":
            image_url = None
        elif msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Suggestion has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            image_url = msg.attachments[0].url

        settings_cog = self.bot.get_cog("settings")
        settings = await settings_cog.get_guild_settings(ctx.guild.id)
        suggestions_channel = ctx.guild.get_channel(settings["suggestions"]["channel"])
        embed = tools.create_embed(
            ctx, title, desc=suggestion, footer_enabled=False, color=color
        )
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        if notes:
            embed.add_field(name="Notes", value=notes, inline=False)
        if image_url:
            embed.set_image(url=image_url)
        msg = await suggestions_channel.send(embed=embed)
        await msg.add_reaction(settings["suggestions"]["up_emoji"])
        if downvote:
            await msg.add_reaction(settings["suggestions"]["down_emoji"])

        embed = tools.create_embed(
            ctx,
            title,
            desc="Your suggestion has been submitted successfully!",
            color=color,
        )
        await ctx.send(embed=embed)

    # @commands.command()
    # @commands.has_permissions(manage_messages=True)
    # async def removesuggestion(self, ctx, id: int):
    #     """This command allows for anyone with the "Manage Messages"
    #     permission to remove a suggestion."""
    #     suggestions_channel = self.bot.get_channel(818901195023843368)
    #     msg = await suggestions_channel.fetch_message(id)
    #     await msg.delete()
    #     desc = f"Suggestion with ID {id} has been removed."
    #     embed = tools.create_embed(ctx, "Suggestion Removal", desc=desc)
    #     await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Suggestions(bot))
