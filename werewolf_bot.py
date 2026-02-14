# werewolf_bot.py
import os
import random
import asyncio
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------
# Roles
# -----------------------
# Villager-side
UTENA = "utena"
MATCHMAKER = "matchmaker"
SNORLAX = "snorlax"
DOCTOR = "doctor"
DETECTIVE = "detective"
VILLAGE_IDIOT = "village_idiot"
LAWYER = "lawyer"
MOD_FAVORITE = "mods_favorite"
VILLAGER = "villager"

# Werewolf-side
STOIC_OMEGA = "stoic_omega"
SOFT_ALPHA = "soft_alpha"
NEEDY_BETA = "needy_beta"
LONER_ALPHA = "loner_alpha"

VILLAGER_SPECIALS = [UTENA, MATCHMAKER, SNORLAX, DOCTOR, DETECTIVE, VILLAGE_IDIOT, LAWYER, MOD_FAVORITE]

ROLE_DISPLAY = {
    UTENA: "Utena — If killed (day or night), immediately kills one player.",
    MATCHMAKER: "Matchmaker — Night 1: choose 2 lovers. If one dies, the other dies too.",
    SNORLAX: "Snorlax — If killed by wolves at night → wolves skip next night’s kill.",
    DOCTOR: "Doctor — Protect 1 player each night. Cannot protect same person twice in a row.",
    DETECTIVE: "Detective — Investigate 1 player each night. Told Innocent or Guilty.",
    VILLAGE_IDIOT: "Village Idiot — If executed → survives, role revealed, loses vote permanently. Dies normally at night.",
    LAWYER: "Lawyer — Each night defend 1 player. If executed next day → they survive. Does not stop night kills.",
    MOD_FAVORITE: "Mod’s Favorite — Vote counts as 2.",
    VILLAGER: "Villager — No ability.",
    STOIC_OMEGA: "Stoic Omega Werewolf — Every other night, nullify 1 player’s ability.",
    SOFT_ALPHA: "Soft Alpha Werewolf — Appears Innocent to Detective.",
    NEEDY_BETA: "Needy Beta Werewolf — Choose 1 player nightly. If that player is investigated → appears Guilty.",
    LONER_ALPHA: "Loner Alpha Werewolf — No special ability.",
}

def is_wolf_role(role: str) -> bool:
    return role in {STOIC_OMEGA, SOFT_ALPHA, NEEDY_BETA, LONER_ALPHA}


# -----------------------
# Role images (URLs)
# -----------------------
ROLE_IMAGE_URLS = {
    SOFT_ALPHA: [
        "https://media.discordapp.net/attachments/1471964301051826382/1472009887277125744/ww_wolf_softAlpha_1.png?ex=69910389&is=698fb209&hm=3d262b691377b87327c94bb7b947d6e9bb2e3441d3114da0550b56e5eae639f6&=&format=webp&quality=lossless",
        "https://media.discordapp.net/attachments/1471964301051826382/1472010096895856721/ww_wolf_softAlpha_2.png?ex=699103bb&is=698fb23b&hm=a9192f32ad509faaff0ac42d3049145400bb7a6c8097849989787b5b0281f7a9&=&format=webp&quality=lossless",
    ],
    STOIC_OMEGA: [
        "https://media.discordapp.net/attachments/1471964301051826382/1472008296360706341/ww_wolf_stoicOmega_1.png?ex=6991020e&is=698fb08e&hm=06d6200d8f2430a99e4e4c889580d33497c39b73991faa5b32f88796195e4948&=&format=webp&quality=lossless",
        "https://media.discordapp.net/attachments/1471964301051826382/1472008601315836095/ww_wolf_stoicOmega_2.png?ex=69910257&is=698fb0d7&hm=de228da91390700b707121d02d12f0eafba73cc21c2bf407f507b674c3750030&=&format=webp&quality=lossless",
    ],
    LONER_ALPHA: [
        "https://media.discordapp.net/attachments/1471964301051826382/1472010682814697543/ww_wolf_lonerAlpha.png?ex=69910447&is=698fb2c7&hm=9fa6b28b7050c8e86fa1a69e7ec267e643fa82ef2b2f5e5d8081c5e742ebd47b&=&format=webp&quality=lossless",
    ],
    NEEDY_BETA: [
        "https://media.discordapp.net/attachments/1471964301051826382/1472009519906291756/ww_wolf_needyBeta.png?ex=69910332&is=698fb1b2&hm=003883d24dce4cdfb164a1bfcd7fb070075517bc0c1a0c84a285d2b646e7c7fa&=&format=webp&quality=lossless",
    ],
    VILLAGER: [
        "https://media.discordapp.net/attachments/1471964301051826382/1472005977401462837/ww_villager_villager_1.png?ex=6990ffe5&is=698fae65&hm=4ad29bdc910f5a1d04ed1ea8a7b37b86db1594660e71a2d601ba77239c3ec2f9&=&format=webp&quality=lossless",
        "https://media.discordapp.net/attachments/1471964301051826382/1472006218892705917/ww_villager_villager_2.png?ex=6991001f&is=698fae9f&hm=77c152b9c4278915b3ec731992f8124d9eb544b69f3f7b6bc649f0d01f16e539&=&format=webp&quality=lossless",
        "https://media.discordapp.net/attachments/1471964301051826382/1472006416599355544/ww_villager_villager_3.png?ex=6991004e&is=698faece&hm=63bdaedd508889554bcc8ecfe1c97a9eebf14a280867a5da6563b537f6af0e88&=&format=webp&quality=lossless",
        "https://media.discordapp.net/attachments/1471964301051826382/1472007144273350798/ww_villager_villager_4.png?ex=699100fb&is=698faf7b&hm=d1efc832b3b08959d4f0f7c1c14201d495d2a2803b398fe8d870edb7c2c4b9fd&=&format=webp&quality=lossless",
    ],
    LAWYER: [
        "https://media.discordapp.net/attachments/1471964301051826382/1472005675662970981/ww_villager_lawyer.png?ex=6990ff9d&is=698fae1d&hm=ecfee4adb3720fc1f3a259b550af924ff48a8af6549df9a276d3b6765a5884c3&=&format=webp&quality=lossless",
    ],
    VILLAGE_IDIOT: [
        "https://media.discordapp.net/attachments/1471964301051826382/1472005158115348591/ww_villager_villageIdiot.png?ex=6990ff22&is=698fada2&hm=63e9bd79940a821dd7143f332ba4ee5949ea48476831be9cb1ecb88c36113592&=&format=webp&quality=lossless",
    ],
    DETECTIVE: [
        "https://media.discordapp.net/attachments/1471964301051826382/1472003772363309187/ww_villager_detective.png?ex=6990fdd7&is=698fac57&hm=c932b3daf5c2f61142dfecad1500f241ff5fe866d9667164c7be97948839683e&=&format=webp&quality=lossless",
    ],
    DOCTOR: [
        "https://media.discordapp.net/attachments/1471964301051826382/1472001767947636846/ww_villager_doctor.png?ex=6990fbf9&is=698faa79&hm=ae042aa1eb674f4a3faeb8f1bea8ce48f3cc827b9bfba2d44be66cb4dca00098&=&format=webp&quality=lossless",
    ],
    SNORLAX: [
        "https://media.discordapp.net/attachments/1471964301051826382/1472000747460890655/ww_villager_snorlax.png?ex=6990fb06&is=698fa986&hm=834439434533ae98f23031fb58c380d8f8efee1fc95009ff3e1f446950a10edb&=&format=webp&quality=lossless",
    ],
    MATCHMAKER: [
        "https://media.discordapp.net/attachments/1471964301051826382/1471999193756340489/ww_villager_matchmaker.png?ex=6990f994&is=698fa814&hm=cc18261f5c4cc0a40abc02a3ab07d42c173ec92ce7d58937b9276a222c4bd96b&=&format=webp&quality=lossless",
    ],
    UTENA: [
        "https://media.discordapp.net/attachments/1471964301051826382/1471997866552590438/ww_villager_utena.png?ex=6990f857&is=698fa6d7&hm=b169771ed29ee38e2014d4d1b48a583d0866204d24bbb607203248089faa94a6&=&format=webp&quality=lossless",
    ],
    MOD_FAVORITE: [
        "https://media.discordapp.net/attachments/1471964301051826382/1472007489032814702/ww_villager_modsFav.png?ex=6991014d&is=698fafcd&hm=751e9ede88d1307ad47802bafd8c593762532444679821796d3d2fcd7bf34413&=&format=webp&quality=lossless",
    ],
}


