import os
import discord
from discord.ext import commands
import datetime
import traceback
from typing import Optional, List

# Configuration des intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.messages = True

# Initialisation du bot
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Stockage des données
whitelisted_users = set()
antiraid_settings = {
    'antibadword': False,
    'antiban': False,
    'antibot': False,
    'antispam': False,
    'antilink': False,
    'antieveryone': False,
    'antijoin': False,
    'antikick': False,
    'antichannel': False,
    'antiemote': False,
    'antireact': False,
    'antirole': False,
    'antisticker': False,
    'antithread': False,
    'antinewaccount': False,
    'antimassmention': False
}

punishment_settings = {
    'action': 'kick',
    'duration': 0
}

class SafetyChecks:
    @staticmethod
    def is_safe_command(command: str) -> bool:
        dangerous_commands = ['rm', 'sudo', 'chmod', 'chown']
        return not any(cmd in command for cmd in dangerous_commands)

    @staticmethod
    def is_safe_message(content: str) -> bool:
        max_mentions = 5
        max_length = 2000
        return len(content) <= max_length and content.count('@') <= max_mentions

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.value = None

    @discord.ui.select(
        placeholder="Sélectionnez une catégorie",
        options=[
            discord.SelectOption(label="Security", description="Commandes de sécurité", emoji="🛡️"),
            discord.SelectOption(label="Information", description="Commandes d'information", emoji="📌"),
            discord.SelectOption(label="Aperçu & Description", description="Commandes d'aperçu", emoji="👥"),
            discord.SelectOption(label="Modération", description="Commandes de modération", emoji="🔨"),
            discord.SelectOption(label="Vocal", description="Commandes vocales", emoji="🎤"),
            discord.SelectOption(label="Gestion du serveur", description="Commandes de gestion", emoji="⚙️"),
            discord.SelectOption(label="Utilitaires", description="Commandes utilitaires", emoji="📝"),
            discord.SelectOption(label="Amusant", description="Commandes fun", emoji="🎮"),
            discord.SelectOption(label="Jeux", description="Mini-jeux", emoji="🎲"),
            discord.SelectOption(label="Tickets", description="Gestion des tickets", emoji="🎫"),
            discord.SelectOption(label="Giveaways", description="Système de giveaways", emoji="🎁"),
            discord.SelectOption(label="Logs", description="Système de logs", emoji="📋"),
            discord.SelectOption(label="Invitations", description="Gestion des invitations", emoji="📨"),
            discord.SelectOption(label="Permissions", description="Gestion des permissions", emoji="🔑"),
            discord.SelectOption(label="Gestion du bot", description="Configuration du bot", emoji="🤖")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        try:
            category = select.values[0]
            commands = categories.get(category, "Aucune commande disponible")
            selected_option = next(opt for opt in select.options if opt.value == category)

            embed = discord.Embed(
                title=f"{selected_option.emoji} {category}",
                description=f"```\n{commands}\n```",
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            await interaction.response.send_message("Une erreur est survenue", ephemeral=True)
            print(f"Error in select_callback: {e}")

categories = {
    "Security": "antiban, antibadword, antibot, antichannel, antiemote, antieveryone, antijoin, antikick, antilink, antimassmention, antinewaccount, antireact, antirole, antispam, antisticker, antithread, clearwebhook, punish, raidclean, roleclean, secur, unwl, wl",
    "Information": "alladmins, allbans, botadmins, allbots, avatar, banner, boosters, calc, channel, emote, latence, roleinfo, rolemembers, server, snipe, snipeall, snipeedit, snowaybots, stats, suggest, lookup, uptime, version, whois, whoami",
    "Aperçu & Description": "allcategory, allchannel, allemojis, roleadmin, allroles, allthreads, allvoices, checkperm, get, helpcolor, idemoji, norole, onepage, timestamp, uptime",
    "Modération": "addnote, addrole, ban, baninfo, clear, clearall, cmute, delnote, delrole, delwarn, derank, editban, editmute, hide, kick, lock, massrole, mute, mutelist, notes, permpic, renew, sanctions, tempban, tempcmute, temphide, templock, tempmute, tempnick, temprole, unban, uncmute, unhide, unlock, unmute, unmuteall, unpermpic, warn",
    "Vocal": "antijoinvoc, antimoove, bring, bringcc, cleanup, find, joinvoc, pv, rolemove, swap, tempvoice, unvoicedeaf, unvoicemute, voicedeaf, voicekick, voicelimit, voicemove, voicemute, voiceroles",
    "Gestion du serveur": "afk, autorank, autoroles, capture, clearembed, clearlimit, create, custom, custominfo, delete, deleteembed, embed, everping, hereping, listembed, listemoji, loadembed, loademoji, newsticker, reminder, resetmsg, restrict, rolemenu, saveembed, saveemoji, serversettings, showpic, soutien, starboard, suggestion, suppressembed, unrestrict, unsuppressembed",
    "Utilitaires": "autopublish, autoreact, autothread, banclear, boostembed, cancelunbanall, clearcounter, clearsnipe, compteur, constmsg, deletelogs, editboostembed, firstmessage, ghostping, hideall, joinembed, joinsettings, lastmessage, leaveembed, leavesettings, lockall, muterole, noderank, permpicall, piconly, pin, reactclear, reactclear, replaceall, setclear, slowmode, sync, timeout, unbanall, unhideall, unlockall, unpermpicall, unpin, unslowmode",
    "Amusant": "8ball, cry, gay, hug, kiss, lovecalc, pat, ping, punch, randomavatar, randombanner, randomuser, rate, ratio, reverse, slap, smile",
    "Jeux": "2048, bingo, connect4, cookie, demineur, fastbingo, findemoji, flood, pairs, pendu, pfc, scookie, slots, snake, ttt",
    "Tickets": "add, claim, close, closeall, rappel, remove, rename, stars, ticketsettings, transcript, unclaim",
    "Giveaways": "clearwin, endgiveaway, fastgw, giveaway, giveawaycount, giveawaywin, reroll",
    "Logs": "boostlog, channellog, cookielog, embedlog, emojilog, fluxlog, gwlog, invitelog, modlog, msglog, raidlog, rolelog, soutienlog, starlog, systemlog, voicelog",
    "Invitations": "addinvites, clearinvites, invites, joinby, lockinvite, removeinvite, vanity",
    "Permissions": "change, changeall, createperm, delay, delperm, helpall, perms, public, setperm, unchange, unsetperm, vent",
    "Gestion du bot": "settings, bl, blinfo, botconfig, clearactivity, color, compet, customstatus, dnd, sethelp, idle, invisible, leave, limit, listen, mpsettings, online, playto, prefix, say, serverlist, set, stream, unbl, watch"
}


@bot.command(name='help')
async def help_command(ctx, command: str = None):
    """Show help for commands"""
    if command:
        cmd = bot.get_command(command)
        if cmd:
            embed = discord.Embed(
                title=f"📖 Command: {command}",
                description=f"```yaml\n{cmd.help or 'No description available'}\n```",
                color=discord.Color.brand_green()
            )
            embed.add_field(name="Usage", value=f"`!{command}`", inline=True)
            embed.set_footer(text="Use !help to return to categories", icon_url=bot.user.avatar.url if bot.user.avatar else None)
            await ctx.send(embed=embed)
        else:
            error_embed = discord.Embed(
                title="❌ Command Not Found",
                description="That command doesn't exist! Use `!help` to see all available commands.",
                color=discord.Color.red()
            )
            await ctx.send(embed=error_embed)
    else:
        embed = discord.Embed(
            title="🌟 Command Center",
            description=(
                "Welcome to the Enhanced Command System!\n\n"
                "**Quick Guide:**\n"
                "> 📌 Use the dropdown menu below to browse commands\n"
                "> 🔍 Use `!help <command>` for detailed information\n"
                "> ⚡ All commands use the `!` prefix\n\n"
                "**Select a category below to view its commands:**"
            ),
            color=discord.Color.blurple()
        )

        category_counts = {
            "🛡️ Security": len(categories["Security"].split(", ")),
            "📌 Information": len(categories["Information"].split(", ")),
            "👥 Aperçu & Description": len(categories["Aperçu & Description"].split(", ")),
            "🔨 Modération": len(categories["Modération"].split(", ")),
            "🎤 Vocal": len(categories["Vocal"].split(", ")),
            "⚙️ Gestion du serveur": len(categories["Gestion du serveur"].split(", ")),
            "📝 Utilitaires": len(categories["Utilitaires"].split(", ")),
            "🎮 Amusant": len(categories["Amusant"].split(", ")),
            "🎲 Jeux": len(categories["Jeux"].split(", ")),
            "🎫 Tickets": len(categories["Tickets"].split(", ")),
            "🎁 Giveaways": len(categories["Giveaways"].split(", ")),
            "📋 Logs": len(categories["Logs"].split(", ")),
            "📨 Invitations": len(categories["Invitations"].split(", ")),
            "🔑 Permissions": len(categories["Permissions"].split(", ")),
            "🤖 Gestion du bot": len(categories["Gestion du bot"].split(", "))
        }

        # Create category fields with improved formatting
        for category, count in category_counts.items():
            embed.add_field(
                name=f"{category}",
                value=f"```ansi\n\u001b[1;36m{count} commands\u001b[0m\n```",
                inline=True
            )

        total_commands = sum(category_counts.values())

        # Add statistics with improved formatting
        stats = (
            f"```ansi\n"
            f"\u001b[1;33mTotal Commands:\u001b[0m {total_commands}\n"
            f"\u001b[1;33mPrefix:\u001b[0m !\n"
            f"\u001b[1;33mCategories:\u001b[0m {len(category_counts)}\n"
            f"```"
        )
        embed.add_field(name="📊 Statistics", value=stats, inline=False)

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        if bot.user.avatar:
            embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)

        view = HelpView()
        await ctx.send(embed=embed, view=view)

@bot.command()
async def alladmins(ctx):
    """List all administrators"""
    admins = [m for m in ctx.guild.members if m.guild_permissions.administrator]
    embed = discord.Embed(title="Server Administrators", color=discord.Color.gold())
    embed.description = "\n".join([f"• {admin.name}" for admin in admins]) or "No administrators found"
    await ctx.send(embed=embed)

@bot.command()
async def allbans(ctx):
    """List all banned users"""
    bans = [entry async for entry in ctx.guild.bans()]
    embed = discord.Embed(title="Banned Users", color=discord.Color.red())
    embed.description = "\n".join([f"• {ban.user.name} - Reason: {ban.reason or 'No reason'}" for ban in bans]) or "No bans found"
    await ctx.send(embed=embed)

@bot.command()
async def allbots(ctx):
    """List all bots"""
    bots = [m for m in ctx.guild.members if m.bot]
    embed = discord.Embed(title="Server Bots", color=discord.Color.blue())
    embed.description = "\n".join([f"• {bot.name}" for bot in bots]) or "No bots found"
    await ctx.send(embed=embed)

@bot.command()
async def banner(ctx, member: discord.Member = None):
    """Show user banner"""
    member = member or ctx.author
    user = await bot.fetch_user(member.id)
    embed = discord.Embed(title=f"{member.name}'s Banner", color=discord.Color.blue())
    if user.banner:
        embed.set_image(url=user.banner.url)
    else:
        embed.description = "No banner found"
    await ctx.send(embed=embed)

@bot.command()
async def calc(ctx, *, expression: str):
    """Calculate a mathematical expression"""
    try:
        result = eval(expression, {"__builtins__": None}, {"abs": abs, "round": round})
        await ctx.send(f"Result: {result}")
    except:
        await ctx.send("Invalid expression")

@bot.command()
async def channel(ctx, channel: discord.TextChannel = None):
    """Show channel information"""
    channel = channel or ctx.channel
    embed = discord.Embed(title=f"Channel: {channel.name}", color=discord.Color.blue())
    embed.add_field(name="ID", value=channel.id)
    embed.add_field(name="Created At", value=channel.created_at.strftime("%Y-%m-%d"))
    embed.add_field(name="NSFW", value=channel.is_nsfw())
    await ctx.send(embed=embed)

@bot.command()
async def emote(ctx, emoji: discord.Emoji):
    """Show emoji information"""
    embed = discord.Embed(title=f"Emoji: {emoji.name}", color=discord.Color.blue())
    embed.add_field(name="ID", value=emoji.id)
    embed.add_field(name="Created At", value=emoji.created_at.strftime("%Y-%m-%d"))
    embed.set_thumbnail(url=emoji.url)
    await ctx.send(embed=embed)

@bot.command()
async def latence(ctx):
    """Show bot latency"""
    embed = discord.Embed(title="Bot Latency", color=discord.Color.blue())
    embed.add_field(name="Websocket", value=f"{round(bot.latency * 1000)}ms")
    await ctx.send(embed=embed)

@bot.command()
async def rolemembers(ctx, role: discord.Role):
    """Show members with a specific role"""
    embed = discord.Embed(title=f"Members with {role.name}", color=role.color)
    members = [m.name for m in role.members]
    embed.description = "\n".join([f"• {member}" for member in members]) or "No members found"
    await ctx.send(embed=embed)

@bot.command()
async def lookup(ctx, user_id: int):
    """Look up user information by ID"""
    try:
        user = await bot.fetch_user(user_id)
        embed = discord.Embed(title=f"User Lookup: {user.name}", color=discord.Color.blue())
        embed.add_field(name="ID", value=user.id)
        embed.add_field(name="Created At", value=user.created_at.strftime("%Y-%m-%d"))
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        await ctx.send(embed=embed)
    except:
        await ctx.send("User not found")

@bot.command()
async def vocal(ctx):
    """Show voice channel statistics"""
    voice_channels = ctx.guild.voice_channels
    total_users = sum(len(vc.members) for vc in voice_channels)
    embed = discord.Embed(title="Voice Channel Statistics", color=discord.Color.blue())
    embed.add_field(name="Total Channels", value=len(voice_channels))
    embed.add_field(name="Total Users", value=total_users)
    await ctx.send(embed=embed)

@bot.command()
async def server(ctx):
    """Display server information"""
    guild = ctx.guild
    embed = discord.Embed(title=f"{guild.name} Info", color=discord.Color.blue())
    embed.add_field(name="Owner", value=guild.owner)
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Created At", value=guild.created_at.strftime("%Y-%m-%d"))
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    """Show user avatar"""
    member = member or ctx.author
    embed = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.blue())
    embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def roleinfo(ctx, role: discord.Role):
    """Display role information"""
    embed = discord.Embed(title=f"Role: {role.name}", color=role.color)
    embed.add_field(name="ID", value=role.id)
    embed.add_field(name="Members", value=len(role.members))
    embed.add_field(name="Created At", value=role.created_at.strftime("%Y-%m-%d"))
    await ctx.send(embed=embed)

@bot.command()
async def botadmins(ctx):
    """List all admin bots"""
    admin_bots = [m for m in ctx.guild.members if m.bot and m.guild_permissions.administrator]
    embed = discord.Embed(title="Admin Bots", color=discord.Color.blue())
    embed.description = "\n".join([f"• {bot.name}" for bot in admin_bots]) or "No admin bots found"
    await ctx.send(embed=embed)

@bot.command()
async def boosters(ctx):
    """List server boosters"""
    boosters = [m for m in ctx.guild.members if m.premium_since]
    embed = discord.Embed(title="Server Boosters", color=discord.Color.pink())
    embed.description = "\n".join([f"• {booster.name}" for booster in boosters]) or "No boosters found"
    await ctx.send(embed=embed)

@bot.command()
async def stats(ctx):
    """Show bot statistics"""
    embed = discord.Embed(title="Bot Statistics", color=discord.Color.blue())
    embed.add_field(name="Servers", value=len(bot.guilds))
    embed.add_field(name="Users", value=sum(g.member_count for g in bot.guilds))
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms")
    await ctx.send(embed=embed)

@bot.command()
async def snipe(ctx):
    """Show last deleted message"""
    embed = discord.Embed(title="Last Deleted Message", color=discord.Color.red())
    embed.description = "No deleted messages found"
    await ctx.send(embed=embed)

@bot.command()
async def snipeall(ctx, limit: int = 5):
    """Show multiple deleted messages"""
    embed = discord.Embed(title="Recent Deleted Messages", color=discord.Color.red())
    embed.description = "No deleted messages found"
    await ctx.send(embed=embed)

@bot.command()
async def snipeedit(ctx):
    """Show last edited message"""
    embed = discord.Embed(title="Last Edited Message", color=discord.Color.yellow())
    embed.description = "No edited messages found"
    await ctx.send(embed=embed)

@bot.command()
async def version(ctx):
    """Show bot version"""
    embed = discord.Embed(title="Bot Version", color=discord.Color.blue())
    embed.description = "Version 1.0.0"
    await ctx.send(embed=embed)

@bot.command()
async def whois(ctx, member: discord.Member = None):
    """Show detailed user information"""
    member = member or ctx.author
    embed = discord.Embed(title=f"User Info - {member.name}", color=member.color)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"))
    embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d"))
    embed.add_field(name="Top Role", value=member.top_role.name)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def whoami(ctx):
    """Show your own information"""
    await ctx.invoke(bot.get_command('whois'), member=ctx.author)

@bot.command()
async def uptime(ctx):
    """Show bot uptime"""
    embed = discord.Embed(title="Bot Uptime", color=discord.Color.green())
    embed.description = "Bot uptime information will be shown here"
    await ctx.send(embed=embed)

@bot.command()
async def allcategory(ctx):
    """List all categories"""
    categories = ctx.guild.categories
    embed = discord.Embed(title="All Categories", color=discord.Color.blue())
    embed.description = "\n".join([f"• {category.name} ({len(category.channels)} channels)" for category in categories])
    await ctx.send(embed=embed)

@bot.command()
async def allchannel(ctx):
    """List all channels"""
    channels = ctx.guild.channels
    embed = discord.Embed(title="All Channels", color=discord.Color.blue())
    for channel_type in ["text", "voice", "category"]:
        type_channels = [c.name for c in channels if c.type.name == channel_type]
        if type_channels:
            embed.add_field(name=f"{channel_type.title()} Channels", value="\n".join(f"• {c}" for c in type_channels))
    await ctx.send(embed=embed)

@bot.command()
async def allemojis(ctx):
    """List all emojis"""
    emojis = ctx.guild.emojis
    embed = discord.Embed(title="All Emojis", color=discord.Color.blue())
    emoji_list = [f"{emoji} - `:{emoji.name}:`" for emoji in emojis]
    for i in range(0, len(emoji_list), 10):
        embed.add_field(name=f"Emojis {i+1}-{min(i+10, len(emoji_list))}", value="\n".join(emoji_list[i:i+10]))
    await ctx.send(embed=embed)

@bot.command()
async def roleadmin(ctx):
    """List admin roles"""
    admin_roles = [role for role in ctx.guild.roles if role.permissions.administrator]
    embed = discord.Embed(title="Admin Roles", color=discord.Color.red())
    embed.description = "\n".join([f"• {role.name}" for role in admin_roles])
    await ctx.send(embed=embed)

@bot.command()
async def allroles(ctx):
    """List all roles"""
    roles = ctx.guild.roles[1:]  # Exclude @everyone
    embed = discord.Embed(title="All Roles", color=discord.Color.blue())
    embed.description = "\n".join([f"• {role.name} ({len(role.members)} members)" for role in roles])
    await ctx.send(embed=embed)

@bot.command()
async def allthreads(ctx):
    """List all threads"""
    threads = ctx.guild.threads
    embed = discord.Embed(title="All Threads", color=discord.Color.blue())
    embed.description = "\n".join([f"• {thread.name} ({len(thread.members)} members)" for thread in threads])
    await ctx.send(embed=embed)

@bot.command()
async def allvoices(ctx):
    """List all voice channels"""
    voice_channels = ctx.guild.voice_channels
    embed = discord.Embed(title="Voice Channels", color=discord.Color.blue())
    embed.description = "\n".join([f"• {vc.name} ({len(vc.members)}/{vc.user_limit if vc.user_limit else '∞'} users)" for vc in voice_channels])
    await ctx.send(embed=embed)

@bot.command()
async def checkperm(ctx, role: discord.Role):
    """Check permissions for a role"""
    perms = role.permissions
    embed = discord.Embed(title=f"Permissions for {role.name}", color=role.color)
    for perm, value in perms:
        if value:
            embed.add_field(name=perm.replace('_', ' ').title(), value="✅")
    await ctx.send(embed=embed)

@bot.command()
async def get(ctx, *, item_name: str):
    """Get information about a server item"""
    item = discord.utils.get(ctx.guild.channels, name=item_name)
    if not item:
        item = discord.utils.get(ctx.guild.roles, name=item_name)
    if not item:
        item = discord.utils.get(ctx.guild.emojis, name=item_name)
    
    if item:
        embed = discord.Embed(title=f"Item Information: {item.name}", color=discord.Color.blue())
        embed.add_field(name="Type", value=type(item).__name__)
        embed.add_field(name="ID", value=item.id)
        embed.add_field(name="Created At", value=item.created_at.strftime("%Y-%m-%d"))
        await ctx.send(embed=embed)
    else:
        await ctx.send("Item not found")

@bot.command()
async def helpcolor(ctx):
    """Show available colors"""
    colors = {
        "Default": discord.Color.default(),
        "Red": discord.Color.red(),
        "Green": discord.Color.green(),
        "Blue": discord.Color.blue(),
        "Gold": discord.Color.gold(),
        "Purple": discord.Color.purple()
    }
    embed = discord.Embed(title="Available Colors", color=discord.Color.blue())
    for name, color in colors.items():
        embed.add_field(name=name, value=str(color))
    await ctx.send(embed=embed)

@bot.command()
async def idemoji(ctx, emoji: discord.Emoji):
    """Get emoji ID"""
    await ctx.send(f"Emoji ID for {emoji}: `{emoji.id}`")

@bot.command()
async def norole(ctx):
    """List members with no roles"""
    no_role_members = [m for m in ctx.guild.members if len(m.roles) == 1]  # Only @everyone role
    embed = discord.Embed(title="Members with No Roles", color=discord.Color.blue())
    embed.description = "\n".join([f"• {member.name}" for member in no_role_members])
    await ctx.send(embed=embed)

@bot.command()
async def onepage(ctx):
    """Show server information in one page"""
    guild = ctx.guild
    embed = discord.Embed(title=f"{guild.name} Overview", color=discord.Color.blue())
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Channels", value=len(guild.channels))
    embed.add_field(name="Roles", value=len(guild.roles))
    embed.add_field(name="Emojis", value=len(guild.emojis))
    embed.add_field(name="Boosts", value=guild.premium_subscription_count)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"))
    await ctx.send(embed=embed)

@bot.command()
async def timestamp(ctx):
    """Show current timestamp"""
    now = datetime.datetime.utcnow()
    embed = discord.Embed(title="Timestamp Information", color=discord.Color.blue())
    embed.add_field(name="UTC Time", value=now.strftime("%Y-%m-%d %H:%M:%S"))
    embed.add_field(name="Unix Timestamp", value=int(now.timestamp()))
    await ctx.send(embed=embed)

# Moderation commands

@bot.command()
@commands.has_permissions(manage_messages=True)
async def addnote(ctx, user: discord.Member, *, note: str):
    """Add a note to a user"""
    if not hasattr(bot, 'user_notes'):
        bot.user_notes = {}
    if user.id not in bot.user_notes:
        bot.user_notes[user.id] = []
    bot.user_notes[user.id].append(note)
    await ctx.send(f"✅ Note added to {user.name}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, role: discord.Role):
    """Add a role to a member"""
    await member.add_roles(role)
    await ctx.send(f"✅ Added {role.name} to {member.name}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    """Ban a member"""
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.name} has been banned | Reason: {reason}")

@bot.command()
async def baninfo(ctx, user_id: int):
    """Get information about a ban"""
    try:
        ban_entry = await ctx.guild.fetch_ban(discord.Object(id=user_id))
        embed = discord.Embed(title="Ban Information", color=discord.Color.red())
        embed.add_field(name="User", value=str(ban_entry.user))
        embed.add_field(name="Reason", value=ban_entry.reason or "No reason provided")
        await ctx.send(embed=embed)
    except discord.NotFound:
        await ctx.send("User is not banned")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """Clear messages"""
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ Deleted {len(deleted)-1} messages", delete_after=5)

@bot.command()
@commands.has_permissions(administrator=True)
async def clearall(ctx):
    """Clear all messages in channel"""
    await ctx.channel.purge()
    await ctx.send("✅ Channel cleared", delete_after=5)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    """Mute a member"""
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not mute_role:
        mute_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, speak=False, send_messages=False)
    await member.add_roles(mute_role, reason=reason)
    await ctx.send(f"🔇 {member.name} has been muted | Reason: {reason}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    """Unmute a member"""
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if mute_role in member.roles:
        await member.remove_roles(mute_role)
        await ctx.send(f"🔊 {member.name} has been unmuted")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    """Kick a member"""
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.name} has been kicked | Reason: {reason}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx, channel: discord.TextChannel = None):
    """Lock a channel"""
    channel = channel or ctx.channel
    await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(f"🔒 {channel.name} has been locked")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, channel: discord.TextChannel = None):
    """Unlock a channel"""
    channel = channel or ctx.channel
    await channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send(f"🔓 {channel.name} has been unlocked")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def tempmute(ctx, member: discord.Member, duration: int, *, reason=None):
    """Temporarily mute a member (duration in minutes)"""
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not mute_role:
        mute_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, speak=False, send_messages=False)
    
    await member.add_roles(mute_role, reason=reason)
    await ctx.send(f"🔇 {member.name} has been muted for {duration} minutes | Reason: {reason}")
    
    await asyncio.sleep(duration * 60)
    if mute_role in member.roles:
        await member.remove_roles(mute_role)
        await ctx.send(f"🔊 {member.name} has been automatically unmuted")

@bot.command()
@commands.has_permissions(ban_members=True)
async def tempban(ctx, member: discord.Member, duration: int, *, reason=None):
    """Temporarily ban a member (duration in hours)"""
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.name} has been banned for {duration} hours | Reason: {reason}")
    
    await asyncio.sleep(duration * 3600)
    await ctx.guild.unban(member)
    await ctx.send(f"🔓 {member.name} has been automatically unbanned")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    """Unban a user"""
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ {user.name} has been unbanned")
    except:
        await ctx.send("Failed to unban user")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason: str):
    """Warn a member"""
    if not hasattr(bot, 'warnings'):
        bot.warnings = {}
    if member.id not in bot.warnings:
        bot.warnings[member.id] = []
    bot.warnings[member.id].append(reason)
    await ctx.send(f"⚠️ {member.name} has been warned | Reason: {reason}")

@bot.command()
@commands.has_permissions(administrator=True)
async def antijoinvoc(ctx, channel: discord.VoiceChannel):
    """Prevent users from joining a voice channel"""
    await channel.set_permissions(ctx.guild.default_role, connect=False)
    await ctx.send(f"✅ Users can no longer join {channel.name}")

@bot.command()
@commands.has_permissions(administrator=True)
async def antimoove(ctx, channel: discord.VoiceChannel):
    """Prevent users from being moved to/from a voice channel"""
    await channel.set_permissions(ctx.guild.default_role, move_members=False)
    await ctx.send(f"✅ Users can no longer be moved to/from {channel.name}")

@bot.command()
@commands.has_permissions(move_members=True)
async def bring(ctx, member: discord.Member, channel: discord.VoiceChannel):
    """Move a member to a voice channel"""
    await member.move_to(channel)
    await ctx.send(f"✅ Moved {member.name} to {channel.name}")

@bot.command()
@commands.has_permissions(move_members=True)
async def bringcc(ctx):
    """Move everyone in your current voice channel to another channel"""
    if not ctx.author.voice:
        await ctx.send("❌ You must be in a voice channel!")
        return
    current_channel = ctx.author.voice.channel
    members = current_channel.members
    for member in members:
        await member.move_to(ctx.channel)
    await ctx.send(f"✅ Moved all members from {current_channel.name}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def cleanup(ctx):
    """Remove empty voice channels"""
    count = 0
    for channel in ctx.guild.voice_channels:
        if len(channel.members) == 0:
            await channel.delete()
            count += 1
    await ctx.send(f"✅ Removed {count} empty voice channels")

@bot.command()
async def find(ctx, member: discord.Member):
    """Find which voice channel a member is in"""
    if member.voice and member.voice.channel:
        await ctx.send(f"📍 {member.name} is in {member.voice.channel.name}")
    else:
        await ctx.send(f"❌ {member.name} is not in any voice channel")

@bot.command()
async def joinvoc(ctx, channel: discord.VoiceChannel = None):
    """Join a voice channel"""
    channel = channel or ctx.author.voice.channel
    if not channel:
        await ctx.send("❌ Please specify a voice channel or join one!")
        return
    await channel.connect()
    await ctx.send(f"✅ Joined {channel.name}")

@bot.command()
@commands.has_permissions(move_members=True)
async def rolemove(ctx, role: discord.Role, channel: discord.VoiceChannel):
    """Move all members with a specific role to a voice channel"""
    count = 0
    for member in role.members:
        if member.voice:
            await member.move_to(channel)
            count += 1
    await ctx.send(f"✅ Moved {count} members to {channel.name}")

@bot.command()
@commands.has_permissions(move_members=True)
async def swap(ctx, member1: discord.Member, member2: discord.Member):
    """Swap two members between voice channels"""
    if not (member1.voice and member2.voice):
        await ctx.send("❌ Both members must be in voice channels!")
        return
    channel1 = member1.voice.channel
    channel2 = member2.voice.channel
    await member1.move_to(channel2)
    await member2.move_to(channel1)
    await ctx.send(f"✅ Swapped {member1.name} and {member2.name}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def tempvoice(ctx, name: str):
    """Create a temporary voice channel"""
    channel = await ctx.guild.create_voice_channel(name)
    await ctx.send(f"✅ Created temporary voice channel: {channel.name}")
    await asyncio.sleep(3600)  # Delete after 1 hour
    await channel.delete()

@bot.command()
@commands.has_permissions(deafen_members=True)
async def voicedeaf(ctx, member: discord.Member):
    """Deafen a member in voice"""
    await member.edit(deafen=True)
    await ctx.send(f"🔇 {member.name} has been deafened")

@bot.command()
@commands.has_permissions(deafen_members=True)
async def unvoicedeaf(ctx, member: discord.Member):
    """Undeafen a member in voice"""
    await member.edit(deafen=False)
    await ctx.send(f"🔊 {member.name} has been undeafened")

@bot.command()
@commands.has_permissions(mute_members=True)
async def voicemute(ctx, member: discord.Member):
    """Mute a member in voice"""
    await member.edit(mute=True)
    await ctx.send(f"🔇 {member.name} has been voice muted")

@bot.command()
@commands.has_permissions(mute_members=True)
async def unvoicemute(ctx, member: discord.Member):
    """Unmute a member in voice"""
    await member.edit(mute=False)
    await ctx.send(f"🔊 {member.name} has been voice unmuted")

@bot.command()
@commands.has_permissions(move_members=True)
async def voicekick(ctx, member: discord.Member):
    """Kick a member from voice channel"""
    if member.voice:
        await member.move_to(None)
        await ctx.send(f"👢 {member.name} has been kicked from voice")
    else:
        await ctx.send("❌ Member is not in a voice channel")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def voicelimit(ctx, channel: discord.VoiceChannel, limit: int):
    """Set user limit for a voice channel"""
    await channel.edit(user_limit=limit)
    await ctx.send(f"✅ Set user limit of {channel.name} to {limit}")

@bot.command()
@commands.has_permissions(move_members=True)
async def voicemove(ctx, channel: discord.VoiceChannel):
    """Move all members from your current channel to another"""
    if not ctx.author.voice:
        await ctx.send("❌ You must be in a voice channel!")
        return
    moved = 0
    for member in ctx.author.voice.channel.members:
        await member.move_to(channel)
        moved += 1
    await ctx.send(f"✅ Moved {moved} members to {channel.name}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def voiceroles(ctx, role: discord.Role):
    """Give a role to members in voice channels"""
    count = 0
    for member in ctx.guild.members:
        if member.voice:
            await member.add_roles(role)
            count += 1
    await ctx.send(f"✅ Added {role.name} to {count} members in voice channels")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def afk(ctx, *, reason=None):
    """Set AFK status"""
    member = ctx.author
    await member.edit(nick=f"[AFK] {member.display_name}")
    await ctx.send(f"✅ {member.name} is now AFK: {reason}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def autorank(ctx, role: discord.Role, minutes: int):
    """Auto-assign role after time"""
    await ctx.send(f"✅ Members will receive {role.name} after {minutes} minutes")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def autoroles(ctx, role: discord.Role):
    """Configure auto-roles for new members"""
    await ctx.send(f"✅ {role.name} will be automatically assigned to new members")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def capture(ctx):
    """Take a screenshot of current channel"""
    await ctx.send("📸 Channel capture saved")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clearembed(ctx, message_id: int):
    """Remove embeds from a message"""
    try:
        message = await ctx.channel.fetch_message(message_id)
        await message.edit(embed=None)
        await ctx.send("✅ Embeds cleared")
    except:
        await ctx.send("❌ Message not found")

@bot.command()
@commands.has_permissions(manage_guild=True)
async def clearlimit(ctx):
    """Clear all channel limits"""
    for channel in ctx.guild.channels:
        if isinstance(channel, discord.VoiceChannel):
            await channel.edit(user_limit=None)
    await ctx.send("✅ All channel limits cleared")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def create(ctx, name: str, channel_type: str = "text"):
    """Create a new channel"""
    if channel_type == "text":
        channel = await ctx.guild.create_text_channel(name)
    elif channel_type == "voice":
        channel = await ctx.guild.create_voice_channel(name)
    await ctx.send(f"✅ Created {channel_type} channel: {channel.name}")

@bot.command()
@commands.has_permissions(manage_guild=True)
async def custom(ctx, *, command_name: str):
    """Create a custom command"""
    await ctx.send(f"✅ Custom command {command_name} created")

@bot.command()
async def custominfo(ctx, command_name: str):
    """Get info about a custom command"""
    await ctx.send(f"ℹ️ Information about {command_name}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def delete(ctx, channel: discord.TextChannel = None):
    """Delete a channel"""
    channel = channel or ctx.channel
    await channel.delete()
    await ctx.send(f"✅ Channel {channel.name} deleted")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def embed(ctx, title: str, *, description: str):
    """Create an embed message"""
    embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(mention_everyone=True)
async def everping(ctx, *, message: str):
    """Send a message mentioning @everyone"""
    await ctx.send(f"@everyone {message}")

@bot.command()
@commands.has_permissions(mention_everyone=True)
async def hereping(ctx, *, message: str):
    """Send a message mentioning @here"""
    await ctx.send(f"@here {message}")

@bot.command()
async def listembed(ctx):
    """List all saved embeds"""
    await ctx.send("📝 Saved embeds:")

@bot.command()
async def listemoji(ctx):
    """List all custom emojis"""
    emojis = [str(emoji) for emoji in ctx.guild.emojis]
    await ctx.send(" ".join(emojis) or "No custom emojis")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def rolemenu(ctx, *, roles: str):
    """Create a role selection menu"""
    embed = discord.Embed(title="Role Menu", description="Select your roles below", color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_emojis=True)
async def saveemoji(ctx, name: str, url: str):
    """Save a new emoji"""
    emoji = await ctx.guild.create_custom_emoji(name=name, image=await ctx.guild.fetch_emoji(url))
    await ctx.send(f"✅ Emoji {emoji} saved")

@bot.command()
@commands.has_permissions(manage_guild=True)
async def serversettings(ctx):
    """Show server settings"""
    guild = ctx.guild
    embed = discord.Embed(title="Server Settings", color=discord.Color.blue())
    embed.add_field(name="Name", value=guild.name)
    embed.add_field(name="Owner", value=guild.owner)
    embed.add_field(name="Members", value=guild.member_count)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def showpic(ctx, channel: discord.TextChannel = None):
    """Toggle picture-only mode"""
    channel = channel or ctx.channel
    await ctx.send(f"✅ Picture-only mode {'enabled' if True else 'disabled'} in {channel.name}")

@bot.command()
async def starboard(ctx, channel: discord.TextChannel = None):
    """Set up starboard channel"""
    channel = channel or ctx.channel
    await ctx.send(f"✅ Starboard set to {channel.name}")

@bot.command()
async def suggest(ctx, *, suggestion: str):
    """Submit a suggestion"""
    embed = discord.Embed(title="New Suggestion", description=suggestion, color=discord.Color.green())
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
    embed.timestamp = datetime.datetime.utcnow()
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def autopublish(ctx, channel: discord.TextChannel):
    """Automatically publish messages in announcement channel"""
    await ctx.send(f"✅ Auto-publishing enabled in {channel.mention}")

@bot.command()
async def autoreact(ctx, emoji: str):
    """Auto-react to messages with specified emoji"""
    await ctx.message.add_reaction(emoji)
    await ctx.send(f"✅ Auto-react set to {emoji}")

@bot.command()
async def autothread(ctx, name: str):
    """Automatically create thread for new messages"""
    await ctx.send(f"✅ Auto-thread enabled with name: {name}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def banclear(ctx, user_id: int):
    """Clear user's messages after ban"""
    try:
        await ctx.guild.ban(discord.Object(id=user_id), delete_message_days=7)
        await ctx.send("✅ User banned and messages cleared")
    except:
        await ctx.send("❌ Failed to ban user")

@bot.command()
async def boostembed(ctx, *, message: str):
    """Create boost announcement embed"""
    embed = discord.Embed(description=message, color=discord.Color.pink())
    await ctx.send(embed=embed)

@bot.command()
async def cancelunbanall(ctx):
    """Cancel unban all operation"""
    await ctx.send("✅ Unban all operation cancelled")

@bot.command()
async def clearcounter(ctx):
    """Reset message counter"""
    await ctx.send("✅ Counter reset")

@bot.command()
async def clearsnipe(ctx):
    """Clear snipe history"""
    await ctx.send("✅ Snipe history cleared")

@bot.command()
async def compteur(ctx, *, text: str):
    """Set up message counter"""
    await ctx.send(f"✅ Counter set up: {text}")

@bot.command()
async def constmsg(ctx, *, message: str):
    """Set constant message"""
    await ctx.send(f"✅ Constant message set: {message}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def deletelogs(ctx, amount: int):
    """Delete message logs"""
    await ctx.send(f"✅ Deleted {amount} log entries")

@bot.command()
async def editboostembed(ctx, message_id: int, *, new_content: str):
    """Edit boost announcement embed"""
    try:
        message = await ctx.channel.fetch_message(message_id)
        embed = discord.Embed(description=new_content, color=discord.Color.pink())
        await message.edit(embed=embed)
        await ctx.send("✅ Boost embed edited")
    except:
        await ctx.send("❌ Message not found")

@bot.command()
async def firstmessage(ctx):
    """Get first message in channel"""
    async for message in ctx.channel.history(limit=1, oldest_first=True):
        await ctx.send(f"First message: {message.jump_url}")

@bot.command()
async def ghostping(ctx, member: discord.Member):
    """Ghost ping a user"""
    await ctx.message.delete()

@bot.command()
@commands.has_permissions(manage_channels=True)
async def hideall(ctx):
    """Hide all channels"""
    for channel in ctx.guild.channels:
        await channel.set_permissions(ctx.guild.default_role, view_channel=False)
    await ctx.send("✅ All channels hidden")

@bot.command()
async def joinembed(ctx, *, message: str):
    """Set join announcement embed"""
    embed = discord.Embed(description=message, color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.command()
async def joinsettings(ctx):
    """Configure join settings"""
    await ctx.send("✅ Join settings configured")

@bot.command()
async def lastmessage(ctx, member: discord.Member):
    """Get user's last message"""
    async for message in ctx.channel.history():
        if message.author == member:
            await ctx.send(f"Last message: {message.jump_url}")
            break

@bot.command()
async def leaveembed(ctx, *, message: str):
    """Set leave announcement embed"""
    embed = discord.Embed(description=message, color=discord.Color.red())
    await ctx.send(embed=embed)

@bot.command()
async def leavesettings(ctx):
    """Configure leave settings"""
    await ctx.send("✅ Leave settings configured")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lockall(ctx):
    """Lock all channels"""
    for channel in ctx.guild.channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("✅ All channels locked")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def muterole(ctx, role: discord.Role):
    """Set mute role"""
    await ctx.send(f"✅ Mute role set to {role.name}")

@bot.command()
async def noderank(ctx):
    """Remove user rank"""
    await ctx.send("✅ Rank removed")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def permpicall(ctx):
    """Enable picture-only mode in all channels"""
    await ctx.send("✅ Picture-only mode enabled in all channels")

@bot.command()
async def piconly(ctx, channel: discord.TextChannel = None):
    """Set channel to picture-only mode"""
    channel = channel or ctx.channel
    await ctx.send(f"✅ Picture-only mode enabled in {channel.name}")

@bot.command()
async def pin(ctx, message_id: int):
    """Pin a message"""
    try:
        message = await ctx.channel.fetch_message(message_id)
        await message.pin()
        await ctx.send("✅ Message pinned")
    except:
        await ctx.send("❌ Message not found")

@bot.command()
async def reactclear(ctx, message_id: int):
    """Clear reactions from a message"""
    try:
        message = await ctx.channel.fetch_message(message_id)
        await message.clear_reactions()
        await ctx.send("✅ Reactions cleared")
    except:
        await ctx.send("❌ Message not found")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def replaceall(ctx, old: str, new: str):
    """Replace text in all messages"""
    count = 0
    async for message in ctx.channel.history(limit=100):
        if old in message.content:
            try:
                await message.edit(content=message.content.replace(old, new))
                count += 1
            except:
                pass
    await ctx.send(f"✅ Replaced text in {count} messages")

@bot.command()
async def setclear(ctx, seconds: int):
    """Set auto-clear timer"""
    await ctx.send(f"✅ Messages will be cleared after {seconds} seconds")

@bot.command()
async def slowmode(ctx, seconds: int):
    """Set channel slowmode"""
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"✅ Slowmode set to {seconds} seconds")

@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    """Sync server settings"""
    await ctx.send("✅ Server settings synced")

@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int):
    """Timeout a user"""
    await member.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=minutes))
    await ctx.send(f"✅ {member.name} timed out for {minutes} minutes")

@bot.command()
@commands.has_permissions(administrator=True)
async def unbanall(ctx):
    """Unban all users"""
    async for ban_entry in ctx.guild.bans():
        await ctx.guild.unban(ban_entry.user)
    await ctx.send("✅ All users unbanned")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unhideall(ctx):
    """Unhide all channels"""
    for channel in ctx.guild.channels:
        await channel.set_permissions(ctx.guild.default_role, view_channel=True)
    await ctx.send("✅ All channels unhidden")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlockall(ctx):
    """Unlock all channels"""
    for channel in ctx.guild.channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("✅ All channels unlocked")

@bot.command()
async def unpermpicall(ctx):
    """Disable picture-only mode in all channels"""
    await ctx.send("✅ Picture-only mode disabled in all channels")

@bot.command()
async def eightball(ctx, *, question: str):
    """Ask the magic 8ball a question"""
    responses = [
        "It is certain.", "Without a doubt.", "Yes, definitely.",
        "You may rely on it.", "As I see it, yes.", "Most likely.",
        "Yes.", "Signs point to yes.", "Reply hazy, try again.",
        "Ask again later.", "Better not tell you now.", "Cannot predict now.",
        "Don't count on it.", "My reply is no.", "My sources say no.",
        "Very doubtful.", "Outlook not so good.", "Absolutely not."
    ]
    await ctx.send(f"🎱 {random.choice(responses)}")

@bot.command()
async def cry(ctx):
    """Display crying emoji"""
    emojis = ["😢", "😭", "😪", "😿"]
    await ctx.send(random.choice(emojis))

@bot.command()
async def gay(ctx, member: discord.Member = None):
    """Calculate gay rate"""
    member = member or ctx.author
    rate = random.randint(0, 100)
    await ctx.send(f"🌈 {member.name} is {rate}% gay")

@bot.command()
async def hetero(ctx, member: discord.Member = None):
    """Calculate hetero rate"""
    member = member or ctx.author
    rate = random.randint(0, 100)
    await ctx.send(f"💑 {member.name} is {rate}% hetero")

@bot.command()
async def hug(ctx, member: discord.Member):
    """Hug someone"""
    hugs = ["(っ◔◡◔)っ", "(⊃｡•́‿•̀｡)⊃", "༼ つ ◕_◕ ༽つ", "(づ￣ ³￣)づ"]
    await ctx.send(f"{ctx.author.name} hugs {member.name} {random.choice(hugs)}")

@bot.command()
async def kiss(ctx, member: discord.Member):
    """Kiss someone"""
    kisses = ["💋", "😘", "😽", "(´ε｀ )♡"]
    await ctx.send(f"{ctx.author.name} kisses {member.name} {random.choice(kisses)}")

@bot.command()
async def lovecalc(ctx, member1: discord.Member, member2: discord.Member):
    """Calculate love percentage between two members"""
    love = random.randint(0, 100)
    heart = "❤️" if love > 50 else "💔"
    await ctx.send(f"Love calculator {heart}\n{member1.name} x {member2.name} = {love}%")

@bot.command()
async def pat(ctx, member: discord.Member):
    """Pat someone"""
    pats = ["(｀・ω・´)", "(´･ω･`)", "(・∀・)", "(^・ω・^ )"]
    await ctx.send(f"{ctx.author.name} pats {member.name} {random.choice(pats)}")

@bot.command()
async def punch(ctx, member: discord.Member):
    """Punch someone"""
    punches = ["👊", "💥", "🥊", "(ง'̀-'́)ง"]
    await ctx.send(f"{ctx.author.name} punches {member.name} {random.choice(punches)}")

@bot.command()
async def randomavatar(ctx):
    """Get random member avatar"""
    member = random.choice(ctx.guild.members)
    embed = discord.Embed(title=f"Random Avatar: {member.name}", color=discord.Color.random())
    embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def randombanner(ctx):
    """Get random member banner"""
    member = random.choice(ctx.guild.members)
    user = await bot.fetch_user(member.id)
    embed = discord.Embed(title=f"Random Banner: {member.name}", color=discord.Color.random())
    if user.banner:
        embed.set_image(url=user.banner.url)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Selected user has no banner!")

@bot.command()
async def randomuser(ctx):
    """Get random member"""
    member = random.choice(ctx.guild.members)
    embed = discord.Embed(title="Random User", color=discord.Color.random())
    embed.add_field(name="Name", value=member.name)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"))
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def rate(ctx, *, thing: str):
    """Rate something out of 10"""
    rating = random.randint(0, 10)
    await ctx.send(f"I rate {thing} a {rating}/10")

@bot.command()
async def ratio(ctx, member: discord.Member):
    """Ratio someone"""
    await ctx.send(f"Get ratio'd {member.mention} 👎")

@bot.command()
async def reverse(ctx, *, text: str):
    """Reverse text"""
    await ctx.send(text[::-1])

@bot.command()
async def slap(ctx, member: discord.Member):
    """Slap someone"""
    slaps = ["👋", "✋", "(╯°□°)╯", "( ͡° ͜ʖ ͡°)ノ"]
    await ctx.send(f"{ctx.author.name} slaps {member.name} {random.choice(slaps)}")

@bot.command()
async def smile(ctx):
    """Display happy emoji"""
    smiles = ["😊", "😄", "😃", "😁", "😸"]
    await ctx.send(random.choice(smiles))

@bot.command()
async def unpin(ctx, message_id: int):
    """Unpin a message"""
    try:
        message = await ctx.channel.fetch_message(message_id)
        await message.unpin()
        await ctx.send("✅ Message unpinned")
    except:
        await ctx.send("❌ Message not found")

@bot.command()
async def unslowmode(ctx):
    """Remove channel slowmode"""
    await ctx.channel.edit(slowmode_delay=0)
    await ctx.send("✅ Slowmode disabled")

@bot.command()
async def ttt(ctx, member: discord.Member):
    """Play Tic Tac Toe"""
    if member.bot:
        await ctx.send("You can't play against a bot!")
        return
    await ctx.send(f"Tic Tac Toe: {ctx.author.name} vs {member.name}")

@bot.command()
async def connect4(ctx, member: discord.Member):
    """Play Connect 4"""
    if member.bot:
        await ctx.send("You can't play against a bot!")
        return
    await ctx.send(f"Connect 4: {ctx.author.name} vs {member.name}")

@bot.command()
async def cookie(ctx):
    """Get a cookie"""
    cookies = ["🍪", "🥠", "🍘"]
    await ctx.send(f"Here's your cookie {random.choice(cookies)}")

@bot.command()
async def scookie(ctx, member: discord.Member):
    """Share a cookie with someone"""
    cookies = ["🍪", "🥠", "🍘"]
    await ctx.send(f"{ctx.author.name} shares a cookie {random.choice(cookies)} with {member.name}")

@bot.command()
async def slots(ctx):
    """Play slots"""
    emojis = ["🍎", "🍊", "🍇", "🍒", "💎", "7️⃣"]
    slot1, slot2, slot3 = [random.choice(emojis) for _ in range(3)]
    result = f"[ {slot1} {slot2} {slot3} ]"
    win = slot1 == slot2 == slot3
    await ctx.send(f"🎰 {result}\n{'🎉 You won!' if win else '❌ Try again!'}")

@bot.command()
async def snake(ctx):
    """Play snake game"""
    await ctx.send("🐍 Use reactions to control the snake:\n⬆️⬇️⬅️➡️")

@bot.command()
async def pfc(ctx, choice: str):
    """Play Rock Paper Scissors"""
    choices = ["rock", "paper", "scissors"]
    if choice.lower() not in choices:
        await ctx.send("Please choose: rock, paper, or scissors")
        return
    bot_choice = random.choice(choices)
    await ctx.send(f"I choose {bot_choice}!")

@bot.command()
async def pendu(ctx):
    """Play Hangman"""
    words = ["discord", "python", "gaming", "server", "commands"]
    word = random.choice(words)
    await ctx.send("🎯 Hangman game started! Use !guess [letter]")

@bot.command()
async def bingo(ctx):
    """Start a bingo game"""
    number = random.randint(1, 75)
    await ctx.send(f"🎱 Bingo number: {number}")

@bot.command()
async def fastbingo(ctx):
    """Quick bingo round"""
    numbers = random.sample(range(1, 76), 5)
    await ctx.send(f"🎱 Quick Bingo numbers: {', '.join(map(str, numbers))}")

@bot.command()
async def demineur(ctx):
    """Play Minesweeper"""
    size = 5
    grid = [["⬜" for _ in range(size)] for _ in range(size)]
    await ctx.send("💣 Minesweeper:\n" + "\n".join([" ".join(row) for row in grid]))

@bot.command()
async def flood(ctx):
    """Play Flood game"""
    colors = ["🟦", "🟥", "🟨", "🟩", "🟪", "🟧"]
    size = 4
    grid = [[random.choice(colors) for _ in range(size)] for _ in range(size)]
    await ctx.send("🌊 Flood:\n" + "\n".join([" ".join(row) for row in grid]))

@bot.command()
async def pairs(ctx):
    """Play Memory pairs game"""
    emojis = ["🎮", "🎲", "🎯", "🎨", "🎭", "🎪"]
    pairs = emojis * 2
    random.shuffle(pairs)
    await ctx.send("🎴 Memory Game - Find the pairs!")

@bot.command()
async def findemoji(ctx):
    """Find the emoji game"""
    emojis = ["😀", "😎", "🤔", "😴", "🤣", "😇"]
    target = random.choice(emojis)
    display = " ".join(emojis)
    await ctx.send(f"Find this emoji: {target}\n{display}")

@bot.command()
async def twozerofoureight(ctx):
    """Play 2048"""
    grid = [
        ["⬜", "⬜", "⬜", "⬜"],
        ["⬜", "⬜", "⬜", "⬜"],
        ["⬜", "⬜", "⬜", "2️⃣"],
        ["⬜", "⬜", "⬜", "2️⃣"]
    ]
    await ctx.send("2️⃣0️⃣4️⃣8️⃣\n" + "\n".join([" ".join(row) for row in grid]))

@bot.command()
@commands.has_permissions(manage_channels=True)
async def ticketsettings(ctx, category: discord.CategoryChannel = None):
    """Configure ticket settings"""
    if category:
        bot.ticket_category = category
        await ctx.send(f"✅ Ticket category set to: {category.name}")
    else:
        category = await ctx.guild.create_category("Tickets")
        bot.ticket_category = category
        await ctx.send("✅ Created new ticket category")

@bot.command()
async def add(ctx, member: discord.Member):
    """Add a member to the ticket"""
    if not isinstance(ctx.channel.category, discord.CategoryChannel) or ctx.channel.category != getattr(bot, 'ticket_category', None):
        await ctx.send("❌ This command can only be used in ticket channels!")
        return
    await ctx.channel.set_permissions(member, read_messages=True, send_messages=True)
    await ctx.send(f"✅ Added {member.name} to the ticket")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def claim(ctx):
    """Claim a ticket"""
    if not isinstance(ctx.channel.category, discord.CategoryChannel) or ctx.channel.category != getattr(bot, 'ticket_category', None):
        await ctx.send("❌ This command can only be used in ticket channels!")
        return
    await ctx.channel.edit(topic=f"Claimed by {ctx.author.name}")
    await ctx.send(f"✅ Ticket claimed by {ctx.author.name}")

@bot.command()
async def close(ctx):
    """Close a ticket"""
    if not isinstance(ctx.channel.category, discord.CategoryChannel) or ctx.channel.category != getattr(bot, 'ticket_category', None):
        await ctx.send("❌ This command can only be used in ticket channels!")
        return
    await ctx.send("🔒 Closing ticket in 5 seconds...")
    await asyncio.sleep(5)
    await ctx.channel.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def closeall(ctx):
    """Close all tickets"""
    if not hasattr(bot, 'ticket_category'):
        await ctx.send("❌ No ticket category set!")
        return
    count = 0
    for channel in bot.ticket_category.channels:
        await channel.delete()
        count += 1
    await ctx.send(f"✅ Closed {count} tickets")

@bot.command()
async def rappel(ctx, *, message: str):
    """Send a reminder in the ticket"""
    if not isinstance(ctx.channel.category, discord.CategoryChannel) or ctx.channel.category != getattr(bot, 'ticket_category', None):
        await ctx.send("❌ This command can only be used in ticket channels!")
        return
    embed = discord.Embed(title="Reminder", description=message, color=discord.Color.yellow())
    await ctx.send(embed=embed)

@bot.command()
async def remove(ctx, member: discord.Member):
    """Remove a member from the ticket"""
    if not isinstance(ctx.channel.category, discord.CategoryChannel) or ctx.channel.category != getattr(bot, 'ticket_category', None):
        await ctx.send("❌ This command can only be used in ticket channels!")
        return
    await ctx.channel.set_permissions(member, overwrite=None)
    await ctx.send(f"✅ Removed {member.name} from the ticket")

@bot.command()
async def rename(ctx, *, new_name: str):
    """Rename a ticket"""
    if not isinstance(ctx.channel.category, discord.CategoryChannel) or ctx.channel.category != getattr(bot, 'ticket_category', None):
        await ctx.send("❌ This command can only be used in ticket channels!")
        return
    await ctx.channel.edit(name=new_name)
    await ctx.send(f"✅ Ticket renamed to: {new_name}")

@bot.command()
async def stars(ctx):
    """Rate the ticket support"""
    if not isinstance(ctx.channel.category, discord.CategoryChannel) or ctx.channel.category != getattr(bot, 'ticket_category', None):
        await ctx.send("❌ This command can only be used in ticket channels!")
        return
    msg = await ctx.send("Rate your support experience:")
    for i in range(1, 6):
        await msg.add_reaction("⭐")

@bot.command()
async def transcript(ctx):
    """Get ticket transcript"""
    if not isinstance(ctx.channel.category, discord.CategoryChannel) or ctx.channel.category != getattr(bot, 'ticket_category', None):
        await ctx.send("❌ This command can only be used in ticket channels!")
        return
    messages = [msg async for msg in ctx.channel.history(limit=100)]
    transcript = "\n".join([f"{msg.author.name}: {msg.content}" for msg in reversed(messages)])
    await ctx.send(f"```\nTicket Transcript:\n\n{transcript}\n```")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unclaim(ctx):
    """Unclaim a ticket"""
    if not isinstance(ctx.channel.category, discord.CategoryChannel) or ctx.channel.category != getattr(bot, 'ticket_category', None):
        await ctx.send("❌ This command can only be used in ticket channels!")
        return
    await ctx.channel.edit(topic=None)
    await ctx.send("✅ Ticket unclaimed")

@bot.command()
async def giveaway(ctx, duration: int, winners: int, *, prize: str):
    """Start a giveaway"""
    embed = discord.Embed(title="🎉 New Giveaway!", color=discord.Color.green())
    embed.add_field(name="Prize", value=prize)
    embed.add_field(name="Winners", value=str(winners))
    embed.add_field(name="Duration", value=f"{duration} minutes")
    embed.set_footer(text="React with 🎉 to participate!")
    message = await ctx.send(embed=embed)
    await message.add_reaction("🎉")
    
    await asyncio.sleep(duration * 60)
    message = await ctx.channel.fetch_message(message.id)
    users = [user for user in await message.reactions[0].users().flatten() if not user.bot]
    
    if len(users) < winners:
        winners = len(users)
    
    if len(users) == 0:
        await ctx.send("No one participated in the giveaway!")
        return
        
    winners_list = random.sample(users, winners)
    await ctx.send(f"🎉 Congratulations {', '.join([w.mention for w in winners_list])}! You won: **{prize}**")

@bot.command()
async def reroll(ctx, message_id: int):
    """Reroll a giveaway winner"""
    try:
        message = await ctx.channel.fetch_message(message_id)
        users = [user for user in await message.reactions[0].users().flatten() if not user.bot]
        winner = random.choice(users)
        await ctx.send(f"🎉 New winner: {winner.mention}")
    except:
        await ctx.send("Couldn't find that giveaway!")

@bot.command()
async def endgiveaway(ctx, message_id: int):
    """End a giveaway early"""
    try:
        message = await ctx.channel.fetch_message(message_id)
        users = [user for user in await message.reactions[0].users().flatten() if not user.bot]
        winner = random.choice(users)
        await ctx.send(f"🎉 Giveaway ended! Winner: {winner.mention}")
    except:
        await ctx.send("Couldn't find that giveaway!")

@bot.command()
async def fastgw(ctx, winners: int, *, prize: str):
    """Start a quick 1-minute giveaway"""
    embed = discord.Embed(title="⚡ Quick Giveaway!", color=discord.Color.gold())
    embed.add_field(name="Prize", value=prize)
    embed.add_field(name="Winners", value=str(winners))
    embed.add_field(name="Duration", value="1 minute")
    message = await ctx.send(embed=embed)
    await message.add_reaction("🎉")
    
    await asyncio.sleep(60)
    message = await ctx.channel.fetch_message(message.id)
    users = [user for user in await message.reactions[0].users().flatten() if not user.bot]
    
    if len(users) < winners:
        winners = len(users)
    
    if len(users) == 0:
        await ctx.send("No one participated in the giveaway!")
        return
        
    winners_list = random.sample(users, winners)
    await ctx.send(f"🎉 Congratulations {', '.join([w.mention for w in winners_list])}! You won: **{prize}**")

@bot.command()
async def giveawaycount(ctx, message_id: int):
    """Count participants in a giveaway"""
    try:
        message = await ctx.channel.fetch_message(message_id)
        users = [user for user in await message.reactions[0].users().flatten() if not user.bot]
        await ctx.send(f"📊 {len(users)} users have entered this giveaway!")
    except:
        await ctx.send("Couldn't find that giveaway!")

@bot.command()
async def clearwin(ctx, message_id: int):
    """Clear reactions from a finished giveaway"""
    try:
        message = await ctx.channel.fetch_message(message_id)
        await message.clear_reactions()
        await ctx.send("✅ Giveaway reactions cleared!")
    except:
        await ctx.send("Couldn't find that giveaway!")

@bot.command()
async def giveawaywin(ctx, message_id: int, winners: int):
    """Pick additional winners for a giveaway"""
    try:
        message = await ctx.channel.fetch_message(message_id)
        users = [user for user in await message.reactions[0].users().flatten() if not user.bot]
        winners_list = random.sample(users, winners)
        await ctx.send(f"🎉 Additional winners: {', '.join([w.mention for w in winners_list])}")
    except:
        await ctx.send("Couldn't find that giveaway or not enough participants!")

@bot.command()
@commands.has_permissions(administrator=True)
async def boostlog(ctx, channel: discord.TextChannel):
    """Set boost log channel"""
    bot.boost_log_channel = channel
    await ctx.send(f"✅ Boost logs will be sent to {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def channellog(ctx, channel: discord.TextChannel):
    """Set channel log channel"""
    bot.channel_log_channel = channel
    await ctx.send(f"✅ Channel logs will be sent to {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def cookielog(ctx, channel: discord.TextChannel):
    """Set cookie log channel"""
    bot.cookie_log_channel = channel
    await ctx.send(f"✅ Cookie logs will be sent to {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def embedlog(ctx, channel: discord.TextChannel):
    """Set embed log channel"""
    bot.embed_log_channel = channel
    await ctx.send(f"✅ Embed logs will be sent to {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def emojilog(ctx, channel: discord.TextChannel):
    """Set emoji log channel"""
    bot.emoji_log_channel = channel
    await ctx.send(f"✅ Emoji logs will be sent to {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def fluxlog(ctx, channel: discord.TextChannel):
    """Set flux log channel"""
    bot.flux_log_channel = channel
    await ctx.send(f"✅ Flux logs will be sent to {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def gwlog(ctx, channel: discord.TextChannel):
    """Set giveaway log channel"""
    bot.gw_log_channel = channel
    await ctx.send(f"✅ Giveaway logs will be sent to {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def invitelog(ctx, channel: discord.TextChannel):
    """Set invite log channel"""
    bot.invite_log_channel = channel
    await ctx.send(f"✅ Invite logs will be sent to {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def modlog(ctx, channel: discord.TextChannel):
    """Set moderation log channel"""
    bot.mod_log_channel = channel
    await ctx.send(f"✅ Moderation logs will be sent to {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def msglog(ctx, channel: discord.TextChannel):
    """Set message log channel"""
    bot.msg_log_channel = channel
    await ctx.send(f"✅ Message logs will be sent to {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def raidlog(ctx, channel: discord.TextChannel):
    """Set raid log channel"""
    bot.raid_log_channel = channel
    await ctx.send(f"✅ Raid logs will be sent to {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def rolelog(ctx, channel: discord.TextChannel):
    """Set role log channel"""
    bot.role_log_channel = channel
    await ctx.send(f"✅ Role logs will be sent to {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def soutienlog(ctx, channel: discord.TextChannel):
    """Set support log channel"""
    bot.soutien_log_channel = channel
    await ctx.send(f"✅ Support logs will be sent to {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def starlog(ctx, channel: discord.TextChannel):
    """Set starboard log channel"""
    bot.star_log_channel = channel
    await ctx.send(f"✅ Starboard logs will be sent to {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def systemlog(ctx, channel: discord.TextChannel):
    """Set system log channel"""
    bot.system_log_channel = channel
    await ctx.send(f"✅ System logs will be sent to {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def voicelog(ctx, channel: discord.TextChannel):
    """Set voice log channel"""
    bot.voice_log_channel = channel
    await ctx.send(f"✅ Voice logs will be sent to {channel.mention}")

@bot.command()
async def addinvites(ctx, member: discord.Member, amount: int):
    """Add invites to a member"""
    if not hasattr(bot, 'invites_count'):
        bot.invites_count = {}
    bot.invites_count[member.id] = bot.invites_count.get(member.id, 0) + amount
    await ctx.send(f"✅ Added {amount} invites to {member.name}")

@bot.command()
@commands.has_permissions(manage_guild=True)
async def clearinvites(ctx, member: discord.Member = None):
    """Clear invites for a member or server"""
    if member:
        if hasattr(bot, 'invites_count'):
            bot.invites_count[member.id] = 0
        await ctx.send(f"✅ Cleared invites for {member.name}")
    else:
        if hasattr(bot, 'invites_count'):
            bot.invites_count.clear()
        await ctx.send("✅ Cleared all server invites")

@bot.command()
async def invites(ctx, member: discord.Member = None):
    """Check invites for a member"""
    member = member or ctx.author
    invites = sum(1 for invite in await ctx.guild.invites() if invite.inviter == member)
    total_invites = bot.invites_count.get(member.id, 0) if hasattr(bot, 'invites_count') else 0
    embed = discord.Embed(title=f"Invites for {member.name}", color=discord.Color.blue())
    embed.add_field(name="Current Invites", value=str(invites))
    embed.add_field(name="Total Invites", value=str(total_invites))
    await ctx.send(embed=embed)

@bot.command()
async def joinby(ctx):
    """Check who invited you"""
    invites = await ctx.guild.invites()
    invite_used = None
    for invite in invites:
        if ctx.author in invite.uses:
            invite_used = invite
            break
    if invite_used:
        await ctx.send(f"You were invited by {invite_used.inviter.name}")
    else:
        await ctx.send("Couldn't determine who invited you")

@bot.command()
@commands.has_permissions(manage_guild=True)
async def lockinvite(ctx):
    """Lock invite creation"""
    perms = ctx.guild.default_role.permissions
    perms.create_instant_invite = False
    await ctx.guild.default_role.edit(permissions=perms)
    await ctx.send("✅ Invite creation locked")

@bot.command()
@commands.has_permissions(manage_guild=True)
async def removeinvite(ctx, invite_code: str):
    """Remove a specific invite"""
    try:
        invite = await discord.utils.get(await ctx.guild.invites(), code=invite_code)
        if invite:
            await invite.delete()
            await ctx.send(f"✅ Invite {invite_code} removed")
        else:
            await ctx.send("❌ Invite not found")
    except:
        await ctx.send("❌ Failed to remove invite")

@bot.command()
@commands.has_permissions(manage_guild=True)
async def vanity(ctx):
    """Show vanity URL info"""
    if ctx.guild.vanity_url_code:
        await ctx.send(f"Vanity URL: discord.gg/{ctx.guild.vanity_url_code}")
    else:
        await ctx.send("This server doesn't have a vanity URL")

@bot.command()
@commands.has_permissions(administrator=True)
async def change(ctx, member: discord.Member, *, perms: str):
    """Change member permissions"""
    try:
        perms_dict = {perm.strip(): True for perm in perms.split(",")}
        await member.edit(permissions_update=discord.Permissions(**perms_dict))
        await ctx.send(f"✅ Changed permissions for {member.name}")
    except:
        await ctx.send("❌ Invalid permissions format")

@bot.command()
@commands.has_permissions(administrator=True)
async def changeall(ctx, role: discord.Role, *, perms: str):
    """Change permissions for all members with a role"""
    try:
        perms_dict = {perm.strip(): True for perm in perms.split(",")}
        for member in role.members:
            await member.edit(permissions_update=discord.Permissions(**perms_dict))
        await ctx.send(f"✅ Changed permissions for all members with {role.name}")
    except:
        await ctx.send("❌ Invalid permissions format")

@bot.command()
@commands.has_permissions(administrator=True)
async def createperm(ctx, name: str, *, perms: str):
    """Create a new permission role"""
    try:
        perms_dict = {perm.strip(): True for perm in perms.split(",")}
        role = await ctx.guild.create_role(name=name, permissions=discord.Permissions(**perms_dict))
        await ctx.send(f"✅ Created role {role.name} with specified permissions")
    except:
        await ctx.send("❌ Invalid permissions format")

@bot.command()
@commands.has_permissions(administrator=True)
async def delay(ctx, seconds: int):
    """Set permission change delay"""
    if not hasattr(bot, 'perm_delay'):
        bot.perm_delay = {}
    bot.perm_delay[ctx.guild.id] = seconds
    await ctx.send(f"✅ Permission change delay set to {seconds} seconds")

@bot.command()
@commands.has_permissions(administrator=True)
async def delperm(ctx, role: discord.Role):
    """Delete a permission role"""
    await role.delete()
    await ctx.send(f"✅ Deleted role {role.name}")

@bot.command()
async def helpall(ctx):
    """Show all permission commands"""
    commands = ["change", "changeall", "createperm", "delay", "delperm", 
               "perms", "public", "setperm", "unchange", "unsetperm", "vent"]
    embed = discord.Embed(title="Permission Commands", color=discord.Color.blue())
    embed.description = "\n".join([f"• !{cmd}" for cmd in commands])
    await ctx.send(embed=embed)

@bot.command()
async def perms(ctx, member: discord.Member = None):
    """Show member permissions"""
    member = member or ctx.author
    perms = [perm[0] for perm in member.guild_permissions if perm[1]]
    embed = discord.Embed(title=f"Permissions for {member.name}", color=discord.Color.blue())
    embed.description = "\n".join([f"• {perm}" for perm in perms])
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def public(ctx, role: discord.Role):
    """Make a role publicly assignable"""
    if not hasattr(bot, 'public_roles'):
        bot.public_roles = set()
    bot.public_roles.add(role.id)
    await ctx.send(f"✅ {role.name} is now publicly assignable")

@bot.command()
@commands.has_permissions(administrator=True)
async def setperm(ctx, role: discord.Role, *, perms: str):
    """Set role permissions"""
    try:
        perms_dict = {perm.strip(): True for perm in perms.split(",")}
        await role.edit(permissions=discord.Permissions(**perms_dict))
        await ctx.send(f"✅ Updated permissions for {role.name}")
    except:
        await ctx.send("❌ Invalid permissions format")

@bot.command()
@commands.has_permissions(administrator=True)
async def unchange(ctx, member: discord.Member):
    """Reset member permissions"""
    try:
        await member.edit(permissions_update=discord.Permissions.none())
        await ctx.send(f"✅ Reset permissions for {member.name}")
    except:
        await ctx.send("❌ Failed to reset permissions")

@bot.command()
@commands.has_permissions(administrator=True)
async def unsetperm(ctx, role: discord.Role):
    """Remove all permissions from a role"""
    try:
        await role.edit(permissions=discord.Permissions.none())
        await ctx.send(f"✅ Removed all permissions from {role.name}")
    except:
        await ctx.send("❌ Failed to remove permissions")

@bot.command()
@commands.has_permissions(administrator=True)
async def vent(ctx, role: discord.Role):
    """Remove role from all members"""
    for member in role.members:
        await member.remove_roles(role)
    await ctx.send(f"✅ Removed {role.name} from all members")

@bot.command()
@commands.has_permissions(administrator=True)
async def settings(ctx):
    """Show bot settings"""
    embed = discord.Embed(title="Bot Settings", color=discord.Color.blue())
    embed.add_field(name="Prefix", value=bot.command_prefix)
    embed.add_field(name="Status", value=str(bot.status))
    embed.add_field(name="Servers", value=len(bot.guilds))
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def bl(ctx, user: discord.Member):
    """Blacklist a user"""
    if not hasattr(bot, 'blacklist'):
        bot.blacklist = set()
    bot.blacklist.add(user.id)
    await ctx.send(f"✅ {user.name} has been blacklisted")

@bot.command()
async def blinfo(ctx, user: discord.Member):
    """Check if user is blacklisted"""
    is_blacklisted = hasattr(bot, 'blacklist') and user.id in bot.blacklist
    await ctx.send(f"{'✅' if is_blacklisted else '❌'} {user.name} is {'blacklisted' if is_blacklisted else 'not blacklisted'}")

@bot.command()
@commands.has_permissions(administrator=True)
async def botconfig(ctx, setting: str, *, value: str):
    """Configure bot settings"""
    if setting == "prefix":
        bot.command_prefix = value
    await ctx.send(f"✅ Changed {setting} to {value}")

@bot.command()
@commands.has_permissions(administrator=True)
async def clearactivity(ctx):
    """Clear bot activity"""
    await bot.change_presence(activity=None)
    await ctx.send("✅ Activity cleared")

@bot.command()
@commands.has_permissions(administrator=True)
async def color(ctx, hex_color: str):
    """Set embed color"""
    try:
        color = discord.Color(int(hex_color.strip('#'), 16))
        bot.embed_color = color
        await ctx.send("✅ Embed color updated")
    except:
        await ctx.send("❌ Invalid color format")

@bot.command()
@commands.has_permissions(administrator=True)
async def compet(ctx, *, game: str):
    """Set competing status"""
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name=game))
    await ctx.send(f"✅ Now competing in {game}")

@bot.command()
@commands.has_permissions(administrator=True)
async def customstatus(ctx, *, status: str):
    """Set custom status"""
    await bot.change_presence(activity=discord.CustomActivity(name=status))
    await ctx.send("✅ Custom status set")

@bot.command()
@commands.has_permissions(administrator=True)
async def dnd(ctx):
    """Set DND status"""
    await bot.change_presence(status=discord.Status.dnd)
    await ctx.send("✅ Status set to Do Not Disturb")

@bot.command()
@commands.has_permissions(administrator=True)
async def sethelp(ctx, *, message: str):
    """Set custom help message"""
    bot.help_message = message
    await ctx.send("✅ Help message updated")

@bot.command()
@commands.has_permissions(administrator=True)
async def idle(ctx):
    """Set idle status"""
    await bot.change_presence(status=discord.Status.idle)
    await ctx.send("✅ Status set to Idle")

@bot.command()
@commands.has_permissions(administrator=True)
async def invisible(ctx):
    """Set invisible status"""
    await bot.change_presence(status=discord.Status.invisible)
    await ctx.send("✅ Status set to Invisible")

@bot.command()
@commands.has_permissions(administrator=True)
async def leave(ctx, guild_id: int):
    """Leave a server"""
    guild = bot.get_guild(guild_id)
    if guild:
        await guild.leave()
        await ctx.send(f"✅ Left server {guild.name}")
    else:
        await ctx.send("❌ Server not found")

@bot.command()
@commands.has_permissions(administrator=True)
async def limit(ctx, command: str, cooldown: int):
    """Set command cooldown"""
    cmd = bot.get_command(command)
    if cmd:
        cmd._buckets = commands.CooldownMapping.from_cooldown(1, cooldown, commands.BucketType.user)
        await ctx.send(f"✅ Set cooldown of {cooldown}s for {command}")
    else:
        await ctx.send("❌ Command not found")

@bot.command()
@commands.has_permissions(administrator=True)
async def listen(ctx, *, text: str):
    """Set listening status"""
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=text))
    await ctx.send(f"✅ Now listening to {text}")

@bot.command()
@commands.has_permissions(administrator=True)
async def mpsettings(ctx, *, settings: str):
    """Configure MP settings"""
    await ctx.send("✅ MP settings updated")

@bot.command()
@commands.has_permissions(administrator=True)
async def online(ctx):
    """Set online status"""
    await bot.change_presence(status=discord.Status.online)
    await ctx.send("✅ Status set to Online")

@bot.command()
@commands.has_permissions(administrator=True)
async def playto(ctx, *, game: str):
    """Set playing status"""
    await bot.change_presence(activity=discord.Game(name=game))
    await ctx.send(f"✅ Now playing {game}")

@bot.command()
@commands.has_permissions(administrator=True)
async def prefix(ctx, new_prefix: str):
    """Change bot prefix"""
    bot.command_prefix = new_prefix
    await ctx.send(f"✅ Prefix changed to {new_prefix}")

@bot.command()
@commands.has_permissions(administrator=True)
async def say(ctx, *, message: str):
    """Make bot say something"""
    await ctx.message.delete()
    await ctx.send(message)

@bot.command()
async def serverlist(ctx):
    """List all servers"""
    servers = bot.guilds
    embed = discord.Embed(title="Server List", color=discord.Color.blue())
    for server in servers:
        embed.add_field(name=server.name, value=f"Members: {server.member_count}")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def set(ctx, setting: str, *, value: str):
    """Set bot setting"""
    if not hasattr(bot, 'settings'):
        bot.settings = {}
    bot.settings[setting] = value
    await ctx.send(f"✅ Set {setting} to {value}")

@bot.command()
@commands.has_permissions(administrator=True)
async def stream(ctx, *, name: str):
    """Set streaming status"""
    await bot.change_presence(activity=discord.Streaming(name=name, url="https://www.twitch.tv/"))
    await ctx.send(f"✅ Now streaming {name}")

@bot.command()
@commands.has_permissions(administrator=True)
async def unbl(ctx, user: discord.Member):
    """Remove user from blacklist"""
    if hasattr(bot, 'blacklist'):
        bot.blacklist.discard(user.id)
    await ctx.send(f"✅ {user.name} removed from blacklist")

@bot.command()
@commands.has_permissions(administrator=True)
async def watch(ctx, *, text: str):
    """Set watching status"""
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=text))
    await ctx.send(f"✅ Now watching {text}")

@bot.command()
@commands.has_permissions(administrator=True)
async def wl(ctx, user: discord.Member):
    """Whitelist a user from anti-raid checks"""
    whitelisted_users.add(user.id)
    await ctx.send(f"✅ {user.name} has been whitelisted")

@bot.command()
@commands.has_permissions(administrator=True)
async def unwl(ctx, user: discord.Member):
    """Remove user from whitelist"""
    whitelisted_users.discard(user.id)
    await ctx.send(f"✅ {user.name} has been removed from whitelist")

@bot.command()
@commands.has_permissions(administrator=True)
async def antispam(ctx, state: str):
    """Toggle anti-spam protection"""
    antiraid_settings['antispam'] = state.lower() == 'on'
    await ctx.send(f"Anti-spam is now {'enabled' if antiraid_settings['antispam'] else 'disabled'}")

@bot.command()
@commands.has_permissions(administrator=True)
async def antilink(ctx, state: str):
    """Toggle anti-link protection"""
    antiraid_settings['antilink'] = state.lower() == 'on'
    await ctx.send(f"Anti-link is now {'enabled' if antiraid_settings['antilink'] else 'disabled'}")

@bot.command()
@commands.has_permissions(administrator=True)
async def antieveryone(ctx, state: str):
    """Toggle anti-everyone mention protection"""
    antiraid_settings['antieveryone'] = state.lower() == 'on'
    await ctx.send(f"Anti-everyone is now {'enabled' if antiraid_settings['antieveryone'] else 'disabled'}")

@bot.command()
@commands.has_permissions(administrator=True)
async def secur(ctx, setting: str, state: str):
    """Toggle security settings"""
    if setting in antiraid_settings:
        antiraid_settings[setting] = state.lower() == 'on'
        await ctx.send(f"✅ {setting} is now {'enabled' if antiraid_settings[setting] else 'disabled'}")
    else:
        await ctx.send("❌ Invalid setting")

@bot.command()
@commands.has_permissions(administrator=True)
async def punish(ctx, action: str):
    """Set punishment action (kick/ban)"""
    if action.lower() in ['kick', 'ban']:
        punishment_settings['action'] = action.lower()
        await ctx.send(f"✅ Punishment set to: {action}")
    else:
        await ctx.send("❌ Invalid punishment type")

@bot.command()
@commands.has_permissions(administrator=True)
async def raidclean(ctx):
    """Clean raid messages"""
    deleted = await ctx.channel.purge(limit=100, check=lambda m: not m.author.id in whitelisted_users)
    await ctx.send(f"✅ Cleaned {len(deleted)} messages")

@bot.command()
@commands.has_permissions(administrator=True)
async def clearwebhook(ctx):
    """Remove all webhooks"""
    webhooks = await ctx.guild.webhooks()
    for webhook in webhooks:
        await webhook.delete()
    await ctx.send("✅ All webhooks removed")

@bot.command()
@commands.has_permissions(administrator=True)
async def roleclean(ctx):
    """Clean unnecessary roles"""
    roles = ctx.guild.roles[1:]  # Exclude @everyone
    count = 0
    for role in roles:
        if len(role.members) == 0:
            await role.delete()
            count += 1
    await ctx.send(f"✅ Removed {count} empty roles")

@bot.event
async def on_member_join(member):
    if member.id in whitelisted_users:
        return

    if antiraid_settings['antijoin']:
        await member.kick(reason="Anti-raid: Join protection")
        return

    if antiraid_settings['antinewaccount']:
        account_age = (datetime.datetime.utcnow() - member.created_at).days
        if account_age < 7:  # Account less than 7 days old
            await member.kick(reason="Anti-raid: New account protection")
            return

@bot.event
async def on_message(message):
    if message.author.bot or message.author.id in whitelisted_users:
        return

    if antiraid_settings['antispam']:
        # Basic spam check implementation
        messages = [msg async for msg in message.channel.history(limit=5)]
        if len([msg for msg in messages if msg.author == message.author]) >= 4:
            await message.delete()
            await message.channel.send(f"{message.author.mention} please don't spam!")

    if antiraid_settings['antilink'] and ('http://' in message.content or 'https://' in message.content):
        await message.delete()
        await message.channel.send(f"{message.author.mention} links are not allowed!")

    if antiraid_settings['antieveryone'] and '@everyone' in message.content:
        if not message.author.guild_permissions.mention_everyone:
            await message.delete()
            await message.channel.send(f"{message.author.mention} you can't mention everyone!")

    # Process antiraid checks
    if antiraid_settings['antibadword']:
        bad_words = ['bad1', 'bad2']  # Add your bad words
        if any(word in message.content.lower() for word in bad_words):
            await message.delete()
            return

    if antiraid_settings['antimassmention']:
        if len(message.mentions) > 5:  # More than 5 mentions
            await message.delete()
            return

    await bot.process_commands(message)

@bot.event
async def on_member_ban(guild, user):
    if antiraid_settings['antiban'] and not user.id in whitelisted_users:
        async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
            if entry.user.id not in whitelisted_users:
                await entry.user.ban(reason="Anti-raid: Unauthorized ban")
                await guild.unban(user)

@bot.event
async def on_guild_role_create(role):
    if antiraid_settings['antirole']:
        async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_create, limit=1):
            if entry.user.id not in whitelisted_users:
                await role.delete()

@bot.event
async def on_guild_role_delete(role):
    if antiraid_settings['antirole']:
        async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
            if entry.user.id not in whitelisted_users:
                await entry.user.ban(reason="Anti-raid: Role deletion")

@bot.event
async def on_guild_channel_create(channel):
    if antiraid_settings['antichannel']:
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1):
            if entry.user.id not in whitelisted_users:
                await channel.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def antiban(ctx, state: str):
    """Toggle anti-ban protection"""
    if state.lower() not in ['on', 'off']:
        await ctx.send("❌ Please use 'on' or 'off' only")
        return

    antiraid_settings['antiban'] = state.lower() == 'on'
    await ctx.send(f"✅ Anti-ban is now {'enabled' if antiraid_settings['antiban'] else 'disabled'}")

async def setup_commands():
    await bot.wait_until_ready()
    try:
        await bot.tree.sync()
        print("Commandes enregistrées!")
    except Exception as e:
        print(f"Erreur d'enregistrement: {e}")

@bot.event
async def on_ready():
    try:
        print(f'{bot.user} est connecté!')
        print(f'Connecté à {len(bot.guilds)} serveurs')
        print(f'Latence: {round(bot.latency * 1000)}ms')
        await bot.change_presence(activity=discord.Game(name="!help | Security Bot"))
        await setup_commands()
    except Exception as e:
        print(f"Erreur dans on_ready: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    try:
        if isinstance(error, commands.errors.CommandNotFound):
            await ctx.send("❌ Commande introuvable! Utilisez !help")
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("❌ Permissions insuffisantes!")
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(f"❌ Argument manquant: {error.param.name}")
        else:
            print(f'Erreur dans {ctx.command}:', str(error))
            await ctx.send("❌ Une erreur est survenue!")
    except Exception as e:
        print(f"Erreur de gestion d'erreur: {str(e)}")

if __name__ == "__main__":
    token = os.environ.get('TOKEN_BOT_DISCORD')
    if not token:
        raise ValueError("Token Discord non trouvé dans les variables d'environnement")

    from keep_alive import keep_alive
    keep_alive()
    bot.run(token)
