import discord
from discord.ext import commands
from bot.helpers import tools
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import SlashCommandOptionType
import datetime
import time

class Moderation(commands.Cog, name='moderation'):
    def __init__(self, bot):
        self.bot = bot

    async def get_records_by_server_id(self, server_id):
        return await self.bot.db.fetch('SELECT * FROM moderations WHERE server_id=$1', str(server_id))
    
    async def get_records_by_user_id(self, server_id, user_id):
        return await self.bot.db.fetch('SELECT * FROM moderations WHERE server_id=$1 AND user_id=$2', str(server_id), str(user_id))
    
    async def get_records_by_type(self, server_id, type):
        return await self.bot.db.fetch('SELECT * FROM moderations WHERE server_id=$1 AND type=$2', str(server_id), type)

    async def get_record_by_id(self, server_id, id):
        return await self.bot.db.fetchrow('SELECT * FROM moderations WHERE server_id=$1 AND id=2;', str(server_id), str(id))

    async def add_record(self, server_id, type, user_id, punisher_id, reason, duration=None, active=None):
        return await self.bot.db.fetchrow('INSERT INTO moderations (server_id, type, user_id, punisher_id, reason, duration, active) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *;',
            server_id, type, user_id, punisher_id, reason, duration, active)

    @cog_ext.cog_subcommand(
        base='purge',
        base_desc='Purge messages from the channel.',
        name='all',
        description='Purge all types of messages.',
        options=[
            create_option(
                name='number',
                description='The number of messages to purge.',
                option_type=SlashCommandOptionType.INTEGER,
                required=True
            ),
        ],
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge_all(self, ctx, num):
        await ctx.respond()
        msgs = []
        async for msg in ctx.channel.history(limit=num, before=ctx.message):
            msgs.append(msg)
        await ctx.channel.delete_messages(msgs)
        embed = tools.create_embed(ctx, 'Message Purge (All)', f'{num} messages deleted.')
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base='purge',
        base_desc='Purge messages from the channel.',
        name='bots',
        description='Purge messages sent by bots.',
        options=[
            create_option(
                name='number',
                description='The number of messages to purge.',
                option_type=SlashCommandOptionType.INTEGER,
                required=True
            ),
        ],
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge_bots(self, ctx, num):
        await ctx.respond()
        msgs = []
        async for msg in ctx.channel.history(limit=num):
            if msg.author.bot:
                msgs.append(msg)
        await ctx.channel.delete_messages(msgs)
        embed = tools.create_embed(ctx, 'Message Purge (Bots)', f'{num} messages deleted.')
        await ctx.send(embed=embed)
    
    @cog_ext.cog_subcommand(
        base='purge',
        base_desc='Purge messages from the channel.',
        name='humans',
        description='Purge messages sent by humans.',
        options=[
            create_option(
                name='number',
                description='The number of messages to purge.',
                option_type=SlashCommandOptionType.INTEGER,
                required=True
            ),
        ],
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge_humans(self, ctx, num):
        await ctx.respond()
        msgs = []
        async for msg in ctx.channel.history(limit=num):
            if not msg.author.bot:
                msgs.append(msg)
        await ctx.channel.delete_messages(msgs)
        embed = tools.create_embed(ctx, 'Message Purge (Humans)', f'{num} messages deleted.')
        await ctx.send(embed=embed)
 
    @cog_ext.cog_slash(
        name='warn',
        description="Warn a member of the server.",
        options=[
            create_option(
                name='user',
                description="The member to warn.",
                option_type=SlashCommandOptionType.USER,
                required=True
            ),
            create_option(
                name='reason',
                description='The reason for the member\'s warn (Optional).',
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
        ],
    )
    # @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, user, reason=None):
        await ctx.respond()
        punishment_record = await self.add_record(str(ctx.guild.id), 'warn', str(user.id), str(ctx.author.id), reason)
        embed = tools.create_embed(ctx, 'User Warn', desc=f'{user} has been warned.')
        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Punishment ID', value=punishment_record['id'], inline=False)
        await ctx.send(embed=embed)
    
    @cog_ext.cog_slash(
        name='kick',
        description="Kick a member from the server.",
        options=[
            create_option(
                name='user',
                description="The member to kick.",
                option_type=SlashCommandOptionType.USER,
                required=True
            ),
            create_option(
                name='reason',
                description='The reason for the member\'s kick (Optional).',
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
        ],
    )
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, user, reason=None):
        await ctx.respond()
        await ctx.guild.kick(user, reason=reason)
        punishment_record = await self.add_record(str(ctx.guild.id), 'kick', str(user.id), str(ctx.author.id), reason)
        embed = tools.create_embed(ctx, 'User Kick', desc=f'{user} has been kicked.')
        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Punishment ID', value=punishment_record['id'], inline=False)
        await ctx.send(embed=embed)
        
    @cog_ext.cog_slash(
        name='ban',
        description="Ban a member from the server.",
        options=[
            create_option(
                name='user',
                description="The member to ban.",
                option_type=SlashCommandOptionType.USER,
                required=True
            ),
            create_option(
                name='reason',
                description='The reason for the member\'s ban. (Optional)',
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
        ],
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user, reason=None):
        await ctx.respond()
        await ctx.guild.ban(user, reason=reason)
        punishment_record = await self.add_record(str(ctx.guild.id), 'ban', str(user.id), str(ctx.author.id), reason)
        embed = tools.create_embed(ctx, 'User Ban', desc=f'{user} has been banned.')
        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Punishment ID', value=punishment_record['id'],inline=False)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name='mute',
        description="Mute a user from the server.",
        options=[
            create_option(
                name='user',
                description="The user to mute.",
                option_type=SlashCommandOptionType.USER,
                required=True
            ),
            create_option(
                name='duration',
                description="The duration of the mute. Use 0 for a manual unmute.",
                option_type=SlashCommandOptionType.INTEGER,
                required=True
            ),
            create_option(
                name='duration_unit',
                description="The unit of time for the duration.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
                choices=[
                    create_choice(
                        name='days',
                        value='days'
                    ),
                    create_choice(
                        name='hours',
                        value='hours'
                    ),
                    create_choice(
                        name='minutes',
                        value='minutes'
                    ),
                    create_choice(
                        name='seconds',
                        value='seconds'
                    )
                ]
            ),
            create_option(
                name='reason',
                description='The reason for the member\'s mute. (Optional)',
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
        ],
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, user, duration, duration_unit, reason=None):
        await ctx.respond()
        await user.add_roles(ctx.guild.get_role(809169133232717890))
        duration_adjustments = {
            'days': 1*60*60*24,
            'hours': 1*60*60,
            'minutes': 1*60,
            'seconds': 1
        }
        adjusted_duration = duration * duration_adjustments[duration_unit]
        punishment_record = await self.add_record(str(ctx.guild.id), 'mute', str(user.id), str(ctx.author.id), reason, duration=adjusted_duration, active=True)
        embed = tools.create_embed(ctx, 'User Mute', desc=f'{user} has been muted.')
        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Punishment ID', value=punishment_record['id'],inline=False)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name='unmute',
        description="Unmute a member from the server.",
        options=[
            create_option(
                name='member',
                description="The member to unmute.",
                option_type=SlashCommandOptionType.USER,
                required=True
            ),
        ],
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx, user):
        await ctx.respond()
        await user.remove_roles(ctx.guild.get_role(809169133232717890))
        embed = tools.create_embed(ctx, 'User Unmute', desc=f'{user} has been unmuted.')
        await ctx.send(embed=embed)
    
    @cog_ext.cog_subcommand(
        base='moderations',
        base_desc='Get moderations registered with the bot.',
        subcommand_group='list',
        sub_group_desc='Get a list of moderations registered with the bot.',
        name='all',
        description='Get a list of all moderations in the server.',
        guild_ids=[809169133086048257],
    )
    @commands.has_permissions(manage_messages=True)
    async def moderations_list_server(self, ctx):
        await ctx.respond()
        records = await self.get_records_by_server_id(ctx.guild.id)
        embeds = []
        number_of_pages = -(len(records) // -10)
        for num in range(number_of_pages):
            embeds.append(tools.create_embed(ctx, f'Server Moderations (Page {num + 1}/{number_of_pages})', desc=f'Found {len(records)} records.'))
        for index, record in enumerate(records):
            user = await self.bot.fetch_user(record['user_id'])
            val = f'User: {user.mention} | Type: {record["type"]} | Timestamp: {record["timestamp"].strftime("%b %-d %Y at %-I:%-M %p")}'
            embeds[index//10].add_field(name=record["id"], value=val)
        paginator = tools.EmbedPaginator(self.bot, ctx, embeds)
        await paginator.run()
    
    @cog_ext.cog_subcommand(
        base='moderations',
        base_desc='Get moderations registered with the bot.',
        subcommand_group='list',
        sub_group_desc='Get moderations registered with the bot.',
        name='user',
        description='Get a list of moderations for a user in the server.',
        options=[
            create_option(
                name='user',
                description='The user to get the moderations of.',
                option_type=SlashCommandOptionType.USER,
                required=True
            ),
        ],
        guild_ids=[809169133086048257],
    )
    @commands.has_permissions(manage_messages=True)
    async def moderations_list_user(self, ctx, user):
        await ctx.respond()
        records = await self.get_records_by_user_id(ctx.guild.id, user.id)
        embeds = []
        number_of_pages = -(len(records) // -10)
        for num in range(number_of_pages):
            embeds.append(tools.create_embed(ctx, f'Server Moderations (Page {num + 1}/{number_of_pages})', desc=f'Filtering by user {user.mention}. Found {len(records)} records.'))
        for index, record in enumerate(records):
            user = await self.bot.fetch_user(record['user_id'])
            val = f'User: {user.mention} | Type: {record["type"]} | Timestamp: {record["timestamp"].strftime("%b %-d %Y at %-I:%-M %p")}'
            embeds[index//10].add_field(name=record["id"], value=val, inline=False)
        paginator = tools.EmbedPaginator(self.bot, ctx, embeds)
        await paginator.run()

    @cog_ext.cog_subcommand(
        base='moderations',
        base_desc='Get moderations registered with the bot.',
        subcommand_group='list',
        sub_group_desc='Get a list of moderations registered with the bot.',
        name='type',
        description='Get a list of all moderations in the server.',
        options=[
            create_option(
                name='type',
                description='The type of moderation to search for.',
                option_type=SlashCommandOptionType.STRING,
                required=True,
                choices=[
                    create_choice(
                        name='mute',
                        value='mute',
                    ),
                    create_choice(
                        name='unmute',
                        value='unmute',
                    ),
                    create_choice(
                        name='warn',
                        value='warn',
                    ),
                    create_choice(
                        name='kick',
                        value='kick',
                    ),
                    create_choice(
                        name='ban',
                        value='ban',
                    ),
                    create_choice(
                        name='unban',
                        value='unban',
                    ),
                    create_choice(
                        name='purge',
                        value='purge',
                    ),
                ]
            ),
        ],
        guild_ids=[809169133086048257],
    )
    @commands.has_permissions(manage_messages=True)
    async def moderations_list_type(self, ctx, type):
        await ctx.respond()
        records = await self.get_records_by_type(ctx.guild.id, type)
        embeds = []
        number_of_pages = -(len(records) // -10)
        for num in range(number_of_pages):
            embeds.append(tools.create_embed(ctx, f'Server Moderations (Page {num + 1}/{number_of_pages})', desc=f'Filtering by type {type}. Found {len(records)} records.'))
        for index, record in enumerate(records):
            user = await self.bot.fetch_user(record['user_id'])
            val = f'User: {user.mention} | Type: {record["type"]} | Timestamp: {record["timestamp"].strftime("%b %-d %Y at %-I:%-M %p")}'
            embeds[index//10].add_field(name=record["id"], value=val, inline=False)
        paginator = tools.EmbedPaginator(self.bot, ctx, embeds)
        await paginator.run()

    @cog_ext.cog_subcommand(
        base='moderations',
        base_desc='Get moderations registered with the bot.',
        name='info',
        description='Get a info on a specific moderation.',
        options=[
            create_option(
                name='id',
                description='The unique ID associated with the moderation.',
                option_type=SlashCommandOptionType.STRING,
                required=True
            ),
        ],
        guild_ids=[809169133086048257, 704819543398285383],
    )
    @commands.has_permissions(manage_messages=True)
    async def moderations_info(self, ctx, id):
        await ctx.respond()
        record = await self.get_record_by_id(ctx.guild.id, id)
        if not record:
            embed = tools.create_error_embed(ctx, 'Punishment not found. Please check the ID you gave.')
            await ctx.send(embed=embed)
        else:
            embed = tools.create_embed(ctx, 'Punishment Lookup')
            embed.add_field(name='ID', value=record['id'])
            embed.add_field(name='Type', value=record['type'])
            if record['duration']:
                embed.add_field(name='Duration', value=time.strftime('%Mm %Ss', time.gmtime(round(record['duration']))))
            embed.add_field(name='Offender', value=int(record['user_id']))
            embed.add_field(name='Punisher', value=int(record['punisher_id']))
            embed.add_field(name='Date', value=record['timestamp'].strftime('%b %-d %Y at %-I:%-M %p'))
            if record['reason']:
                embed.add_field(name='Reason', value=record['reason'])
            else:
                embed.add_field(name='Reason', value='None')
            await ctx.send(embed=embed)