# -----------------------
# Game state
# -----------------------
@dataclass
class Game:
    channel_id: int
    host_id: int
    started: bool = False
    phase: str = "lobby"  # lobby, night, day, vote

    players: List[int] = field(default_factory=list)
    alive: Set[int] = field(default_factory=set)
    roles: Dict[int, str] = field(default_factory=dict)

    # Lock-in per-player chosen image URL
    role_image_chosen: Dict[int, str] = field(default_factory=dict)

    # Private role channels (created in guild, unlocked on game end)
    private_category_id: Optional[int] = None
    role_channels: Dict[str, int] = field(default_factory=dict)

    # Lovers (Matchmaker)
    lovers: Optional[Tuple[int, int]] = None
    matchmaker_used: bool = False

    # Village Idiot
    idiot_revealed: bool = False
    idiot_no_vote: Set[int] = field(default_factory=set)

    # Snorlax effect
    wolves_skip_next_night_kill: bool = False

    # Night count
    night_num: int = 0
    # Host-controlled night step (0=not started, 1..7 phases)
    night_step: int = 0

    # Night actions
    wolf_votes: Dict[int, int] = field(default_factory=dict)
    doctor_target: Optional[int] = None
    doctor_last_target: Optional[int] = None
    lawyer_target: Optional[int] = None
    detective_target: Optional[int] = None

    omega_nullify_target: Optional[int] = None
    needy_mark_target: Optional[int] = None

    # Day votes
    day_votes: Dict[int, int] = field(default_factory=dict)

    # Execution protection from Lawyer (applies to next day execution only)
    pending_lawyer_defense: Optional[int] = None

    # Utena revenge
    revenge_pending_for: Optional[int] = None
    revenge_window_task: Optional[asyncio.Task] = None

    def wolves_alive(self) -> List[int]:
        return [uid for uid in self.alive if is_wolf_role(self.roles.get(uid, ""))]

    def villagers_alive(self) -> List[int]:
        return [uid for uid in self.alive if not is_wolf_role(self.roles.get(uid, ""))]

games: Dict[int, Game] = {}

# Stores the last unlocked category per channel so we can delete it when a new game starts.
last_game_category_by_channel: Dict[int, int] = {}

ROLE_CHAT_KEYS = {
    'wolves': 'wolves-den',
    'doctor': 'doctor-room',
    'lawyer': 'lawyer-room',
    'detective': 'detective-room',
    'matchmaker': 'matchmaker-room',
    'omega': 'omega-room',
    'beta': 'beta-room',
    'lovers': 'lovers-room',
}

async def create_role_chat_category_for(channel: discord.TextChannel, g: Game) -> Optional[discord.CategoryChannel]:
    if not channel.guild:
        return None
    guild = channel.guild
    if g.private_category_id:
        cat = guild.get_channel(g.private_category_id)
        if isinstance(cat, discord.CategoryChannel):
            return cat
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
    }
    name = f"werewolf-game-{channel.id}"
    cat = await guild.create_category(name=name, overwrites=overwrites)
    g.private_category_id = cat.id
    return cat

async def ensure_role_channel_for(channel: discord.TextChannel, g: Game, key: str, member_ids: List[int]) -> Optional[discord.TextChannel]:
    if not channel.guild:
        return None
    guild = channel.guild
    cat = await create_role_chat_category_for(channel, g)
    if not cat:
        return None
    if key in g.role_channels:
        ch = guild.get_channel(g.role_channels[key])
        if isinstance(ch, discord.TextChannel):
            return ch
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
    }
    host = guild.get_member(g.host_id)
    if host:
        overwrites[host] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
    for uid in member_ids:
        m = guild.get_member(uid)
        if m:
            overwrites[m] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
    name = ROLE_CHAT_KEYS.get(key, f"role-{key}")
    ch = await guild.create_text_channel(name=name, category=cat, overwrites=overwrites)
    g.role_channels[key] = ch.id
    return ch

