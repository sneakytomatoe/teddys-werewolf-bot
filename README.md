# 🌕 Teddy’s Werewolf Bonanza 🐺
A fully automated Discord bot for running a flexible, host-controlled Werewolf game with secret roles, DM actions, and cinematic chaos.

---

# 🚀 Quick Start

In a Discord channel:

```
!ww_create
```

Add players:

```
!ww_setplayers @p1 @p2 @p3 @p4 @p5
```

Start:

```
!ww_start
```

The bot assigns roles, DMs everyone, and begins Night 1.

---

# 🛠 Setup

## Local Setup

1. Install Python 3.11+
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file:
   ```
   DISCORD_TOKEN=YOUR_BOT_TOKEN
   ```
4. Run:
   ```
   python werewolf_bot.py
   ```

---

## Railway Deployment

1. Upload:
   - `werewolf_bot.py`
   - `requirements.txt`
   - `README.md`
2. Add Environment Variable:
   ```
   DISCORD_TOKEN=YOUR_TOKEN
   ```
3. Set start command:
   ```
   python werewolf_bot.py
   ```

---

# ⚙️ Discord Developer Portal Setup

Enable:
- ✅ Message Content Intent
- ✅ Server Members Intent

Bot Permissions:
- View Channels
- Send Messages
- Embed Links

---

# 🎮 GAME FLOW

---

## 1️⃣ Create Game

In a channel:

```
!ww_create
```

The user who runs this becomes the **Host**.

---

## 2️⃣ Add Players

### Option A — Host sets roster

```
!ww_setplayers @p1 @p2 @p3 ...
```

Supports **5–20 players** (wolves scale automatically).

### Option B — Join lobby

Players type:

```
!ww_join
```

Host runs `!ww_start` when ready.

---

## 3️⃣ Start Game

Host:

```
!ww_start
```

The bot:
- Assigns roles
- DMs each player their role + image
- DMs wolves their teammates
- DMs host the full role list
- Begins Night 1

---

# 🌙 NIGHT PHASE (Host Controlled)

Host uses **DM commands** with the bot.

---

## Host Controls

Advance automatically:

```
!next
```

Skip current phase:

```
!skip
```

Show phase + submitted actions:

```
!status
```

Manual phase control:

```
!phase1  → Matchmaker (Night 1 only)
!phase2  → Doctor
!phase3  → Lawyer
!phase4  → Detective
!phase5  → Stoic Omega
!phase6  → Needy Beta
!phase7  → Wolves kill
```

End the night:

```
!night_end
```

Bot resolves:
- Protection
- Nullification
- Kill
- Lovers
- Utena revenge
- Win conditions

Then Day begins.

---

# ☀️ DAY PHASE

Players discuss in channel.

Host controls voting.

---

# 🗳️ VOTING

Start voting (Host DM):

```
!vote_start
```

Players vote (in channel):

```
!vote @player
```

End voting (Host DM):

```
!vote_end
```

Bot resolves execution and starts next Night.

---

# 🐺 PLAYER NIGHT ACTIONS (DM Only)

Matchmaker:

```
!match @p1 @p2
```

Doctor:

```
!protect @player
```

Lawyer:

```
!defend @player
```

Detective:

```
!investigate @player
```

Stoic Omega:

```
!nullify @player
```

Needy Beta:

```
!mark @player
```

Werewolves:

```
!kill @player
```

Utena (after death only):

```
!revenge @player
```

---

# 👑 HOST SPECIAL COMMANDS (DM)

Resend role list:

```
!host_roles
```

End game immediately:

```
!ww_end
```

---

# ⚖️ WIN CONDITIONS

Villagers win:
- All wolves are dead.

Wolves win:
- Wolves equal or outnumber villagers.

---

# 📊 Scaling Rules

The bot automatically scales wolves:

| Players | Wolves |
|----------|--------|
| 5–6      | 1 |
| 7–9      | 2 |
| 10–13    | 3 |
| 14–17    | 4 |
| 18–20    | 5 |

Villager special roles scale proportionally.

---

# 🔒 Notes

- Players must allow DMs from server members.
- Never commit your bot token.
- Host receives live DM updates when actions are submitted.
- All night logic is manually driven by host commands.

---


