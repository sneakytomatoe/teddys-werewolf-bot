def wolf_count_for(player_count: int) -> int:
    return max(1, player_count // 4)

MIN_PLAYERS = 6
MAX_PLAYERS = 20

# werewolf_bot.py
import os
import random
import asyncio
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
        "https://media.discordapp.net/attachments/1471964301051826382/1472005675662970981/ww_villager_lawyer.png?ex=6990ff9d&is=698fae1d&hm=ecfee4adb3720fc1f3a259b550af924ff48a8af6549df9a276d3b6765a5884c3&=&format=webp&quality=lossless"
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

# -----------------------
# Game state
# -----------------------
@dataclass
class Game:
    channel_id: int
    host_id: int
    started: bool = False
    players: List[int] = field(default_factory=list)
    roles: Dict[int, str] = field(default_factory=dict)
    role_image_chosen: Dict[int, str] = field(default_factory=dict)

games: Dict[int, Game] = {}

# -----------------------
# Helpers
# -----------------------
async def dm(user: discord.User | discord.Member, msg: str = "", *, embed: Optional[discord.Embed] = None):
    try:
        if embed is not None:
            await user.send(msg, embed=embed) if msg else await user.send(embed=embed)
        else:
            await user.send(msg)
    except discord.Forbidden:
        pass

def clamp_players(n: int) -> bool:
    return MIN_PLAYERS <= n <= MAX_PLAYERS

def choose_image_for_role(role: str) -> Optional[str]:
    options = ROLE_IMAGE_URLS.get(role, [])
    if not options:
        return None
    return random.choice(options)

def build_role_pool_for_n(n_players: int) -> Tuple[List[str], List[str]]:
    """Return (wolf_roles, villager_roles) sized to n_players using scaling rules."""
    wolves_n = wolf_count_for(n_players)
    villagers_n = n_players - wolves_n

    wolf_roles = pick_wolf_roles(wolves_n)
    villager_roles = pick_villager_roles(villagers_n)
    return wolf_roles, villager_roles

def roles_summary_lines(g: Game) -> List[str]:
    return [f"<@{uid}> — {g.roles.get(uid, 'unknown')}" for uid in g.players]

# -----------------------
# Commands
# -----------------------
@bot.command()
async def ww_create(ctx: commands.Context):
    if ctx.channel.id in games and games[ctx.channel.id].started:
        return await ctx.send("A game is already running in this channel.")
    games[ctx.channel.id] = Game(channel_id=ctx.channel.id, host_id=ctx.author.id)
    await ctx.send(f"🌕 Game created! Players join with `!ww_join` (or host uses `!ww_setplayers`).\n"
                   f"Supports **{MIN_PLAYERS}–{MAX_PLAYERS}** players.")

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

    ids: List[int] = []
    for m in members:
        if m.id not in ids:
            ids.append(m.id)

    if not clamp_players(len(ids)):
        return await ctx.send(f"Player count must be **{MIN_PLAYERS}–{MAX_PLAYERS}**. You provided **{len(ids)}**.")

    g.players = ids
    await ctx.send("✅ Player roster set:\n" + " ".join([f"<@{uid}>" for uid in g.players]))

@bot.command()
async def ww_players(ctx: commands.Context):
    g = games.get(ctx.channel.id)
    if not g:
        return await ctx.send("No game here. Create one with `!ww_create`.")
    if not g.players:
        return await ctx.send("No players yet.")
    await ctx.send("👥 Players:\n" + " ".join([f"<@{uid}>" for uid in g.players]) + f"\nTotal: **{len(g.players)}**")

@bot.command()
async def ww_start(ctx: commands.Context):
    g = games.get(ctx.channel.id)
    if not g:
        return await ctx.send("No game. Use `!ww_create`.")
    if ctx.author.id != g.host_id:
        return await ctx.send("Only the host can start.")
    if g.started:
        return await ctx.send("Already started.")
    if not clamp_players(len(g.players)):
        return await ctx.send(f"Need **{MIN_PLAYERS}–{MAX_PLAYERS}** players to start. Currently: **{len(g.players)}**.")

    # Build role pools
    wolf_roles, vill_roles = build_role_pool_for_n(len(g.players))
    wolves_n = len(wolf_roles)

    wolf_ids = random.sample(g.players, wolves_n)
    vill_ids = [uid for uid in g.players if uid not in wolf_ids]

    g.roles.clear()
    for uid, r in zip(wolf_ids, wolf_roles):
        g.roles[uid] = r
    for uid, r in zip(vill_ids, vill_roles):
        g.roles[uid] = r

    g.started = True

    wolf_list_mentions = ", ".join([f"<@{w}>" for w in wolf_ids])

    # DM host the full role list
    host_member = ctx.guild.get_member(g.host_id)
    if host_member:
        await dm(host_member, "📋 **Host Role List** (keep secret!)\n" + "\n".join(roles_summary_lines(g)))

    # DM each player their role + image
    failed = []
    for uid in g.players:
        member = ctx.guild.get_member(uid)
        if not member:
            continue

        role = g.roles[uid]
        if uid not in g.role_image_chosen:
            g.role_image_chosen[uid] = choose_image_for_role(role) or ""

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
            failed.append(uid)

    msg = f"✅ Roles assigned via DM! Wolves: **{wolves_n}** | Villagers: **{len(g.players)-wolves_n}**."
    if failed:
        msg += "\n⚠️ Could not DM: " + " ".join([f"<@{u}>" for u in failed]) + " (DMs disabled)."
    await ctx.send(msg)

@bot.command()
async def ww_resend_roles(ctx: commands.Context):
    """Host-only: resend all roles to everyone (useful if someone missed the DM)."""
    g = games.get(ctx.channel.id)
    if not g or not g.started:
        return await ctx.send("No active game.")
    if ctx.author.id != g.host_id:
        return await ctx.send("Only the host can use this.")
    # reuse start DM logic without reassigning roles
    wolf_ids = [uid for uid in g.players if is_wolf_role(g.roles.get(uid, ""))]
    wolf_list_mentions = ", ".join([f"<@{w}>" for w in wolf_ids])

    failed = []
    for uid in g.players:
        member = ctx.guild.get_member(uid)
        if not member:
            continue
        role = g.roles.get(uid, "unknown")
        if uid not in g.role_image_chosen:
            g.role_image_chosen[uid] = choose_image_for_role(role) or ""
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
            failed.append(uid)

    await ctx.send("📨 Re-sent roles. " + ("⚠️ DM failed for: " + " ".join([f"<@{u}>" for u in failed]) if failed else "✅ All DMs sent."))

@bot.command()
async def ww_end(ctx: commands.Context):
    g = games.get(ctx.channel.id)
    if not g:
        return await ctx.send("No game to end.")
    if ctx.author.id != g.host_id:
        return await ctx.send("Only the host can end the game.")
    del games[ctx.channel.id]
    await ctx.send("Game ended. You can `!ww_create` to start a new one.")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (id={bot.user.id})")

bot.run(TOKEN)