async def unlock_game_channels_for(channel: discord.TextChannel, g: Game):
    """Unlock role channels read-only for everyone so you can read the history after the game."""
    if not channel.guild:
        return
    guild = channel.guild
    # Unlock category
    if g.private_category_id:
        cat = guild.get_channel(g.private_category_id)
        if isinstance(cat, discord.CategoryChannel):
            ow = cat.overwrites
            ow[guild.default_role] = discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=False)
            await cat.edit(overwrites=ow)
            last_game_category_by_channel[channel.id] = cat.id
    # Unlock each channel
    for key, cid in list(g.role_channels.items()):
        ch = guild.get_channel(cid)
        if isinstance(ch, discord.TextChannel):
            ow = ch.overwrites
            ow[guild.default_role] = discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=False)
            await ch.edit(overwrites=ow)


# -----------------------
# Helpers
# -----------------------
async def dm(user: discord.User | discord.Member, msg: str):
    try:
        await user.send(msg)
    except discord.Forbidden:
        pass

async def announce(channel: discord.TextChannel, msg: str):
    await channel.send(msg)

def tally(votes: Dict[int, int]) -> Optional[int]:
    if not votes:
        return None
    counts: Dict[int, int] = {}
    for target in votes.values():
        counts[target] = counts.get(target, 0) + 1
    maxv = max(counts.values())
    winners = [t for t, c in counts.items() if c == maxv]
    if len(winners) != 1:
        return None
    return winners[0]

def check_win(g: Game) -> Optional[str]:
    wolves = len(g.wolves_alive())
    villagers = len(g.villagers_alive())
    if wolves == 0 and g.started:
        return "✅ **Villagers win!** All werewolves are dead."
    if wolves >= villagers and g.started:
        return "🐺 **Werewolves win!** Wolves equal/outnumber villagers."
    return None

def pick_wolf_roles(n: int) -> List[str]:
    pool = (
        [STOIC_OMEGA, STOIC_OMEGA] +
        [SOFT_ALPHA, SOFT_ALPHA] +
        [NEEDY_BETA] +
        [LONER_ALPHA, LONER_ALPHA, LONER_ALPHA, LONER_ALPHA]
    )
    roles = []
    while len(roles) < n:
        r = random.choice(pool)
        if r == NEEDY_BETA and roles.count(NEEDY_BETA) >= 1:
            continue
        if r == STOIC_OMEGA and roles.count(STOIC_OMEGA) >= 2:
            continue
        if r == SOFT_ALPHA and roles.count(SOFT_ALPHA) >= 2:
            continue
        roles.append(r)
    random.shuffle(roles)
    return roles

def pick_villager_roles(n: int) -> List[str]:
    specials = VILLAGER_SPECIALS.copy()
    random.shuffle(specials)
    chosen: List[str] = []
    k = random.choice([2, 3, 3, 4, 4, 5])
    k = min(k, n, len(specials))
    chosen.extend(specials[:k])
    while len(chosen) < n:
        chosen.append(VILLAGER)
    random.shuffle(chosen)
    return chosen

async def kill_player(g: Game, channel: discord.TextChannel, guild: discord.Guild, victim_id: int, cause: str):
    if victim_id not in g.alive:
        return

    g.alive.remove(victim_id)
    await announce(channel, f"💀 <@{victim_id}> died ({cause}).")

    # Snorlax effect: only if killed by wolves at night
    if g.roles.get(victim_id) == SNORLAX and cause == "wolf kill (night)":
        g.wolves_skip_next_night_kill = True
        await announce(channel, "😴 **Snorlax effect!** Wolves will **skip next night’s kill**.")

    # Lovers chain
    if g.lovers and victim_id in g.lovers:
        other = g.lovers[0] if g.lovers[1] == victim_id else g.lovers[1]
        if other in g.alive:
            g.alive.remove(other)
            await announce(channel, f"💔 Lovers’ bond! <@{other}> dies too.")
            await maybe_trigger_utena_revenge(g, channel, guild, other)

    # Utena revenge trigger
    await maybe_trigger_utena_revenge(g, channel, guild, victim_id)

async def maybe_trigger_utena_revenge(g: Game, channel: discord.TextChannel, guild: discord.Guild, dead_id: int):
    if g.roles.get(dead_id) != UTENA:
        return

    g.revenge_pending_for = dead_id
    utena_member = guild.get_member(dead_id)
    if utena_member:
        await dm(
            utena_member,
            "🔥 You are **UTENA** and you died. You may immediately kill ONE player.\n"
            "Reply in DM with: `!revenge @player`\n"
            "You have **30 seconds**. If you don’t choose, revenge is lost."
        )
    await announce(channel, "🔥 **Utena revenge triggers!** (Utena has 30 seconds to pick a target in DM.)")

    if g.revenge_window_task and not g.revenge_window_task.done():
        g.revenge_window_task.cancel()

    async def revenge_timeout():
        await asyncio.sleep(30)
        if g.revenge_pending_for == dead_id:
            g.revenge_pending_for = None
            await announce(channel, "⏳ Utena did not choose a revenge target in time.")

    g.revenge_window_task = asyncio.create_task(revenge_timeout())

def detective_result_for(g: Game, target_id: int) -> str:
    if g.needy_mark_target == target_id:
        return "Guilty"
    role = g.roles.get(target_id, "")
    if is_wolf_role(role):
        if role == SOFT_ALPHA:
            return "Innocent"
        return "Guilty"
    return "Innocent"

def omega_can_act_this_night(g: Game) -> bool:
    return g.night_num % 2 == 1

# -----------------------
# Commands (channel)
# -----------------------
@bot.command()
async def ww_create(ctx: commands.Context):
    # If a previous game left an unlocked archive category, delete it when starting a new one
    if ctx.guild and ctx.channel.id in last_game_category_by_channel:
        old_cat_id = last_game_category_by_channel.pop(ctx.channel.id, None)
        if old_cat_id:
            old_cat = ctx.guild.get_channel(old_cat_id)
            if isinstance(old_cat, discord.CategoryChannel):
                for ch in list(old_cat.channels):
                    try:
                        await ch.delete()
                    except Exception:
                        pass
                try:
                    await old_cat.delete()
                except Exception:
                    pass

    if ctx.channel.id in games and games[ctx.channel.id].phase != "lobby":
        return await ctx.send("A game is already running in this channel.")
    games[ctx.channel.id] = Game(channel_id=ctx.channel.id, host_id=ctx.author.id)
    await ctx.send("🌕 **Teddy’s Werewolf Bonanza** created!\nPlayers join with `!ww_join` (or host uses `!ww_setplayers`).")

