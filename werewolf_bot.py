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
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966298194837576/SoftAlpha_Werewolf_2.png?ex=6990daf1&is=698f8971&hm=8d4281e7b8ce5ef00307ca81a10ba183286461ed0f2687cef152cedfe814fc75&",
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966302842257642/SoftAlpha_Werewolf_1.png?ex=6990daf2&is=698f8972&hm=61773ce59146e5f6dc09d1a742353f8636b1e799e6d948ce936e8c538606338a&=&format=webp&quality=lossless",
    ],
    STOIC_OMEGA: [
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966307959308468/StoicOmega_Werewolf_1.png?ex=6990daf3&is=698f8973&hm=94b9b30f3a9c80fd0eb743abdcd5dd65caaa8a1fde039414658d380b882260b7&=&format=webp&quality=lossless",
        # NOTE: this link filename looks like Needy Beta, but kept as provided
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966327551033414/NeedyBeta_Werewolf_1.png?ex=6990daf8&is=698f8978&hm=e43ae26192ecb38d40f8551881a8d530ea11e959d3c0dd0121da4dd925f557f1&",
    ],
    LONER_ALPHA: [
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966312514195608/LonerAlpha_Werewolf_1.png?ex=6990daf4&is=698f8974&hm=254dddee1680af6fbdf1b4ac176474114b03072ac1f44c00857f8e06011cc701&",
    ],
    NEEDY_BETA: [
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966320240230470/NeedyBeta_Werewolf_2.png?ex=6990daf6&is=698f8976&hm=b4d4c6e437aea678565e0d3e4302496d7cf1e73115ed8f48fefe71c3cfc3db1b&=&format=webp&quality=lossless",
    ],
    VILLAGER: [
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966332055715900/Base_Villager_1.png?ex=6990daf9&is=698f8979&hm=58fe6472227607b135cb4ee1df806834940b0dbefee71eb4a9409920e1601a32&",
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966338795966760/Base_Villager_2.png?ex=6990dafa&is=698f897a&hm=7cb351d1fb6c9190bb21ae35293dd8d999b7d439146d6832b83cd08c963584b3&",
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966349721993337/Base_Villager_3.png?ex=6990dafd&is=698f897d&hm=9e11e6b658518e67afd894602b06cc00cc89deedfe8163b85989f7b2ee7fc67d&",
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966382144094228/Base_Villager_4.png?ex=6990db05&is=698f8985&hm=6f263abbc384ee4caf5980a81131eafa1b91815895236bfcc250ea92f3719cb9&=&format=webp&quality=lossless",
    ],
    LAWYER: [
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966388049412331/Lawyer_Villager_1.png?ex=6990db06&is=698f8986&hm=1da9520713ec0e41fd5900f992b513648e10fc02c1314501a0e1c407292da2e0&",
    ],
    VILLAGE_IDIOT: [
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966394886389862/Idiot_Villager_1.png?ex=6990db08&is=698f8988&hm=8f9f48e6d2e0b660d4d872d5a25cf48fb55c5fb07ed7ae5c354b0036e611a903&",
    ],
    DETECTIVE: [
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966402607972477/Detective_Villager_1.png?ex=6990db0a&is=698f898a&hm=b24088e9a4ff394deaf6d99b0d71f01f6165ce83bc18c9bd4adb3827f1151edd&",
    ],
    DOCTOR: [
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966410753446082/Doctor_Villager_1.png?ex=6990db0c&is=698f898c&hm=c198c2d459d7264645fb15e29851fb056dfe06c06b312298c3c5b12aa677667c&",
    ],
    SNORLAX: [
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966415555924172/Snorlax_Villager_1.png?ex=6990db0d&is=698f898d&hm=28c0c0774ec3094c2920b7da35ec86ab2d237a20cf2a3fbae5d0d3b7e135be77&",
    ],
    MATCHMAKER: [
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966421058851090/Matchmaker_Villager_1.png?ex=6990db0e&is=698f898e&hm=4172a8145c9fa711c2288b53f13d5147d652a43a8a6225684465d56e9f044682&",
    ],
    UTENA: [
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966424066162748/Utena_Villager_1.png?ex=6990db0f&is=698f898f&hm=70dc3b4bf21131340123052ace79bc7eb2a0e5a0417840b24d49259ceb7af8e9&",
    ],
    MOD_FAVORITE: [
        "https://cdn.discordapp.com/attachments/1471964301051826382/1471966343996899463/ModFav_Villager_1.png?ex=6990dafc&is=698f897c&hm=7f55d78f60054b55c423f792bf433872991f2c68c37487de1d21021590756567&",
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

    wolf_list_mentions = ", ".join([f"<@{w}>" for w in wolf_ids])

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
async def start_night(channel: discord.TextChannel, guild: discord.Guild):
    g = games.get(channel.id)
    if not g:
        return

    g.phase = "night"
    g.night_num += 1

    g.wolf_votes.clear()
    g.doctor_target = None
    g.lawyer_target = None
    g.detective_target = None
    g.omega_nullify_target = None
    g.needy_mark_target = None

    win = check_win(g)
    if win:
        await announce(channel, win)
        games.pop(channel.id, None)
        return

    msg = "🌙 **Night phase**\n"
    if g.night_num == 1:
        msg += "Order: Matchmaker (Night 1 only) → Doctor → Lawyer → Detective → Omega/Needy (if in game) → Wolves kill\n"
    else:
        msg += "Order: Doctor → Lawyer → Detective → Omega/Needy (if in game) → Wolves kill\n"

    if g.wolves_skip_next_night_kill:
        msg += "\n😴 **Snorlax effect active:** Wolves will **skip** tonight’s kill."
    await announce(channel, msg)

    # DM instructions
    if g.night_num == 1 and not g.matchmaker_used:
        for uid in [u for u in g.alive if g.roles.get(u) == MATCHMAKER]:
            m = guild.get_member(uid)
            if m:
                await dm(m, "💘 You are **Matchmaker**. Choose TWO lovers: `!match @p1 @p2`")

    for uid in [u for u in g.alive if g.roles.get(u) == DOCTOR]:
        m = guild.get_member(uid)
        if m:
            extra = f"\n(Last protected: <@{g.doctor_last_target}>)" if g.doctor_last_target else ""
            await dm(m, "🩻 Protect ONE: `!protect @player`" + extra)

    for uid in [u for u in g.alive if g.roles.get(u) == LAWYER]:
        m = guild.get_member(uid)
        if m:
            await dm(m, "👉 Defend ONE (execution-only): `!defend @player`")

    for uid in [u for u in g.alive if g.roles.get(u) == DETECTIVE]:
        m = guild.get_member(uid)
        if m:
            await dm(m, "🔎 Investigate ONE: `!investigate @player`")

    omegas = [u for u in g.alive if g.roles.get(u) == STOIC_OMEGA]
    if omegas and omega_can_act_this_night(g):
        for uid in omegas:
            m = guild.get_member(uid)
            if m:
                await dm(m, "😼 Nullify ONE ability tonight: `!nullify @player`")

    for uid in [u for u in g.alive if g.roles.get(u) == NEEDY_BETA]:
        m = guild.get_member(uid)
        if m:
            await dm(m, "🙏 Mark ONE: `!mark @player`")

    for uid in g.wolves_alive():
        m = guild.get_member(uid)
        if m:
            await dm(m, "🐺 Vote kill target: `!kill @player` (DM). Majority required.")

    await asyncio.sleep(60)

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

    # Wolves kill
    if g.wolves_skip_next_night_kill:
        g.wolves_skip_next_night_kill = False
        await announce(channel, "😴 Wolves skip the kill tonight (Snorlax effect).")
    else:
        target = tally(g.wolf_votes)
        if target and target in g.alive:
            if protected == target:
                await announce(channel, f"🩻 Doctor protected <@{target}> — kill blocked.")
            else:
                await kill_player(g, channel, guild, target, "wolf kill (night)")
        else:
            await announce(channel, "🌙 Wolves did not kill (no majority / no votes).")

    win = check_win(g)
    if win:
        await announce(channel, win)
        games.pop(channel.id, None)
        return

    await asyncio.sleep(2)
    await start_day(channel, guild)

async def start_day(channel: discord.TextChannel, guild: discord.Guild):
    g = games.get(channel.id)
    if not g:
        return
    g.phase = "day"
    await announce(channel, "☀️ **Day phase**: discuss. Voting begins in 60 seconds.")
    await asyncio.sleep(60)
    await start_vote(channel, guild)

async def start_vote(channel: discord.TextChannel, guild: discord.Guild):
    g = games.get(channel.id)
    if not g:
        return
    g.phase = "vote"
    g.day_votes.clear()
    await announce(channel, "🗳️ **Voting phase**: vote with `!vote @player` (45 seconds).")
    await asyncio.sleep(45)

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
        return await start_night(channel, guild)

    maxv = max(counts.values())
    winners = [t for t, c in counts.items() if c == maxv]
    if len(winners) != 1:
        await announce(channel, "⚖️ No execution (tie).")
        return await start_night(channel, guild)

    executed = winners[0]
    if executed not in g.alive:
        await announce(channel, "⚖️ Execution failed (not alive).")
        return await start_night(channel, guild)

    if g.pending_lawyer_defense == executed:
        await announce(channel, f"🧑‍⚖️ Lawyer saved <@{executed}> from execution!")
        g.pending_lawyer_defense = None
        return await start_night(channel, guild)

    if g.roles.get(executed) == VILLAGE_IDIOT and not g.idiot_revealed:
        g.idiot_revealed = True
        g.idiot_no_vote.add(executed)
        await announce(channel, f"🤡 <@{executed}> survives! **Village Idiot revealed** and loses vote permanently.")
        g.pending_lawyer_defense = None
        return await start_night(channel, guild)

    g.pending_lawyer_defense = None
    await kill_player(g, channel, guild, executed, "execution (day)")

    win = check_win(g)
    if win:
        await announce(channel, win)
        games.pop(channel.id, None)
        return

    return await start_night(channel, guild)

# -----------------------
# DM Commands (Night abilities)
# -----------------------
def find_game_for_user(uid: int) -> Optional[Game]:
    for game in games.values():
        if uid in game.players and game.started:
            return game
    return None

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
    g.matchmaker_used = True
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