@bot.command()
async def ww_join(ctx: commands.Context):
    g = games.get(ctx.channel.id)
    if not g:
        return await ctx.send("No game here. Create one with `!ww_create`.")
    if g.started:
        return await ctx.send("Game already started.")
    if ctx.author.id in g.players:
        return await ctx.send("You already joined.")
    g.players.append(ctx.author.id)
    await ctx.send(f"{ctx.author.mention} joined! ({len(g.players)} players)")

@bot.command()
async def ww_setplayers(ctx: commands.Context, *members: discord.Member):
    g = games.get(ctx.channel.id)
    if not g:
        return await ctx.send("No game here. Create one with `!ww_create`.")
    if ctx.author.id != g.host_id:
        return await ctx.send("Only the host can set the player list.")
    if g.started:
        return await ctx.send("Game already started.")

    ids = []
    for m in members:
        if m.id not in ids:
            ids.append(m.id)

    if len(ids) != 8:
        return await ctx.send(f"This ruleset needs **exactly 8 players**. You provided **{len(ids)}**.")

    g.players = ids
    await ctx.send("✅ Player roster set:\n" + " ".join([f"<@{uid}>" for uid in g.players]))

@bot.command()
async def ww_start(ctx: commands.Context):
    g = games.get(ctx.channel.id)
    if not g:
        return await ctx.send("No game. Use `!ww_create`.")
    if ctx.author.id != g.host_id:
        return await ctx.send("Only the host can start.")
    if g.started:
        return await ctx.send("Already started.")
    if len(g.players) != 8:
        return await ctx.send("This ruleset expects **exactly 8 players** (3 wolves, 5 villagers).")

    wolf_ids = random.sample(g.players, 3)
    vill_ids = [uid for uid in g.players if uid not in wolf_ids]

    wolf_roles = pick_wolf_roles(3)
    vill_roles = pick_villager_roles(5)

    g.roles = {}
    for uid, r in zip(wolf_ids, wolf_roles):
        g.roles[uid] = r
    for uid, r in zip(vill_ids, vill_roles):
        g.roles[uid] = r

    g.alive = set(g.players)
    g.started = True


    # Create private role chats (server channels) for coordination.
    # Hidden during the game, then unlocked read-only on !ww_end / win.
    channel = ctx.channel
    wolves = [uid for uid, role in g.roles.items() if is_wolf_role(role)]
    await ensure_role_channel_for(channel, g, 'wolves', wolves)
    role_to_key = {
        DOCTOR: 'doctor',
        LAWYER: 'lawyer',
        DETECTIVE: 'detective',
        MATCHMAKER: 'matchmaker',
        STOIC_OMEGA: 'omega',
        NEEDY_BETA: 'beta',
    }
    for role_name, key in role_to_key.items():
        members = [uid for uid, r in g.roles.items() if r == role_name]
        if members:
            await ensure_role_channel_for(channel, g, key, members)

    wolf_list_mentions = ", ".join([f"<@{w}>" for w in wolf_ids])

    # DM host the full role list (host-only info)
    role_lines = []
    for uid in g.players:
        role_lines.append(f"<@{uid}> — {g.roles.get(uid, 'unknown')}")
    host_member = ctx.guild.get_member(g.host_id)
    if host_member:
        try:
            await host_member.send("📋 **Host Role List** (keep secret!)\n" + "\n".join(role_lines))
        except discord.Forbidden:
            await ctx.send("⚠️ Could not DM the host the role list (host DMs may be disabled).")


    # DM roles (secret) with random (locked) image
    for uid in g.players:
        member = ctx.guild.get_member(uid)
        role = g.roles[uid]
        if not member:
            continue

        if uid not in g.role_image_chosen:
            options = ROLE_IMAGE_URLS.get(role, [])
            g.role_image_chosen[uid] = random.choice(options) if options else ""
        img_url = g.role_image_chosen[uid] or None

        embed = discord.Embed(
            title="🌕 Teddy's Werewolf Bonanza",
            description=f"🎭 You are:\n\n**{ROLE_DISPLAY.get(role, role)}**",
        )
        if img_url:
            embed.set_image(url=img_url)

        try:
            await member.send(embed=embed)
            if is_wolf_role(role):
                await member.send(f"🐺 Werewolves: {wolf_list_mentions}")
        except discord.Forbidden:
            await ctx.send(f"⚠️ Could not DM <@{uid}> (they may have DMs disabled).")

    await ctx.send("✅ Roles assigned (check DMs). Night begins in 3 seconds...")
    await asyncio.sleep(3)
    await start_night(ctx.channel, ctx.guild)

@bot.command()
async def ww_end(ctx: commands.Context):
    g = games.get(ctx.channel.id)
    if not g:
        return await ctx.send("No game to end.")
    if ctx.author.id != g.host_id:
        return await ctx.send("Only the host can end the game.")
    del games[ctx.channel.id]
    await ctx.send("Game ended.")

# -----------------------
# Phase Logic (Night/Day/Vote)
# -----------------------
async def notify_host(g: Game, guild: discord.Guild, msg: str):
    host = guild.get_member(g.host_id) if guild else None
    if host:
        await dm(host, msg)

async def night_prompt_step(g: Game, guild: discord.Guild, step: int):
    """Send DM prompts for a given night step.
    1=Matchmaker(N1), 2=Doctor, 3=Lawyer, 4=Detective, 5=Omega(if can), 6=Needy, 7=Wolves
    """
    if step == 1:
        if g.night_num != 1 or g.matchmaker_used:
            return
        for uid in [u for u in g.alive if g.roles.get(u) == MATCHMAKER]:
            m = guild.get_member(uid)
            if m:
                await dm(m, "💘 You are **Matchmaker**. Choose TWO lovers: `!match @p1 @p2`")
    elif step == 2:
        for uid in [u for u in g.alive if g.roles.get(u) == DOCTOR]:
            m = guild.get_member(uid)
            if m:
                extra = f"\n(Last protected: <@{g.doctor_last_target}>)" if g.doctor_last_target else ""
                await dm(m, "🩻 Protect ONE: `!protect @player`" + extra)
    elif step == 3:
        for uid in [u for u in g.alive if g.roles.get(u) == LAWYER]:
            m = guild.get_member(uid)
            if m:
                await dm(m, "👉 Defend ONE (execution-only): `!defend @player`")
    elif step == 4:
        for uid in [u for u in g.alive if g.roles.get(u) == DETECTIVE]:
            m = guild.get_member(uid)
            if m:
                await dm(m, "🔎 Investigate ONE: `!investigate @player`")
    elif step == 5:
        omegas = [u for u in g.alive if g.roles.get(u) == STOIC_OMEGA]
        if omegas and omega_can_act_this_night(g):
            for uid in omegas:
                m = guild.get_member(uid)
                if m:
                    await dm(m, "😼 Nullify ONE ability tonight: `!nullify @player` (only every other night)")
    elif step == 6:
        for uid in [u for u in g.alive if g.roles.get(u) == NEEDY_BETA]:
            m = guild.get_member(uid)
            if m:
                await dm(m, "🙏 Mark ONE: `!mark @player`")
    elif step == 7:
        for uid in g.wolves_alive():
            m = guild.get_member(uid)
            if m:
                await dm(m, "🐺 Vote kill target: `!kill @player` (DM). Majority required.")

async def resolve_night(g: Game, channel: discord.TextChannel, guild: discord.Guild):
    """Resolve all night actions and transition to day."""
    nullified = g.omega_nullify_target

    # Doctor resolve
    protected = None
    doctor_players = [u for u in g.alive if g.roles.get(u) == DOCTOR]
    if g.doctor_target and (nullified not in doctor_players):
        protected = g.doctor_target
        g.doctor_last_target = g.doctor_target

    # Lawyer resolve (execution-only)
    lawyer_players = [u for u in g.alive if g.roles.get(u) == LAWYER]
    if g.lawyer_target and (nullified not in lawyer_players):
        g.pending_lawyer_defense = g.lawyer_target
    else:
        g.pending_lawyer_defense = None

    # Detective resolve
    detective_players = [u for u in g.alive if g.roles.get(u) == DETECTIVE]
    if g.detective_target and (nullified not in detective_players):
        result = detective_result_for(g, g.detective_target)
        for uid in detective_players:
            m = guild.get_member(uid)
            if m:
                await dm(m, f"🔎 Result for <@{g.detective_target}>: **{result.upper()}**")
        await notify_host(g, guild, f"🔎 Detective investigated <@{g.detective_target}> → **{result.upper()}**")

    # Wolves kill
    if g.wolves_skip_next_night_kill:
        g.wolves_skip_next_night_kill = False
        await announce(channel, "😴 Wolves skip the kill tonight (Snorlax effect).")
        await notify_host(g, guild, "😴 Wolves kill skipped (Snorlax effect)." )
    else:
        target = tally(g.wolf_votes)
        if target and target in g.alive:
            if protected == target:
                await announce(channel, f"🩻 Doctor protected <@{target}> — kill blocked.")
                await notify_host(g, guild, f"🩻 Doctor protected <@{target}> — kill blocked.")
            else:
                await notify_host(g, guild, f"🐺 Wolves killed <@{target}>.")
                await kill_player(g, channel, guild, target, "wolf kill (night)")
        else:
            await announce(channel, "🌙 Wolves did not kill (no majority / no votes).")
            await notify_host(g, guild, "🌙 Wolves did not kill (no majority / no votes).")

async def start_night(channel: discord.TextChannel, guild: discord.Guild):
    g = games.get(channel.id)
    if not g:
        return

    g.phase = "night"
    g.night_num += 1
    g.night_step = 0  # host-controlled

    g.wolf_votes.clear()
    g.doctor_target = None
    g.lawyer_target = None
    g.detective_target = None
    g.omega_nullify_target = None
    g.needy_mark_target = None

    win = check_win(g)
    if win:
        await announce(channel, win)
        # Unlock role channels for everyone (read-only) so you can enjoy the history
        await unlock_game_channels_for(channel, g)
        games.pop(channel.id, None)
        return

    msg = "🌙 **Night phase**\n"
    msg += "Host will run night phases via DM: `!phase1` … `!phase7`, then `!night_end`.\n"
    if g.wolves_skip_next_night_kill:
        msg += "\n😴 **Snorlax effect active:** Wolves will **skip** tonight’s kill."
    await announce(channel, msg)

    await notify_host(
        g,
        guild,
        "🌙 Night started. Run phases in order (DM me):\n"
        "`!phase1` Matchmaker (Night 1 only)\n"
        "`!phase2` Doctor\n`!phase3` Lawyer\n`!phase4` Detective\n"
        "`!phase5` Stoic Omega (if applicable)\n`!phase6` Needy Beta (if applicable)\n"
        "`!phase7` Wolves choose kill\n\n"
        "When ready to resolve night actions: `!night_end`\n"
        "(You can also skip a phase if that role isn't in game.)"
    )
async def start_day(channel: discord.TextChannel, guild: discord.Guild):
    g = games.get(channel.id)
    if not g:
        return
    g.phase = "day"
    await announce(channel, "☀️ **Day phase**: discuss. Host can start voting via DM with `!vote_start`.")

    await notify_host(
        g,
        guild,
        "☀️ Day started. When ready, start voting with `!vote_start` (DM)."
    )
async def resolve_vote(g: Game, channel: discord.TextChannel, guild: discord.Guild):
    # Tally weighted votes
    counts: Dict[int, int] = {}
    for voter, target in g.day_votes.items():
        if voter not in g.alive:
            continue
        if voter in g.idiot_no_vote:
            continue
        weight = 2 if g.roles.get(voter) == MOD_FAVORITE else 1
        counts[target] = counts.get(target, 0) + weight

    if not counts:
        await announce(channel, "⚖️ No execution (no votes).")
        await notify_host(g, guild, "⚖️ No execution (no votes).")
        return await start_night(channel, guild)

    maxv = max(counts.values())
    winners = [t for t, c in counts.items() if c == maxv]
    if len(winners) != 1:
        await announce(channel, "⚖️ No execution (tie).")
        await notify_host(g, guild, "⚖️ No execution (tie).")
        return await start_night(channel, guild)

    executed = winners[0]
    if executed not in g.alive:
        await announce(channel, "⚖️ Execution failed (not alive).")
        await notify_host(g, guild, "⚖️ Execution failed (not alive).")
        return await start_night(channel, guild)

    if g.pending_lawyer_defense == executed:
        await announce(channel, f"🧑‍⚖️ Lawyer saved <@{executed}> from execution!")
        await notify_host(g, guild, f"🧑‍⚖️ Lawyer saved <@{executed}> from execution!")
        g.pending_lawyer_defense = None
        return await start_night(channel, guild)

    if g.roles.get(executed) == VILLAGE_IDIOT and not g.idiot_revealed:
        # Important interaction: if saved by Lawyer, reveal does NOT trigger.
        g.idiot_revealed = True
        g.idiot_no_vote.add(executed)
        await announce(channel, f"🤡 <@{executed}> survives! **Village Idiot revealed** and loses vote permanently.")
        await notify_host(g, guild, f"🤡 Village Idiot <@{executed}> survived execution; reveal triggered; vote removed.")
        g.pending_lawyer_defense = None
        return await start_night(channel, guild)

    g.pending_lawyer_defense = None
    await notify_host(g, guild, f"⚖️ Executed <@{executed}>.")
    await kill_player(g, channel, guild, executed, "execution (day)")

    win = check_win(g)
    if win:
        await announce(channel, win)
        await notify_host(g, guild, win)
        await unlock_game_channels_for(channel, g)
        games.pop(channel.id, None)
        return

    return await start_night(channel, guild)

async def start_vote(channel: discord.TextChannel, guild: discord.Guild):
    g = games.get(channel.id)
    if not g:
        return
    g.phase = "vote"
    g.day_votes.clear()
    await announce(channel, "🗳️ **Voting phase**: vote with `!vote @player`. Host ends voting via DM with `!vote_end`.")
    await notify_host(g, guild, "🗳️ Voting started. End voting with `!vote_end` (DM).")

# -----------------------
# DM Commands (Night abilities)
# -----------------------
# -----------------------
# DM Commands (Night abilities)
# -----------------------

def find_game_for_host(host_id: int) -> Optional[Game]:
    for game in games.values():
        if game.started and game.host_id == host_id:
            return game
    return None

def _night_step_applicable(g: Game, step: int) -> bool:
    # 1: Matchmaker (Night 1 only)
    if step == 1:
        if g.night_num != 1 or g.matchmaker_used:
            return False
        return any(uid in g.alive and g.roles.get(uid) == MATCHMAKER for uid in g.players)
    # 2: Doctor
    if step == 2:
        return any(uid in g.alive and g.roles.get(uid) == DOCTOR for uid in g.players)
    # 3: Lawyer
    if step == 3:
        return any(uid in g.alive and g.roles.get(uid) == LAWYER for uid in g.players)
    # 4: Detective
    if step == 4:
        return any(uid in g.alive and g.roles.get(uid) == DETECTIVE for uid in g.players)
    # 5: Stoic Omega (every other night)
    if step == 5:
        if not omega_can_act_this_night(g):
            return False
        return any(uid in g.alive and g.roles.get(uid) == STOIC_OMEGA for uid in g.players)
    # 6: Needy Beta
    if step == 6:
        return any(uid in g.alive and g.roles.get(uid) == NEEDY_BETA for uid in g.players)
    # 7: Wolves
    if step == 7:
        return len(g.wolves_alive()) > 0
    return True

def next_night_step(g: Game) -> int:
    step = max(0, g.night_step)
    for s in range(step + 1, 8):
        if _night_step_applicable(g, s):
            return s
    return 7

def find_game_for_user(uid: int) -> Optional[Game]:
    for game in games.values():
        if uid in game.players and game.started:
            return game
    return None


def _resolve_channel_and_guild(g: Game):
    channel = bot.get_channel(g.channel_id)
    if isinstance(channel, discord.TextChannel):
        return channel, channel.guild
    return None, None

@bot.command()
async def host_roles(ctx: commands.Context):
    """DM-only: host can request the full role list again."""
    if ctx.guild is not None:
        return
    g = find_game_for_user(ctx.author.id)
    if not g or ctx.author.id != g.host_id:
        return await ctx.send("Host-only DM command.")
    channel, guild = _resolve_channel_and_guild(g)
    if not guild:
        return await ctx.send("Could not resolve guild/channel.")
    role_lines = [f"<@{uid}> — {g.roles.get(uid, 'unknown')}" for uid in g.players]
    await ctx.send("📋 **Host Role List** (keep secret!)\n" + "\n".join(role_lines))


@bot.command()
async def status(ctx: commands.Context):
    """Host-only (DM): show current game status and which night actions are in."""
    if ctx.guild is not None:
        return
    g = find_game_for_host(ctx.author.id)
    if not g:
        return await ctx.send("No active game found where you are the host.")
    channel, guild = _resolve_channel_and_guild(g)
    if not channel or not guild:
        return await ctx.send("Could not resolve guild/channel.")

    wolves = g.wolves_alive()
    lines = []
    lines.append(f"🧭 **Status** — Phase: **{g.phase.upper()}** | Night: **{g.night_num}** | Night step: **{g.night_step}**")
    lines.append(f"🧑‍🤝‍🧑 Alive: **{len(g.alive)}/{len(g.players)}** | Wolves: **{len(wolves)}** | Villagers: **{len(g.villagers_alive())}**")

    if g.phase == "night":
        if g.night_num == 1 and any(g.roles.get(u)==MATCHMAKER for u in g.players):
            lines.append(f"💘 Lovers set: **{'Yes' if g.lovers else 'No'}**")
        if any(g.roles.get(u)==DOCTOR for u in g.players):
            dt = f"<@{g.doctor_target}>" if g.doctor_target else "(none)"
            lines.append(f"🩻 Doctor target: {dt}")
        if any(g.roles.get(u)==LAWYER for u in g.players):
            lt = f"<@{g.lawyer_target}>" if g.lawyer_target else "(none)"
            lines.append(f"⚖️ Lawyer defend: {lt}")
        if any(g.roles.get(u)==DETECTIVE for u in g.players):
            it = f"<@{g.detective_target}>" if g.detective_target else "(none)"
            lines.append(f"🔎 Detective investigate: {it}")
        if any(g.roles.get(u)==STOIC_OMEGA for u in g.players):
            ot = f"<@{g.omega_nullify_target}>" if g.omega_nullify_target else "(none)"
            lines.append(f"😼 Omega nullify: {ot} (can act tonight: {'Yes' if omega_can_act_this_night(g) else 'No'})")
        if any(g.roles.get(u)==NEEDY_BETA for u in g.players):
            nt = f"<@{g.needy_mark_target}>" if g.needy_mark_target else "(none)"
            lines.append(f"🙏 Needy mark: {nt}")
        lines.append(f"🐺 Wolf votes: **{len(g.wolf_votes)}/{len(wolves)}**")

    if g.phase == "vote":
        lines.append(f"🗳️ Day votes received: **{len(g.day_votes)}**")

    await ctx.send("\n".join(lines))

@bot.command()
async def next(ctx: commands.Context):
    """Host-only (DM): advance to the next applicable night phase."""
    if ctx.guild is not None:
        return
    g = find_game_for_host(ctx.author.id)
    if not g or ctx.author.id != g.host_id:
        return await ctx.send("Host-only DM command.")
    if g.phase != "night":
        return await ctx.send("`!next` is for **night phases**. Use `!vote_start` / `!vote_end` for day.")
    step = next_night_step(g)
    return await _host_run_phase(ctx, step)

@bot.command()
async def skip(ctx: commands.Context):
    """Host-only (DM): skip the current night phase and jump to the next one."""
    if ctx.guild is not None:
        return
    g = find_game_for_host(ctx.author.id)
    if not g or ctx.author.id != g.host_id:
        return await ctx.send("Host-only DM command.")
    if g.phase != "night":
        return await ctx.send("You can only skip during the **night**.")
    # move forward at least one step
    g.night_step = max(0, g.night_step)
    step = next_night_step(g)
    return await _host_run_phase(ctx, step)

@bot.command()
async def phase1(ctx: commands.Context):
    if ctx.guild is not None:
        return
    await _host_run_phase(ctx, 1)

@bot.command()
async def phase2(ctx: commands.Context):
    if ctx.guild is not None:
        return
    await _host_run_phase(ctx, 2)

@bot.command()
async def phase3(ctx: commands.Context):
    if ctx.guild is not None:
        return
    await _host_run_phase(ctx, 3)

@bot.command()
async def phase4(ctx: commands.Context):
    if ctx.guild is not None:
        return
    await _host_run_phase(ctx, 4)

@bot.command()
async def phase5(ctx: commands.Context):
    if ctx.guild is not None:
        return
    await _host_run_phase(ctx, 5)

@bot.command()
async def phase6(ctx: commands.Context):
    if ctx.guild is not None:
        return
    await _host_run_phase(ctx, 6)

@bot.command()
async def phase7(ctx: commands.Context):
    if ctx.guild is not None:
        return
    await _host_run_phase(ctx, 7)

async def _host_run_phase(ctx: commands.Context, step: int):
    g = find_game_for_user(ctx.author.id)
    if not g or ctx.author.id != g.host_id:
        return await ctx.send("Host-only DM command.")
    if g.phase != "night":
        return await ctx.send("You can only run phases during the **night**.")
    channel, guild = _resolve_channel_and_guild(g)
    if not channel or not guild:
        return await ctx.send("Could not resolve guild/channel.")
    g.night_step = step
    await night_prompt_step(g, guild, step)
    await ctx.send(f"✅ Sent prompts for **phase {step}**.")

@bot.command()
async def night_end(ctx: commands.Context):
    """DM-only: host resolves the night immediately."""
    if ctx.guild is not None:
        return
    g = find_game_for_user(ctx.author.id)
    if not g or ctx.author.id != g.host_id:
        return await ctx.send("Host-only DM command.")
    if g.phase != "night":
        return await ctx.send("Not currently night.")
    channel, guild = _resolve_channel_and_guild(g)
    if not channel or not guild:
        return await ctx.send("Could not resolve guild/channel.")
    await ctx.send("🌙 Resolving night now…")
    await resolve_night(g, channel, guild)

    win = check_win(g)
    if win:
        await announce(channel, win)
        await notify_host(g, guild, win)
        await unlock_game_channels_for(channel, g)
        games.pop(channel.id, None)
        return

    await start_day(channel, guild)

@bot.command()
async def vote_start(ctx: commands.Context):
    """DM-only: host starts voting during the day."""
    if ctx.guild is not None:
        return
    g = find_game_for_user(ctx.author.id)
    if not g or ctx.author.id != g.host_id:
        return await ctx.send("Host-only DM command.")
    channel, guild = _resolve_channel_and_guild(g)
    if not channel or not guild:
        return await ctx.send("Could not resolve guild/channel.")
    if g.phase != "day":
        return await ctx.send("You can only start voting during the **day**.")
    await start_vote(channel, guild)
    await ctx.send("🗳️ Voting started in the channel.")

@bot.command()
async def vote_end(ctx: commands.Context):
    """DM-only: host ends voting and resolves execution."""
    if ctx.guild is not None:
        return
    g = find_game_for_user(ctx.author.id)
    if not g or ctx.author.id != g.host_id:
        return await ctx.send("Host-only DM command.")
    channel, guild = _resolve_channel_and_guild(g)
    if not channel or not guild:
        return await ctx.send("Could not resolve guild/channel.")
    if g.phase != "vote":
        return await ctx.send("Not currently voting.")
    await ctx.send("🗳️ Resolving vote now…")
    await resolve_vote(g, channel, guild)


@bot.command()
async def match(ctx: commands.Context, p1: Optional[discord.User] = None, p2: Optional[discord.User] = None):
    if ctx.guild is not None:
        return
    g = find_game_for_user(ctx.author.id)
    if not g or g.phase != "night" or g.night_num != 1:
        return await ctx.send("Matchmaker only acts on Night 1.")
    if g.roles.get(ctx.author.id) != MATCHMAKER:
        return await ctx.send("You are not Matchmaker.")
    if not p1 or not p2 or p1.id == p2.id:
        return await ctx.send("Usage: `!match @p1 @p2`")
    if p1.id not in g.alive or p2.id not in g.alive:
        return await ctx.send("Both must be alive.")
    g.lovers = (p1.id, p2.id)


    # Create lovers room in the server (private during game)
    game_channel = bot.get_channel(g.channel_id)
    if isinstance(game_channel, discord.TextChannel):
        await ensure_role_channel_for(game_channel, g, 'lovers', [p1.id, p2.id])
    g.matchmaker_used = True
    channel, guild = _resolve_channel_and_guild(g)
    if guild:
        await notify_host(g, guild, f"💘 Matchmaker set lovers: <@{p1.id}> + <@{p2.id}>.")
    await ctx.send(f"💘 Lovers set: <@{p1.id}> and <@{p2.id}>.")

@bot.command()
async def protect(ctx: commands.Context, target: Optional[discord.User] = None):
    if ctx.guild is not None:
        return
    g = find_game_for_user(ctx.author.id)
    if not g or g.phase != "night":
        return await ctx.send("Not night.")
    if g.roles.get(ctx.author.id) != DOCTOR:
        return await ctx.send("You are not Doctor.")
    if not target or target.id not in g.alive:
        return await ctx.send("Usage: `!protect @alivePlayer`")
    if g.doctor_last_target == target.id:
        return await ctx.send("Cannot protect same person twice in a row.")
    g.doctor_target = target.id
    channel, guild = _resolve_channel_and_guild(g)
    if guild:
        await notify_host(g, guild, f"🩻 Doctor selected protect: <@{target.id}>.")
    await ctx.send(f"🩻 Protected: <@{target.id}>")

@bot.command()
async def defend(ctx: commands.Context, target: Optional[discord.User] = None):
    if ctx.guild is not None:
        return
    g = find_game_for_user(ctx.author.id)
    if not g or g.phase != "night":
        return await ctx.send("Not night.")
    if g.roles.get(ctx.author.id) != LAWYER:
        return await ctx.send("You are not Lawyer.")
    if not target or target.id not in g.alive:
        return await ctx.send("Usage: `!defend @alivePlayer`")
    g.lawyer_target = target.id
    channel, guild = _resolve_channel_and_guild(g)
    if guild:
        await notify_host(g, guild, f"🧑‍⚖️ Lawyer selected defend: <@{target.id}>.")
    await ctx.send(f"🧑‍⚖️ Defending: <@{target.id}>")

@bot.command()
async def investigate(ctx: commands.Context, target: Optional[discord.User] = None):
    if ctx.guild is not None:
        return
    g = find_game_for_user(ctx.author.id)
    if not g or g.phase != "night":
        return await ctx.send("Not night.")
    if g.roles.get(ctx.author.id) != DETECTIVE:
        return await ctx.send("You are not Detective.")
    if not target or target.id not in g.alive:
        return await ctx.send("Usage: `!investigate @alivePlayer`")
    g.detective_target = target.id
    channel, guild = _resolve_channel_and_guild(g)
    if guild:
        await notify_host(g, guild, f"🔎 Detective selected investigate: <@{target.id}>.")
    await ctx.send(f"🔎 Investigating: <@{target.id}>")

@bot.command()
async def nullify(ctx: commands.Context, target: Optional[discord.User] = None):
    if ctx.guild is not None:
        return
    g = find_game_for_user(ctx.author.id)
    if not g or g.phase != "night":
        return await ctx.send("Not night.")
    if g.roles.get(ctx.author.id) != STOIC_OMEGA:
        return await ctx.send("You are not Stoic Omega.")
    if not omega_can_act_this_night(g):
        return await ctx.send("You can only nullify every other night (1,3,5,...).")
    if not target or target.id not in g.alive:
        return await ctx.send("Usage: `!nullify @alivePlayer`")
    g.omega_nullify_target = target.id
    channel, guild = _resolve_channel_and_guild(g)
    if guild:
        await notify_host(g, guild, f"😼 Stoic Omega selected nullify: <@{target.id}>.")
    await ctx.send(f"😼 Nullifying: <@{target.id}>")

@bot.command()
async def mark(ctx: commands.Context, target: Optional[discord.User] = None):
    if ctx.guild is not None:
        return
    g = find_game_for_user(ctx.author.id)
    if not g or g.phase != "night":
        return await ctx.send("Not night.")
    if g.roles.get(ctx.author.id) != NEEDY_BETA:
        return await ctx.send("You are not Needy Beta.")
    if not target or target.id not in g.alive:
        return await ctx.send("Usage: `!mark @alivePlayer`")
    g.needy_mark_target = target.id
    channel, guild = _resolve_channel_and_guild(g)
    if guild:
        await notify_host(g, guild, f"🙏 Needy Beta marked: <@{target.id}> (will appear Guilty if investigated).")
    await ctx.send(f"🙏 Marked: <@{target.id}>")

@bot.command()
async def kill(ctx: commands.Context, target: Optional[discord.User] = None):
    if ctx.guild is not None:
        return
    g = find_game_for_user(ctx.author.id)
    if not g or g.phase != "night":
        return await ctx.send("Not night.")
    if not is_wolf_role(g.roles.get(ctx.author.id, "")):
        return await ctx.send("You are not a werewolf.")
    if not target or target.id not in g.alive:
        return await ctx.send("Usage: `!kill @alivePlayer`")
    g.wolf_votes[ctx.author.id] = target.id
    channel, guild = _resolve_channel_and_guild(g)
    if guild:
        await notify_host(g, guild, f"🐺 Wolf <@{ctx.author.id}> voted to kill <@{target.id}>.")
    await ctx.send(f"🐺 Vote recorded for <@{target.id}>")

@bot.command()
async def revenge(ctx: commands.Context, target: Optional[discord.User] = None):
    if ctx.guild is not None:
        return
    g = find_game_for_user(ctx.author.id)
    if not g or g.revenge_pending_for != ctx.author.id:
        return await ctx.send("No revenge pending.")
    if not target or target.id not in g.alive:
        return await ctx.send("Usage: `!revenge @alivePlayer`")

    channel = bot.get_channel(g.channel_id)
    if not isinstance(channel, discord.TextChannel):
        g.revenge_pending_for = None
        return await ctx.send("Could not resolve game channel.")
    guild = channel.guild

    g.revenge_pending_for = None
    await kill_player(g, channel, guild, target.id, "Utena revenge")
    await ctx.send(f"🔥 Revenge executed on <@{target.id}>")

@bot.command()
async def vote(ctx: commands.Context, target: Optional[discord.Member] = None):
    g = games.get(ctx.channel.id)
    if not g or not g.started:
        return await ctx.send("No active game.")
    if g.phase != "vote":
        return await ctx.send("Not voting phase.")
    if ctx.author.id not in g.alive:
        return await ctx.send("You are dead.")
    if ctx.author.id in g.idiot_no_vote:
        return await ctx.send("🤡 You permanently lost your vote.")
    if not target or target.id not in g.alive:
        return await ctx.send("Usage: `!vote @alivePlayer`")
    g.day_votes[ctx.author.id] = target.id
    await ctx.send(f"{ctx.author.mention} voted for {target.mention}.")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (id={bot.user.id})")

bot.run(TOKEN)
